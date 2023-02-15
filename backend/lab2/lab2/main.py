from os import getcwd
from os.path import join

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

import joblib

model_filename = "model_pipeline.pkl"
model_path = join(getcwd(), model_filename)

PIPELINE = joblib.load(model_path)

app = FastAPI()

@app.get("/health")
async def health():
    return {"status": "healthy"}


# Raises 422 if bad parameter automatically by FastAPI
@app.get("/hello")
async def hello(name: str):
    return {"message": f"Hello {name}"}


# /docs endpoint is defined by FastAPI automatically
# /openapi.json returns a json object automatically by FastAPI

class Item(BaseModel):
    MedInc: float
    HouseAge: float
    AveRooms: float
    AveBedrms: float
    Population: float
    AveOccup: float
    Latitude: float
    Longitude: float

    def to_X(self):
        return [self.MedInc,
                self.HouseAge,
                self.AveRooms,
                self.AveBedrms,
                self.Population,
                self.AveOccup,
                self.Latitude,
                self.Longitude]

class Prediction(BaseModel):
    prediction: float


@app.post("/predict/")
async def predict(item: Item):
    X = item.to_X()
    predicted_value = PIPELINE.predict([X])[0]
    prediction = Prediction(prediction=predicted_value)
    return prediction


