# 🏥 HospiTrack — ER Wait Tracker
## Overview

HospiTrack is a Python + Streamlit-based web app that helps patients in the U.S. find nearby emergency departments and walk-in clinics with wait times, quality scores, and patient experience metrics.

Patients can:

1. Enter or select their location on a map

2. View nearby emergency facilities with their estimated wait times

3. Sort hospitals by ED efficiency, patient satisfaction, or mortality performance

4. Adjust quality rankings based on chief complaints (e.g., Stroke, Heart Attack, Pneumonia)

## Tech Stack

Frontend: Streamlit, Leaflet (via st.map)

Backend and Data Tranformation Pipeline: Python (Pandas)

Scraping: BeautifulSoup, Requests

Libraries: `streamlit`, `pandas`, `numpy`, `geopy`, `folium`

## Dataset  
The final working dataset (`midwest_er_transformed_final.csv`) includes the following relevant columns:

| Column | Description |
|---------|--------------|
| `hospital_name` | Hospital name |
| `detail_address` | Full street address |
| `lat`, `lon` | Geocoded coordinates |
| `detail_avg_time_in_ed_minutes` | Average ED time |
| `detail_overall_patient_rating_points` | Patient rating score |
| `mortality_overall_contribution` | Mortality performance (“better”, “worse”, etc.) |
| `Top_Procedures` | Most common procedures |
| ... | Additional quality metrics |

## Setup Instructions  

1. Clone the repository or download the zip folder

2. Create and activate a virtual environment:

```bash
# For Windows
python -m venv venv
venv\Scripts\activate

# For Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies on the virtualenv: 
```bash
    pip install -r requirements.txt
```

4. Run the following command: 
```bash
    streamlit run app.py
```

## How It Works

### Input:
Users type their location. Validation ensures the US.

### Geocoding:
Geopy (Nominatim) converts the address to coordinates. We cache hospital coordinates to avoid repeated geocoding.

### Filtering & Sorting:

1. Find the 10 nearest hospitals using geographic distance.

2. Present the top 5, sorted by the user-selected metric (Quality, ED Time, Patient Rating, or Mortality Contribution).

3. If a chief complaint is selected, we use complaint-specific adjusted quality columns (e.g., adj_total_stroke) to reorder the quality metric.

### Display:

1. Map markers with hover/popups (name, address, website, quality points).

2. A compact, styled top-5 card list under the map with links to Google Maps and key metrics.

## Future Enhancements

1. Real-time API integration for live ER wait times

2. Predictive modeling for surges and staff recommendations

3. More data to include more states


# Collaborators: Imama Zahoor, Vidhi Kothari, Eugene Ho, Elissa Matlock, Jonah Zembower
