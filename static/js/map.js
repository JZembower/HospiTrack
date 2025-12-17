// HospiTrack - Leaflet Map Utilities

let map = null;
let markersLayer = null;
let userMarker = null;
let currentHospitals = [];

// Initialize Map
function initMap(containerId = 'map', center = [39.8283, -98.5795], zoom = 4) {
  // Clear existing map if any
  if (map) {
    map.remove();
  }
  
  // Create map
  map = L.map(containerId, {
    zoomControl: true,
    scrollWheelZoom: true
  }).setView(center, zoom);
  
  // Add tile layer (OpenStreetMap)
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    maxZoom: 19,
    subdomains: ['a', 'b', 'c']
  }).addTo(map);
  
  // Create markers layer group
  markersLayer = L.layerGroup().addTo(map);
  
  // Add scale control
  L.control.scale({ imperial: true, metric: true }).addTo(map);
  
  return map;
}

// Add User Location Marker
function addUserMarker(lat, lon) {
  if (!map) return;
  
  // Remove existing user marker
  if (userMarker) {
    markersLayer.removeLayer(userMarker);
  }
  
  // Create custom icon for user location
  const userIcon = L.divIcon({
    className: 'user-marker',
    html: '<div style="background-color: #2563eb; width: 20px; height: 20px; border-radius: 50%; border: 3px solid white; box-shadow: 0 2px 5px rgba(0,0,0,0.3);"></div>',
    iconSize: [20, 20],
    iconAnchor: [10, 10]
  });
  
  userMarker = L.marker([lat, lon], { icon: userIcon })
    .bindPopup('<strong>Your Location</strong>')
    .addTo(markersLayer);
  
  return userMarker;
}

// Get Marker Color Based on Rank/Quality
function getMarkerColor(index, total) {
  // Color gradient from green (best) to red (worst)
  const ratio = index / Math.max(total - 1, 1);
  
  if (ratio < 0.33) {
    return '#10b981'; // Green - Top tier
  } else if (ratio < 0.67) {
    return '#f59e0b'; // Orange - Mid tier
  } else {
    return '#ef4444'; // Red - Lower tier
  }
}

// Create Hospital Marker
function createHospitalMarker(hospital, index, total) {
  const color = getMarkerColor(index, total);
  
  // Create custom icon
  const icon = L.divIcon({
    className: 'hospital-marker',
    html: `<div style="background-color: ${color}; width: 12px; height: 12px; border-radius: 50%; border: 2px solid white; box-shadow: 0 2px 5px rgba(0,0,0,0.4);"></div>`,
    iconSize: [12, 12],
    iconAnchor: [6, 6]
  });
  
  // Create popup content
  const popupContent = `
    <div style="min-width: 200px;">
      <strong style="color: #2563eb; font-size: 1.1em;">${hospital.facility_name || 'Unknown Hospital'}</strong>
      <div style="margin-top: 8px; font-size: 0.9em;">
        ${hospital.address ? `<div><strong>Address:</strong> ${hospital.address}</div>` : ''}
        ${hospital.distance_km ? `<div><strong>Distance:</strong> ${formatDistance(hospital.distance_km)}</div>` : ''}
        ${hospital.ed_avg_time_admit !== undefined ? `<div><strong>Wait Time:</strong> ${formatWaitTime(hospital.ed_avg_time_admit)}</div>` : ''}
        ${hospital.quality_points !== undefined ? `<div><strong>Quality Score:</strong> ${formatQualityScore(hospital.quality_points)}</div>` : ''}
        ${hospital.overall_rating ? `<div><strong>Rating:</strong> ${formatRating(hospital.overall_rating)}</div>` : ''}
        ${hospital.mortality_display ? `<div><strong>Mortality:</strong> ${hospital.mortality_display}</div>` : ''}
      </div>
      <button onclick="viewHospitalDetails('${hospital.facility_id || index}')" 
              style="margin-top: 10px; padding: 5px 15px; background-color: #2563eb; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 0.9em;">
        View Details
      </button>
    </div>
  `;
  
  // Create marker
  const marker = L.marker([hospital.lat, hospital.lon], { icon })
    .bindPopup(popupContent);
  
  // Store hospital data with marker
  marker.hospitalData = hospital;
  marker.hospitalIndex = index;
  
  return marker;
}

// Add Hospital Markers
function addHospitalMarkers(hospitals) {
  if (!map || !markersLayer) return;
  
  // Clear existing hospital markers (keep user marker)
  markersLayer.eachLayer(layer => {
    if (layer !== userMarker) {
      markersLayer.removeLayer(layer);
    }
  });
  
  // Store current hospitals
  currentHospitals = hospitals;
  
  // Add markers for each hospital
  const markers = hospitals.map((hospital, index) => {
    if (!hospital.lat || !hospital.lon) return null;
    const marker = createHospitalMarker(hospital, index, hospitals.length);
    marker.addTo(markersLayer);
    return marker;
  }).filter(m => m !== null);
  
  // Fit bounds to show all markers
  if (markers.length > 0) {
    const bounds = L.featureGroup(markers).getBounds();
    
    // Include user marker if exists
    if (userMarker) {
      bounds.extend(userMarker.getLatLng());
    }
    
    map.fitBounds(bounds, { padding: [50, 50], maxZoom: 12 });
  }
  
  return markers;
}

// Highlight Hospital Marker
function highlightMarker(hospitalIndex) {
  if (!markersLayer) return;
  
  markersLayer.eachLayer(layer => {
    if (layer === userMarker) return;
    
    if (layer.hospitalIndex === hospitalIndex) {
      // Highlight marker
      const icon = L.divIcon({
        className: 'hospital-marker-highlighted',
        html: '<div style="background-color: #2563eb; width: 18px; height: 18px; border-radius: 50%; border: 3px solid #fbbf24; box-shadow: 0 3px 8px rgba(0,0,0,0.5); animation: pulse 1s infinite;"></div>',
        iconSize: [18, 18],
        iconAnchor: [9, 9]
      });
      layer.setIcon(icon);
      
      // Open popup
      layer.openPopup();
      
      // Center map on marker
      map.setView(layer.getLatLng(), Math.max(map.getZoom(), 10));
    } else {
      // Reset to normal
      const color = getMarkerColor(layer.hospitalIndex, currentHospitals.length);
      const icon = L.divIcon({
        className: 'hospital-marker',
        html: `<div style="background-color: ${color}; width: 12px; height: 12px; border-radius: 50%; border: 2px solid white; box-shadow: 0 2px 5px rgba(0,0,0,0.4);"></div>`,
        iconSize: [12, 12],
        iconAnchor: [6, 6]
      });
      layer.setIcon(icon);
      layer.closePopup();
    }
  });
}

// View Hospital Details (to be implemented per page)
function viewHospitalDetails(facilityId) {
  console.log('View details for facility:', facilityId);
  // This will be overridden in each page's specific implementation
  alert('Details functionality will be implemented per page');
}

// Add CSS for marker animation
if (!document.getElementById('map-animation-styles')) {
  const style = document.createElement('style');
  style.id = 'map-animation-styles';
  style.textContent = `
    @keyframes pulse {
      0% { transform: scale(1); }
      50% { transform: scale(1.2); }
      100% { transform: scale(1); }
    }
  `;
  document.head.appendChild(style);
}