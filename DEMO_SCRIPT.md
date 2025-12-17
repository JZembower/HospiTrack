# HospiTrack Product Demo Script

A comprehensive walkthrough for demonstrating HospiTrack to stakeholders, investors, or potential users.

**Duration**: 5-10 minutes  
**Audience**: Non-technical and technical stakeholders  
**Goal**: Showcase key features, privacy focus, and production readiness

---

## Pre-Demo Checklist

- [ ] Application is deployed and accessible
- [ ] Test search with "San Francisco, CA" works
- [ ] Map is rendering correctly
- [ ] ML demo toggle is functional
- [ ] API documentation loads at `/docs`
- [ ] Browser developer tools closed (for cleaner presentation)
- [ ] Prepare backup demo location if San Francisco data is sparse

---

## Introduction (30 seconds)

### Opening Statement

> "Today I'll show you **HospiTrack**, a privacy-focused hospital recommendation platform that helps people find the right emergency care based on their specific medical needs. Unlike generic hospital finders, HospiTrack uses symptom-specific quality metrics and transparent AI to provide personalized recommendations."

### Key Differentiators
- ✅ **Privacy-first**: No PII storage, no tracking
- ✅ **Symptom-aware**: Rankings adjust based on medical complaint
- ✅ **Transparent AI**: Clear explanations for every recommendation
- ✅ **Production-ready**: Deployed, tested, and scalable

---

## Demo Flow

### 1. Landing Page Walkthrough (1 minute)

**Navigate to**: `https://your-app-url.com/`

#### What to Show
- **Hero Section**: "Find the Right Emergency Care, Fast"
- **Three Feature Cards**:
  1. **Find Care** → Emergency search with symptom matching
  2. **Explore Hospitals** → Nationwide hospital browser
  3. **Company Demo** → B2B triage API showcase
- **How It Works**: 4-step process explanation
- **Medical Disclaimer**: Emphasis on "call 911 for emergencies"

#### Talking Points
> "The landing page clearly guides users to three core features. Notice the prominent medical disclaimer—we're very clear this is a research tool, not a replacement for emergency services."

---

### 2. Emergency Care Search Demo (3 minutes)

**Navigate to**: Click **"Find Emergency Care Now"** or go to `/static/home.html`

#### Step 2.1: Select Symptom and Priority

1. **Choose Symptom**: Select **"Chest Pain"** (most impactful for demo)
2. **Choose Priority**: Select **"Fastest Care"**
3. **Explain**:
   > "Users can choose what matters most to them. 'Fastest Care' prioritizes low wait times, while 'Highest Quality' focuses on clinical outcomes. For chest pain, speed is critical."

#### Step 2.2: Enter Location

**Option A**: Use address input
- **Enter**: `San Francisco, CA` or `Los Angeles, CA`
- **Set Radius**: Adjust slider to **25 km**

**Option B**: Demonstrate browser geolocation
- Click **"Use My Location"** button
- Allow browser location permission
- Show that lat/lon auto-populates

**Talking Point**:
> "HospiTrack supports address search, ZIP codes, and browser geolocation. All geocoding is privacy-preserving—we don't store any location data."

#### Step 2.3: Execute Search

- Click **"Find Hospitals"**
- **Note the loading state** (shows good UX design)

---

### 3. Results Page Deep Dive (3 minutes)

**Page loads**: `/static/results.html` with map and hospital list

#### Step 3.1: Show Ranking Explanation

**Point to the explanation box at the top**:
> "Notice HospiTrack doesn't just show results—it explains WHY these hospitals are ranked this way. For chest pain with 'Fastest Care' priority, we're prioritizing hospitals with low wait times and high heart attack care quality."

**Key Elements**:
- **Primary sorting criteria**: ED wait time (fastest care)
- **Adjusted quality metric**: Heart attack care performance
- **Transparency**: Clear, non-technical language

#### Step 3.2: Interactive Map Features

1. **Show color coding**:
   - Green markers = Top-ranked hospitals
   - Orange markers = Mid-range
   - Red markers = Lower-ranked (if visible)
   
2. **Click on a map marker**:
   - Popup shows: Name, address, distance, quality score
   - **Highlight**: "Popups provide at-a-glance decision-making info"

3. **Show map clustering** (if >10 hospitals):
   - Zoom out to show clusters
   - Zoom in to show individual markers
   - **Explain**: "For dense urban areas, we cluster markers to avoid clutter"

#### Step 3.3: Hospital List Features

**Scroll through the hospital list**:

1. **Show detailed cards**:
   - Hospital name, address, phone
   - Distance, quality rating, mortality comparison
   - CMS ratings (if available)
   
2. **Demonstrate list ↔ map sync**:
   - Click a hospital card
   - Show how the map marker highlights and centers
   - **Explain**: "Clicking a hospital in the list highlights it on the map—seamless navigation"

#### Step 3.4: Adjust Filters

**Show dynamic refinement**:

1. **Change priority** to **"Highest Quality"**
   - Click "Apply Filters"
   - **Observe**: Hospital rankings re-sort immediately
   - **Explain**: "Users can refine results without losing their search context"

2. **Adjust radius slider** to **50 km**
   - More hospitals appear
   - Map zooms out to fit

3. **Optional: Filter by state** (if applicable)

**Talking Point**:
> "This flexibility is key—users might start wanting the fastest care, then realize they're willing to drive farther for better quality. HospiTrack adapts in real-time."

---

### 4. Explore Page Demo (1.5 minutes)

**Navigate to**: `/static/explore.html` or click **"Explore Hospitals"** in nav

#### Step 4.1: Search by State

1. **Select State**: Choose **"California"** from dropdown
2. **Click "Search"**
3. **Show results**: Paginated list of all CA hospitals with map

**Talking Point**:
> "The Explore feature lets users browse hospitals nationwide without needing an emergency. Great for research, travel planning, or comparing facilities."

#### Step 4.2: Demonstrate Sorting Options

1. **Sort by**: Change to **"ED Wait Time (Shortest)"**
2. **Show results update**: Fastest ERs appear first
3. **Explain**:
   > "Users can sort by quality, wait time, patient rating, or mortality—whatever metric matters most to them."

#### Step 4.3: Optional Location-Based Search

- Enter a city name (e.g., "Los Angeles")
- Set radius to 50 km
- Show hospitals within that area on map

---

### 5. Company Demo Page (2 minutes)

**Navigate to**: `/static/demo.html` or click **"Company Demo"**

> "This page is designed for healthcare companies interested in integrating our triage API into their systems. Let me show you both the rule-based and ML-powered approaches."

#### Step 5.1: Fill Intake Form (Rule-Based)

**Input the following**:
- **Complaint**: `Chest pain`
- **Severity**: `4` (out of 5)
- **Age Band**: `Adult`
- **Heart Rate**: `110` bpm
- **Respiratory Rate**: `20` (normal)
- **Blood Pressure**: `140/90`
- **Mode**: Ensure **"Rule-Based"** is selected

**Click "Get Triage Recommendation"**

#### Step 5.2: Explain Rule-Based Output

**Results shown**:
- **Triage Level**: Likely "Urgent" or "Critical"
- **Recommended Priority**: "Fastest Care"
- **Adjusted Quality Metric**: `adj_total_heartattack`
- **Explanation**: Clear rationale based on severity + vitals

**Talking Point**:
> "Our rule-based system uses medical guidelines to map symptoms and vitals to triage priorities. It's deterministic, explainable, and doesn't require ML infrastructure—perfect for compliance-heavy environments."

#### Step 5.3: Toggle to ML Demo

1. **Switch toggle** to **"ML Demo"**
2. **Keep the same inputs**
3. **Click "Get Triage Recommendation"** again

**Results shown**:
- **Triage Level**: Predicted category (e.g., "Emergency")
- **Confidence**: Percentage (e.g., 87%)
- **Feature Importance**: Top factors driving the prediction
- **Warning**: "Trained on synthetic data—for demo purposes only"

**Talking Point**:
> "The ML model provides probabilistic predictions with confidence scores. We clearly label this as a demo trained on synthetic data—in production, this would be trained on real EHR data with proper validation. Notice we provide feature importance for explainability."

#### Step 5.4: Show API Documentation

**Scroll down to "API Integration" section**:

1. **Show curl example**:
   ```bash
   curl -X POST https://your-app.com/api/triage \
     -H "Content-Type: application/json" \
     -d '{"complaint": "chest pain", "severity": 4, ...}'
   ```

2. **Explain**:
   > "Healthcare companies can integrate this via REST API. We provide clear documentation, sample requests, and response formats. The `/docs` endpoint has full OpenAPI specs for automated client generation."

3. **Open API Docs** (new tab): `https://your-app-url.com/docs`
   - Show interactive Swagger UI
   - Expand `/api/triage` endpoint
   - **Optional**: Execute a test request in the browser

**Talking Point**:
> "FastAPI auto-generates this interactive documentation. Developers can test the API right in the browser before integrating."

---

## Key Talking Points Throughout Demo

### Privacy & Security
- ✅ **No PII storage**: We never save user addresses, searches, or medical info
- ✅ **Geocoding privacy**: Addresses are hashed for caching, not logged
- ✅ **HTTPS enforced**: All data in transit is encrypted
- ✅ **Transparent disclaimers**: Clear medical warnings throughout

### Technical Excellence
- ✅ **Production-ready**: Deployed on Render/cloud with health checks
- ✅ **Fast & efficient**: Parquet-optimized dataset, LRU caching
- ✅ **Scalable**: Docker-based, horizontal scaling supported
- ✅ **Well-tested**: 43 passing tests covering core logic

### User Experience
- ✅ **Mobile-responsive**: Works on phones, tablets, desktops
- ✅ **Accessible**: Semantic HTML, keyboard navigation
- ✅ **Intuitive**: Clear UI, no medical jargon in UX
- ✅ **Fast**: Sub-second search results for most queries

### Business Value
- ✅ **B2C**: Direct-to-consumer hospital finder
- ✅ **B2B**: API for healthcare companies, telemedicine platforms
- ✅ **Differentiation**: Symptom-specific rankings (not just distance)
- ✅ **Compliance-ready**: Clear disclaimers, no diagnostic claims

---

## Handling Q&A

### Common Questions & Answers

**Q: Where does the hospital data come from?**  
**A**: "CMS Hospital Compare dataset—publicly available data from the Centers for Medicare & Medicaid Services. We process and optimize it for fast queries."

**Q: How accurate is the ML triage model?**  
**A**: "The current model is trained on synthetic data for demonstration. In production, it would be trained on real EHR data with clinical validation and regulatory approval. We clearly label this as a demo."

**Q: Does this replace calling 911?**  
**A**: "Absolutely not. We have prominent disclaimers throughout the app—for life-threatening emergencies, always call 911. HospiTrack is for informed decision-making when you have time to choose."

**Q: How do you handle geocoding rate limits?**  
**A**: "We implement LRU caching (stores 1,000 recent lookups) and rate limiting. For high traffic, we'd switch to a commercial geocoding API with higher quotas."

**Q: Can this be white-labeled for healthcare systems?**  
**A**: "Yes! The codebase is modular. We can customize the UI, add hospital system branding, and integrate with existing EHR/referral systems via our API."

**Q: What's the deployment cost?**  
**A**: "Current deployment on Render costs ~$7/month for starter plan. For production scale, we'd recommend ~$20-50/month depending on traffic. Fully scalable."

**Q: Is the code open source?**  
**A**: "The repository is available for review. Licensing can be discussed based on use case—we're flexible for healthcare/nonprofit use."

---

## Closing (30 seconds)

### Summary Statement

> "To recap, HospiTrack combines public health data, privacy-preserving design, and transparent AI to help people make informed emergency care decisions. It's production-ready, scalable, and can serve both consumers directly and healthcare companies via API."

### Call to Action

- **For Investors**: "We're ready to scale—looking for funding to expand data coverage and add real-time ER wait times."
- **For Healthcare Orgs**: "Let's discuss a pilot integration. We can have a demo API running for your system within a week."
- **For Technical Audience**: "Full documentation, API specs, and deployment guides are available. Happy to do a deeper technical dive."

### Leave-Behinds

- 🔗 **Live demo URL**: `https://your-app-url.com`
- 📄 **API docs**: `https://your-app-url.com/docs`
- 📧 **Contact**: your-email@example.com
- 📦 **GitHub** (if public): `https://github.com/your-username/hospitracker`

---

## Demo Environment Setup

### Before Presenting

1. **Test the demo flow** with the exact steps above
2. **Clear browser cache/cookies** to show first-time user experience
3. **Prepare backup locations** in case primary location has sparse data:
   - San Francisco, CA (usually has good data)
   - Los Angeles, CA (backup)
   - New York, NY (backup)
4. **Have API docs pre-loaded** in a background tab
5. **Close unnecessary tabs/apps** for clean screen sharing

### Technical Backup Plan

- **If API is slow**: Mention caching: "First queries are slower due to geocoding; subsequent ones are instant"
- **If map doesn't load**: Have screenshots ready as backup
- **If ML demo fails**: Focus on rule-based triage (more reliable)
- **If entire app is down**: Have a recorded video demo as ultimate fallback

---

## Customization Tips

### For Different Audiences

**For Non-Technical Stakeholders**:
- Skip technical details (Docker, API specs)
- Focus on UX, privacy, and business value
- Use analogies: "Like Google Maps for emergency care"

**For Technical Audience**:
- Dive into API docs and architecture
- Show `main.py` code (backend)
- Discuss scaling strategy, caching, and performance
- Mention CI/CD, testing, and monitoring

**For Healthcare Professionals**:
- Emphasize data sources (CMS Hospital Compare)
- Discuss triage rule logic (clinical guidelines)
- Address compliance and disclaimer approach
- Highlight "no diagnostic claims" positioning

**For Investors**:
- Focus on market opportunity and differentiation
- Discuss monetization: B2B API licensing, white-label, ads
- Highlight scalability and low operational costs
- Mention expansion: international markets, real-time data

---

**Demo Script Version**: 1.0  
**Last Updated**: December 2024  
**Recommended Presenter Prep Time**: 15 minutes
