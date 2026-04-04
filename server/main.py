import logging
from fastapi import FastAPI
from server.routes.rochester_roofing.incoming_call_handler_roofing_rochester import router as twilio_router
from server.routes.rochester_roofing.websocket_handler_roofing_rochester import router as ws_router

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logging.getLogger("botocore").setLevel(logging.WARNING)
logging.getLogger("boto3").setLevel(logging.WARNING)

app = FastAPI()
app.include_router(twilio_router)
app.include_router(ws_router)