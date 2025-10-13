import streamlit as st
import numpy as np
from modules.data_loader import load_data
from modules.geolocation import safe_geocode, validate_location, add_distance
from modules.map_display import render_map
from modules.sorting_logic import prepare_mortality_sort, sort_by_selected_option, parse_mortality
from modules.ui_components import render_sort_buttons, display_hospital_cards, display_chief_complaint_info

# setting page config
st.set_page_config(page_title="HospiTrack", layout="centered")

# --- Data Loading ---
df = load_data("Data and Cleaning/Transformed Data/midwest_er_transformed_final.csv")

# --- UI ---
st.title("Welcome to HospiTrack 🏥")
st.subheader("Find the best ER near you")
st.markdown(
    """
    1. Enter your address or place name in the search box.
    2. The map will show the 10 closest hospitals in the U.S. Midwest.
    3. Click a hospital marker for more info.
    4. View and sort hospitals by quality, wait times, patient ratings, and mortality contribution.
    5. You can also filter quality scores based on your chief complaint.
    """
)

# --- User Input ---
address = st.text_input("Enter address:", "Chicago, IL")

# --- Geolocation & Distance Calculation ---
with st.spinner("🔍 Finding your location..."):
    location = safe_geocode(address)
    validated = validate_location(location)
    if validated:
        st.success(f"📍 Location validated: {validated.address}")
        user_lat, user_lon = validated.latitude, validated.longitude
    else:
        user_lat, user_lon = 41.8781, -87.6298

df = add_distance(df, user_lat, user_lon)
closest = df.nsmallest(10, "distance_km").copy()
render_map(closest, user_lat, user_lon)

# --- CSS for Display ---
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

# --- Sorting Metrics ---
sort_options = {
"total_quality_points": "Quality",
"detail_avg_time_in_ed_minutes": "ED Time",
"detail_overall_patient_rating_points": "Patient Rating",
"mortality_overall_contribution": "Mortality"
}

if "selected_sort" not in st.session_state:
    st.session_state.selected_sort = "total_quality_points"

cols = st.columns(len(sort_options))
render_sort_buttons(sort_options)

# --- Chief Complaint Adjustment ---
complaint_map = {
    "Overall": ["total_quality_points"],
    "Chest Pain": ["adj_total_heartattack"],
    "Heart Attack": ["adj_total_heartattack"],
    "Slurred Speech": ["adj_total_stroke"],
    "Facial Droop": ["adj_total_stroke"],
    "Stroke": ["adj_total_stroke"],
    "Shortness of Breath": ["adj_total_pneu"],
    "Trouble Breathing": ["adj_total_pneu"],
    "Cough": ["adj_total_pneu"],
    "Fever": ["adj_total_pneu"],
}

st.markdown("")
chief_complaint = display_chief_complaint_info(complaint_map)
df, quality_label = sort_by_selected_option(complaint_map, chief_complaint,df)
closest["adjusted_quality_points"] = closest[complaint_map[chief_complaint]]
st.markdown(f"**Sorting by:** {sort_options[st.session_state.selected_sort]}")

# --- Data Preparation & Display ---
closest = prepare_mortality_sort(closest)
# Sort top hospitals by chosen metric
closest["detail_avg_time_in_ed_minutes"] = df["detail_avg_time_in_ed_minutes"].replace(0, np.nan)
if st.session_state.selected_sort == "detail_avg_time_in_ed_minutes":
    top_5 = closest.sort_values(by=st.session_state.selected_sort, ascending=True, na_position='last').head(5)
elif st.session_state.selected_sort == "mortality_overall_contribution":
    top_5 = closest.sort_values(by=["mortality_order", "mortality_sort_value"], ascending=[True, False]).head(5)
else:
    top_5 = closest.sort_values(by=st.session_state.selected_sort, ascending=False).head(5)

display_hospital_cards(top_5, quality_label)