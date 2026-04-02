import boto3
dynamodb = boto3.resource("dynamodb", region_name="us-east-2")
twilio_conversations = dynamodb.Table("twilio_conversations")
roofing_appointments = dynamodb.Table("roofing_appointments")
bedrock = boto3.client("bedrock-runtime", region_name="us-east-2")

DEFAULT_APPOINTMENT_DATA = {
    "first_name": None,
    "last_name": None,
    "address": None,
    "appointment_type": None,
    "appointment_date": None,
    "homeowners_present": None,
    "attic_access": None,
    "roof_age": None
}