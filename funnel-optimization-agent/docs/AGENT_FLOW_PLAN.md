# 📋 Agent Flow Plan - How Your Monitoring Agent Works

## 🎯 Overview

Your agent runs **automatically every 48 hours** on AWS Lambda and sends you Slack alerts with code-level recommendations for fixing funnel drop issues.

---

## 🏗️ Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        AWS CLOUDWATCH EVENT (Scheduler)                         │
│                   Triggers every 48 hours at 2 AM UTC                           │
└────────────────────────────────┬──────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         AWS LAMBDA (signup-funnel-monitor)                       │
│                                                                                  │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────────────────┐  │
│  │ Amplitude Client │  │ Anomaly Detector │  │ Claude AI Code Analyzer     │  │
│  │                  │  │                  │  │                              │  │
│  │ • Query Events   │  │ • Compare to     │  │ • Read your source code     │  │
│  │ • Get metrics    │  │   52% baseline   │  │ • Find root causes          │  │
│  │ • Device tiers   │  │ • Flag issues    │  │ • Suggest exact fixes       │  │
│  └──────────────────┘  └──────────────────┘  └──────────────────────────────┘  │
│                                                                                  │
└────────────────────────────────┬──────────────────────────────────────────────────┘
                                 │
                    ┌────────────┴────────────┐
                    ▼                         ▼
        ┌──────────────────────┐   ┌──────────────────────┐
        │   Slack Webhook      │   │ GitHub Notifications │
        │                      │   │ (optional)           │
        │ Sends formatted      │   │                      │
        │ alert with:          │   │ Create issues with   │
        │ • Device breakdown   │   │ recommended fixes    │
        │ • Anomalies found    │   │                      │
        │ • Code recommendations    │                      │
        │ • Next steps              │                      │
        └──────────────────────┘   └──────────────────────┘
                    │
                    ▼
        ┌──────────────────────┐
        │ You get Slack Alert  │
        │ Every 48 hours       │
        │ With actionable info │
        └──────────────────────┘
```

---

## 🔄 Step-by-Step Execution Flow

### **Step 1: CloudWatch Triggers Lambda (Every 48 Hours)**
```
Time: March 9, 2 AM UTC (and every 48 hours after)
Trigger: CloudWatch Events (Cron: 0 2 */2 * ? *)
Status: ✓ Lambda wakes up
```

---

### **Step 2: Query Amplitude for Last 48 Hours of Data**

**Lambda makes API call:**
```python
GET https://amplitude.com/api/2/events/list
Authorization: Basic base64(api_key:secret_key)

Query 1: SIGNIN_PAGE_VIEW events
   └─ Returns: User count by device, OS, platform

Query 2: SIGNIN_PAGE_NUMBER_ENTERED events
   └─ Returns: User count by device, OS, platform
```

**Example Response:**
```
SIGNIN_PAGE_VIEW:             908 events (683 unique users)
SIGNIN_PAGE_NUMBER_ENTERED:   908 events (228 unique users)
Overall Conversion:           33.4%
```

---

### **Step 3: Categorize Users by Device Tier**

**Lambda groups users:**
```
From: { device_model: "Samsung Galaxy A12", os_name: "Android" }
To:   "Mid-tier Android"

From: { device_model: "iPhone 13", os_name: "iOS" }
To:   "iOS"

From: { device_model: "Redmi 6", os_name: "Android" }
To:   "Low-tier Android"
```

**Device Categories:**
- 🔴 **Low-tier Android**: Redmi 6-9, Realme C, Moto E, Samsung J2-J7
- 🟡 **Mid-tier Android**: Samsung A/M, Poco, Redmi Note, OnePlus Nord, Moto G
- 🟢 **Premium Android**: Samsung S22+, OnePlus 9+, Pixel, Poco F
- 💙 **iOS**: iPhone 12+, iPad
- 🖥️ **Web**: Desktop browsers

---

### **Step 4: Calculate Conversions Per Device Tier**

```
Low-tier Android:
  Views: 240 → Entries: 57 → Conversion: 23.8%

Mid-tier Android:
  Views: 280 → Entries: 107 → Conversion: 38.2%

Premium Android:
  Views: 60 → Entries: 42 → Conversion: 70.0%

iOS:
  Views: 82 → Entries: 18 → Conversion: 22.0%

Web:
  Views: 21 → Entries: 4 → Conversion: 19.0%
```

---

### **Step 5: Detect Anomalies**

**Compare each tier to 52% baseline:**

| Tier | Current | Baseline | Drop | Severity |
|---|---|---|---|---|
| Low-tier Android | 23.8% | 52% | -28.3% | 🔴 CRITICAL |
| Mid-tier Android | 38.2% | 52% | -13.8% | ⚠️ HIGH |
| Premium Android | 70.0% | 52% | +18.0% | ✅ HEALTHY |
| iOS | 22.0% | 52% | -30.0% | 🔴 CRITICAL |
| Web | 19.0% | 52% | -33.0% | 🔴 CRITICAL |

**Thresholds:**
- < 35% = 🔴 CRITICAL (alert immediately)
- < 45% = ⚠️ HIGH (alert)
- < 50% = ⚡ MEDIUM (log)
- ≥ 50% = ✅ HEALTHY (no alert)

---

### **Step 6: Claude AI Analyzes Your Code**

**Lambda calls Claude API with:**
```json
{
  "anomalies": [
    {
      "tier": "iOS",
      "current": 22.0,
      "baseline": 52.0,
      "drop": 30.0,
      "severity": "CRITICAL"
    },
    {
      "tier": "Low-tier Android",
      "current": 23.8,
      "baseline": 52.0,
      "drop": 28.3,
      "severity": "CRITICAL"
    }
  ],
  "codebase": "yubi-b2c-mobile React Native",
  "relevant_files": [
    "screens/MobileNumberEntry/useMobileNumberScreen.tsx",
    "components/PhoneNumberInput.tsx",
    "screens/MobileNumberEntry/usePhoneHint.tsx"
  ]
}

Prompt: "Given these anomalies, what in the code could cause 30% drop in iOS signup?"
```

**Claude Response:**
```
iOS Issue Analysis:
1. usePhoneHint.tsx - iOS keyboard handling
   └─ May not be capturing phone number correctly
   └─ Try: Verify keyboard state management

2. PhoneNumberInput.tsx - Input validation
   └─ Possible validation error on iOS
   └─ Try: Add try-catch around validation

3. Loading state timing
   └─ 2-3 second delay might trigger iOS timeout
   └─ Try: Reduce initial config fetch time
```

---

### **Step 7: Format Slack Alert**

**Agent creates rich Slack message:**

```
🚨 SIGNUP FUNNEL ANOMALY DETECTED

📊 Current Status:
   Period:        March 7-9, 2026 (last 48 hours)
   Overall Conv:  33.4% (baseline 52%, drop -18.6%)
   Total Views:   683 users
   Total Entries: 228 users

📱 Device Tier Breakdown:
   🔴 iOS:             22.0% (drop -30.0%) CRITICAL
   🔴 Web:             19.0% (drop -33.0%) CRITICAL
   🔴 Low-tier Android: 23.8% (drop -28.3%) CRITICAL
   ⚠️  Mid-tier Android: 38.2% (drop -13.8%) HIGH
   ✅ Premium Android:  70.0% (healthy)

🎯 Root Cause Analysis:

1. iOS Issue (CRITICAL)
   File: screens/MobileNumberEntry/usePhoneHint.tsx:45
   Problem: Keyboard input not captured correctly
   Fix: Update iOS-specific keyboard handler
   Estimated Impact: +8-10% conversion

2. Low-Tier Device Issue (CRITICAL)
   File: screens/MobileNumberEntry/useMobileNumberScreen.tsx:215
   Problem: Loading state > 3 seconds, users abandon
   Fix: Cache remote config, reduce load time < 2s
   Estimated Impact: +5-8% conversion

3. Event Tracking Missing (HIGH)
   File: screens/MobileNumberEntry/useMobileNumberScreen.tsx:190
   Problem: Event only fires on blur, not submit
   Fix: Add event tracking to form submit handler
   Estimated Impact: +3-5% conversion

💡 Next Steps:
   1. Prioritize iOS fix (highest impact + urgency)
   2. Optimize device load time
   3. Add submit event tracking
   4. Deploy and monitor next 48-hour cycle

🔗 View Dashboard: https://analytics.amplitude.com/dashboard
```

---

### **Step 8: Send Slack Alert**

**Lambda sends to Slack Webhook:**
```
POST https://hooks.slack.com/services/YOUR/WEBHOOK/URL
Content-Type: application/json

Payload: {
  "text": "🚨 Signup Funnel Alert",
  "blocks": [ ... formatted message ... ]
}

Response: 200 OK ✓
```

---

### **Step 9: Store Results (Optional)**

**Agent can optionally:**
- Store alert history in DynamoDB
- Send GitHub issues with recommendations
- Email summary to team
- Create PagerDuty incident if CRITICAL

---

## 📅 48-Hour Cycle Example

```
Day 1 - Monday, March 9, 2 AM UTC
├─ Lambda triggered by CloudWatch
├─ Fetches last 48 hours of Amplitude data
├─ Processes 908 events
├─ Detects 4 anomalies
├─ Analyzes code with Claude
└─ Sends Slack alert ✓

Day 1 - Monday, March 9, 3 AM UTC (or whenever you see it)
└─ You receive Slack alert with:
   • Device tier breakdown
   • Exact issues identified
   • File:line recommendations
   • Estimated fix impact

Day 1-2 - You fix issues locally and deploy
└─ Push to production

Day 3 - Wednesday, March 11, 2 AM UTC
├─ Lambda triggers again
├─ Fetches latest data
├─ Compares new metrics vs previous
├─ If conversion improved: 📈 "Fixed! Conversion now 45%"
└─ If still broken: Alert with new analysis

Repeat every 48 hours automatically...
```

---

## 🔧 Lambda Function Code Flow

```python
def lambda_handler(event, context):
    """
    Triggered every 48 hours by CloudWatch
    """

    # 1️⃣ Initialize clients
    amplitude = AmplitudeAnalyticsClient(api_key, secret_key)
    claude = ClaudeAIClient(api_key)
    slack = SlackAlerter(webhook_url)
    detector = AnomalyDetector(baseline=0.52)

    # 2️⃣ Fetch data from Amplitude
    view_events = amplitude.get_events('SIGNIN_PAGE_VIEW', hours=48)
    enter_events = amplitude.get_events('SIGNIN_PAGE_NUMBER_ENTERED', hours=48)

    # 3️⃣ Process events
    conversions = process_events(view_events, enter_events)
    # Output: {
    #   'Low-tier Android': {'views': 240, 'entries': 57, 'conversion': 0.238},
    #   'Mid-tier Android': {'views': 280, 'entries': 107, 'conversion': 0.382},
    #   ...
    # }

    # 4️⃣ Detect anomalies
    anomalies = detector.detect(conversions)
    # Output: [
    #   {'tier': 'iOS', 'drop': 30.0, 'severity': 'CRITICAL'},
    #   {'tier': 'Low-tier Android', 'drop': 28.3, 'severity': 'CRITICAL'},
    #   ...
    # ]

    # 5️⃣ Analyze code (if anomalies found)
    if anomalies:
        analysis = claude.analyze_anomalies(
            anomalies=anomalies,
            codebase='yubi-b2c-mobile',
            relevant_files=['useMobileNumberScreen.tsx', ...]
        )
        # Output: Root cause analysis with file:line recommendations

    # 6️⃣ Send Slack alert
    alert = format_slack_message(conversions, anomalies, analysis)
    slack.send(alert)

    # 7️⃣ Return response
    return {
        'statusCode': 200,
        'body': {
            'message': 'Alert sent successfully',
            'anomalies_detected': len(anomalies),
            'timestamp': datetime.now().isoformat()
        }
    }
```

---

## 🚀 Deployment Timeline

### **Week 1: Setup (Friday, March 7)**
```
1. Get Claude API key (5 min)
   └─ https://console.anthropic.com

2. Get Slack Webhook (10 min)
   └─ https://api.slack.com/apps
   └─ Create webhook in your workspace

3. Deploy to Lambda (15 min)
   └─ ./deploy_lambda.sh
   └─ Test manual invoke

✅ Agent deployed and running
```

### **Week 1-2: First Alert (Monday, March 9 at 2 AM UTC)**
```
Lambda automatically triggers
  └─ Fetches Amplitude data
  └─ Analyzes with Claude
  └─ Sends first Slack alert

You receive alert showing:
  ✓ Device tier breakdown
  ✓ Issues identified
  ✓ Code recommendations
```

### **Week 2: Investigate & Fix (March 9-11)**
```
You review alert:
  ✓ iOS issue - 30% drop
  ✓ Low-tier device performance
  ✓ Event tracking missing

You make fixes:
  □ Update usePhoneHint.tsx
  □ Optimize load time
  □ Add event tracking

You deploy to production
```

### **Week 2+: Monitor Improvements (Wednesday, March 11 at 2 AM UTC)**
```
Lambda triggers again (automatic)
  └─ Fetches new data
  └─ Compares to baseline
  └─ Shows improvement

If conversion improved: 📈
  ✓ "Great job! iOS conversion now 45% (+23%)"
  ✓ "Next focus: Low-tier Android"

If still broken: 📊
  ✓ "Still detecting issues in Mid-tier Android"
  ✓ "New recommendations..."

Repeat every 48 hours...
```

---

## 📊 Example Slack Alerts Over Time

### **Alert 1: March 9 (Initial)**
```
🚨 SIGNUP FUNNEL ANOMALY DETECTED
📊 Overall: 33.4% (baseline 52%, drop -18.6%)
📱 Device Breakdown:
   🔴 iOS: 22.0% (CRITICAL)
   🔴 Low-tier: 23.8% (CRITICAL)
   ⚠️ Mid-tier: 38.2% (HIGH)
   ✅ Premium: 70.0% (healthy)
```

### **Alert 2: March 11 (After your fix)**
```
📈 SIGNUP FUNNEL IMPROVED
📊 Overall: 41.5% (baseline 52%, drop -10.5%)
📱 Device Breakdown:
   ✅ iOS: 45.0% (+23% improvement!)
   ⚠️ Low-tier: 28.5% (still needs work)
   ✅ Mid-tier: 45.5% (improved)
   ✅ Premium: 72.0% (still healthy)
🎯 Next Priority: Low-tier Android performance
```

### **Alert 3: March 13 (Full recovery)**
```
✅ SIGNUP FUNNEL HEALTHY
📊 Overall: 51.8% (baseline 52%, almost there!)
📱 Device Breakdown:
   ✅ iOS: 51.0%
   ✅ Low-tier: 48.5%
   ✅ Mid-tier: 52.0%
   ✅ Premium: 73.0%
🎉 All metrics within healthy range!
```

---

## 💰 Cost Breakdown

```
AWS Lambda:
  • Invocations: 2 per day = 60 per month
  • Duration: ~10 seconds per run
  • Cost: ~$0.20/month

Amplitude API:
  • Queries: 2 per invocation (60/month)
  • Cost: Included in your plan

Claude API:
  • ~500 tokens per analysis
  • ~0.0003 per token (claude-opus)
  • Cost: ~$0.10/month

Slack:
  • Webhooks: Free

CloudWatch Events:
  • Cost: Free tier

────────────────
Total: ~$0.30/month (basically free)
```

---

## 🔐 Security

```
Credentials stored in Lambda environment:
├─ AMPLITUDE_API_KEY
├─ AMPLITUDE_SECRET_KEY
├─ CLAUDE_API_KEY
└─ SLACK_WEBHOOK_URL

Best Practices:
✓ Use AWS Secrets Manager instead of env vars
✓ Rotate keys monthly
✓ Use IAM roles (no hardcoded credentials)
✓ Enable CloudTrail logging
✓ Enable Lambda VPC for network isolation
```

---

## ❓ FAQ

**Q: What if no anomalies are detected?**
A: Agent still sends alert showing all metrics are healthy ✅

**Q: Can I customize thresholds?**
A: Yes, in Lambda environment:
```
CRITICAL_THRESHOLD = 0.35   # < 35%
HIGH_THRESHOLD = 0.45       # < 45%
BASELINE = 0.52             # 52%
```

**Q: What if API fails?**
A: Lambda has error handling + retry logic + CloudWatch logs

**Q: Can I test locally?**
A: Yes! Run: `python3 run_agent_locally.py`

**Q: How do I disable alerts?**
A: Set `SLACK_WEBHOOK_URL=""` to disable Slack, or disable CloudWatch trigger

**Q: Can I monitor multiple funnels?**
A: Yes! Clone and customize for:
- Signin funnel (current)
- Transaction funnel
- Onboarding funnel
- etc.

---

## 📞 Support

```
📖 Documentation:
   • DEPLOYMENT_READY.md - Deployment checklist
   • AGENT_IMPLEMENTATION.md - Full Lambda code
   • DEVICE_TIER_BREAKDOWN_GUIDE.md - Device analysis
   • localhost_agent_demo.py - Demo version
   • run_agent_locally.py - Local testing

🔧 Troubleshooting:
   • Check CloudWatch logs: /aws/lambda/signup-funnel-monitor
   • Test locally: python3 run_agent_locally.py
   • Verify credentials: echo $AMPLITUDE_API_KEY
   • Check Slack webhook: test in Slack app settings
```

---

## ✅ Checklist for Deployment

```
Before deploying to Lambda:

Credentials:
  □ Amplitude API Key (you have: 80ba75db...)
  □ Amplitude Secret Key (you have: a81c9a78...)
  □ Claude API Key (get from: console.anthropic.com)
  □ Slack Webhook URL (get from: api.slack.com/apps)

Setup:
  □ AWS account active
  □ AWS CLI configured locally
  □ Lambda execution role created
  □ CloudWatch Events rule created

Deployment:
  □ Run: ./deploy_lambda.sh
  □ Test: aws lambda invoke response.json
  □ Verify: Check CloudWatch logs
  □ Test Slack: Manual invoke to verify alert format

Monitoring:
  □ Subscribe to CloudWatch logs
  □ Set up Lambda error alerts
  □ Monitor first 3 runs (first 6 days)
  □ Adjust thresholds if needed
```

---

**Ready to deploy? Gather the 2 credentials and we'll set up Lambda! 🚀**
