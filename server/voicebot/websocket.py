import json
import logging
import asyncio
from fastapi import APIRouter, WebSocket
from config import DEFAULT_APPOINTMENT_DATA
from extraction.dynamo import get_conversation_history, save_conversation, get_appointment_data
from bedrock import stream_conversation, run_extraction

router = APIRouter()
logger = logging.getLogger(__name__)


@router.websocket("/ws")
async def websocket_handler(websocket: WebSocket):
    await websocket.accept()
    call_sid = None
    phone_number = None
    history = []
    is_processing = False

    try:
        async for message in websocket.iter_text():
            data = json.loads(message)
            event = data.get("type")

            if event == "setup":
                call_sid = data.get("callSid")
                phone_number = data.get("from")
                logger.info(f"Call started — SID: {call_sid}, From: {phone_number}")
                history = get_conversation_history(call_sid)

            elif event == "prompt":
                user_text = data.get("voicePrompt", "").strip()
                if not user_text:
                    continue

                if is_processing:
                    logger.info(f"Skipping prompt while processing: {user_text}")
                    continue

                is_processing = True

                try:
                    logger.info(f"User said: {user_text}")

                    appointment_data = get_appointment_data(phone_number, DEFAULT_APPOINTMENT_DATA)
                    history.append({"role": "user", "content": user_text})

                    # Stream conversational response to Twilio
                    stream_response = stream_conversation(history, appointment_data)

                    full_reply = []
                    for bedrock_event in stream_response["body"]:
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

                    await websocket.send_text(json.dumps({
                        "type": "text",
                        "token": "",
                        "last": True
                    }))

                    assistant_text = "".join(full_reply)
                    history.append({"role": "assistant", "content": assistant_text})

                    # Save conversation history
                    save_conversation(call_sid, history)

                    # Fire extraction in background
                    asyncio.create_task(run_extraction(
                        user_text=user_text,
                        assistant_text=assistant_text,
                        current_data=appointment_data,
                        phone_number=phone_number,
                        call_sid=call_sid,
                        history=history
                    ))

                finally:
                    is_processing = False

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