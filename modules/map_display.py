import folium
from streamlit_folium import st_folium

# This function renders a map with user and hospital locations
def render_map(df, user_lat, user_lon):
    m = folium.Map(location=[user_lat, user_lon], zoom_start=11)
    folium.Marker([user_lat, user_lon], tooltip="You are here", icon=folium.Icon(color="blue")).add_to(m)
    for _, row in df.iterrows():
        popup_html = f"""
        <b>{row['hospital_name']}</b><br>
        {row['detail_address']}, {row['detail_city']}, {row['detail_state']} {row['detail_zip']}<br>
        Distance: {row['distance_km']:.2f} km<br>
        Quality Points: {row['total_quality_points']}
        """
        folium.Marker(
            [row["lat"], row["lon"]],
            tooltip=row["hospital_name"],
            popup=popup_html,
            icon=folium.Icon(color="red", icon="plus-sign")
        ).add_to(m)
    st_folium(m, width=700, height=500, returned_objects=[])