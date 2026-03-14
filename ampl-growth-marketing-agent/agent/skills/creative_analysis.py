"""
Skill 2 — Creative Analysis

Fetches Aspero's own Google App Ad copy from the Google Ads API and analyzes
it using Claude (AWS Bedrock) to produce:
  - Per-ad copy analysis: value prop, clarity score, gaps, suggested headline tests
  - Cross-ad pattern synthesis: what's working, what's missing, why
  - 5 specific copy angles to test (with example headlines + descriptions)
  - Strategic creative recommendation for the bond investment audience

Run condition: requires AWS_ACCESS_KEY_ID + AWS_SECRET_ACCESS_KEY.
Gracefully falls back to raw copy export if AWS creds are absent.
"""

import json
import os
from typing import Optional

from connectors.google_ads import get_app_ad_copy
import config


# ── Prompts ───────────────────────────────────────────────────────────────────

_SYSTEM_PROMPT = """You are a senior performance marketing creative strategist specializing \
in fintech mobile apps for the Indian retail investor market.

## About Aspero
Aspero is a SEBI-registered Online Bond Platform Provider (OBPP). Users directly buy and sell \
bonds — government securities, corporate bonds, and NCDs — with yields typically 8–12% p.a. \
This is a high-trust, considered purchase. Target audience: salaried professionals aged 30–55, \
₹15L+ annual income, metro + Tier-1 cities, looking for stable returns beyond FDs and mutual funds. \
Average investment ticket: ₹50,000–₹5,00,000.

## Campaign goals
- BankVerified campaign: acquire users who will complete bank KYC verification
- PaymentSuccess campaign: acquire users who will make an actual bond investment

## Competitors
Wint Wealth, GoldenPi, Grip Invest, StableMoney, INDmoney, Groww

## Rules
- Be specific and actionable — reference actual headlines/copy, not generic advice
- These are Google App Ads (MULTI_CHANNEL) — they run on Play Store, YouTube, Search, Display
- App ad character limits: headlines ≤ 30 chars, descriptions ≤ 90 chars
- The audience will NOT install if the ad is unclear about what the product does
- Return only valid JSON when asked for JSON — no markdown fences, no explanation text"""

_AD_PROMPT = """\
Analyze this Google App Ad:

Campaign: {campaign_name}
Performance (7-day window): {impressions:,} impressions | {ctr_pct}% CTR | \
{conversions:.0f} conversions | ₹{cost:,.0f} spend

Headlines ({n_h}):
{headlines_block}

Descriptions ({n_d}):
{descriptions_block}

Return a JSON object with exactly these fields:
{{
  "primary_value_prop": "one short phrase — what is this ad primarily selling",
  "emotional_hook": "one of: aspiration | safety | returns | ease | trust | fomo | none",
  "clarity_score": <integer 1-5, 5=crystal clear what the app does and why install>,
  "what_works": ["strength 1", "strength 2"],
  "what_missing": ["gap 1", "gap 2"],
  "suggested_headline_tests": ["headline ≤30 chars", "headline ≤30 chars", "headline ≤30 chars"]
}}"""

_SYNTHESIS_PROMPT = """\
Here are all {n} Google App Ads for Aspero with copy and per-ad analysis:

{ads_block}

Write a creative strategy report. Be specific — reference actual headlines and copy. No generic advice.

## What high-performing ads have in common
(Ads with highest CTR and conversions — what messaging patterns do they share?)

## What low-performing ads are missing
(Ads with lowest CTR — what are they failing to communicate?)

## 5 copy angles to test
For each angle:
- Angle name
- 3 headline examples (max 30 chars each)
- 1 description example (max 90 chars)
Focus on angles currently absent or underused across all ads.

## Creative strategy recommendation
2–3 sentences: what should Aspero's Google App Ad messaging strategy be, \
given the bond investment audience and current campaign goals?"""


# ── Bedrock client ────────────────────────────────────────────────────────────

def _has_aws_creds() -> bool:
    return bool(os.environ.get("AWS_ACCESS_KEY_ID"))


def _call_claude(prompt: str, system: str, max_tokens: int = 1024) -> str:
    """Call Claude via AWS Bedrock and return the response text."""
    import boto3
    client = boto3.client(
        "bedrock-runtime",
        region_name=config.AWS_REGION,
        aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
    )
    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": max_tokens,
        "system": system,
        "messages": [{"role": "user", "content": prompt}],
    })
    response = client.invoke_model(
        modelId=config.BEDROCK_MODEL,
        body=body,
        contentType="application/json",
        accept="application/json",
    )
    result = json.loads(response["body"].read())
    return result["content"][0]["text"]


# ── Per-ad analysis ───────────────────────────────────────────────────────────

def _analyze_ad_copy(ad: dict) -> dict:
    """
    Send a single ad's copy to Claude and return structured analysis.
    Falls back to empty analysis dict if Claude call fails.
    """
    headlines_block    = "\n".join(f"  {i+1}. {h}" for i, h in enumerate(ad["headlines"]))    or "  (none)"
    descriptions_block = "\n".join(f"  {i+1}. {d}" for i, d in enumerate(ad["descriptions"])) or "  (none)"

    prompt = _AD_PROMPT.format(
        campaign_name=ad["campaign_name"],
        impressions=ad["impressions"],
        ctr_pct=ad["ctr_pct"],
        conversions=ad["conversions"],
        cost=ad["cost"],
        n_h=len(ad["headlines"]),
        headlines_block=headlines_block,
        n_d=len(ad["descriptions"]),
        descriptions_block=descriptions_block,
    )

    try:
        raw = _call_claude(prompt, _SYSTEM_PROMPT, max_tokens=600)
        # Strip any accidental markdown fences
        clean = raw.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
        return json.loads(clean)
    except Exception as e:
        print(f"[creative_analysis] Claude call failed for ad {ad['ad_id']}: {e}")
        return {
            "primary_value_prop": "unknown",
            "emotional_hook": "unknown",
            "clarity_score": None,
            "what_works": [],
            "what_missing": [],
            "suggested_headline_tests": [],
        }


# ── Synthesis ─────────────────────────────────────────────────────────────────

def _synthesize(ads_with_analysis: list[dict]) -> str:
    """
    Send all ads + per-ad analysis to Claude and return a strategic narrative.
    """
    ads_block_parts = []
    for i, ad in enumerate(ads_with_analysis):
        a = ad.get("analysis", {})
        part = (
            f"--- Ad {i+1}: {ad['campaign_name']} ---\n"
            f"Performance: {ad['impressions']:,} impr | {ad['ctr_pct']}% CTR | "
            f"{ad['conversions']:.0f} conv | ₹{ad['cost']:,.0f} spend\n"
            f"Headlines: {' | '.join(ad['headlines']) or '(none)'}\n"
            f"Descriptions: {' | '.join(ad['descriptions']) or '(none)'}\n"
            f"Analysis: value_prop={a.get('primary_value_prop','?')} | "
            f"hook={a.get('emotional_hook','?')} | "
            f"clarity={a.get('clarity_score','?')}/5\n"
            f"Missing: {', '.join(a.get('what_missing', [])) or 'none identified'}\n"
        )
        ads_block_parts.append(part)

    prompt = _SYNTHESIS_PROMPT.format(
        n=len(ads_with_analysis),
        ads_block="\n".join(ads_block_parts),
    )

    try:
        return _call_claude(prompt, _SYSTEM_PROMPT, max_tokens=2000)
    except Exception as e:
        print(f"[creative_analysis] Synthesis Claude call failed: {e}")
        return "(synthesis unavailable — AWS call failed)"


# ── Main entry point ──────────────────────────────────────────────────────────

def run(start_date: str, end_date: str) -> dict:
    """
    Entry point for Skill 2.

    Returns:
    {
        "ads": [
            {
                "campaign_name": str,
                "ad_id":         str,
                "impressions":   int,
                "ctr_pct":       float,
                "conversions":   float,
                "cost":          float,
                "headlines":     list[str],
                "descriptions":  list[str],
                "analysis":      dict | None   # None if no AWS creds
            },
            ...
        ],
        "synthesis": str | None,    # None if no AWS creds
        "llm_enabled": bool,
    }
    """
    print("[creative_analysis] Fetching APP_AD copy from Google Ads...")
    ads = get_app_ad_copy(start_date, end_date)

    if not ads:
        print("[creative_analysis] No APP_AD creatives found for the period.")
        return {"ads": [], "synthesis": None, "llm_enabled": False}

    print(f"[creative_analysis] Found {len(ads)} app ads.")

    llm_enabled = _has_aws_creds()
    if not llm_enabled:
        print("[creative_analysis] AWS creds not set — returning raw copy only (no analysis).")
        for ad in ads:
            ad["analysis"] = None
        return {"ads": ads, "synthesis": None, "llm_enabled": False}

    # Per-ad analysis
    for i, ad in enumerate(ads):
        print(f"[creative_analysis] Analyzing ad {i+1}/{len(ads)}: {ad['campaign_name']}...")
        ad["analysis"] = _analyze_ad_copy(ad)

    # Cross-ad synthesis
    print("[creative_analysis] Running synthesis...")
    synthesis = _synthesize(ads)

    return {
        "ads":         ads,
        "synthesis":   synthesis,
        "llm_enabled": True,
    }
