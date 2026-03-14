# Code Sentinel Agent

**Status:** Planned — build starts March 13, 2026
**Owner:** Arpit Goyal
**Repo:** `yubisecurities/yubi-b2c-mobile`

---

## Overview

An automated agent that cross-references **live Amplitude funnel data** with the **React Native codebase** and publishes a weekly Slack report to the product/stakeholder channel.

Unlike pure analytics alerts, this agent reads the actual source code and uses Claude AI to explain *why* conversion dropped and *which line to fix*.

---

## Problem Statement

Signup and KYC funnel conversion is currently **below baseline**:

| Platform | Conversion | Baseline | Gap |
|---|---|---|---|
| Android | 41.4% | 52% | -10.6% |
| iOS | 46.8% | 52% | -5.2% |
| Web | 64.4% | 52% | +12.4% |
| **Overall** | **42.9%** | **52%** | **-9.1%** |

Without automated monitoring, these drops go undetected for weeks. When found, root cause analysis is manual and slow.

---

## Agent Goal

Every 48 hours, automatically:

1. **Query Amplitude** → detect funnel drops per platform
2. **Read source code** (in parallel) → extract analytics events, loading states, API calls, platform-specific conditions
3. **Send both to Claude AI** → get specific `file:line` root cause + recommended fix
4. **Publish to Slack** → formatted report with code diagnosis, ready for stakeholders

---

## Funnels in Scope

### Funnel 1: Signup

```
SIGNIN_PAGE_VIEW
    ↓
SIGNIN_PAGE_NUMBER_ENTERED
    ↓
VERIFY_OTP_PAGE_VIEW
    ↓
VERIFY_OTP_SUCCESS
    ↓
EMAIL_PAGE_VIEW
    ↓
EMAIL_PAGE_VERIFY_API_SUCCESS
    ↓
VERIFY_SECURE_PIN_PAGE_VIEW
    ↓
VERIFY_SECURE_PIN_SUCCESS  ← Signup complete
```

**Baseline completion rate:** 52% (Signin Page View → Mobile Number Entered step)

### Funnel 2: KYC

```
AADHAAR_PAN_INITIAL_SCREEN_VIEW
    ↓
AADHAAR_PAN_SCREEN_VIEW
    ↓
DIGILOCKER_VERIFICATION_IN_PROGRESS
    ↓
KYC_EMAIL_VERIFIED
    ↓
KYC_AML_VERIFIED  ← KYC complete
```

### Future Funnels (Phase 2)

- First investment flow
- Bank verification flow

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     AGENT ORCHESTRATOR                       │
│                        agent.py                             │
└──────────────┬──────────────────────────────┬───────────────┘
               │                              │
               ▼ (parallel)                  ▼ (parallel)
┌──────────────────────────┐    ┌─────────────────────────────┐
│    AMPLITUDE CLIENT       │    │      CODEBASE READER        │
│   amplitude_client.py    │    │     codebase_reader.py      │
│                          │    │                             │
│ For each funnel:         │    │ Reads source files mapped   │
│ • Fetch event counts     │    │ to each funnel stage:       │
│ • By platform (OS)       │    │                             │
│ • Current 7 days         │    │ Signup screens:             │
│ • Prior 7 days (WoW)     │    │ • MobileNumberEntry/        │
│                          │    │ • OTPVerification/          │
│ Outputs:                 │    │ • EmailVerification/        │
│ • Conversion per step    │    │ • PINSetup/                 │
│ • Platform breakdown     │    │                             │
│ • Anomalies flagged      │    │ KYC screens:                │
│ • WoW trend              │    │ • KYC/                      │
└──────────────┬───────────┘    │ • Digilocker/               │
               │                │                             │
               │                │ Extracts:                   │
               │                │ • Analytics event calls     │
               │                │ • Loading/error states      │
               │                │ • API calls                 │
               │                │ • Platform.OS conditions    │
               │                │ • Form submit handlers      │
               │                └──────────────┬──────────────┘
               │                               │
               └──────────────┬────────────────┘
                              ▼
               ┌──────────────────────────────┐
               │       CLAUDE AI ANALYZER      │
               │      claude_analyzer.py       │
               │                              │
               │ For each anomaly:            │
               │  Input: metrics + code       │
               │  Ask: "What in this code     │
               │  explains this drop? Give    │
               │  file:line and fix."         │
               │                              │
               │  Output:                     │
               │  • Root cause explanation    │
               │  • Exact file:line           │
               │  • Recommended code fix      │
               └──────────────┬───────────────┘
                              ▼
               ┌──────────────────────────────┐
               │       SLACK REPORTER          │
               │      slack_reporter.py        │
               │                              │
               │ Publishes weekly report to   │
               │ stakeholder Slack channel     │
               └──────────────────────────────┘
```

---

## File Structure

```
code-sentinel-agent/
├── agent.py               ← Main orchestrator (entry point)
├── amplitude_client.py    ← Amplitude API queries
├── codebase_reader.py     ← Read + extract from source files
├── claude_analyzer.py     ← Claude AI diagnosis
├── slack_reporter.py      ← Format + publish to Slack
├── config.py              ← Funnel definitions, thresholds, file mappings
├── requirements.txt
└── README.md
```

---

## config.py — Key Definitions

```python
# Funnel event sequences
SIGNUP_FUNNEL = [
    "SIGNIN_PAGE_VIEW",
    "SIGNIN_PAGE_NUMBER_ENTERED",
    "VERIFY_OTP_PAGE_VIEW",
    "VERIFY_OTP_SUCCESS",
    "EMAIL_PAGE_VIEW",
    "EMAIL_PAGE_VERIFY_API_SUCCESS",
    "VERIFY_SECURE_PIN_PAGE_VIEW",
    "VERIFY_SECURE_PIN_SUCCESS",
]

KYC_FUNNEL = [
    "AADHAAR_PAN_INITIAL_SCREEN_VIEW",
    "AADHAAR_PAN_SCREEN_VIEW",
    "DIGILOCKER_VERIFICATION_IN_PROGRESS",
    "KYC_EMAIL_VERIFIED",
    "KYC_AML_VERIFIED",
]

# Anomaly thresholds
CRITICAL_THRESHOLD = 0.35   # < 35% conversion = critical
HIGH_THRESHOLD     = 0.45   # < 45% = high
BASELINE           = 0.52   # 52% expected

# Source code directory
CODEBASE_PATH = "/Users/arpit.goyal/aspero repos/yubi-b2c-mobile/src"

# Funnel stage → source directory mapping
STAGE_TO_CODE = {
    "SIGNIN_PAGE_VIEW":                "screens/MobileNumberEntry/",
    "SIGNIN_PAGE_NUMBER_ENTERED":      "screens/MobileNumberEntry/",
    "VERIFY_OTP_PAGE_VIEW":            "screens/OTPVerification/",
    "VERIFY_OTP_SUCCESS":              "screens/OTPVerification/",
    "EMAIL_PAGE_VIEW":                 "screens/EmailVerification/",
    "EMAIL_PAGE_VERIFY_API_SUCCESS":   "screens/EmailVerification/",
    "VERIFY_SECURE_PIN_PAGE_VIEW":     "screens/PINSetup/",
    "VERIFY_SECURE_PIN_SUCCESS":       "screens/PINSetup/",
    "AADHAAR_PAN_INITIAL_SCREEN_VIEW": "screens/KYC/",
    "KYC_AML_VERIFIED":                "screens/KYC/",
}
```

---

## Slack Report Format

```
📊 FUNNEL HEALTH REPORT — Week of Mar 3–9, 2026

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SIGNUP FUNNEL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  4,769 users started signup this week
  204 completed PIN setup (4.3% end-to-end)

Step Conversion:
  ✅ Signin Page → Mobile Entered      42.9%  (4,769 → 2,047)
  ⚠️  Mobile Entered → OTP Sent        ~20%   (2,047 → 408)
  ✅ OTP Page → OTP Success            84.6%  (408 → 345)
  🔴 OTP Success → Email Success       54.2%  (336 → 182)  ← DROP
  ✅ Email Verified → PIN Page         153%   (182 → 280)
  ⚠️  PIN Page → PIN Success           72.9%  (280 → 204)

By Platform (Mobile Number Entry step):
  Android  41.4% ⚠️   4,183 users
  iOS      46.8% ⚠️     361 users
  Web      64.4% ✅     225 users

🔍 Code Issues Found:

  1. Email Verification Drop (All platforms)
     File: src/screens/EmailVerification/useEmailVerification.tsx:87
     Problem: No retry on API timeout — 209 users hit EMAIL_PAGE_VERIFY_API_FAILED
     Fix: Add retry with 3 attempts + 2s delay before showing error state

  2. OTP Timeout (Android low/mid-tier)
     File: src/screens/OTPVerification/useOTPScreen.tsx:143
     Problem: 30s timer too short on slow networks (2G/3G devices)
     Fix: Increase OTP_TIMEOUT from 30000 to 60000ms for Android

  3. Loading State (Web)
     File: src/screens/MobileNumberEntry/MobileNoForm.web.tsx:34
     Problem: Returns undefined instead of null during config load → blank screen
     Fix: Change `return undefined` → `return null`

Estimated impact if all fixed: 42.9% → ~50–52% 📈

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
KYC FUNNEL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  117 users started KYC → 113 completed (96.6%) ✅
  KYC funnel is healthy — no action needed.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Updated: 2026-03-09 09:00 IST | Runs every 48h
```

---

## Schedule

| Mode | How | When |
|---|---|---|
| On-demand | `python3 agent.py` | Any time |
| Daily | GitHub Actions cron | Weekdays 9 AM IST |
| Lambda | AWS CloudWatch | Every 48 hours |

GitHub Actions workflow: `.github/workflows/code-sentinel.yml`

---

## Credentials Required

| Credential | Status | Source |
|---|---|---|
| `AMPLITUDE_API_KEY` | ✅ Available | Amplitude Settings |
| `AMPLITUDE_SECRET_KEY` | ✅ Available | Amplitude Settings |
| `SLACK_WEBHOOK_URL` | ✅ Available | Slack App Settings |
| `CLAUDE_API_KEY` | ❌ Needed | console.anthropic.com |

---

## Build Phases

### Phase 1 — Amplitude + Codebase Reader (Day 1)
- `amplitude_client.py`: query both funnels, calculate step conversion, flag anomalies, WoW diff
- `codebase_reader.py`: auto-discover files per stage, extract events/API calls/platform conditions
- `config.py`: funnel definitions, thresholds, stage→file mapping

### Phase 2 — AI Analysis + Slack Report (Day 1–2)
- `claude_analyzer.py`: send anomalies + code to Claude, parse `file:line` response
- `slack_reporter.py`: format Block Kit message, publish to webhook
- `agent.py`: orchestrate all steps, run both in parallel

### Phase 3 — Scheduling + Deploy (Day 2)
- GitHub Actions workflow for daily run
- Secrets configuration
- First live run + verify Slack output

### Phase 4 — Extend to KYC + More Funnels (Future)
- Add KYC funnel to scope
- Add first investment funnel
- Add bank verification funnel

---

## Current Baseline Metrics (as of Mar 9, 2026)

**Signup funnel actual numbers:**

| Event | Count | Step Conv | Overall |
|---|---|---|---|
| SIGNIN_PAGE_VIEW | 4,769 | — | 100% |
| SIGNIN_PAGE_NUMBER_ENTERED | 2,047 | 42.9% | 42.9% |
| VERIFY_OTP_PAGE_VIEW | 408 | ~20% | 8.6% |
| VERIFY_OTP_SUCCESS | 345 | 84.6% | 7.2% |
| EMAIL_PAGE_VIEW | 336 | 97.4% | 7.0% |
| EMAIL_PAGE_VERIFY_API_SUCCESS | 182 | 54.2% | 3.8% |
| VERIFY_SECURE_PIN_PAGE_VIEW | 280 | — | 5.9% |
| VERIFY_SECURE_PIN_SUCCESS | 204 | 72.9% | 4.3% |
| SETUP_SECURE_PIN_SUCCESS | 114 | — | 2.4% |

**Known failure events:**
- `EMAIL_PAGE_VERIFY_API_FAILED`: 209 (biggest bottleneck)
- `VERIFY_OTP_FAILED`: 192
- `VERIFY_SECURE_PIN_FAILED`: 58
- `PIN_TOKEN_EXPIRED`: 153

---

## Related Projects

- **Funnel Optimization Agent** — `code/funnel-optimization-agent/` — daily signup + SSO report
- **Growth Marketing Agent** — `code/ampl-growth-marketing-agent/` — Google Ads + creative analysis
- **yubi-b2c-mobile** — React Native source code being monitored
