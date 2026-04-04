from fastapi import Response
from twilio.twiml.voice_response import VoiceResponse, Connect, ConversationRelay


def incoming_call(websocket_url: str, welcome_greeting: str, voice_name: str):
    response = VoiceResponse()
    connect = Connect()
    conversationrelay = ConversationRelay(
        url=websocket_url,
        welcome_greeting=welcome_greeting,
        welcome_greeting_interruptible = False
    )
    conversationrelay.language(
        code="en-US",
        tts_provider="ElevenLabs",
        voice=voice_name,
    )
    connect.append(conversationrelay)
    response.append(connect)
    return Response(content=str(response), media_type="application/xml")