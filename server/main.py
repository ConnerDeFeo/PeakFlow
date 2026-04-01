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
table = dynamodb.Table("twilio_conversations")
bedrock = boto3.client("bedrock-runtime", region_name="us-east-2")

SYSTEM_PROMPT = """Your name Exodia, the Forbidon One. 
You are a friendly demo receptionist. People are calling you to talk, have a chat with them. 
Keep responses short and conversational — you are speaking out loud, not writing.
Never use bullet points, lists, or special characters.
Always end with a question to keep the conversation going."""

logging.getLogger("botocore").setLevel(logging.WARNING)
logging.getLogger("boto3").setLevel(logging.WARNING)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/incoming-call")
def incoming_call():
    response = VoiceResponse()
    connect = Connect()
    conversationrelay = ConversationRelay(
        url="wss://receptionist.connerdefeo.com/ws",
        welcome_greeting="Hi, thanks for calling! How can I help you today?"
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
                # Load existing history if any
                resp = table.get_item(Key={"call_sid": call_sid})
                history = resp.get("Item", {}).get("history", [])

            elif event == "prompt":
                user_text = data.get("voicePrompt", "")
                if not user_text:
                    continue
                    
                # Check for goodbye before calling Claude
                goodbye_words = ["goodbye", "bye", "hang up", "that's all", "thank you bye"]
                if any(word in user_text.lower() for word in goodbye_words):
                    await websocket.send_text(json.dumps({
                        "type": "text",
                        "token": "Thanks for calling, have a great day!",
                        "last": True
                    }))
                    await asyncio.sleep(3)  # give Twilio time to speak the goodbye
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
                        "max_tokens": 150,
                        "system": SYSTEM_PROMPT,
                        "messages": history
                    })
                )

                full_reply = ""
                for bedrock_event in response["body"]:
                    chunk = json.loads(bedrock_event["chunk"]["bytes"])
                    if chunk["type"] == "content_block_delta":
                        token = chunk["delta"].get("text", "")
                        if token:
                            full_reply += token
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

                print(f"Bedrock reply: '{full_reply}'")

                # Save history
                history.append({"role": "assistant", "content": full_reply})
                print(f"Saving history to DynamoDB (total: {len(history)} messages)")
                table.put_item(Item={
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