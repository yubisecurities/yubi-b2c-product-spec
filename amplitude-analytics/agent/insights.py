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

    # Known Android vendor but unmatched model → other_android
    android_hints = (
        "samsung", "redmi", "xiaomi", "oneplus", "oppo", "vivo",
        "realme", "poco", "motorola", "moto", "asus", "lenovo",
        "huawei", "honor", "iqoo", "nothing",
    )
    if any(k in lower for k in android_hints):
        return "other_android"

    return "other"


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
        "ios", "web", "other_android", "other",
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
