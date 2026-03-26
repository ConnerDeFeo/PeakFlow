import base64
from urllib.parse import parse_qs
from twilio.twiml.voice_response import VoiceResponse

def lambda_handler(event, context):
    raw_body = event.get("body", "")
    
    # Lambda Function URLs base64-encode the body when Content-Type is form data
    if event.get("isBase64Encoded"):
        raw_body = base64.b64decode(raw_body).decode("utf-8")

    
    body = parse_qs(raw_body)
    digit = body.get("Digits", [""])[0]

    result = {"1": "YES", "2": "NO"}.get(digit, "NO_RESPONSE")

    resp = VoiceResponse()
    resp.say(f"Thank you. The answer we got was {result}. Goodbye.")
    resp.hangup()

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "text/xml"},
        "body": str(resp)
    }