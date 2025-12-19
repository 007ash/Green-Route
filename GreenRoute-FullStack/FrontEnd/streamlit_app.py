import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000/predict"

st.set_page_config(page_title="GreenRoute", page_icon="🌱")

st.title("🌍 GreenRoute – Carbon Optimized Travel Planner")
st.write("Find the most carbon-efficient travel route using ML.")

st.sidebar.header("Route Details")

distance = st.sidebar.number_input("Distance (km)", 1.0, 100.0, 10.0)
speed = st.sidebar.number_input("Average Speed (km/h)", 10.0, 120.0, 40.0)

vehicle = st.sidebar.selectbox("Vehicle Type", ["car", "bike"])
traffic = st.sidebar.selectbox("Traffic Level", ["low", "medium", "high"])

vehicle_map = {"Car": 1500, "Bike": 150}
traffic_map = {"Low": 1.0, "Medium": 1.4, "High": 2.5}

if st.button("🌱 Find Green Route"):
    payload = {
        "routes":[
        {
            "distance": float(round(distance,2)),
            "avg_speed": float(round(speed,2)),
            "vehicle": str(vehicle),
            "traffic": str(traffic)
        }
        ]
    }

    with st.spinner("Predicting CO₂ emission..."):
        response = requests.post(API_URL, json=payload)
    
    st.write("Sending payload:", payload)

    if response.status_code == 200:
        result = response.json()
        st.success(
            f"✅ Predicted CO₂ Emission: **{result['all_routes']} g**"
            f"✅ Predicted CO₂ Emission: **{result['recommended_green_route']} g**"
            

        )
    else:
        st.error("❌ Backend API error")
