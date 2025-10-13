import streamlit as st
import pandas as pd

# This function renders sorting buttons
def render_sort_buttons(sort_options):
    cols = st.columns(len(sort_options))
    for i, (key, label) in enumerate(sort_options.items()):
        if cols[i].button(f"↑ {label}", key=f"sort_{key}", use_container_width=True):
            st.session_state.selected_sort = key

# This function displays hospital cards with details
def display_hospital_cards(top_5, quality_label):
    for _, row in top_5.iterrows():
        gmaps_url = f"https://www.google.com/maps/search/?api=1&query={row['lat']},{row['lon']}"
        if pd.isna(row['detail_avg_time_in_ed_minutes']):
            row['detail_avg_time_in_ed_minutes'] = "ED wait time data not available"
        else:
            hours, mins = int(row['detail_avg_time_in_ed_minutes'] // 60), int(row['detail_avg_time_in_ed_minutes'] % 60)
            row['detail_avg_time_in_ed_minutes'] = f"{hours} hours {mins} mins"

        st.markdown(f"""
        <div class="hospital-card">
            <div class="hospital-name">🏥 {row['hospital_name']}</div>
            <div class="hospital-details">
                📍 {row['detail_address']}, {row['detail_city']}, {row['detail_state']} {row['detail_zip']}<br> 
                📌 <a href="{gmaps_url}" target="_blank">Open in Google Maps</a>
            </div>
            <div class="metric">⭐ {quality_label}: {row['adjusted_quality_points']}</div>
            <div class="metric">⏱️ ED Wait Times: {row["detail_avg_time_in_ed_minutes"]}</div>
            <div class="metric">💬 Patient Rating Points: {row['detail_overall_patient_rating_points']}</div>
            <div class="metric">⚕️ Mortality Contribution: {row['mortality_overall_contribution']}</div>
            <div class="metric">🏅 Top Procedures: {row['Top_Procedures']}</div>
        </div>
        """, unsafe_allow_html=True)

# This function displays the chief complaint selection box
def display_chief_complaint_info(complaint_map):
    return st.selectbox(
    "Quality with Chief Complaint:",
    list(complaint_map.keys()),
    index=0,
    )