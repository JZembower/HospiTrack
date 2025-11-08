# 🏥 HospiTrack — ER Wait Tracker

## Overview

HospiTrack is a Python + FastAPI web app with a simple HTML UI that helps patients in the U.S. find nearby emergency departments and walk-in clinics. It surfaces:

* Estimated ED wait times

* Patient experience ratings

* Quality and mortality performance

* Proximity to the user (via geolocation)

Users can:

1. Enter an address or pass coordinates to center the map

2. View nearby facilities within a radius

3. Sort by ED efficiency, patient satisfaction, quality (incl. complaint-adjusted), or mortality

4. Filter by state (optional)

---

## Data Pipeline: From Scraping to a Geolocated Dataset

### 1) Scrape hospital stats (ER wait times, core details)

* Use `requests` + `BeautifulSoup` to scrape facility-level stats such as:

  * Facility name and address

  * Average ED time (`detail_avg_time_in_ed_minutes`)

  * Patient ratings (`detail_overall_patient_rating`)

  * Hospital type, emergency services flag, etc.

* Store raw rows with the corresponding detail page and phone/address elements.

* Normalize text fields, trim whitespace, and standardize numeric fields (minutes, percentages).

Output: a raw hospitals CSV with columns like:

* `hospital_name`, `detail_address`, `detail_city`, `detail_state`, `detail_zip`

* `detail_avg_time_in_ed_minutes`, `detail_overall_patient_rating`

* Other detail fields required for joining and scoring

Tip: When paginating during scraping, be polite (sleep/retry), and avoid overloading host sites.

### 2) Enrich with Medicare/Hospital Compare-based quality and mortality

* Pull Medicare/Hospital Compare data (CSV downloads, API, or aggregated datasets). Typical fields used:

  * Overall mortality text (e.g., “46% better”, “12% worse”) → `detail_mortality_overall_text`

  * Complaint-adjusted quality scores:

    * `adj_total_heartattack`

    * `adj_total_stroke`

    * `adj_total_pneu`

  * Overall quality: `total_quality_points`

* Join against scraped hospital records using a robust key strategy:

  * Prefer exact matches on name + address + ZIP

  * Fall back to fuzzy matching on name and city if needed (with manual fixes for edge cases)

Output: a unified CSV we refer to as `us_er_transformed.csv` containing:

* Identity and location fields

* ED wait, patient ratings

* Mortality strings and quality points (overall and complaint-adjusted)

### 3) Geocode (lat/lon) to make it map-ready

* If `lat`/`lon` are missing, generate them once from ZIP using `pgeocode` (fast and offline) or a geocoding service.

* This app’s loader can compute `lat`/`lon` automatically if only `detail_zip` is present.

Result: `us_er_transformed.csv` becomes a geolocated, analysis-ready dataset.

---

## Converting CSV to Parquet (fast load in the app)

We cache a tight subset of columns in a compact Parquet file for fast startup.

Key implementation: `modules/data_loader.py`

* Preferred cache path: `data/us_er.parquet`

* Loader trims to the API/UI subset and downcasts columns for size.

### Minimal example (outside the app)

```python
from pathlib import Path
from modules.data_loader import build_parquet_cache

csv_path = Path("us_er_transformed.csv")
out_path = Path("data/us_er.parquet")
df = build_parquet_cache(csv_path, out_path)
print("Parquet rows:", len(df))
```

What columns are kept for the API/UI?

```python
API_COLUMNS = [
    "hospital_name",
    "detail_address", "detail_city", "detail_state", "detail_zip",
    "lat", "lon",
    "total_quality_points",
    "detail_avg_time_in_ed_minutes",
    "detail_overall_patient_rating",
    "detail_mortality_overall_text",
    "adj_total_heartattack", "adj_total_stroke", "adj_total_pneu",
    # (Optionally) "Top_Procedures"
]
```

Load preference inside the app (`main.py`):

1. `data/US_er_final.parquet`

2. `data/us_er.parquet`

3. `data/us_er_transformed.csv`

4. `./us_er.parquet`

5. `./US_er_transformed.csv`

The first existing path is used. If a CSV is used and no cache exists yet, it is converted to `data/us_er.parquet` automatically.

---

## How Sorting and UI Logic Work

### 1) Complaint-adjusted quality scoring

File: `modules/sorting_logic.py`

User complaint → column mapping:

* Overall → `total_quality_points`

* Heart Attack / Chest Pain → `adj_total_heartattack`

* Stroke / Slurred Speech / Facial Droop → `adj_total_stroke`

* Shortness of Breath / Cough / Fever → `adj_total_pneu`

The chosen column is materialized as `adjusted_quality_points` and becomes the default quality sort.

### 2) Mortality sorting

* `detail_mortality_overall_text` strings like “46% better” are parsed to:

  * `mortality_type`: better/worse/not used

  * `mortality_sort_value`: numeric score (positive for better, negative for worse)

* Sort order for “Mortality”:

  1. `mortality_order` (better first)

  2. `mortality_sort_value` (higher magnitude of “better” before lower)

### 3) Distance and filters

* For any request, user location is resolved (lat/lon or via geocoding).

* We compute `distance_km` and filter to `within_km`.

* Optional server-side state filter via `state=XX`.

### 4) Sort options exposed to UI/API

* `adjusted_quality_points` (descending: higher is better)

* `detail_avg_time_in_ed_minutes` (ascending: lower is better)

* `detail_overall_patient_rating` (descending)

* `mortality` (special logic above)

Final map/table is constructed from the top-K after sorting.

---

## Quick Start (Docker)

### Prerequisites

* Docker Desktop running

* Python 3.8+ (to run the helper script)

* Ensure your dataset exists at one of the candidate paths (recommended: `data/us_er.parquet`)

### Fast path (recommended)

From PowerShell at the repo root:

```powershell
python .\dev_start.py
```

What this does:

* Builds the Docker image and starts the compose stack

* Waits for health at `http://localhost:8000/healthz`

* Opens the UI at `http://localhost:8000/static/index.html`

Flags:

```powershell
# Don’t open browser automatically
python .\dev_start.py --no-browser

# Increase startup wait (seconds)
python .\dev_start.py --timeout 240

# Use a different compose file
python .\dev_start.py --compose-file docker-compose.override.yml
```

### Manual compose (if you prefer)

```powershell
# Build and start
docker compose up --build -d

# Check logs
docker compose logs -f

# Stop the stack
docker compose down
```

Default endpoints:

* Health: `http://localhost:8000/healthz`

* API docs: `http://localhost:8000/docs`

* UI: `http://localhost:8000/static/index.html`

---

## Project Structure (selected)

* `main.py` — FastAPI app, routes (`/map`, `/api/hospitals`, `/api/states`)

* `modules/data_loader.py` — CSV/Parquet loading, cache builder, column selection

* `modules/sorting_logic.py` — Mortality parsing, complaint-adjusted quality selection

* `modules/geolocation.py` — Geocoding helpers and distance calculation

* `modules/map_display.py` — HTML/Leaflet map rendering

* `static/index.html` — Simple front-end

* `Dockerfile`, `docker-compose.yml`, `dev_start.py` — containerization and local dev tooling

* `data/us_er.parquet` — compact cached dataset (preferred at runtime)

* `us_er_transformed.csv` — geolocated CSV source that can be converted to Parquet

---

## Troubleshooting

### Dataset not found or missing lat/lon

* Ensure one of the candidate data files exists (see list above).

* If starting from CSV, verify `detail_zip` is present so the loader can compute `lat`/`lon`.

* If `lat`/`lon` are entirely missing after load, the app will raise a startup error.

### Windows SSL/geocoding issues

* `main.py` sets `SSL_CERT_FILE` to `certifi.where()` for more reliable HTTPS on Windows.

### Parquet files and text extraction

If you try to “open” a Parquet file as plain text in some tools, it will fail because Parquet is a binary columnar format. In this environment, note that the uploaded file `us_er.parquet` cannot be text-extracted; these documents can only be used in code execution.

Common reasons for text extraction failure from Parquet:

* It’s a binary, compressed, columnar store (not human-readable text)

* Requires a Parquet reader (e.g., `pandas.read_parquet`, `pyarrow`, `fastparquet`)

* Compression and encoding block plain-text extraction

Use code like:

```python
import pandas as pd
df = pd.read_parquet("data/us_er.parquet")
print(df.head())
```

---

## Credits

Collaborators: Imama Zahoor, Vidhi Kothari, Eugene Ho, Elissa Matlock, Jonah Zembower