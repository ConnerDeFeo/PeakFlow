from twilio.twiml.voice_response import VoiceResponse, Gather

CONSENT_ANSWER_URL = "https://okhrvw3hrd4l2xqn5edkwxr3fy0lrnyv.lambda-url.us-east-2.on.aws/"

def lambda_handler(event, context):
    """Called when the call connects — asks the question"""
    resp = VoiceResponse()
    
    gather = Gather(
        num_digits=1,
        action=CONSENT_ANSWER_URL,
        timeout=10
    )
    gather.say("Hello, this is SOS Roofing. Press 1 for yes, or 2 for no. Did you request a free roof inspection?")
    
    resp.append(gather)
    resp.say("We didn't receive a response. Goodbye.")  # fallback if no input
    resp.hangup()
    
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "text/xml"},
        "body": str(resp)
    }