import boto3
import json

ses = boto3.client('ses', region_name='us-east-2')

def lambda_handler(event, context):
    body = json.loads(event['body'])
    to_address = body['toAddress']
    
    ses.send_email(
        Source='peakflowaiautomations@gmail.com',
        Destination={'ToAddresses': [to_address]},
        Message={
            'Subject': {'Data': f"Test email"},
            'Body': {'Text': {'Data': f"""
                Testing this works
            """}}
        }
    )
    
    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type'
        },
        'body': json.dumps({'message': 'success'})
    }