import streamlit as st
import pandas as pd
import joblib
import pickle

@st.cache_resource
def load_model():
    return joblib.load("model/model_pipeline.pkl")


@st.cache_data
def load_pickles():
    with open("model/origins.pkl", "rb") as f:
        origins = pickle.load(f)
    with open("model/destinations.pkl", "rb") as f:
        destinations = pickle.load(f)
    with open("model/origin_dest_distance.pkl", "rb") as f:
        distance_map = pickle.load(f)
    return origins, destinations, distance_map

model_pipeline = load_model()
origins, destinations, distance_map = load_pickles()

st.set_page_config(page_title="GreenRoute", page_icon="🌿")

st.markdown("""
    <style>
    .main {
        background-color: #f4f8f4;
    }
    .title {
        font-size: 2.5rem;
        font-weight: 700;
        color: #2c7a4b;
    }
    .subheader {
        font-size: 1.3rem;
        color: #555;
    }
    .stButton>button {
        background-color: #2c7a4b;
        color: white;
        border-radius: 8px;
        font-size: 16px;
        padding: 10px 16px;
    }
    .stButton>button:hover {
        background-color: #25663c;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<div class='title'>🌿 GreenRoute</div>", unsafe_allow_html=True)
st.markdown("<div class='subheader'>Carbon-Optimized Travel Planner</div>", unsafe_allow_html=True)
st.markdown("---")

with st.form("route_form"):
    col1, col2 = st.columns(2)
    with col1:
        origin = st.selectbox("📍 Select Origin", sorted(origins))
        vehicle = st.selectbox("🚗 Vehicle Type", ["Petrol Car", "Diesel Car", "Electric Car", "Bus", "Bike", "Walk", "Train"])
        weather = st.selectbox("⛅ Weather Condition", ["Clear", "Rainy", "Snowy", "Foggy"])
    with col2:
        destination = st.selectbox("📍 Select Destination", sorted(destinations))
        traffic = st.selectbox("🚦 Traffic Level", ["Low", "Medium", "High"])
        temp = st.number_input("🌡️ Temperature (°C)", value=25.0)
        speed = st.number_input("🚘 Average Speed (km/h)", value=50.0)

    submitted = st.form_submit_button("🔍 Predict Emission")

if submitted:
    route_key = (origin, destination)
    if route_key in distance_map:
        distance = distance_map[route_key]
        input_data = pd.DataFrame([{
            "distance": distance,
            "vehicle": vehicle,
            "speed": speed,
            "traffic": traffic,
            "weather": weather,
            "temp": temp
        }])

        try:
            prediction = model_pipeline.predict(input_data)[0]

            st.success("✅ Emission prediction successful!")

            col1, col2 = st.columns(2)
            with col1:
                st.metric(label="🌍 Estimated CO₂ Emission", value=f"{prediction:.2f} grams")
            with col2:
                st.metric(label="🛣️ Distance", value=f"{distance:.2f} km")

            st.markdown("### 🧭 Route Info")
            st.write(f"**From:** `{origin}` → **To:** `{destination}`")
            st.markdown("### 🔍 Model Input Used")
            st.dataframe(input_data)

        except Exception as e:
            st.error(f"❌ Prediction failed: {e}")
    else:
        st.warning("⚠️ Distance data for this route not found in the dataset.")

