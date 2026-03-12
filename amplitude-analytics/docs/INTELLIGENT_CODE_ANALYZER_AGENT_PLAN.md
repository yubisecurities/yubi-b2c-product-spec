# 🤖 Intelligent Code Analyzer Agent - Implementation Plan

## Vision
An automated agent that:
1. **Detects** anomalies in analytics/metrics
2. **Investigates** the codebase to find root causes
3. **Explains** what's wrong in plain English
4. **Suggests** specific fixes with code examples
5. **Notifies** team on Slack with all details

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│           INTELLIGENT CODE ANALYZER AGENT                   │
├─────────────────────────────────────────────────────────────┤

TRIGGER (Every 48 hours via AWS Lambda/GCP Cloud Functions)
    ↓
STEP 1: Fetch Analytics Data
    ├─ Query: Last 24 hours events
    ├─ Calculate: Conversion rates
    ├─ Baseline: Historical average
    └─ Output: Anomalies detected
    ↓
STEP 2: Anomaly Detection
    ├─ If metrics normal → Exit (no alert)
    ├─ If metrics bad → Continue to Step 3
    ├─ Analysis:
    │  ├─ Event drop: SIGNIN_PAGE_VIEW → SIGNIN_PAGE_NUMBER_ENTERED
    │  ├─ Error spike: SIGNIN_PAGE_VERIFY_API_FAILED
    │  ├─ Performance: Page load time > 5s
    │  └─ Platform-specific: Android/iOS/Web breakdowns
    └─ Output: Issue type + severity
    ↓
STEP 3: Clone Repo & Scan Code
    ├─ Get latest main branch
    ├─ Find relevant files based on issue type
    ├─ Examples:
    │  ├─ If "onBlur event issue" → Read SignInForm.tsx, useMobileNumberScreen.tsx
    │  ├─ If "blank screen" → Read MobileNoForm.web.tsx
    │  ├─ If "Phone Hint problem" → Read usePhoneHint.ts, SignInForm.tsx
    │  └─ If "performance" → Read bundle size, async operations
    └─ Output: Relevant code files
    ↓
STEP 4: AI-Powered Analysis
    ├─ Claude API analyzes code
    ├─ Compares to baseline/working version
    ├─ Identifies bugs:
    │  ├─ Missing returns/null checks
    │  ├─ Event not firing
    │  ├─ Race conditions
    │  ├─ Blocking operations
    │  └─ Logic errors
    └─ Output: Root cause diagnosis
    ↓
STEP 5: Generate Fix Recommendations
    ├─ Show what's wrong (with line numbers)
    ├─ Show what the fix is
    ├─ Show before/after code
    ├─ Explain the fix
    └─ Output: Actionable recommendations
    ↓
STEP 6: Create Slack Report
    ├─ Issue severity (🔴 Critical / 🟡 Warning / 🟢 Info)
    ├─ What's wrong (in plain English)
    ├─ Where it is (file + line number)
    ├─ Root cause
    ├─ How to fix (with code example)
    ├─ Impact estimate
    └─ Link to code
    ↓
STEP 7: Send to Slack + Save Report
    ├─ Post: Slack channel #engineering-alerts
    ├─ Include: GitHub link to relevant code
    ├─ Store: Report in S3 for history
    └─ Log: Issue in internal database
    ↓
END
```

---

## Implementation Details

### Step 1: Setup Infrastructure

```yaml
# AWS Lambda Function (Recommended)
Runtime: Python 3.11
Memory: 1024 MB
Timeout: 300 seconds (5 minutes)
Trigger: CloudWatch Events (every 1 hour)
Environment Variables:
  - SLACK_WEBHOOK_URL
  - ANALYTICS_API_KEY
  - GITHUB_TOKEN
  - CLAUDE_API_KEY
Cost: ~$1-5/month

# Database (optional, for history)
DynamoDB Table: agent_issues
- issue_id (PK)
- timestamp
- issue_type
- severity
- metrics
- root_cause
- fix_recommended
- status (open/fixed/investigating)

# Storage
S3 Bucket: monitoring-reports/
- Reports stored by date
- Metrics history
- Root cause database
```

### Step 2: Anomaly Detection Logic

```python
class AnomalyDetector:
    def __init__(self, analytics_client):
        self.baseline = {
            'signin_funnel': 0.52,  # 52% conversion
            'verify_api_error': 0.02,  # 2% errors
            'page_load_time': 2.0,  # 2 seconds
            'event_firing_rate': 0.95,  # 95% fire
        }

    def detect_anomalies(self, metrics):
        """Compare current metrics to baseline"""
        issues = []

        # Check 1: Signin funnel conversion
        conversion = metrics['signin_entered'] / metrics['signin_viewed']
        if conversion < self.baseline['signin_funnel'] * 0.85:  # 15% drop
            issues.append({
                'type': 'conversion_drop',
                'severity': 'high',
                'current': conversion,
                'baseline': self.baseline['signin_funnel'],
                'drop_percent': (1 - conversion/self.baseline['signin_funnel']) * 100
            })

        # Check 2: Platform-specific drops
        for platform in ['android', 'ios', 'web']:
            platform_conv = metrics[f'{platform}_conversion']
            platform_baseline = self.baseline[f'{platform}_baseline']

            if platform_conv < platform_baseline * 0.80:  # 20% drop
                issues.append({
                    'type': 'platform_drop',
                    'platform': platform,
                    'severity': 'high',
                    'conversion': platform_conv
                })

        # Check 3: API errors
        error_rate = metrics['api_errors'] / metrics['api_requests']
        if error_rate > self.baseline['verify_api_error'] * 2.5:  # 2x spike
            issues.append({
                'type': 'api_error_spike',
                'severity': 'critical',
                'current_rate': error_rate,
                'baseline': self.baseline['verify_api_error']
            })

        # Check 4: Event not firing
        event_rate = metrics['events_fired'] / metrics['expected_events']
        if event_rate < self.baseline['event_firing_rate']:  # < 95%
            issues.append({
                'type': 'missing_events',
                'severity': 'high',
                'firing_rate': event_rate
            })

        return issues
```

### Step 3: Code Scanning

```python
class CodeScanner:
    def __init__(self, repo_path):
        self.repo_path = repo_path

    def scan_for_issue(self, issue):
        """Find relevant code files for the issue"""

        if issue['type'] == 'conversion_drop':
            files = [
                'src/screens/onboarding/MobileNumberFlow/mobileNumberVerification/MobileNumberVerificationScreen.tsx',
                'src/molecules/MobileNoForm/SignInForm.tsx',
                'src/molecules/MobileNoForm/MobileNoForm.web.tsx',
                'src/screens/onboarding/MobileNumberFlow/mobileNumberVerification/hooks/useMobileNumberScreen.tsx',
            ]

        elif issue['type'] == 'missing_events':
            files = [
                'src/screens/onboarding/events/onboardingEvents.ts',
                'src/screens/onboarding/MobileNumberFlow/mobileNumberVerification/hooks/useMobileNumberScreen.tsx',
            ]

        elif issue['type'] == 'platform_drop' and issue['platform'] == 'android':
            files = [
                'src/molecules/MobileNoForm/SignInForm.tsx',
                'src/molecules/MobileNoForm/hooks/usePhoneHint.ts',
            ]

        # Read and return file contents
        code_context = {}
        for file_path in files:
            full_path = f"{self.repo_path}/{file_path}"
            try:
                with open(full_path, 'r') as f:
                    code_context[file_path] = f.read()
            except FileNotFoundError:
                continue

        return code_context
```

### Step 4: AI-Powered Root Cause Analysis

```python
class CodeAnalyzer:
    def __init__(self, claude_api_key):
        self.client = anthropic.Anthropic(api_key=claude_api_key)

    def analyze_issue(self, issue, code_context):
        """Use Claude to analyze code and find root cause"""

        prompt = f"""
        Analyze this code issue and find the root cause.

        ISSUE: {issue['type']}
        SEVERITY: {issue['severity']}
        METRICS: {json.dumps(issue, indent=2)}

        RELEVANT CODE:
        {self._format_code_context(code_context)}

        TASK:
        1. Identify the root cause of this issue
        2. Explain what's wrong in plain English
        3. Show the exact lines causing the problem
        4. Provide a fix with before/after code
        5. Explain why this fix works

        Format your response as JSON with these fields:
        {{
            "root_cause": "Clear explanation of what's wrong",
            "problematic_file": "path/to/file.tsx",
            "problematic_lines": [10, 20, 30],
            "explanation": "Why this causes the issue",
            "fix": "The fix code snippet",
            "fix_explanation": "Why this fixes it",
            "impact": "High/Medium/Low - user impact",
            "time_to_fix": "30min/1hour/2hours - estimated"
        }}
        """

        response = self.client.messages.create(
            model="claude-opus-4-6",  # Use latest Claude model
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )

        return json.loads(response.content[0].text)

    def _format_code_context(self, code_context):
        """Format code with line numbers"""
        formatted = []
        for file_path, code in code_context.items():
            lines = code.split('\n')
            numbered = '\n'.join([f"{i+1:3d} | {line}" for i, line in enumerate(lines)])
            formatted.append(f"FILE: {file_path}\n{numbered}")
        return "\n\n".join(formatted)
```

### Step 5: Slack Report Generator

```python
class SlackReporter:
    def __init__(self, webhook_url):
        self.webhook_url = webhook_url

    def create_report(self, issue, analysis, metrics):
        """Create formatted Slack message"""

        severity_emoji = {
            'critical': '🔴',
            'high': '🟡',
            'medium': '🟠',
            'low': '🟢'
        }

        message = {
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": f"{severity_emoji[issue['severity']]} Auto-Detected Issue"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*What's Wrong:*\n{analysis['root_cause']}"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Where:*\n`{analysis['problematic_file']}` (lines {analysis['problematic_lines']})"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Impact:*\nConversion dropped from {metrics['baseline']:.1%} to {metrics['current']:.1%}"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*How to Fix:*\n```\n{analysis['fix']}\n```"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Why This Fixes It:*\n{analysis['fix_explanation']}"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"⏱️ Est. Fix Time: {analysis['time_to_fix']}"
                    }
                },
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {"type": "plain_text", "text": "View Code"},
                            "url": f"https://github.com/yubisecurities/yubi-b2c-mobile/blob/main/{analysis['problematic_file']}#L{analysis['problematic_lines'][0]}"
                        },
                        {
                            "type": "button",
                            "text": {"type": "plain_text", "text": "View Report"},
                            "url": f"https://monitoring.internal.yubi.io/reports/{issue['id']}"
                        }
                    ]
                }
            ]
        }

        requests.post(self.webhook_url, json=message)
```

### Step 6: Main Orchestrator

```python
import time
from datetime import datetime

class CodeAnalyzerAgent:
    def __init__(self, config):
        self.analytics = AnalyticsClient(config['analytics_key'])
        self.detector = AnomalyDetector(self.analytics)
        self.scanner = CodeScanner(config['repo_path'])
        self.analyzer = CodeAnalyzer(config['claude_api_key'])
        self.reporter = SlackReporter(config['slack_webhook'])
        self.db = DynamoDBClient()

    def run(self):
        """Main agent execution"""
        print(f"[{datetime.now()}] Starting Code Analyzer Agent...")

        # Step 1: Fetch metrics
        print("Step 1: Fetching analytics data...")
        metrics = self.analytics.get_last_24h_metrics()

        # Step 2: Detect anomalies
        print("Step 2: Detecting anomalies...")
        issues = self.detector.detect_anomalies(metrics)

        if not issues:
            print("✅ No anomalies detected")
            return

        # Step 3-5: Analyze each issue
        for issue in issues:
            print(f"Step 3-5: Analyzing {issue['type']}...")

            # Clone repo / get code
            code_context = self.scanner.scan_for_issue(issue)

            # Analyze with Claude
            analysis = self.analyzer.analyze_issue(issue, code_context)

            # Generate report
            self.reporter.create_report(issue, analysis, metrics)

            # Save to database
            self.db.save_issue({
                'timestamp': datetime.now().isoformat(),
                'issue': issue,
                'analysis': analysis,
                'status': 'open'
            })

            print(f"✅ Report sent to Slack")
            time.sleep(1)  # Rate limiting

        print(f"[{datetime.now()}] Agent run complete")

# Lambda handler
def lambda_handler(event, context):
    config = {
        'analytics_key': os.getenv('ANALYTICS_API_KEY'),
        'claude_api_key': os.getenv('CLAUDE_API_KEY'),
        'slack_webhook': os.getenv('SLACK_WEBHOOK_URL'),
        'repo_path': '/tmp/repo'  # Cloned in Lambda
    }

    agent = CodeAnalyzerAgent(config)
    agent.run()

    return {'statusCode': 200, 'body': 'Agent run complete'}
```

---

## What This Agent Would Detect

### Issue 1: Blank Screen on Web
```
Detection: Page load → form render delay
│
Analysis:
├─ File: src/molecules/MobileNoForm/MobileNoForm.web.tsx
├─ Problem: Function returns undefined instead of null
├─ Line: 12
├─ Impact: 2-3s blank screen
└─ Fix: Add "return null;"

Slack Alert:
🟡 Web Signin Page Blank Screen Detected
What's Wrong: MobileNoForm.web.tsx returns undefined when config loads
Where: src/molecules/MobileNoForm/MobileNoForm.web.tsx (line 12)
Impact: Form delayed 2-3 seconds on page load
How to Fix: Add explicit return null statement
Est. Time: 2 minutes
```

### Issue 2: 48% Conversion Drop
```
Detection: SIGNIN_PAGE_VIEW → SIGNIN_PAGE_NUMBER_ENTERED drop
│
Analysis:
├─ File: useMobileNumberScreen.tsx
├─ Problem: Event only fires on onBlur, not on submit
├─ Lines: 137-139, 190-192
├─ Impact: Event missed when user taps Continue button
└─ Fix: Fire event on both onBlur AND onSubmit

Slack Alert:
🔴 CRITICAL: 48% Signin Funnel Drop Detected
What's Wrong: SIGNIN_PAGE_NUMBER_ENTERED event only fires on field blur,
             not when user submits the form
Where: src/screens/onboarding/.../hooks/useMobileNumberScreen.tsx
       Lines: 137-139 (event logic), 195 (submit handler)
Impact: 8-12% of users who submit immediately don't trigger event
Root Cause: Missing event in onSubmitButtonPress handler
How to Fix: Add signinPageNumberEntered event call in submit handler
Est. Time: 15 minutes
```

### Issue 3: Android Performance Drop
```
Detection: Android conversion 63% vs iOS 38% (25% gap)
│
Analysis:
├─ File: SignInForm.tsx
├─ Problem: Phone Hint field set to editable={false}
├─ Lines: 48-71
├─ Impact: Field appears locked when Phone Hint unavailable
└─ Fix: Always make field editable, show hint on focus

Slack Alert:
🟡 Android-Specific Issue: 63% Drop Rate
What's Wrong: When Phone Hint is unavailable, field shows as locked (editable={false})
             Users can't type, think app is broken, abandon
Where: src/molecules/MobileNoForm/SignInForm.tsx (lines 48-71)
Impact: 15-20% of Android users see locked field and leave
Root Cause: Conditional rendering disabled input when Phone Hint shows
How to Fix: Keep field editable even when Phone Hint is active
Est. Time: 30 minutes
```

---

## Deployment Steps

```bash
# 1. Create Python package
pip install -r requirements.txt

# 2. Deploy to AWS Lambda
aws lambda create-function \
  --function-name code-analyzer-agent \
  --runtime python3.11 \
  --handler lambda_function.lambda_handler \
  --zip-file fileb://deployment.zip \
  --environment Variables={
      SLACK_WEBHOOK_URL=https://hooks.slack.com/...,
      ANALYTICS_API_KEY=xxx,
      CLAUDE_API_KEY=xxx,
      GITHUB_TOKEN=xxx
    }

# 3. Schedule 48-hour execution (runs every 2 days at 2 AM UTC)
aws events put-rule \
  --name code-analyzer-48hours \
  --schedule-expression "cron(0 2 */2 * ? *)"

aws events put-targets \
  --rule code-analyzer-48hours \
  --targets "Id"="1","Arn"="arn:aws:lambda:...","RoleArn"="arn:aws:iam::..."

# 4. Test
aws lambda invoke \
  --function-name code-analyzer-agent \
  response.json
```

---

## Cost Breakdown

```
Monthly Costs (48-hour schedule):
├─ AWS Lambda: ~$1 (15 executions/month, well under free tier)
├─ CloudWatch Logs: ~$2
├─ DynamoDB: ~$5
├─ Claude API: ~$5-10 (1-2 analyses every 2 days)
├─ Slack: Free (included in workspace)
└─ Total: ~$13-18/month (80% REDUCTION from hourly!)

vs.

Manual Investigation:
├─ 1 engineer × 2 hours/issue × $50/hr = $100+
└─ Agent finds issues 3-5 before manual discovery (48-hour schedule)
```

---

## Why 48-Hour Schedule Works for Signup Funnel

```
Trade-offs Analysis:

Hourly Schedule (every 1 hour):
├─ ✅ Catch issues within 1 hour
├─ ✅ Quick alerts
├─ ❌ Higher cost (~$50-70/month)
├─ ❌ More noise/false positives
├─ ❌ Overkill for signup funnel
└─ ❌ More API calls to analytics

48-Hour Schedule (every 2 days):
├─ ✅ Catch issues within 48 hours (still proactive!)
├─ ✅ Low cost (~$13-18/month, 80% REDUCTION)
├─ ✅ Reduces false positive alerts
├─ ✅ Signup funnel is relatively stable
├─ ✅ Still 10x faster than manual detection
└─ ✅ Perfect for monitoring trends

Reality Check:
- Most bugs discovered by users take days/weeks to report
- 48-hour detection is still dramatically faster than manual
- Signup funnel doesn't change hourly
- Natural variation smooths out over 48 hours
- Code changes trigger on-demand analysis anyway
```

**Recommendation:** Start with 48-hour for signup funnel. If you need faster detection later, easily upgrade to hourly (just change CloudWatch schedule).

---

## Success Metrics

```
What We'll Measure:
├─ Time to Issue Detection: < 48 hours (vs. days/weeks manual)
├─ Time to Diagnosis: < 10 min (vs. 1-2 hours manual)
├─ False Positives: < 5%
├─ Issues Found Before Users Report: 95%+
└─ Fix Time with Agent: 3x faster

Expected Benefits:
├─ Catch 95% of issues before users notice
├─ Reduce MTTR (Mean Time To Resolution) by 2-3x
├─ Enable proactive fixes instead of reactive
└─ Prevent 20-30% of production issues
```

---

## Phase Rollout

### Phase 1: Week 1-2 (MVP)
- [ ] Setup Lambda function
- [ ] Implement anomaly detection
- [ ] Code scanning for signin flow
- [ ] Slack reporter
- [ ] Manual testing

### Phase 2: Week 3
- [ ] Add Android-specific detection
- [ ] Add performance monitoring
- [ ] Add API error detection
- [ ] Setup database logging

### Phase 3: Week 4+
- [ ] Add more workflows (checkout, payment, etc)
- [ ] Implement auto-fix recommendations (in comment/PR)
- [ ] Add trending analysis
- [ ] Create dashboard/reports
- [ ] Integrate with PagerDuty for critical issues

---

## Next Steps

Ready to build this? I can:

1. ✅ Create the full Lambda function code
2. ✅ Set up AWS infrastructure as code (Terraform/CloudFormation)
3. ✅ Build the Claude prompt for code analysis
4. ✅ Create deployment scripts
5. ✅ Set up testing suite

What would you like me to start with?
