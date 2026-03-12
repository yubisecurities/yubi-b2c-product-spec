#!/usr/bin/env python3
"""
Aspero Amplitude → Slack Agent
================================
Fetches the last 7 days of signup funnel data from Amplitude and posts
a rich insight report to a Slack channel.

Usage:
  python3 agent.py [--dry-run]

  --dry-run   Print the Slack message to stdout instead of sending it.

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
from config import FUNNEL_STEPS, FAILURE_EVENTS
from insights import (
    compute_funnel,
    compute_platform_insights,
    compute_wow,
    generate_alerts,
    get_overall_health,
)
from slack import build_message, send_to_slack


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _date_window(days: int, offset_days: int = 0):
    """
    Return (start_str, end_str) for a window of `days` ending `offset_days` ago.
    Format: YYYYMMDD
    """
    end   = datetime.now() - timedelta(days=offset_days)
    start = end - timedelta(days=days)
    return start.strftime("%Y%m%d"), end.strftime("%Y%m%d")


def _period_label(start_str: str, end_str: str) -> str:
    start = datetime.strptime(start_str, "%Y%m%d")
    end   = datetime.strptime(end_str,   "%Y%m%d")
    if start.year == end.year:
        return f"{start.strftime('%b %-d')} – {end.strftime('%-d, %Y')}"
    return f"{start.strftime('%b %-d, %Y')} – {end.strftime('%b %-d, %Y')}"


def _fetch_all(client: AmplitudeClient, start: str, end: str) -> dict:
    """Fetch unique user counts for every funnel + failure event."""
    all_events = [s["event"] for s in FUNNEL_STEPS] + FAILURE_EVENTS
    counts = {}
    for event in all_events:
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
        print(
            "\nSet them before running:\n"
            "  export AMPLITUDE_API_KEY='...'\n"
            "  export AMPLITUDE_SECRET_KEY='...'\n"
            "  export SLACK_WEBHOOK_URL='...'\n"
        )
        sys.exit(1)

    client = AmplitudeClient(api_key or "", secret_key or "")

    # ── Date windows ──────────────────────────────────────────────────────
    cur_start, cur_end   = _date_window(7)           # last 7 days
    prev_start, prev_end = _date_window(7, offset_days=7)  # prior 7 days

    label = _period_label(cur_start, cur_end)
    print(f"\n🗓  Period: {label}  ({cur_start} → {cur_end})")

    # ── Fetch ─────────────────────────────────────────────────────────────
    print("\n📡  Fetching current period from Amplitude...")
    current_counts = _fetch_all(client, cur_start, cur_end)

    print(f"\n📡  Fetching prior period ({prev_start} → {prev_end})...")
    prior_counts = _fetch_all(client, prev_start, prev_end)

    print("\n📡  Fetching platform breakdown (SIGNIN_PAGE_VIEW + VERIFY_OTP_SUCCESS)...")
    platform_views   = client.get_event_by_platform("SIGNIN_PAGE_VIEW",   cur_start, cur_end)
    platform_verified = client.get_event_by_platform("VERIFY_OTP_SUCCESS", cur_start, cur_end)
    print(f"    Views by platform:    {platform_views}")
    print(f"    Verified by platform: {platform_verified}")

    # ── Analyse ───────────────────────────────────────────────────────────
    print("\n🔍  Generating insights...")

    funnel_steps      = compute_funnel(current_counts)
    platform_insights = compute_platform_insights(platform_views, platform_verified)
    wow               = compute_wow(current_counts, prior_counts)
    failure_counts    = {e: current_counts.get(e, 0) for e in FAILURE_EVENTS}
    alerts            = generate_alerts(funnel_steps, platform_insights, failure_counts, wow)
    health            = get_overall_health(platform_insights, wow)

    # Quick console summary
    registrations = next((s for s in funnel_steps if s.get("is_registration")), {})
    print(f"\n  📊 Registrations:  {registrations.get('count', 0):,}  ({registrations.get('pct_of_top', 0)}% of sessions)")
    print(f"  🩺 Health:         {health.upper()}")
    if alerts:
        print(f"  🚨 Alerts ({len(alerts)}):")
        for a in alerts:
            print(f"     • {a}")

    # ── Slack ─────────────────────────────────────────────────────────────
    payload = build_message(
        period_label=label,
        funnel_steps=funnel_steps,
        platform_insights=platform_insights,
        wow=wow,
        alerts=alerts,
        health=health,
    )

    if dry_run:
        print("\n── DRY RUN — Slack payload ──────────────────────────────────────────")
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        print("────────────────────────────────────────────────────────────────────")
        return

    print("\n📤  Sending to Slack...")
    success = send_to_slack(webhook_url, payload)

    if success:
        print("✅  Report sent to Slack!")
    else:
        print("❌  Failed to send to Slack")
        sys.exit(1)


if __name__ == "__main__":
    dry_run = "--dry-run" in sys.argv
    run(dry_run=dry_run)
