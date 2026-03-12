# 🚀 Quick Start: Deploy Agent with Amplitude

Since you're using Amplitude, here's the fastest way to get the agent running.

---

## 1️⃣ Get Your Amplitude Credentials (2 minutes)

1. Go to: **https://analytics.amplitude.com/settings/api-keys**
2. Look for "Organization API Key" and "Organization Secret Key"
3. Copy them (you'll need them in step 3)

Example:
```
Organization API Key: 123abc456def789ghi
Organization Secret Key: secret_key_xyz789
```

---

## 2️⃣ Set Environment Variables (1 minute)

Create a `.env` file in your project root:

```bash
# Analytics
ANALYTICS_PROVIDER=amplitude
AMPLITUDE_API_KEY=your-org-api-key-here
AMPLITUDE_SECRET_KEY=your-org-secret-key-here

# Slack Webhook (where alerts go)
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL

# Claude API (for code analysis)
CLAUDE_API_KEY=sk-ant-your-key-here

# GitHub (optional, for repo access)
GITHUB_TOKEN=ghp_your-token-here

# AWS
AWS_REGION=us-east-1
```

**How to get each:**

### Slack Webhook URL
1. Go to your Slack workspace settings
2. Create incoming webhook for #engineering channel
3. Copy the webhook URL

### Claude API Key
1. Go to: **https://console.anthropic.com/account/keys**
2. Create new API key
3. Copy it

### GitHub Token (optional)
1. Go to: **https://github.com/settings/tokens**
2. Create new token with `repo` scope
3. Copy it

---

## 3️⃣ Deploy the Agent (5 minutes)

```bash
# Load environment variables
source .env

# Copy the Lambda function code
cp AGENT_IMPLEMENTATION.md lambda_function.py  # Extract the Python code

# Deploy
chmod +x deploy_lambda.sh
./deploy_lambda.sh
```

That's it! The agent is now deployed.

---

## 4️⃣ Test It (2 minutes)

### Test 1: Invoke manually
```bash
aws lambda invoke \
  --function-name signup-funnel-monitor \
  --region us-east-1 \
  response.json

cat response.json
```

### Test 2: Check logs
```bash
aws logs tail /aws/lambda/signup-funnel-monitor --follow
```

---

## 5️⃣ What Happens Next

### Every 48 hours at 2 AM UTC:

1. ✅ Agent queries last 48 hours of Amplitude data
2. ✅ Extracts: SIGNIN_PAGE_VIEW → SIGNIN_PAGE_NUMBER_ENTERED conversion
3. ✅ Calculates per-platform conversion rates
4. ✅ Compares to baselines (52% Android, 62% iOS, 55% Web)
5. ✅ If drop detected → Sends Slack alert with root cause analysis

### Example Alert:
```
🚨 Signup Funnel Anomaly Detected

Platform:      Android
Severity:      HIGH
Current Rate:  48% (down from 52% baseline)
Drop:          7.7% below baseline
Users:         1000 → 480 entries

Probable Causes:
1. Event not firing on form submit (HIGH likelihood, 8-12% impact)
   → File: src/screens/onboarding/.../useMobileNumberScreen.tsx:190
   → Fix: Fire event on both onBlur AND submit button click

2. Phone Hint field locked when API fails (MEDIUM likelihood, 5-8% impact)
   → File: src/molecules/MobileNoForm/SignInForm.tsx:66
   → Fix: Keep field editable, show hint on focus
```

---

## 🔧 How It Works

```
Amplitude API
      ↓
Extract Events (SIGNIN_PAGE_VIEW, SIGNIN_PAGE_NUMBER_ENTERED)
      ↓
Group by Platform (Android/iOS/Web)
      ↓
Calculate Conversion Rate
      ↓
Compare to Baseline (52%/62%/55%)
      ↓
Detect Anomalies (if drop > threshold)
      ↓
Use Claude AI to analyze code for root causes
      ↓
Send Slack alert with file:line references
      ↓
Log for historical tracking
```

---

## 📊 What Gets Monitored

| Metric | Current | Baseline | Alert If |
|--------|---------|----------|----------|
| **Overall** | - | 52% | < 45% |
| **Android** | - | 52% | < 45% |
| **iOS** | - | 62% | < 55% |
| **Web** | - | 55% | < 48% |

Checked every 48 hours.

---

## 🛠️ Troubleshooting

### Problem: "Cannot query Amplitude"
**Solution:** Verify API key and secret are correct
```bash
# Test Amplitude connection
curl -u YOUR_API_KEY:YOUR_SECRET_KEY \
  "https://api2.amplitude.com/events?start=1000&end=2000"
```

### Problem: "No anomalies detected" (when you expect alerts)
**Possible causes:**
- Funnel conversion is still healthy (> 45%)
- Agent hasn't run yet (waits 48 hours)
- Events not being tracked in Amplitude (check event names)

### Problem: "Slack alert not sending"
**Solution:** Verify webhook URL is correct
```bash
# Test Slack webhook
curl -X POST $SLACK_WEBHOOK_URL \
  -d '{"text":"Test message"}'
```

---

## 📝 Next Steps

1. ✅ Deploy the agent (you just did!)
2. ⏳ Wait 48 hours for first check
3. 📊 Monitor Slack for alerts
4. 🔧 When issues detected, fix code and re-deploy
5. 📈 Track improvements over time

---

## 💡 Tips

- **Test without waiting 48 hours:** Manually invoke the Lambda
  ```bash
  aws lambda invoke --function-name signup-funnel-monitor response.json
  ```

- **Change check frequency:** Edit `deploy_lambda.sh` line 938
  ```bash
  SCHEDULE_EXPRESSION="cron(0 2 */2 * ? *)"  # Every 48 hours
  # Change to:
  SCHEDULE_EXPRESSION="cron(0 * * * ? *)"    # Every hour (more expensive)
  ```

- **Adjust alert thresholds:** Edit `lambda_function.py` lines 290-295
  ```python
  self.thresholds = {
      'critical': 0.30,     # Alert if < 30%
      'high': 0.45,         # Alert if < 45%
      'medium': 0.50,       # Alert if < 50%
  }
  ```

---

## 📞 Support

If you hit issues:
1. Check Amplitude API docs: https://www.amplitude.com/docs/analytics/apis
2. Check AWS Lambda logs: `aws logs tail /aws/lambda/signup-funnel-monitor --follow`
3. Test Amplitude connection manually (see Troubleshooting)

---

## ✅ Checklist

- [ ] Got Amplitude API key and secret
- [ ] Created .env file with credentials
- [ ] Set up Slack webhook
- [ ] Got Claude API key
- [ ] Deployed agent with `deploy_lambda.sh`
- [ ] Tested with manual invoke
- [ ] Verified CloudWatch schedule is set
- [ ] Waiting for first 48-hour check!
