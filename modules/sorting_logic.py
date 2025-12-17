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