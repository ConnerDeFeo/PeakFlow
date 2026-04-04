import time
import logging
from typing import Any
from config import twilio_conversations
    

logger = logging.getLogger(__name__)

class DynamoDB():
    def __init__(self, table: Any):
        self.table = table
    
    def get_conversation_history(self, call_sid: str) -> list:
        resp = twilio_conversations.get_item(Key={"call_sid": call_sid})
        return resp.get("Item", {}).get("history", [])


    def save_conversation(self, call_sid: str, history: list, appointment_booked: bool = False):
        twilio_conversations.put_item(Item={
            "call_sid": call_sid,
            "history": history,
            "appointment_booked": appointment_booked,
            "expires_at": int(time.time()) + 3600
        })

    def get_appointment_data(self, phone_number: str, default: dict) -> dict:
        resp = self.table.get_item(Key={"customer_phone_number": phone_number})
        if "Item" in resp:
            return resp["Item"]
        return default.copy()


    def save_appointment_data(self, phone_number: str, data: dict):
        clean_data = {k: v for k, v in data.items() if v is not None}
        self.table.put_item(Item={
            "customer_phone_number": phone_number,
            **clean_data
        })
        logger.info(f"Saved appointment data for {phone_number}: {clean_data}")