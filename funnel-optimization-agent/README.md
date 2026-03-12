# Amplitude Analytics - Aspero B2C Mobile

**Amplitude Project ID:** 506002
**Platform:** Aspero Bond Investment App

This project contains all Amplitude analytics context, analysis scripts, and monitoring tooling for the Aspero B2C signup and engagement funnels.

---

## Structure

```
funnel-optimization-agent/
├── AMPLITUDE_CONTEXT.md          # Master event catalog (19 events, signup funnel)
├── docs/                         # Analysis docs and planning
│   ├── AMPLITUDE_QUICKSTART.md   # Getting started with Amplitude API
│   ├── TEST_AMPLITUDE.md         # API connection testing guide
│   ├── MONITORING_STRATEGY.md    # Alerting and monitoring strategy
│   ├── DEVICE_TIER_BREAKDOWN_GUIDE.md  # Device tier classification guide
│   ├── AGENT_IMPLEMENTATION.md   # Analytics agent implementation plan
│   ├── AGENT_DATA_FLOW.md        # Data flow architecture
│   ├── AGENT_FLOW_PLAN.md        # Agent flow design
│   ├── DEPLOYMENT_READY.md       # Deployment checklist
│   ├── FIX_SUMMARY.md            # Summary of fixes applied
│   ├── FROZEN_FRAMES_ANALYSIS.md # Android frozen frames investigation
│   ├── INTELLIGENT_CODE_ANALYZER_AGENT_PLAN.md
│   ├── LOCAL_TESTING_GUIDE.md    # Local testing setup
│   └── SESSION_SUMMARY.md        # Session notes and decisions
├── scripts/                      # Python analytics scripts
│   ├── test_amplitude_connection.py      # Verify API credentials
│   ├── query_mobile_email_pin_funnel.py  # Full signup funnel query
│   ├── mobile_email_pin_funnel_analysis.py
│   ├── signin_weekly_trend_analysis.py   # Week-on-week signin trends
│   ├── actual_signin_metrics.py          # Current period metrics
│   ├── enhanced_amplitude_agent.py       # Monitoring agent
│   ├── run_agent_locally.py              # Run agent locally
│   ├── localhost_agent_demo.py           # Local demo
│   ├── test_agent_locally.py             # Agent test runner
│   └── publish_metrics_to_slack.py       # Slack reporting
└── exports/                      # Exported data files
    └── placement_quality_analysis_20260306_164521.json
```

---

## Signup Funnel Overview

```
SIGNIN_PAGE_VIEW
  → SIGNIN_PAGE_NUMBER_ENTERED
    → SIGNIN_PAGE_VERIFY_OTP_SENT
      → VERIFY_OTP_SUCCESS          ← repeatable (every login)
        → EMAIL_VERIFY_OTP_SUCCESS  ← one-time (signup only)
          → SETUP_SECURE_PIN_SUCCESS ← USER REGISTERED ⭐⭐⭐⭐⭐
```

See [AMPLITUDE_CONTEXT.md](./AMPLITUDE_CONTEXT.md) for the full 19-event catalog with quality ratings.

---

## Platform Conversion Rates (baseline)

| Platform | SIGNIN_PAGE_VIEW → VERIFY_OTP_SUCCESS |
|---|---|
| Android | 29.2% |
| iOS | 53.8% |
| Web | 51.3% |

---

## Setup

```bash
export AMPLITUDE_API_KEY='your-api-key'
export AMPLITUDE_SECRET_KEY='your-secret-key'

# Test connection
python3 scripts/test_amplitude_connection.py

# Query signup funnel
python3 scripts/query_mobile_email_pin_funnel.py

# Run weekly trend analysis
python3 scripts/signin_weekly_trend_analysis.py
```

Credentials: Amplitude Project 506002 → Settings → API Keys

---

## Pending

- [ ] KYC funnel event catalog
- [ ] Investment funnel event catalog
- [ ] Automated 7-day funnel report
