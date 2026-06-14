import boto3
import json

ses = boto3.client('ses', region_name='us-east-2')

def lambda_handler(event, context):
    
    ses.send_email(
        Source='peakflowaiautomations@gmail.com',
        Destination={'ToAddresses': ['peakflowaiautomations@gmail.com']},
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