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
                history = dynamo.get_conversation_history(call_sid)

            elif event == "prompt":
                user_text = data.get("voicePrompt", "").strip()
                if not user_text:
                    continue

                is_processing = True

                try:
                    appointment_data = dynamo.get_appointment_data(phone_number, DEFAULT_APPOINTMENT_DATA[client])
                    history.append({"role": "user", "content": [{"text": user_text}]})

                    # Stream conversational response to Twilio
                    stream_response = stream_conversation(history, appointment_data, client, **kwargs)

                    full_reply = []
                    token_count = 0
                    for bedrock_event in stream_response["stream"]:
                        chunk = bedrock_event.get("contentBlockDelta", {})
                        token = chunk.get("delta", {}).get("text", "")
                        if token:
                            full_reply.append(token)
                            token_count += 1
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

                    assistant_text = "".join(full_reply)
                    logger.debug(f"Full assistant reply: {assistant_text}")
                    appointment_booked = APPOINTMENT_BOOKED_INDICATOR[client] in assistant_text
                    history.append({"role": "assistant", "content": [{"text": assistant_text}]})

                    # Save conversation history
                    dynamo.save_conversation(call_sid, history)

                    # Fire extraction in background
                    asyncio.create_task(run_extraction(
                        user_text=user_text,
                        assistant_text=assistant_text,
                        current_data=appointment_data,
                        phone_number=phone_number,
                        call_sid=call_sid,
                        history=history,
                        client=client
                    ))

                    if appointment_booked:
                        word_count = len(assistant_text.split())
                        speak_time = max(5, (word_count / 160) * 60)
                        await asyncio.sleep(speak_time)
                        try:
                            await websocket.send_text(json.dumps({"type": "end"}))
                        except:
                            logger.warning("Failed to send 'end' message over WebSocket (likely already closed)")

                        appointment_datetime_start = appointment_data.get("appointment_datetime_start") 
                        callers_name = f"{appointment_data.get('first_name', '')} {appointment_data.get('last_name', '')}".strip()

                        if client == Client.PERSONAL and appointment_datetime_start:
                            from personal.calendar_service import book_google_calendar_appointment
                            from dateutil import parser

                            try:
                                dt = parser.parse(appointment_datetime_start)
                                summary = f"AI Receptionist Appointment with {appointment_data.get('company', 'Unknown Company')}"
                                description = f"Caller's Name: {callers_name} \n Phone: {phone_number}"
                                book_google_calendar_appointment(dt, summary, description=description)
                            except Exception as e:
                                logger.warning(f"Failed to book Google Calendar appointment: {e}")
                        
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
        logger.debug(f"Closing WebSocket for call_sid: {call_sid}")
        try:
            await websocket.close()
            logger.debug("WebSocket closed cleanly")
        except RuntimeError:
            logger.debug("WebSocket already closed (RuntimeError suppressed)")
            pass