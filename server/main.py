import logging
from fastapi import FastAPI
from routes import router as twilio_router
from dotenv import load_dotenv
load_dotenv()

load_dotenv()

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logging.getLogger("botocore").setLevel(logging.WARNING)
logging.getLogger("boto3").setLevel(logging.WARNING)

app = FastAPI()
app.include_router(twilio_router)