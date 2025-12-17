# main.py
import os
import time
import threading
<<<<<<< HEAD
from typing import Optional, Tuple, Dict, Any
from functools import lru_cache
import hashlib

import certifi
import pandas as pd
from fastapi import FastAPI, Query, Body
from fastapi.responses import HTMLResponse, ORJSONResponse, JSONResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
=======
from typing import Optional, Tuple

import certifi
import pandas as pd
from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse, ORJSONResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
>>>>>>> 7ebb9bfd8079f63809bc17004756d74b16217b95

# Local modules
from modules.data_loader import load_data
from modules.geolocation import safe_geocode, validate_location, add_distance
from modules.map_display import render_map_html
from modules.sorting_logic import (
    prepare_mortality_sort,
    apply_complaint_adjustment
)
<<<<<<< HEAD
from modules.triage_rules import triage_from_form, TriageProfile
from modules.triage_ml import load_triage_model, TriageMLModel
=======
>>>>>>> 7ebb9bfd8079f63809bc17004756d74b16217b95

# Ensure SSL certs work for requests/geopy on Windows
os.environ["SSL_CERT_FILE"] = certifi.where()

app = FastAPI(title="HospiTrack API", version="1.0")

# Serve static UI if present
if os.path.isdir("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")
else:
    # still serve root HTML using /static route if you copy index.html into static/
    print("[HospiTrack] Warning: static/ directory not found; skipping static mount.")

# CORS – permissive for local dev; restrict in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data locations and globals
DATA_DIR = os.environ.get("HOSPITRACK_DATA_PATH", "data")
CANDIDATE_PATHS = [
    os.path.join(DATA_DIR, "US_er_final.parquet"),
    os.path.join(DATA_DIR, "us_er.parquet"),
    os.path.join(DATA_DIR, "us_er_transformed.csv"),
    "us_er.parquet",
    "US_er_transformed.csv",
]

df_all: Optional[pd.DataFrame] = None
STARTUP_ERROR: Optional[Exception] = None
DATA_LOAD_STARTED = False
<<<<<<< HEAD
ml_triage_model: Optional[TriageMLModel] = None

# Simple cache for explore endpoint (TTL: 5 minutes)
_explore_cache = {}
_explore_cache_timestamps = {}
EXPLORE_CACHE_TTL = 300  # 5 minutes
=======
>>>>>>> 7ebb9bfd8079f63809bc17004756d74b16217b95

# Supported sort options for docs/UI labeling
SORT_OPTIONS = {
    "adjusted_quality_points": "Quality",
    "detail_avg_time_in_ed_minutes": "ED Time (min, lower is better)",
    "detail_overall_patient_rating": "Patient Rating",
    "mortality": "Mortality"
}


<<<<<<< HEAD
# Request/Response Models
class SearchRequest(BaseModel):
    """Request model for /api/search endpoint."""
    complaint: str = Field(default="overall", description="Chief complaint or symptom")
    priority: str = Field(default="quality", description="Priority: quality/time/rating/mortality")
    location: Optional[str] = Field(default=None, description="Address or city")
    lat: Optional[float] = Field(default=None, description="Latitude")
    lon: Optional[float] = Field(default=None, description="Longitude")
    radius_km: float = Field(default=50.0, ge=1.0, le=1000.0, description="Search radius in km")
    state_filter: Optional[str] = Field(default=None, description="State code filter (e.g., 'CA')")
    limit: int = Field(default=50, ge=1, le=200, description="Maximum number of results")


class TriageRequest(BaseModel):
    """Request model for /api/triage endpoint."""
    chief_complaint: str = Field(..., description="Patient's chief complaint")
    severity: int = Field(default=3, ge=1, le=5, description="Severity level (1-5)")
    age: Optional[int] = Field(default=None, ge=0, le=120, description="Patient age")
    heart_rate: Optional[float] = Field(default=None, description="Heart rate (bpm)")
    systolic_bp: Optional[float] = Field(default=None, description="Systolic BP (mmHg)")
    diastolic_bp: Optional[float] = Field(default=None, description="Diastolic BP (mmHg)")
    respiratory_rate: Optional[float] = Field(default=None, description="Respiratory rate")
    temperature: Optional[float] = Field(default=None, description="Body temperature (C)")
    oxygen_saturation: Optional[float] = Field(default=None, description="O2 saturation (%)")
    use_ml_model: bool = Field(default=False, description="Use ML model instead of rules")


=======
>>>>>>> 7ebb9bfd8079f63809bc17004756d74b16217b95
def _first_existing_path(paths):
    for p in paths:
        if os.path.exists(p):
            return p
    return None


def _load_data_background():
    """
    Load data once in a background thread so the app starts immediately.
    """
    global df_all, STARTUP_ERROR
    try:
        t0 = time.time()
        preferred_path = _first_existing_path(CANDIDATE_PATHS)
        if not preferred_path:
            raise FileNotFoundError(f"No dataset found in any of: {CANDIDATE_PATHS}")
        print(f"[HospiTrack] Loading dataset from: {preferred_path}")
        df_all = load_data(preferred_path)
        if not isinstance(df_all, pd.DataFrame):
            raise RuntimeError("load_data() did not return a pandas DataFrame")
        # sanity: ensure lat/lon exist and not all NaN
        if "lat" not in df_all.columns or "lon" not in df_all.columns or (
            df_all["lat"].isna().all() or df_all["lon"].isna().all()
        ):
            raise RuntimeError("Dataset missing lat/lon coordinates after load.")
        print(f"[HospiTrack] Loaded {len(df_all):,} rows in {time.time() - t0:.2f}s")
    except Exception as e:
        STARTUP_ERROR = e
        print(f"[HospiTrack] ERROR during dataset load: {e!r}")


@app.on_event("startup")
def _startup():
    """
    Launch background data load. App will return 503 for data-dependent routes
    until loading completes, and 500 if a startup error occurred.
    """
    global DATA_LOAD_STARTED
    if DATA_LOAD_STARTED:
        return
    DATA_LOAD_STARTED = True
    thread = threading.Thread(target=_load_data_background, daemon=True)
    thread.start()
    print("[HospiTrack] Startup: background data load thread launched.")


def _sort_df(df: pd.DataFrame, selected_sort: str) -> pd.DataFrame:
    """
    Preserve sorting semantics, including mortality special handling.
    """

    if selected_sort == "detail_avg_time_in_ed_minutes" and selected_sort in df.columns:
        return df.sort_values(by=selected_sort, ascending=True, na_position="last")

    if selected_sort == "mortality":
        tmp = prepare_mortality_sort(df)  # adds mortality_order & mortality_sort_value
        by, asc = [], []
        if "mortality_order" in tmp.columns:
            by.append("mortality_order")
            asc.append(True)
        if "mortality_sort_value" in tmp.columns:
            by.append("mortality_sort_value")
            asc.append(False)
        return tmp.sort_values(by=by or tmp.columns.tolist(), ascending=asc or True)

    if selected_sort in df.columns:
        # Default: higher is better for most columns
        return df.sort_values(by=selected_sort, ascending=False, na_position="last")

    # fallback preference
    for candidate in ("adjusted_quality_points", "detail_overall_patient_rating"):
        if candidate in df.columns:
            asc = candidate == "detail_avg_time_in_ed_minutes"
            return df.sort_values(by=candidate, ascending=asc, na_position="last")
    return df


<<<<<<< HEAD
@app.get("/")
def root():
    """Redirect to the main landing page"""
    return RedirectResponse(url="/static/index.html")
=======
@app.get("/", response_class=HTMLResponse)
def root():
    return """
    <html>
    <head><title>HospiTrack</title></head>
    <body>
    <h2>HospiTrack — US ER Finder</h2>
    <p>Status: <a href="/healthz">/healthz</a> | API: <a href="/docs">/docs</a> | UI: <a href="/static/index.html">/static/index.html</a></p>
    <p>Examples:</p>
    <ul>
    <li><code>/map?address=Chicago, IL&sort=adjusted_quality_points&complaint=Overall&top_k=50</code></li>
    <li><code>/api/hospitals?address=Chicago, IL&top_k=25&within_km=200&sort=detail_overall_patient_rating</code></li>
    </ul>
    </body>
    </html>
    """
>>>>>>> 7ebb9bfd8079f63809bc17004756d74b16217b95


@app.get("/healthz")
def healthz():
    if STARTUP_ERROR is not None:
        return JSONResponse(status_code=500, content={"status": "error", "detail": str(STARTUP_ERROR)})
    status = "ready" if isinstance(df_all, pd.DataFrame) else "starting"
    return {"status": status}


<<<<<<< HEAD
def generate_ranking_explanation(
    sort_by: str,
    complaint: str = "Overall",
    radius_km: Optional[float] = None,
    state_filter: Optional[str] = None,
    top_k: Optional[int] = None
) -> str:
    """
    Generate human-readable explanation for hospital ranking.
    
    Args:
        sort_by: Sorting criterion used
        complaint: Patient complaint/condition
        radius_km: Search radius in km
        state_filter: State filter applied
        top_k: Number of results returned
    
    Returns:
        Human-readable explanation string
    """
    sort_label = SORT_OPTIONS.get(sort_by, sort_by)
    
    # Base explanation
    if sort_by == "detail_avg_time_in_ed_minutes":
        explanation = f"Hospitals ranked by **fastest ED wait time** (lowest minutes)"
    elif sort_by == "mortality":
        explanation = f"Hospitals ranked by **lowest mortality rates**"
    elif sort_by == "detail_overall_patient_rating":
        explanation = f"Hospitals ranked by **highest patient satisfaction ratings**"
    else:  # adjusted_quality_points or default
        explanation = f"Hospitals ranked by **quality of care**"
    
    # Add complaint context
    if complaint and complaint.lower() not in ["overall", "general", "other"]:
        explanation += f" for **{complaint}** cases"
    
    # Add geographic filters
    if radius_km:
        explanation += f" within **{radius_km:.0f} km** of your location"
    if state_filter:
        explanation += f" in **{state_filter.upper()}**"
    
    # Add result count
    if top_k:
        explanation += f". Showing top **{top_k}** results"
    
    explanation += "."
    
    return explanation


def _resolve_user_location(address: str, lat: Optional[float], lon: Optional[float]) -> Tuple[float, float, str]:
    """
    Resolve user location from lat/lon or by geocoding an address.
    Defaults to Chicago if geocoding fails or no inputs are provided.
    Uses enhanced safe_geocode with caching and rate limiting.
    
    Returns:
        Tuple of (latitude, longitude, status_message)
        status_message indicates whether geocoding succeeded or fell back
    """
    # Use enhanced safe_geocode that handles all three modes
    loc = safe_geocode(address=address, lat=lat, lon=lon)
    loc = validate_location(loc, restrict_to_midwest=False)
    if loc:
        if lat is not None and lon is not None:
            return float(loc.latitude), float(loc.longitude), "using_coordinates"
        return float(loc.latitude), float(loc.longitude), "geocoded_successfully"
    
    # Default: Chicago (fallback when geocoding fails)
    print(f"[WARN] Geocoding failed for '{address}', falling back to Chicago coordinates")
    return 41.8781, -87.6298, "geocoding_failed_fallback"
=======
def _resolve_user_location(address: str, lat: Optional[float], lon: Optional[float]) -> Tuple[float, float]:
    """
    Resolve user location from lat/lon or by geocoding an address.
    Defaults to Chicago if geocoding fails or no inputs are provided.
    """
    if lat is not None and lon is not None:
        return float(lat), float(lon)
    if address:
        loc = safe_geocode(address)
        loc = validate_location(loc, restrict_to_midwest=False)
        if loc:
            return float(loc.latitude), float(loc.longitude)
    # Default: Chicago
    return 41.8781, -87.6298
>>>>>>> 7ebb9bfd8079f63809bc17004756d74b16217b95


def _ensure_data_ready() -> Optional[JSONResponse]:
    """
    Return a JSON error response if data is not ready or startup failed.
    """
    if STARTUP_ERROR is not None:
        return JSONResponse(status_code=500, content={"error": f"startup_error: {STARTUP_ERROR}"})
    if not isinstance(df_all, pd.DataFrame):
        return JSONResponse(status_code=503, content={"error": "Data loading; try again shortly."})
    return None


@app.get("/map", response_class=HTMLResponse)
def map_view(
    address: str = Query(default="", description="Address to center on"),
    lat: Optional[float] = Query(default=None),
    lon: Optional[float] = Query(default=None),
    sort: str = Query(
        default="adjusted_quality_points",
        regex="adjusted_quality_points|detail_avg_time_in_ed_minutes|detail_overall_patient_rating|mortality",
    ),
    complaint: str = Query(default="Overall"),
    top_k: int = Query(default=50, ge=1, le=1000),
    within_km: float = Query(default=300.0, ge=1.0, le=10000.0),
    state: Optional[str] = Query(default=None, description="Two-letter state to prefilter points (optional)"),
):
    not_ready = _ensure_data_ready()
    if not_ready:
        return not_ready

<<<<<<< HEAD
    user_lat, user_lon, _ = _resolve_user_location(address, lat, lon)
=======
    user_lat, user_lon = _resolve_user_location(address, lat, lon)
>>>>>>> 7ebb9bfd8079f63809bc17004756d74b16217b95

    df = df_all.copy()
    df, _ = apply_complaint_adjustment(df, complaint)
    df = df.dropna(subset=["lat", "lon"])
    df = add_distance(df, user_lat, user_lon)

    # Optional state prefilter on map too
    if state and "detail_state" in df.columns:
        df = df[df["detail_state"].astype("string").str.upper() == state.strip().upper()]

    df = df[df["distance_km"] <= within_km].copy()
    if df.empty:
        # fallback: closest 2000
        df = df_all.copy()
        df, _ = apply_complaint_adjustment(df, complaint)
        df = df.dropna(subset=["lat", "lon"])
        df = add_distance(df, user_lat, user_lon)
        df = df.nsmallest(2000, "distance_km")

    df_sorted = _sort_df(df, sort).head(top_k)
    html_map = render_map_html(df_sorted, user_lat, user_lon, max_points=5000)

    return f"""
    <html>
    <head>
    <meta charset="utf-8">
    <title>HospiTrack Map</title>
    </head>
    <body>
    <h3>HospiTrack Map — Sort: {SORT_OPTIONS.get(sort, sort)} | Complaint: {complaint}</h3>
    {html_map}
    </body>
    </html>
    """


@app.get("/api/states")
def api_states():
    """
    Returns a list of unique state abbreviations in the dataset.
    Used by the UI to populate the state dropdown.
    """
    if isinstance(df_all, pd.DataFrame) and "detail_state" in df_all.columns:
        states = sorted(
            {str(s).upper() for s in df_all["detail_state"].dropna().astype(str) if 1 <= len(str(s)) <= 3}
        )
    else:
        states = ["IL","IN","IA","MI","MN","MO","OH","WI","PA","NY","CA","TX","FL","GA","NC","VA","WA","CO","AZ","MA"]
    return {"states": states}


@app.get("/api/hospitals", response_class=ORJSONResponse)
def api_hospitals(
    address: str = Query(default="", description="Free-form address or city, ST"),
    lat: Optional[float] = Query(default=None),
    lon: Optional[float] = Query(default=None),
    state: Optional[str] = Query(default=None, description="Two-letter state code (server-side filter)"),
    sort: str = Query(
        default="adjusted_quality_points",
        regex="adjusted_quality_points|detail_avg_time_in_ed_minutes|detail_overall_patient_rating|mortality",
    ),
    complaint: str = Query(default="Overall"),
    top_k: int = Query(default=50, ge=1, le=2000),
    within_km: float = Query(default=200.0, ge=1.0, le=10000.0),
):
    not_ready = _ensure_data_ready()
    if not_ready:
        return not_ready

<<<<<<< HEAD
    user_lat, user_lon, _ = _resolve_user_location(address, lat, lon)
=======
    user_lat, user_lon = _resolve_user_location(address, lat, lon)
>>>>>>> 7ebb9bfd8079f63809bc17004756d74b16217b95

    df = df_all.copy()
    df, _ = apply_complaint_adjustment(df, complaint)
    df = df.dropna(subset=["lat", "lon"])
    df = add_distance(df, user_lat, user_lon)

    # Server-side state filtering for correctness and performance
    if state and "detail_state" in df.columns:
        df = df[df["detail_state"].astype("string").str.upper() == state.strip().upper()]

    nearby = df[df["distance_km"] <= within_km]
    if nearby.empty:
        nearby = df.nsmallest(2000, "distance_km")

    nearby = _sort_df(nearby, sort).head(top_k)

    cols = [
        "hospital_name",
        "detail_address", "detail_city", "detail_state", "detail_zip",
        "lat", "lon",
        "distance_km",
        "total_quality_points", "adjusted_quality_points",
        "detail_avg_time_in_ed_minutes",
        "detail_overall_patient_rating",
        "detail_mortality_overall_text",
        "Top_Procedures",
    ]
    cols = [c for c in cols if c in nearby.columns]
    data = nearby[cols].to_dict(orient="records")
<<<<<<< HEAD
    
    # Add ranking explanation
    ranking_explanation = generate_ranking_explanation(
        sort_by=sort,
        complaint=complaint,
        radius_km=within_km,
        state_filter=state,
        top_k=top_k
    )
    
    return {
        "count": len(data),
        "results": data,
        "ranking_explanation": ranking_explanation
    }


@app.post("/api/search", response_class=ORJSONResponse)
def api_search(request: SearchRequest):
    """
    Enhanced search endpoint for home page queries.
    Accepts complaint, priority, location, radius, and state filter.
    Returns sorted hospitals with ranking explanations.
    """
    print(f"\n[DEBUG /api/search] Received request:")
    print(f"  - complaint: {request.complaint}")
    print(f"  - priority: {request.priority}")
    print(f"  - location: {request.location}")
    print(f"  - lat: {request.lat}, lon: {request.lon}")
    print(f"  - radius_km: {request.radius_km}")
    print(f"  - state_filter: {request.state_filter}")
    print(f"  - limit: {request.limit}")
    
    not_ready = _ensure_data_ready()
    if not_ready:
        print(f"[DEBUG /api/search] Data not ready: {not_ready}")
        return not_ready
    
    print(f"[DEBUG /api/search] df_all has {len(df_all)} hospitals")
    
    # Resolve location
    user_lat, user_lon, geocode_status = _resolve_user_location(
        request.location or "",
        request.lat,
        request.lon
    )
    print(f"[DEBUG /api/search] Resolved user location: lat={user_lat}, lon={user_lon}, status={geocode_status}")
    
    # Map priority to sort field
    priority_map = {
        "quality": "adjusted_quality_points",
        "time": "detail_avg_time_in_ed_minutes",
        "rating": "detail_overall_patient_rating",
        "mortality": "mortality"
    }
    sort_by = priority_map.get(request.priority.lower(), "adjusted_quality_points")
    print(f"[DEBUG /api/search] Sort by: {sort_by}")
    
    # Apply complaint adjustment
    df = df_all.copy()
    print(f"[DEBUG /api/search] Starting with {len(df)} hospitals")
    
    df, _ = apply_complaint_adjustment(df, request.complaint)
    print(f"[DEBUG /api/search] After complaint adjustment: {len(df)} hospitals")
    
    df = df.dropna(subset=["lat", "lon"])
    print(f"[DEBUG /api/search] After dropping null lat/lon: {len(df)} hospitals")
    
    df = add_distance(df, user_lat, user_lon)
    print(f"[DEBUG /api/search] After adding distance, sample distances: {df['distance_km'].head().tolist() if 'distance_km' in df.columns else 'NO DISTANCE COLUMN'}")
    
    # State filter
    if request.state_filter and "detail_state" in df.columns:
        before_state = len(df)
        df = df[df["detail_state"].astype("string").str.upper() == request.state_filter.strip().upper()]
        print(f"[DEBUG /api/search] After state filter ({request.state_filter}): {len(df)} hospitals (was {before_state})")
    
    # Radius filter with fallback
    print(f"[DEBUG /api/search] Filtering by radius {request.radius_km} km")
    nearby = df[df["distance_km"] <= request.radius_km]
    print(f"[DEBUG /api/search] Hospitals within radius: {len(nearby)}")
    
    if nearby.empty:
        print(f"[DEBUG /api/search] No hospitals within radius, taking nearest 1000")
        nearby = df.nsmallest(1000, "distance_km")
        print(f"[DEBUG /api/search] Nearest hospitals: {len(nearby)}")
    
    # Sort and limit
    nearby = _sort_df(nearby, sort_by).head(request.limit)
    print(f"[DEBUG /api/search] After sorting and limit: {len(nearby)} hospitals")
    
    # Select columns
    cols = [
        "hospital_name",
        "detail_address", "detail_city", "detail_state", "detail_zip",
        "lat", "lon",
        "distance_km",
        "total_quality_points", "adjusted_quality_points",
        "detail_avg_time_in_ed_minutes",
        "detail_overall_patient_rating",
        "detail_mortality_overall_text",
        "Top_Procedures",
    ]
    cols = [c for c in cols if c in nearby.columns]
    data = nearby[cols].to_dict(orient="records")
    
    # Transform field names to match frontend expectations
    for record in data:
        # Rename fields
        if "hospital_name" in record:
            record["facility_name"] = record.pop("hospital_name")
        
        # Create combined address field
        address_parts = []
        if "detail_address" in record and record["detail_address"]:
            address_parts.append(str(record["detail_address"]))
        if "detail_city" in record and record["detail_city"]:
            address_parts.append(str(record["detail_city"]))
        if "detail_state" in record and record["detail_state"]:
            address_parts.append(str(record["detail_state"]))
        if "detail_zip" in record and record["detail_zip"]:
            address_parts.append(str(record["detail_zip"]))
        record["address"] = ", ".join(address_parts) if address_parts else ""
        
        # Rename quality/rating fields
        if "adjusted_quality_points" in record:
            record["quality_points"] = record.get("adjusted_quality_points")
        if "detail_avg_time_in_ed_minutes" in record:
            record["ed_avg_time_admit"] = record.get("detail_avg_time_in_ed_minutes")
        if "detail_overall_patient_rating" in record:
            record["overall_rating"] = record.get("detail_overall_patient_rating")
        if "detail_mortality_overall_text" in record:
            record["mortality_display"] = record.get("detail_mortality_overall_text")
        
        # Generate facility_id from hospital name (simple hash)
        if "facility_name" in record:
            import hashlib
            record["facility_id"] = hashlib.md5(str(record["facility_name"]).encode()).hexdigest()[:12]
    
    # Generate explanation
    ranking_explanation = generate_ranking_explanation(
        sort_by=sort_by,
        complaint=request.complaint,
        radius_km=request.radius_km,
        state_filter=request.state_filter,
        top_k=request.limit
    )
    
    return {
        "count": len(data),
        "hospitals": data,  # Changed from "results" to "hospitals"
        "ranking_explanation": ranking_explanation,
        "user_location": {"lat": user_lat, "lon": user_lon}
    }


@app.get("/api/explore", response_class=ORJSONResponse)
def api_explore(
    name: Optional[str] = Query(default=None, description="Hospital name search"),
    city: Optional[str] = Query(default=None, description="City filter"),
    state: Optional[str] = Query(default=None, description="State filter (e.g., CA)"),
    sort_by: str = Query(default="adjusted_quality_points", description="Sort field"),
    limit: int = Query(default=50, ge=1, le=200, description="Results per page"),
    offset: int = Query(default=0, ge=0, description="Pagination offset"),
):
    """
    Explore US-wide hospitals with search, filtering, and pagination.
    No location required - browse entire dataset.
    """
    not_ready = _ensure_data_ready()
    if not_ready:
        return not_ready
    
    # Create cache key from query parameters
    cache_key = f"{name}:{city}:{state}:{sort_by}:{limit}:{offset}"
    cache_hash = hashlib.md5(cache_key.encode()).hexdigest()
    
    # Check cache
    current_time = time.time()
    if cache_hash in _explore_cache and cache_hash in _explore_cache_timestamps:
        cache_age = current_time - _explore_cache_timestamps[cache_hash]
        if cache_age < EXPLORE_CACHE_TTL:
            print(f"[CACHE HIT] /api/explore - age: {cache_age:.1f}s")
            return _explore_cache[cache_hash]
    
    df = df_all.copy()
    
    # Apply filters
    if name and "hospital_name" in df.columns:
        df = df[df["hospital_name"].astype(str).str.contains(name, case=False, na=False)]
    
    if city and "detail_city" in df.columns:
        df = df[df["detail_city"].astype(str).str.contains(city, case=False, na=False)]
    
    if state and "detail_state" in df.columns:
        df = df[df["detail_state"].astype("string").str.upper() == state.strip().upper()]
    
    # Sort
    df = _sort_df(df, sort_by)
    
    # Pagination
    total_count = len(df)
    df_page = df.iloc[offset : offset + limit]
    
    # Select columns
    cols = [
        "hospital_name",
        "detail_address", "detail_city", "detail_state", "detail_zip",
        "lat", "lon",
        "total_quality_points", "adjusted_quality_points",
        "detail_avg_time_in_ed_minutes",
        "detail_overall_patient_rating",
        "detail_mortality_overall_text",
        "Top_Procedures",
    ]
    cols = [c for c in cols if c in df_page.columns]
    data = df_page[cols].to_dict(orient="records")
    
    # Generate explanation
    filters_applied = []
    if name:
        filters_applied.append(f"name matching '{name}'")
    if city:
        filters_applied.append(f"in {city}")
    if state:
        filters_applied.append(f"in {state.upper()}")
    
    filter_text = ", ".join(filters_applied) if filters_applied else "all hospitals nationwide"
    ranking_explanation = f"Exploring {filter_text}, sorted by {SORT_OPTIONS.get(sort_by, sort_by)}. " \
                         f"Showing results {offset + 1}-{offset + len(data)} of {total_count} total."
    
    response = {
        "count": len(data),
        "total": total_count,
        "offset": offset,
        "limit": limit,
        "results": data,
        "ranking_explanation": ranking_explanation
    }
    
    # Store in cache
    _explore_cache[cache_hash] = response
    _explore_cache_timestamps[cache_hash] = current_time
    
    # Clean old cache entries (keep max 100 entries)
    if len(_explore_cache) > 100:
        oldest_key = min(_explore_cache_timestamps, key=_explore_cache_timestamps.get)
        del _explore_cache[oldest_key]
        del _explore_cache_timestamps[oldest_key]
    
    return response


@app.post("/api/triage", response_class=ORJSONResponse)
def api_triage(request: TriageRequest):
    """
    Triage endpoint for company demo.
    Accepts intake form and returns triage profile with recommendations.
    
    Uses rule-based logic by default, with optional ML model (if trained).
    """
    # Prepare form data
    form_data = request.dict()
    
    # Rule-based triage (default)
    if not request.use_ml_model:
        profile: TriageProfile = triage_from_form(form_data)
        
        return {
            "method": "rule-based",
            "recommended_sort": profile.recommended_sort,
            "quality_column": profile.quality_column,
            "urgency_level": profile.urgency_level,
            "weights": profile.weights,
            "explanation": profile.explanation,
            "demo_mode_warning": "Rule-based triage for demonstration purposes. Not for clinical use."
        }
    
    # ML-based triage (if requested and model available)
    else:
        global ml_triage_model
        
        # Try to load model if not already loaded
        if ml_triage_model is None:
            ml_triage_model = load_triage_model()
        
        if ml_triage_model is None:
            return JSONResponse(
                status_code=503,
                content={
                    "error": "ML triage model not trained yet. Train model first or use rule-based method.",
                    "suggestion": "Set use_ml_model=false to use rule-based triage."
                }
            )
        
        try:
            # Prepare data for ML model
            patient_data = {
                "Age": form_data.get("age"),
                "Chief_complain": form_data.get("chief_complaint"),
                "HR": form_data.get("heart_rate"),
                "SBP": form_data.get("systolic_bp"),
                "DBP": form_data.get("diastolic_bp"),
                "RR": form_data.get("respiratory_rate"),
                "BT": form_data.get("temperature"),
                "Saturation": form_data.get("oxygen_saturation"),
            }
            
            predicted_level, confidence, explanation = ml_triage_model.predict(patient_data)
            
            return {
                "method": "ml-model",
                "predicted_triage_level": predicted_level,
                "confidence": confidence,
                "explanation": explanation,
                "demo_mode_warning": "⚠️ ML model trained on SYNTHETIC DATA. NOT for clinical use."
            }
        
        except Exception as e:
            return JSONResponse(
                status_code=500,
                content={"error": f"ML prediction failed: {str(e)}"}
            )
=======
    return {"count": len(data), "results": data}
>>>>>>> 7ebb9bfd8079f63809bc17004756d74b16217b95


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)