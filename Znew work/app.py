from fastapi import FastAPI
import joblib
import numpy as np

app = FastAPI()

model = joblib.load('model/greenroute_model.pkl')

@app.post("/predict")
def predict_co2(data: dict):
    vechile_weight_map = {'car': 1500, 'bike': 150}
    traffic_impact_map = {'low':1.0, 'medium':1.4, 'high':2.5}
    congestion_factor = traffic_impact_map[data["traffic"]] * data["distance"]
    effective_speed = data["avg_speed"] / traffic_impact_map[data["traffic"]]
    stress_score = vechile_weight_map[data["vehicle"]] * congestion_factor
    features = np.array([[
        data["distance"],
        data["avg_speed"],
        vechile_weight_map[data["vehicle"]],
        traffic_impact_map[data["traffic"]],
        congestion_factor,
        effective_speed,
        stress_score
    ]])

    co2 = model.predict(features)[0]

    return {
        "predicted_co2_emission": round(float(co2), 2)
    }