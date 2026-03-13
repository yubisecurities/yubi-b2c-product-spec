"""
Slack Block Kit formatter and webhook sender.

5-section report:
  1. Header — period, health, registration summary, WoW
  2. Stage 1 · Signin → OTP Verified   (6-step funnel + platform breakdown)
  3. Stage 2 · Email Verification       (6-step funnel — new users only)
  4. Stage 3 · PIN Setup                (3-step funnel — new users only)
  5. Device Quality                     (tier table: Low/Mid/Premium Android, iOS, Web)
  6. Insights, Alerts & Recommendations
"""

import requests
from datetime import datetime
from typing import Dict, List

_STATUS_ICON  = {"healthy": "✅", "warning": "🟡", "critical": "🔴"}
_STATUS_LABEL = {"healthy": "All Good", "warning": "Needs Attention", "critical": "Action Required"}
_TIER_ICON    = {"healthy": "✅", "warning": "⚠️", "alert": "🔴"}
_PLAT_ICON    = {"healthy": "✅", "warning": "⚠️", "alert": "🔴"}
_WOW_ARROW    = lambda pct: "📈" if pct > 2 else ("📉" if pct < -2 else "→")


# ---------------------------------------------------------------------------
# Builder
# ---------------------------------------------------------------------------

def build_message(
    period_label:        str,
    stage1_funnel:       List[Dict],
    stage2_funnel:       List[Dict],
    stage3_funnel:       List[Dict],
    platform_insights:   Dict[str, Dict],
    device_tier_insights: Dict[str, Dict],
    wow:                 Dict[str, Dict],
    alerts:              List[str],
    recommendations:     List[str],
    health:              str,
) -> Dict:
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
    reg_step    = next((s for s in stage3_funnel if s.get("is_registration")), {})
    reg_count   = reg_step.get("count", 0)
    s1_top      = next((s for s in stage1_funnel if s["event"] == "SIGNIN_PAGE_VIEW"), {})
    s1_sessions = s1_top.get("count", 0)

    wow_reg   = wow.get("SETUP_SECURE_PIN_SUCCESS", {})
    wow_pct   = wow_reg.get("pct_change", 0)
    wow_arrow = _WOW_ARROW(wow_pct)

    blocks.append({
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": (
                f"{_STATUS_ICON[health]}  *{_STATUS_LABEL[health]}*\n"
                f"*{reg_count:,}* new registrations  "
                f"{wow_arrow} *{wow_pct:+.1f}%* WoW  |  "
                f"{s1_sessions:,} sessions at top of funnel"
            ),
        },
    })
    blocks.append({"type": "divider"})

    # ── STAGE 1 ───────────────────────────────────────────────────────────
    blocks.append(_md_section("*📱 Stage 1 · Signin → OTP Verified*"))
    blocks.append(_md_section(_funnel_lines(stage1_funnel)))

    # Platform breakdown as fields
    platform_fields = []
    for platform in ["Android", "iOS", "Web"]:
        data  = platform_insights.get(platform, {})
        icon  = _PLAT_ICON.get(data.get("status", "healthy"), "✅")
        delta = data.get("delta_from_baseline", 0)
        platform_fields.append({
            "type": "mrkdwn",
            "text": (
                f"*{platform}*  {icon}\n"
                f"{data.get('views', 0):,} sessions → "
                f"{data.get('verified', 0):,} verified\n"
                f"*{data.get('conversion', 0)}%*  "
                f"({delta:+.1f}pp vs {data.get('baseline', 0)}% baseline)"
            ),
        })
    blocks.append({"type": "section", "fields": platform_fields})
    blocks.append({"type": "divider"})

    # ── STAGE 2 ───────────────────────────────────────────────────────────
    blocks.append(_md_section("*📧 Stage 2 · Email Verification  ·  New Users Only*"))
    blocks.append(_md_section(_funnel_lines(stage2_funnel)))
    blocks.append({"type": "divider"})

    # ── STAGE 3 ───────────────────────────────────────────────────────────
    blocks.append(_md_section("*🔐 Stage 3 · PIN Setup  ·  New Users Only*"))
    blocks.append(_md_section(_funnel_lines(stage3_funnel)))
    blocks.append({"type": "divider"})

    # ── DEVICE QUALITY ────────────────────────────────────────────────────
    blocks.append(_md_section(
        "*📲 Device Quality  ·  Email Verify → Registration  ·  New Users Only  ·  Last 7 Days*"
    ))
    blocks.append(_md_section(_device_tier_table(device_tier_insights)))
    blocks.append({"type": "divider"})

    # ── WEEK-OVER-WEEK ────────────────────────────────────────────────────
    wow_lines = ["*📆 Week-over-Week  ·  vs prior 7 days*\n"]
    _WOW_EVENT_LABELS = {
        "SIGNIN_PAGE_VIEW":        "Signin Sessions",
        "VERIFY_OTP_SUCCESS":       "OTP Verified",
        "EMAIL_VERIFY_OTP_SUCCESS": "Email Verified",
        "SETUP_SECURE_PIN_SUCCESS": "Registrations ⭐",
    }
    for event, lbl in _WOW_EVENT_LABELS.items():
        w = wow.get(event)
        if not w:
            continue
        arrow  = _WOW_ARROW(w["pct_change"])
        wow_lines.append(
            f"  {arrow}  {lbl}:  "
            f"{w['previous']:,} → *{w['current']:,}*  "
            f"(*{w['pct_change']:+.1f}%*)"
        )
    blocks.append(_md_section("\n".join(wow_lines)))

    # ── ALERTS & RECOMMENDATIONS ──────────────────────────────────────────
    if alerts or recommendations:
        blocks.append({"type": "divider"})
        insight_lines = []
        if alerts:
            insight_lines.append("*🚨 Alerts*")
            insight_lines.extend(f"• {a}" for a in alerts)
        if recommendations:
            if alerts:
                insight_lines.append("")
            insight_lines.append("*💡 Recommendations*")
            insight_lines.extend(f"• {r}" for r in recommendations)
        blocks.append(_md_section("\n".join(insight_lines)))

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


def _funnel_lines(steps: List[Dict]) -> str:
    """Format funnel steps as aligned text lines."""
    lines = []
    for step in steps:
        count    = step["count"]
        pct_top  = step["pct_of_top"]
        step_pct = step["step_conv"]
        label    = step["label"]

        # Show step-to-step conversion for all steps after the first
        step_str = f"  ↓ {step_pct}%" if step_pct is not None and steps.index(step) > 0 else ""

        if step.get("is_registration"):
            lines.append(f"  ⭐  *{label}:*  *{count:,}*  ({pct_top}% of top){step_str}")
        elif step.get("is_key"):
            lines.append(f"  ✦  *{label}:*  *{count:,}*  ({pct_top}% of top){step_str}")
        else:
            lines.append(f"  {label}:  {count:,}  ({pct_top}%){step_str}")

    return "\n".join(lines)


def _device_tier_table(device_tier_insights: Dict[str, Dict]) -> str:
    """Format device tier data as a fixed-width Slack-friendly table."""
    if not device_tier_insights:
        return "_No device data available_"

    header = f"{'Tier':<20} {'Sessions':>8}  {'Registered':>10}  {'Conv':>6}  {'vs Target':>12}"
    sep    = "─" * 62
    lines  = [header, sep]

    for tier, data in device_tier_insights.items():
        icon  = _TIER_ICON.get(data["status"], "✅")
        delta = data["delta"]
        sign  = "+" if delta >= 0 else ""
        lines.append(
            f"{data['label']:<20} {data['entries']:>8,}  "
            f"{data['registrations']:>10,}  "
            f"{data['conversion']:>5.1f}%  "
            f"{icon} {sign}{delta:.1f}pp"
        )

    return "```\n" + "\n".join(lines) + "\n```"


# ---------------------------------------------------------------------------
# V2 — Compact milestone report
# ---------------------------------------------------------------------------

_SNAP_ICON = {"healthy": "✅", "warning": "⚠️", "critical": "🔴"}

def _wow_direction(pct: float) -> str:
    """Return ↑/↓/→ prefix string with the percentage."""
    if pct > 2:
        return f"↑{abs(pct):.1f}%"
    if pct < -2:
        return f"↓{abs(pct):.1f}%"
    return f"→{abs(pct):.1f}%"


def build_message_v2(
    period_label:       str,
    device_table:       List[Dict],
    cur_otp:            int,
    cur_email_page:     int,
    cur_email_otp:      int,
    cur_email_sso:      int,
    cur_signup:         int,
    wow:                Dict[str, Dict],
    yesterday_snapshot: Dict,
    alerts:             List[str],
    wins:               List[str],
    health:             str,
) -> Dict:
    """
    Compact 4-section Slack report matching screenshot format:
      1. Header + registration summary
      2. Yesterday Snapshot  |  7-Day Trend
      3. Device Tier Table
      4. Needs Attention  |  Wins
    """
    blocks = []
    now     = datetime.utcnow()
    weekday = now.strftime("%a")
    date    = now.strftime("%b %-d")

    cur_email_total = cur_email_otp + cur_email_sso

    # ── HEADER ────────────────────────────────────────────────────────────
    blocks.append({
        "type": "header",
        "text": {
            "type": "plain_text",
            "text": f"📊 Aspero Funnel · {weekday} {date}",
            "emoji": True,
        },
    })

    # ── SIGNUP SUMMARY ────────────────────────────────────────────────────
    wow_reg = wow.get("signup", {})
    wow_dir = _wow_direction(wow_reg.get("pct_change", 0))
    blocks.append(_md_section(
        f"{_STATUS_ICON[health]}  *Signups: {cur_signup:,}*  ({wow_dir} vs prior 7d)"
    ))
    blocks.append({"type": "divider"})

    # ── YESTERDAY SNAPSHOT + 7-DAY TREND (side by side) ───────────────────
    snap = yesterday_snapshot
    s_reg  = snap.get("registrations", {})
    s_otp  = snap.get("otp_verified",  {})
    s_eml  = snap.get("email_conv",    {})

    snap_lines = [
        "*Yesterday Snapshot*",
        f"• Signups:      *{s_reg.get('value', 0):,}*\n"
        f"  7d avg: {int(s_reg.get('avg', 0)):,}/day  {_SNAP_ICON.get(s_reg.get('status','healthy'), '✅')}",
        f"• OTP Verified: *{s_otp.get('value', 0):,}*\n"
        f"  7d avg: {int(s_otp.get('avg', 0)):,}/day  {_SNAP_ICON.get(s_otp.get('status','healthy'), '✅')}",
        f"• Email Conv:   *{s_eml.get('value', 0)}%*\n"
        f"  7d avg: {s_eml.get('avg', 0)}%  {_SNAP_ICON.get(s_eml.get('status','healthy'), '✅')}",
    ]

    _WOW_LABELS = [
        ("otp",    "OTP Verified  "),
        ("email",  "Email Verified"),
        ("signup", "Signups       "),
    ]
    trend_lines = ["*📋 7-Day Trend*"]
    for key, lbl in _WOW_LABELS:
        w = wow.get(key, {})
        if not w:
            continue
        trend_lines.append(
            f"• {lbl}:  {w['previous']:,} → *{w['current']:,}*  "
            f"({_wow_direction(w['pct_change'])})"
        )

    blocks.append({
        "type": "section",
        "fields": [
            {"type": "mrkdwn", "text": "\n".join(snap_lines)},
            {"type": "mrkdwn", "text": "\n".join(trend_lines)},
        ],
    })
    blocks.append({"type": "divider"})

    # ── DEVICE TIER TABLE ─────────────────────────────────────────────────
    blocks.append(_md_section(
        "*Milestone Funnel by Device Tier  ·  Last 7 Days*\n"
        "_Mob. Verif = new users (EMAIL_PAGE_VIEW)  ·  "
        "Em% = email completion rate  ·  "
        "PIN% = email verified → signup_"
    ))
    blocks.append(_md_section(
        _milestone_table(device_table, cur_email_page, cur_email_total, cur_signup)
    ))
    blocks.append({"type": "divider"})

    # ── NEEDS ATTENTION + WINS ────────────────────────────────────────────
    if alerts:
        alert_lines = ["*Needs Attention*"]
        alert_lines.extend(f"• {a}" for a in alerts)
        blocks.append(_md_section("\n".join(alert_lines)))

    if wins:
        win_lines = ["*Wins*"]
        win_lines.extend(f"• {w}" for w in wins)
        blocks.append(_md_section("\n".join(win_lines)))

    if not alerts and not wins:
        blocks.append(_md_section("_No alerts or notable wins this period._"))

    # ── FOOTER ────────────────────────────────────────────────────────────
    blocks.append({
        "type": "context",
        "elements": [{
            "type": "mrkdwn",
            "text": (
                f"Amplitude Project 506002  ·  "
                f"Generated {now.strftime('%Y-%m-%d %H:%M UTC')}"
            ),
        }],
    })

    return {"blocks": blocks}


def _milestone_table(
    device_table:   List[Dict],
    cur_email_page: int,   # Mobile Verified = EMAIL_PAGE_VIEW (new users)
    cur_email:      int,   # Email ✓ combined (OTP + SSO paths)
    cur_signup:     int,
) -> str:
    """
    Fixed-width device tier × milestone table for Slack code block.

    Columns: Tier | Mob. Verif | Email ✓ | Signup | Em% | PIN%
      Mob. Verif = EMAIL_PAGE_VIEW  (new users — 99.5% match with first-time OTP)
      Email ✓    = EMAIL_VERIFY_OTP_SUCCESS + SSO_VERIFICATION_SUCCESS combined
      Em%        = Email ✓ / Mob. Verif  (email completion rate for new users)
      PIN%       = Signup / Email ✓      (email-verified → signup)
    """
    if not device_table:
        return "_No device data available_"

    C_TIER = 16
    C_MOB  =  10  # Mob. Verif
    C_EML  =   8  # Email ✓
    C_PIN  =   7  # Signup
    C_EM   =   7  # Em%
    C_E2P  =   7  # PIN%
    S      = "  "

    def _fmt_row(label, mob, eml, pin, em_pct, e2p_pct):
        return (
            f"{label:<{C_TIER}}"
            f"{S}{mob:>{C_MOB},}"
            f"{S}{eml:>{C_EML},}"
            f"{S}{pin:>{C_PIN},}"
            f"{S}{f'{em_pct}%':>{C_EM}}"
            f"{S}{f'{e2p_pct}%':>{C_E2P}}"
        )

    col_total = C_TIER + (C_MOB + C_EML + C_PIN + C_EM + C_E2P) + len(S) * 5
    sep    = "─" * col_total
    header = (
        f"{'Tier':<{C_TIER}}"
        f"{S}{'Mob. Verif':>{C_MOB}}"
        f"{S}{'Email ✓':>{C_EML}}"
        f"{S}{'Signup':>{C_PIN}}"
        f"{S}{'Em%':>{C_EM}}"
        f"{S}{'PIN%':>{C_E2P}}"
    )

    lines = [header, sep]
    for row in device_table:
        lines.append(_fmt_row(
            row["label"],
            row["email_page"],
            row["email_total"],
            row["signup"],
            row["newuser_to_email_pct"],
            row["email_to_signup_pct"],
        ))

    em_total  = round(cur_email      / cur_email_page * 100, 1) if cur_email_page > 0 else 0.0
    e2p_total = round(cur_signup     / cur_email      * 100, 1) if cur_email      > 0 else 0.0
    lines.append(sep)
    lines.append(_fmt_row("TOTAL", cur_email_page, cur_email, cur_signup, em_total, e2p_total))

    has_unknown = any(r["tier"] == "unknown_android" for r in device_table)
    table_text  = "```\n" + "\n".join(lines) + "\n```"
    if has_unknown:
        table_text += (
            "\n_† Unknown Android: device model string not matched by our classifier. "
            "Most likely Low tier — flagship (Galaxy S, Pixel, OnePlus flagship) and popular "
            "mid-range (Galaxy A/M, Redmi Note, Realme) models are explicitly listed. "
            "If a device doesn't match any known pattern, it is almost certainly not a premium "
            "or mid-range device._"
        )
    return table_text


# ---------------------------------------------------------------------------
# Executive briefing — plain mrkdwn, verdict-first, ~18 lines
# Audience: CEO, CPO, CMO, core leadership
# Answers: growing or declining? audience quality? what to do today?
# ---------------------------------------------------------------------------

def build_exec_report(
    period_label:       str,
    cur_signup:         int,
    wow:                Dict[str, Dict],
    prev_prev_signup:   int,
    yesterday_snapshot: Dict,
    device_table:       List[Dict],
    sso_pct:            float,
    kyc_start_pct:      float,
    kyc_done_pct:       float,
    kyc_start_wow_pp:   float,
    kyc_done_wow_pp:    float,
    kyc_cohort_signups: int,
    kyc_v2_recent:      bool,
    alerts:             List[str],
    wins:               List[str],
    health:             str,
    generated_at:       str,
) -> Dict:
    """
    Executive daily briefing as plain mrkdwn text (not Block Kit).
    Posted first to the same channel so it sits above the detailed report.
    Pure Python — no LLM required.
    """
    now      = datetime.utcnow()
    weekday  = now.strftime("%a")
    date_str = now.strftime("%b %-d")

    _STATUS_EMOJI = {"healthy": "🟢", "warning": "🟡", "critical": "🔴"}
    status_emoji  = _STATUS_EMOJI.get(health, "🟡")

    # ── Signup headline ───────────────────────────────────────────────────
    wow_reg  = wow.get("signup", {})
    wow_pct  = wow_reg.get("pct_change", 0)
    prev_signup = wow_reg.get("previous", 0)

    if wow_pct > 2:
        wow_str = f"↑{abs(wow_pct):.1f}% WoW"
    elif wow_pct < -2:
        wow_str = f"↓{abs(wow_pct):.1f}% WoW"
    else:
        wow_str = "→ flat WoW"

    # Consecutive trend using prior-prior week
    prev_wow_pct = (
        round((prev_signup - prev_prev_signup) / prev_prev_signup * 100, 1)
        if prev_prev_signup > 0 else 0
    )
    if wow_pct <= -5 and prev_wow_pct <= -5:
        trajectory = "2nd consecutive weekly decline"
    elif wow_pct >= 5 and prev_wow_pct >= 5:
        trajectory = "2nd consecutive week of growth"
    elif wow_pct <= -5 and prev_wow_pct >= 5:
        trajectory = "reversal from last week's growth"
    elif wow_pct >= 5 and prev_wow_pct <= -5:
        trajectory = "reversal from last week's decline"
    else:
        trajectory = "broadly stable"

    # Yesterday vs daily average
    s_reg       = yesterday_snapshot.get("registrations", {})
    yest_val    = s_reg.get("value", 0)
    yest_avg    = int(s_reg.get("avg", 0))
    yest_status = s_reg.get("status", "healthy")
    if yest_status == "healthy":
        yest_note = f"Yesterday's *{yest_val:,}* was above the *{yest_avg:,}/day* average — pace may be stabilizing."
    elif yest_status == "warning":
        yest_note = f"Yesterday's *{yest_val:,}* was below the *{yest_avg:,}/day* average — trend continuing."
    else:
        yest_note = f"Yesterday's *{yest_val:,}* was well below the *{yest_avg:,}/day* average — decline accelerating."

    # ── Audience quality (1 line) ─────────────────────────────────────────
    total_signup = sum(r["signup"] for r in device_table)
    premium_ios  = sum(r["signup"] for r in device_table
                       if r["tier"] in ("premium_android", "ios"))
    if total_signup > 0:
        pi_pct = round(premium_ios / total_signup * 100, 1)
        if pi_pct >= 50:
            audience_line = f"Target audience (iOS + Premium Android) = *{pi_pct}%* of signups — acquisition quality healthy."
        elif pi_pct >= 35:
            audience_line = f"Target audience (iOS + Premium Android) = *{pi_pct}%* of signups — channel mix worth watching."
        else:
            audience_line = f"⚠️ Target audience (iOS + Premium Android) = only *{pi_pct}%* of signups — low-LTV devices dominating, review acquisition channels."
    else:
        audience_line = ""

    # ── Assemble report ───────────────────────────────────────────────────
    lines = [
        f"{status_emoji} *ASPERO DAILY · {weekday} {date_str}*",
        "",
        f"*Signups: {cur_signup:,}* — {wow_str}, {trajectory}.",
        yest_note,
    ]

    if audience_line:
        lines.append(audience_line)

    # ── KYC block ─────────────────────────────────────────────────────────
    def _wow_pp(pp: float) -> str:
        if pp > 0.5:
            return f"↑{abs(pp):.1f}pp WoW"
        if pp < -0.5:
            return f"↓{abs(pp):.1f}pp WoW"
        return "→ flat WoW"

    kyc_lines = ["", "*KYC (7-day cohort)*"]
    if kyc_cohort_signups > 0:
        kyc_lines.append(
            f"*{kyc_start_pct}%* of last week's {kyc_cohort_signups:,} signups started KYC "
            f"({_wow_pp(kyc_start_wow_pp)})."
        )
        if kyc_start_pct > 0:
            kyc_lines.append(
                f"Of those, *{kyc_done_pct}%* completed within 7 days "
                f"({_wow_pp(kyc_done_wow_pp)})."
            )
        if kyc_v2_recent:
            kyc_lines.append(
                "_KYC flow updated Mar 10 (wet signature step added, 8→9 steps) — "
                "completion dip this week may be structural, not a bug._"
            )
    else:
        kyc_lines.append("_KYC data not yet available for this cohort window._")

    lines.extend(kyc_lines)

    lines.append("")
    lines.append("━━━━━━━━━━━━━━━")

    # Top 2 alerts only
    top_alerts = alerts[:2]
    if top_alerts:
        lines.append("*Needs Attention*")
        for a in top_alerts:
            lines.append(f"• {a}")

    # Top 2 wins only
    top_wins = wins[:2]
    if top_wins:
        if top_alerts:
            lines.append("")
        lines.append("*Wins*")
        for w in top_wins:
            lines.append(f"• {w}")

    if not top_alerts and not top_wins:
        lines.append("_No urgent actions — funnel running normally._")

    lines.append("━━━━━━━━━━━━━━━")
    lines.append(f"_Amplitude 506002 · {generated_at} IST_")

    return {"text": "\n".join(lines)}
