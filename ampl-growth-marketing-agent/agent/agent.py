"""
Growth Marketing Agent — Orchestrator

Run:
    cd agent/
    cp .env.example .env          # fill in credentials
    pip install -r requirements.txt
    python agent.py
"""

import json
import os
import sys
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

# ── Validate required env vars before doing anything ─────────────────────────
REQUIRED = [
    "GOOGLE_ADS_DEVELOPER_TOKEN",
    "GOOGLE_ADS_CLIENT_ID",
    "GOOGLE_ADS_CLIENT_SECRET",
    "GOOGLE_ADS_REFRESH_TOKEN",
    "GOOGLE_ADS_LOGIN_CUSTOMER_ID",
    "GOOGLE_ADS_CUSTOMER_ID",
]

missing = [k for k in REQUIRED if not os.environ.get(k)]
if missing:
    print("[agent] Missing required environment variables:")
    for k in missing:
        print(f"  - {k}")
    print("\nCopy agent/.env.example → agent/.env and fill in the values.")
    print("Need a refresh token? Run: python scripts/generate_refresh_token.py")
    sys.exit(1)

from skills import campaign_analysis


def main():
    print("=" * 60)
    print("  Growth Marketing Agent — starting run")
    print("=" * 60)

    # ── Skill 1: Campaign Analysis ────────────────────────────────────────────
    print("\n[1/1] Running campaign analysis...")
    data = campaign_analysis.run()

    # Pretty-print results to console for now
    # (Slack + LLM skills will be added in future iterations)
    print("\n── Campaign Summary ─────────────────────────────────────────")
    cw = data["current_week"]
    pw = data["prior_week"]
    wow = data["wow"]
    dr  = data["date_range"]

    print(f"Period:                {dr['current_start']} → {dr['current_end']}")
    print(f"Impressions:           {cw['impressions']:,}  ({_fmt_pct(wow['impressions_pct'])} WoW)")
    print(f"Clicks:                {cw['clicks']:,}  ({_fmt_pct(wow['clicks_pct'])} WoW)")
    print(f"CTR:                   {cw['ctr']}%  ({_fmt_pct(wow['ctr_pct'])} WoW)")
    print(f"Spend:                 ₹{cw['cost']:,}  ({_fmt_pct(wow['cost_pct'])} WoW)")
    print(f"In-App Actions:        {cw['in_app_actions']:,.0f}  ({_fmt_pct(wow['in_app_actions_pct'])} WoW)")
    print(f"Cost / In-App Action:  ₹{cw['cost_per_in_app_action']:,}  ({_fmt_pct(wow['cost_per_in_app_action_pct'])} WoW)")
    print(f"ROAS:                  {cw['roas']}x  ({_fmt_pct(wow['roas_pct'])} WoW)")

    print("\n── Top Campaigns by Spend ────────────────────────────────────")
    print(f"  {'Campaign':<40}  {'Spend':>12}  {'CTR':>6}  {'In-App Actions':>14}  {'Cost/Action':>11}")
    print(f"  {'-'*40}  {'-'*12}  {'-'*6}  {'-'*14}  {'-'*11}")
    for c in data["top_campaigns"]:
        cpa = f"₹{c['cost_per_in_app_action']:,.0f}" if c['in_app_actions'] > 0 else "—"
        print(f"  {c['campaign_name'][:40]:<40}  ₹{c['cost']:>10,}  {c['ctr_pct']:>5}%  {c['in_app_actions']:>14,.0f}  {cpa:>11}")

    print("\n── Device Split ──────────────────────────────────────────────")
    for device, m in data["device_split"].items():
        print(f"  {device:<10}  {m['impressions']:>10,} impr  {m['clicks']:>6,} clicks  ₹{m['cost']:>8,.0f}")

    print("\n── Top Performing Ads ────────────────────────────────────────")
    for ad in data["top_ads"]:
        print(f"  [{ad['campaign_name'][:25]}]  {ad['impressions']:,} impr  {ad['ctr_pct']}% CTR")
        if ad["headlines"]:
            print(f"    Headlines: {' | '.join(ad['headlines'][:3])}")

    # Save raw data to exports/
    os.makedirs("../exports", exist_ok=True)
    from datetime import date
    out_path = f"../exports/campaign_data_{date.today().isoformat()}.json"
    with open(out_path, "w") as f:
        json.dump(data, f, indent=2, default=str)
    print(f"\n[agent] Raw data saved to {out_path}")

    print("\n[agent] Run complete.")


def _fmt_pct(v: Optional[float]) -> str:
    if v is None:
        return "n/a"
    sign = "+" if v >= 0 else ""
    return f"{sign}{v}%"


if __name__ == "__main__":
    main()
