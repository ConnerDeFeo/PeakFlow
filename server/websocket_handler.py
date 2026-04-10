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
    logger.debug(f"WebSocket connection received for client: {client}")
    await websocket.accept()
    logger.debug("WebSocket accepted")
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
            logger.debug(f"Received event: {event}")

            if event == "setup":
                call_sid = data.get("callSid")
                phone_number = data.get("from")
                logger.debug(f"Setup event: call_sid={call_sid}, phone_number={phone_number}")
                history = dynamo.get_conversation_history(call_sid)
                logger.debug(f"Loaded {len(history)} history entries for call_sid={call_sid}")

            elif event == "prompt":
                user_text = data.get("voicePrompt", "").strip()
                if not user_text:
                    logger.debug("Empty voicePrompt received, skipping")
                    continue

                logger.debug(f"Prompt event: user_text={user_text!r}")
                is_processing = True

                try:
                    appointment_data = dynamo.get_appointment_data(phone_number, DEFAULT_APPOINTMENT_DATA[client])
                    logger.debug(f"Fetched appointment_data for phone_number={phone_number}: {appointment_data}")
                    history.append({"role": "user", "content": [{"text": user_text}]})

                    # Stream conversational response to Twilio
                    logger.debug("Starting stream_conversation")
                    stream_response = stream_conversation(history, appointment_data, client, **kwargs)

                    full_reply = []
                    token_count = 0
                    for response, chunk in stream_response.stream():
                        logger.info(f"Grok response chunk: {chunk}")
                        

                    await websocket.send_text(json.dumps({
                        "type": "text",
                        "token": "",
                        "last": True
                    }))

                    assistant_text = "".join(full_reply)
                    logger.debug(f"Full assistant reply ({token_count} tokens): {assistant_text}")
                    appointment_booked = APPOINTMENT_BOOKED_INDICATOR[client].lower() in assistant_text.lower()
                    logger.debug(f"appointment_booked={appointment_booked}")
                    history.append({"role": "assistant", "content": [{"text": assistant_text}]})

                    # Save conversation history
                    logger.debug(f"Saving conversation history for call_sid={call_sid} ({len(history)} entries)")
                    dynamo.save_conversation(call_sid, history)

                    # Fire extraction in background
                    logger.debug("Firing background extraction task")
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
                        logger.debug(f"Appointment booked. Waiting {speak_time:.1f}s for speech to finish ({word_count} words)")
                        await asyncio.sleep(speak_time)
                        try:
                            await websocket.send_text(json.dumps({"type": "end"}))
                        except:
                            logger.warning("Failed to send 'end' message over WebSocket (likely already closed)")

                        appointment_datetime_start = appointment_data.get("appointment_datetime_start") 
                        callers_name = f"{appointment_data.get('first_name', '')} {appointment_data.get('last_name', '')}".strip()

                        if client == Client.PERSONAL and appointment_datetime_start:
                            logger.debug(f"Booking Google Calendar appointment at {appointment_datetime_start} for {callers_name}")
                            from personal.calendar_service import book_google_calendar_appointment
                            from dateutil import parser

                            try:
                                dt = parser.parse(appointment_datetime_start)
                                summary = f"AI Receptionist Appointment with {appointment_data.get('company', 'Unknown Company')}"
                                description = f"Caller's Name: {callers_name} \n Phone: {phone_number}"
                                book_google_calendar_appointment(dt, summary, description=description)
                            except Exception as e:
                                logger.warning(f"Failed to book Google Calendar appointment: {e}")
                        
                        logger.debug(f"Sending booking notification for {callers_name} ({phone_number})")
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
                logger.debug(f"Stop event received for call_sid={call_sid}")
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