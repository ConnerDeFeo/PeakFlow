import json
import boto3
import time
import logging
import asyncio
from fastapi import FastAPI, WebSocket, Response
from twilio.twiml.voice_response import VoiceResponse, Connect, ConversationRelay

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI()

dynamodb = boto3.resource("dynamodb", region_name="us-east-2")
twilio_conversations = dynamodb.Table("twilio_conversations")
roofing_appointments = dynamodb.Table("roofing_appointments")
bedrock = boto3.client("bedrock-runtime", region_name="us-east-2")

DEFAULT_APPOINTMENT_DATA = {
    "first_name": None,
    "last_name": None,
    "address": None,
    "appointment_type": None,
    "appointment_date": None,
    "homeowners_present": None,
    "attic_access": None,
    "roof_age": None,
    "appointment_booked": False
}

logging.getLogger("botocore").setLevel(logging.WARNING)
logging.getLogger("boto3").setLevel(logging.WARNING)


@app.get("/health")
def health():
    return {"status": "ok"}


def get_system_prompt(current_data):
    return f"""
        You are a friendly roofing receptionist named Ron for Rochester Pro Roofing.
        You are collecting information to book a roofing inspection appointment.

        Here is the information you have collected so far:
        {json.dumps(current_data, indent=2)}

        Collect the following fields in this order, skipping any that are already filled in:
        1. First and last name
        2. Address
        3. Is this for a repair or replacement?
        4. What date are they looking to book the appointment?
        5. Only if this is a replacement: will both homeowners (partners) be available for the appointment? 
        Frame this naturally, e.g. "Since we go over a lot of options like systems, colors, and pricing, 
        we find it works best when both partners can be there. Is that something you can arrange?"
        Skip this question entirely if appointment_type is "repair".
        6. Will the roofers be able to access the attic? (yes, no, or crawl space)
        7. Approximately how old is the roof?

        Rules:
        - Do not ask a question you already have the answer to.
        - Do not move on until you have the current answer.
        - Once all required fields are collected, confirm everything back to the customer clearly.
        - Ask if they have any questions.
        - Once confirmed and questions are handled, set appointment_booked to true.

        You must ALWAYS respond in the following JSON format and nothing else. No preamble, no markdown, no extra text:
        {{
        "message": "Your spoken response to the caller here",
        "data": {{
            "first_name": null,
            "last_name": null,
            "address": null,
            "appointment_type": null,
            "appointment_date": null,
            "homeowners_present": null,
            "attic_access": null,
            "roof_age": null,
            "appointment_booked": false
        }}
        }}

        Important rules for the JSON:
        - Always include all fields in "data", even ones you have not collected yet (use null).
        - Carry forward any values already collected — never reset a field that already has a value.
        - The "message" field is what will be spoken aloud. Never include asterisks, markdown, bullet points, or special characters in the message.
        - appointment_booked should only be true once all fields are filled and the customer has confirmed.
    """


@app.post("/incoming-call")
def incoming_call():
    response = VoiceResponse()
    connect = Connect()
    conversationrelay = ConversationRelay(
        url="wss://receptionist.connerdefeo.com/ws",
        welcome_greeting="Hi, this is Rochester Pro Roofing. How can I help you today?"
    )
    conversationrelay.language(
        code="en-US",
        tts_provider="ElevenLabs",
        voice="7EzWGsX10sAS4c9m9cPf",
    )
    connect.append(conversationrelay)
    response.append(connect)
    return Response(content=str(response), media_type="application/xml")


@app.websocket("/ws")
async def websocket_handler(websocket: WebSocket):
    await websocket.accept()
    call_sid = None
    phone_number = None
    history = []

    try:
        async for message in websocket.iter_text():
            data = json.loads(message)
            event = data.get("type")

            if event == "setup":
                call_sid = data.get("callSid")
                phone_number = data.get("from")
                logger.info(f"Call started — SID: {call_sid}, From: {phone_number}")

                # Load conversation history for this call
                resp = twilio_conversations.get_item(Key={"call_sid": call_sid})
                history = resp.get("Item", {}).get("history", [])

            elif event == "prompt":
                user_text = data.get("voicePrompt", "").strip()
                if not user_text:
                    continue

                logger.info(f"User said: {user_text}")

                # Load current appointment data for this caller
                appointment_data = DEFAULT_APPOINTMENT_DATA.copy()
                if phone_number:
                    appt_resp = roofing_appointments.get_item(
                        Key={"customer_phone_number": phone_number}
                    )
                    if "Item" in appt_resp:
                        appointment_data = appt_resp["Item"]

                # If already booked, just say goodbye and hang up
                if appointment_data.get("appointment_booked"):
                    await websocket.send_text(json.dumps({
                        "type": "text",
                        "token": "Your appointment is booked. Thanks for calling Rochester Pro Roofing, have a great day!",
                        "last": True
                    }))
                    await asyncio.sleep(3)
                    await websocket.send_text(json.dumps({"type": "end"}))
                    break

                # Add user message to history
                history.append({"role": "user", "content": user_text})

                # Call Bedrock (no streaming — need full response to parse JSON)
                response = bedrock.invoke_model(
                    modelId="us.anthropic.claude-haiku-4-5-20251001-v1:0",
                    contentType="application/json",
                    accept="application/json",
                    body=json.dumps({
                        "anthropic_version": "bedrock-2023-05-31",
                        "max_tokens": 400,
                        "system": get_system_prompt(appointment_data),
                        "messages": history
                    })
                )

                raw_body = json.loads(response["body"].read())
                logger.debug(f"Full raw body: {raw_body}")  # add this
                raw_text = raw_body["content"][0]["text"].strip()
                logger.debug(f"Bedrock raw response: {raw_text}")

                # Parse the JSON response from Bedrock
                try:
                    parsed = json.loads(raw_text)
                    spoken = parsed.get("message", "Sorry, I didn't catch that. Could you repeat?")
                    updated_data = parsed.get("data", appointment_data)
                except (json.JSONDecodeError, KeyError) as e:
                    logger.error(f"Failed to parse Bedrock JSON response: {e}")
                    spoken = "Sorry, I had a little trouble there. Could you say that again?"
                    updated_data = appointment_data

                logger.info(f"Ron says: {spoken}")

                # Save updated appointment data to DynamoDB
                if phone_number:
                    roofing_appointments.put_item(Item={
                        "customer_phone_number": phone_number,
                        **updated_data
                    })

                # Add assistant response to history
                history.append({"role": "assistant", "content": spoken})

                # Save conversation history
                if call_sid:
                    twilio_conversations.put_item(Item={
                        "call_sid": call_sid,
                        "history": history,
                        "expires_at": int(time.time()) + 3600
                    })

                # Send spoken response to Twilio
                await websocket.send_text(json.dumps({
                    "type": "text",
                    "token": spoken,
                    "last": True
                }))

                # If appointment just got booked, wait then hang up
                if updated_data.get("appointment_booked"):
                    logger.info("Appointment booked — ending call.")
                    await asyncio.sleep(3)
                    await websocket.send_text(json.dumps({"type": "end"}))
                    break

            elif event == "stop":
                logger.info("Call ended by Twilio.")
                break

    except Exception as e:
        logger.exception(f"Unhandled error in websocket_handler: {e}")
    finally:
        try:
            await websocket.close()
        except RuntimeError:
            pass