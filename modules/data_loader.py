# modules/data_loader.py
from pathlib import Path
from typing import Optional, Iterable

import pandas as pd
import numpy as np
import pgeocode

CACHE_PARQUET = Path("data/us_er.parquet")

# Keep only what the UI/API needs. Remove Top_Procedures for smaller file unless you display it.
API_COLUMNS: list[str] = [
    "hospital_name",
    "detail_address", "detail_city", "detail_state", "detail_zip",
    "lat", "lon",
    "total_quality_points",
    "detail_avg_time_in_ed_minutes",
    "detail_overall_patient_rating",
    "detail_mortality_overall_text",
    # complaint-adjusted columns if present
    "adj_total_heartattack", "adj_total_stroke", "adj_total_pneu",
    # "Top_Procedures",  # uncomment if you need it in UI
]

def _zip_to_latlon(zip_code: Optional[str], country: str = "US"):
    if pd.isna(zip_code):
        return np.nan, np.nan
    s = str(zip_code).strip()
    if not s or s.lower() == "nan":
        return np.nan, np.nan
    nomi = pgeocode.Nominatim(country)
    rec = nomi.query_postal_code(s)
    if rec is None or pd.isna(rec.latitude) or pd.isna(rec.longitude):
        return np.nan, np.nan
    return float(rec.latitude), float(rec.longitude)

def _ensure_lat_lon(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    has_latlon = "lat" in df.columns and "lon" in df.columns
    # If lat/lon present and mostly filled, keep them
    if has_latlon and not (df["lat"].isna().all() or df["lon"].isna().all()):
        return df

    if "detail_zip" not in df.columns:
        df["lat"] = np.nan
        df["lon"] = np.nan
        return df

    # Vectorized: build unique ZIP set → query once per ZIP → map back
    zips = (
        df["detail_zip"]
        .astype(str)
        .str.strip()
        .replace({"": np.nan, "nan": np.nan, "NaN": np.nan})
    )
    unique_zips = sorted(set(zips.dropna().unique().tolist()))
    if not unique_zips:
        df["lat"] = np.nan
        df["lon"] = np.nan
        return df

    nomi = pgeocode.Nominatim("US")
    recs = nomi.query_postal_code(unique_zips)
    # recs is a DataFrame indexed by position; map back using a dict
    zip_to_lat = {}
    zip_to_lon = {}
    for zip_code, lat, lon in zip(recs["postal_code"], recs["latitude"], recs["longitude"]):
        if pd.isna(zip_code):
            continue
        zip_to_lat[str(zip_code)] = float(lat) if pd.notna(lat) else np.nan
        zip_to_lon[str(zip_code)] = float(lon) if pd.notna(lon) else np.nan

    df["lat"] = zips.map(zip_to_lat).astype(float)
    df["lon"] = zips.map(zip_to_lon).astype(float)
    return df

def _clean_repeated_headers(df: pd.DataFrame) -> pd.DataFrame:
    header_like = df.columns.tolist()
    mask = ~(df.apply(lambda r: list(r.astype(str).values) == header_like, axis=1))
    return df[mask].copy()

def _select_columns(df: pd.DataFrame, keep: Iterable[str]) -> pd.DataFrame:
    cols = [c for c in keep if c in df.columns]
    for c in ("detail_state", "lat", "lon"):
        if c in df.columns and c not in cols:
            cols.append(c)
    return df[cols].copy() if cols else df

def build_parquet_cache(source_path: Path, out_path: Path) -> pd.DataFrame:
    """Build or refresh the Parquet cache from CSV or Parquet input."""
    if not source_path.exists():
        raise FileNotFoundError(f"Source not found: {source_path.resolve()}")

    # Load
    if source_path.suffix.lower() == ".parquet":
        df = pd.read_parquet(source_path)
    else:
        try:
            df = pd.read_csv(source_path, low_memory=False)
        except Exception:
            df = pd.read_csv(source_path, low_memory=False, encoding_errors="ignore")

    # Clean/normalize
    df = _clean_repeated_headers(df)
    for c in ["detail_state", "detail_city", "hospital_name"]:
        if c in df.columns:
            df[c] = df[c].astype(str)

    # Compute lat/lon once here
    df = _ensure_lat_lon(df)

    # Trim to just what API needs
    df = _select_columns(df, API_COLUMNS)

    # Downcast for size
    for c in ["detail_state", "detail_city"]:
        if c in df.columns:
            df[c] = df[c].astype("category")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(out_path, index=False)
    return df

def load_data(path: str) -> pd.DataFrame:
    """
    Load dataset from CSV or Parquet, prefer cached Parquet for fast startup.
    """
    p = Path(path).resolve()

    # If caller points to CSV and our cache exists, load cache
    if p.suffix.lower() == ".csv" and CACHE_PARQUET.exists():
        return pd.read_parquet(CACHE_PARQUET)

    # If caller points to Parquet, load it
    if p.suffix.lower() == ".parquet":
        return pd.read_parquet(p)

    # If caller points to CSV but no cache, build cache once
    if p.suffix.lower() == ".csv":
        df = build_parquet_cache(p, CACHE_PARQUET)
        return df

    # Last resort (unexpected extension)
    if p.exists():
        try:
            return pd.read_parquet(p)
        except Exception:
            return pd.read_csv(p, low_memory=False)
    raise FileNotFoundError(f"Dataset not found at {p}")