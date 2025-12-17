# 🏥 HospiTrack - Intelligent Emergency Care Finder

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-00a393.svg)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.11+-3776ab.svg)](https://www.python.org)
[![Docker](https://img.shields.io/badge/Docker-ready-2496ed.svg)](https://www.docker.com)

> **Find the best emergency care when you need it most**

HospiTrack is an intelligent hospital search and recommendation platform that helps users find the most appropriate emergency care facility based on their medical needs, location, and priorities. Built with modern web technologies and powered by comprehensive hospital data, HospiTrack makes critical healthcare decisions faster and more informed.

---

## 🌟 Features

### 🔍 Intelligent Search
- **Location-Based**: Search by address, GPS coordinates, or use browser geolocation
- **Condition-Specific**: Get specialized rankings for heart attack, stroke, trauma, and more
- **Customizable Priorities**: Choose between fastest care, highest quality, best ratings, or lowest mortality

### 🗺️ Interactive Mapping
- Visual hospital locations with color-coded markers
- Distance calculations and route planning
- Real-time filtering and sorting
- Map-list synchronization for easy comparison

### ⏱️ Real Data
- Emergency department wait times
- Hospital quality scores and patient ratings
- Mortality rates by condition
- 4,000+ US hospitals with comprehensive metrics

### 🎯 Smart Triage Demo
- Rule-based and ML-powered triage recommendations
- Vital signs analysis
- Severity assessment
- Hospital sorting strategy suggestions

### 📊 Explore Mode
- Browse all hospitals nationwide
- Filter by state, quality, and performance
- Compare facilities side-by-side
- Export and analyze data

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+**
- **pip** (Python package manager)
- **Git**

### Step-by-Step Setup

#### 1. Clone the Repository
```bash
git clone <repository-url>
cd hospitracker
```

#### 2. Create a Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

#### 3. Install Dependencies
```bash
pip install -r requirements_fastapi.txt
```

#### 4. Verify Data Files
Ensure these files exist:
- `data/us_er.parquet` - Hospital database (auto-generated if missing)
- `models/triage_model.pkl` - ML triage model (optional)

If the Parquet file is missing, the app will automatically generate it from `data/us_er.csv` on first run.

#### 5. Run the Application
```bash
python main.py
```

The application will start on **http://localhost:8000**

#### 6. Access the Application
Open your browser and navigate to:
- **Main App**: http://localhost:8000/static/index.html
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/healthz

---

## 🐳 Docker Deployment

### Local Docker (Development)

#### Using Docker Compose
```bash
# Build and start
docker-compose up --build

# Run in background
docker-compose up -d

# Stop
docker-compose down
```

Access at: http://localhost:8000

### Production Docker

#### Build Production Image
```bash
docker build -f Dockerfile.prod -t hospitracker:latest .
```

#### Run Production Container
```bash
docker run -d \
  -p 8000:8000 \
  --name hospitracker \
  -e PORT=8000 \
  -e ML_DEMO_ENABLED=true \
  hospitracker:latest
```

---

## 📖 Usage Guide

### Find Emergency Care

1. Navigate to **Find Care** page
2. Select your symptoms (chest pain, stroke, trauma, etc.)
3. Choose your priority (speed, quality, rating, mortality)
4. Enter your location or use current location
5. Set search radius (default: 50 km)
6. Optional: Filter by state
7. Click **Search** to view ranked results

### Explore Hospitals

1. Navigate to **Explore** page
2. Browse 4,000+ hospitals across the US
3. Use filters:
   - State selection
   - Sort by quality, wait time, mortality
   - Search by hospital name
4. Click any hospital for detailed information

### Triage Demo

1. Navigate to **Demo** page
2. Select demonstration mode:
   - **Rule-Based**: Logic-driven recommendations
   - **ML-Powered**: Machine learning predictions
3. Enter patient information:
   - Chief complaint
   - Age group
   - Severity level
   - Vital signs
4. View triage recommendations and explanations

---

## 🛠️ Development

### Project Structure
```
hospitracker/
├── main.py                 # FastAPI application entry point
├── modules/                # Core application modules
│   ├── data_loader.py     # Hospital data processing
│   ├── geolocation.py     # Location services
│   ├── sorting_logic.py   # Hospital ranking algorithms
│   ├── map_display.py     # Map rendering
│   ├── triage_rules.py    # Rule-based triage logic
│   └── triage_ml.py       # ML triage model
├── static/                 # Frontend files
│   ├── css/               # Stylesheets
│   ├── js/                # JavaScript utilities
│   ├── index.html         # Landing page
│   ├── home.html          # Find Care interface
│   ├── results.html       # Search results
│   ├── explore.html       # Hospital browser
│   ├── demo.html          # Triage demo
│   └── about.html         # About page
├── data/                   # Hospital datasets
│   ├── us_er.csv          # Source data
│   └── us_er.parquet      # Optimized cache
├── models/                 # ML models
│   └── triage_model.pkl   # Trained triage model
├── tests/                  # Test suites
├── Dockerfile.prod         # Production Docker config
├── docker-compose.yml      # Development Docker config
├── requirements_fastapi.txt # Python dependencies
└── README.md              # This file
```

### Running Tests
```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run all tests
pytest

# Run with coverage
pytest --cov=modules --cov-report=html

# Run specific test file
pytest tests/test_sorting.py
```

### Environment Variables

Create a `.env` file for custom configuration:
```env
# Core Settings
PORT=8000
PYTHONUNBUFFERED=1

# Data Path
HOSPITRACK_DATA_PATH=data/us_er.parquet

# Geocoding
GEOCODING_CACHE_SIZE=500
GEOCODING_RATE_LIMIT=1

# Features
ML_DEMO_ENABLED=true

# Performance
GUNICORN_WORKERS=4
GUNICORN_TIMEOUT=120
```

---

## 🌐 API Documentation

### Key Endpoints

#### Search Hospitals
```http
POST /api/search
Content-Type: application/json

{
  "lat": 37.7749,
  "lon": -122.4194,
  "radius": 50,
  "complaint": "chest_pain",
  "sort": "ed_time_asc",
  "state_filter": "CA"
}
```

#### Explore Hospitals
```http
GET /api/explore?state=CA&sort=quality_desc&page=1&per_page=50
```

#### Triage Recommendation
```http
POST /api/triage
Content-Type: application/json

{
  "chief_complaint": "chest pain",
  "age": 45,
  "severity": 3,
  "heart_rate": 95,
  "systolic_bp": 140,
  "respiratory_rate": 20,
  "use_ml_model": false
}
```

#### Get States List
```http
GET /api/states
```

**Full API documentation available at**: http://localhost:8000/docs

---

## 🚀 Deployment

### Deploy to Render (Recommended)

#### One-Click Deploy
[![Deploy to Render](https://render.com/docs/deploy-to-render/opengraph-image?0486a2afd882d86e)

#### Manual Deployment

1. **Push to GitHub**:
   ```bash
   git add .
   git commit -m "Deploy to Render"
   git push origin main
   ```

2. **Create Render Web Service**:
   - Go to [Render Dashboard](https://dashboard.render.com)
   - Click **New +** → **Web Service**
   - Connect your GitHub repository
   - Use these settings:
     - **Name**: hospitracker
     - **Environment**: Docker
     - **Dockerfile Path**: Dockerfile.prod
     - **Branch**: main

3. **Configure Environment Variables**:
   ```
   PORT=8000
   PYTHONUNBUFFERED=1
   ML_DEMO_ENABLED=true
   ```

4. **Deploy**: Click **Create Web Service**

Your app will be available at: `https://hospitracker.onrender.com`

### Deploy to Other Platforms

#### Fly.io
```bash
# Install Fly CLI
curl -L https://fly.io/install.sh | sh

# Launch app
fly launch --dockerfile Dockerfile.prod

# Deploy
fly deploy
```

#### Railway
```bash
# Install Railway CLI
npm i -g @railway/cli

# Login and init
railway login
railway init

# Deploy
railway up
```

#### VPS/Cloud Server
```bash
# Clone and setup
git clone <repo-url> /opt/hospitracker
cd /opt/hospitracker

# Build Docker image
docker build -f Dockerfile.prod -t hospitracker .

# Run container
docker run -d \
  -p 80:8000 \
  --name hospitracker \
  --restart unless-stopped \
  hospitracker
```

---

## 📊 Data Sources

Hospital data is sourced from:
- **CMS Hospital Compare**: Quality metrics, patient ratings, mortality data
- **Medicare Data**: Emergency department performance
- **HCAHPS Surveys**: Patient experience scores

Data includes:
- Emergency department wait times
- Hospital quality ratings (1-5 scale)
- Patient satisfaction scores
- Condition-specific mortality rates
- Hospital capabilities and services

---

## ⚠️ Important Medical Disclaimer

**HospiTrack is an informational tool only and does NOT provide medical advice, diagnosis, or treatment.**

- 🚨 **In life-threatening emergencies, call 911 immediately**
- Do NOT delay seeking emergency care while using this tool
- This tool does not diagnose medical conditions
- Always follow guidance from emergency dispatchers and medical professionals
- Hospital data may not reflect real-time availability
- Consult qualified healthcare providers for medical decisions

---

## 🤝 Contributing

We welcome contributions! Here's how to get started:

### Development Workflow

1. **Fork the repository**
2. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes**
4. **Run tests**:
   ```bash
   pytest
   ```
5. **Commit with clear messages**:
   ```bash
   git commit -m "Add feature: your feature description"
   ```
6. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```
7. **Open a Pull Request**

### Code Standards

- Follow PEP 8 for Python code
- Use Black for code formatting: `black main.py modules/`
- Add docstrings to all functions
- Write tests for new features
- Update documentation as needed

---

## 🐛 Troubleshooting

### Common Issues

#### "Module not found" error
```bash
# Ensure virtual environment is activated
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r requirements_fastapi.txt
```

#### "Data file not found"
```bash
# The app will auto-generate the Parquet file from CSV
# If issues persist, manually generate:
python -c "from modules.data_loader import build_parquet_cache; build_parquet_cache()"
```

#### Geocoding timeout errors
```bash
# Increase timeout in modules/geolocation.py
# Or use hardcoded coordinates for testing
```

#### Port already in use
```bash
# Change port in main.py or use environment variable
PORT=8080 python main.py
```

### Getting Help

- **GitHub Issues**: Report bugs or request features
- **API Documentation**: http://localhost:8000/docs
- **Demo Script**: See `DEMO_SCRIPT.md` for usage examples

---

## 🙏 Acknowledgments

- **FastAPI** - Modern Python web framework
- **Leaflet** - Interactive mapping library
- **CMS** - Hospital quality data
- **Open-source community** - Various libraries and tools

---

## 📧 Contact

For questions, feedback, or support:
- **GitHub Issues**: [Report a bug or request a feature]
- **API Documentation**: http://localhost:8000/docs

---

## 🗓️ Changelog

### Version 1.0.0 (Current)
- ✅ Intelligent hospital search with condition-specific rankings
- ✅ Interactive maps with 4,000+ US hospitals
- ✅ Rule-based and ML-powered triage demo
- ✅ Real-time geocoding and distance calculation
- ✅ Comprehensive API documentation
- ✅ Docker support for easy deployment
- ✅ Mobile-responsive modern UI
- ✅ Production-ready with health checks

---

**Made with ❤️ for better healthcare access**

*Note: localhost refers to the computer running the application. To access remotely or locally on your machine, you'll need to deploy the application on your own system.*
