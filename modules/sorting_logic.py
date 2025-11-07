# modules/sorting_logic.py
import numpy as np
import pandas as pd
from typing import Dict, Tuple

def parse_mortality(val):
    """
    Normalize strings like "46% better" or "12% worse" into a tuple:
    ("better"/"worse"/"not used", numeric_value)
    Numeric values are positive for "better" and negative for "worse".
    """
    if not isinstance(val, str):
        return ("not used", np.nan)
    s = val.lower()
    if "not used" in s:
        return ("not used", np.nan)
    if "better" in s:
        num = ''.join(c for c in s if c.isdigit())
        return ("better", int(num) if num else 0)
    if "worse" in s:
        num = ''.join(c for c in s if c.isdigit())
        return ("worse", -int(num) if num else 0)
    return ("not used", np.nan)


def prepare_mortality_sort(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add mortality_type, mortality_sort_value and mortality_order columns to a copy of df.
    mortality_order: lower is better (0 == better)
    """
    out = df.copy()
    if "detail_mortality_overall_text" in out.columns:
        parsed = out["detail_mortality_overall_text"].apply(parse_mortality).apply(pd.Series)
        parsed.columns = ["mortality_type", "mortality_sort_value"]
        out = pd.concat([out.reset_index(drop=True), parsed.reset_index(drop=True)], axis=1)
    else:
        out["mortality_type"] = "not used"
        out["mortality_sort_value"] = np.nan

    order = {"better": 0, "worse": 1, "not used": 2}
    out["mortality_order"] = out["mortality_type"].map(order).fillna(2).astype(int)
    return out


def apply_complaint_adjustment(df: pd.DataFrame, complaint: str) -> Tuple[pd.DataFrame, str]:
    """
    Map user complaint to an adjusted quality column if available.
    Returns (df_with_adjusted_quality_column, label).
    """
    complaint_map = {
        "Overall": "total_quality_points",
        "Chest Pain": "adj_total_heartattack",
        "Heart Attack": "adj_total_heartattack",
        "Slurred Speech": "adj_total_stroke",
        "Facial Droop": "adj_total_stroke",
        "Stroke": "adj_total_stroke",
        "Shortness of Breath": "adj_total_pneu",
        "Trouble Breathing": "adj_total_pneu",
        "Cough": "adj_total_pneu",
        "Fever": "adj_total_pneu",
    }
    col = complaint_map.get(complaint, "total_quality_points")
    out = df.copy()
    if col in out.columns:
        out["adjusted_quality_points"] = out[col]
        label = f"Quality Points (adjusted for {complaint})"
    else:
        base = "total_quality_points" if "total_quality_points" in out.columns else None
        if base is not None:
            out["adjusted_quality_points"] = out[base]
            label = "Overall Quality Points"
        else:
            out["adjusted_quality_points"] = np.nan
            label = "Quality Points"
    return out, label


def compute_composite_score(df: pd.DataFrame, weights: Dict[str, float] = None) -> pd.DataFrame:
    """
    Compute a composite score and return a copy of df including 'composite_score'.

    Default weights chosen to favor quality but include wait, rating and mortality:
      - quality: 0.40
      - wait:    0.25  (lower is better)
      - rating:  0.20
      - mortality: 0.15

    The function performs min-max normalization for each component and treats missing
    data conservatively (neutral-ish score) so facilities with partial data are not dropped.
    """
    if weights is None:
        weights = {"quality": 0.4, "wait": 0.25, "rating": 0.2, "mortality": 0.15}

    wq = weights.get("quality", 0.4)
    ww = weights.get("wait", 0.25)
    wr = weights.get("rating", 0.2)
    wm = weights.get("mortality", 0.15)

    out = df.copy()

    # Quality: prefer adjusted_quality_points, fallback to total_quality_points
    if "adjusted_quality_points" in out.columns:
        quality = pd.to_numeric(out["adjusted_quality_points"], errors="coerce")
    elif "total_quality_points" in out.columns:
        quality = pd.to_numeric(out["total_quality_points"], errors="coerce")
    else:
        quality = pd.Series(np.nan, index=out.index)

    # Wait: lower is better
    wait = pd.to_numeric(out["detail_avg_time_in_ed_minutes"], errors="coerce") if "detail_avg_time_in_ed_minutes" in out.columns else pd.Series(np.nan, index=out.index)

    # Rating: higher is better
    rating = pd.to_numeric(out["detail_overall_patient_rating"], errors="coerce") if "detail_overall_patient_rating" in out.columns else pd.Series(np.nan, index=out.index)

    # Mortality: try to use mortality_sort_value; fallback to mortality_order to construct a numeric.
    if "detail_mortality_overall_text" in out.columns:
        tmp = prepare_mortality_sort(out)
        mortality_val = pd.to_numeric(tmp["mortality_sort_value"], errors="coerce").fillna(0)
        mortality_order = pd.to_numeric(tmp["mortality_order"], errors="coerce").fillna(2)
        mortality = (mortality_val - mortality_order)  # heuristic combination (higher better)
    else:
        mortality = pd.Series(np.nan, index=out.index)

    # min-max scale function (0..1) with safe defaults
    def minmax(series: pd.Series) -> pd.Series:
        s = series.copy().astype(float)
        if s.isna().all():
            return pd.Series(0.5, index=s.index)
        s = s.fillna(s.min())  # treat NaN as min so they don't artificially gain top score
        mn, mx = s.min(), s.max()
        if mn == mx:
            return pd.Series(0.5, index=s.index)
        return (s - mn) / (mx - mn)

    q_n = minmax(quality)
    w_n = 1.0 - minmax(wait)  # invert wait (lower is better)
    r_n = minmax(rating)
    m_n = minmax(mortality)

    out["composite_score"] = (wq * q_n.fillna(0.5) +
                              ww * w_n.fillna(0.5) +
                              wr * r_n.fillna(0.5) +
                              wm * m_n.fillna(0.5))

    return out


def sort_facilities(df: pd.DataFrame, key: str = "wait") -> pd.DataFrame:
    """
    Legacy helper left for compatibility. Prefer using _sort_df in main.py.
    """
    if key == "wait" and "wait_minutes" in df.columns:
        return df.sort_values(
            by=[col for col in ["wait_minutes", "detail_overall_patient_rating"] if col in df.columns],
            ascending=[True, False][:1 if "detail_overall_patient_rating" not in df.columns else 2],
            na_position="last",
        )
    if key == "rating" and "detail_overall_patient_rating" in df.columns:
        return df.sort_values(
            by=[col for col in ["detail_overall_patient_rating", "wait_minutes"] if col in df.columns],
            ascending=[False, True][:1 if "wait_minutes" not in df.columns else 2],
            na_position="last",
        )
    return df