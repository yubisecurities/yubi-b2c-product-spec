"""
Slack Block Kit formatter and webhook sender.

Produces a rich, structured Slack message with:
  1. Header — period + overall health status
  2. Funnel steps — counts and conversion at each stage
  3. Platform breakdown — Android / iOS / Web side-by-side
  4. Week-over-week changes — key metrics vs prior 7 days
  5. Alerts — anomalies and threshold breaches
"""

import requests
from datetime import datetime
from typing import Dict, List

_STATUS_ICON = {"healthy": "✅", "warning": "🟡", "critical": "🔴"}
_STATUS_LABEL = {"healthy": "All Good", "warning": "Needs Attention", "critical": "Action Required"}
_PLATFORM_ICON = {"healthy": "✅", "warning": "⚠️", "alert": "🔴"}
_WOW_ARROW = lambda pct: "📈" if pct > 2 else ("📉" if pct < -2 else "→")


def build_message(
    period_label: str,
    funnel_steps: List[Dict],
    platform_insights: Dict[str, Dict],
    wow: Dict[str, Dict],
    alerts: List[str],
    health: str,
) -> Dict:
    """Build and return the full Slack Block Kit payload."""

    blocks = []

    # ── HEADER ────────────────────────────────────────────────────────────
    blocks.append({
        "type": "header",
        "text": {
            "type": "plain_text",
            "text": f"📊 Aspero Signup Funnel — {period_label}",
            "emoji": True,
        },
    })

    # Summary line
    registration  = next((s for s in funnel_steps if s.get("is_registration")), {})
    top_of_funnel = next((s for s in funnel_steps if s["event"] == "SIGNIN_PAGE_VIEW"), {})
    reg_count     = registration.get("count", 0)
    top_count     = top_of_funnel.get("count", 0)
    reg_pct       = registration.get("pct_of_top", 0)

    wow_reg   = wow.get("SETUP_SECURE_PIN_SUCCESS", {})
    wow_arrow = _WOW_ARROW(wow_reg.get("pct_change", 0))
    wow_pct   = wow_reg.get("pct_change", 0)

    blocks.append({
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": (
                f"{_STATUS_ICON[health]}  *{_STATUS_LABEL[health]}*\n"
                f"*{reg_count:,}* new registrations  ({reg_pct}% of sessions)  "
                f"{wow_arrow} *{wow_pct:+.1f}%* WoW  |  "
                f"{top_count:,} sessions at top of funnel"
            ),
        },
    })

    blocks.append({"type": "divider"})

    # ── FUNNEL STEPS ─────────────────────────────────────────────────────
    blocks.append(_md_section("*📉 Signup Funnel  ·  Last 7 Days (Unique Users)*"))

    current_stage = None
    lines: List[str] = []

    for step in funnel_steps:
        # Stage heading
        if step["stage"] != current_stage:
            current_stage = step["stage"]
            if lines:
                lines.append("")          # blank line between stages
            lines.append(f"*{current_stage}*")

        count    = step["count"]
        pct_top  = step["pct_of_top"]
        step_pct = step.get("step_conv")

        if step.get("is_registration"):
            lines.append(
                f"  ⭐  {step['label']}:  *{count:,}*"
                f"  —  {pct_top}% of sessions"
                + (f"  ·  {step_pct}% from prev step" if step_pct is not None else "")
            )
        elif step.get("is_key"):
            lines.append(
                f"  ✦  {step['label']}:  *{count:,}*"
                f"  —  {pct_top}% of sessions"
            )
        else:
            lines.append(f"  {step['label']}:  {count:,}  ({pct_top}%)")

    blocks.append(_md_section("\n".join(lines)))
    blocks.append({"type": "divider"})

    # ── PLATFORM BREAKDOWN ───────────────────────────────────────────────
    blocks.append(_md_section("*📱 Platform Conversion  ·  Signin → OTP Verified*"))

    platform_fields = []
    for platform in ["Android", "iOS", "Web"]:
        data  = platform_insights.get(platform, {})
        icon  = _PLATFORM_ICON.get(data.get("status", "healthy"), "✅")
        delta = data.get("delta_from_baseline", 0)
        platform_fields.append({
            "type": "mrkdwn",
            "text": (
                f"*{platform}*  {icon}\n"
                f"{data.get('views', 0):,} views → {data.get('verified', 0):,} verified\n"
                f"*{data.get('conversion', 0)}%*  "
                f"({delta:+.1f}pp vs {data.get('baseline', 0)}% baseline)"
            ),
        })

    blocks.append({"type": "section", "fields": platform_fields})
    blocks.append({"type": "divider"})

    # ── WEEK-OVER-WEEK ────────────────────────────────────────────────────
    wow_lines = ["*📆 Week-over-Week  ·  vs prior 7 days*\n"]
    for event in ["SIGNIN_PAGE_VIEW", "VERIFY_OTP_SUCCESS", "EMAIL_VERIFY_OTP_SUCCESS", "SETUP_SECURE_PIN_SUCCESS"]:
        w = wow.get(event)
        if not w:
            continue
        arrow  = _WOW_ARROW(w["pct_change"])
        label  = _event_label(event)
        change = w["pct_change"]
        wow_lines.append(
            f"  {arrow}  {label}:  "
            f"{w['previous']:,} → *{w['current']:,}*  "
            f"(*{change:+.1f}%*)"
        )

    blocks.append(_md_section("\n".join(wow_lines)))

    # ── ALERTS ────────────────────────────────────────────────────────────
    if alerts:
        blocks.append({"type": "divider"})
        alert_text = "*🚨 Alerts*\n" + "\n".join(f"• {a}" for a in alerts)
        blocks.append(_md_section(alert_text))

    # ── FOOTER ────────────────────────────────────────────────────────────
    blocks.append({
        "type": "context",
        "elements": [{
            "type": "mrkdwn",
            "text": (
                f"Amplitude Project {506002}  ·  "
                f"Generated {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}"
            ),
        }],
    })

    return {"blocks": blocks}


# ---------------------------------------------------------------------------
# Send
# ---------------------------------------------------------------------------

def send_to_slack(webhook_url: str, payload: Dict) -> bool:
    """POST the Block Kit payload to a Slack incoming webhook. Returns True on success."""
    try:
        resp = requests.post(
            webhook_url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10,
        )
        if resp.status_code == 200:
            return True
        print(f"  ⚠️  Slack returned HTTP {resp.status_code}: {resp.text}")
        return False
    except Exception as e:
        print(f"  ⚠️  Slack send failed: {e}")
        return False


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _md_section(text: str) -> Dict:
    return {"type": "section", "text": {"type": "mrkdwn", "text": text}}


_EVENT_LABELS = {
    "SIGNIN_PAGE_VIEW":           "Signin Page View",
    "SIGNIN_PAGE_NUMBER_ENTERED": "Mobile Number Entered",
    "SIGNIN_PAGE_VERIFY_OTP_SENT":"OTP Sent",
    "VERIFY_OTP_SUCCESS":         "OTP Verified",
    "EMAIL_PAGE_VIEW":            "Email Page View",
    "EMAIL_VERIFY_OTP_SUCCESS":   "Email Verified",
    "SETUP_SECURE_PIN_PAGE_VIEW": "PIN Setup Page",
    "SETUP_SECURE_PIN_SUCCESS":   "PIN Setup ✓ (Registered)",
}

def _event_label(event: str) -> str:
    return _EVENT_LABELS.get(event, event.replace("_", " ").title())
