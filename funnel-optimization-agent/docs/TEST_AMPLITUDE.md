# 🔗 Test Amplitude Connection

## Quick Start

### Step 1: Get Your Credentials

1. Go to: **https://analytics.amplitude.com/settings/api-keys**
2. Find and copy:
   - **Organization API Key**
   - **Organization Secret Key**

### Step 2: Set Environment Variables

```bash
export AMPLITUDE_API_KEY="your-org-api-key"
export AMPLITUDE_SECRET_KEY="your-org-secret-key"
```

### Step 3: Install Dependencies

```bash
pip install requests
```

### Step 4: Run the Test

```bash
python test_amplitude_connection.py
```

---

## Expected Output

If connection works, you'll see:

```
======================================================================
🔗 AMPLITUDE API CONNECTION TEST
======================================================================

✓ API Key found: 123abc456...
✓ Secret Key found: secret_key...

🔄 Initializing Amplitude client...

📡 Fetching signup funnel data (last 48 hours)...
  → Fetching SIGNIN_PAGE_VIEW events...
    POST https://api2.amplitude.com/events
    Status: 200
    ✓ Received 1250 events for SIGNIN_PAGE_VIEW

  → Fetching SIGNIN_PAGE_NUMBER_ENTERED events...
    POST https://api2.amplitude.com/events
    Status: 200
    ✓ Received 650 events for SIGNIN_PAGE_NUMBER_ENTERED

    Parsing 1250 events...
    Parsing 650 events...

======================================================================
📊 RESULTS
======================================================================

✓ Status: success
✓ Period: 2026-03-07T12:34:56 to 2026-03-09T12:34:56

📈 CONVERSION RATES BY PLATFORM:
----------------------------------------------------------------------
Platform     Views      Entries    Rate       Status
----------------------------------------------------------------------
Android      1000       520        52.0%      ✓ healthy
iOS          800        496        62.0%      ✓ healthy
Web          1200       606        50.5%      ✓ healthy
```

---

## Troubleshooting

### Error: "Amplitude credentials not found"
**Solution:** Set the environment variables
```bash
export AMPLITUDE_API_KEY="your-key"
export AMPLITUDE_SECRET_KEY="your-secret"
```

### Error: "HTTP Error 401"
**Solution:** Invalid API key or secret
- Go to https://analytics.amplitude.com/settings/api-keys
- Verify you copied the correct keys
- Make sure there are no extra spaces

### Error: "No 'data' field in response"
**Possible causes:**
1. No events recorded in the time period (try longer: change `hours=48` to `hours=168`)
2. Wrong event names (should be `SIGNIN_PAGE_VIEW` and `SIGNIN_PAGE_NUMBER_ENTERED`)
3. Events tracked with different names - check your Amplitude dashboard

### No events received
**Check:**
1. Are events being tracked to Amplitude? Check dashboard
2. Event names match exactly (case-sensitive)
3. Time period has events (try last 7 days instead of 48 hours)

---

## What This Tests

✅ Amplitude API connection
✅ Authentication (API key + secret)
✅ Event fetching for both events
✅ Platform-level data extraction
✅ Conversion rate calculation

Once this works, we know the agent will be able to fetch your signup data successfully!
