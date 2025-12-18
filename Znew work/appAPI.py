from fastapi import FastAPI
import joblib
import numpy as np

app = FastAPI()

model = joblib.load('model/greenroute_model.pkl')

@app.post("/predict")
def predict_co2(data: dict):
    features = np.array([[
        data["distance_km"],
        data["avg_speed_kmph"],
        data["vehicle_type"],
        data["traffic_level"]
    ]])

    co2 = model.predict(features)[0]

    return {
        "predicted_co2_emission": round(float(co2), 2)
    }