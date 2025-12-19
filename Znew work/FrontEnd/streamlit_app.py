import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000/predict"

st.set_page_config(page_title="GreenRoute", page_icon="🌱")

st.title("🌍 GreenRoute – Carbon Optimized Travel Planner")
st.write("Find the most carbon-efficient travel route using ML.")

st.sidebar.header("Route Details")

distance = st.sidebar.number_input("Distance (km)", 1.0, 100.0, 10.0)
speed = st.sidebar.number_input("Average Speed (km/h)", 10.0, 120.0, 40.0)

vehicle = st.sidebar.selectbox("Vehicle Type", ["Car", "Bike"])
traffic = st.sidebar.selectbox("Traffic Level", ["Low", "Medium", "High"])

vehicle_map = {"Car": 0, "Bike": 1}
traffic_map = {"Low": 0, "Medium": 1, "High": 2}

if st.button("🌱 Find Green Route"):
    payload = {
        "distance_km": distance,
        "avg_speed_kmph": speed,
        "vehicle_type": vehicle_map[vehicle],
        "traffic_level": traffic_map[traffic],
    }

    with st.spinner("Predicting CO₂ emission..."):
        response = requests.post(API_URL, json=payload)

    if response.status_code == 200:
        result = response.json()
        st.success(
            f"✅ Predicted CO₂ Emission: **{result['predicted_co2_emission']} g**"
        )
    else:
        st.error("❌ Backend API error")
