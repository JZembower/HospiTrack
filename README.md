# 🏥 HospiTrack — Smart Emergency Care Finder

[![CI/CD Pipeline](https://miro.medium.com/0*neovUAYgPR1UlMl4.png)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

**HospiTrack** is a privacy-focused, AI-powered hospital recommendation platform that helps people find the right emergency care based on their specific medical needs. Unlike generic hospital finders, HospiTrack uses **symptom-specific quality metrics** and **transparent triage algorithms** to provide personalized recommendations.

---

## 🌟 Key Features

### For Patients
- **🔍 Smart Search**: Find hospitals by symptom, priority (speed vs. quality), and location
- **🗺️ Interactive Maps**: Visual hospital finder with color-coded quality rankings
- **📊 Transparent Rankings**: Clear explanations for why hospitals are recommended
- **🔒 Privacy-First**: No PII storage, no tracking, geocoding cache is anonymized
- **📱 Mobile-Friendly**: Responsive design works on all devices

### For Healthcare Organizations
- **🤖 Triage API**: RESTful API for symptom-based hospital routing
- **🧠 ML-Powered Demo**: Machine learning triage model (rule-based + ML options)
- **📖 OpenAPI Docs**: Auto-generated interactive API documentation
- **⚡ Production-Ready**: Docker-based, horizontally scalable, health checks included

### Technical Highlights
- **Fast**: Parquet-optimized dataset, LRU geocoding cache, sub-second searches
- **Tested**: 43 passing tests covering core logic (sorting, geocoding, triage)
- **Deployed**: Production-ready with Dockerfile, CI/CD, and platform configs
- **Compliant**: Medical disclaimers throughout, no diagnostic claims

---

## 🚀 Quick Deploy to Production

**Ready to deploy HospiTrack in 5 minutes?**

[![Deploy to Render](https://i.ytimg.com/vi/Qb7tNtIEpcA/maxresdefault.jpg)

### Deployment Guides

Choose the guide that fits your needs:

| Guide | Best For | Time Required |
|-------|----------|---------------|
| **[QUICK_START.md](QUICK_START.md)** | First-time deployers who want step-by-step instructions | 5 minutes |
| **[DEPLOY_CHECKLIST.md](DEPLOY_CHECKLIST.md)** | Quick reference during deployment | 5 minutes |
| **[ACTUAL_DEPLOYMENT_STEPS.md](ACTUAL_DEPLOYMENT_STEPS.md)** | Comprehensive guide with troubleshooting | 10 minutes |
| **[DEPLOYMENT_FLOW.md](DEPLOYMENT_FLOW.md)** | Understanding architecture and data flow | 15 minutes |

**Current Status:**
- ✅ All code tested and ready
- ✅ Deployment files configured (`render.yaml`, `Dockerfile.prod`)
- ✅ 11 commits ready to push to GitHub
- ⏳ **Next step:** Push to GitHub and deploy!

**Quick Start Command:**
```bash
cd /home/ubuntu/hospitracker
git push origin main  # Push to GitHub
# Then visit: https://render.com/deploy?repo=https://github.com/JZembower/HospiTrack
```

---

## 📋 Table of Contents

- [Demo](#-demo)
- [Quick Start](#-quick-start)
- [Features in Detail](#-features-in-detail)
- [Installation](#-installation)
- [Usage](#-usage)
- [API Documentation](#-api-documentation)
- [Data Management](#-data-management)
- [Deployment](#-deployment)
- [Testing](#-testing)
- [Environment Variables](#-environment-variables)
- [Contributing](#-contributing)
- [Architecture](#-architecture)
- [Troubleshooting](#-troubleshooting)
- [License](#-license)
- [Credits](#-credits)

---

## 🎥 Demo

> **🚀 After deploying, update these URLs with your actual Render URL:**  
> `https://hospitracker-XXXX.onrender.com`

**Live Demo**: Coming soon (after deployment)  
**API Docs**: Coming soon (after deployment)

<!-- After deployment, replace with:
**Live Demo**: [https://hospitracker-XXXX.onrender.com](https://hospitracker-XXXX.onrender.com)  
**API Docs**: [https://hospitracker-XXXX.onrender.com/docs](https://hospitracker-XXXX.onrender.com/docs)
-->

### Demo Walkthrough
See [DEMO_SCRIPT.md](./DEMO_SCRIPT.md) for a complete product demo script.

**Quick Test**:
```bash
curl -X POST https://your-app.onrender.com/api/search \\
  -H "Content-Type: application/json" \\
  -d '{
    "complaint": "chest pain",
    "priority": "fastest_care",
    "user_location": "San Francisco, CA",
    "radius_km": 25
  }'
```

---

## 🚀 Quick Start

### Prerequisites
- **Python 3.11+** (3.11 recommended)
- **Docker** (optional, but recommended)
- **Git**
- **Data file**: `data/us_er.parquet` (hospital dataset)

### Option 1: Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/hospitracker.git
cd hospitracker

# Start with Docker Compose
docker compose up --build -d

# Check health
curl http://localhost:8000/healthz

# Open in browser
open http://localhost:8000/
```

**Windows PowerShell** (uses helper script):
```powershell
python .\\dev_start.py
```

### Option 2: Local Python

```bash
# Clone and navigate
git clone https://github.com/YOUR_USERNAME/hospitracker.git
cd hospitracker

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate

# Install dependencies
pip install -r requirements_fastapi.txt

# Run the application
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Access the application**:
- Landing page: http://localhost:8000/
- API docs: http://localhost:8000/docs
- Health check: http://localhost:8000/healthz

---

## ✨ Features in Detail

### 1. Emergency Care Search (`/static/home.html`)
- **Symptom Selection**: Choose from common emergencies (chest pain, stroke, difficulty breathing, etc.)
- **Priority Options**:
  - **Fastest Care**: Prioritizes lowest ED wait times
  - **Highest Quality**: Prioritizes symptom-specific quality metrics
  - **Best Rating**: Prioritizes patient satisfaction ratings
  - **Best Mortality**: Prioritizes hospitals with better survival outcomes
- **Location Input**: Address, ZIP code, or browser geolocation
- **Radius Control**: Adjustable search radius (5-100 km)
- **Results**: Ranked hospital list with interactive map

### 2. Explore Hospitals (`/static/explore.html`)
- **Nationwide Search**: Browse all hospitals without emergency context
- **Flexible Filters**: Search by name, city, state, or location
- **Dynamic Sorting**: Sort by quality, wait time, rating, or mortality
- **Pagination**: Efficiently browse large result sets
- **Export-Ready**: Results optimized for research or travel planning

### 3. Company Demo (`/static/demo.html`)
- **Triage API Showcase**: Interactive demo for healthcare companies
- **Dual Modes**:
  - **Rule-Based**: Deterministic triage using medical guidelines
  - **ML Demo**: Probabilistic predictions with confidence scores (synthetic data)
- **API Integration Guide**: Sample curl commands and response formats
- **Feature Importance**: Explainable AI for ML predictions

### 4. Interactive Maps (all pages)
- **Leaflet Integration**: OpenStreetMap-based interactive maps
- **Color-Coded Markers**: Green (top-ranked), orange (mid), red (lower-ranked)
- **Marker Clustering**: Automatic clustering for dense urban areas
- **Popups**: Quick-view hospital details on marker click
- **List Sync**: Clicking hospital card highlights map marker

---

## 💾 Installation

### System Requirements
- **OS**: Linux, macOS, or Windows
- **RAM**: 1 GB minimum, 2 GB recommended
- **Disk**: 500 MB for application + dependencies
- **Python**: 3.11+ (tested on 3.11.5)

### Development Setup

1. **Clone repository**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/hospitracker.git
   cd hospitracker
   ```

2. **Set up virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\\Scripts\\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install --upgrade pip
   pip install -r requirements_fastapi.txt
   ```

4. **Verify data files**:
   ```bash
   ls -lh data/us_er.parquet
   ls -lh models/triage_model.pkl  # Optional, for ML demo
   ```

5. **Run tests** (optional but recommended):
   ```bash
   pytest tests/ -v
   ```

6. **Start development server**:
   ```bash
   uvicorn main:app --reload --port 8000
   ```

---

## 📖 Usage

### Web Interface

#### Landing Page
Visit `http://localhost:8000/` to see:
- Overview of features
- Navigation to Emergency Search, Explore, and Demo
- Medical disclaimers

#### Emergency Care Search
1. Navigate to `/static/home.html`
2. Select symptom (e.g., \"Chest Pain\")
3. Choose priority (e.g., \"Fastest Care\")
4. Enter location or use browser geolocation
5. Set search radius (5-100 km)
6. Click \"Find Hospitals\"
7. View results on map and ranked list

#### Explore Hospitals
1. Navigate to `/static/explore.html`
2. Filter by state (e.g., \"California\")
3. Sort by desired metric (quality, time, rating, mortality)
4. Optionally add location-based search
5. Browse paginated results

#### Company Triage Demo
1. Navigate to `/static/demo.html`
2. Fill in patient intake form:
   - Complaint, severity, age band, vital signs
3. Toggle between \"Rule-Based\" and \"ML Demo\"
4. Click \"Get Triage Recommendation\"
5. Review triage profile and API integration guide

### Command-Line Testing

#### Health Check
```bash
curl http://localhost:8000/healthz
# Expected: {\"status\": \"healthy\"}
```

#### Search API
```bash
curl -X POST http://localhost:8000/api/search \\
  -H \"Content-Type: application/json\" \\
  -d '{
    \"complaint\": \"chest pain\",
    \"priority\": \"fastest_care\",
    \"user_location\": \"San Francisco, CA\",
    \"radius_km\": 25
  }'
```

#### Explore API
```bash
curl \"http://localhost:8000/api/explore?state=CA&sort_by=quality&limit=10\"
```

#### Triage API (Rule-Based)
```bash
curl -X POST http://localhost:8000/api/triage \\
  -H \"Content-Type: application/json\" \\
  -d '{
    \"complaint\": \"chest pain\",
    \"severity\": 4,
    \"age_band\": \"adult\",
    \"heart_rate\": 110,
    \"use_ml\": false
  }'
```

#### Triage API (ML Demo)
```bash
curl -X POST http://localhost:8000/api/triage \\
  -H \"Content-Type: application/json\" \\
  -d '{
    \"complaint\": \"chest pain\",
    \"severity\": 4,
    \"age_band\": \"adult\",
    \"heart_rate\": 110,
    \"respiratory_rate\": 20,
    \"use_ml\": true
  }'
```

---

## 📡 API Documentation

### Interactive Documentation
Visit `http://localhost:8000/docs` for auto-generated Swagger UI with:
- All endpoint specifications
- Request/response schemas
- Interactive API tester (try endpoints in browser)

### Key Endpoints

#### `POST /api/search`
**Description**: Search for hospitals based on symptom and location.

**Request Body**:
```json
{
  \"complaint\": \"chest pain\",
  \"priority\": \"fastest_care\",
  \"user_location\": \"San Francisco, CA\",
  \"radius_km\": 25,
  \"state\": \"CA\"
}
```

**Response**:
```json
{
  \"hospitals\": [...],
  \"count\": 15,
  \"ranking_explanation\": \"Hospitals ranked by...\",
  \"user_location\": {\"lat\": 37.7749, \"lon\": -122.4194}
}
```

#### `GET /api/explore`
**Description**: Browse hospitals nationwide with filters.

**Query Parameters**:
- `state` (optional): Two-letter state code
- `search` (optional): Search by name/city
- `sort_by` (optional): quality, time, rating, mortality
- `limit` (optional): Results per page (default: 50)
- `offset` (optional): Pagination offset

#### `POST /api/triage`
**Description**: Get triage recommendation for patient intake.

**Request Body**:
```json
{
  \"complaint\": \"chest pain\",
  \"severity\": 4,
  \"age_band\": \"adult\",
  \"heart_rate\": 110,
  \"respiratory_rate\": 20,
  \"blood_pressure_systolic\": 140,
  \"blood_pressure_diastolic\": 90,
  \"use_ml\": false
}
```

**Response**:
```json
{
  \"triage_level\": \"urgent\",
  \"priority\": \"fastest_care\",
  \"adjusted_metric\": \"adj_total_heartattack\",
  \"explanation\": \"High severity chest pain...\",
  \"confidence\": 0.87
}
```

#### `GET /api/states`
**Description**: Get list of available states in dataset.

**Response**:
```json
{
  \"states\": [\"CA\", \"NY\", \"TX\", ...]
}
```

#### `GET /healthz`
**Description**: Health check endpoint for monitoring.

**Response**:
```json
{\"status\": \"healthy\"}
```

---

## 📊 Data Management

### Dataset Location
**Primary data file**: `data/us_er.parquet`

**Required columns**:
- `hospital_name`, `detail_address`, `detail_city`, `detail_state`, `detail_zip`
- `lat`, `lon` (geolocation)
- `total_quality_points`, `detail_avg_time_in_ed_minutes`
- `detail_overall_patient_rating`, `detail_mortality_overall_text`
- `adj_total_heartattack`, `adj_total_stroke`, `adj_total_pneu` (symptom-specific quality)

### Data Source
- **CMS Hospital Compare**: Public dataset from Centers for Medicare & Medicaid Services
- **Data Processing**: See `modules/data_loader.py` for transformation pipeline

### Updating the Dataset

**Option 1: Replace Parquet file**
```bash
# Backup current data
cp data/us_er.parquet data/us_er.parquet.bak

# Replace with new data
cp /path/to/new_data.parquet data/us_er.parquet

# Rebuild Docker image (if using Docker)
docker compose up --build -d
```

**Option 2: Convert CSV to Parquet**
```python
from pathlib import Path
from modules.data_loader import build_parquet_cache

csv_path = Path(\"us_er_transformed.csv\")
out_path = Path(\"data/us_er.parquet\")
df = build_parquet_cache(csv_path, out_path)
print(f\"Processed {len(df)} hospitals\")
```

### ML Model Files (Optional)
- **Location**: `models/triage_model.pkl`, `models/triage_encoders.pkl`
- **Training**: Use `train_triage_model.py` with your own EHR data
- **Note**: Current model trained on synthetic data for demo purposes

**Training custom model**:
```bash
python train_triage_model.py --data /path/to/triage_data.csv
```

---

## 🚢 Deployment

**Full deployment guide**: See [DEPLOYMENT.md](./DEPLOYMENT.md) for comprehensive instructions.

### Quick Deploy to Render (Recommended)

1. **Push code to GitHub**:
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/hospitracker.git
   git push -u origin main
   ```

2. **Create Render account**: Visit [render.com](https://render.com) and connect GitHub

3. **Deploy with Blueprint**:
   - In Render dashboard: **New +** → **Blueprint**
   - Select `hospitracker` repository
   - Render auto-detects `render.yaml`
   - Click **Apply**

4. **Set environment variables** (in Render dashboard):
   - `PORT=8000`
   - `GEOCODING_CACHE_SIZE=1000`
   - `ML_DEMO_ENABLED=true`
   - See [.env.example](./.env.example) for full list

5. **Access deployed app**: Visit your Render URL (e.g., `https://hospitracker.onrender.com`)

### Alternative Platforms
- **Fly.io**: See [DEPLOYMENT.md](./DEPLOYMENT.md#alternative-flyio-deployment)
- **Railway**: See [DEPLOYMENT.md](./DEPLOYMENT.md#alternative-railway-deployment)
- **AWS/GCP/Azure**: See [DEPLOYMENT.md](./DEPLOYMENT.md#custom-vpscloud-deployment)
- **Docker Compose (VPS)**: See [docker-compose.prod.yml](./docker-compose.prod.yml)

### Pre-Deployment Checklist
See [PRODUCTION_CHECKLIST.md](./PRODUCTION_CHECKLIST.md) for complete pre-deployment checks.

---

## 🧪 Testing

### Run All Tests
```bash
# Activate virtual environment
source venv/bin/activate

# Run tests with coverage
pytest tests/ -v --cov=modules --cov-report=html

# View coverage report
open htmlcov/index.html  # macOS
# or: xdg-open htmlcov/index.html  # Linux
# or: start htmlcov/index.html  # Windows
```

### Run Specific Test Suites
```bash
# Sorting logic tests
pytest tests/test_sorting.py -v

# Geocoding tests
pytest tests/test_geolocation.py -v

# Triage tests
pytest tests/test_triage.py -v

# API integration tests (requires running server)
pytest tests/test_api.py -v
```

### Linting and Formatting
```bash
# Check code formatting
black . --check

# Auto-format code
black .

# Run linter
flake8 . --config=.flake8

# Sort imports
isort .

# Check JavaScript/CSS formatting
prettier --check \"static/**/*.{js,css,html}\"
```

### Pre-Commit Hooks (Optional)
```bash
# Install pre-commit
pip install pre-commit

# Set up git hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

---

## ⚙️ Environment Variables

Create a `.env` file from the template:
```bash
cp .env.example .env
```

### Core Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | `8000` | Application port |
| `PYTHONUNBUFFERED` | `1` | Enable real-time logging |
| `HOSPITRACK_DATA_PATH` | `/app/data` | Data directory path |

### Geocoding Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `GEOCODING_CACHE_SIZE` | `1000` | LRU cache size for address lookups |
| `GEOCODING_RATE_LIMIT` | `1` | Requests per second |

### Feature Flags

| Variable | Default | Description |
|----------|---------|-------------|
| `ML_DEMO_ENABLED` | `true` | Enable ML triage demo |

### Logging

| Variable | Default | Description |
|----------|---------|-------------|
| `LOG_LEVEL` | `INFO` | Logging verbosity (DEBUG, INFO, WARNING, ERROR) |
| `ACCESS_LOG_ENABLED` | `true` | Enable access logs |

### Performance Tuning

| Variable | Default | Description |
|----------|---------|-------------|
| `GUNICORN_WORKERS` | `4` | Number of worker processes |
| `GUNICORN_TIMEOUT` | `120` | Worker timeout (seconds) |
| `GUNICORN_KEEPALIVE` | `5` | Keep-alive timeout (seconds) |

**Full list**: See [.env.example](./.env.example)

---

## 🤝 Contributing

We welcome contributions! Please follow these guidelines:

### Getting Started
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Set up development environment (see [Installation](#-installation))
4. Make your changes
5. Run tests: `pytest tests/ -v`
6. Run linters: `black . && flake8 .`
7. Commit changes: `git commit -m \"Add your feature\"`
8. Push to branch: `git push origin feature/your-feature-name`
9. Open a Pull Request

### Code Style
- **Python**: Follow PEP 8, use Black formatter (100 char line length)
- **JavaScript**: Use Prettier with provided config
- **Commits**: Use clear, descriptive commit messages

### Testing Requirements
- All new features must include tests
- Maintain >80% code coverage
- All tests must pass before PR merge

### Documentation
- Update README.md for user-facing changes
- Add docstrings to new functions/classes
- Update API documentation if endpoints change

---

## 🏗️ Architecture

### Project Structure
```
hospitracker/
├── main.py                    # FastAPI application, API routes
├── modules/
│   ├── data_loader.py        # Dataset loading and caching
│   ├── geolocation.py        # Geocoding service with privacy
│   ├── sorting_logic.py      # Hospital ranking algorithms
│   ├── map_display.py        # Map rendering
│   ├── triage_rules.py       # Rule-based triage logic
│   └── triage_ml.py          # ML triage model
├── static/
│   ├── index.html            # Landing page
│   ├── home.html             # Emergency search interface
│   ├── results.html          # Search results with map
│   ├── explore.html          # Hospital browser
│   ├── demo.html             # Triage demo
│   ├── css/main.css          # Shared styles
│   └── js/
│       ├── utils.js          # Shared utilities
│       └── map.js            # Leaflet map integration
├── tests/                    # Test suite
├── data/
│   └── us_er.parquet         # Hospital dataset
├── models/                   # ML models (optional)
├── Dockerfile.prod           # Production Docker image
├── docker-compose.yml        # Local development
├── docker-compose.prod.yml   # Production compose
├── render.yaml               # Render platform config
├── requirements_fastapi.txt  # Python dependencies
└── README.md                 # This file
```

### Technology Stack

**Backend**:
- **FastAPI**: Modern Python web framework
- **Uvicorn/Gunicorn**: ASGI server
- **Pandas**: Data processing
- **PyArrow**: Parquet file handling
- **scikit-learn**: ML triage model
- **Geopy/pgeocode**: Geocoding

**Frontend**:
- **Vanilla JavaScript**: No framework dependencies
- **Leaflet.js**: Interactive maps
- **OpenStreetMap**: Map tiles
- **Responsive CSS**: Mobile-first design

**Infrastructure**:
- **Docker**: Containerization
- **Render/Fly.io/Railway**: Cloud platforms
- **GitHub Actions**: CI/CD pipeline
- **Nginx**: Reverse proxy (for custom VPS)

### Data Flow
1. **User Input** → Frontend (HTML/JS)
2. **API Request** → FastAPI backend
3. **Geocoding** → Location resolution with caching
4. **Data Query** → Parquet file (in-memory Pandas DataFrame)
5. **Ranking** → Sorting logic based on priority + complaint
6. **Response** → JSON with hospitals + explanations
7. **Map Rendering** → Leaflet.js with color-coded markers

### Architecture Decisions
- **Parquet over CSV**: 5-10x faster load times, smaller file size
- **LRU Geocoding Cache**: Reduces API calls, privacy-preserving (hashed addresses)
- **Multi-page Frontend**: Better UX than single-page, easier to maintain
- **Rule-based + ML**: Provides flexible triage options for different use cases
- **Docker-first**: Consistent environments, easy deployment

**Full architecture analysis**: See [ARCHITECTURE_ANALYSIS.md](./ARCHITECTURE_ANALYSIS.md)

---

## 🐛 Troubleshooting

### Common Issues

#### Application Won't Start
**Symptom**: Container exits immediately or `uvicorn` command fails

**Solutions**:
1. Check data file exists: `ls -la data/us_er.parquet`
2. Verify dependencies installed: `pip list | grep fastapi`
3. Check logs: `docker logs hospitracker` (Docker) or console output (local)
4. Ensure port 8000 is available: `lsof -i :8000` (macOS/Linux) or `netstat -an | findstr :8000` (Windows)

#### Data File Not Found
**Symptom**: Error \"Could not load hospital data\"

**Solutions**:
1. Verify `data/us_er.parquet` exists in project root
2. Check `HOSPITRACK_DATA_PATH` environment variable
3. Rebuild Parquet from CSV: `python -c \"from modules.data_loader import build_parquet_cache; build_parquet_cache('us_er_transformed.csv', 'data/us_er.parquet')\"`

#### Geocoding Errors
**Symptom**: \"Location not found\" for valid addresses

**Solutions**:
1. Check internet connectivity (geocoding requires external API)
2. Increase `GEOCODING_CACHE_SIZE` if repeated lookups fail
3. Use ZIP codes instead of full addresses (more reliable)
4. Enable browser geolocation for most accurate results

#### Map Not Rendering
**Symptom**: Blank map or markers not appearing

**Solutions**:
1. Check browser console for JavaScript errors (F12 → Console)
2. Verify Leaflet.js CDN is accessible (check Network tab)
3. Ensure data includes valid `lat`/`lon` values
4. Clear browser cache and reload

#### ML Demo Fails
**Symptom**: Triage API returns error when `use_ml=true`

**Solutions**:
1. Verify `models/triage_model.pkl` exists
2. Check `ML_DEMO_ENABLED=true` in environment
3. Review logs for model loading errors
4. Fall back to rule-based triage (`use_ml=false`)

#### Docker Build Fails
**Symptom**: \"Error building image\"

**Solutions**:
1. Check Dockerfile syntax
2. Ensure all files in `.dockerignore` exist
3. Verify `requirements_fastapi.txt` is valid
4. Increase Docker memory allocation (Docker Desktop settings)

#### High Memory Usage
**Symptom**: Container killed or OOM errors

**Solutions**:
1. Reduce Gunicorn workers: `GUNICORN_WORKERS=2`
2. Upgrade instance/VPS RAM (minimum 1 GB, recommended 2 GB)
3. Check for memory leaks in logs
4. Optimize Parquet file (remove unused columns)

### Debug Mode

**Enable verbose logging**:
```bash
export LOG_LEVEL=DEBUG
uvicorn main:app --reload
```

**Docker logs**:
```bash
docker compose logs -f hospitracker
```

**Health check**:
```bash
curl -v http://localhost:8000/healthz
```

### Getting Help
- **GitHub Issues**: [https://github.com/YOUR_USERNAME/hospitracker/issues](https://github.com/YOUR_USERNAME/hospitracker/issues)
- **Documentation**: [DEPLOYMENT.md](./DEPLOYMENT.md), [PRODUCTION_CHECKLIST.md](./PRODUCTION_CHECKLIST.md)
- **API Docs**: http://localhost:8000/docs

---

## 📄 License

**MIT License**

Copyright (c) 2024 HospiTrack Team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the \"Software\"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED \"AS IS\", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

**Third-Party Licenses**:
- FastAPI: MIT License
- Folium/Leaflet.js: BSD License
- OpenStreetMap Data: ODbL License (attribution required)
- CMS Hospital Compare Data: Public Domain

---

## 👥 Credits

**Development Team**:
- Imama Zahoor
- Vidhi Kothari
- Eugene Ho
- Elissa Matlock
- Jonah Zembower

**Data Sources**:
- Centers for Medicare & Medicaid Services (CMS Hospital Compare)
- OpenStreetMap Contributors

**Technologies**:
- FastAPI, Pandas, scikit-learn, Geopy, Leaflet.js, and many more open-source projects

---

## 📚 Additional Documentation

- **[DEPLOYMENT.md](./DEPLOYMENT.md)**: Complete deployment guide for all platforms
- **[DEMO_SCRIPT.md](./DEMO_SCRIPT.md)**: Step-by-step product demo walkthrough
- **[PRODUCTION_CHECKLIST.md](./PRODUCTION_CHECKLIST.md)**: Pre-deployment verification checklist
- **[ARCHITECTURE_ANALYSIS.md](./ARCHITECTURE_ANALYSIS.md)**: Detailed technical architecture
- **[BACKEND_ENHANCEMENTS.md](./BACKEND_ENHANCEMENTS.md)**: Backend implementation details
- **[.env.example](./.env.example)**: Environment variable template

---

## 🔗 Links

- **GitHub Repository**: [https://github.com/YOUR_USERNAME/hospitracker](https://github.com/YOUR_USERNAME/hospitracker)
- **Live Demo**: [https://hospitracker.onrender.com](https://hospitracker.onrender.com) *(Update with your URL)*
- **API Documentation**: [https://hospitracker.onrender.com/docs](https://hospitracker.onrender.com/docs) *(Update with your URL)*

---

**⚠️ Medical Disclaimer**: HospiTrack is for informational purposes only and does not provide medical advice. For life-threatening emergencies, always call 911 or your local emergency number immediately. This tool is not a substitute for professional medical judgment.

---

**Built with ❤️ for better healthcare access**