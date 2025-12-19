import streamlit as st
import requests
from geopy.geocoders import Nominatim
import folium
from streamlit_folium import st_folium

# ---------------- CONFIG ----------------
API_URL = "http://127.0.0.1:8000/predict"

st.set_page_config(page_title="GreenRoute 🌱", layout="wide")
st.title("🌍 GreenRoute – Carbon Optimized Travel Planner")
st.write("Find the most **carbon-efficient route** between two locations.")

# ---------------- USER INPUT ----------------
col1, col2, col3 = st.columns(3)

with col1:
    source = st.text_input("📍 Source")

with col2:
    destination = st.text_input("🏁 Destination")

with col3:
    vehicle = st.selectbox("🚗 Vehicle Type", ["car", "bike"])

# ---------------- HELPERS ----------------
def get_coordinates(place):
    geolocator = Nominatim(user_agent="greenroute")
    location = geolocator.geocode(place)
    if location is None:
        raise ValueError(f"Could not find location: {place}")
    return location.latitude, location.longitude

def traffic_level(speed):
    if speed > 40:
        return "low"
    elif speed > 25:
        return "medium"
    else:
        return "high"

# ---------------- MAIN ----------------
if st.button("🌱 Find Green Route"):
    st.write("Button clicked ✅")
    try:
        # 1️⃣ Geocode source & destination
        src_lat, src_lon = get_coordinates(source)
        dst_lat, dst_lon = get_coordinates(destination)
        st.write("Source coords:", src_lat, src_lon)
        st.write("Destination coords:", dst_lat, dst_lon)

        # 2️⃣ Get multiple routes from OSRM
        osrm_url = (
            f"http://router.project-osrm.org/route/v1/driving/"
            f"{src_lon},{src_lat};{dst_lon},{dst_lat}"
            f"?alternatives=true&overview=full&geometries=geojson"
        )

        osrm_response = requests.get(osrm_url).json()
        routes = osrm_response["routes"]
        st.write("OSRM raw response:", osrm_response)
        st.write("Number of routes:", len(routes))

        processed_routes = []

        # 3️⃣ Feature extraction for API
        for idx, r in enumerate(routes, start=1):
            distance_km = r["distance"] / 1000
            duration_hr = r["duration"] / 3600
            avg_speed = distance_km / duration_hr
            traffic = traffic_level(avg_speed)

            processed_routes.append({
                "route_id": idx,
                "distance": round(distance_km, 2),
                "avg_speed": round(avg_speed, 2),
                "vehicle": vehicle,
                "traffic": traffic,
                "geometry": r["geometry"]
            })

        # 4️⃣ Prepare API payload (EXACT MATCH)
        payload = {
            "routes": [
                {
                    "distance": r["distance"],
                    "avg_speed": r["avg_speed"],
                    "vehicle": r["vehicle"],
                    "traffic": r["traffic"]
                }
                for r in processed_routes
            ]
        }

        # 5️⃣ Call FastAPI
        api_response = requests.post(API_URL, json=payload).json()

        all_routes = api_response["all_routes"]
        recommended = api_response["recommended_green_route"]
        best_route_id = recommended["route_id"]

        # 6️⃣ Map visualization
        m = folium.Map(location=[src_lat, src_lon], zoom_start=13)

        # 🔵 All routes
        for r in processed_routes:
            folium.GeoJson(
                r["geometry"],
                style_function=lambda x: {
                    "color": "blue",
                    "weight": 4,
                    "opacity": 0.6
                }
            ).add_to(m)

        # 🟢 Recommended green route
        best_route = next(
            r for r in processed_routes if r["route_id"] == best_route_id
        )

        folium.GeoJson(
            best_route["geometry"],
            style_function=lambda x: {
                "color": "green",
                "weight": 6
            }
        ).add_to(m)

        st.success("✅ Greenest route successfully identified!")
        st_folium(m, width=900, height=550)

        # 7️⃣ CO₂ Summary
        st.subheader("📊 CO₂ Emissions Comparison")

        for r in all_routes:
            tag = "🌱 RECOMMENDED" if r["route_id"] == best_route_id else ""
            st.write(
                f"Route {r['route_id']} | "
                f"Distance: {r['distance']} km | "
                f"CO₂: {round(r['predicted_co2'], 2)} g {tag}"
            )

    except Exception as e:
        st.error("❌ Error occurred. Please check inputs or API status.")
        st.write(e)
