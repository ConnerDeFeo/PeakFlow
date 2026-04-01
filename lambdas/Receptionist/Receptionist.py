import json
import os
import time
import boto3
from urllib.parse import parse_qs
import base64
from twilio.twiml.voice_response import VoiceResponse, Gather

# Clients
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("twilio_conversations")
bedrock = boto3.client("bedrock-runtime", region_name=os.environ.get("AWS_REGION", "us-east-2"))
ACTION_URL = os.environ["RECEPTIONIST_LAMBDA_URL"]
VOICE = "Polly.Joanna-Generative"

SYSTEM_PROMPT = """You are a helpful AI phone assistant for a roofing company.
Keep responses under 2 sentences — this is a phone call, be concise.
Never use markdown, lists, or special characters."""

# Call Claude via Bedrock
def call_claude(history):
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
    return result["content"][0]["text"]

# Retrieve conversation history from DynamoDB
def get_history(call_sid):
    resp = table.get_item(Key={"call_sid": call_sid})
    return resp.get("Item", {}).get("history", [])

# Save conversation history to DynamoDB with a 1-hour TTL
def save_history(call_sid, history):
    table.put_item(Item={
        "call_sid": call_sid,
        "history": history,
        "expires_at": int(time.time()) + 3600
    })

# Generate TwiML for gathering speech input from the caller
def twiml_gather(say_text, action_url):
    response = VoiceResponse()
    gather = Gather(input="speech", action=action_url, method="POST",
                    speech_timeout="auto", language="en-US")
    gather.say(say_text, voice=VOICE)
    response.append(gather)
    response.say("I didn't catch that. Goodbye!", voice=VOICE)
    return str(response)

# Generate TwiML for ending the call
def twiml_end(say_text):
    response = VoiceResponse()
    response.say(say_text, voice=VOICE)
    response.hangup()
    return str(response)


def lambda_handler(event, context):
    body = event.get('body', '')
    # Decode if base64 encoded
    if event.get('isBase64Encoded', False):
        body = base64.b64decode(body).decode('utf-8')
    body = parse_qs(body)
    call_sid = body.get("CallSid", ["unknown"])[0]
    speech_result = body.get("SpeechResult", [None])[0]

    # First call — greet the caller
    if not speech_result:
        greeting = "Hi, thanks for calling! I'm an AI assistant. How can I help you today?"
        save_history(call_sid, [])
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "text/xml"},
            "body": twiml_gather(greeting, ACTION_URL)
        }

    # Load history and append user message
    history = get_history(call_sid)
    history.append({"role": "user", "content": speech_result})

    # Call Claude via Bedrock
    assistant_reply = call_claude(history)

    # Save updated history
    history.append({"role": "assistant", "content": assistant_reply})
    save_history(call_sid, history)

    # End call if user signals goodbye
    if any(word in speech_result.lower() for word in ["goodbye", "bye", "hang up", "that's all"]):
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "text/xml"},
            "body": twiml_end(assistant_reply)
        }

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "text/xml"},
        "body": twiml_gather(assistant_reply, ACTION_URL)
    }