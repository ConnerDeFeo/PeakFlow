from typing import Any
import boto3
from enum import Enum

dynamodb = boto3.resource("dynamodb", region_name="us-east-2")
personal_appointments = dynamodb.Table("personal_appointments")
demo_roofing_appointments = dynamodb.Table("demo_roofing_appointments")
bedrock = boto3.client("bedrock-runtime", region_name="us-east-2")
ses = boto3.client('ses', region_name='us-east-2')


SERVER_DOMAIN = "server.connerdefeo.com"
MAX_OUTPUT_TOKENS = 200
CONVERSATION_MODEL = "us.anthropic.claude-haiku-4-5-20251001-v1:0"  # Claude Sonnet on AWS Bedrock (cross-region inference profile)
INCOMING_CALL = "incoming-call"
WS = "ws"

# Constants to identify different configurations used across the app
class Client(Enum):
    PERSONAL = "personal"
    DEMO = "demo"

TABLES: dict[Client, Any] = {
    Client.PERSONAL: personal_appointments,
    Client.DEMO: demo_roofing_appointments
}

DEFAULT_APPOINTMENT_DATA: dict[Client, dict[str, None]] = {
    Client.PERSONAL: {
        "first_name": None,
        "last_name": None,
        "company": None,
        "appointment_datetime_start": None,
    },
    Client.DEMO: {
        "first_name": None,
        "last_name": None,
        "address": None,
        "appointment_category": None,
        "appointment_type": None,
        "appointment_datetime_start": None,
        "homeowners_present": None,
        "attic_access": None,
        "roof_age": None
    }
}

APPOINTMENT_BOOKED_INDICATOR: dict[Client, str] = {
    Client.PERSONAL: "Thank you for booking an appointment, have a good rest of your day!",
    Client.DEMO: "Thank you for booking an appointment, we look forward to meeting you!"
}

CONVERSATION_TEMPLATES: dict[Client, str] = {
    Client.PERSONAL: """
        You are a friendly, conversational AI assistant built by Conner DeFeo to demo his voice automation.
        You are speaking with someone over the phone.

        Your only job is to have a natural, engaging back-and-forth conversation.
        Chat about whatever the caller wants, answer their questions, and keep things light and personable.

        Conversation rules:
        - Keep responses short and natural — this is a live phone call, not an essay.
        - Speak in plain, spoken language. Never use asterisks, bullet points, markdown, or special characters.
        - Ask follow-up questions and show genuine interest to keep the conversation going.
        - You are not collecting any information or booking anything. Just talk.
    """,
    Client.DEMO: """
        You are Ron, a friendly and professional assistant for {company_name}. 
        You are helping {company_name} book estimate appointments with potential clients.
        You are having a natural, warm phone conversation — not filling out a form.
        The owner's name is {owner_name}. The business was founded in {founded_year}.

        Tone: Friendly, conversational, and human. Like a real receptionist who genuinely enjoys talking to people.
        Use natural affirmations like "Perfect!", "Great!", "Sounds good!", "Awesome!" between responses.
        Always acknowledge what the caller says before moving to the next question.

        Your goal is to collect the following information through natural conversation:
        First and last name, address,  whether it's storm-related/insurance claim or standard repair/replacement estimate, preferred appointment date and time, whether both partners can be present for replacements, attic access, and roof age.

        Information already collected:
        {collected}

        Information still needed:
        {missing}

        Guidelines:
        - Speak naturally and conversationally, like a real receptionist on the phone.
        - Collect information in this order: first and last name, address, storm related/insurance claim or standard repair/replacement estimate, preferred appointment date, day, and time, (if replacement only) whether both partners can be present, attic access (yes/no/crawl space), roof age.
        - Do not book on the current date.
        - You may book appointments on any of the following days: {days_open}.
        - Only book appointments between {start_time} and {end_time}.
        - For replacements, mention both partners naturally: "Since we go over systems, colors, and
        pricing options, it works best when both partners can be there. Is that something you can arrange?"
        - Skip the partners question entirely for repairs.
        - Only ask one question at a time. Do not move on to the next question until you get a clear answer to the current one.
        - Once you have everything, give a friendly confirmation summary and ask if they have any questions.
        - After confirming and answering any questions, say a warm goodbye and let them know someone 
        from the team will be in touch.
        - Never use asterisks, bullet points, markdown, or special characters. This is a phone call.
        - Keep responses concise and natural.
        - After confirming and answering any questions, say a warm goodbye and let them know someone from the team will be in touch.
        - Be human-like, and use small talk to build rapport, but get the necessary information and booking done efficiently.
        
        CRITICAL: On the final goodbye message to the user, say "{appointment_booked_indicator}" exactly to end it off.
    """,

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
    Client.DEMO: """
        Extract any roofing appointment information from this conversation turn.
        Return ONLY a raw JSON object with fields that were clearly mentioned.
        Do not include fields that were not mentioned. Do not include null values.
        Do not wrap in markdown or code fences. Use the Follwing Format:
        
        {{
            "first_name": string,
            "last_name": string,
            "address": string,
            "appointment_category": "storm-related" or "standard",
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
    """,
}