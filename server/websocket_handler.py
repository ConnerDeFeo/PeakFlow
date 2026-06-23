import json
import logging
import asyncio
from fastapi import APIRouter, WebSocket
from config import APPOINTMENT_BOOKED_INDICATOR, DEFAULT_APPOINTMENT_DATA, Client
from dynamo import DynamoDB
from conversation import stream_conversation
from extraction import run_extraction
from email_service import send_booking_notification

router = APIRouter()
logger = logging.getLogger(__name__)

async def websocket_handler(websocket: WebSocket, client: Client, **kwargs):
    await websocket.accept()
    call_sid = None
    phone_number = None
    history = []
    is_processing = False
    dynamo = DynamoDB(client)

    try:
        async for message in websocket.iter_text():
            if is_processing:
                continue

            data = json.loads(message)
            event = data.get("type")

            if event == "setup":
                call_sid = data.get("callSid")
                phone_number = data.get("from")

            elif event == "prompt":
                user_text = data.get("voicePrompt", "").strip()
                if not user_text:
                    continue

                is_processing = True

                try:
                    history.append({"role": "user", "content": [{"text": user_text}]})

                    # Personal is a basic conversational demo — no appointment data.
                    if client == Client.PERSONAL:
                        appointment_data = {}
                    else:
                        appointment_data = dynamo.get_appointment_data(phone_number, DEFAULT_APPOINTMENT_DATA[client])

                    # Stream conversational response (Claude Sonnet on Bedrock) to Twilio
                    stream = stream_conversation(history, appointment_data, client, **kwargs)

                    assistant_text = ""
                    for chunk in stream:
                        token = chunk.get("contentBlockDelta", {}).get("delta", {}).get("text", "")
                        if token:
                            assistant_text += token
                            await websocket.send_text(json.dumps({
                                "type": "text",
                                "token": token,
                                "last": False
                            }))

                    await websocket.send_text(json.dumps({
                        "type": "text",
                        "token": "",
                        "last": True
                    }))

                    history.append({"role": "assistant", "content": [{"text": assistant_text}]})

                    # Personal demo just talks back and forth — skip booking/extraction.
                    if client == Client.PERSONAL:
                        continue

                    appointment_booked = APPOINTMENT_BOOKED_INDICATOR[client].lower() in assistant_text.lower()

                    # Fire extraction in background
                    asyncio.create_task(run_extraction(
                        user_text=user_text,
                        assistant_text=assistant_text,
                        current_data=appointment_data,
                        phone_number=phone_number,
                        client=client
                    ))

                    if appointment_booked:
                        word_count = len(assistant_text.split())
                        speak_time = max(5, (word_count / 150) * 60)
                        await asyncio.sleep(speak_time)
                        try:
                            await websocket.send_text(json.dumps({"type": "end"}))
                        except:
                            logger.warning("Failed to send 'end' message over WebSocket (likely already closed)")

                        appointment_datetime_start = appointment_data.get("appointment_datetime_start")
                        callers_name = f"{appointment_data.get('first_name', '')} {appointment_data.get('last_name', '')}".strip()

                        send_booking_notification(
                            customer_name=callers_name,
                            phone=phone_number,
                            datetime=appointment_datetime_start,
                            client=client,
                            history=history
                        )

                        break

                finally:
                    is_processing = False

            elif event == "stop":
                break

    except Exception as e:
        logger.exception(f"Unhandled error in websocket_handler: {e}")
    finally:
        try:
            await websocket.close()
        except RuntimeError:
            pass