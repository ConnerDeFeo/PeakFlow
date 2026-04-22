from datetime import datetime
from zoneinfo import ZoneInfo
import json
import logging
from config import EXTRACTION_PROMPTS, Client
from dynamo import DynamoDB
from config import grok_client
from xai_sdk.chat import user

    
logger = logging.getLogger(__name__)

def get_extraction_prompt(user_text: str, assistant_text: str, current_data: dict, prompt: str) -> str:
    current_data_json = json.dumps(current_data, indent=2)
    current_date = datetime.now(ZoneInfo("America/New_York")).strftime("%Y-%m-%d %H:%M:%S %Z")
    variables = {
        "user_text": user_text,
        "assistant_text": assistant_text,
        "current_data_json": current_data_json,
        "current_date": current_date
    }
    return prompt.format_map(variables)

async def run_extraction(
    user_text: str,
    assistant_text: str,
    current_data: dict,
    phone_number: str,
    call_sid: str,
    history: list,
    client: Client
):
    """Runs in background after each turn — extracts structured data and saves to DynamoDB."""

    try:
        grok_chat = grok_client.chat.create(model="grok-4.20-non-reasoning")
        grok_chat.append(user(get_extraction_prompt(user_text, assistant_text, current_data, EXTRACTION_PROMPTS[client])))

        response = grok_chat.sample()
        raw_text = response.content

        # Strip code fences if model ignores instructions
        if raw_text.startswith("```"):
            raw_text = raw_text.split("```")[1]
            if raw_text.startswith("json"):
                raw_text = raw_text[4:]
            raw_text = raw_text.strip()

        if not raw_text or raw_text == "{}":
            return

        extracted = json.loads(raw_text)
        appointment_booked = extracted.pop("appointment_booked", False)
        dynamo = DynamoDB(client)

        if extracted:
            updated_data = {**current_data, **extracted}
            if phone_number:
                dynamo.save_appointment_data(phone_number, updated_data)

        if call_sid:
            dynamo.save_conversation(call_sid, history, appointment_booked)

    except Exception as e:
        logger.error(f"Extraction failed: {e}")