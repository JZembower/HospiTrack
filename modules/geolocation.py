# modules/geolocation.py
import hashlib
import logging
import time
from collections import OrderedDict
from typing import Optional, Tuple, Union, Dict, Any
from threading import Lock

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


class LRUCache:
    """
    Simple thread-safe LRU cache implementation for geocoding results.
    """
    def __init__(self, max_size: int = 1000):
        self.cache: OrderedDict = OrderedDict()
        self.max_size = max_size
        self.lock = Lock()
    
    def get(self, key: str) -> Optional[Any]:
        with self.lock:
            if key in self.cache:
                # Move to end to mark as recently used
                self.cache.move_to_end(key)
                return self.cache[key]
            return None
    
    def set(self, key: str, value: Any):
        with self.lock:
            if key in self.cache:
                # Update and move to end
                self.cache.move_to_end(key)
            self.cache[key] = value
            # Remove oldest item if over capacity
            if len(self.cache) > self.max_size:
                self.cache.popitem(last=False)


class RateLimiter:
    """
    Rate limiter for Nominatim API calls (1 request per second with exponential backoff).
    """
    def __init__(self, min_interval: float = 1.0):
        self.min_interval = min_interval
        self.last_request_time = 0.0
        self.lock = Lock()
        self.consecutive_failures = 0
    
    def wait(self):
        """Wait if necessary to respect rate limits."""
        with self.lock:
            current_time = time.time()
            elapsed = current_time - self.last_request_time
            if elapsed < self.min_interval:
                sleep_time = self.min_interval - elapsed
                # Apply exponential backoff for consecutive failures
                if self.consecutive_failures > 0:
                    sleep_time *= (2 ** min(self.consecutive_failures, 5))
                time.sleep(sleep_time)
            self.last_request_time = time.time()
    
    def record_success(self):
        """Reset failure counter on successful request."""
        with self.lock:
            self.consecutive_failures = 0
    
    def record_failure(self):
        """Increment failure counter for exponential backoff."""
        with self.lock:
            self.consecutive_failures += 1


# Global instances
_geocode_cache = LRUCache(max_size=1000)
_rate_limiter = RateLimiter(min_interval=1.0)

# Pre-cached common US cities to avoid geocoding delays
COMMON_LOCATIONS = {
    "san francisco, ca": (37.7749, -122.4194),
    "los angeles, ca": (34.0522, -118.2437),
    "new york, ny": (40.7128, -74.0060),
    "chicago, il": (41.8781, -87.6298),
    "houston, tx": (29.7604, -95.3698),
    "phoenix, az": (33.4484, -112.0740),
    "philadelphia, pa": (39.9526, -75.1652),
    "san antonio, tx": (29.4241, -98.4936),
    "san diego, ca": (32.7157, -117.1611),
    "dallas, tx": (32.7767, -96.7970),
    "austin, tx": (30.2672, -97.7431),
    "seattle, wa": (47.6062, -122.3321),
    "boston, ma": (42.3601, -71.0589),
    "miami, fl": (25.7617, -80.1918),
    "atlanta, ga": (33.7490, -84.3880),
    "denver, co": (39.7392, -104.9903),
    "washington, dc": (38.9072, -77.0369),
    "portland, or": (45.5152, -122.6784),
    "las vegas, nv": (36.1699, -115.1398),
    "detroit, mi": (42.3314, -83.0458),
}


def _hash_address(address: str) -> str:
    """
    Privacy-focused: hash addresses for logging without storing raw input.
    """
    return hashlib.sha256(address.encode('utf-8')).hexdigest()[:12]


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


def safe_geocode(
    address: Optional[str] = None,
    lat: Optional[float] = None,
    lon: Optional[float] = None,
    retries: int = 3,
    timeout: int = 30
) -> Optional[object]:
    """
    Enhanced geocoding with three input modes:
    1. address string: geocode via Nominatim
    2. lat/lon tuple: return mock location object
    3. browser geolocation: same as lat/lon
    
    Features:
    - In-memory LRU cache (max 1000 entries)
    - Rate limiting (1 req/sec with exponential backoff)
    - Privacy-focused logging (hashed addresses)
    - Fallback strategies for failures
    
    Args:
        address: Address string to geocode
        lat: Latitude (if providing coordinates directly)
        lon: Longitude (if providing coordinates directly)
        retries: Number of retry attempts
        timeout: Request timeout in seconds
    
    Returns:
        Location object with .latitude and .longitude attributes, or None on failure
    """
    # Mode 2 & 3: Direct lat/lon coordinates (browser geolocation)
    if lat is not None and lon is not None:
        try:
            lat_f = float(lat)
            lon_f = float(lon)
            print(f"[DEBUG safe_geocode] Using direct coordinates: lat={lat_f}, lon={lon_f}")
            # Return a mock location object
            class MockLocation:
                def __init__(self, lat, lon):
                    self.latitude = lat
                    self.longitude = lon
                    self.address = f"Coordinates: {lat:.4f}, {lon:.4f}"
            return MockLocation(lat_f, lon_f)
        except (ValueError, TypeError) as e:
            logger.warning("Invalid lat/lon provided: %s, %s - %s", lat, lon, e)
            print(f"[DEBUG safe_geocode] Invalid lat/lon: {lat}, {lon} - {e}")
            return None
    
    # Mode 1: Address string geocoding
    if not address:
        print(f"[DEBUG safe_geocode] No address or coordinates provided")
        return None
    
    print(f"[DEBUG safe_geocode] Geocoding address: {address}")
    
    # Check pre-cached common locations first (instant, no API call)
    cache_key = address.strip().lower()
    if cache_key in COMMON_LOCATIONS:
        lat, lon = COMMON_LOCATIONS[cache_key]
        print(f"[DEBUG safe_geocode] Found in common locations cache: lat={lat}, lon={lon}")
        class MockLocation:
            def __init__(self, lat, lon):
                self.latitude = lat
                self.longitude = lon
                self.address = address
        return MockLocation(lat, lon)
    
    # Check LRU cache
    cached_result = _geocode_cache.get(cache_key)
    if cached_result is not None:
        logger.debug("Cache hit for address hash: %s", _hash_address(address))
        return cached_result
    
    # Rate limiting
    _rate_limiter.wait()
    
    # Privacy-focused logging
    addr_hash = _hash_address(address)
    logger.info("Geocoding address hash: %s", addr_hash)
    
    geolocator = Nominatim(user_agent=USER_AGENT, timeout=timeout)
    
    for attempt in range(1, retries + 1):
        try:
            result = geolocator.geocode(address)
            if result:
                _rate_limiter.record_success()
                # Cache successful result
                _geocode_cache.set(cache_key, result)
                logger.info("Geocoding successful for hash: %s", addr_hash)
                print(f"[DEBUG safe_geocode] Geocoding successful: lat={result.latitude}, lon={result.longitude}")
                return result
            else:
                logger.warning("No results found for address hash: %s", addr_hash)
                print(f"[DEBUG safe_geocode] No geocoding results found for address: {address}")
                _rate_limiter.record_failure()
                break
        except GeocoderTimedOut:
            logger.warning("Geocoder timed out for hash %s (attempt %d/%d)", addr_hash, attempt, retries)
            _rate_limiter.record_failure()
            if attempt < retries:
                time.sleep(2 ** attempt)  # Exponential backoff
        except GeocoderServiceError as e:
            logger.error("Geocoder service error for hash %s: %s", addr_hash, e)
            _rate_limiter.record_failure()
            break
        except Exception as e:
            logger.exception("Unexpected error during geocoding for hash %s: %s", addr_hash, e)
            _rate_limiter.record_failure()
            break
    
    # Cache negative result to avoid repeated failed lookups
    _geocode_cache.set(cache_key, None)
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