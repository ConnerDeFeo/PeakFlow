from datetime import datetime
from zoneinfo import ZoneInfo
import json
import logging
from config import EXTRACTION_PROMPTS, Client, bedrock
from dynamo import DynamoDB
from config import EXTRACTION_MODEL, grok_client
from xai_sdk.chat import user, system

    
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
    grok_chat = grok_client.chat.create(
        model="grok-4.20-non-reasoning",
    )
    grok_chat.append(user(get_extraction_prompt(user_text, assistant_text, current_data, EXTRACTION_PROMPTS[client])))

    for response, chunk in grok_chat.stream():
        logger.info(f"Grok response chunk: {chunk}")