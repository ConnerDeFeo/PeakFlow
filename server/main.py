import json
import boto3
import time
from fastapi import FastAPI, Response, WebSocket
from twilio.twiml.voice_response import VoiceResponse, Connect

app = FastAPI()

dynamodb = boto3.resource("dynamodb", region_name="us-east-2")
table = dynamodb.Table("twilio_conversations")
bedrock = boto3.client("bedrock-runtime", region_name="us-east-2")

SYSTEM_PROMPT = """You are a friendly receptionist for a roofing company. 
Keep responses short and conversational — you are speaking out loud, not writing.
Never use bullet points, lists, or special characters.
Always end with a question to keep the conversation going.
If someone wants to book an appointment or get a quote, collect their name and phone number."""

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/incoming-call")
def incoming_call():
    response = VoiceResponse()
    connect = Connect()
    connect.conversation_relay(
        url="wss://receptionist.connerdefeo.com/ws",
        tts_provider="Amazon",
        voice="Polly.Joanna-Generative",
        transcription_provider="Deepgram",
        welcome_greeting="Hi, thanks for calling! How can I help you today?"
    )
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
            event = data.get("event")

            if event == "start":
                call_sid = data["start"]["callSid"]
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
                    # Tell Twilio to end the call
                    await websocket.send_text(json.dumps({
                        "type": "end"
                    }))
                    break

                history.append({"role": "user", "content": user_text})

                # Call Claude
                response = bedrock.invoke_model(
                    modelId="us.anthropic.claude-sonnet-4-20250514-v1:0",
                    contentType="application/json",
                    accept="application/json",
                    body=json.dumps({
                        "anthropic_version": "bedrock-2023-05-31",
                        "max_tokens": 150,
                        "system": SYSTEM_PROMPT,
                        "messages": history
                    })
                )
                result = json.loads(response["body"].read())
                reply = result["content"][0]["text"]

                history.append({"role": "assistant", "content": reply})

                # Save history
                table.put_item(Item={
                    "call_sid": call_sid,
                    "history": history,
                    "expires_at": int(time.time()) + 3600
                })

                # Send reply back to ConversationRelay
                await websocket.send_text(json.dumps({
                    "type": "text",
                    "token": reply,
                    "last": True
                }))

            elif event == "stop":
                break

    except Exception as e:
        print(f"Error: {e}")
    finally:
        try:
            await websocket.close()
        except RuntimeError:
            pass