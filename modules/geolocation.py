from geopy.distance import geodesic
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
import time, streamlit as st
import pandas as pd

MIDWEST_STATES = {
    "Illinois", "Indiana", "Iowa", "Kansas", "Michigan", "Minnesota",
    "Missouri", "Nebraska", "North Dakota", "Ohio", "South Dakota", "Wisconsin"
}

# Geocode with retries and error handling
def safe_geocode(address, retries=3):
    geolocator = Nominatim(user_agent="er_app")
    for i in range(retries):
        try:
            return geolocator.geocode(address, timeout=10)
        except GeocoderTimedOut:
            if i < retries - 1:
                time.sleep(2)
            else:
                st.error("⏱️ Geocoding timed out. Try again.")
    return None

# Validate location is in U.S. Midwest
def validate_location(location):
    if not location:
        st.error("❌ Could not find that location.")
        return None
    if "United States" not in location.address:
        st.error("🌍 Currently limited to U.S. locations only. Defaulting to Chicago, IL.")
        return None
    if not any(state in location.address for state in MIDWEST_STATES):
        st.error("🚫 Outside the Midwest region. Defaulting to Chicago, IL.")
        return None
    return location

# Add distance column to DataFrame
def add_distance(df, user_lat, user_lon):
    df["distance_km"] = df.apply(
        lambda row: geodesic((user_lat, user_lon), (row["lat"], row["lon"])).km
        if pd.notnull(row["lat"]) else float("inf"), axis=1
    )
    return df