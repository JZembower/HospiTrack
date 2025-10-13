import pandas as pd
from geopy.geocoders import Nominatim
import streamlit as st

@st.cache_data
def load_data(path: str):
    df = pd.read_csv(path)
    if "lat" not in df.columns or "lon" not in df.columns:
        geolocator = Nominatim(user_agent="er_app")
        df["full_address"] = df["detail_address"] + ", " + df["detail_city"] + ", " + df["detail_state"]
        df["lat"], df["lon"] = zip(*df["full_address"].apply(lambda addr: _geocode(addr, geolocator)))
        df.to_csv(path, index=False)
    return df

# Helper to geocode an address
def _geocode(addr, geolocator):
    loc = geolocator.geocode(addr)
    return (loc.latitude, loc.longitude) if loc else (None, None)