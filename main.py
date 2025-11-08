# main.py
import os
import time
import threading
from typing import Optional, Tuple

import certifi
import pandas as pd
from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse, ORJSONResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# Local modules
from modules.data_loader import load_data
from modules.geolocation import safe_geocode, validate_location, add_distance
from modules.map_display import render_map_html
from modules.sorting_logic import (
    prepare_mortality_sort,
    apply_complaint_adjustment
)

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

# Supported sort options for docs/UI labeling
SORT_OPTIONS = {
    "adjusted_quality_points": "Quality",
    "detail_avg_time_in_ed_minutes": "ED Time (min, lower is better)",
    "detail_overall_patient_rating": "Patient Rating",
    "mortality": "Mortality"
}


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


@app.get("/healthz")
def healthz():
    if STARTUP_ERROR is not None:
        return JSONResponse(status_code=500, content={"status": "error", "detail": str(STARTUP_ERROR)})
    status = "ready" if isinstance(df_all, pd.DataFrame) else "starting"
    return {"status": status}


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

    user_lat, user_lon = _resolve_user_location(address, lat, lon)

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

    user_lat, user_lon = _resolve_user_location(address, lat, lon)

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
    return {"count": len(data), "results": data}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)