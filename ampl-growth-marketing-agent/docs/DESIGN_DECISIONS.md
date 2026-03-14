# Growth Marketing Agent — Design Decisions & Key Findings

This file captures architectural choices, data discoveries, and analytical decisions
made during the build and analysis of the Aspero Growth Marketing Agent.
Updated incrementally — newest entries at the top.

---

## Google Ads Conversion Tracking — Audit Findings (Mar 14 2026)

### Discovery: Both MULTI_CHANNEL campaigns are effectively install campaigns
**Date:** Mar 14 2026
**Status:** ✅ Documented — action required on Google Ads side

**What the data shows (7-day window: Mar 7–13 2026):**

| Campaign | Spend | Primary Conv | Primary Events |
|---|---|---|---|
| BankVerified | ₹1,48,940 | 944 | first_open: 832 (88%) + KYC_ADDRESS_VERIFIED: 112 (12%) |
| PaymentSuccess | ₹1,17,529 | 872 | first_open: 870 (99.8%) + in_app_purchase: 2 (0.2%) |

Both campaigns are MULTI_CHANNEL (Google App) on tCPA. Their intended conversion events
don't fire in Google Ads (or fire too infrequently), so Smart Bidding defaults to `first_open`.
Both are effectively buying installs — ₹2,66,469 combined — at ~₹156/install.

**Root cause per campaign:**

**BankVerified:**
- Intended event: bank verification
- Bank verification redesigned Jan 20 2026 → new events: `KYC_BANK_VERIFIED_PD` + `KYC_BANK_VERIFIED_REVERSE_PD`
- Neither new event is linked to Google Ads
- Old event `KYC_BANK_VERIFIED` (legacy) fires ~0/week now (pre-Jan 20 method)
- Smart Bidding fell back to: `first_open` (primary install signal) + `KYC_ADDRESS_VERIFIED` (nearest KYC signal)
- Budget capped at 106% — spending ₹148K/week with no bank verification signal at all

**PaymentSuccess:**
- Intended event: `in_app_purchase` (actual bond investment transaction)
- Only 2 in_app_purchase events in the 7-day window — insufficient for Smart Bidding (needs 30-50/month minimum)
- Smart Bidding defaults to `first_open` (870/week — abundant signal)
- Budget at 34% utilization — pulled back because bid strategy can't find enough high-intent users
- Spend dropped -52.9% WoW — likely a bid strategy confidence collapse

**Fix required:**
1. BankVerified: Add `KYC_BANK_VERIFIED_PD` + `KYC_BANK_VERIFIED_REVERSE_PD` to Google Ads conversion actions and link to campaign. Keep `KYC_BANK_VERIFIED` for straggler coverage.
2. PaymentSuccess: Identify intermediate funnel events that fire more frequently (e.g. `KYC_READY_FOR_TRADE` = KYC complete = ~58% of signups) to give Smart Bidding a learnable signal. `in_app_purchase` alone is too sparse.

---

## Per-Campaign Primary Event Breakdown (Code Design)

### Decision: Show primary_events breakdown per campaign instead of raw conversion count
**Date:** Mar 14 2026
**Status:** ✅ Implemented

**Problem:** The `in_app_actions` count per campaign (from `metrics.conversions`) showed 944
and 872, which I initially mis-attributed to KYC events. The actual composition was opaque.

**Fix:** `conv_breakdown_rows` already contains `(campaign_name, conversion_action, all_conversions,
primary_conversions)` per row. Build `camp_primary_events` dict by filtering rows where
`primary_conversions > 0`, grouped by campaign. Attach as `primary_events` list to each
top campaign in the output.

**Result:** Per-campaign output now shows:
```
BankVerified: 944 primary conversions
  └ first_open              832
  └ KYC_ADDRESS_VERIFIED    112

PaymentSuccess: 872 primary conversions
  └ first_open              870
  └ in_app_purchase           2
```

**Why not use all_conversions per campaign:** Previous attempt showed 8,714 for BankVerified
because all_conversions includes session_start (5,336 total), first_open, reinstall etc.
This was misleading. `metrics.conversions` (primary only) is the correct metric for
"what is this campaign actually optimizing for."

---

## Duplicate Firebase Conversion Tracking

### Discovery: Two Firebase property names tracking same events
**Date:** Mar 14 2026
**Status:** ⚠️ Unresolved — needs cleanup in Google Ads conversion settings

From the all_conversions breakdown:

| Event | Aspero property | yubi-invest property |
|---|---|---|
| VERIFY_OTP_SUCCESS | 1,443 | 1,438 |
| first_open | 1,720 | 1,859 |
| session_start | 5,336 | (in yubi-invest total) |

Two Firebase property names appear in Google Ads:
- `Aspero Fixed Income- Buy Bonds (Android)` — primary property
- `yubi-invest - Aspero Fixed Income- Buy Bonds (Android)` — duplicate

Near-identical event counts confirm these are the same users tracked twice.
Smart Bidding sees inflated conversion signals. CPA metrics are understated.

**Fix:** Remove/exclude the `yubi-invest` property events from active conversion actions,
or consolidate to a single Firebase property.

---

## Correct Conversion Hierarchy for Aspero

### Decision: Map conversion events to business intent
**Date:** Mar 14 2026
**Status:** ✅ Documented

From Amplitude context + Google Ads audit, the correct conversion hierarchy is:

| Level | Amplitude Event | Google Ads Status | Fires/week |
|---|---|---|---|
| Install | `first_open` | ✅ Tracked (primary for both campaigns) | 1,720 |
| Registration | `SETUP_SECURE_PIN_SUCCESS` | ✅ Tracked (secondary only) | 857 |
| KYC Start | `KYC_RISKDETAILS_SUBMIT` | ❌ Not in Google Ads | ~600 est |
| KYC Complete | `KYC_READY_FOR_TRADE` | ❌ Not in Google Ads | ~350 est |
| Bank Verified | `KYC_BANK_VERIFIED_PD` / `_REVERSE_PD` | ❌ Not in Google Ads | unknown |
| Investment | `in_app_purchase` | ✅ Tracked (primary for PaymentSuccess) | 2 |

**Key insight:** There's a massive gap in the middle of the funnel. Google Ads knows about
installs (1,720) and investments (2), but nothing about the 857 registrations, ~600 KYC
starts, or bank verifications in between. Smart Bidding has no signal to learn from for
the $-value stages of the funnel.

**Recommended conversion action setup:**
- Primary: `KYC_READY_FOR_TRADE` (enough volume, clear intent signal, ~350/week est)
- Secondary: `SETUP_SECURE_PIN_SUCCESS` (upstream proxy), `in_app_purchase` (ultimate goal)
- Bank verification: `KYC_BANK_VERIFIED_PD` + `KYC_BANK_VERIFIED_REVERSE_PD` + `KYC_BANK_VERIFIED`

---

## Summary Statistics (7-day window: Mar 7–13 2026)

| Metric | Value | WoW |
|---|---|---|
| Impressions | 9,70,055 | -62.5% |
| Clicks | 19,940 | -36.1% |
| CTR | 2.06% | +70.2% |
| Total Spend | ₹2,73,691 | -43.1% |
| True new registrations (SETUP_SECURE_PIN_SUCCESS) | 857 | — |
| True CPA (spend / new registrations) | ₹319 | — |
| Reported CPA (misleading, all events) | ₹16 | — |
| Install CPA (first_open, 1,702 total) | ₹161 | — |

---

## Skill 1 — Campaign Analysis (Code Decisions)

### Decision: Per-campaign in_app_actions uses metrics.conversions (primary)
Primary conversions per campaign = what campaign bids on. Consistent with Google Ads UI "Conversions" column.
All_conversions includes session_start noise and would inflate per-campaign counts.

### Decision: Summary-level in_app_actions uses all_conversions
Total in-app actions at summary level uses all_conversions to capture every tracked event.
WoW uses all_conversions for both current and prior week for consistency.

### Decision: Channel split computed BEFORE top_campaigns loop pops cost_micros
`channel_split` iterates `current_campaigns` which still has `cost_micros`. If `top_campaigns`
loop runs first and pops `cost_micros`, channel_split would see 0. Order matters.

### Known: geo_target_constant cannot be joined from geographic_view in GAQL
`PROHIBITED_RESOURCE_TYPE_IN_SELECT_CLAUSE` error. Use static `_GEO_NAMES` dict instead.
Currently maps top 15 country criterion IDs → human-readable names.

### Known: segments.conversion_action_name cannot combine with metrics.cost_micros
`PROHIBITED_SEGMENT_WITH_METRIC` error. Cost per action computed in `campaign_analysis.py`
using total spend / per-action count (not per-campaign-per-action split).

---

## Open Questions / Next Steps

| # | Item | Priority |
|---|---|---|
| 1 | Link `KYC_BANK_VERIFIED_PD` + `_REVERSE_PD` to BankVerified Google Ads campaign | P0 |
| 2 | Fix duplicate Firebase property tracking (yubi-invest vs Aspero property) | P0 |
| 3 | Add `KYC_READY_FOR_TRADE` as conversion action for Smart Bidding signal | P1 |
| 4 | Switch primary conversion from `VERIFY_OTP_SUCCESS` → `SETUP_SECURE_PIN_SUCCESS` | P1 |
| 5 | Investigate PaymentSuccess -52.9% spend WoW drop | P1 |
| 6 | Build Skill 2: LLM insights layer (AWS Bedrock / Claude) | P2 |
| 7 | Build business_context.md for growth marketing agent system prompt | P2 |
