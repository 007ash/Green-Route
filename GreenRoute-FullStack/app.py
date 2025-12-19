from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import joblib
import numpy as np

app = FastAPI(title="GreenRoute API")

# Load trained model
model = joblib.load("model/greenroute_model.pkl")

class RouteInput(BaseModel):
    distance: float
    avg_speed: float
    vehicle: str      # car / bike
    traffic: str      # low / medium / high


class RoutesRequest(BaseModel):
    routes: List[RouteInput]


@app.get("/")
def home():
    return {"message": "GreenRoute CO2 Prediction API is running"}


@app.post("/predict")
def find_green_route(data: RoutesRequest):

    vehicle_weight_map = {'car': 1500, 'bike': 150}
    traffic_impact_map = {'low': 1.0, 'medium': 1.4, 'high': 2.5}

    results = []

    for idx, route in enumerate(data.routes):

        vehicle_weight = vehicle_weight_map.get(route.vehicle)
        traffic_impact = traffic_impact_map.get(route.traffic)

        congestion_factor = traffic_impact * route.distance
        effective_speed = route.avg_speed / traffic_impact
        stress_score = vehicle_weight * congestion_factor

        features = np.array([[
            route.distance,
            route.avg_speed,
            vehicle_weight,
            traffic_impact,
            congestion_factor,
            effective_speed,
            stress_score
        ]])

        co2 = model.predict(features)[0]

        results.append({
            "route_id": idx + 1,
            "distance": route.distance,
            "predicted_co2": round(float(co2), 2)
        })

    # Select greenest route
    green_route = min(results, key=lambda x: x["predicted_co2"])

    return {
        "all_routes": results,
        "recommended_green_route": green_route
    }
