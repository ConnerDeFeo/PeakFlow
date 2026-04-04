import json
import logging
from config import EXTRACTION_PROMPTS, TABLES, Client, bedrock
from dynamo import DynamoDB
from config import EXTRACTION_MODEL

    
logger = logging.getLogger(__name__)

def get_extraction_prompt(user_text: str, assistant_text: str, current_data: dict, prompt: str) -> str:
    current_data_json = json.dumps(current_data, indent=2)
    variables = {
        "user_text": user_text,
        "assistant_text": assistant_text,
        "current_data_json": current_data_json
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
        response = bedrock.invoke_model(
            modelId=EXTRACTION_MODEL,
            contentType="application/json",
            accept="application/json",
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 300,
                "messages": [{
                    "role": "user",
                    "content": get_extraction_prompt(user_text, assistant_text, current_data, EXTRACTION_PROMPTS[client])
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
                dynamo = DynamoDB(TABLES[Client])
                dynamo.save_appointment_data(phone_number, updated_data)

        if call_sid:
            dynamo.save_conversation(call_sid, history, appointment_booked)

    except Exception as e:
        logger.error(f"Extraction failed: {e}")