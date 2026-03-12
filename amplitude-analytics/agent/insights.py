"""
Insight generation — converts raw Amplitude counts into:
  - Funnel step conversion rates
  - Platform health status
  - Week-over-week deltas
  - Anomaly alerts
"""

from typing import Dict, List, Tuple
from config import (
    FUNNEL_STEPS,
    FAILURE_EVENTS,
    PLATFORM_BASELINES,
    PLATFORM_ALERT_THRESHOLDS,
    PLATFORM_WARNING_THRESHOLDS,
    STEP_THRESHOLDS,
)


# ---------------------------------------------------------------------------
# Funnel
# ---------------------------------------------------------------------------

def compute_funnel(event_counts: Dict[str, int]) -> List[Dict]:
    """
    Annotate each funnel step with:
      - count: unique users
      - pct_of_top: % relative to SIGNIN_PAGE_VIEW (top of funnel)
      - step_conv: % conversion from the previous step
    """
    top = event_counts.get("SIGNIN_PAGE_VIEW", 0)
    enriched = []

    for i, step in enumerate(FUNNEL_STEPS):
        event = step["event"]
        count = event_counts.get(event, 0)
        pct_of_top = round(count / top * 100, 1) if top > 0 else 0.0

        prev_count = enriched[i - 1]["count"] if i > 0 else count
        step_conv = round(count / prev_count * 100, 1) if prev_count > 0 else 0.0

        enriched.append({
            **step,
            "count":      count,
            "pct_of_top": pct_of_top,
            "step_conv":  step_conv,
        })

    return enriched


# ---------------------------------------------------------------------------
# Platform
# ---------------------------------------------------------------------------

def compute_platform_insights(
    platform_funnel: Dict[str, Dict[str, int]],
) -> Dict[str, Dict]:
    """
    For each platform (Android / iOS / Web):
      - views (SIGNIN_PAGE_VIEW), verified (VERIFY_OTP_SUCCESS), conversion %
      - delta vs historical baseline
      - health status: healthy | warning | alert

    platform_funnel: {platform: {event_name: cumulative_count}} from Funnel API.
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
            # Full per-step counts for this platform (useful in Slack for registrations)
            "steps":               steps,
        }

    return results


# ---------------------------------------------------------------------------
# Week-over-week
# ---------------------------------------------------------------------------

def compute_wow(
    current: Dict[str, int],
    previous: Dict[str, int],
) -> Dict[str, Dict]:
    """
    Return WoW delta for every event that appears in `current`.
    """
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
    funnel_steps: List[Dict],
    platform_insights: Dict[str, Dict],
    failure_counts: Dict[str, int],
    wow: Dict[str, Dict],
) -> List[str]:
    """
    Return a list of human-readable alert strings (markdown-ish for Slack).
    Sorted: 🔴 first, then ⚠️.
    """
    alerts: List[str] = []

    # 1. Platform alerts
    for platform, data in platform_insights.items():
        status = data["status"]
        conv   = data["conversion"]
        base   = data["baseline"]
        delta  = data["delta_from_baseline"]

        if status == "alert":
            alerts.append(
                f"🔴 *{platform}* conversion critically low: "
                f"*{conv}%*  (baseline {base}%, {delta:+.1f}pp)"
            )
        elif status == "warning":
            alerts.append(
                f"⚠️ *{platform}* below baseline: "
                f"*{conv}%*  (baseline {base}%, {delta:+.1f}pp)"
            )

    # 2. Step-to-step threshold breaches
    step_map = {s["event"]: s for s in funnel_steps}
    for (from_event, to_event), threshold in STEP_THRESHOLDS.items():
        from_count = step_map.get(from_event, {}).get("count", 0)
        to_count   = step_map.get(to_event,   {}).get("count", 0)
        if from_count > 0:
            actual = round(to_count / from_count * 100, 1)
            if actual < threshold:
                from_label = from_event.replace("_", " ").title()
                to_label   = to_event.replace("_", " ").title()
                alerts.append(
                    f"⚠️ Low step conversion *{from_label} → {to_label}*: "
                    f"*{actual}%*  (min expected {threshold}%)"
                )

    # 3. High failure rates (>5% of top-of-funnel)
    top = step_map.get("SIGNIN_PAGE_VIEW", {}).get("count", 0)
    if top > 0:
        for event in FAILURE_EVENTS:
            count = failure_counts.get(event, 0)
            rate  = round(count / top * 100, 1)
            if rate >= 5.0:
                label = event.replace("_", " ").title()
                alerts.append(
                    f"⚠️ High failure rate — *{label}*: "
                    f"{count:,} failures ({rate}% of sessions)"
                )

    # 4. Sharp WoW drops (>15% drop in registrations)
    registration_wow = wow.get("SETUP_SECURE_PIN_SUCCESS", {})
    pct = registration_wow.get("pct_change", 0)
    if pct <= -20:
        alerts.append(
            f"🔴 *Registrations down {pct:.1f}% WoW* — "
            f"{registration_wow.get('previous', 0):,} → {registration_wow.get('current', 0):,}"
        )
    elif pct <= -10:
        alerts.append(
            f"⚠️ *Registrations down {pct:.1f}% WoW* — "
            f"{registration_wow.get('previous', 0):,} → {registration_wow.get('current', 0):,}"
        )

    # Sort 🔴 before ⚠️
    alerts.sort(key=lambda x: (0 if x.startswith("🔴") else 1))
    return alerts


# ---------------------------------------------------------------------------
# Overall health
# ---------------------------------------------------------------------------

def get_overall_health(
    platform_insights: Dict[str, Dict],
    wow: Dict[str, Dict],
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
