import time
import logging
from config import Client, TABLES
    

logger = logging.getLogger(__name__)

class DynamoDB():
    def __init__(self, client: Client):
        self.table = TABLES[client]

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