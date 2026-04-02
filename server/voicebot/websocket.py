import json
import logging
import asyncio
from fastapi import APIRouter, WebSocket
from config import DEFAULT_APPOINTMENT_DATA
from extraction.dynamo import get_conversation_history, save_conversation, get_appointment_data
from voicebot.bedrock import stream_conversation, run_extraction

router = APIRouter()
logger = logging.getLogger(__name__)


@router.websocket("/ws")
async def websocket_handler(websocket: WebSocket):
    logger.debug("WebSocket connection received, accepting...")
    await websocket.accept()
    logger.debug("WebSocket connection accepted")
    call_sid = None
    phone_number = None
    history = []
    is_processing = False

    try:
        async for message in websocket.iter_text():
            logger.debug(f"Raw message received: {message[:200]}")
            data = json.loads(message)
            event = data.get("type")
            logger.debug(f"Parsed event type: {event}")

            if event == "setup":
                call_sid = data.get("callSid")
                phone_number = data.get("from")
                logger.info(f"Call started — SID: {call_sid}, From: {phone_number}")
                logger.debug(f"Fetching conversation history for call_sid: {call_sid}")
                history = get_conversation_history(call_sid)
                logger.debug(f"Loaded {len(history)} history entries for call_sid: {call_sid}")

            elif event == "prompt":
                user_text = data.get("voicePrompt", "").strip()
                logger.debug(f"Received prompt, voicePrompt raw value: {repr(data.get('voicePrompt'))}")
                if not user_text:
                    logger.debug("Empty voicePrompt received, skipping")
                    continue

                if is_processing:
                    logger.info(f"Skipping prompt while processing: {user_text}")
                    continue

                is_processing = True
                logger.debug("is_processing set to True")

                try:
                    logger.info(f"User said: {user_text}")

                    logger.debug(f"Fetching appointment data for phone_number: {phone_number}")
                    appointment_data = get_appointment_data(phone_number, DEFAULT_APPOINTMENT_DATA)
                    logger.debug(f"Appointment data retrieved: {appointment_data}")
                    history.append({"role": "user", "content": user_text})
                    logger.debug(f"Appended user turn to history (total turns: {len(history)})")

                    # Stream conversational response to Twilio
                    logger.debug("Calling stream_conversation with current history and appointment data")
                    stream_response = stream_conversation(history, appointment_data)
                    logger.debug("stream_conversation returned, beginning to iterate response body")

                    full_reply = []
                    token_count = 0
                    for bedrock_event in stream_response["body"]:
                        chunk = json.loads(bedrock_event["chunk"]["bytes"])
                        if chunk["type"] == "content_block_delta":
                            token = chunk["delta"].get("text", "")
                            if token:
                                full_reply.append(token)
                                token_count += 1
                                logger.debug(f"Streaming token #{token_count}: {repr(token)}")
                                await websocket.send_text(json.dumps({
                                    "type": "text",
                                    "token": token,
                                    "last": False
                                }))

                    logger.debug(f"Finished streaming {token_count} tokens, sending final 'last' marker")
                    await websocket.send_text(json.dumps({
                        "type": "text",
                        "token": "",
                        "last": True
                    }))

                    assistant_text = "".join(full_reply)
                    logger.debug(f"Full assistant reply assembled ({len(assistant_text)} chars): {assistant_text[:100]}")
                    history.append({"role": "assistant", "content": assistant_text})
                    logger.debug(f"Appended assistant turn to history (total turns: {len(history)})")

                    # Save conversation history
                    logger.debug(f"Saving conversation history for call_sid: {call_sid}")
                    save_conversation(call_sid, history)
                    logger.debug("Conversation history saved")

                    # Fire extraction in background
                    logger.debug("Scheduling run_extraction as background task")
                    asyncio.create_task(run_extraction(
                        user_text=user_text,
                        assistant_text=assistant_text,
                        current_data=appointment_data,
                        phone_number=phone_number,
                        call_sid=call_sid,
                        history=history
                    ))
                    logger.debug("run_extraction background task created")

                finally:
                    is_processing = False
                    logger.debug("is_processing reset to False")

            elif event == "stop":
                logger.info("Call ended by Twilio.")
                logger.debug(f"Stop event received for call_sid: {call_sid}, closing loop")
                break

            else:
                logger.debug(f"Unrecognized event type received: {event!r}")

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