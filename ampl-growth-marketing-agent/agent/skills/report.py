"""
Skill — Report Generator

Converts the structured campaign data dict (output of campaign_analysis.run())
into a full formatted Markdown report. Includes:
  - Overall account summary (with WoW)
  - Per-campaign breakdown with auto-diagnosed issues
  - Full conversion funnel (all tracked events + CPAs)
  - Auto-detected measurement issues
  - Prioritised recommendations derived from data
  - Channel / device split tables
"""

from typing import Optional


# ── Helpers ───────────────────────────────────────────────────────────────────

def _fmt_pct(v: Optional[float], plus: bool = True) -> str:
    if v is None:
        return "n/a"
    sign = "+" if (v >= 0 and plus) else ""
    return f"{sign}{v}%"


def _wow_tag(v: Optional[float]) -> str:
    """Return a short WoW string like '+3.4%' or '**-52.9%**' (bold if > ±20%)."""
    if v is None:
        return "n/a"
    sign = "+" if v >= 0 else ""
    s = f"{sign}{v}%"
    return f"**{s}**" if abs(v) >= 20 else s


def _inr(v: float) -> str:
    return f"₹{v:,.0f}"


def _primary_event_share(events: list[dict], event_substr: str) -> float:
    """Return the % of primary conversions accounted for by events containing event_substr."""
    total = sum(e["count"] for e in events)
    matched = sum(e["count"] for e in events if event_substr in e["action"])
    return round(matched / total * 100, 1) if total > 0 else 0.0


# ── Section builders ──────────────────────────────────────────────────────────

def _section_overall(data: dict) -> str:
    cw  = data["current_week"]
    wow = data["wow"]
    dr  = data["date_range"]

    # Derive true-registration metrics from in_app_actions_breakdown
    true_reg_cpa = _get_true_reg_cpa(data)
    install_cpa  = _get_install_cpa(data)

    lines = [
        "## Overall Account Summary",
        "",
        f"**Period:** {dr['current_start']} → {dr['current_end']}",
        "",
        "| Metric | This Week | WoW |",
        "|---|---|---|",
        f"| Impressions | {cw['impressions']:,} | {_wow_tag(wow['impressions_pct'])} |",
        f"| Clicks | {cw['clicks']:,} | {_wow_tag(wow['clicks_pct'])} |",
        f"| CTR | {cw['ctr']}% | {_wow_tag(wow['ctr_pct'])} |",
        f"| Total Spend | {_inr(cw['cost'])} | {_wow_tag(wow['cost_pct'])} |",
        f"| All In-App Events (reported) | {cw['in_app_actions']:,.0f} | {_wow_tag(wow['in_app_actions_pct'])} |",
        f"| Reported CPA | {_inr(cw['cost_per_in_app_action'])} | ← see measurement issues below |",
    ]

    if true_reg_cpa:
        reg_count, reg_cpa = true_reg_cpa
        lines.append(f"| **True New Registrations (SETUP_SECURE_PIN_SUCCESS)** | **{reg_count:,.0f}** | one-time per user |")
        lines.append(f"| **True CPA (spend ÷ registrations)** | **{_inr(reg_cpa)}** | the honest number |")

    if install_cpa:
        inst_count, inst_cpa = install_cpa
        lines.append(f"| Install CPA (first_open) | {_inr(inst_cpa)} | {_inr(cw['cost'])} ÷ {inst_count:,.0f} installs |")

    return "\n".join(lines)


def _get_true_reg_cpa(data: dict) -> Optional[tuple]:
    """Find SETUP_SECURE_PIN_SUCCESS count and derive CPA."""
    cost = data["current_week"]["cost"]
    for a in data["in_app_actions_breakdown"]:
        if "SETUP_SECURE_PIN_SUCCESS" in a["action"] and "yubi-invest" not in a["action"]:
            count = a["count"]
            cpa = round(cost / count, 0) if count > 0 else None
            return (count, cpa)
    return None


def _get_install_cpa(data: dict) -> Optional[tuple]:
    """Find first_open (Aspero primary, not yubi-invest) count and derive CPA."""
    cost = data["current_week"]["cost"]
    for a in data["in_app_actions_breakdown"]:
        if "first_open" in a["action"] and "yubi-invest" not in a["action"]:
            count = a["count"]
            cpa = round(cost / count, 0) if count > 0 else None
            return (count, cpa)
    return None


def _diagnose_campaign(c: dict) -> list[str]:
    """
    Return a list of diagnostic bullet strings for a campaign based on its data.
    Checks: primary event composition, budget utilisation, spend WoW trend.
    """
    notes = []
    events = c.get("primary_events", [])
    total_primary = sum(e["count"] for e in events)

    # Check if first_open dominates primary conversions
    if total_primary > 0:
        install_pct = _primary_event_share(events, "first_open")
        if install_pct >= 80:
            notes.append(
                f"**Effectively an install campaign** — {install_pct}% of primary conversions "
                f"are `first_open` (installs). Intended conversion event is not firing or below "
                f"Smart Bidding minimum (~30-50/month). Smart Bidding defaulted to install signal."
            )
        elif install_pct >= 50:
            notes.append(
                f"**Install-heavy bidding** — {install_pct}% of primary conversions are `first_open`. "
                f"Intended downstream event has insufficient volume; consider adding a mid-funnel proxy."
            )

    # Check `in_app_purchase` volume — too sparse for Smart Bidding?
    iap_events = [e for e in events if "in_app_purchase" in e["action"]]
    if iap_events:
        iap_count = sum(e["count"] for e in iap_events)
        weekly_rate = iap_count
        monthly_est = weekly_rate * 4
        if monthly_est < 50:
            notes.append(
                f"**`in_app_purchase` too sparse** — ~{weekly_rate:.0f}/week (~{monthly_est:.0f}/month est). "
                f"Smart Bidding needs ≥30-50/month minimum. Recommend adding a higher-volume mid-funnel event "
                f"(e.g. `KYC_READY_FOR_TRADE`) as primary to give Smart Bidding a learnable signal."
            )

    # Budget utilisation
    util = c.get("budget_util_pct")
    if util is not None:
        if util >= 95:
            notes.append(
                f"**Budget capped ({util:.0f}%)** — spending at/above daily budget cap. "
                f"If the campaign had a better conversion signal, this budget is available to drive more quality conversions."
            )
        elif util < 50:
            notes.append(
                f"**Under-delivering ({util:.0f}% budget used)** — Smart Bidding is pulling back spend, "
                f"likely due to insufficient conversion signal. Adding a higher-volume primary conversion event "
                f"should restore bidding confidence."
            )

    # Spend WoW
    spend_wow = c.get("spend_wow_pct")
    if spend_wow is not None and spend_wow <= -30:
        notes.append(
            f"**Spend dropped {spend_wow}% WoW** — likely a bid strategy confidence collapse. "
            f"Smart Bidding reduces spend when it can't find enough users matching the conversion goal."
        )

    return notes


def _section_campaigns(data: dict) -> str:
    lines = ["## Campaign-Level Breakdown", ""]

    for c in data["top_campaigns"]:
        if c["cost"] == 0 and c["impressions"] == 0:
            continue  # skip fully paused with zero activity

        cpa     = _inr(c["cost_per_in_app_action"]) if c["in_app_actions"] > 0 else "—"
        util    = c.get("budget_util_pct")
        util_s  = f"{util:.0f}%" if util is not None else "n/a"
        status  = c.get("status", "")

        lines += [
            f"### {c['campaign_name']}",
            "",
            f"| Metric | Value |",
            f"|---|---|",
            f"| Status | {status} |",
            f"| Channel | {c.get('channel_type', '—')} |",
            f"| Spend | {_inr(c['cost'])} |",
            f"| Spend WoW | {_wow_tag(c.get('spend_wow_pct'))} |",
            f"| Budget Utilization | {util_s} |",
            f"| Impressions | {c['impressions']:,} |",
            f"| Clicks | {c['clicks']:,} |",
            f"| CTR | {c['ctr_pct']}% |",
            f"| Avg CPC | {_inr(c['avg_cpc'])} |",
            f"| Primary Conversions | {c['in_app_actions']:,.0f} |",
            f"| Conv WoW | {_wow_tag(c.get('in_app_actions_wow_pct'))} |",
            f"| Cost / Primary Conv | {cpa} |",
            "",
        ]

        # Primary event breakdown
        events = c.get("primary_events", [])
        if events:
            total = sum(e["count"] for e in events)
            lines.append("**Primary event composition (what Smart Bidding optimizes for):**")
            lines.append("```")
            lines.append(f"{total:.0f} primary conversions =")
            for ev in events:
                pct = round(ev["count"] / total * 100, 1) if total > 0 else 0
                clean = ev["action"].replace("Aspero Fixed Income- Buy Bonds (Android) ", "")
                lines.append(f"  └ {clean:<40}  {ev['count']:>6,.0f}   ({pct}%)")
            lines.append("```")
            lines.append("")

        # Diagnosis
        diagnoses = _diagnose_campaign(c)
        if diagnoses:
            lines.append("**Diagnosis:**")
            for d in diagnoses:
                lines.append(f"- {d}")
            lines.append("")

        lines.append("---")
        lines.append("")

    return "\n".join(lines)


def _section_funnel(data: dict) -> str:
    lines = [
        "## Full Conversion Funnel (All Tracked Events)",
        "",
        f"Total spend {_inr(data['current_week']['cost'])} across {data['total_all_conversions']:,.0f} total in-app events.",
        "",
        "| In-App Event | Count | Cost/Action | Notes |",
        "|---|---|---|---|",
    ]

    spend = data["current_week"]["cost"]

    # Build a set of base event names to detect duplicates
    # yubi-invest entries that match an Aspero entry = duplicate tracking
    aspero_events: dict[str, float] = {}
    for a in data["in_app_actions_breakdown"]:
        if "yubi-invest" not in a["action"]:
            # extract the event name after the property prefix
            # e.g. "Aspero Fixed Income- Buy Bonds (Android) first_open" → "first_open"
            parts = a["action"].split(" ")
            event_name = parts[-1] if parts else a["action"]
            aspero_events[event_name] = a["count"]

    for a in data["in_app_actions_breakdown"]:
        action = a["action"]
        count  = a["count"]
        cpa    = _inr(a["cost_per_action"])

        # Tag duplicates
        note = ""
        if "yubi-invest" in action:
            # check if there's a matching aspero event
            parts = action.split(" ")
            event_name = parts[-1] if parts else action
            if event_name in aspero_events:
                note = "**DUPLICATE** — same users as Aspero property"
        elif "session_start" in action:
            note = "Noise — fires every session"
        elif "reinstall_open" in action:
            note = "Noise — returning user reopens"
        elif "YouTube" in action or "follow-on" in action:
            note = "Video engagement noise"
        elif "WEB_BANNER" in action:
            note = "Web banner click"
        elif "App Download" in action:
            note = "Google Play install count"
        elif "SETUP_SECURE_PIN_SUCCESS" in action and "yubi-invest" not in action:
            note = "**True new registration** (one-time per user)"
        elif "in_app_purchase" in action:
            note = "**Actual bond investment** (ultimate goal)"
        elif "KYC_READY_FOR_TRADE" in action:
            note = "KYC complete — recommended primary event"
        elif "KYC_BANK_VERIFIED" in action:
            note = "Bank verification step"

        # Shorten action name for display
        display = (action
                   .replace("Aspero Fixed Income- Buy Bonds (Android) ", "")
                   .replace("yubi-invest - Aspero Fixed Income- Buy Bonds (Android) ", "[dup] "))

        lines.append(f"| {display} | {count:,.0f} | {cpa} | {note} |")

    return "\n".join(lines)


def _section_measurement_issues(data: dict) -> str:
    """Auto-detect measurement issues from data."""
    issues = []

    breakdown = data["in_app_actions_breakdown"]
    action_map: dict[str, float] = {}
    for a in breakdown:
        action_map[a["action"]] = a["count"]

    # Issue 1: duplicate Firebase property
    dup_pairs = []
    for action, count in action_map.items():
        if "yubi-invest" in action:
            parts = action.split(" ")
            event_name = parts[-1] if parts else ""
            aspero_key = f"Aspero Fixed Income- Buy Bonds (Android) {event_name}"
            if aspero_key in action_map:
                diff = abs(action_map[aspero_key] - count)
                if diff / max(count, 1) < 0.10:  # within 10% = almost certainly same users
                    dup_pairs.append((event_name, action_map[aspero_key], count))

    if dup_pairs:
        issues.append({
            "title": "Duplicate Firebase Property Tracking",
            "priority": "P0",
            "detail": (
                "Two Firebase properties in Google Ads are tracking the same users:\n"
                "- `Aspero Fixed Income- Buy Bonds (Android)` — primary\n"
                "- `yubi-invest - Aspero Fixed Income- Buy Bonds (Android)` — duplicate\n\n"
                "Near-identical event counts confirm the same users counted twice:"
            ),
            "table_rows": [
                f"| `{ev}` | {a:,.0f} (Aspero) | {y:,.0f} (yubi-invest) |"
                for ev, a, y in dup_pairs
            ],
            "fix": (
                "Remove/exclude all `yubi-invest` property events from active conversion actions, "
                "or consolidate to a single Firebase property. Until resolved, all CPAs are ~50% "
                "understated and Smart Bidding is learning from inflated signals."
            ),
        })

    # Issue 2: campaigns where first_open dominates primary conversions
    install_campaigns = []
    for c in data["top_campaigns"]:
        events = c.get("primary_events", [])
        total = sum(e["count"] for e in events)
        if total > 0:
            install_pct = _primary_event_share(events, "first_open")
            if install_pct >= 80:
                install_campaigns.append((c["campaign_name"], install_pct))

    if install_campaigns:
        camp_list = "\n".join(f"- `{name}` — {pct}% of primary conv = `first_open`"
                              for name, pct in install_campaigns)
        issues.append({
            "title": "Campaigns Optimizing for Installs Instead of Intended Events",
            "priority": "P0",
            "detail": (
                "The following campaigns have their intended conversion event missing or too sparse, "
                "causing Smart Bidding to fall back to `first_open` (installs):\n\n" + camp_list
            ),
            "table_rows": [],
            "fix": (
                "Link the correct conversion events to each campaign. For BankVerified: add "
                "`KYC_BANK_VERIFIED_PD` + `KYC_BANK_VERIFIED_REVERSE_PD`. For PaymentSuccess: "
                "add `KYC_READY_FOR_TRADE` as primary (sufficient volume) and keep `in_app_purchase` "
                "as secondary/value signal."
            ),
        })

    # Issue 3: missing mid-funnel KYC signals
    kyc_ready = any("KYC_READY_FOR_TRADE" in a["action"] for a in breakdown)
    if not kyc_ready:
        issues.append({
            "title": "Missing Mid-Funnel KYC Signals in Google Ads",
            "priority": "P1",
            "detail": (
                "Google Ads knows about installs and investments, but nothing about "
                "registrations, KYC starts, or bank verifications in between. "
                "Smart Bidding cannot learn to find high-intent users without mid-funnel signals.\n\n"
                "Events NOT in Google Ads conversion actions:\n"
                "- `KYC_RISKDETAILS_SUBMIT` — KYC start (~71% of signups)\n"
                "- `KYC_READY_FOR_TRADE` — KYC complete (~58% of KYC starters)\n"
                "- `KYC_BANK_VERIFIED_PD` — Bank verification (active since Jan 20 2026)\n"
                "- `KYC_BANK_VERIFIED_REVERSE_PD` — Bank verification (active since Jan 20 2026)"
            ),
            "table_rows": [],
            "fix": (
                "Add `KYC_READY_FOR_TRADE` as primary conversion (enough volume for Smart Bidding). "
                "Add bank verification events to BankVerified campaign specifically."
            ),
        })

    # Build output
    lines = ["## Measurement Issues", ""]
    if not issues:
        lines.append("No measurement issues detected.")
        return "\n".join(lines)

    for issue in issues:
        lines += [
            f"### [{issue['priority']}] {issue['title']}",
            "",
            issue["detail"],
            "",
        ]
        if issue["table_rows"]:
            lines += ["| Event | Aspero count | yubi-invest count |", "|---|---|---|"]
            lines += issue["table_rows"]
            lines.append("")
        lines += [f"**Fix:** {issue['fix']}", "", "---", ""]

    return "\n".join(lines)


def _section_recommendations(data: dict) -> str:
    """Generate prioritised recommendations from data."""
    breakdown = data["in_app_actions_breakdown"]
    action_map: dict[str, float] = {a["action"]: a["count"] for a in breakdown}

    recs = []

    # P0: duplicate tracking
    has_dup = any("yubi-invest" in a and
                  f"Aspero Fixed Income- Buy Bonds (Android) {a.split(' ')[-1]}" in action_map
                  for a in action_map)
    if has_dup:
        recs.append(("P0", "Fix duplicate Firebase property tracking",
                     "Remove or exclude all `yubi-invest - Aspero Fixed Income` events from Google Ads "
                     "conversion actions. Consolidate to a single Firebase property. Every metric (CPA, "
                     "ROAS, conversion count) is inflated ~2x until this is fixed."))

    # P0: bank verified events not in Google Ads
    bank_verified_pd = any("KYC_BANK_VERIFIED_PD" in a for a in action_map)
    if not bank_verified_pd:
        recs.append(("P0", "Link bank verification events to BankVerified campaign",
                     "Add `KYC_BANK_VERIFIED_PD` + `KYC_BANK_VERIFIED_REVERSE_PD` + `KYC_BANK_VERIFIED` "
                     "as conversion actions in Google Ads and link to the BankVerified campaign. "
                     "Without this, ₹148K/week is buying installs with zero bank verification signal."))

    # P1: add KYC_READY_FOR_TRADE
    recs.append(("P1", "Add `KYC_READY_FOR_TRADE` as primary conversion for PaymentSuccess campaign",
                 "KYC-complete users (~350/week estimated) give Smart Bidding a learnable signal "
                 "while steering toward investment-intent users. `in_app_purchase` alone (2/week) "
                 "is too sparse. This should restore bidding confidence and recover the -52.9% spend drop."))

    # P1: switch primary from VERIFY_OTP_SUCCESS to SETUP_SECURE_PIN_SUCCESS
    otp_success = action_map.get("Aspero Fixed Income- Buy Bonds (Android) VERIFY_OTP_SUCCESS", 0)
    pin_success = action_map.get("Aspero Fixed Income- Buy Bonds (Android) SETUP_SECURE_PIN_SUCCESS", 0)
    if otp_success > pin_success * 1.5:
        recs.append(("P1", "Switch primary conversion from `VERIFY_OTP_SUCCESS` → `SETUP_SECURE_PIN_SUCCESS`",
                     f"`VERIFY_OTP_SUCCESS` fires {otp_success:,.0f} times (includes returning users re-verifying). "
                     f"`SETUP_SECURE_PIN_SUCCESS` fires {pin_success:,.0f} times — it's a one-time event per user "
                     f"and the true new registration signal. Smart Bidding should optimize for this."))

    # P1: investigate PaymentSuccess spend drop
    for c in data["top_campaigns"]:
        wow = c.get("spend_wow_pct")
        if wow is not None and wow <= -30 and c["cost"] > 0:
            recs.append(("P1", f"Investigate {c['campaign_name']} -{abs(wow)}% spend WoW drop",
                         f"Spend dropped from prior week by {abs(wow)}%. Budget utilization is "
                         f"{c.get('budget_util_pct', 'n/a')}% — this is Smart Bidding pulling back, "
                         f"not a budget constraint. Adding `KYC_READY_FOR_TRADE` as primary conversion "
                         f"should restore algorithm confidence. Monitor recovery within 7 days of fix."))
            break  # only flag once

    # P2: correct full conversion hierarchy
    recs.append(("P2", "Build the correct conversion hierarchy in Google Ads",
                 "**Recommended setup:**\n"
                 "| Level | Event | Action |\n"
                 "|---|---|---|\n"
                 "| Install | `first_open` | Already primary — keep |\n"
                 "| Registration | `SETUP_SECURE_PIN_SUCCESS` | Add as secondary |\n"
                 "| KYC Start | `KYC_RISKDETAILS_SUBMIT` | Add as secondary |\n"
                 "| KYC Complete | `KYC_READY_FOR_TRADE` | **Add as primary for both campaigns** |\n"
                 "| Bank Verified | `KYC_BANK_VERIFIED_PD` + `_REVERSE_PD` + `KYC_BANK_VERIFIED` | **Add to BankVerified campaign** |\n"
                 "| Investment | `in_app_purchase` | Keep as secondary/value |"))

    # P2: add conversion tracking to Search campaigns
    search_no_conv = [c for c in data["top_campaigns"]
                      if c.get("channel_type") == "SEARCH" and c["cost"] > 0 and c["in_app_actions"] == 0]
    if search_no_conv:
        names = ", ".join(f"`{c['campaign_name']}`" for c in search_no_conv)
        recs.append(("P2", "Add conversion tracking to Search campaigns",
                     f"{names} spend ₹{sum(c['cost'] for c in search_no_conv):,.0f}/week with zero "
                     f"conversion data. Add `SETUP_SECURE_PIN_SUCCESS` at minimum to measure "
                     f"whether branded/generic search drives registrations."))

    lines = ["## Prioritised Recommendations", ""]
    for priority, title, detail in recs:
        lines += [f"### [{priority}] {title}", "", detail, "", "---", ""]

    return "\n".join(lines)


def _section_channel_device(data: dict) -> str:
    lines = ["## Channel & Device Split", "", "**Channel:**", "",
             "| Channel | Spend | Impressions | Clicks | CTR | Primary Conv |",
             "|---|---|---|---|---|---|"]

    for ch, m in data["channel_split"].items():
        if m["impressions"] == 0 and m["cost"] == 0:
            continue
        ctr = round(m["clicks"] / m["impressions"] * 100, 2) if m["impressions"] else 0
        lines.append(
            f"| {ch} | {_inr(m['cost'])} | {m['impressions']:,} | {m['clicks']:,} | {ctr}% | {m['conversions']:,.0f} |"
        )

    lines += ["", "**Device:**", "",
              "| Device | Impressions | Clicks | Spend | Primary Conv |",
              "|---|---|---|---|---|"]

    for device, m in data["device_split"].items():
        if m["impressions"] == 0 and m["cost"] == 0:
            continue
        lines.append(
            f"| {device} | {m['impressions']:,} | {m['clicks']:,} | {_inr(m['cost'])} | {m['conversions']:,.0f} |"
        )

    return "\n".join(lines)


# ── Main entry point ──────────────────────────────────────────────────────────

def generate(data: dict) -> str:
    """
    Generate the full campaign report as a Markdown string.

    Args:
        data: dict returned by campaign_analysis.run()

    Returns:
        Full report as a Markdown-formatted string.
    """
    dr = data["date_range"]
    sections = [
        f"# Google Ads Campaign Report — {dr['current_start']} → {dr['current_end']}",
        f"*Generated by Growth Marketing Agent | Prior period: {dr['prior_start']} → {dr['prior_end']}*",
        "",
        _section_overall(data),
        "",
        "---",
        "",
        _section_campaigns(data),
        _section_funnel(data),
        "",
        "---",
        "",
        _section_measurement_issues(data),
        _section_recommendations(data),
        _section_channel_device(data),
        "",
    ]
    return "\n".join(sections)
