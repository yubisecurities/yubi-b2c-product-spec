# ampl-growth-marketing-agent

LLM-powered growth marketing intelligence agent for Aspero (Yubi B2C).

Connects to ad platforms, analyses campaign performance, and generates strategy briefs — posted to Slack on a schedule.

## Agent Skills (roadmap)

| # | Skill | Status |
|---|-------|--------|
| 1 | **Google & Meta Campaign Analysis** | ✅ In progress |
| 2 | **Campaign Insights & Recommendations** | Planned |
| 3 | **Competitor Campaign & Creative Analysis** | Planned |
| 4 | **Marketing Asset Generation** | Planned |
| 5 | **Audience & Segment Analysis** | Planned |
| 6 | **Weekly Strategy Brief** | Planned |
| 7 | **Compliance Guidelines Checker** | Planned |

## Project structure

```
ampl-growth-marketing-agent/
├── README.md
├── scripts/
│   └── generate_refresh_token.py  # One-time OAuth2 setup helper
├── exports/                        # Output JSON snapshots (gitignored)
└── agent/
    ├── agent.py                    # Orchestrator — run this
    ├── config.py                   # Env vars, date windows
    ├── requirements.txt
    ├── .env.example                # Template — copy to .env
    ├── connectors/
    │   └── google_ads.py           # Google Ads API client (GAQL)
    └── skills/
        └── campaign_analysis.py    # Skill 1 — performance metrics + WoW trends
```

## Quick start

### Step 1 — Get your credentials

You need four things from Google:

| Credential | Where to get it |
|---|---|
| **Developer Token** | [Google Ads manager account](https://ads.google.com) → Tools → API Center |
| **Client ID + Secret** | [Google Cloud Console](https://console.cloud.google.com) → APIs & Services → Credentials → OAuth 2.0 Client (Desktop) |
| **Refresh Token** | Run the helper script below |
| **Customer ID** | Your Ads account number (10 digits, no hyphens) |

### Step 2 — Generate your refresh token (one-time)

```bash
pip install google-auth-oauthlib
python scripts/generate_refresh_token.py
```

This opens your browser, you log in with the Google account linked to your Ads manager account, and it prints the refresh token.

### Step 3 — Set up your `.env`

```bash
cd agent/
cp .env.example .env
# Edit .env and fill in all values
```

### Step 4 — Run

```bash
pip install -r requirements.txt
python agent.py
```

## Sample output

```
════════════════════════════════════════════════════════════
  Growth Marketing Agent — starting run
════════════════════════════════════════════════════════════

── Campaign Summary ─────────────────────────────────────────
Period:       2026-03-06 → 2026-03-12
Impressions:  1,284,320  (+12.4% WoW)
Clicks:       38,210     (+8.1% WoW)
CTR:          2.97%      (-0.3% WoW)
Spend:        ₹241,800   (+5.2% WoW)
Conversions:  1,240       (+18.7% WoW)
ROAS:         3.2x        (+12.3% WoW)

── Top Campaigns by Spend ────────────────────────────────────
  Brand — Search               ₹ 85,200   3.4% CTR  480 conv
  Retargeting — App Users      ₹ 62,100   4.1% CTR  320 conv
  ...
```

## Related agents

- [funnel-optimization-agent](../funnel-optimization-agent/) — daily signup funnel health (Amplitude)
