from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import numpy as np

app = FastAPI()

# Load trained model
model = joblib.load("model.pkl")


class PredictionInput(BaseModel):
    crop: str
    state: str


@app.post("/predict")
def predict(data: PredictionInput):

    months = range(1, 13)
    predictions = []

    for month in months:
        # Example feature vector
        # Replace with real feature encoding
        features = np.array([[month, 0, 0]])  

        price = model.predict(features)[0]

        predictions.append({
            "month": month,
            "predicted_price": float(price)
        })

    return {
        "crop": data.crop,
        "state": data.state,
        "monthly_predictions": predictions
    }
