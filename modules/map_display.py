# modules/map_display.py
import pandas as pd
import folium
from folium.plugins import MarkerCluster

def render_map_html(df: pd.DataFrame, user_lat: float, user_lon: float, max_points: int = 8000) -> str:
    """
    Return HTML for a Leaflet map with clustered hospital markers.
    """
    m = folium.Map(location=[user_lat, user_lon], zoom_start=5, tiles="CartoDB positron")
    folium.Marker([user_lat, user_lon], tooltip="Selected location", icon=folium.Icon(color="blue")).add_to(m)

    cluster = MarkerCluster().add_to(m)

    count = 0
    for _, row in df.iterrows():
        lat, lon = row.get("lat"), row.get("lon")
        if pd.isna(lat) or pd.isna(lon):
            continue
        dist = row.get("distance_km")
        try:
            dist_txt = f"{float(dist):.1f} km" if dist == dist else "NA"
        except Exception:
            dist_txt = "NA"

        popup_html = f"""
        <b>{row.get('hospital_name', 'Unknown')}</b><br>
        {row.get('detail_address', '')}, {row.get('detail_city', '')}, {row.get('detail_state', '')} {row.get('detail_zip', '')}<br>
        Distance: {dist_txt}<br>
        Quality: {row.get('adjusted_quality_points', row.get('total_quality_points', 'NA'))}<br>
        ED Time (min): {row.get('detail_avg_time_in_ed_minutes', 'NA')}
        """

        folium.Marker(
            [lat, lon],
            tooltip=row.get("hospital_name", "Hospital"),
            popup=popup_html,
            icon=folium.Icon(color="red", icon="plus-sign")
        ).add_to(cluster)

        count += 1
        if count >= max_points:
            break

    return m.get_root().render()