# modules/sorting_logic.py
import numpy as np
import pandas as pd

def parse_mortality(val):
    if isinstance(val, str):
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
    out = df.copy()
    if "detail_mortality_overall_text" in out.columns:
        out[["mortality_type", "mortality_sort_value"]] = (
            out["detail_mortality_overall_text"].apply(parse_mortality).apply(pd.Series)
        )
    else:
        out["mortality_type"] = "not used"
        out["mortality_sort_value"] = np.nan
    order = {"better": 0, "worse": 1, "not used": 2}
    out["mortality_order"] = out["mortality_type"].map(order)
    return out

def apply_complaint_adjustment(df: pd.DataFrame, complaint: str) -> tuple[pd.DataFrame, str]:
    # Map chief complaints to adjusted columns if present
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
        # Fallback to total_quality_points if not present
        base = "total_quality_points" if "total_quality_points" in out.columns else None
        if base is not None:
            out["adjusted_quality_points"] = out[base]
            label = "Overall Quality Points"
        else:
            out["adjusted_quality_points"] = np.nan
            label = "Quality Points"
    return out, label

def sort_facilities(df: pd.DataFrame, key: str = "wait") -> pd.DataFrame:
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