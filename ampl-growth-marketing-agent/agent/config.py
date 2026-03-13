import os
from datetime import date, timedelta

# ── Date windows ──────────────────────────────────────────────────────────────
TODAY         = date.today()
YESTERDAY     = TODAY - timedelta(days=1)

CURRENT_END   = YESTERDAY
CURRENT_START = CURRENT_END - timedelta(days=6)   # last 7 full days

PRIOR_END     = CURRENT_START - timedelta(days=1)
PRIOR_START   = PRIOR_END - timedelta(days=6)      # prior 7 days (WoW baseline)

# ── Google Ads ────────────────────────────────────────────────────────────────
# Manager (MCC) account ID — no hyphens, e.g. "1234567890"
GOOGLE_ADS_LOGIN_CUSTOMER_ID = os.environ.get("GOOGLE_ADS_LOGIN_CUSTOMER_ID", "")

# The specific sub-account to pull data from (can be same as MCC if flat structure)
GOOGLE_ADS_CUSTOMER_ID = os.environ.get("GOOGLE_ADS_CUSTOMER_ID", "")

GOOGLE_ADS_DEVELOPER_TOKEN = os.environ.get("GOOGLE_ADS_DEVELOPER_TOKEN", "")
GOOGLE_ADS_CLIENT_ID       = os.environ.get("GOOGLE_ADS_CLIENT_ID", "")
GOOGLE_ADS_CLIENT_SECRET   = os.environ.get("GOOGLE_ADS_CLIENT_SECRET", "")
GOOGLE_ADS_REFRESH_TOKEN   = os.environ.get("GOOGLE_ADS_REFRESH_TOKEN", "")

# ── AWS / Bedrock (LLM) ───────────────────────────────────────────────────────
AWS_REGION    = "ap-south-1"
BEDROCK_MODEL = "anthropic.claude-opus-4-5"

# ── Slack ─────────────────────────────────────────────────────────────────────
SLACK_WEBHOOK_URL = os.environ.get("SLACK_WEBHOOK_URL", "")
