from fastapi import FastAPI, Header, HTTPException, Depends
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("API_KEY")

app = FastAPI()

api_key_header = APIKeyHeader(name="x-api-key")


class PredictionInput(BaseModel):
    crop: str
    state: str
    temperature: float
    rainfall: float


def verify_api_key(api_key: str = Depends(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Unauthorized")


@app.post("/predict")
def predict(data: PredictionInput, api_key: str = Depends(verify_api_key)):

    predicted_price = 2000 + data.temperature * 15 - data.rainfall * 3

    return {
        "crop": data.crop,
        "predicted_price": predicted_price
    }
