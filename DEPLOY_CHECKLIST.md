# HospiTrack Deployment Checklist

**Quick reference for deploying to Render**

---

## ☑️ Pre-Deployment (Already Done)

- [x] All bug fixes completed
- [x] Code tested locally
- [x] Data files ready (us_er.parquet, triage_model.pkl)
- [x] Deployment files created (render.yaml, Dockerfile.prod)
- [x] .gitignore configured
- [x] 10 commits ready to push

---

## ☐ Step 1: Push to GitHub (YOU DO THIS)

```bash
cd /home/ubuntu/hospitracker
git push origin main
```

**Authentication Options:**
- [ ] GitHub CLI: `gh auth login`
- [ ] Personal Access Token: https://github.com/settings/tokens
- [ ] SSH key: `git remote set-url origin git@github.com:JZembower/HospiTrack.git`

**Verify:** https://github.com/JZembower/HospiTrack/commits/main

---

## ☐ Step 2: Deploy on Render (YOU DO THIS)

### One-Click Deploy:
1. [ ] Visit: https://render.com/deploy?repo=https://github.com/JZembower/HospiTrack
2. [ ] Connect GitHub account
3. [ ] Service name: `hospitracker`
4. [ ] Click "Create Web Service"
5. [ ] Wait 8-10 minutes

### Your Public URL:
```
https://hospitracker-XXXX.onrender.com
```
**Write it here:** _________________________________

---

## ☐ Step 3: Verify Deployment (TEST THESE)

### 3.1 Health Check
```bash
curl https://hospitracker-XXXX.onrender.com/healthz
```
**Expected:** `{"status": "healthy"}`
- [ ] ✅ Passed

### 3.2 Landing Page
**URL:** https://hospitracker-XXXX.onrender.com/
- [ ] Hero section loads
- [ ] 3 feature cards visible
- [ ] Medical disclaimer shown
- [ ] No console errors

### 3.3 Find Care Page
**URL:** https://hospitracker-XXXX.onrender.com/static/home.html
- [ ] Form loads correctly
- [ ] Symptom dropdown works
- [ ] Location input accepts text
- [ ] Search returns results

**Test Case:**
```
Symptom: Chest pain
Location: San Francisco, CA
Radius: 50 km
```
- [ ] Returns hospitals list
- [ ] Map shows markers
- [ ] Distance calculated correctly

### 3.4 Explore Page
**URL:** https://hospitracker-XXXX.onrender.com/static/explore.html
- [ ] Map loads with hospitals
- [ ] Shows "Found 4088 hospitals"
- [ ] Hospital names NOT "Unknown Hospital"
- [ ] State filter works
- [ ] Sorting works

### 3.5 Demo Page (ML Triage)
**URL:** https://hospitracker-XXXX.onrender.com/static/demo.html
- [ ] Form submits successfully
- [ ] Returns triage level
- [ ] Shows confidence score
- [ ] Recommendation displayed
- [ ] Medical disclaimer visible

**Test Case:**
```
Complaint: Chest pain
Age: 45
Severity: High
Heart Rate: 110
BP: 160/100
ML Mode: ON
```
- [ ] Returns Level 2 or similar
- [ ] Confidence > 70%

### 3.6 API Documentation
**URL:** https://hospitracker-XXXX.onrender.com/docs
- [ ] Swagger UI loads
- [ ] All 5+ endpoints listed
- [ ] Can test endpoints interactively

---

## ☐ Step 4: Performance Check

### 4.1 Response Times
```bash
time curl https://hospitracker-XXXX.onrender.com/healthz
time curl https://hospitracker-XXXX.onrender.com/api/states
```
- [ ] Health check < 200ms
- [ ] API calls < 2s

### 4.2 Mobile Responsiveness
- [ ] Open on mobile browser
- [ ] Layout adjusts correctly
- [ ] Map is interactive
- [ ] Forms are usable

---

## ☐ Step 5: Monitor & Document

### 5.1 Check Render Dashboard
- [ ] View logs for errors
- [ ] Confirm health checks passing
- [ ] Check memory usage (<512 MB for free tier)

### 5.2 Document Your URL
**Add to README.md:**
```markdown
## Live Demo
🌐 **Public URL:** https://hospitracker-XXXX.onrender.com

### Features
- Find emergency care by symptoms
- Browse 4,088 US hospitals
- ML-powered triage demo
```

### 5.3 Share with Stakeholders
```
Subject: HospiTrack is Live! 🏥

The HospiTrack application is now publicly accessible:
https://hospitracker-XXXX.onrender.com

Key features:
✅ Find Care - Search hospitals by symptoms and location
✅ Explore - Browse 4,088 US emergency rooms nationwide
✅ Demo - ML-powered triage recommendations

Technical details:
- Platform: Render.com
- Backend: FastAPI + Python 3.11
- Frontend: Multi-page responsive design
- Data: 4,088 hospitals with quality scores
- API: RESTful with Swagger docs at /docs

Please test and provide feedback!
```

---

## 🚨 Troubleshooting

### Build Failed
- [ ] Check Render logs for specific error
- [ ] Verify Dockerfile.prod is in repo
- [ ] Ensure data/ and models/ are committed

### Health Check Failed
- [ ] Wait 2-3 minutes for startup
- [ ] Check logs for Python errors
- [ ] Verify PORT env variable is set

### No Hospitals Found
- [ ] Increase radius to 100 km
- [ ] Try coordinates: lat=37.7749, lon=-122.4194
- [ ] Check console for errors

### Geocoding Timeout
- [ ] Expected for some addresses
- [ ] Recommend users click "Use My Location"
- [ ] Or enter lat/lon coordinates

### ML Demo Error
- [ ] Verify ML_DEMO_ENABLED=true
- [ ] Check models/triage_model.pkl exists
- [ ] View logs for model loading errors

---

## 📞 Support Resources

- **Detailed Guide:** `ACTUAL_DEPLOYMENT_STEPS.md`
- **Quick Start:** `QUICK_START.md`
- **Architecture:** `DEPLOYMENT_FLOW.md`
- **Render Docs:** https://render.com/docs
- **GitHub Repo:** https://github.com/JZembower/HospiTrack

---

## ✅ Deployment Complete!

When all checks pass:
- [ ] Mark deployment as successful
- [ ] Share URL with team
- [ ] Monitor for 24 hours
- [ ] Plan for upgrades if needed

**Congratulations! HospiTrack is now live! 🎉**

---

**Deployment Date:** _____________  
**Deployed By:** _____________  
**Public URL:** _____________  
**Status:** 🟢 Live | 🟡 Testing | 🔴 Issues
