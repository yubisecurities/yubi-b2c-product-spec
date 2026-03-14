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

from skills import campaign_analysis, creative_analysis, report


def main():
    print("=" * 60)
    print("  Growth Marketing Agent — starting run")
    print("=" * 60)

    # ── Skill 1: Campaign Analysis ────────────────────────────────────────────
    print("\n[1/2] Running campaign analysis...")
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

    print("\n── Top Campaigns by Spend ────────────────────────────────────────────────")
    print(f"  {'Campaign':<40}  {'Spend':>12}  {'Spend WoW':>10}  {'Budget':>7}  {'CTR':>6}  {'Primary Conv':>12}  {'Conv WoW':>9}  {'Cost/Conv':>10}")
    print(f"  {'-'*40}  {'-'*12}  {'-'*10}  {'-'*7}  {'-'*6}  {'-'*12}  {'-'*9}  {'-'*10}")
    for c in data["top_campaigns"]:
        cpa         = f"₹{c['cost_per_in_app_action']:,.0f}" if c['in_app_actions'] > 0 else "—"
        spend_wow   = _fmt_pct(c.get("spend_wow_pct"))
        actions_wow = _fmt_pct(c.get("in_app_actions_wow_pct"))
        util        = c.get("budget_util_pct")
        budget_str  = f"{util:.0f}%{'!' if util and util >= 90 else ' '}" if util is not None else "n/a"
        print(f"  {c['campaign_name'][:40]:<40}  ₹{c['cost']:>10,}  {spend_wow:>10}  {budget_str:>7}  {c['ctr_pct']:>5}%  {c['in_app_actions']:>12,.0f}  {actions_wow:>9}  {cpa:>10}")
        # Show which specific events make up the primary conversions for this campaign
        for ev in c.get("primary_events", []):
            print(f"    └ {ev['action'][:60]:<60}  {ev['count']:>6,.0f}")

    print("\n── In-App Actions Breakdown (all tracked events) ─────────────")
    print(f"  Total spend ₹{cw['cost']:,} across {data['total_all_conversions']:,.0f} total in-app events")
    print(f"  {'In-App Action':<55}  {'Count':>7}  {'Cost/Action':>11}")
    print(f"  {'-'*55}  {'-'*7}  {'-'*11}")
    for a in data["in_app_actions_breakdown"]:
        cpa_str = f"₹{a['cost_per_action']:,.0f}"
        print(f"  {a['action'][:55]:<55}  {a['count']:>7,.0f}  {cpa_str:>11}")

    print("\n── Channel Type Split ────────────────────────────────────────")
    for ch, m in data["channel_split"].items():
        ctr = round(m["clicks"] / m["impressions"] * 100, 2) if m["impressions"] else 0
        print(f"  {ch:<20}  ₹{m['cost']:>10,.0f}  {m['impressions']:>10,} impr  {ctr:>5}% CTR")

    print("\n── Device Split ──────────────────────────────────────────────")
    for device, m in data["device_split"].items():
        print(f"  {device:<10}  {m['impressions']:>10,} impr  {m['clicks']:>6,} clicks  ₹{m['cost']:>8,.0f}")

    print("\n── Top Performing Ads ────────────────────────────────────────")
    for ad in data["top_ads"]:
        print(f"  [{ad['campaign_name'][:25]}]  {ad['impressions']:,} impr  {ad['ctr_pct']}% CTR")
        if ad["headlines"]:
            print(f"    Headlines: {' | '.join(ad['headlines'][:3])}")

    # ── Skill 2: Creative Analysis ────────────────────────────────────────────
    print("\n[2/2] Running creative analysis (APP_AD copy)...")
    dr = data["date_range"]
    creative_data = creative_analysis.run(dr["current_start"], dr["current_end"])

    if creative_data["ads"]:
        print(f"\n── Creative Analysis ({len(creative_data['ads'])} app ads) ─────────────────")
        for ad in creative_data["ads"]:
            h_preview = " | ".join(ad["headlines"][:2]) or "(no headlines)"
            print(f"  [{ad['campaign_name'][:30]}]  {ad['impressions']:,} impr  {ad['ctr_pct']}% CTR")
            print(f"    Copy: {h_preview[:80]}")
            if creative_data["llm_enabled"] and ad.get("analysis"):
                a = ad["analysis"]
                print(f"    Prop: {a.get('primary_value_prop','?')}  |  Hook: {a.get('emotional_hook','?')}  |  Clarity: {a.get('clarity_score','?')}/5")
                if a.get("what_missing"):
                    print(f"    Missing: {', '.join(a['what_missing'])}")

        if creative_data.get("synthesis"):
            print("\n── Creative Strategy Synthesis ──────────────────────────────")
            print(creative_data["synthesis"])
    else:
        print("[2/2] No APP_AD creatives found for the period.")

    # Save raw data to exports/
    os.makedirs("../exports", exist_ok=True)
    from datetime import date
    today = date.today().isoformat()
    out_path = f"../exports/campaign_data_{today}.json"
    with open(out_path, "w") as f:
        json.dump(data, f, indent=2, default=str)
    print(f"\n[agent] Raw data saved to {out_path}")

    # Generate and save the full formatted report (campaign + creative analysis)
    report_md = report.generate(data, creative_data)
    report_path = f"../exports/campaign_report_{today}.md"
    with open(report_path, "w") as f:
        f.write(report_md)
    print(f"[agent] Full report saved to {report_path}")

    print("\n[agent] Run complete.")


def _fmt_pct(v: Optional[float]) -> str:
    if v is None:
        return "n/a"
    sign = "+" if v >= 0 else ""
    return f"{sign}{v}%"


if __name__ == "__main__":
    main()
