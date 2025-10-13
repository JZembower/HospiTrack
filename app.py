import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from geopy.exc import GeocoderTimedOut
import time
import numpy as np

# Load hospital data
@st.cache_data
def load_data():
    df = pd.read_csv(r"Data and Cleaning\Transformed Data\midwest_er_transformed_final.csv")
    # Ensure lat/lon exists
    if "lat" not in df.columns or "lon" not in df.columns:
        geolocator = Nominatim(user_agent="er_app")
        df["full_address"] = df["detail_address"] + ", " + df["detail_city"] + ", " + df["detail_state"] + " " + df["detail_zip"].astype(str)
        lats, lons = [], []
        for addr in df["full_address"]:
            try:
                loc = geolocator.geocode(addr)
                if loc:
                    lats.append(loc.latitude)
                    lons.append(loc.longitude)
                else:
                    lats.append(None)
                    lons.append(None)
            except:
                lats.append(None)
                lons.append(None)
        df["lat"] = lats
        df["lon"] = lons
        df.to_csv(r"Data and Cleaning\Transformed Data\midwest_er_transformed_final.csv", index=False)  # cache back
    return df

df = load_data()
st.set_page_config(
page_title="HospiTrack",
page_icon="📊",
layout="centered", 
)

st.title("Welcome to HospiTrack 🏥")
st.subheader("Find the best ER near you")
st.markdown(
    """
    1. Enter your address or place name in the search box.
    2. The map will show the 10 closest hospitals in the U.S. Midwest.
    3. Click a hospital marker for more info and a link to Google Maps directions.
    4. View and sort hospitals by quality, wait times, patient ratings, and mortality contribution.
    5. You can also filter quality scores based on your chief complaint.
    """
)

MIDWEST_STATES = {
    "Illinois", "Indiana", "Iowa", "Kansas", "Michigan", "Minnesota",
    "Missouri", "Nebraska", "North Dakota", "Ohio", "South Dakota", "Wisconsin"
}

# Location search
st.subheader("Search your address")

def safe_geocode(address, retries=3):
    for i in range(retries):
        try:
            return geolocator.geocode(address, timeout=10)
        except GeocoderTimedOut:
            if i < retries - 1:
                time.sleep(2)
                continue
            else:
                st.error("⏱️ Geocoding service timed out. Please try again.")
                return None
        except Exception:
            return None

def validate_location(location):
    """Validate that a geocoded location lies within the U.S. Midwest."""
    if not location:
        st.error("❌ Could not find that location. Please try again.")
        return None

    # st.write(location.address)
    # Extract structured components safely
    address = location.address.split(", ")
    state = address[-2]
    country = address[-1]
    
    # Handle missing or unexpected country/state data
    if not country or "United States" not in country:
        st.error("🌍 Currently limited to U.S. locations only. Defaulting to Chicago, IL.")
        return None

    if not state:
        st.error("⚠️ Could not determine the state for this location. Defaulting to Chicago, IL.")
        return None

    # Check if it's in the Midwest
    if state not in MIDWEST_STATES:
        st.error(f"🚫 Sorry, {state} is outside the Midwest region. Defaulting to Chicago, IL.")
        return None

    return location


user_lat, user_lon = 41.8781, -87.6298  # default Chicago

address = st.text_input("Enter address or place name:", "Chicago, IL")
if address:
    geolocator = Nominatim(user_agent="er_app")
    with st.spinner("🔍 Finding your location..."):
        location = safe_geocode(address)
        validated_location = validate_location(location)
        if validated_location:
            st.success(f"📍 Location validated: {validated_location.address}")
            user_lat = validated_location.latitude
            user_lon = validated_location.longitude
    # st.success(f"Selected location: {validate_location.address}")

# if address:
#     geolocator = Nominatim(user_agent="er_app")
#     loc = safe_geocode(address)
#     if loc:
#         user_lat, user_lon = loc.latitude, loc.longitude
#         st.success(f"Selected location: {loc.address}")
#     else:
#         print("Geocoding failed")

# Compute distances
df["distance_km"] = df.apply(
    lambda row: geodesic((user_lat, user_lon), (row["lat"], row["lon"])).km
    if pd.notnull(row["lat"]) else float("inf"), axis=1
)

# Closest 10 hospitals
closest_10 = df.nsmallest(10, "distance_km").copy()

# Create map
m = folium.Map(location=[user_lat, user_lon], zoom_start=11)
folium.Marker([user_lat, user_lon], tooltip="You are here", icon=folium.Icon(color="blue")).add_to(m)

for _, row in closest_10.iterrows():
    tooltip_text = row["hospital_name"]
    popup_html = f"""
    <b>{row['hospital_name']}</b><br>
    {row['detail_address']}, {row['detail_city']}, {row['detail_state']} {row['detail_zip']}<br>
    Distance: {row['distance_km']:.2f} km<br>
    Quality Points: {row['total_quality_points']}
    """
    folium.Marker(
        [row["lat"], row["lon"]],
        tooltip=tooltip_text,
        popup=popup_html,
        icon=folium.Icon(color="red", icon="plus-sign")
    ).add_to(m)

st_folium(m, width=700, height=500, returned_objects=[])

# ---- Sorting & pretty display section ----

st.subheader("🏥 Top Nearby Hospitals")
st.markdown("<style>" + """
    .sort-buttons { display: flex; gap: 15px; margin-bottom: 15px; justify-content: center; }
    .sort-btn {
        background-color: #f0f2f6;
        border: 1px solid #d1d5db;
        border-radius: 8px;
        padding: 6px 14px;
        font-size: 14px;
        cursor: pointer;
        transition: all 0.2s;
    }
    .sort-btn:hover { background-color: #e0e3e8; }
    .hospital-card {
        background-color: #fafafa;
        border-radius: 10px;
        border: 1px solid #ddd;
        padding: 12px 18px;
        margin-bottom: 12px;
        box-shadow: 1px 2px 3px rgba(0,0,0,0.05);
    }
    .hospital-name {
        font-weight: 600;
        color: #2b2b2b;
        font-size: 16px;
        margin-bottom: 4px;
    }
    .hospital-details {
        color: #555;
        font-size: 13px;
        margin-bottom: 6px;
    }
    .metric {
        font-size: 13px;
        color: #333;
        padding-left: 4px;
    }
"""+ "</style>", unsafe_allow_html=True)


complaint_map = {
    "Overall": ["total_quality_points"],
    "Chest Pain": ["adj_total_heartattack"],
    "Heart Attack": ["adj_total_heartattack", "detail_mortality_overall_percent"],
    "Slurred Speech": ["adj_total_stroke"],
    "Facial Droop": ["dadj_total_stroke"],
    "Stroke": ["adj_total_stroke"],
    "Shortness of Breath": ["adj_total_heartattack", "adj_total_pneu"],
    "Trouble Breathing": ["adj_total_heartattack", "adj_total_pneu"],
    "Cough": ["adj_total_pneu"],
    "Fever": ["adj_total_pneu"],
}


# Sort buttons
# cols = st.columns(4)
sort_options = {
"total_quality_points": "Quality",
"detail_avg_time_in_ed_minutes": "ED Time",
"detail_overall_patient_rating_points": "Patient Rating",
"mortality_overall_contribution": "Mortality"
}

if "selected_sort" not in st.session_state:
    st.session_state.selected_sort = "total_quality_points"

# selected_sort = st.session_state.get("selected_sort", "total_quality_points")

# for i, (key, label) in enumerate(sort_options.items()):
#     if cols[i].button(f"⬍ {label}"):
#         selected_sort = key
#         st.session_state["selected_sort"] = key

cols = st.columns(len(sort_options))

# for i, (key, label) in enumerate(sort_options.items()):
#     # Highlight active button by changing its color with Markdown styling
#     button_color = (
#         "background-color:#0066cc;color:white;border:none;"
#         if st.session_state.selected_sort == key
#         else "background-color:#f0f2f6;color:black;border:none;"
#     )
#     # Inline CSS buttons using Markdown (st.button isn’t styleable)
#     button_html = f"""
#     <button style="{button_color}padding:8px 14px;border-radius:8px;cursor:pointer;width:100%;">
#         ↑ {label}
#     </button>
#     """
#     if cols[i].markdown(button_html, unsafe_allow_html=True):
#         # st.session_state.selected_sort = key
#         st.session_state["selected_sort"] = key

for i, (key, label) in enumerate(sort_options.items()):
    is_active = st.session_state.selected_sort == key
    with cols[i]:
        if st.button(
            f"↑ {label}",
            key=f"btn_{key}",
            use_container_width=True,
        ):
            st.session_state.selected_sort = key

st.markdown("")
chief_complaint = st.selectbox(
    "Quality with Chief Complaint:",
    list(complaint_map.keys()),
    index=0,
)

if complaint_map[chief_complaint]:
    adjusted_col = complaint_map[chief_complaint]
    df["adjusted_quality_points"] = df[adjusted_col]
    quality_label = f"Quality Points (adjusted for {chief_complaint})"
else:
    df["adjusted_quality_points"] = df["total_quality_points"]
    quality_label = "Overall Quality Points"

closest_10["adjusted_quality_points"] = closest_10[adjusted_col]

st.markdown(f"**Sorting by:** {sort_options[st.session_state.selected_sort]}")
# selected_sort = st.session_state.selected_sort
# Sort top hospitals by chosen metric
closest_10["detail_avg_time_in_ed_minutes"] = df["detail_avg_time_in_ed_minutes"].replace(0, np.nan)
if st.session_state.selected_sort == "detail_avg_time_in_ed_minutes" or st.session_state.selected_sort == "mortality_overall_contribution":
    top_5 = closest_10.sort_values(by=st.session_state.selected_sort, ascending=True, na_position='last').head(5)
else:
    top_5 = closest_10.sort_values(by=st.session_state.selected_sort, ascending=False).head(5)

# Pretty display
for _, row in top_5.iterrows():
    gmaps_url = f"https://www.google.com/maps/search/?api=1&query={row['lat']},{row['lon']}"
    if pd.isna(row['detail_avg_time_in_ed_minutes']):
        row['detail_avg_time_in_ed_minutes'] = "ED wait time data not available"
    else:
        hours, mins = int(row['detail_avg_time_in_ed_minutes'] // 60), int(row['detail_avg_time_in_ed_minutes'] % 60)
        row['detail_avg_time_in_ed_minutes'] = f"{hours} hours {mins} mins"

    st.markdown(f"""
    <div class="hospital-card">
        <div class="hospital-name">🏥 {row['hospital_name']}</div>
        <div class="hospital-details">
            📍 {row['detail_address']}, {row['detail_city']}, {row['detail_state']} {row['detail_zip']}<br> 
            📌 <a href="{gmaps_url}" target="_blank">Open in Google Maps</a>
        </div>
        <div class="metric">⭐ {quality_label}: {row['adjusted_quality_points']}</div>
        <div class="metric">⏱️ ED Wait Times: {row["detail_avg_time_in_ed_minutes"]}</div>
        <div class="metric">💬 Patient Rating Points: {row['detail_overall_patient_rating_points']}</div>
        <div class="metric">⚕️ Mortality Contribution: {row['mortality_overall_contribution']}</div>
        <div class="metric">🏅 Top Procedures: {row['Top_Procedures']}</div>
    </div>
    """, unsafe_allow_html=True)