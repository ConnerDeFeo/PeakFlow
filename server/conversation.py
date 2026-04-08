import json
import logging
from config import APPOINTMENT_BOOKED_INDICATOR, CONVERSATION_MODEL, CONVERSATION_TEMPLATES, MAX_OUTPUT_TOKENS, Client, bedrock

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

# us.anthropic.claude-haiku-4-5-20251001-v1:0
def stream_conversation(history: list, appointment_data: dict, client: Client, **kwargs):
    """Returns a streaming response from a given model."""
    return bedrock.converse_stream(
        modelId=CONVERSATION_MODEL,
        system=[{"text": get_conversation_prompt(CONVERSATION_TEMPLATES[client], appointment_data, APPOINTMENT_BOOKED_INDICATOR[client], **kwargs)}],
        messages=history,
        inferenceConfig={"maxTokens": MAX_OUTPUT_TOKENS}
    )