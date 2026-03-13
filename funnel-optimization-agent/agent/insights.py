"""
Insight generation — converts raw Amplitude counts into:
  - Per-stage funnel conversion rates (3 stages)
  - Platform health for Stage 1
  - Device tier analysis
  - Week-over-week deltas
  - Anomaly alerts and recommendations
"""

import re
from datetime import date
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
    SSO_LAUNCH_DATE,
    KYC_STEP_LABELS,
    KYC_STEP_ORDER,
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

    Handles both marketing names ("Samsung Galaxy S22") and raw hardware model
    codes returned by the Amplitude API ("SM-S901B", "2201116TG", "RMX3511").

    Checks premium → mid → low to avoid mis-classifying high-end devices.
    """
    lower = device_label.lower()

    # Apple / web first
    if any(k in lower for k in ("iphone", "ipad", "ipod")):
        return "ios"
    if any(k in lower for k in ("windows", "mac", "linux", "chrome os", "chromebook")):
        return "web"

    # ── Hardware model code patterns (raw codes from Amplitude API) ───────
    # Samsung SM-* codes
    if re.match(r"^sm-s\d", lower) or re.match(r"^sm-f\d", lower):
        return "premium_android"   # Galaxy S-series (S8/S9/S21/S22/S23/S24/S25), Fold/Flip
    if re.match(r"^sm-a\d", lower) or re.match(r"^sm-m\d", lower):
        return "mid_android"       # Galaxy A-series, M-series
    if re.match(r"^sm-j\d", lower):
        return "low_android"       # Galaxy J-series (budget)
    if re.match(r"^sm-", lower):
        return "unknown_android"   # Other Samsung (older G-series, etc.)

    # Xiaomi / Redmi / POCO numeric codes (10–11 digits, start with 21 or 22)
    if re.match(r"^2[012]\d{8,}", lower):
        return "mid_android"       # Redmi Note / POCO M/X series

    # Realme RMX* codes
    if re.match(r"^rmx\d{4}", lower):
        return "mid_android"       # Realme (C-series is minority; default mid)

    # OPPO CPH* codes
    if re.match(r"^cph\d{4}", lower):
        return "mid_android"       # OPPO A/F series

    # Vivo V*/T* codes
    if re.match(r"^v[12]\d{3}", lower) or re.match(r"^t[12]\d{3}", lower):
        return "mid_android"       # Vivo V-series, T-series

    # ── Marketing name patterns ────────────────────────────────────────────
    for tier in ("premium_android", "mid_android", "low_android"):
        if any(kw in lower for kw in DEVICE_TIER_PATTERNS[tier]):
            return tier

    # Known vendor by name but unmatched model → unknown
    android_hints = (
        "samsung", "redmi", "xiaomi", "oneplus", "oppo", "vivo",
        "realme", "poco", "motorola", "moto", "asus", "lenovo",
        "huawei", "honor", "iqoo", "nothing",
    )
    if any(k in lower for k in android_hints):
        return "unknown_android"

    return "unknown_android"


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
    otp_email_funnel: Dict[str, List],  # {device: [otp, email_page, email_otp, signup]}
    otp_sso_funnel:   Dict[str, List],  # {device: [otp, email_page, email_sso, signup]}
) -> List[Dict]:
    """
    Aggregate 4-step Funnel API results by device tier.

    Step indices (both funnels):
      [0] OTP           = VERIFY_OTP_SUCCESS         (new + returning users)
      [1] Email Page    = EMAIL_PAGE_VIEW             (proxy for new-user OTPs)
      [2] Email Verify  = EMAIL_VERIFY_OTP_SUCCESS or SSO_VERIFICATION_SUCCESS
      [3] Signup        = SETUP_SECURE_PIN_SUCCESS

    EMAIL_PAGE_VIEW fires for ALL new users (both OTP and SSO paths) and matches
    first-time VERIFY_OTP_SUCCESS at 99.5% — used as accurate denominator for New%.

    Two conversion columns replace the old misleading single OTP→Em%:
      New%  = email_page / otp           (what % of all OTPs are new users)
      Em%   = email_total / email_page   (of new users, what % complete email verification)
    """
    otp_t         : Dict[str, int] = {}
    email_page_t  : Dict[str, int] = {}
    email_otp_t   : Dict[str, int] = {}
    signup_otp_t  : Dict[str, int] = {}

    for device, steps in otp_email_funnel.items():
        tier = classify_device_type(device)
        otp_t[tier]        = otp_t.get(tier, 0)        + (steps[0] if len(steps) > 0 else 0)
        email_page_t[tier] = email_page_t.get(tier, 0) + (steps[1] if len(steps) > 1 else 0)
        email_otp_t[tier]  = email_otp_t.get(tier, 0)  + (steps[2] if len(steps) > 2 else 0)
        signup_otp_t[tier] = signup_otp_t.get(tier, 0) + (steps[3] if len(steps) > 3 else 0)

    email_sso_t  : Dict[str, int] = {}
    signup_sso_t : Dict[str, int] = {}

    for device, steps in otp_sso_funnel.items():
        tier = classify_device_type(device)
        email_sso_t[tier]  = email_sso_t.get(tier, 0)  + (steps[2] if len(steps) > 2 else 0)
        signup_sso_t[tier] = signup_sso_t.get(tier, 0) + (steps[3] if len(steps) > 3 else 0)

    display_order = [
        "low_android", "mid_android", "premium_android",
        "ios", "web", "unknown_android",
    ]

    rows = []
    for tier in display_order:
        otp         = otp_t.get(tier, 0)
        email_page  = email_page_t.get(tier, 0)
        email_otp   = email_otp_t.get(tier, 0)
        email_sso   = email_sso_t.get(tier, 0)
        email_total = email_otp + email_sso
        signup      = signup_otp_t.get(tier, 0) + signup_sso_t.get(tier, 0)

        if otp == 0 and email_total == 0 and signup == 0:
            continue

        # New%: what % of all OTPs are new users (email_page ≈ first-time OTP)
        otp_to_newuser    = round(email_page  / otp        * 100, 1) if otp        > 0 else 0.0
        # Em%: of new users who hit email page, what % complete email verification
        newuser_to_email  = round(email_total / email_page * 100, 1) if email_page > 0 else 0.0
        # PIN%: of email-verified users, what % complete PIN setup (unchanged)
        email_to_signup   = round(signup      / email_total * 100, 1) if email_total > 0 else 0.0

        rows.append({
            "tier":                 tier,
            "label":                DEVICE_TIER_LABELS.get(tier, tier),
            "otp":                  otp,
            "email_page":           email_page,
            "email_otp":            email_otp,
            "email_sso":            email_sso,
            "email_total":          email_total,
            "signup":               signup,
            "otp_to_newuser_pct":   otp_to_newuser,
            "newuser_to_email_pct": newuser_to_email,
            "email_to_signup_pct":  email_to_signup,
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


def compute_kyc_steps_wow(
    cur_counts:   Dict[str, int],   # {step_key: count} for current cohort window
    prev_counts:  Dict[str, int],   # {step_key: count} for prior cohort window
    cur_signups:  int,              # signups in current cohort window (denominator)
    prev_signups: int,              # signups in prior cohort window (denominator)
) -> List[Dict]:
    """
    For each KYC intermediate step, compute what % of signups reached it (same window),
    the WoW pp change, and return sorted by worst drop first.

    Skips steps where both current and prior counts are 0 (e.g. V2-only steps in early
    prior windows before the Mar 10 funnel change).

    Returns list of dicts: {key, label, cur_pct, prev_pct, wow_pp}
    Sorted ascending by wow_pp (worst drop first).
    """
    result = []
    for step_key in KYC_STEP_ORDER:
        cur  = cur_counts.get(step_key, 0)
        prev = prev_counts.get(step_key, 0)
        if cur == 0 and prev == 0:
            continue  # step not active in either window (e.g. V2 step before Mar 10)
        cur_pct  = round(cur  / cur_signups  * 100, 1) if cur_signups  > 0 else 0.0
        prev_pct = round(prev / prev_signups * 100, 1) if prev_signups > 0 else 0.0
        wow_pp   = round(cur_pct - prev_pct, 1)
        result.append({
            "key":      step_key,
            "label":    KYC_STEP_LABELS.get(step_key, step_key),
            "cur_pct":  cur_pct,
            "prev_pct": prev_pct,
            "wow_pp":   wow_pp,
        })
    return sorted(result, key=lambda x: x["wow_pp"])  # worst drop first


def generate_alerts_v2(
    wow:              Dict[str, Dict],
    device_table:     List[Dict],
    sso_pct:          float,
    kyc_start_pct:    float = 0.0,
    kyc_done_pct:     float = 0.0,
    kyc_start_wow_pp: float = 0.0,
    kyc_done_wow_pp:  float = 0.0,
    kyc_steps_wow:    List[Dict] = None,
) -> List[str]:
    """Alerts for the v2 compact report, informed by business context (business_context.md)."""
    alerts: List[str] = []

    # ── KYC drop alerts ───────────────────────────────────────────────────
    _kyc_steps = kyc_steps_wow or []

    # Find the worst intermediate step (largest pp drop among tracked steps)
    worst_step = _kyc_steps[0] if _kyc_steps else None

    if kyc_done_wow_pp <= -5.0 and kyc_done_pct > 0:
        msg = (
            f"🔴 *KYC Completion down {abs(kyc_done_wow_pp):.1f}pp* WoW to *{kyc_done_pct}%*"
        )
        if worst_step and worst_step["wow_pp"] <= -2.0:
            msg += (
                f" — bottleneck: *{worst_step['label']}* step "
                f"({worst_step['wow_pp']:+.1f}pp, now {worst_step['cur_pct']}% of signups)"
            )
        else:
            msg += " — investigate drop-offs in KYC flow"
        alerts.append(msg)
    elif kyc_done_wow_pp <= -2.0 and kyc_done_pct > 0:
        msg = (
            f"⚠️ *KYC Completion down {abs(kyc_done_wow_pp):.1f}pp* WoW to *{kyc_done_pct}%*"
        )
        if worst_step and worst_step["wow_pp"] <= -2.0:
            msg += (
                f" — *{worst_step['label']}* step most affected "
                f"({worst_step['wow_pp']:+.1f}pp WoW)"
            )
        alerts.append(msg)
    elif worst_step and worst_step["wow_pp"] <= -5.0:
        # Intermediate step dropping even if overall completion is flat — early warning
        alerts.append(
            f"⚠️ *KYC {worst_step['label']}* step down *{abs(worst_step['wow_pp']):.1f}pp* WoW "
            f"to *{worst_step['cur_pct']}%* of signups — may drag completion next week"
        )

    if kyc_start_wow_pp <= -5.0 and kyc_start_pct > 0:
        alerts.append(
            f"⚠️ *KYC Start Rate down {abs(kyc_start_wow_pp):.1f}pp* WoW to *{kyc_start_pct}%* — "
            f"fewer signups proceeding to KYC"
        )

    # ── Signup WoW drop ───────────────────────────────────────────────────
    reg = wow.get("signup", {})
    pct = reg.get("pct_change", 0)
    if pct <= -20:
        alerts.append(
            f"🔴 *Signups down {abs(pct):.1f}% WoW* — "
            f"{reg.get('previous', 0):,} → {reg.get('current', 0):,}"
        )
    elif pct <= -10:
        alerts.append(
            f"⚠️ *Signups down {abs(pct):.1f}% WoW* — "
            f"{reg.get('previous', 0):,} → {reg.get('current', 0):,}"
        )

    # ── Audience quality: Low+Mid Android vs Premium+iOS (always shown) ──────
    total_signup        = sum(r["signup"] for r in device_table)
    low_mid_signup      = sum(r["signup"] for r in device_table
                              if r["tier"] in ("low_android", "mid_android", "other_android"))
    premium_ios_signup  = sum(r["signup"] for r in device_table
                              if r["tier"] in ("premium_android", "ios"))
    if total_signup > 0:
        low_mid_pct     = round(low_mid_signup    / total_signup * 100, 1)
        premium_ios_pct = round(premium_ios_signup / total_signup * 100, 1)
        if low_mid_pct > 70:
            icon = "🔴"
        elif low_mid_pct > 50:
            icon = "⚠️"
        else:
            icon = "📊"
        alerts.append(
            f"{icon} Audience mix: Low & Mid Android *{low_mid_pct}%* of signups, "
            f"Premium Android + iOS *{premium_ios_pct}%* — "
            f"{'target audience underrepresented, review acquisition channels' if low_mid_pct > 50 else 'audience quality looks healthy'}"
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
                f"({row['email_total']:,} email verified, {row['signup']:,} signed up)"
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
            if row["otp_to_newuser_pct"] < 10:
                alerts.append(
                    f"💡 *Low Android* new-user ratio only *{row['otp_to_newuser_pct']}%* — "
                    f"mostly returning logins, negligible new user acquisition"
                )

    # ── SSO adoption gap (Needs Attention when below 40% target) ─────────
    # SSO quality is always good (89.6% completion). Low adoption = users
    # defaulting to the harder OTP path — a UI discovery problem to fix.
    if sso_pct > 0:
        days_since_sso = (date.today() - SSO_LAUNCH_DATE).days
        otp_pct        = round(100 - sso_pct, 1)
        if days_since_sso <= 30 and sso_pct < 40:
            days_remaining = 30 - days_since_sso
            alerts.append(
                f"⚠️ *SSO adoption: {sso_pct}%* — {otp_pct}% of users still on OTP "
                f"(6 steps, 69.6% completion vs SSO's 89.6%) · "
                f"increase Google button prominence on email page to reach 40% in {days_remaining}d"
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
    wow:              Dict[str, Dict],
    device_table:     List[Dict],
    sso_pct:          float,
    kyc_start_pct:    float = 0.0,
    kyc_done_pct:     float = 0.0,
    kyc_start_wow_pp: float = 0.0,
    kyc_done_wow_pp:  float = 0.0,
) -> List[str]:
    """Positive signals worth calling out — informed by business context."""
    wins: List[str] = []

    # Signup WoW growth
    reg = wow.get("signup", {})
    if reg.get("pct_change", 0) >= 5:
        wins.append(
            f"Signups up *{reg['pct_change']:+.1f}%* WoW "
            f"({reg['previous']:,} → {reg['current']:,})"
        )

    # KYC improvements
    if kyc_start_wow_pp >= 2.0:
        wins.append(
            f"KYC Start Rate up *↑{kyc_start_wow_pp:.1f}pp* WoW to *{kyc_start_pct}%* — "
            f"more signups proceeding to KYC"
        )
    if kyc_done_wow_pp >= 2.0:
        wins.append(
            f"KYC Completion Rate up *↑{kyc_done_wow_pp:.1f}pp* WoW to *{kyc_done_pct}%* — "
            f"post-update completion improving"
        )

    # SSO quality win — always show when any users are on SSO.
    # 89.6% completion vs 69.6% OTP is a UX quality win regardless of adoption %.
    # If adoption >= 40%, also celebrate hitting the target.
    if sso_pct > 0:
        days_since_sso = (date.today() - SSO_LAUNCH_DATE).days
        if sso_pct >= 40:
            wins.append(
                f"✅ *SSO at {sso_pct}%* — 40% target reached · "
                f"SSO users convert at 89.6% vs 69.6% for OTP (4 steps vs 6)"
            )
        else:
            wins.append(
                f"SSO users convert at *89.6%* vs 69.6% for OTP — "
                f"{sso_pct}% of users already on the faster path (4 steps vs 6)"
            )

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
