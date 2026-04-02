import json
import boto3
import time
import logging
from fastapi import FastAPI, WebSocket, Response
from twilio.twiml.voice_response import ConversationRelay, VoiceResponse, Connect
import asyncio

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
        You are a friendly roofing receptionist named Ron. 
        You are collecting data to set up a roofing inspection. Here is what you have so far: 
        {current_data}. 

        The order in which you should collect the data is:
        1. First and Last name
        2. Address
        3. Is this for a repair or replacement?
        4. What is the date you are looking to book the appointment for?
        5. If this is for a replacement, will both homeowners be home?
        6. Will the roofers be able to access the attic?
        7. What is the age of the roof?

        Continue the conversation and collect whatever is missing. 
        Do not move on to the next question until you have the answer to the current question.
        Once all fields are collected, confirm and book the appointment.
        
        Never use markdown, asterisks, bullet points, or any special characters in your responses. 
        Speak in plain conversational sentences only, as this is a phone call.
        
        Once all the information is gathered, confirm the information with the customer, ask if they have any questions.
        Once all of the above is completed, set "appointment_booked" to True.
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
    history = []

    try:
        async for message in websocket.iter_text():
            data = json.loads(message)
            event = data.get("type")

            if event == "setup":
                call_sid = data.get("callSid")
                phone_number = data.get("from")
                # Load existing history if any
                resp = twilio_conversations.get_item(Key={"call_sid": call_sid})
                history = resp.get("Item", {}).get("history", [])

            elif event == "prompt":
                user_text = data.get("voicePrompt", "")
                appointment_data_resp = roofing_appointments.get_item(Key={"customer_phone_number": phone_number})
                appointment_data = appointment_data_resp.get("Item", DEFAULT_APPOINTMENT_DATA)
                if not user_text:
                    continue
                    
                # Check if appointment_booked is True, if so, skip processing and just respond with a confirmation message
                if appointment_data.get("appointment_booked"):
                    await websocket.send_text(json.dumps({
                        "type": "text",
                        "token": "Thanks for calling, have a great day!",
                        "last": True
                    }))
                    await asyncio.sleep(2.5)  # give Twilio time to speak the goodbye
                    # Tell Twilio to end the call
                    await websocket.send_text(json.dumps({
                        "type": "end"
                    }))
                    break

                history.append({"role": "user", "content": user_text})

                # Stream the response
                response = bedrock.invoke_model_with_response_stream(
                    modelId="us.anthropic.claude-haiku-4-5-20251001-v1:0",
                    contentType="application/json",
                    accept="application/json",
                    body=json.dumps({
                        "anthropic_version": "bedrock-2023-05-31",
                        "max_tokens": 75,
                        "system": get_system_prompt(appointment_data),
                        "messages": history
                    })
                )

                full_reply = []
                for bedrock_event in response["body"]:
                    chunk = json.loads(bedrock_event["chunk"]["bytes"])
                    if chunk["type"] == "content_block_delta":
                        token = chunk["delta"].get("text", "")
                        if token:
                            full_reply.append(token)
                            await websocket.send_text(json.dumps({
                                "type": "text",
                                "token": token,
                                "last": False
                            }))

                # Send final token
                await websocket.send_text(json.dumps({
                    "type": "text",
                    "token": "",
                    "last": True
                }))


                # Save history
                history.append({"role": "assistant", "content": "".join(full_reply)})
                twilio_conversations.put_item(Item={
                    "call_sid": call_sid,
                    "history": history,
                    "expires_at": int(time.time()) + 3600
                })

            elif event == "stop":
                break

    except Exception as e:
        logger.exception("Unhandled error in websocket_handler: %s", e)
    finally:
        try:
            await websocket.close()
        except RuntimeError:
            pass