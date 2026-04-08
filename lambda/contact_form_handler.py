import boto3
import json

ses = boto3.client('ses', region_name='us-east-2')

def lambda_handler(event, context):
    body = json.loads(event['body'])
    
    ses.send_email(
        Source='peakflowaiautomations@gmail.com',
        Destination={'ToAddresses': ['peakflowaiautomations@gmail.com']},
        Message={
            'Subject': {'Data': f"New Lead: {body.get('business', 'Unknown')}"},
            'Body': {'Text': {'Data': f"""
Name: {body.get('name')}
Business: {body.get('business')}
Phone: {body.get('phone')}
Email: {body.get('email')}
Missed calls/week: {body.get('missed_calls')}
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