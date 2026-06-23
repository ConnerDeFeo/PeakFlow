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


def stream_conversation(history: list, appointment_data: dict, client: Client, **kwargs):
    """Stream a conversational response from Claude Sonnet on AWS Bedrock.

    Returns the Bedrock converse_stream event iterator. `history` is the full
    conversation in Bedrock Converse format and must already include the latest
    user turn.
    """
    system_prompt = get_conversation_prompt(
        CONVERSATION_TEMPLATES[client], appointment_data, APPOINTMENT_BOOKED_INDICATOR[client], **kwargs
    )

    response = bedrock.converse_stream(
        modelId=CONVERSATION_MODEL,
        messages=history,
        system=[{"text": system_prompt}],
        inferenceConfig={"maxTokens": MAX_OUTPUT_TOKENS},
    )

    return response["stream"]