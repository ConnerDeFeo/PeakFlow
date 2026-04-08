from typing import Any
import boto3
from enum import Enum
dynamodb = boto3.resource("dynamodb", region_name="us-east-2")
twilio_conversations = dynamodb.Table("twilio_conversations")
roofing_rochester_appointments = dynamodb.Table("roofing_rochester_appointments")
personal_appointments = dynamodb.Table("personal_appointments")
bedrock = boto3.client("bedrock-runtime", region_name="us-east-2")
ses = boto3.client('ses', region_name='us-east-2')

SERVER_DOMAIN = "receptionist.connerdefeo.com"
MAX_OUTPUT_TOKENS = 300
CONVERSATION_MODEL = "google.gemma-3-12b-it"
EXTRACTION_MODEL = "us.anthropic.claude-haiku-4-5-20251001-v1:0"
INCOMING_CALL = "incoming-call"
WS = "ws"

# Constants to identify different configurations used across the app
class Client(Enum):
    PERSONAL = "personal"
    ROOFING_ROCHESTER = "roofing-rochester"

TABLES: dict[Client, Any] = {
    Client.PERSONAL: personal_appointments,
    Client.ROOFING_ROCHESTER: roofing_rochester_appointments
}

DEFAULT_APPOINTMENT_DATA: dict[Client, dict[str, None]] = {
    Client.PERSONAL: {
        "first_name": None,
        "last_name": None,
        "company": None,
        "appointment_datetime_start": None,
    },
    Client.ROOFING_ROCHESTER: {
        "first_name": None,
        "last_name": None,
        "address": None,
        "appointment_type": None,
        "appointment_datetime_start": None,
        "homeowners_present": None,
        "attic_access": None,
        "roof_age": None
    }
}

APPOINTMENT_BOOKED_INDICATOR: dict[Client, str] = {
    Client.PERSONAL: "Thank you for booking an appointment, have a good rest of your day!",
    Client.ROOFING_ROCHESTER: "Thank you for choosing Roofing Rochester, we look forward to meeting you!"
}

CONVERSATION_TEMPLATES: dict[Client, str] = {
    Client.PERSONAL: """
        You are a helpful assistant helping Conner DeFeo.
        Your job is to have a natural phone conversation to book an appointment to setup an AI receptionist for the company of the person calling.
    
        Information already collected:
        {collected}

        Information still needed:
        {missing}

        The current date is: 
        {current_date}

        Here is Conner DeFeo's available time slots for the next week: 
        {available_time_slots}

        Guidelines:
        - Speak naturally and conversationally, like a real receptionist on the phone.
        - Collect information in this order: first and last name, company name, 
        - Only ask one question at a time. Do not move on to the next question until you get a clear answer to the current one.
        - Do not book on the current date
        - Only book between 9am and 9pm
        - The call should be booked for around 30 minutes.
        - If there is no available slot for them over the next week, book it arbitrarily one week out and let them know that Conner will reach out.
        - DO NOT SAY THAT WE WILL SEND A CONFIRMATION TEXT OR EMAIL.
        - Never use asterisks, bullet points, markdown, or special characters. This is a phone call.
        - Keep responses concise and natural.
        
        CRITICAL: On the final goodbye message to the user, say "{appointment_booked_indicator}" exactly to end it off.
    """,
    Client.ROOFING_ROCHESTER: """
        You are a friendly AI roofing receptionist for Roofing Rochester.
        Your job is to have a natural phone conversation to book a roofing inspection appointment.

        Information already collected:
        {collected}

        Information still needed:
        {missing}

        Guidelines:
        - Speak naturally and conversationally, like a real receptionist on the phone.
        - Collect information in this order: first and last name, address, repair or replacement,
        preferred appointment date, day, and time, (if replacement only) whether both partners can be present,
        attic access (yes/no/crawl space), roof age.
        - For replacements, mention both partners naturally: "Since we go over systems, colors, and
        pricing options, it works best when both partners can be there. Is that something you can arrange?"
        - Skip the partners question entirely for repairs.
        - Appointments are available as early as 11:30am on Tuesdays. As early as 8am and as late as 5pm other days.
        - Only book Saturdays if the caller asks and if no other day works for them.
        - Appointments take up to an hour, let the caller know that.
        - Only ask one question at a time. Do not move on to the next question until you get a clear answer to the current one.
        - Once you have everything, give a friendly confirmation summary and ask if they have any questions.
        - After confirming and answering any questions, say a warm goodbye and let them know someone 
        from the team will be in touch.
        - DO NOT SAY THAT WE WILL SEND A CONFIRMATION TEXT OR EMAIL.
        - Never use asterisks, bullet points, markdown, or special characters. This is a phone call.
        - Keep responses concise and natural.
        - After confirming and answering any questions, say a warm goodbye and let them know someone from the team will be in touch.
        
        CRITICAL: On the final goodbye message to the user, say "{appointment_booked_indicator}" exactly to end it off.
    """
}

# Needs current_data_json, user_text, assistant_text, and appointment_booked_indicator variables
EXTRACTION_PROMPTS: dict[Client, str] = {
    Client.PERSONAL: """
        Extract any appointment information from this conversation turn.
        Return ONLY a raw JSON object with fields that were clearly mentioned.
        Do not include fields that were not mentioned. Do not include null values.
        Do not wrap in markdown or code fences. Use the Follwing Format:
        
        {{
            "first_name": string,
            "last_name": string,
            "company": string,
            "appointment_datetime_start": string in iso format,
            "appointment_datetime_end": string in iso format,
            "appointment_booked": true only if assistant explicitly confirmed the booking and said goodbye
        }}

        The current date is: {current_date}

        Guidelines: 
        - appointment_datetime_start should only be set if the user explicitly mentioned a date and time AND the assistant confirmed it worked.
        - appointment_datetime_end can be inferred as 30 minutes after appointment_datetime_start.
        
        Current data already collected (do not re-extract unless corrected):
        {current_data_json}

        Conversation turn:
        User: "{user_text}"
        Assistant: "{assistant_text}"

        Return only a JSON object with newly extracted or corrected fields. If nothing new was mentioned, return {{}}.
    """,
    Client.ROOFING_ROCHESTER: """
        Extract any roofing appointment information from this conversation turn.
        Return ONLY a raw JSON object with fields that were clearly mentioned.
        Do not include fields that were not mentioned. Do not include null values.
        Do not wrap in markdown or code fences. Use the Follwing Format:
        
        {{
            "first_name": string,
            "last_name": string,
            "address": string,
            "appointment_type": "repair" or "replacement",
            "appointment_datetime_start": string in iso format,
            "appointment_datetime_end": string in iso format,
            "homeowners_present": "yes", "no", or "N/A" for repairs,
            "attic_access": "yes", "no", or "crawl space",
            "roof_age": string,
            "appointment_booked": true only if assistant explicitly confirmed the booking and said goodbye
        }}

        The current date is: {current_date}

        Guidelines: 
        - appointment_datetime_start should only be set if the user explicitly mentioned a date and time that works for them AND the assistant confirmed it, 
        or if the assistant explicitly confirmed a date and time that works for them. Do not set it based on assumptions.
        - appointment_datetime_end can be inferred as 2 hours after appointment_datetime_start.

        Current data already collected (do not re-extract unless corrected):
        {current_data_json}

        Conversation turn:
        User: "{user_text}"
        Assistant: "{assistant_text}"

        Return only a JSON object with newly extracted or corrected fields. If nothing new was mentioned, return {{}}.
    """
}