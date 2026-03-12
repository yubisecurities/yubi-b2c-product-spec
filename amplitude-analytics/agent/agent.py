#!/usr/bin/env python3
"""
Aspero Amplitude → Slack Agent
================================
Fetches 7-day rolling signup funnel data from Amplitude and posts a
structured 5-section insight report to Slack:

  1. Stage 1 · Signin → OTP Verified  (full 6-step funnel + platform breakdown)
  2. Stage 2 · Email Verification      (full 6-step funnel — new users only)
  3. Stage 3 · PIN Setup               (full 3-step funnel — new users only)
  4. Device Quality                    (Low / Mid / Premium Android + iOS + Web)
  5. Insights & Recommendations

Usage:
  python3 agent.py [--dry-run]

Required env vars:
  AMPLITUDE_API_KEY      Amplitude API key    (Project 506002)
  AMPLITUDE_SECRET_KEY   Amplitude secret key
  SLACK_WEBHOOK_URL      Slack incoming webhook URL

Cron example (every Monday 9am):
  0 9 * * 1 cd /path/to/agent && python3 agent.py >> agent.log 2>&1
"""

import json
import os
import sys
from datetime import datetime, timedelta

from amplitude import AmplitudeClient
from config import STAGE1_STEPS, STAGE2_STEPS, STAGE3_STEPS, FAILURE_EVENTS
from insights import (
    compute_funnel,
    compute_platform_insights,
    compute_device_tier_insights,
    compute_wow,
    generate_alerts,
    generate_recommendations,
    get_overall_health,
)
from slack import build_message, send_to_slack


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _date_window(days: int, offset_days: int = 0):
    """Return (start_str, end_str) for a window of `days` ending `offset_days` ago. YYYYMMDD."""
    end   = datetime.now() - timedelta(days=offset_days)
    start = end - timedelta(days=days)
    return start.strftime("%Y%m%d"), end.strftime("%Y%m%d")


def _period_label(start_str: str, end_str: str) -> str:
    start = datetime.strptime(start_str, "%Y%m%d")
    end   = datetime.strptime(end_str,   "%Y%m%d")
    if start.year == end.year:
        return f"{start.strftime('%b %-d')} – {end.strftime('%-d, %Y')}"
    return f"{start.strftime('%b %-d, %Y')} – {end.strftime('%b %-d, %Y')}"


def _fetch_failure_counts(client: AmplitudeClient, start: str, end: str) -> dict:
    counts = {}
    for event in FAILURE_EVENTS:
        print(f"    {event}")
        counts[event] = client.get_event_totals(event, start, end)
    return counts


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

    label = _period_label(cur_start, cur_end)
    print(f"\n🗓  Period: {label}  ({cur_start} → {cur_end})")

    s1_events = [s["event"] for s in STAGE1_STEPS]
    s2_events = [s["event"] for s in STAGE2_STEPS]
    s3_events = [s["event"] for s in STAGE3_STEPS]

    # WoW uses 4 key milestone events only (light 2-step funnel per stage)
    wow_events = [
        "SIGNIN_PAGE_VIEW", "VERIFY_OTP_SUCCESS",
        "EMAIL_VERIFY_OTP_SUCCESS", "SETUP_SECURE_PIN_SUCCESS",
    ]

    # ── Fetch — 8 API calls total ──────────────────────────────────────────
    print("\n📡  [1/8] Stage 1 funnel — current period (6 steps)...")
    s1_counts = client.get_funnel(s1_events, cur_start, cur_end)
    print(f"    SIGNIN_PAGE_VIEW={s1_counts.get('SIGNIN_PAGE_VIEW', 0):,}  "
          f"VERIFY_OTP_SUCCESS={s1_counts.get('VERIFY_OTP_SUCCESS', 0):,}")

    print("\n📡  [2/8] Stage 1 funnel — by platform...")
    s1_platform = client.get_funnel_by_platform(s1_events, cur_start, cur_end)
    for plat, steps in s1_platform.items():
        views    = steps.get("SIGNIN_PAGE_VIEW", 0)
        verified = steps.get("VERIFY_OTP_SUCCESS", 0)
        conv     = round(verified / views * 100, 1) if views > 0 else 0
        print(f"    {plat:<10}  views={views}  verified={verified}  conv={conv}%")

    print("\n📡  [3/8] Stage 2 funnel — current period (6 steps)...")
    s2_counts = client.get_funnel(s2_events, cur_start, cur_end)
    print(f"    EMAIL_PAGE_VIEW={s2_counts.get('EMAIL_PAGE_VIEW', 0):,}  "
          f"EMAIL_VERIFY_OTP_SUCCESS={s2_counts.get('EMAIL_VERIFY_OTP_SUCCESS', 0):,}")

    print("\n📡  [4/8] Stage 3 funnel — current period (3 steps)...")
    s3_counts = client.get_funnel(s3_events, cur_start, cur_end)
    print(f"    SETUP_SECURE_PIN_PAGE_VIEW={s3_counts.get('SETUP_SECURE_PIN_PAGE_VIEW', 0):,}  "
          f"SETUP_SECURE_PIN_SUCCESS={s3_counts.get('SETUP_SECURE_PIN_SUCCESS', 0):,}")

    print(f"\n📡  [5/8] WoW milestones — prior period ({prev_start} → {prev_end})...")
    prior_counts = client.get_funnel(wow_events, prev_start, prev_end)

    print("\n📡  [6/8] Device tier — new user entries by device type (EMAIL_PAGE_VIEW)...")
    entries_by_device = client.get_event_by_device_type("EMAIL_PAGE_VIEW", cur_start, cur_end)
    print(f"    {len(entries_by_device)} device types found")

    print("\n📡  [7/8] Device tier — registrations by device type...")
    regs_by_device = client.get_event_by_device_type("SETUP_SECURE_PIN_SUCCESS", cur_start, cur_end)
    print(f"    {len(regs_by_device)} device types found")

    print("\n📡  [8/8] Failure events...")
    failure_counts = _fetch_failure_counts(client, cur_start, cur_end)

    # ── Analyse ───────────────────────────────────────────────────────────
    print("\n🔍  Generating insights...")

    stage1_funnel = compute_funnel(s1_counts, STAGE1_STEPS)
    stage2_funnel = compute_funnel(s2_counts, STAGE2_STEPS)
    stage3_funnel = compute_funnel(s3_counts, STAGE3_STEPS)

    platform_insights    = compute_platform_insights(s1_platform)
    device_tier_insights = compute_device_tier_insights(entries_by_device, regs_by_device)

    # WoW: align current key events with prior funnel output
    current_key = {
        "SIGNIN_PAGE_VIEW":        s1_counts.get("SIGNIN_PAGE_VIEW", 0),
        "VERIFY_OTP_SUCCESS":       s1_counts.get("VERIFY_OTP_SUCCESS", 0),
        "EMAIL_VERIFY_OTP_SUCCESS": s2_counts.get("EMAIL_VERIFY_OTP_SUCCESS", 0),
        "SETUP_SECURE_PIN_SUCCESS": s3_counts.get("SETUP_SECURE_PIN_SUCCESS", 0),
    }
    wow = compute_wow(current_key, prior_counts)

    alerts = generate_alerts(
        stage1_funnel, platform_insights, device_tier_insights, failure_counts, wow,
    )
    recs = generate_recommendations(
        stage1_funnel, stage2_funnel, device_tier_insights, platform_insights,
    )
    health = get_overall_health(platform_insights, wow)

    # Console summary
    regs = next((s for s in stage3_funnel if s.get("is_registration")), {})
    print(f"\n  📊 Registrations:  {regs.get('count', 0):,}")
    print(f"  🩺 Health:         {health.upper()}")
    if alerts:
        print(f"  🚨 Alerts ({len(alerts)}):")
        for a in alerts: print(f"     • {a}")
    if recs:
        print(f"  💡 Recs ({len(recs)}):")
        for r in recs: print(f"     • {r}")

    # ── Slack ─────────────────────────────────────────────────────────────
    payload = build_message(
        period_label=label,
        stage1_funnel=stage1_funnel,
        stage2_funnel=stage2_funnel,
        stage3_funnel=stage3_funnel,
        platform_insights=platform_insights,
        device_tier_insights=device_tier_insights,
        wow=wow,
        alerts=alerts,
        recommendations=recs,
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
