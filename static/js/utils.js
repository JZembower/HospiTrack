// HospiTrack - Shared Utilities

// API Base URL
const API_BASE = '';

// Loading State Management
let loadingOverlay = null;

function showLoading(message = 'Loading...') {
  if (!loadingOverlay) {
    loadingOverlay = document.createElement('div');
    loadingOverlay.className = 'loading-overlay';
    loadingOverlay.innerHTML = `
      <div style="text-align: center;">
        <div class="spinner"></div>
        <div class="loading-text" id="loading-message">${message}</div>
      </div>
    `;
    document.body.appendChild(loadingOverlay);
  } else {
    loadingOverlay.style.display = 'flex';
    document.getElementById('loading-message').textContent = message;
  }
}

function hideLoading() {
  if (loadingOverlay) {
    loadingOverlay.style.display = 'none';
  }
}

// Error Handling
function showError(message, containerId = null) {
  const errorDiv = document.createElement('div');
  errorDiv.className = 'error-message';
  errorDiv.innerHTML = `
    <strong>⚠️ Error:</strong> ${message}
    <button onclick="this.parentElement.remove()" style="float: right; background: none; border: none; cursor: pointer; font-size: 1.2rem;">&times;</button>
  `;
  
  if (containerId) {
    const container = document.getElementById(containerId);
    if (container) {
      container.insertBefore(errorDiv, container.firstChild);
    }
  } else {
    document.body.insertBefore(errorDiv, document.body.firstChild);
  }
  
  // Auto-remove after 10 seconds
  setTimeout(() => errorDiv.remove(), 10000);
}

// API Call Wrapper with Retry
async function apiCall(url, options = {}, retries = 2) {
  try {
    const response = await fetch(API_BASE + url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers
      }
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      const errorMessage = errorData.detail || errorData.error || errorData.message || `HTTP ${response.status}: ${response.statusText}`;
      throw new Error(errorMessage);
    }
    
    return await response.json();
  } catch (error) {
    if (retries > 0 && !error.message.includes('HTTP 4')) {
      // Retry on network errors and 5xx errors, but not 4xx client errors
      await new Promise(resolve => setTimeout(resolve, 1000));
      return apiCall(url, options, retries - 1);
    }
    // Ensure error has a message property
    if (!error.message) {
      error.message = String(error);
    }
    throw error;
  }
}

// GET request
async function apiGet(endpoint, params = {}) {
  const queryString = new URLSearchParams(params).toString();
  const url = queryString ? `${endpoint}?${queryString}` : endpoint;
  return apiCall(url, { method: 'GET' });
}

// POST request
async function apiPost(endpoint, data = {}) {
  return apiCall(endpoint, {
    method: 'POST',
    body: JSON.stringify(data)
  });
}

// URL State Management
function getUrlParams() {
  const params = new URLSearchParams(window.location.search);
  const result = {};
  for (const [key, value] of params) {
    result[key] = value;
  }
  return result;
}

function setUrlParams(params) {
  const url = new URL(window.location);
  Object.keys(params).forEach(key => {
    if (params[key] !== null && params[key] !== undefined && params[key] !== '') {
      url.searchParams.set(key, params[key]);
    } else {
      url.searchParams.delete(key);
    }
  });
  window.history.pushState({}, '', url);
}

function updateUrlParams(params) {
  const currentParams = getUrlParams();
  setUrlParams({ ...currentParams, ...params });
}

// Browser Geolocation
function getCurrentLocation() {
  return new Promise((resolve, reject) => {
    if (!navigator.geolocation) {
      reject(new Error('Geolocation is not supported by your browser. Please enter your address or coordinates manually.'));
      return;
    }
    
    navigator.geolocation.getCurrentPosition(
      position => {
        resolve({
          lat: position.coords.latitude,
          lon: position.coords.longitude
        });
      },
      error => {
        let message = 'Unable to get your location. Please enter your address or coordinates manually.';
        if (error.code === error.PERMISSION_DENIED) {
          message = 'Location permission denied. Please enable location access in your browser settings, or enter your address manually.';
        } else if (error.code === error.POSITION_UNAVAILABLE) {
          message = 'Location information unavailable. Please check your device settings or enter your address manually.';
        } else if (error.code === error.TIMEOUT) {
          message = 'Location request timed out. This may happen due to poor GPS signal or browser settings. Please try again or enter your address manually.';
        }
        reject(new Error(message));
      },
      {
        enableHighAccuracy: false, // Changed to false for faster response
        timeout: 30000, // Increased from 10s to 30s
        maximumAge: 60000 // Allow cached location up to 1 minute old
      }
    );
  });
}

// Form Validation
function validateForm(formId, rules) {
  const form = document.getElementById(formId);
  if (!form) return false;
  
  let isValid = true;
  const errors = [];
  
  Object.keys(rules).forEach(fieldName => {
    const field = form.elements[fieldName];
    if (!field) return;
    
    const rule = rules[fieldName];
    const value = field.value.trim();
    
    // Required validation
    if (rule.required && !value) {
      isValid = false;
      errors.push(`${rule.label || fieldName} is required`);
      field.classList.add('error');
    } else {
      field.classList.remove('error');
    }
    
    // Min/Max validation for numbers
    if (value && rule.type === 'number') {
      const numValue = parseFloat(value);
      if (rule.min !== undefined && numValue < rule.min) {
        isValid = false;
        errors.push(`${rule.label || fieldName} must be at least ${rule.min}`);
      }
      if (rule.max !== undefined && numValue > rule.max) {
        isValid = false;
        errors.push(`${rule.label || fieldName} must be at most ${rule.max}`);
      }
    }
    
    // Pattern validation
    if (value && rule.pattern && !rule.pattern.test(value)) {
      isValid = false;
      errors.push(rule.patternMessage || `${rule.label || fieldName} format is invalid`);
    }
  });
  
  if (!isValid && errors.length > 0) {
    showError(errors.join('<br>'));
  }
  
  return isValid;
}

// Format Distance
function formatDistance(km) {
  if (!km && km !== 0) return 'N/A';
  return `${km.toFixed(1)} km`;
}

// Format Rating
function formatRating(rating) {
  if (!rating && rating !== 0) return 'N/A';
  // Handle string ratings (e.g., "AVERAGE", "VERY GOOD")
  if (typeof rating === 'string') {
    return rating;
  }
  // Handle numeric ratings
  return `${rating.toFixed(1)} ⭐`;
}

// Format Wait Time
function formatWaitTime(minutes) {
  if (!minutes && minutes !== 0) return 'N/A';
  if (minutes < 60) return `${Math.round(minutes)} min`;
  const hours = Math.floor(minutes / 60);
  const mins = Math.round(minutes % 60);
  return mins > 0 ? `${hours}h ${mins}m` : `${hours}h`;
}

// Format Quality Score
function formatQualityScore(score) {
  if (!score && score !== 0) return 'N/A';
  return score.toFixed(0);
}

// Format Mortality
function formatMortality(mortality) {
  if (!mortality) return 'N/A';
  return mortality;
}

// Debounce Function
function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

// Load States List
async function loadStates() {
  try {
    const data = await apiGet('/api/states');
    return data.states || [];
  } catch (error) {
    console.error('Failed to load states:', error);
    return [];
  }
}

// Populate State Dropdown
async function populateStateDropdown(selectId, includeAllOption = true) {
  const select = document.getElementById(selectId);
  if (!select) return;
  
  try {
    const states = await loadStates();
    
    if (includeAllOption) {
      select.innerHTML = '<option value="">All States</option>';
    } else {
      select.innerHTML = '<option value="">Select State</option>';
    }
    
    states.forEach(state => {
      const option = document.createElement('option');
      option.value = state;
      option.textContent = state;
      select.appendChild(option);
    });
  } catch (error) {
    showError('Failed to load states list');
  }
}

// Mobile Menu Toggle
function initMobileMenu() {
  const toggle = document.querySelector('.navbar-toggle');
  const menu = document.querySelector('.navbar-menu');
  
  if (toggle && menu) {
    toggle.addEventListener('click', () => {
      menu.classList.toggle('active');
    });
    
    // Close menu when clicking outside
    document.addEventListener('click', (e) => {
      if (!toggle.contains(e.target) && !menu.contains(e.target)) {
        menu.classList.remove('active');
      }
    });
  }
}

// Active Navigation Link
function setActiveNavLink() {
  const currentPage = window.location.pathname.split('/').pop() || 'index.html';
  const navLinks = document.querySelectorAll('.navbar-menu a');
  
  navLinks.forEach(link => {
    const linkPage = link.getAttribute('href');
    if (linkPage === currentPage || (currentPage === '' && linkPage === 'index.html')) {
      link.classList.add('active');
    } else {
      link.classList.remove('active');
    }
  });
}

// Initialize Common Features
function initCommon() {
  initMobileMenu();
  setActiveNavLink();
}

// Run on DOM load
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initCommon);
} else {
  initCommon();
}
