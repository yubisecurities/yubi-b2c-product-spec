#!/usr/bin/env python3
"""
Aspero Amplitude → Slack Agent
================================
Fetches 7-day rolling signup funnel data from Amplitude and posts a
compact report to Slack with 4 sections:

  1. Header — registrations, WoW, health, email method split
  2. Yesterday Snapshot — vs 7-day average
  3. Device Tier Table — 4 milestones × device tiers (with OTP/SSO split)
  4. Needs Attention + Wins

Funnel milestones fetched via Funnel API (same-user tracking) by device_type:
  OTP ✓         = VERIFY_OTP_SUCCESS           (new + returning users)
  Email ✓ OTP   = EMAIL_VERIFY_OTP_SUCCESS      (new users only)
  Email ✓ SSO   = SSO_VERIFICATION_SUCCESS      (new users only, launched ~7d ago)
  Signup ✓      = SETUP_SECURE_PIN_SUCCESS      (new users only)

Using Funnel API for current period ensures Em→PIN conversion is always ≤100%
(same user tracked across steps — timing boundary artefacts eliminated).

API calls: 7 total
  [1–2] device_type funnel (OTP→Email→Signup, OTP→SSO→Signup) for current 7d
  [3–6] event totals for 4 events (prior 7d, for WoW)
  [7]   event totals for 4 events (yesterday, for daily snapshot)

Usage:
  python3 agent.py [--dry-run]

Required env vars:
  AMPLITUDE_API_KEY      Amplitude API key    (Project 506002)
  AMPLITUDE_SECRET_KEY   Amplitude secret key
  SLACK_WEBHOOK_URL      Slack incoming webhook URL
"""

import json
import os
import sys
from datetime import datetime, timedelta

from amplitude import AmplitudeClient
from config import MILESTONE_EVENTS
from insights import (
    compute_device_funnel_table,
    compute_wow_totals,
    compute_yesterday_snapshot,
    generate_alerts_v2,
    generate_wins_v2,
    get_overall_health_v2,
)
from slack import build_message_v2, send_to_slack


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _date_window(days: int, offset_days: int = 0):
    end   = datetime.now() - timedelta(days=offset_days)
    start = end - timedelta(days=days)
    return start.strftime("%Y%m%d"), end.strftime("%Y%m%d")


def _period_label(start_str: str, end_str: str) -> str:
    start = datetime.strptime(start_str, "%Y%m%d")
    end   = datetime.strptime(end_str,   "%Y%m%d")
    if start.year == end.year:
        return f"{start.strftime('%b %-d')} – {end.strftime('%-d, %Y')}"
    return f"{start.strftime('%b %-d, %Y')} – {end.strftime('%b %-d, %Y')}"


def _event_total(by_device: dict) -> int:
    return sum(by_device.values())


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def run(dry_run: bool = False):
    # ── Credentials ───────────────────────────────────────────────────────
    api_key     = os.getenv("AMPLITUDE_API_KEY")
    secret_key  = os.getenv("AMPLITUDE_SECRET_KEY")
    webhook_url = os.getenv("SLACK_WEBHOOK_URL")

    missing = [k for k, v in {
        "AMPLITUDE_API_KEY":    api_key,
        "AMPLITUDE_SECRET_KEY": secret_key,
        "SLACK_WEBHOOK_URL":    webhook_url,
    }.items() if not v]

    if missing and not dry_run:
        print(f"❌  Missing env vars: {', '.join(missing)}")
        sys.exit(1)

    client = AmplitudeClient(api_key or "", secret_key or "")

    # ── Date windows ──────────────────────────────────────────────────────
    cur_start, cur_end   = _date_window(7)
    prev_start, prev_end = _date_window(7, offset_days=7)
    yest_str             = (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")
    label = _period_label(cur_start, cur_end)
    print(f"\n🗓  Period: {label}  ({cur_start} → {cur_end})")
    print(f"📅  Yesterday: {yest_str}")

    # ── Fetch [1–2] — current 7d funnels by device type ──────────────────
    # Using Funnel API (same-user tracking) instead of independent segmentation.
    # cumulativeRaw[i+1] <= cumulativeRaw[i] by definition → Em→PIN always ≤100%.
    print("\n📡  [1/7] OTP → Email OTP → Signup funnel by device type...")
    otp_email_funnel = client.get_funnel_by_device_type(
        [MILESTONE_EVENTS["otp"], MILESTONE_EVENTS["email_otp"], MILESTONE_EVENTS["signup"]],
        cur_start, cur_end,
    )
    print(f"    device_types={len(otp_email_funnel)}")

    print("\n📡  [2/7] OTP → Email SSO → Signup funnel by device type...")
    otp_sso_funnel = client.get_funnel_by_device_type(
        [MILESTONE_EVENTS["otp"], MILESTONE_EVENTS["email_sso"], MILESTONE_EVENTS["signup"]],
        cur_start, cur_end,
    )
    print(f"    device_types={len(otp_sso_funnel)}")

    # ── Fetch [3–6] — WoW prior period totals ─────────────────────────────
    print(f"\n📡  [3–6] WoW totals — prior period ({prev_start} → {prev_end})...")
    prior_otp    = client.get_event_totals(MILESTONE_EVENTS["otp"],       prev_start, prev_end)
    prior_email  = client.get_event_totals(MILESTONE_EVENTS["email_otp"], prev_start, prev_end)
    prior_sso    = client.get_event_totals(MILESTONE_EVENTS["email_sso"], prev_start, prev_end)
    prior_signup = client.get_event_totals(MILESTONE_EVENTS["signup"],    prev_start, prev_end)
    print(f"    otp={prior_otp:,}  email_otp={prior_email:,}  email_sso={prior_sso:,}  signup={prior_signup:,}")

    # ── Fetch [7] — Yesterday snapshot ────────────────────────────────────
    print(f"\n📡  [7] Yesterday totals ({yest_str})...")
    yest_otp    = client.get_event_totals(MILESTONE_EVENTS["otp"],       yest_str, yest_str)
    yest_email  = client.get_event_totals(MILESTONE_EVENTS["email_otp"], yest_str, yest_str)
    yest_sso    = client.get_event_totals(MILESTONE_EVENTS["email_sso"], yest_str, yest_str)
    yest_signup = client.get_event_totals(MILESTONE_EVENTS["signup"],    yest_str, yest_str)
    print(f"    otp={yest_otp:,}  email={yest_email:,}  sso={yest_sso:,}  signup={yest_signup:,}")

    # ── Analyse ───────────────────────────────────────────────────────────
    print("\n🔍  Generating insights...")

    device_table = compute_device_funnel_table(otp_email_funnel, otp_sso_funnel)

    # Current 7d totals derived from funnel results
    # OTP: funnel step[0] = all users who fired OTP (same as segmentation)
    cur_otp    = sum(s[0] for s in otp_email_funnel.values() if s)
    cur_email  = sum(s[1] for s in otp_email_funnel.values() if len(s) > 1)
    cur_sso    = sum(s[1] for s in otp_sso_funnel.values()   if len(s) > 1)
    cur_signup = (sum(s[2] for s in otp_email_funnel.values() if len(s) > 2) +
                  sum(s[2] for s in otp_sso_funnel.values()   if len(s) > 2))
    cur_email_total = cur_email + cur_sso

    wow = compute_wow_totals(
        cur_otp, cur_email_total, cur_signup,
        prior_otp, prior_email + prior_sso, prior_signup,
    )

    yesterday_snapshot = compute_yesterday_snapshot(
        yest_otp, yest_email + yest_sso, yest_signup,
        cur_otp, cur_email_total, cur_signup,
    )

    sso_pct   = round(cur_sso   / cur_email_total * 100, 1) if cur_email_total > 0 else 0
    email_pct = round(cur_email / cur_email_total * 100, 1) if cur_email_total > 0 else 0

    health = get_overall_health_v2(wow, device_table)
    alerts = generate_alerts_v2(wow, device_table, sso_pct)
    wins   = generate_wins_v2(wow, device_table, sso_pct)

    print(f"\n  📊 Registrations:  {cur_signup:,}")
    print(f"  📧 Email method:   OTP {email_pct}% | SSO {sso_pct}%")
    print(f"  🩺 Health:         {health.upper()}")
    if alerts:
        print(f"  🚨 Alerts ({len(alerts)}):")
        for a in alerts:
            print(f"     • {a}")
    if wins:
        print(f"  ✅ Wins ({len(wins)}):")
        for w in wins:
            print(f"     • {w}")

    # ── Slack ─────────────────────────────────────────────────────────────
    payload = build_message_v2(
        period_label=label,
        device_table=device_table,
        cur_otp=cur_otp,
        cur_email_otp=cur_email,
        cur_email_sso=cur_sso,
        cur_signup=cur_signup,
        wow=wow,
        yesterday_snapshot=yesterday_snapshot,
        alerts=alerts,
        wins=wins,
        health=health,
    )

    if dry_run:
        print("\n── DRY RUN — Slack payload ──────────────────────────────────────────")
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        print("────────────────────────────────────────────────────────────────────")
        return

    print("\n📤  Sending to Slack...")
    if send_to_slack(webhook_url, payload):
        print("✅  Report sent to Slack!")
    else:
        print("❌  Failed to send to Slack")
        sys.exit(1)


if __name__ == "__main__":
    dry_run = "--dry-run" in sys.argv
    run(dry_run=dry_run)
