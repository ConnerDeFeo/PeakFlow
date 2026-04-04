import logging
from fastapi import FastAPI
from routes.rochester_roofing.rochester_roofing_handler import router as twilio_router
from routes.rochester_roofing.rochester_roofing_websocket import router as ws_router

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logging.getLogger("botocore").setLevel(logging.WARNING)
logging.getLogger("boto3").setLevel(logging.WARNING)

app = FastAPI()
app.include_router(twilio_router)
app.include_router(ws_router)