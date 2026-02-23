# import streamlit as st
# import requests
# from geopy.geocoders import Nominatim
# from geopy.extra.rate_limiter import RateLimiter
# import folium
# from streamlit_folium import st_folium

# API_URL = "http://127.0.0.1:8000/predict"

# st.set_page_config(page_title="GreenRoute", layout="wide", page_icon="🌿")
# st.title("GreenRoute – Carbon Optimized Travel Planner")
# st.write("Find the most **carbon-efficient route** between two locations.")

# if "result" not in st.session_state:
#     st.session_state.result = None

# geolocator = Nominatim(user_agent="greenroute_app", timeout=10)
# geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)

# @st.cache_data
# def get_coordinates(place):
#     try:
#         location = geocode(place)
#         if location is None:
#             return None
#         return (location.latitude, location.longitude)
#     except Exception:
#         return None

# def traffic_level(speed):
#     if speed > 40:
#         return "low"
#     elif speed > 25:
#         return "medium"
#     else:
#         return "high"

# # ----------------------------
# # UI Inputs
# # ----------------------------
# col1, col2, col3 = st.columns(3)

# with col1:
#     source = st.text_input("Source", placeholder="e.g., Chennai")

# with col2:
#     destination = st.text_input("Destination", placeholder="e.g., Coimbatore")

# with col3:
#     vehicle = st.selectbox("Vehicle Type", ["car", "bike"])

# # ----------------------------
# # Find Green Route Button
# # ----------------------------
# if st.button("Find Green Route"):
#     if not source or not destination:
#         st.warning("Please enter both source and destination.")
#     else:
#         with st.spinner("Calculating green route... 🌿"):

#             # Get Coordinates
#             src_coords = get_coordinates(source)
#             dst_coords = get_coordinates(destination)

#             if src_coords is None:
#                 st.error(f"Could not find location: {source}")
#                 st.stop()

#             if dst_coords is None:
#                 st.error(f"Could not find location: {destination}")
#                 st.stop()

#             src_lat, src_lon = src_coords
#             dst_lat, dst_lon = dst_coords

#             # OSRM Routing
#             osrm_url = (
#                 f"http://router.project-osrm.org/route/v1/driving/"
#                 f"{src_lon},{src_lat};{dst_lon},{dst_lat}"
#                 f"?alternatives=true&overview=full&geometries=geojson"
#             )

#             osrm_response = requests.get(osrm_url).json()

#             if "routes" not in osrm_response:
#                 st.error("Routing API failed.")
#                 st.stop()

#             routes = osrm_response["routes"]

#             processed_routes = []

#             # Process Routes
#             for idx, r in enumerate(routes, start=1):
#                 distance_km = r["distance"] / 1000
#                 duration_hr = r["duration"] / 3600
#                 avg_speed = distance_km / duration_hr
#                 traffic = traffic_level(avg_speed)

#                 processed_routes.append({
#                     "route_id": idx,
#                     "distance": round(distance_km, 2),
#                     "avg_speed": round(avg_speed, 2),
#                     "vehicle": vehicle,
#                     "traffic": traffic,
#                     "geometry": r["geometry"]
#                 })

#             # Backend Payload
#             payload = {
#                 "routes": [
#                     {
#                         "distance": r["distance"],
#                         "avg_speed": r["avg_speed"],
#                         "vehicle": r["vehicle"],
#                         "traffic": r["traffic"]
#                     }
#                     for r in processed_routes
#                 ]
#             }

#             # Call ML Backend
#             api_response = requests.post(API_URL, json=payload).json()

#             best_route_id = api_response["recommended_green_route"]["route_id"]

#             st.session_state.result = {
#                 "processed_routes": processed_routes,
#                 "api_response": api_response,
#                 "src_coords": (src_lat, src_lon),
#                 "best_route_id": best_route_id
#             }

# # ----------------------------
# # Display Results
# # ----------------------------
# if st.session_state.result is not None:

#     data = st.session_state.result

#     processed_routes = data["processed_routes"]
#     api_response = data["api_response"]
#     src_lat, src_lon = data["src_coords"]
#     best_route_id = data["best_route_id"]

#     # Create Map
#     m = folium.Map(location=[src_lat, src_lon], zoom_start=13)

#     # All routes (blue)
#     for r in processed_routes:
#         folium.GeoJson(
#             r["geometry"],
#             style_function=lambda x: {
#                 "color": "blue",
#                 "weight": 4,
#                 "opacity": 0.6
#             }
#         ).add_to(m)

#     # Best route (green)
#     best_route = next(
#         r for r in processed_routes if r["route_id"] == best_route_id
#     )

#     folium.GeoJson(
#         best_route["geometry"],
#         style_function=lambda x: {
#             "color": "green",
#             "weight": 6
#         }
#     ).add_to(m)

#     st.success("✅ Greenest route identified!")
#     st_folium(m, width=900, height=550)

#     # CO2 Comparison
#     st.subheader("📊 CO₂ Emissions Comparison")

#     for r in api_response["all_routes"]:
#         tag = "🌿 RECOMMENDED" if r["route_id"] == best_route_id else ""
#         st.write(
#             f"Route {r['route_id']} | "
#             f"Distance: {r['distance']} km | "
#             f"CO₂: {round(r['predicted_co2'], 2)} g {tag}"
#         )

#     # Reset Button
#     if st.button("🔄 Reset"):
#         st.session_state.result = None

import streamlit as st
import requests
import folium
import pandas as pd
import altair as alt
from geopy.geocoders import Nominatim
from streamlit_folium import st_folium

# --- CONFIGURATION & STYLING ---
st.set_page_config(
    page_title="GreenRoute AI",
    layout="wide",
    page_icon="🌿",
    initial_sidebar_state="expanded"
)

# Custom CSS for a greener, cleaner look
st.markdown("""
    <style>
    .stButton>button {
        background-color: #2E8B57;
        color: white;
        border-radius: 10px;
        height: 3em;
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #3CB371;
        color: white;
    }
    div[data-testid="stMetricValue"] {
        color: #2E8B57;
    }
    h1 {
        color: #1b4332;
    }
    </style>
""", unsafe_allow_html=True)

# --- CONSTANTS ---
API_URL = "http://127.0.0.1:8000/predict"

if "result" not in st.session_state:
    st.session_state.result = None

# --- SIDEBAR INPUTS ---
with st.sidebar:
    st.title("🌿 GreenRoute")
    st.markdown("Optimization Parameters")
    
    source = st.text_input("📍 Origin", placeholder="e.g., Chennai")
    destination = st.text_input("🏁 Destination", placeholder="e.g., Coimbatore")
    
    vehicle = st.selectbox(
        "🚗 Vehicle Type", 
        ["car", "bike"], 
        format_func=lambda x: x.capitalize()
    )
    
    st.markdown("---")
    
    find_btn = st.button("Calculate Eco-Route")
    
    if st.session_state.result:
        if st.button("🔄 Reset Plan"):
            st.session_state.result = None
            st.rerun()

    st.info("💡 **Did you know?** Choosing an optimized route can reduce carbon footprint by up to 15%.")

# --- CORE LOGIC (UNCHANGED) ---
def get_coordinates(place):
    geolocator = Nominatim(user_agent="greenroute")
    location = geolocator.geocode(place)
    if location is None:
        raise ValueError(f"Location not found: {place}")
    return location.latitude, location.longitude

def traffic_level(speed):
    if speed > 40: return "low"
    elif speed > 25: return "medium"
    else: return "high"

# --- MAIN EXECUTION ---
st.title("Carbon Optimized Travel Planner")
st.markdown("Navigate smarter. Save fuel. Save the planet.")

if find_btn:
    if not source or not destination:
        st.error("⚠️ Please enter both source and destination.")
    else:
        with st.spinner("🌍 Analyzing satellite data & calculating emissions..."):
            try:
                # 1. Geocoding
                src_lat, src_lon = get_coordinates(source)
                dst_lat, dst_lon = get_coordinates(destination)

                # 2. OSRM Routing
                osrm_url = (
                    f"http://router.project-osrm.org/route/v1/driving/"
                    f"{src_lon},{src_lat};{dst_lon},{dst_lat}"
                    f"?alternatives=true&overview=full&geometries=geojson"
                )
                
                # Error handling for OSRM
                try:
                    osrm_response = requests.get(osrm_url).json()
                    routes = osrm_response["routes"]
                except Exception as e:
                    st.error("Error fetching routes from OSRM. Service might be busy.")
                    st.stop()

                processed_routes = []

                # 3. Feature Extraction
                for idx, r in enumerate(routes, start=1):
                    distance_km = r["distance"] / 1000
                    duration_hr = r["duration"] / 3600
                    
                    # Avoid division by zero
                    avg_speed = distance_km / duration_hr if duration_hr > 0 else 0
                    traffic = traffic_level(avg_speed)

                    processed_routes.append({
                        "route_id": idx,
                        "distance": round(distance_km, 2),
                        "avg_speed": round(avg_speed, 2),
                        "vehicle": vehicle,
                        "traffic": traffic,
                        "geometry": r["geometry"]
                    })

                # 4. API Payload
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

                # 5. API Call to Model
                try:
                    api_response = requests.post(API_URL, json=payload).json()
                except requests.exceptions.ConnectionError:
                    st.error("❌ Could not connect to the Prediction API (Is uvicorn running?).")
                    st.stop()

                best_route_id = api_response["recommended_green_route"]["route_id"]

                # Store in session
                st.session_state.result = {
                    "processed_routes": processed_routes,
                    "api_response": api_response,
                    "src_coords": (src_lat, src_lon),
                    "dst_coords": (dst_lat, dst_lon), # Added dst for map markers
                    "best_route_id": best_route_id
                }
                
            except ValueError as e:
                st.error(str(e))

# --- DISPLAY DASHBOARD ---
if st.session_state.result is not None:
    data = st.session_state.result
    processed_routes = data["processed_routes"]
    api_response = data["api_response"]
    best_route_id = data["best_route_id"]
    
    # Extract Best Route Data
    best_route_geom = next(r for r in processed_routes if r["route_id"] == best_route_id)
    best_route_stats = next(r for r in api_response["all_routes"] if r["route_id"] == best_route_id)

    # --- TOP METRICS ROW ---
    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric("🌿 Lowest Emissions", f"{round(best_route_stats['predicted_co2'], 2)} g")
    with m2:
        st.metric("📏 Total Distance", f"{best_route_geom['distance']} km")
    with m3:
        st.metric("🚦 Traffic Condition", best_route_geom['traffic'].upper())

    # --- MAP & CHART LAYOUT ---
    col_map, col_stats = st.columns([2, 1])

    with col_map:
        st.subheader("🗺️ Route Visualization")
        
        # Initialize Map
        m = folium.Map(location=data["src_coords"], zoom_start=6, tiles="cartodbpositron")

        # Markers
        folium.Marker(
            data["src_coords"], 
            popup="Start", 
            icon=folium.Icon(color="green", icon="play")
        ).add_to(m)
        
        folium.Marker(
            data["dst_coords"], 
            popup="End", 
            icon=folium.Icon(color="red", icon="flag")
        ).add_to(m)

        # Draw Routes
        for r in processed_routes:
            is_best = r["route_id"] == best_route_id
            
            # Style: Green for best, Gray for others
            color = "#2E8B57" if is_best else "#A9A9A9"
            weight = 6 if is_best else 3
            opacity = 0.9 if is_best else 0.5
            tooltip = f"Route {r['route_id']} {'(Recommended)' if is_best else ''}"

            folium.GeoJson(
                r["geometry"],
                style_function=lambda x, col=color, w=weight, o=opacity: {
                    "color": col, "weight": w, "opacity": o
                },
                tooltip=tooltip
            ).add_to(m)

        st_folium(m, width="100%", height=500)

    with col_stats:
        st.subheader("📊 Comparative Analysis")
        
        # Prepare Data for Chart
        chart_data = pd.DataFrame(api_response["all_routes"])
        chart_data['Type'] = chart_data['route_id'].apply(
            lambda x: 'Recommended' if x == best_route_id else 'Alternative'
        )
        
        # Altair Bar Chart
        chart = alt.Chart(chart_data).mark_bar().encode(
            x=alt.X('route_id:O', title='Route ID'),
            y=alt.Y('predicted_co2:Q', title='CO₂ Emissions (g)'),
            color=alt.Color('Type', scale=alt.Scale(domain=['Recommended', 'Alternative'], range=['#2E8B57', '#bdc3c7'])),
            tooltip=['route_id', 'predicted_co2', 'distance']
        ).properties(height=400)
        
        st.altair_chart(chart, use_container_width=True)
        
        # Text Summary
        st.markdown("### Route Details")
        for r in api_response["all_routes"]:
            icon = "✅" if r["route_id"] == best_route_id else "🔹"
            st.caption(
                f"{icon} **Route {r['route_id']}**: "
                f"{r['distance']}km | {round(r['predicted_co2'], 1)}g CO₂"
            )