# 📊 How the Agent Monitors Signup Funnel Conversion

## Data Flow Overview

```
┌─────────────────────────────────────────────────────────────────┐
│               AGENT MONITORING FLOW (Every 48 Hours)            │
├─────────────────────────────────────────────────────────────────┤

STEP 1: Agent Wakes Up (2 AM UTC)
    ↓
STEP 2: Query Analytics Data
    ├─ Which events?
    ├─ Time period?
    ├─ Platform breakdown?
    └─ How to get this data?
    ↓
STEP 3: Calculate Conversion Rates
    ├─ funnel_rate = events_entered / events_viewed
    ├─ platform_breakdown (Android/iOS/Web)
    └─ Compare to baseline
    ↓
STEP 4: Detect Anomalies
    ├─ If drop > threshold → Alert
    └─ If normal → Silent exit
    ↓
END
```

---

## Step 1: Data Source Options

First, you need to choose WHERE the agent gets data from:

### Option A: Mixpanel (RECOMMENDED)
```
Pros:
✅ Best-in-class funnel analysis
✅ Pre-built conversion tracking
✅ REST API (easy to query)
✅ Real-time data
✅ Free tier available
```

### Option B: Amplitude
```
Pros:
✅ Good funnel analysis
✅ Fast queries
✅ REST API
```

### Option C: Segment
```
Pros:
✅ Aggregates from multiple sources
✅ Sends to multiple platforms
✅ Good for data warehouse
```

### Option D: Custom Database (Firebase, Firestore, BigQuery)
```
Pros:
✅ Full control over data
✅ No third-party dependency
✅ Cheaper at scale
```

---

## Step 2: Events You're Already Tracking

Looking at your codebase, you have these events:

```
src/manager/analytics/eventList/onboarding.ts:

1. SIGNIN_PAGE_VIEW
   ├─ Event Type: Page View
   ├─ When Fires: User lands on signin page
   ├─ Data: timestamp, platform, user_id
   └─ Line: 6

2. SIGNIN_PAGE_NUMBER_ENTERED
   ├─ Event Type: Custom Event
   ├─ When Fires: User enters mobile number
   ├─ Data: mobile_number, timestamp, platform
   ├─ Line: 7
   └─ Note: Currently fires on onBlur only (we need to fix this!)

3. SIGNIN_PAGE_VERIFY_CLICKED
   ├─ Event Type: Click Event
   ├─ When Fires: User taps Continue button
   └─ Line: 8

4. SIGNIN_PAGE_VERIFY_API_SUCCESS / FAILED
   ├─ Event Type: API Result
   ├─ When Fires: OTP API response
   └─ Line: 9-10
```

---

## Step 3: Conversion Funnel Stages

```
SIGNIN FUNNEL (What the agent tracks):

Stage 1: SIGNIN_PAGE_VIEW
         ↓ (100% baseline)

Stage 2: SIGNIN_PAGE_NUMBER_ENTERED
         ↓ (52% conversion from Stage 1)

Stage 3: SIGNIN_PAGE_VERIFY_CLICKED
         ↓ (80% conversion from Stage 2)

Stage 4: SIGNIN_PAGE_VERIFY_API_SUCCESS
         ↓ (95% conversion from Stage 3)

Goal: Signin Complete
(Final conversion: 100% × 52% × 80% × 95% = 39.6%)

What Agent Monitors:
┌─────────────────────────────────────────┐
│ Most Important: Stage 1 → Stage 2       │
│                                         │
│ Baseline: 52% (52 out of 100 users)    │
│ Alert If: < 45% (7% drop)              │
│                                         │
│ This is the biggest funnel leak         │
│ Also platform-specific:                 │
│ ├─ Android: 52% baseline               │
│ ├─ iOS: 62% baseline                   │
│ └─ Web: 55% baseline                   │
└─────────────────────────────────────────┘
```

---

## Step 4: How Agent Queries Analytics

### Using Mixpanel REST API

```python
import requests
from datetime import datetime, timedelta

class MixpanelAnalytics:
    def __init__(self, project_token, api_key, api_secret):
        self.project_token = project_token
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = "https://mixpanel.com/api/2.0"

    def query_events(self, event_name, from_date, to_date):
        """Query Mixpanel for specific event counts"""

        # Example: Get count of SIGNIN_PAGE_VIEW events
        endpoint = f"{self.base_url}/events"

        params = {
            'event': event_name,
            'from_date': from_date.strftime('%Y-%m-%d'),
            'to_date': to_date.strftime('%Y-%m-%d'),
            'unit': 'day',
            'key': self.api_key,
            'secret': self.api_secret,
        }

        response = requests.get(endpoint, params=params)
        return response.json()

    def get_conversion_data(self):
        """Get last 48 hours of funnel data"""

        to_date = datetime.now()
        from_date = to_date - timedelta(days=2)  # Last 48 hours

        # Query: How many users viewed signin page?
        view_data = self.query_events(
            'SIGNIN_PAGE_VIEW',
            from_date,
            to_date
        )

        # Query: How many entered mobile number?
        enter_data = self.query_events(
            'SIGNIN_PAGE_NUMBER_ENTERED',
            from_date,
            to_date
        )

        # Parse response
        view_count = view_data['data']['values']['SIGNIN_PAGE_VIEW']
        enter_count = enter_data['data']['values']['SIGNIN_PAGE_NUMBER_ENTERED']

        # Calculate conversion
        conversion_rate = enter_count / view_count if view_count > 0 else 0

        return {
            'period': f"{from_date.date()} to {to_date.date()}",
            'views': view_count,
            'entries': enter_count,
            'conversion_rate': conversion_rate,
            'conversion_percent': conversion_rate * 100
        }

# Usage
mixpanel = MixpanelAnalytics(
    project_token='YOUR_TOKEN',
    api_key='YOUR_API_KEY',
    api_secret='YOUR_API_SECRET'
)

data = mixpanel.get_conversion_data()
print(f"Conversion Rate: {data['conversion_percent']:.1f}%")
# Output: Conversion Rate: 48.5%
```

---

### Using Firebase/BigQuery

```python
from google.cloud import bigquery
from datetime import datetime, timedelta

class FirebaseAnalytics:
    def __init__(self, project_id, dataset_id='analytics_XXX'):
        self.client = bigquery.Client(project=project_id)
        self.dataset_id = dataset_id

    def get_conversion_data(self):
        """Query Firebase events from BigQuery"""

        to_date = datetime.now()
        from_date = to_date - timedelta(days=2)

        query = f"""
        SELECT
            event_name,
            COUNT(DISTINCT user_id) as unique_users,
            COUNT(*) as event_count,
            platform
        FROM
            `{self.dataset_id}.events_*`
        WHERE
            event_date >= '{from_date.date()}'
            AND event_date <= '{to_date.date()}'
            AND event_name IN ('SIGNIN_PAGE_VIEW', 'SIGNIN_PAGE_NUMBER_ENTERED')
        GROUP BY
            event_name,
            platform
        ORDER BY
            event_name,
            platform
        """

        query_job = self.client.query(query)
        results = query_job.result()

        # Parse results
        data = {}
        for row in results:
            key = f"{row.event_name}_{row.platform}"
            data[key] = {
                'event': row.event_name,
                'platform': row.platform,
                'unique_users': row.unique_users,
                'event_count': row.event_count
            }

        # Calculate conversion rates
        conversions = {}

        for platform in ['Android', 'iOS', 'Web']:
            view_key = f"SIGNIN_PAGE_VIEW_{platform}"
            enter_key = f"SIGNIN_PAGE_NUMBER_ENTERED_{platform}"

            view_users = data.get(view_key, {}).get('unique_users', 0)
            enter_users = data.get(enter_key, {}).get('unique_users', 0)

            conversion_rate = enter_users / view_users if view_users > 0 else 0

            conversions[platform] = {
                'views': view_users,
                'entries': enter_users,
                'rate': conversion_rate,
                'percent': conversion_rate * 100
            }

        return conversions

# Usage
firebase = FirebaseAnalytics(project_id='your-gcp-project')
conversions = firebase.get_conversion_data()

for platform, data in conversions.items():
    print(f"{platform}: {data['percent']:.1f}%")
    # Output:
    # Android: 48.5%
    # iOS: 62.1%
    # Web: 55.3%
```

---

## Step 5: Calculate Baselines & Detect Anomalies

```python
class AnomalyDetector:
    def __init__(self):
        # Historical baselines (should come from database)
        self.baselines = {
            'overall': 0.52,      # 52%
            'Android': 0.52,
            'iOS': 0.62,
            'Web': 0.55,
        }

        # Thresholds for alerts
        self.alert_thresholds = {
            'critical': 0.30,     # Alert if < 30% (40% drop)
            'high': 0.45,         # Alert if < 45% (13% drop)
            'medium': 0.50,       # Alert if < 50% (4% drop)
        }

    def detect_anomalies(self, current_conversions):
        """Compare current data to baseline"""

        issues = []

        for platform, data in current_conversions.items():
            current_rate = data['percent'] / 100
            baseline = self.baselines.get(platform, self.baselines['overall'])

            # Calculate drop percentage
            drop_percent = (1 - current_rate / baseline) * 100

            # Determine severity
            if current_rate < self.alert_thresholds['critical']:
                severity = 'CRITICAL'
            elif current_rate < self.alert_thresholds['high']:
                severity = 'HIGH'
            elif current_rate < self.alert_thresholds['medium']:
                severity = 'MEDIUM'
            else:
                severity = None  # No alert

            if severity:
                issues.append({
                    'platform': platform,
                    'severity': severity,
                    'current_rate': current_rate * 100,
                    'baseline': baseline * 100,
                    'drop_percent': drop_percent,
                    'views': data['views'],
                    'entries': data['entries'],
                })

        return issues

# Usage
detector = AnomalyDetector()

# Current conversion data (from analytics query)
current_conversions = {
    'Android': {'views': 1000, 'entries': 480, 'percent': 48.0},
    'iOS': {'views': 800, 'entries': 496, 'percent': 62.0},
    'Web': {'views': 1200, 'entries': 606, 'percent': 50.5},
}

issues = detector.detect_anomalies(current_conversions)

for issue in issues:
    print(f"""
    {issue['severity']} - {issue['platform']}
    Current: {issue['current_rate']:.1f}%
    Baseline: {issue['baseline']:.1f}%
    Drop: {issue['drop_percent']:.1f}%
    Users: {issue['views']} views → {issue['entries']} entries
    """)
```

---

## Step 6: Real-Time Example Execution

```
SCENARIO: Agent runs at 2 AM UTC on Wednesday

Query Result:
├─ Period: Monday 2 AM → Wednesday 2 AM (48 hours)
├─ Total Views: 3000 users
├─ Total Entries: 1500 users
├─ Overall Conversion: 50%
└─ Platform Breakdown:
   ├─ Android: 48% (1000 views, 480 entries) ❌ [48% < 52% baseline]
   ├─ iOS: 62% (800 views, 496 entries) ✅ [62% = baseline]
   └─ Web: 50.5% (1200 views, 606 entries) ✅ [50.5% > 50% threshold]

Analysis:
├─ Anomaly Detected: Android 48% < baseline 52%
├─ Drop: 7.7% below baseline
├─ Severity: MEDIUM (between 45% and 50%)
└─ Trigger: YES → Proceed to root cause analysis

Root Cause Analysis:
├─ Agent clones repo
├─ Scans: SignInForm.tsx, usePhoneHint.ts, useMobileNumberScreen.tsx
├─ Claude AI analyzes code
├─ Finds: Phone Hint field editable={false}
├─ Root Cause: "When Phone Hint unavailable, field locked"
└─ Recommendation: "Make field always editable"

Slack Alert Sent:
🟡 Android Signup Drop Detected
Current: 48% (vs 52% baseline)
Issue: Phone Hint field appears locked when unavailable
Fix: Keep field editable, show hint on focus
Est. Time: 30 minutes
Link: GitHub PR to relevant code
```

---

## Step 7: Full Agent Code (Data Collection)

```python
import requests
from datetime import datetime, timedelta
from typing import Dict, List
import json

class SignupFunnelMonitor:
    def __init__(self, analytics_client, anomaly_detector, code_analyzer):
        self.analytics = analytics_client
        self.detector = anomaly_detector
        self.analyzer = code_analyzer

    def run_48hour_check(self):
        """Main agent execution for 48-hour check"""

        print(f"[{datetime.now()}] Starting 48-hour signup funnel check...")

        # STEP 1: Query last 48 hours of data
        print("Step 1: Querying analytics...")
        current_data = self.analytics.get_conversion_data()

        print(f"Raw Data: {json.dumps(current_data, indent=2)}")

        # STEP 2: Detect anomalies
        print("Step 2: Analyzing data...")
        issues = self.detector.detect_anomalies(current_data)

        if not issues:
            print("✅ No anomalies detected. Signup funnel healthy.")
            return

        print(f"⚠️ Found {len(issues)} anomalies:")
        for issue in issues:
            print(f"  - {issue['platform']}: {issue['drop_percent']:.1f}% drop")

        # STEP 3: Root cause analysis for each issue
        print("Step 3: Analyzing code...")
        for issue in issues:
            analysis = self.analyzer.analyze_signup_issue(issue)
            issue['analysis'] = analysis

        # STEP 4: Send alerts
        print("Step 4: Sending alerts...")
        for issue in issues:
            self.send_slack_alert(issue)

        # STEP 5: Log for history
        print("Step 5: Logging...")
        self.log_issues(issues)

        print("✅ 48-hour check complete")
        return issues

    def send_slack_alert(self, issue):
        """Send formatted alert to Slack"""
        # Implementation here
        pass

    def log_issues(self, issues):
        """Store in database for history"""
        # Implementation here
        pass

# Usage in Lambda
def lambda_handler(event, context):
    """AWS Lambda entry point"""

    # Initialize clients
    analytics = MixpanelAnalytics(
        project_token=os.getenv('MIXPANEL_TOKEN'),
        api_key=os.getenv('MIXPANEL_API_KEY'),
        api_secret=os.getenv('MIXPANEL_API_SECRET')
    )

    detector = AnomalyDetector()
    analyzer = CodeAnalyzer(os.getenv('CLAUDE_API_KEY'))

    # Run monitor
    monitor = SignupFunnelMonitor(analytics, detector, analyzer)
    issues = monitor.run_48hour_check()

    return {
        'statusCode': 200,
        'body': json.dumps({
            'timestamp': datetime.now().isoformat(),
            'issues_found': len(issues),
            'issues': issues
        })
    }
```

---

## Data Sources Comparison

| Feature | Mixpanel | Firebase | Amplitude | Custom DB |
|---------|----------|----------|-----------|-----------|
| Ease of Setup | ⭐⭐⭐ Easy | ⭐⭐ Moderate | ⭐⭐⭐ Easy | ⭐ Hard |
| Query Speed | Fast | Fast | Fast | Depends |
| Cost | ~$500-2000/mo | ~$100-300/mo | ~$1000+/mo | Lowest |
| API Quality | Excellent | Good | Good | DIY |
| Already Using? | Check your code | Likely (Firebase) | Possibly | Check |

---

## Recommended Approach

### For MVP (Quick Start):
```
✅ Use: Mixpanel REST API
├─ Why: Easiest to implement
├─ Time: 1 day setup
├─ Cost: Minimal
└─ Decision: Do you already have Mixpanel?
```

### For Long-term:
```
✅ Use: Firebase BigQuery + Custom DB for baselines
├─ Why: Full control + cost-effective
├─ Time: 3-5 days setup
├─ Cost: ~$100-300/month
└─ Decision: If you already use Firebase
```

---

## Which Analytics Platform Are You Using?

Based on your code, you're sending events somewhere. I need to know:

1. **Where are events going?**
   - Mixpanel?
   - Amplitude?
   - Firebase?
   - Segment?
   - Custom backend?

2. **Do you have an API to query them?**
   - Can you access historical data?
   - Can you get event counts?

3. **Do you have baselines stored?**
   - Historical conversion rates?
   - Platform breakdowns?
   - Or should agent calculate them?

**Once you tell me what analytics platform you're using, I can:**
- ✅ Build the exact query code
- ✅ Set up the API integration
- ✅ Configure anomaly thresholds
- ✅ Deploy the agent

What analytics platform are you currently tracking events to?
