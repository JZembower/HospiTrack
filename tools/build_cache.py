# tools/build_cache.py
import argparse
from pathlib import Path

from modules.data_loader import build_parquet_cache

def main():
    parser = argparse.ArgumentParser(description="Prebuild Parquet cache for HospiTrack")
    parser.add_argument("--input", required=True, help="Path to CSV or Parquet source (e.g., data/US_er_final.csv)")
    parser.add_argument("--output", default="data/us_er.parquet", help="Path to write Parquet cache")
    args = parser.parse_args()

    src = Path(args.input)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)

    print(f"[build_cache] Building cache from: {src} -> {out}")
    df = build_parquet_cache(src, out)
    print(f"[build_cache] Wrote {len(df):,} rows to {out.resolve()}")
    print(f"[build_cache] Columns: {list(df.columns)}")

if __name__ == "__main__":
    main()