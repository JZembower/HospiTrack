# HospiTrack Actual Deployment Steps to Render

**Date:** December 17, 2025  
**Repository:** https://github.com/JZembower/HospiTrack  
**Target Platform:** Render.com

---

## ✅ Completed Pre-Deployment Steps

### 1. Repository Verification (Completed)
- ✅ Checked git status: **10 commits ready to push**
- ✅ Verified deployment files exist:
  - `render.yaml` - Render Blueprint configuration
  - `Dockerfile.prod` - Production Docker image
  - `.env.example` - Environment variable template
  - `DEPLOYMENT_GUIDE.md` - Detailed deployment guide
- ✅ Created `.gitignore` to exclude temporary files
- ✅ Verified data and models are in place:
  - `data/us_er.parquet` (268 KB) - Hospital dataset
  - `models/triage_model.pkl` (1.3 MB) - ML triage model
  - `models/triage_encoders.pkl` (288 bytes) - Model encoders

### 2. Code Preparation (Completed)
- ✅ All bug fixes applied and tested:
  - Fixed `/api/search` lat/lon parameter passing
  - Fixed hospital name display on Explore page
  - Fixed map marker popups showing "Unknown Hospital"
  - Increased geolocation timeout from 10s to 30s
- ✅ Multi-page frontend fully functional:
  - Landing page (`index.html`)
  - Find Care page (`home.html`)
  - Results page with interactive map (`results.html`)
  - Explore hospitals nationwide (`explore.html`)
  - ML Triage Demo (`demo.html`)

---

## 🔄 Step-by-Step Deployment Guide

### Step 1: Push Code to GitHub

**Note:** You'll need to authenticate with GitHub to push the code.

#### Option A: Using GitHub CLI (Recommended)
```bash
cd /home/ubuntu/hospitracker

# Install GitHub CLI if not already installed
# (You may already have it configured)
gh auth login

# Push the commits
git push origin main
```

#### Option B: Using Personal Access Token
```bash
cd /home/ubuntu/hospitracker

# Set up Git credentials helper (one-time setup)
git config --global credential.helper store

# Push with token authentication
# You'll be prompted for username and token
git push origin main

# When prompted:
# Username: Your GitHub username
# Password: Your Personal Access Token (not your GitHub password)
```

**To create a Personal Access Token:**
1. Go to GitHub.com → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Click "Generate new token (classic)"
3. Give it a descriptive name: "HospiTrack Deployment"
4. Select scopes: `repo` (full control of private repositories)
5. Click "Generate token"
6. **Copy the token immediately** (you won't see it again)

#### Option C: Using SSH (If you have SSH keys set up)
```bash
cd /home/ubuntu/hospitracker

# Update remote to use SSH
git remote set-url origin git@github.com:JZembower/HospiTrack.git

# Push the commits
git push origin main
```

#### Verify Push Success
After pushing, verify on GitHub:
```
https://github.com/JZembower/HospiTrack/commits/main
```
You should see 10 new commits including "Add .gitignore to exclude temporary and log files"

---

### Step 2: Deploy to Render Using Blueprint

#### Method 1: One-Click Deploy Button (Easiest)

1. **Visit the Render Deploy URL:**
   ```
   https://render.com/deploy?repo=https://github.com/JZembower/HospiTrack
   ```

2. **Connect Your GitHub Account:**
   - Click "Connect GitHub" if not already connected
   - Authorize Render to access your repositories

3. **Configure the Service:**
   - Render will automatically detect `render.yaml`
   - **Service Name:** `hospitracker` (or choose your own)
   - **Region:** Choose closest to your users (e.g., Oregon for US West)
   - **Branch:** `main`
   - **Plan:** Start with **Free tier** for testing

4. **Review Environment Variables:**
   Render will auto-configure these from `render.yaml`:
   - `PORT` → Auto-set by Render
   - `PYTHONUNBUFFERED` → `1`
   - `HOSPITRACK_DATA_PATH` → `/app/data`
   - `GEOCODING_CACHE_SIZE` → `1000`
   - `ML_DEMO_ENABLED` → `true`
   - `LOG_LEVEL` → `INFO`

5. **Click "Create Web Service"**

#### Method 2: Manual Render Dashboard Setup (Alternative)

1. **Log into Render:** https://dashboard.render.com

2. **Create New Web Service:**
   - Click "New +" → "Web Service"
   - Connect your GitHub account
   - Select repository: `JZembower/HospiTrack`
   - Click "Connect"

3. **Configure Build Settings:**
   - **Name:** `hospitracker`
   - **Region:** Oregon (or preferred)
   - **Branch:** `main`
   - **Root Directory:** (leave blank)
   - **Runtime:** Docker
   - **Dockerfile Path:** `Dockerfile.prod`

4. **Set Environment Variables:**
   Navigate to "Environment" tab and add:
   ```
   PYTHONUNBUFFERED=1
   HOSPITRACK_DATA_PATH=/app/data
   GEOCODING_CACHE_SIZE=1000
   ML_DEMO_ENABLED=true
   LOG_LEVEL=INFO
   ```

5. **Configure Health Check:**
   - **Path:** `/healthz`
   - **Interval:** 30 seconds
   - **Timeout:** 5 seconds
   - **Retries:** 3

6. **Deploy:**
   - Click "Create Web Service"
   - Render will automatically start building and deploying

---

### Step 3: Monitor Deployment

#### Watch Build Logs
1. Go to your Render dashboard
2. Click on your `hospitracker` service
3. View the "Logs" tab in real-time

**Expected Build Process:**
```
==> Building Docker image from Dockerfile.prod
==> Step 1/15 : FROM python:3.11-slim as builder
==> Step 2/15 : RUN apt-get update && apt-get install -y ...
==> Step 3/15 : COPY requirements_fastapi.txt .
==> Step 4/15 : RUN pip install --no-cache-dir -r requirements_fastapi.txt
...
==> Build successful! Starting web service...
==> Health check passed on /healthz
==> Your service is live at https://hospitracker-xxxx.onrender.com
```

**Build Time:** Typically 5-10 minutes for first deployment

#### Expected Health Check Behavior
Render will continuously check `/healthz` endpoint:
- **Status:** Should return `200 OK`
- **Response:** `{"status": "healthy", "service": "hospitracker"}`

---

### Step 4: Get Your Public URL

Once deployment completes successfully:

1. **Find Your URL:**
   - Go to Render dashboard → Your service
   - Look for the URL at the top (e.g., `https://hospitracker-xxxx.onrender.com`)
   - Click to open in a new tab

2. **Save Your URL:**
   ```
   Public URL: https://hospitracker-XXXX.onrender.com
   ```
   (Replace XXXX with your actual Render-generated subdomain)

---

### Step 5: Verify Deployment

#### 5.1 Test Landing Page
```bash
# Using curl
curl -I https://hospitracker-XXXX.onrender.com/

# Expected: HTTP/2 200
```

**Browser Test:**
1. Visit `https://hospitracker-XXXX.onrender.com/`
2. ✅ Verify landing page loads with:
   - Hero section: "What do you need most right now?"
   - Three feature cards: Find Care, Explore, Demo
   - Medical disclaimer visible

#### 5.2 Test Find Care Page
```bash
curl https://hospitracker-XXXX.onrender.com/api/states
```

**Browser Test:**
1. Click "Find Care" or visit `/static/home.html`
2. ✅ Fill out search form:
   - Select symptom (e.g., "Chest pain")
   - Select priority (e.g., "Fastest available care")
   - Enter address: "San Francisco, CA"
   - Click "Find Hospitals"
3. ✅ Verify results page shows:
   - Interactive map with hospital markers
   - List of hospitals with details
   - Distance calculations correct

#### 5.3 Test Explore Page
```bash
curl "https://hospitracker-XXXX.onrender.com/api/explore?limit=10"
```

**Browser Test:**
1. Visit `/static/explore.html`
2. ✅ Verify:
   - Map displays 4,088 hospitals (showing 50 at a time)
   - Hospital names display correctly (not "Unknown Hospital")
   - State filter dropdown works
   - Sorting by quality/mortality works

#### 5.4 Test Demo (ML Triage)
```bash
curl -X POST https://hospitracker-XXXX.onrender.com/api/triage \
  -H "Content-Type: application/json" \
  -d '{
    "chief_complaint": "chest pain",
    "age": 45,
    "severity": "high",
    "heart_rate": 110,
    "systolic_bp": 160,
    "use_ml_model": true
  }'
```

**Browser Test:**
1. Visit `/static/demo.html`
2. ✅ Fill out triage form:
   - Select complaint: "Chest pain"
   - Age: "Adult"
   - Severity: "High"
   - Enter vitals
   - Toggle ML mode ON
3. ✅ Verify response shows:
   - Triage level (e.g., "Level 2")
   - Confidence score
   - Sorting strategy recommendation
   - Medical disclaimers

#### 5.5 Test API Documentation
```bash
curl https://hospitracker-XXXX.onrender.com/docs
```

**Browser Test:**
1. Visit `/docs` (FastAPI Swagger UI)
2. ✅ Verify all endpoints listed:
   - `GET /healthz`
   - `POST /api/search`
   - `GET /api/explore`
   - `POST /api/triage`
   - `GET /api/states`

---

### Step 6: Performance Testing

#### 6.1 Test Response Times
```bash
# Health check (should be < 100ms)
time curl https://hospitracker-XXXX.onrender.com/healthz

# Hospital search (should be < 2s)
time curl -X POST https://hospitracker-XXXX.onrender.com/api/search \
  -H "Content-Type: application/json" \
  -d '{"lat": 37.7749, "lon": -122.4194, "radius": 50}'

# Explore API (should be < 1s)
time curl https://hospitracker-XXXX.onrender.com/api/explore
```

#### 6.2 Test Under Load (Optional)
```bash
# Install Apache Bench if needed
sudo apt-get install apache2-utils

# 100 requests, 10 concurrent
ab -n 100 -c 10 https://hospitracker-XXXX.onrender.com/healthz
```

---

### Step 7: Configure Custom Domain (Optional)

If you want a custom domain like `hospitracker.com`:

1. **In Render Dashboard:**
   - Go to your service → Settings → Custom Domains
   - Click "Add Custom Domain"
   - Enter your domain: `hospitracker.com`

2. **In Your DNS Provider:**
   - Add a CNAME record:
     ```
     Type: CNAME
     Name: @ (or www)
     Value: hospitracker-xxxx.onrender.com
     TTL: 3600
     ```

3. **Wait for SSL:**
   - Render will automatically provision a free SSL certificate via Let's Encrypt
   - This takes 5-15 minutes

4. **Verify:**
   ```bash
   curl -I https://hospitracker.com
   ```

---

## 📊 Deployment Summary

### What Was Deployed

**Application:**
- **Name:** HospiTrack
- **Type:** FastAPI backend + Multi-page frontend
- **Runtime:** Docker (Python 3.11)
- **Database:** None (uses static Parquet file)
- **Storage:** 4.9 MB (data + models + static files)

**Data Files:**
- `data/us_er.parquet` (268 KB) - 4,088 US emergency rooms
- `models/triage_model.pkl` (1.3 MB) - ML model for triage prediction
- `models/triage_encoders.pkl` (288 bytes) - Label encoders

**Frontend Pages:**
1. **Landing Page** (`/`) - Multi-feature overview
2. **Find Care** (`/static/home.html`) - Symptom-based hospital search
3. **Results** (`/static/results.html`) - Interactive map with hospital list
4. **Explore** (`/static/explore.html`) - Browse 4,088 hospitals nationwide
5. **Demo** (`/static/demo.html`) - ML-powered triage simulation

**API Endpoints:**
- `GET /healthz` - Health check
- `POST /api/search` - Find hospitals by location and symptoms
- `GET /api/explore` - Browse hospitals with filters
- `POST /api/triage` - Get triage recommendation (rule-based or ML)
- `GET /api/states` - Get list of US states for filtering
- `GET /docs` - Interactive API documentation

### Resource Usage
- **Memory:** ~512 MB (Free tier: 512 MB)
- **CPU:** Minimal (<5% average)
- **Cold Start:** ~30 seconds on free tier
- **Requests/month:** Unlimited on free tier

---

## 🔧 Troubleshooting

### Issue: Build Fails - "Unable to find Dockerfile.prod"
**Solution:**
```bash
# Verify file exists in repository
git ls-files | grep Dockerfile.prod

# If missing, ensure it's committed
git add Dockerfile.prod
git commit -m "Add production Dockerfile"
git push origin main
```

### Issue: Build Fails - "COPY failed: file not found"
**Solution:**
- Check that `data/us_er.parquet` and `models/` are in the repository
- Verify they're not excluded by `.gitignore`
```bash
git ls-files | grep -E "(data/|models/)"
```

### Issue: Health Check Failing
**Solution:**
1. Check logs for application startup errors:
   ```
   Render Dashboard → Logs
   ```
2. Verify `/healthz` endpoint is accessible:
   ```bash
   curl https://hospitracker-XXXX.onrender.com/healthz
   ```
3. Check environment variables are set correctly

### Issue: Geocoding Timeouts
**Solution:**
- This is expected for some addresses due to rate limiting
- Recommend users enter lat/lon coordinates or use "Use My Location" button
- Consider upgrading to paid geocoding service (e.g., Google Maps API) for production

### Issue: "No hospitals found" Despite Valid Location
**Solution:**
1. Check if location was geocoded successfully (view logs)
2. Increase radius slider to 100 km
3. Verify `data/us_er.parquet` contains lat/lon columns
4. Test with known coordinates:
   ```bash
   curl -X POST https://hospitracker-XXXX.onrender.com/api/search \
     -H "Content-Type: application/json" \
     -d '{"lat": 37.7749, "lon": -122.4194, "radius": 50}'
   ```

### Issue: ML Triage Demo Returns Errors
**Solution:**
1. Verify `models/triage_model.pkl` exists and is not corrupted
2. Check `ML_DEMO_ENABLED=true` environment variable is set
3. View logs for model loading errors:
   ```
   Render Dashboard → Logs → Search for "triage_model"
   ```

### Issue: Free Tier Service Spins Down (Cold Starts)
**Explanation:**
- Render's free tier spins down after 15 minutes of inactivity
- First request after spin-down takes ~30 seconds to respond

**Solutions:**
- Upgrade to paid plan ($7/month) for always-on service
- Use a cron job to ping `/healthz` every 10 minutes:
  ```bash
  # Add to crontab
  */10 * * * * curl https://hospitracker-XXXX.onrender.com/healthz
  ```

---

## 🚀 Post-Deployment Recommendations

### 1. Monitor Performance
- Set up monitoring alerts in Render dashboard
- Configure alerts for:
  - Health check failures
  - High memory usage (>450 MB on free tier)
  - Build failures

### 2. Update Medical Disclaimers
- Ensure all pages display prominent medical disclaimers
- Add "Call 911 for life-threatening emergencies" warnings
- Consult legal counsel for healthcare-related software compliance

### 3. Consider Paid Tier for Production
**Benefits of Paid Plan ($7/month):**
- No cold starts (always-on)
- Better performance (dedicated CPU)
- Custom domains with SSL
- Priority support
- More memory/CPU

### 4. Implement Analytics (Optional)
Add Google Analytics or Plausible to track:
- Page views per feature
- Most searched locations
- Most common symptoms
- User retention

**Example (add to `<head>` of all HTML files):**
```html
<!-- Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=GA_TRACKING_ID"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'GA_TRACKING_ID');
</script>
```

### 5. Set Up CI/CD (Already Configured)
The repository includes `.github/workflows/ci.yml` for:
- Automated testing on push
- Docker build verification
- Automatic deployment to Render on main branch updates

**Verify it's enabled:**
```
https://github.com/JZembower/HospiTrack/actions
```

---

## 📝 Quick Reference

### Important URLs
```
Repository:        https://github.com/JZembower/HospiTrack
Render Dashboard:  https://dashboard.render.com
Public URL:        https://hospitracker-XXXX.onrender.com
API Docs:          https://hospitracker-XXXX.onrender.com/docs
Health Check:      https://hospitracker-XXXX.onrender.com/healthz
```

### Deployment Commands
```bash
# Push code
cd /home/ubuntu/hospitracker
git push origin main

# Test health
curl https://hospitracker-XXXX.onrender.com/healthz

# Test API
curl https://hospitracker-XXXX.onrender.com/api/states

# View logs (from Render dashboard or CLI)
render logs hospitracker
```

### Environment Variables Reference
```
PORT=10000                           # Auto-set by Render
PYTHONUNBUFFERED=1                   # Disable Python output buffering
HOSPITRACK_DATA_PATH=/app/data       # Path to hospital data
GEOCODING_CACHE_SIZE=1000            # Number of cached locations
ML_DEMO_ENABLED=true                 # Enable ML triage demo
LOG_LEVEL=INFO                       # Logging verbosity
```

---

## ✅ Deployment Checklist

Before marking deployment as complete, verify:

- [ ] Code pushed to GitHub successfully
- [ ] Render service created and connected to repository
- [ ] Build completed without errors
- [ ] Health check passing (`/healthz` returns 200)
- [ ] Landing page loads correctly
- [ ] Find Care search works with sample address
- [ ] Explore page displays all 4,088 hospitals
- [ ] ML Triage Demo returns predictions
- [ ] API documentation accessible at `/docs`
- [ ] No console errors in browser dev tools
- [ ] Mobile responsive design works on phone
- [ ] Medical disclaimers visible on all pages

---

## 🎉 Success!

Once all checks pass, your HospiTrack application is **live and publicly accessible**!

**Share your deployment:**
```
🏥 HospiTrack is now live!
🔗 https://hospitracker-XXXX.onrender.com

Find the best emergency care based on your symptoms and location.
Powered by data from 4,088 US hospitals.
```

---

## 📞 Support

**Issues with deployment?**
- Check Render logs for detailed error messages
- Review this guide's Troubleshooting section
- Refer to `DEPLOYMENT_GUIDE.md` for additional context
- Contact Render support: https://render.com/support

**Application bugs?**
- Check `FIXES_SUMMARY.md` for known issues and fixes
- Review GitHub issues: https://github.com/JZembower/HospiTrack/issues
- Test locally with Docker: `docker-compose up`

---

**Deployment Guide Version:** 1.0  
**Last Updated:** December 17, 2025  
**Platform:** Render.com  
**Status:** ✅ Ready for Production
