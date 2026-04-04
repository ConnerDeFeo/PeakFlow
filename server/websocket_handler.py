import json
import logging
import asyncio
from fastapi import APIRouter, WebSocket
from config import APPOINTMENT_BOOKED_INDICATOR, DEFAULT_APPOINTMENT_DATA, Client
from dynamo import get_conversation_history, save_conversation, get_appointment_data
from conversation import stream_conversation
from extraction import run_extraction

router = APIRouter()
logger = logging.getLogger(__name__)

async def websocket_handler(websocket: WebSocket, client: Client):
    await websocket.accept()
    call_sid = None
    phone_number = None
    history = []
    is_processing = False

    try:
        async for message in websocket.iter_text():
            if is_processing:
                continue

            data = json.loads(message)
            event = data.get("type")

            if event == "setup":
                call_sid = data.get("callSid")
                phone_number = data.get("from")
                history = get_conversation_history(call_sid)

            elif event == "prompt":
                user_text = data.get("voicePrompt", "").strip()
                if not user_text:
                    continue

                is_processing = True

                try:
                    appointment_data = get_appointment_data(phone_number, DEFAULT_APPOINTMENT_DATA[client])
                    history.append({"role": "user", "content": user_text})

                    # Stream conversational response to Twilio
                    stream_response = stream_conversation(history, appointment_data, client)

                    full_reply = []
                    token_count = 0
                    for bedrock_event in stream_response["body"]:
                        chunk = json.loads(bedrock_event["chunk"]["bytes"])
                        if chunk["type"] == "content_block_delta":
                            token = chunk["delta"].get("text", "")
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
                    appointment_booked = APPOINTMENT_BOOKED_INDICATOR[client] in assistant_text
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
                        history=history,
                        client=client
                    ))

                    if appointment_booked:
                        word_count = len(assistant_text.split())
                        speak_time = max(5, (word_count / 160) * 60)
                        await asyncio.sleep(speak_time)
                        await websocket.send_text(json.dumps({"type": "end"}))
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