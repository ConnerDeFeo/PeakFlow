import json
import logging
from config import APPOINTMENT_BOOKED_INDICATOR, CONVERSATION_MODEL, CONVERSATION_TEMPLATES, MAX_OUTPUT_TOKENS, Client, bedrock
from config import grok_client
from xai_sdk.chat import user, system

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
    grok_chat = grok_client.chat.create(
        model="grok-4.20-non-reasoning",
        timeout=3600,
    )
    grok_chat.append(system(get_conversation_prompt(CONVERSATION_TEMPLATES[client], appointment_data, APPOINTMENT_BOOKED_INDICATOR[client], **kwargs)))
    grok_chat.append(history)

    return grok_chat.stream()
    