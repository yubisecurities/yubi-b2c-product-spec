"""
Skill 1 — Campaign Analysis

Fetches current + prior week data from Google Ads, computes WoW deltas,
and returns a structured summary ready for LLM analysis or Slack posting.
"""

from typing import Optional
from connectors.google_ads import (
    get_campaign_performance,
    get_ad_performance,
    get_device_segments,
    get_geo_segments,
    get_conversion_breakdown,
)
import config


def _micros_to_inr(micros: int) -> float:
    """Convert cost_micros to currency units (Google stores cost × 1,000,000)."""
    return round(micros / 1_000_000, 2)


def _pct_change(current: float, prior: float) -> Optional[float]:
    if prior == 0:
        return None
    return round(((current - prior) / prior) * 100, 1)


def _aggregate_campaigns(rows: list[dict]) -> dict:
    """Roll up all campaigns into a single totals dict."""
    totals = {
        "impressions":      0,
        "clicks":           0,
        "cost":             0.0,
        "in_app_actions":   0.0,
        "conversion_value": 0.0,
    }
    for r in rows:
        totals["impressions"]      += r["impressions"]
        totals["clicks"]           += r["clicks"]
        totals["cost"]             += _micros_to_inr(r["cost_micros"])
        totals["in_app_actions"]   += r["conversions"]
        totals["conversion_value"] += r["conversion_value"]

    totals["ctr"]                    = round(totals["clicks"] / totals["impressions"] * 100, 2) if totals["impressions"] else 0
    totals["cpc"]                    = round(totals["cost"] / totals["clicks"], 2) if totals["clicks"] else 0
    totals["roas"]                   = round(totals["conversion_value"] / totals["cost"], 2) if totals["cost"] else 0
    totals["cost_per_in_app_action"] = round(totals["cost"] / totals["in_app_actions"], 2) if totals["in_app_actions"] else 0

    return totals


def run() -> dict:
    """
    Entry point for Skill 1.

    Returns a structured dict:
    {
        "current_week": { totals + per-campaign breakdown },
        "prior_week":   { totals },
        "wow":          { % changes for key metrics },
        "top_campaigns": [ top 5 by spend ],
        "device_split": { MOBILE: {...}, DESKTOP: {...}, TABLET: {...} },
        "geo_split":    [ top 10 countries ],
        "top_ads":      [ top 5 ads by impressions ],
        "date_range":   { current_start, current_end, prior_start, prior_end },
    }
    """
    current_start = config.CURRENT_START.isoformat()
    current_end   = config.CURRENT_END.isoformat()
    prior_start   = config.PRIOR_START.isoformat()
    prior_end     = config.PRIOR_END.isoformat()

    print(f"[campaign_analysis] Fetching current week: {current_start} → {current_end}")
    current_campaigns = get_campaign_performance(current_start, current_end)

    print(f"[campaign_analysis] Fetching prior week:   {prior_start} → {prior_end}")
    prior_campaigns   = get_campaign_performance(prior_start, prior_end)

    print("[campaign_analysis] Fetching ad creative performance...")
    top_ads = get_ad_performance(current_start, current_end)

    print("[campaign_analysis] Fetching device segments...")
    device_rows = get_device_segments(current_start, current_end)

    print("[campaign_analysis] Fetching geo segments...")
    geo_rows = get_geo_segments(current_start, current_end)

    print("[campaign_analysis] Fetching conversion action breakdown...")
    conv_breakdown_rows = get_conversion_breakdown(current_start, current_end)

    # ── Aggregates ────────────────────────────────────────────────────────────
    current_totals = _aggregate_campaigns(current_campaigns)
    prior_totals   = _aggregate_campaigns(prior_campaigns)

    wow = {
        "impressions_pct":           _pct_change(current_totals["impressions"],           prior_totals["impressions"]),
        "clicks_pct":                _pct_change(current_totals["clicks"],                prior_totals["clicks"]),
        "cost_pct":                  _pct_change(current_totals["cost"],                  prior_totals["cost"]),
        "in_app_actions_pct":        _pct_change(current_totals["in_app_actions"],        prior_totals["in_app_actions"]),
        "cost_per_in_app_action_pct":_pct_change(current_totals["cost_per_in_app_action"],prior_totals["cost_per_in_app_action"]),
        "roas_pct":                  _pct_change(current_totals["roas"],                  prior_totals["roas"]),
        "ctr_pct":                   _pct_change(current_totals["ctr"],                   prior_totals["ctr"]),
    }

    # ── In-app action totals (all_conversions across all actions) ─────────────
    action_totals: dict[str, float] = {}
    for row in conv_breakdown_rows:
        action = row["conversion_action"]
        action_totals[action] = action_totals.get(action, 0) + row["all_conversions"]

    total_all_conversions = sum(action_totals.values())
    total_cost = current_totals["cost"]
    cost_per_action_breakdown = {
        action: round(total_cost / count, 2) if count > 0 else 0
        for action, count in action_totals.items()
    }

    # Sort by count descending, keep top 20
    in_app_actions_breakdown = sorted(
        [
            {
                "action":           action,
                "count":            round(count, 0),
                "cost_per_action":  cost_per_action_breakdown[action],
            }
            for action, count in action_totals.items()
        ],
        key=lambda x: x["count"],
        reverse=True,
    )[:20]

    # ── Top campaigns by spend ────────────────────────────────────────────────
    top_campaigns = sorted(current_campaigns, key=lambda r: r["cost_micros"], reverse=True)[:5]
    for c in top_campaigns:
        c["cost"]                  = _micros_to_inr(c.pop("cost_micros"))
        c["avg_cpc"]               = _micros_to_inr(c.pop("avg_cpc_micros"))
        c["cost_per_in_app_action"]= _micros_to_inr(c.pop("cost_per_conversion_micros"))
        c["in_app_actions"]        = c.pop("conversions")
        c["ctr_pct"]               = round(c["ctr"] * 100, 2)

    # ── Device split ──────────────────────────────────────────────────────────
    device_split: dict[str, dict] = {}
    for row in device_rows:
        d = row["device"]
        if d not in device_split:
            device_split[d] = {"impressions": 0, "clicks": 0, "cost": 0.0, "conversions": 0.0}
        device_split[d]["impressions"] += row["impressions"]
        device_split[d]["clicks"]      += row["clicks"]
        device_split[d]["cost"]        += _micros_to_inr(row["cost_micros"])
        device_split[d]["conversions"] += row["conversions"]

    # ── Top ads ───────────────────────────────────────────────────────────────
    top_ads_clean = []
    for ad in top_ads[:5]:
        top_ads_clean.append({
            "campaign_name": ad["campaign_name"],
            "ad_type":       ad["ad_type"],
            "impressions":   ad["impressions"],
            "ctr_pct":       round(ad["ctr"] * 100, 2),
            "conversions":   ad["conversions"],
            "cost":          _micros_to_inr(ad["cost_micros"]),
            "headlines":     ad["headlines"][:3],   # top 3 headlines for brevity
            "descriptions":  ad["descriptions"][:2],
        })

    return {
        "current_week":           current_totals,
        "prior_week":             prior_totals,
        "wow":                    wow,
        "top_campaigns":          top_campaigns,
        "in_app_actions_breakdown": in_app_actions_breakdown,
        "total_all_conversions":  total_all_conversions,
        "device_split":           device_split,
        "geo_split":              geo_rows[:10],
        "top_ads":                top_ads_clean,
        "date_range": {
            "current_start": current_start,
            "current_end":   current_end,
            "prior_start":   prior_start,
            "prior_end":     prior_end,
        },
    }
