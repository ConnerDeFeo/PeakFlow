import json
import logging
from config import APPOINTMENT_BOOKED_INDICATOR, CONVERSATION_TEMPLATES, MAX_OUTPUT_TOKENS, Client, bedrock

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
    """Returns a streaming response from Haiku."""
    return bedrock.converse_stream(
        modelId="openai.gpt-oss-20b-1:0",
        system=[{"text": get_conversation_prompt(CONVERSATION_TEMPLATES[client], appointment_data, APPOINTMENT_BOOKED_INDICATOR[client], **kwargs)}],
        messages=history,
        inferenceConfig={"maxTokens": MAX_OUTPUT_TOKENS},
        additionalModelRequestFields={
            "reasoning_effort": "low"
        }
    )

# def stream_conversation_gpt_oss_20b(history: list, appointment_data: dict, client: Client, **kwargs):
#     messages = [get_conversation_prompt(CONVERSATION_TEMPLATES[client], appointment_data, APPOINTMENT_BOOKED_INDICATOR[client], **kwargs)] + history
#     # Use Bedrock AI to compare the sections and generate insights
#     response = bedrock.converse_stream(
#         modelId = "openai.gpt-oss-20b-1:0",
#         messages=messages,
#         inferenceConfig={
#             "maxTokens": MAX_OUTPUT_TOKENS, 
#             "temperature": 0.7
#         },
#         additionalModelRequestFields={
#             "reasoning_effort": "low"
#         }
#     )
    
#     stream = response.get('stream')
#     if stream:
#         for stream_event in stream:
#             if 'contentBlockDelta' in stream_event:
#                 delta = stream_event['contentBlockDelta']['delta']
#                 if 'text' in delta:
#                     text_chunk = delta['text']
#                     apigateway.post_to_connection(
#                         ConnectionId=connection_id,
#                         Data=json.dumps({'type': 'chunk', 'data': text_chunk})
#                     )
                    
#             elif 'messageStop' in stream_event:
#                 # Stream finished
#                 break
#     apigateway.post_to_connection(
#         ConnectionId=connection_id,
#         Data=json.dumps({'type': 'complete'})
#     )
