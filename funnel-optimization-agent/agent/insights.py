"""
Insight generation — converts raw Amplitude counts into:
  - Per-stage funnel conversion rates (3 stages)
  - Platform health for Stage 1
  - Device tier analysis
  - Week-over-week deltas
  - Anomaly alerts and recommendations
"""

from typing import Dict, List
from config import (
    STAGE1_STEPS, STAGE2_STEPS, STAGE3_STEPS,
    FAILURE_EVENTS,
    PLATFORM_BASELINES,
    PLATFORM_ALERT_THRESHOLDS,
    PLATFORM_WARNING_THRESHOLDS,
    DEVICE_TIER_PATTERNS,
    DEVICE_TIER_BASELINES,
    DEVICE_TIER_LABELS,
)


# ---------------------------------------------------------------------------
# Funnel
# ---------------------------------------------------------------------------

def compute_funnel(event_counts: Dict[str, int], steps: List[Dict]) -> List[Dict]:
    """
    Annotate each step with:
      - count:       unique users at this step
      - pct_of_top:  % relative to the first step in `steps`
      - step_conv:   % conversion from the immediately preceding step
    """
    if not steps:
        return []

    top = event_counts.get(steps[0]["event"], 0)
    enriched = []

    for i, step in enumerate(steps):
        count      = event_counts.get(step["event"], 0)
        pct_of_top = round(count / top * 100, 1) if top > 0 else 0.0
        prev_count = enriched[i - 1]["count"] if i > 0 else count
        step_conv  = round(count / prev_count * 100, 1) if prev_count > 0 else 0.0

        enriched.append({
            **step,
            "count":      count,
            "pct_of_top": pct_of_top,
            "step_conv":  step_conv,
        })

    return enriched


# ---------------------------------------------------------------------------
# Platform (Stage 1 — SIGNIN_PAGE_VIEW → VERIFY_OTP_SUCCESS)
# ---------------------------------------------------------------------------

def compute_platform_insights(
    platform_funnel: Dict[str, Dict[str, int]],
) -> Dict[str, Dict]:
    """
    For each platform (Android / iOS / Web):
      - views, verified, conversion %
      - delta vs historical baseline
      - health status: healthy | warning | alert
    """
    results = {}

    for platform in ["Android", "iOS", "Web"]:
        steps    = platform_funnel.get(platform, {})
        views    = steps.get("SIGNIN_PAGE_VIEW", 0)
        verified = steps.get("VERIFY_OTP_SUCCESS", 0)
        conv     = round(verified / views * 100, 1) if views > 0 else 0.0

        baseline  = PLATFORM_BASELINES.get(platform, 50.0)
        alert_thr = PLATFORM_ALERT_THRESHOLDS.get(platform, 25.0)
        warn_thr  = PLATFORM_WARNING_THRESHOLDS.get(platform, 35.0)

        if conv < alert_thr:
            status = "alert"
        elif conv < warn_thr:
            status = "warning"
        else:
            status = "healthy"

        results[platform] = {
            "views":               views,
            "verified":            verified,
            "conversion":          conv,
            "baseline":            baseline,
            "delta_from_baseline": round(conv - baseline, 1),
            "status":              status,
            "steps":               steps,
        }

    return results


# ---------------------------------------------------------------------------
# Device tier
# ---------------------------------------------------------------------------

def classify_device_type(device_label: str) -> str:
    """
    Classify a device_type string into a tier bucket.
    Checks premium → mid → low to avoid mis-classifying high-end devices.
    """
    lower = device_label.lower()

    # Apple / web first
    if any(k in lower for k in ("iphone", "ipad", "ipod")):
        return "ios"
    if any(k in lower for k in ("windows", "mac", "linux", "chrome os", "chromebook")):
        return "web"

    # Android tiers — most specific first
    for tier in ("premium_android", "mid_android", "low_android"):
        if any(kw in lower for kw in DEVICE_TIER_PATTERNS[tier]):
            return tier

    # Known Android vendor but unmatched model → low_android
    # Premium and popular mid-range models are already enumerated above.
    # If a device doesn't match any pattern, it's likely an obscure/budget model.
    android_hints = (
        "samsung", "redmi", "xiaomi", "oneplus", "oppo", "vivo",
        "realme", "poco", "motorola", "moto", "asus", "lenovo",
        "huawei", "honor", "iqoo", "nothing",
    )
    if any(k in lower for k in android_hints):
        return "low_android"

    # Generic "android" string or unknown OEM → low_android
    return "low_android"


def compute_device_tier_insights(
    entries_by_device: Dict[str, int],    # SIGNIN_PAGE_VIEW by device_type
    regs_by_device:    Dict[str, int],    # SETUP_SECURE_PIN_SUCCESS by device_type
) -> Dict[str, Dict]:
    """
    Aggregate entries and registrations by device tier, compute conversion.
    Returns ordered dict: low → mid → premium → ios → web → other
    """
    tier_entries: Dict[str, int] = {}
    tier_regs:    Dict[str, int] = {}

    for device, count in entries_by_device.items():
        tier = classify_device_type(device)
        tier_entries[tier] = tier_entries.get(tier, 0) + count

    for device, count in regs_by_device.items():
        tier = classify_device_type(device)
        tier_regs[tier] = tier_regs.get(tier, 0) + count

    results = {}
    display_order = [
        "low_android", "mid_android", "premium_android",
        "ios", "web",
    ]

    for tier in display_order:
        entries = tier_entries.get(tier, 0)
        regs    = tier_regs.get(tier, 0)
        if entries == 0 and regs == 0:
            continue

        conv     = round(regs / entries * 100, 1) if entries > 0 else 0.0
        baseline = DEVICE_TIER_BASELINES.get(tier, 40.0)
        delta    = round(conv - baseline, 1)

        if conv < baseline * 0.6:
            status = "alert"
        elif conv < baseline * 0.85:
            status = "warning"
        else:
            status = "healthy"

        results[tier] = {
            "label":         DEVICE_TIER_LABELS.get(tier, tier),
            "entries":       entries,
            "registrations": regs,
            "conversion":    conv,
            "baseline":      baseline,
            "delta":         delta,
            "status":        status,
        }

    return results


# ---------------------------------------------------------------------------
# Week-over-week
# ---------------------------------------------------------------------------

def compute_wow(
    current:  Dict[str, int],
    previous: Dict[str, int],
) -> Dict[str, Dict]:
    """Return WoW delta for every event that appears in `current`."""
    wow: Dict[str, Dict] = {}

    for event, curr_val in current.items():
        prev_val   = previous.get(event, 0)
        delta      = curr_val - prev_val
        pct_change = round(delta / prev_val * 100, 1) if prev_val > 0 else 0.0

        wow[event] = {
            "current":    curr_val,
            "previous":   prev_val,
            "delta":      delta,
            "pct_change": pct_change,
        }

    return wow


# ---------------------------------------------------------------------------
# Alerts
# ---------------------------------------------------------------------------

def generate_alerts(
    stage1:               List[Dict],
    platform_insights:    Dict[str, Dict],
    device_tier_insights: Dict[str, Dict],
    failure_counts:       Dict[str, int],
    wow:                  Dict[str, Dict],
) -> List[str]:
    """Return human-readable alert strings, sorted 🔴 first then ⚠️."""
    alerts: List[str] = []

    # 1. Platform conversion alerts
    for platform, data in platform_insights.items():
        conv   = data["conversion"]
        base   = data["baseline"]
        delta  = data["delta_from_baseline"]
        if data["status"] == "alert":
            alerts.append(
                f"🔴 *{platform}* OTP conversion critically low: "
                f"*{conv}%*  (baseline {base}%, {delta:+.1f}pp)"
            )
        elif data["status"] == "warning":
            alerts.append(
                f"⚠️ *{platform}* OTP conversion below baseline: "
                f"*{conv}%*  (baseline {base}%, {delta:+.1f}pp)"
            )

    # 2. Device tier alerts
    for tier, data in device_tier_insights.items():
        if data["status"] == "alert":
            alerts.append(
                f"🔴 *{data['label']}* conversion critically low: "
                f"*{data['conversion']}%*  (target {data['baseline']}%, {data['delta']:+.1f}pp)"
            )
        elif data["status"] == "warning":
            alerts.append(
                f"⚠️ *{data['label']}* below target: "
                f"*{data['conversion']}%*  (target {data['baseline']}%, {data['delta']:+.1f}pp)"
            )

    # 3. High failure rates (>5% of SIGNIN_PAGE_VIEW)
    top = next((s["count"] for s in stage1 if s["event"] == "SIGNIN_PAGE_VIEW"), 0)
    if top > 0:
        for event in FAILURE_EVENTS:
            count = failure_counts.get(event, 0)
            rate  = round(count / top * 100, 1)
            if rate >= 5.0:
                label = event.replace("_", " ").title()
                alerts.append(
                    f"⚠️ High failure — *{label}*: "
                    f"{count:,} failures ({rate}% of sessions)"
                )

    # 4. Sharp WoW drop in registrations
    reg_wow = wow.get("SETUP_SECURE_PIN_SUCCESS", {})
    pct     = reg_wow.get("pct_change", 0)
    if pct <= -20:
        alerts.append(
            f"🔴 *Registrations down {pct:.1f}% WoW* — "
            f"{reg_wow.get('previous', 0):,} → {reg_wow.get('current', 0):,}"
        )
    elif pct <= -10:
        alerts.append(
            f"⚠️ *Registrations down {pct:.1f}% WoW* — "
            f"{reg_wow.get('previous', 0):,} → {reg_wow.get('current', 0):,}"
        )

    alerts.sort(key=lambda x: (0 if x.startswith("🔴") else 1))
    return alerts


# ---------------------------------------------------------------------------
# Recommendations
# ---------------------------------------------------------------------------

def generate_recommendations(
    stage1_steps:         List[Dict],
    stage2_steps:         List[Dict],
    device_tier_insights: Dict[str, Dict],
    platform_insights:    Dict[str, Dict],
) -> List[str]:
    """Return actionable recommendation strings based on biggest drop-offs."""
    recs: List[str] = []

    # Worst Stage 1 step drop
    worst_drop, worst_label = 0.0, ""
    for step in stage1_steps[1:]:
        drop = 100 - step["step_conv"]
        if drop > worst_drop:
            worst_drop = drop
            worst_label = step["label"]
    if worst_drop >= 20:
        recs.append(
            f"💡 Biggest Stage 1 drop at *{worst_label}* ({worst_drop:.0f}% fall-off) — "
            f"investigate UX or backend errors at this step"
        )

    # Stage 2 end-to-end completion
    if len(stage2_steps) >= 2:
        s2_top = stage2_steps[0]["count"]
        s2_bot = stage2_steps[-1]["count"]
        s2_conv = round(s2_bot / s2_top * 100, 1) if s2_top > 0 else 0
        if s2_conv < 70:
            recs.append(
                f"💡 Email verification completion *{s2_conv}%* — "
                f"reduce steps or auto-fill email OTP to improve this"
            )

    # Low Android traffic share vs conversion
    total_entries = sum(d["entries"] for d in device_tier_insights.values())
    low = device_tier_insights.get("low_android", {})
    if low and total_entries > 0:
        share = round(low["entries"] / total_entries * 100, 1)
        if share > 20 and low.get("status") in ("warning", "alert"):
            recs.append(
                f"💡 Low Android is *{share}%* of traffic but only "
                f"*{low['conversion']}%* conversion (target {low['baseline']}%) — "
                f"optimise bundle size and OTP timeout for budget devices"
            )

    # iOS vs Android gap
    ios_c = platform_insights.get("iOS", {}).get("conversion", 0)
    and_c = platform_insights.get("Android", {}).get("conversion", 0)
    if ios_c > 0 and and_c > 0 and (ios_c - and_c) > 15:
        recs.append(
            f"💡 iOS converts *{ios_c - and_c:.1f}pp higher* than Android "
            f"({ios_c}% vs {and_c}%) — Android OTP flow needs performance work"
        )

    return recs


# ---------------------------------------------------------------------------
# Overall health
# ---------------------------------------------------------------------------

def get_overall_health(
    platform_insights: Dict[str, Dict],
    wow:               Dict[str, Dict],
) -> str:
    """Return 'healthy' | 'warning' | 'critical'."""
    alert_count   = sum(1 for p in platform_insights.values() if p["status"] == "alert")
    warning_count = sum(1 for p in platform_insights.values() if p["status"] == "warning")
    reg_pct       = wow.get("SETUP_SECURE_PIN_SUCCESS", {}).get("pct_change", 0)

    if alert_count >= 2 or reg_pct <= -20:
        return "critical"
    if alert_count >= 1 or warning_count >= 2 or reg_pct <= -10:
        return "warning"
    return "healthy"


# ===========================================================================
# V2 — Compact device-tier milestone report
# ===========================================================================

def compute_device_funnel_table(
    otp_email_funnel: Dict[str, List],  # {device: [otp, email_otp, signup_otp_path]}
    otp_sso_funnel:   Dict[str, List],  # {device: [otp, email_sso, signup_sso_path]}
) -> List[Dict]:
    """
    Aggregate Funnel API results by device tier.

    Both dicts come from get_funnel_by_device_type(), so step[i+1] <= step[i].
    This guarantees Email→Signup conversion is always ≤ 100%.

    otp_email_funnel: OTP → EMAIL_VERIFY_OTP_SUCCESS → SETUP_SECURE_PIN_SUCCESS
    otp_sso_funnel:   OTP → SSO_VERIFICATION_SUCCESS  → SETUP_SECURE_PIN_SUCCESS
    """
    otp_t        : Dict[str, int] = {}
    email_otp_t  : Dict[str, int] = {}
    signup_otp_t : Dict[str, int] = {}

    for device, steps in otp_email_funnel.items():
        tier = classify_device_type(device)
        otp_t[tier]        = otp_t.get(tier, 0)        + (steps[0] if len(steps) > 0 else 0)
        email_otp_t[tier]  = email_otp_t.get(tier, 0)  + (steps[1] if len(steps) > 1 else 0)
        signup_otp_t[tier] = signup_otp_t.get(tier, 0) + (steps[2] if len(steps) > 2 else 0)

    email_sso_t  : Dict[str, int] = {}
    signup_sso_t : Dict[str, int] = {}

    for device, steps in otp_sso_funnel.items():
        tier = classify_device_type(device)
        email_sso_t[tier]  = email_sso_t.get(tier, 0)  + (steps[1] if len(steps) > 1 else 0)
        signup_sso_t[tier] = signup_sso_t.get(tier, 0) + (steps[2] if len(steps) > 2 else 0)

    display_order = [
        "low_android", "mid_android", "premium_android",
        "ios", "web",
    ]

    rows = []
    for tier in display_order:
        otp         = otp_t.get(tier, 0)
        email_otp   = email_otp_t.get(tier, 0)
        email_sso   = email_sso_t.get(tier, 0)
        email_total = email_otp + email_sso
        # signup = both paths combined; guaranteed ≤ email_total per path by funnel definition
        signup      = signup_otp_t.get(tier, 0) + signup_sso_t.get(tier, 0)

        if otp == 0 and email_total == 0 and signup == 0:
            continue

        otp_to_email    = round(email_total / otp         * 100, 1) if otp        > 0 else 0.0
        email_to_signup = round(signup      / email_total * 100, 1) if email_total > 0 else 0.0

        rows.append({
            "tier":                tier,
            "label":               DEVICE_TIER_LABELS.get(tier, tier),
            "otp":                 otp,
            "email_otp":           email_otp,
            "email_sso":           email_sso,
            "email_total":         email_total,
            "signup":              signup,
            "otp_to_email_pct":    otp_to_email,
            "email_to_signup_pct": email_to_signup,
        })

    return rows


def compute_wow_totals(
    cur_otp:    int, cur_email: int, cur_signup: int,
    prev_otp:   int, prev_email: int, prev_signup: int,
) -> Dict[str, Dict]:
    """Return WoW dict for the 3 key milestone totals."""
    def _delta(curr, prev):
        delta = curr - prev
        pct   = round(delta / prev * 100, 1) if prev > 0 else 0.0
        return {"current": curr, "previous": prev, "delta": delta, "pct_change": pct}

    return {
        "otp":    _delta(cur_otp,    prev_otp),
        "email":  _delta(cur_email,  prev_email),
        "signup": _delta(cur_signup, prev_signup),
    }


def generate_alerts_v2(
    wow:          Dict[str, Dict],
    device_table: List[Dict],
    sso_pct:      float,
) -> List[str]:
    """Alerts for the v2 compact report, informed by business context (business_context.md)."""
    alerts: List[str] = []

    # ── Registration WoW drop ─────────────────────────────────────────────
    reg = wow.get("signup", {})
    pct = reg.get("pct_change", 0)
    if pct <= -20:
        alerts.append(
            f"🔴 *Registrations down {abs(pct):.1f}% WoW* — "
            f"{reg.get('previous', 0):,} → {reg.get('current', 0):,}"
        )
    elif pct <= -10:
        alerts.append(
            f"⚠️ *Registrations down {abs(pct):.1f}% WoW* — "
            f"{reg.get('previous', 0):,} → {reg.get('current', 0):,}"
        )

    # ── Audience quality: Low+Mid Android dominating (target = Premium+iOS) ──
    total_otp       = sum(r["otp"] for r in device_table)
    low_mid_otp     = sum(r["otp"] for r in device_table
                          if r["tier"] in ("low_android", "mid_android", "other_android"))
    premium_ios_otp = sum(r["otp"] for r in device_table
                          if r["tier"] in ("premium_android", "ios"))
    if total_otp > 0:
        low_mid_pct     = round(low_mid_otp     / total_otp * 100, 1)
        premium_ios_pct = round(premium_ios_otp / total_otp * 100, 1)
        if low_mid_pct > 60:
            alerts.append(
                f"📊 Low & Mid Android = *{low_mid_pct}%* of signups — "
                f"target audience (Premium Android + iOS) only *{premium_ios_pct}%*. "
                f"Review acquisition channels for higher-intent users"
            )

    # ── Premium Android + iOS: Email→PIN must stay >90% (high-value users) ──
    for row in device_table:
        if row["tier"] not in ("premium_android", "ios"):
            continue
        if row["email_total"] < 5:
            continue
        e2s = row["email_to_signup_pct"]
        if e2s < 80:
            alerts.append(
                f"🔴 *{row['label']}* (target audience) Email→Signup only *{e2s}%* "
                f"— high-intent users dropping at PIN setup "
                f"({row['email_total']:,} email verified, {row['signup']:,} registered)"
            )
        elif e2s < 90:
            alerts.append(
                f"⚠️ *{row['label']}* (target audience) Email→Signup *{e2s}%* "
                f"— below 90% target for high-value users"
            )

    # ── Other tiers: Email→Signup anomalies ───────────────────────────────
    for row in device_table:
        if row["tier"] in ("premium_android", "ios"):
            continue
        if row["email_total"] < 10:
            continue
        if row["email_to_signup_pct"] < 70:
            alerts.append(
                f"⚠️ *{row['label']}* Email→Signup low: *{row['email_to_signup_pct']}%* "
                f"({row['email_total']:,} email verified, {row['signup']:,} registered)"
            )

    # ── Low Android new-user ratio ─────────────────────────────────────────
    for row in device_table:
        if row["tier"] == "low_android" and row["otp"] > 0:
            if row["otp_to_email_pct"] < 10:
                alerts.append(
                    f"💡 *Low Android* OTP→Email only *{row['otp_to_email_pct']}%* — "
                    f"mostly returning logins, negligible new user acquisition"
                )

    # ── SSO adoption note ─────────────────────────────────────────────────
    if sso_pct > 5:
        alerts.append(
            f"📈 *Google SSO: {sso_pct}%* of email verifications "
            f"(launched 7 days ago — target 40% within 30 days)"
        )

    alerts.sort(key=lambda x: (0 if x.startswith("🔴") else (1 if x.startswith("⚠️") else 2)))
    return alerts


def get_overall_health_v2(
    wow:          Dict[str, Dict],
    device_table: List[Dict],
) -> str:
    """Return 'healthy' | 'warning' | 'critical' for v2 report."""
    reg_pct = wow.get("signup", {}).get("pct_change", 0)

    # Critical if target audience (Premium+iOS) Email→PIN < 80%
    premium_ios_critical = any(
        r["email_to_signup_pct"] < 80 and r["email_total"] >= 5
        for r in device_table
        if r["tier"] in ("premium_android", "ios")
    )
    low_e2s_tiers = [
        r for r in device_table
        if r["email_total"] >= 10 and r["email_to_signup_pct"] < 70
    ]

    if reg_pct <= -20 or premium_ios_critical or len(low_e2s_tiers) >= 3:
        return "critical"
    if reg_pct <= -10 or len(low_e2s_tiers) >= 1:
        return "warning"
    return "healthy"


def compute_yesterday_snapshot(
    yest_otp:          int,
    yest_email_total:  int,
    yest_signup:       int,
    cur_otp:           int,
    cur_email_total:   int,
    cur_signup:        int,
) -> Dict:
    """
    Compare yesterday's metrics against the 7-day rolling average.
    Returns a dict with 'registrations', 'otp_verified', 'email_conv' keys,
    each containing: value, avg, status ('healthy'|'warning'|'critical').
    """
    avg_signup = cur_signup / 7
    avg_otp    = cur_otp    / 7
    avg_email_conv = round(cur_email_total / cur_otp * 100, 1) if cur_otp > 0 else 0

    yest_email_conv = round(yest_email_total / yest_otp * 100, 1) if yest_otp > 0 else 0

    def _status(val: float, avg: float) -> str:
        if avg == 0:
            return "healthy"
        ratio = val / avg
        return "healthy" if ratio >= 0.95 else ("warning" if ratio >= 0.82 else "critical")

    return {
        "registrations": {
            "value":  yest_signup,
            "avg":    round(avg_signup, 0),
            "status": _status(yest_signup, avg_signup),
        },
        "otp_verified": {
            "value":  yest_otp,
            "avg":    round(avg_otp, 0),
            "status": _status(yest_otp, avg_otp),
        },
        "email_conv": {
            "value":  yest_email_conv,
            "avg":    avg_email_conv,
            "status": _status(yest_email_conv, avg_email_conv),
        },
    }


def generate_wins_v2(
    wow:          Dict[str, Dict],
    device_table: List[Dict],
    sso_pct:      float,
) -> List[str]:
    """Positive signals worth calling out — informed by business context."""
    wins: List[str] = []

    # Registration WoW growth
    reg = wow.get("signup", {})
    if reg.get("pct_change", 0) >= 5:
        wins.append(
            f"Registrations up *{reg['pct_change']:+.1f}%* WoW "
            f"({reg['previous']:,} → {reg['current']:,})"
        )

    # SSO healthy adoption (launched recently)
    if sso_pct >= 15:
        wins.append(f"Google SSO at *{sso_pct}%* adoption — strong start since launch")

    # Premium Android or iOS holding strong Email→PIN
    for row in device_table:
        if row["tier"] in ("premium_android", "ios") and row["email_total"] >= 5:
            if row["email_to_signup_pct"] >= 90:
                wins.append(
                    f"*{row['label']}* Email→Signup at *{row['email_to_signup_pct']}%* "
                    f"— target audience completing registration well"
                )

    # Premium+iOS growing share of registrations
    total_signup    = sum(r["signup"] for r in device_table)
    premium_ios_reg = sum(r["signup"] for r in device_table
                          if r["tier"] in ("premium_android", "ios"))
    if total_signup > 0:
        pi_pct = round(premium_ios_reg / total_signup * 100, 1)
        if pi_pct >= 40:
            wins.append(
                f"Premium Android + iOS = *{pi_pct}%* of registrations "
                f"— strong target audience quality"
            )

    return wins
