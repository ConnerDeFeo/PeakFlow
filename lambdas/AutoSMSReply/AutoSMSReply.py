import urllib.parse
import twilio.rest
import os
import base64

TWILIO_ACCOUNT_SID = os.environ['TWILIO_ACCOUNT_SID']
TWILIO_AUTH_TOKEN = os.environ['TWILIO_AUTH_TOKEN']

def lambda_handler(event, context):
    body = event.get('body', '')
    # Decode if base64 encoded
    if event.get('isBase64Encoded', False):
        body = base64.b64decode(body).decode('utf-8')
    
    # Grab the url encoded body from the incoming Twilio request
    body = urllib.parse.parse_qs(body)
    
    caller     = body.get('From', ['Unknown'])[0]
    twilio_number = body.get('To', ['Unknown'])[0]

    twilio_client = twilio.rest.Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    twilio_client.messages.create(
        to=caller,
        from_=twilio_number,
        body="Hey! Sorry we missed your call. We'll get back to you shortly."
    )

    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'text/xml'},
        'body': '''
            <?xml version="1.0" encoding="UTF-8"?>
            <Response>
                <Say>Sorry we missed you. You will receive a text shortly.</Say>
            </Response>
        '''
    }