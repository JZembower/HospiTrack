# HospiTrack Deployment Guide

## ✅ Pre-Deployment Checklist

All fixes have been implemented and committed:
- ✅ Map marker popups now show correct hospital names
- ✅ Location timeout increased to 30 seconds with better error handling
- ✅ All files committed to git
- ✅ Data files present (us_er.parquet)
- ✅ ML models present (triage_model.pkl, triage_encoders.pkl)
- ✅ Dockerfile.prod configured
- ✅ render.yaml blueprint ready

## 🚀 Deploy to Render (Recommended)

### Step 1: Push to GitHub

```bash
cd /home/ubuntu/hospitracker
git push origin main
```

**Note:** If you get a permission error, you may need to:
1. Set up GitHub authentication (personal access token or SSH key)
2. Or manually push from your local machine

### Step 2: Create Render Account

1. Go to [https://render.com](https://render.com)
2. Sign up with your GitHub account
3. Authorize Render to access your repositories

### Step 3: Deploy from Blueprint

**Option A: One-Click Deploy (Easiest)**

1. Click this button in your GitHub repository:
   [![Deploy to Render](https://i.ytimg.com/vi/yWxBUcG_C7g/mqdefault.jpg)

**Option B: Manual Deploy**

1. Log in to [Render Dashboard](https://dashboard.render.com)
2. Click **"New +"** → **"Blueprint"**
3. Connect your GitHub repository: `JZembower/HospiTrack`
4. Render will automatically detect `render.yaml`
5. Review the configuration:
   - **Service Name:** hospitracker
   - **Region:** Oregon (or choose closest to your users)
   - **Plan:** Starter (free) or Standard ($7/month)
6. Click **"Apply"** to start deployment

### Step 4: Wait for Build

- First build takes 5-10 minutes
- Render will:
  - Clone your repository
  - Build Docker image from `Dockerfile.prod`
  - Start the application
  - Run health checks

### Step 5: Access Your Application

Once deployed, Render provides a public URL:
```
https://hospitracker-XXXX.onrender.com
```

Test the following pages:
- **Landing Page:** `/static/index.html`
- **Find Care:** `/static/home.html`
- **Explore:** `/static/explore.html`
- **Demo:** `/static/demo.html`
- **API Docs:** `/docs`

### Step 6: Verify Fixes

1. **Test Map Marker Popup:**
   - Go to Explore page
   - Click on any map marker
   - Verify popup shows actual hospital name (not "Unknown Hospital")

2. **Test Location Button:**
   - Go to Find Care page
   - Click "Use My Current Location"
   - Verify improved error message if location fails
   - Or verify coordinates populate if location succeeds

## 🔧 Custom Domain (Optional)

To use a custom domain like `hospitracker.com`:

1. Go to Render Dashboard → Your Service → **Settings**
2. Scroll to **Custom Domain**
3. Click **"Add Custom Domain"**
4. Enter your domain name
5. Add DNS records provided by Render to your domain registrar:
   ```
   CNAME www hospitracker-XXXX.onrender.com
   ```

## 📊 Monitor Your Deployment

### View Logs

```bash
# In Render Dashboard
Services → hospitracker → Logs
```

### Health Check

```bash
curl https://hospitracker-XXXX.onrender.com/healthz
```

Expected response:
```json
{"status": "ready"}
```

### Check API

```bash
curl https://hospitracker-XXXX.onrender.com/api/search \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "complaint": "heart_attack",
    "priority": "time",
    "location": "San Francisco, CA",
    "radius_km": 25
  }'
```

## 🔄 Auto-Deploy Updates

Render is configured for auto-deploy on `main` branch:

1. Make changes locally
2. Commit and push to GitHub:
   ```bash
   git add .
   git commit -m "Your update message"
   git push origin main
   ```
3. Render automatically rebuilds and deploys

## 💰 Pricing

**Starter Plan (Free):**
- Good for development and testing
- Sleeps after 15 minutes of inactivity
- 750 hours/month free

**Standard Plan ($7/month):**
- Always on
- No sleep
- Better for production use

## 🆘 Troubleshooting

### Build Fails

Check build logs in Render dashboard for errors. Common issues:
- Missing dependencies in `requirements_fastapi.txt`
- Docker build errors
- Data files not found

### Application Crashes

Check runtime logs:
```bash
# In Render Dashboard
Services → hospitracker → Logs → Filter: "ERROR"
```

### Health Check Fails

Verify the `/healthz` endpoint is responding:
```bash
curl https://hospitracker-XXXX.onrender.com/healthz
```

## 📝 Environment Variables

Current configuration in `render.yaml`:

| Variable | Value | Description |
|----------|-------|-------------|
| PORT | 8000 | Server port |
| PYTHONUNBUFFERED | 1 | Python logging |
| HOSPITRACK_DATA_PATH | /app/data | Data directory |
| GEOCODING_CACHE_SIZE | 1000 | Geocoding cache size |
| ML_DEMO_ENABLED | true | Enable ML demo |
| LOG_LEVEL | INFO | Logging level |

To modify:
1. Render Dashboard → Your Service → **Environment**
2. Add/edit variables
3. Click **"Save Changes"** (triggers redeploy)

## 🎉 Success!

Your HospiTrack application is now:
- ✅ Deployed to Render
- ✅ Publicly accessible
- ✅ Auto-deploying on updates
- ✅ Map markers show correct hospital names
- ✅ Location timeout properly handled

**Share Your Deployment:**
```
🏥 HospiTrack - Find Emergency Care Fast
https://hospitracker-XXXX.onrender.com
```

## 📚 Additional Resources

- [Render Documentation](https://render.com/docs)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [HospiTrack GitHub](https://github.com/JZembower/HospiTrack)

---

**Need Help?** 
- Check Render Dashboard logs
- Review application logs
- Consult DEPLOYMENT.md for alternative deployment options
