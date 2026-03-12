# 📱 Device Tier Breakdown Guide

## Current Signup Funnel Data

| Metric | Value |
|--------|-------|
| **SIGNIN_PAGE_VIEW** | 683 unique users |
| **SIGNIN_PAGE_NUMBER_ENTERED** | 228 unique users |
| **Overall Conversion** | 33.4% |
| **Baseline** | 52% |
| **Gap** | -18.6% ⚠️ |

---

## Get Device Tier Breakdown - 3 Methods

### ✅ METHOD 1: Amplitude Dashboard (RECOMMENDED - 5 minutes)

**Steps:**

1. Go to: **https://amplitude.com/dashboard**

2. Find **SIGNIN_PAGE_VIEW** event

3. Click **"Add Segment"** button (top right)
   - Select **"Device Model"** from dropdown

4. You'll see breakdown like:
   ```
   Samsung Galaxy A12     ← 45 views
   Samsung Galaxy S21     ← 32 views
   iPhone 13              ← 28 views
   Redmi Note 10          ← 18 views
   OnePlus 9              ← 15 views
   ...
   ```

5. **Categorize into tiers:**

   | Category | Devices |
   |----------|---------|
   | **Low-tier Android** | Redmi, Realme C, Moto E, Samsung J2-J7, Infinix, Tecno, Nokia 1-2 |
   | **Mid-tier Android** | Samsung A, Samsung M, Poco, Redmi Note, Oneplus Nord, Moto G, Vivo V, Oppo F/A |
   | **Premium Android** | Samsung S22+, S23+, S24+, OnePlus 9+, Google Pixel, Poco F-series |
   | **iOS** | iPhone 12+, iPhone SE, iPad |
   | **Web** | Desktop/Web browsers |

6. **Get the numbers:**
   - Note device counts for each tier
   - Export as screenshot or CSV

---

### ✅ METHOD 2: Export & Analyze (10 minutes)

**Steps:**

1. Go to SIGNIN_PAGE_VIEW event
2. Click **"Export"** → Download CSV
3. Open in Excel/Google Sheets
4. Create pivot table with **Device Model**
5. Count unique users per device
6. Add categorization column:
   ```excel
   =IF(ISNUMBER(SEARCH("Samsung S",A2)),"Premium",
        IF(ISNUMBER(SEARCH("Redmi",A2)),"Low-tier",
           "Mid-tier"))
   ```
7. Calculate conversions per category

---

### ✅ METHOD 3: Deploy Enhanced Agent (Automated)

**What it does:**

✅ Fetches SIGNIN_PAGE_VIEW events from Amplitude
✅ Fetches SIGNIN_PAGE_NUMBER_ENTERED events
✅ Extracts device_model from each event
✅ Automatically categorizes into tiers
✅ Calculates conversion rates per tier
✅ Sends detailed report to Slack every 48 hours
✅ Alerts on underperforming device tiers

**To deploy:**

```bash
# 1. Go to the repo
cd /Users/arpit.goyal/aspero\ repos/yubi-b2c-mobile

# 2. Use the enhanced agent script
python3 ENHANCED_AMPLITUDE_AGENT.py

# 3. It will show you device breakdown automatically
```

---

## Expected Device Tier Breakdown

Based on typical India mobile market, you'll likely see:

| Tier | Est. % of Users | Est. Conversion |
|------|-----------------|-----------------|
| **Low-tier Android** | 35-40% | 25-35% ⚠️ |
| **Mid-tier Android** | 40-45% | 40-50% ⚠️ |
| **Premium Android** | 5-10% | 60-70% ✅ |
| **iOS** | 8-12% | 65-75% ✅ |
| **Web** | 3-5% | 45-55% ⚠️ |

**Key Insight:** Low-tier devices likely have lower conversion due to:
- Slower app load times
- Memory constraints
- Screen size issues
- Older OS versions

---

## What the Agent Will Show

Once deployed, you'll get Slack alerts like:

```
📊 SIGNUP FUNNEL BY DEVICE TIER

├─ ✅ Premium Android: 68% (baseline 52%)
├─ ✅ iOS: 72% (baseline 52%)
├─ ⚠️ Web: 42% (baseline 52%, -10% drop)
├─ ❌ Mid-tier Android: 38% (baseline 52%, -14% drop)
└─ ❌ Low-tier Android: 28% (baseline 52%, -24% drop)

🔴 PROBLEM AREA: Low-tier Android
   Likely causes:
   - App load time > 3 seconds
   - Memory constraints (RAM usage high)
   - Network timeout issues
   - Screen layout issues on small displays

✅ RECOMMENDATIONS:
   1. Optimize assets for low-end devices
   2. Reduce initial bundle size
   3. Implement progressive loading
   4. Test on Samsung J2, Redmi 6 devices
```

---

## Action Items

### Immediate (Today)

- [ ] Check Amplitude dashboard for device breakdown
- [ ] Screenshot or note the device distribution
- [ ] Identify which device tier has lowest conversion

### This Week

- [ ] Test app on low-tier device (borrow or use emulator)
- [ ] Check app load time on 3G/4G network
- [ ] Identify performance bottlenecks

### Next Week

- [ ] Optimize for low-tier devices
- [ ] Deploy agent to monitor conversions
- [ ] Set up Slack alerts

---

## Quick Links

- **Amplitude Dashboard:** https://amplitude.com/dashboard
- **Device Categorizer (Python script):** `ENHANCED_AMPLITUDE_AGENT.py`
- **Agent Implementation:** `AGENT_IMPLEMENTATION.md`
- **Session Summary:** `SESSION_SUMMARY.md`

---

## Need Help?

The agent is ready to deploy with your credentials:
```
API Key: 80ba75db8682a36264f7eb8becb6107b
Secret: a81c9a7884de00ab43e4577fe039fb6e
```

Just provide:
- [ ] Slack webhook URL
- [ ] Claude API key
- [ ] GitHub token (optional)

And we can deploy the full monitoring agent!
