import json
import logging
from config import APPOINTMENT_BOOKED_INDICATOR, CONVERSATION_TEMPLATES, CONVERSATION_MODEL, Client, bedrock

logger = logging.getLogger(__name__)


def get_conversation_prompt(template: str, current_data: dict, appointment_booked_indicator: str, **kwargs) -> str:
    collected = {k: v for k, v in current_data.items() if v is not None}
    missing = [k for k, v in current_data.items() if v is None]
   
    variables = {
        "collected": json.dumps(collected, indent=2),
        "missing": missing,
        "appointment_booked_indicator": appointment_booked_indicator,
        **kwargs
    }

    return template.format_map(variables)


def stream_conversation(history: list, appointment_data: dict, client: Client, **kwargs):
    """Returns a streaming response from Sonnet."""
    return bedrock.invoke_model_with_response_stream(
        modelId=CONVERSATION_MODEL,
        contentType="application/json",
        accept="application/json",
        body=json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 300,
            "system": get_conversation_prompt(CONVERSATION_TEMPLATES[client], appointment_data, APPOINTMENT_BOOKED_INDICATOR[client], **kwargs),
            "messages": history
        })
    )
