from fastapi import FastAPI
from pydantic import BaseModel
import joblib

class ClientData(BaseModel):
    first_name: str
    second_name: str
    house_id: int
    passport: int

app = FastAPI()
model = joblib.load("model_pipeline.joblib")

@app.post("/score")
def score(data: ClientData):
    features = [data.first_name, data.second_name, data.house_id]
    # тут запрос в бд
    price = model.predict([all_features])[0].item()
    
    return {'price' : price}