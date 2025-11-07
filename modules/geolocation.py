# modules/geolocation.py
import logging
import time
from typing import Optional, Tuple

import pandas as pd
from geopy.distance import geodesic
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
import requests

USER_AGENT = "HospiTrack/0.1 (contact: jr.zembower@gmail.com)"  # replace with your contact
logger = logging.getLogger(__name__)

MIDWEST_STATES = {
    "Illinois", "Indiana", "Iowa", "Kansas", "Michigan", "Minnesota",
    "Missouri", "Nebraska", "North Dakota", "Ohio", "South Dakota", "Wisconsin"
}

def geocode_fallback(zip: Optional[str] = None, address: Optional[str] = None) -> Tuple[float, float]:
    """
    Minimal geocoder using OpenStreetMap Nominatim. Not for heavy prod use.
    Replace with a key-based provider for reliability.
    """
    q = zip or address
    if not q:
        raise ValueError("No query provided")
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": q, "format": "json", "limit": 1, "addressdetails": 0}
    headers = {"User-Agent": USER_AGENT}
    resp = requests.get(url, params=params, headers=headers, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    if not data:
        raise ValueError("Location not found")
    time.sleep(1)  # basic politeness delay
    return float(data[0]["lat"]), float(data[0]["lon"])

def safe_geocode(address: str, retries: int = 3, timeout: int = 10):
    """
    Try to geocode `address` using geopy.Nominatim with a simple retry loop.
    Returns the location object if successful, or None on failure.
    """
    if not address:
        return None

    geolocator = Nominatim(user_agent="hospi_track_app")
    for attempt in range(1, retries + 1):
        try:
            return geolocator.geocode(address, timeout=timeout)
        except GeocoderTimedOut:
            logger.warning("Geocoder timed out for address %s (attempt %d/%d)", address, attempt, retries)
            if attempt < retries:
                time.sleep(2)
        except GeocoderServiceError as e:
            logger.error("Geocoder service error for address %s: %s", address, e)
            break
        except Exception as e:
            logger.exception("Unexpected error during geocoding for %s: %s", address, e)
            break
    return None

def validate_location(location, restrict_to_midwest: bool = False) -> Optional[object]:
    """
    Optionally restrict geocoded result to Midwest states. For nationwide app,
    set restrict_to_midwest=False.
    """
    if not location:
        return None
    if not restrict_to_midwest:
        return location

    try:
        address = location.address or ""
    except Exception:
        return None

    if "United States" not in address:
        return None
    if not any(state in address for state in MIDWEST_STATES):
        return None
    return location

def add_distance(df: pd.DataFrame, user_lat: float, user_lon: float) -> pd.DataFrame:
    """
    Add a 'distance_km' column to `df` computed from (user_lat, user_lon).
    Rows with missing lat/lon will have distance = inf.
    """
    def compute(row):
        lat = row.get("lat")
        lon = row.get("lon")
        if pd.notnull(lat) and pd.notnull(lon):
            try:
                return geodesic((user_lat, user_lon), (lat, lon)).km
            except Exception as e:
                logger.debug("Error computing distance for row index %s: %s", getattr(row, "name", "?"), e)
                return float("inf")
        return float("inf")

    out = df.copy()
    out["distance_km"] = out.apply(compute, axis=1)
    return out