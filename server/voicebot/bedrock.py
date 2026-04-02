import json
import logging
from config import bedrock
from dynamo import save_appointment_data, save_conversation
from config import CONVERSATION_MODEL, EXTRACTION_MODEL

logger = logging.getLogger(__name__)


def get_conversation_prompt(current_data: dict) -> str:
    collected = {k: v for k, v in current_data.items() if v is not None}
    missing = [k for k, v in current_data.items() if v is None]

    return f"""You are a friendly roofing receptionist named Ron for Rochester Pro Roofing.
Your job is to have a natural phone conversation to book a roofing inspection appointment.

Information already collected:
{json.dumps(collected, indent=2)}

Information still needed:
{missing}

Guidelines:
- Speak naturally and conversationally, like a real receptionist on the phone.
- Collect information in this order: first and last name, address, repair or replacement,
  preferred appointment date, (if replacement only) whether both partners can be present,
  attic access (yes/no/crawl space), roof age.
- For replacements, mention both partners naturally: "Since we go over systems, colors, and
  pricing options, it works best when both partners can be there. Is that something you can arrange?"
- Skip the partners question entirely for repairs.
- Only ask one question at a time.
- Once you have everything, give a friendly confirmation summary and ask if they have any questions.
- After confirming and answering any questions, say a warm goodbye and let them know someone 
  from the team will be in touch.
- Never use asterisks, bullet points, markdown, or special characters. This is a phone call.
- Keep responses concise and natural."""


def get_extraction_prompt(user_text: str, assistant_text: str, current_data: dict) -> str:
    return f"""Extract any roofing appointment information from this conversation turn.
Return ONLY a raw JSON object with fields that were clearly mentioned.
Do not include fields that were not mentioned. Do not include null values.
Do not wrap in markdown or code fences.

Fields to extract:
- first_name (string)
- last_name (string)
- address (string)
- appointment_type ("repair" or "replacement")
- appointment_date (string)
- homeowners_present ("yes", "no", or "N/A" for repairs)
- attic_access ("yes", "no", or "crawl space")
- roof_age (string)
- appointment_booked (true only if assistant explicitly confirmed the booking and said goodbye)

Current data already collected (do not re-extract unless corrected):
{json.dumps(current_data, indent=2)}

Conversation turn:
User: "{user_text}"
Assistant: "{assistant_text}"

Return only a JSON object with newly extracted or corrected fields. If nothing new was mentioned, return {{}}."""


def stream_conversation(history: list, appointment_data: dict):
    """Returns a streaming response from Sonnet."""
    return bedrock.invoke_model_with_response_stream(
        modelId=CONVERSATION_MODEL,
        contentType="application/json",
        accept="application/json",
        body=json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 300,
            "system": get_conversation_prompt(appointment_data),
            "messages": history
        })
    )


async def run_extraction(
    user_text: str,
    assistant_text: str,
    current_data: dict,
    phone_number: str,
    call_sid: str,
    history: list
):
    """Runs in background after each turn — extracts structured data and saves to DynamoDB."""
    try:
        response = bedrock.invoke_model(
            modelId=EXTRACTION_MODEL,
            contentType="application/json",
            accept="application/json",
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 300,
                "messages": [{
                    "role": "user",
                    "content": get_extraction_prompt(user_text, assistant_text, current_data)
                }]
            })
        )

        raw_body = json.loads(response["body"].read())
        raw_text = raw_body["content"][0]["text"].strip()

        # Strip code fences if model ignores instructions
        if raw_text.startswith("```"):
            raw_text = raw_text.split("```")[1]
            if raw_text.startswith("json"):
                raw_text = raw_text[4:]
            raw_text = raw_text.strip()

        logger.debug(f"Extraction result: {raw_text}")

        if not raw_text or raw_text == "{}":
            return

        extracted = json.loads(raw_text)
        appointment_booked = extracted.pop("appointment_booked", False)

        if extracted:
            updated_data = {**current_data, **extracted}
            if phone_number:
                save_appointment_data(phone_number, updated_data)

        if call_sid:
            save_conversation(call_sid, history, appointment_booked)

    except Exception as e:
        logger.error(f"Extraction failed: {e}")