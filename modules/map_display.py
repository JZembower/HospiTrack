# modules/map_display.py
import pandas as pd
import folium
from folium.plugins import MarkerCluster

def render_map_html(df: pd.DataFrame, user_lat: float, user_lon: float, max_points: int = 8000) -> str:
    """
    Render a Folium (Leaflet) map with clustered hospital markers.
    Returns the HTML string for embedding.
    """
    m = folium.Map(location=[user_lat, user_lon], zoom_start=8, tiles="CartoDB positron")
    folium.Marker([user_lat, user_lon], tooltip="Selected location", icon=folium.Icon(color="blue", icon="user")).add_to(m)

    cluster = MarkerCluster().add_to(m)

    count = 0
    for _, row in df.iterrows():
        lat = row.get("lat")
        lon = row.get("lon")
        if pd.isna(lat) or pd.isna(lon):
            continue

        dist = row.get("distance_km", None)
        try:
            dist_txt = f"{float(dist):.1f} km" if (dist is not None and not pd.isna(dist)) else "NA"
        except Exception:
            dist_txt = "NA"

        quality = row.get("adjusted_quality_points", row.get("total_quality_points", "NA"))
        ed_time = row.get("detail_avg_time_in_ed_minutes", "NA")
        mort = row.get("detail_mortality_overall_text", "NA")
        rating = row.get("detail_overall_patient_rating", "NA")
        composite = row.get("composite_score", None)

        popup_lines = [
            f"<b>{row.get('hospital_name', 'Unknown')}</b>",
            f"{row.get('detail_address', '')}, {row.get('detail_city', '')}, {row.get('detail_state', '')} {row.get('detail_zip', '')}",
            f"Distance: {dist_txt}",
            f"Quality: {quality}",
            f"ED Time (min): {ed_time}",
            f"Rating: {rating}",
            f"Mortality: {mort}",
        ]
        if composite is not None:
            popup_lines.append(f"<b>Composite Score: {float(composite):.3f}</b>")

        popup_html = "<br>".join(popup_lines)

        folium.Marker(
            [lat, lon],
            tooltip=row.get("hospital_name", "Hospital"),
            popup=popup_html,
            icon=folium.Icon(color="red", icon="plus")
        ).add_to(cluster)

        count += 1
        if count >= max_points:
            break

    return m.get_root().render()