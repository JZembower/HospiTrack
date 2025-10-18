import numpy as np
import pandas as pd

# Helper to parse mortality strings into sortable values
def parse_mortality(val):
    if isinstance(val, str):
        val = val.lower()
        if "not used" in val: return ("not used", np.nan)
        if "worse" in val:
            num = ''.join(c for c in val if c.isdigit())
            return ("better", int(num) if num else 0)
        if "better" in val:
            num = ''.join(c for c in val if c.isdigit())
            return ("worse", -int(num) if num else 0)
    return ("not used", np.nan)

# Prepare DataFrame for mortality sorting
def prepare_mortality_sort(df):
    df[["mortality_type", "mortality_sort_value"]] = (
        df["mortality_overall_contribution"].apply(parse_mortality).apply(pd.Series)
    )
    order = {"better": 0, "worse": 1, "not used": 2}
    df["mortality_order"] = df["mortality_type"].map(order)
    return df

# Adjust quality points based on chief complaint and sorting option
def sort_by_selected_option(complaint_map, chief_complaint, df):
    if complaint_map[chief_complaint]:
        adjusted_col = complaint_map[chief_complaint]
        df["adjusted_quality_points"] = df[adjusted_col]
        quality_label = f"Quality Points (adjusted for {chief_complaint})"
    else:
        df["adjusted_quality_points"] = df["total_quality_points"]
        quality_label = "Overall Quality Points"
    return df, quality_label