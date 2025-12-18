from fastapi import FastAPI
import joblib
import numpy as np

app = FastAPI()

model = joblib.load('model/greenroute_model.pkl')

@app.post("/predict")
def predict_co2(data: dict):
    vehicle_weight_map = {'car': 1500, 'bike': 150}
    traffic_impact_map = {'low':1.0, 'medium':1.4, 'high':2.5}
    vehicle_weight = vehicle_weight_map.get(data['vehicle'])
    traffic_impact = traffic_impact_map.get(data['traffic'])
    data['vehicle'] = vehicle_weight 
    data['traffic'] = traffic_impact
    data['congestion_factor'] = data['traffic']*data['distance']
    data['effective_speed'] = data['avg_speed'] / data['traffic']
    data['stress_score'] = data['vehicle'] * data['congestion_factor'] 

    features = np.array([[
        data["distance"],
        data["avg_speed"],
        data["vehicle"],
        data["traffic"],
        data["congestion_factor"],
        data["effective_speed"],
        data["stress_score"]
    ]])

    co2 = model.predict(features)[0]

    return {"co2_emission": round(float(co2), 2)}