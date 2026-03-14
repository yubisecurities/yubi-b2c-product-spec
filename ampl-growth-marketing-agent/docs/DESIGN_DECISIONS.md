# Growth Marketing Agent — Design Decisions & Key Findings

This file captures architectural choices, data discoveries, and analytical decisions
made during the build and analysis of the Aspero Growth Marketing Agent.
Updated incrementally — newest entries at the top.

---

## Creative Analysis Report Format

### Decision: Standardised 6-section format for weekly creative reviews
**Date:** Mar 14 2026
**Status:** ✅ Documented — see `docs/CREATIVE_ANALYSIS_FORMAT.md`

**6 sections (in order):**
1. **Raw Copy Table** — all ads, impressions, CTR, full headlines + descriptions
2. **Key Finding** — single lead insight, always data-anchored (CTR gap, spend concentration, etc.)
3. **Per-Ad Analysis** — `Clarity: X/5`, primary value prop, emotional hook, what works, what's missing
4. **Cross-Ad Pattern Analysis** — numbered findings: repeated headlines, description quality, trust signal usage, duplicate creatives, missing angles
5. **5 Copy Angles to Test** — each currently absent/underused; format: angle name, 3 headlines ≤30 chars, 1 description ≤90 chars
6. **Priority Fixes** — P0 = this week, numbered, specific (which headline to replace + 2-3 options)

**First live analysis (Mar 7–13 2026) key findings:**
- `"Earn 9-15% Fixed Returns Today"` is the single headline driving BankVerified's CTR premium (2.70–2.80% vs 1.73% for PaymentSuccess Ad 1 which has zero yield number)
- `"Explore Bonds on Aspero"` — highest-impression headline in the account, worst performing (passive, no benefit)
- BankVerified Ad 3 (highest CTR 2.80%) wins on `"Invest Smart"` + strong descriptions, not yield headline — aspiration beats security framing
- PaymentSuccess has single-creative dependency: Ad 1 = 91.9% of campaign impressions
- Ads 2 and 5 (BankVerified) are near-duplicate creatives — wasted learning slot
- `"zero defaults since inception"` is in all descriptions but never tested as a headline

**Weekly analysis checklist (before writing):**
- Are any two ads running identical copy? (duplicate waste)
- Which headline appears in all ads? (table stakes vs differentiator)
- Is there a yield number in PaymentSuccess? (historically absent — flag every time)
- CTR spread > 0.5% = meaningful copy signal worth explaining
- Did any new creative launch this week?

---

## Skill 2 — Creative Analysis (Code Design)

### Decision: Analyze own Google App Ad copy with Claude (AWS Bedrock)
**Date:** Mar 14 2026
**Status:** ✅ Implemented

**What was built:** `skills/creative_analysis.py` — `run(start_date, end_date)` fetches
all APP_AD copy via `get_app_ad_copy()`, analyzes each ad with Claude, and synthesizes
cross-ad insights + recommendations. Report section added to `skills/report.py`.

**Why copy-only (no image analysis):**
Google App Ad images are served from authenticated CDN URLs — fetching them requires
OAuth headers. Deferred to a future iteration. Copy alone is sufficient for first-pass
creative strategy because headlines/descriptions carry the core messaging signal.

**Per-ad analysis (Claude, JSON output):**
- `primary_value_prop` — what the ad is primarily selling (one phrase)
- `emotional_hook` — aspiration / safety / returns / ease / trust / fomo / none
- `clarity_score` — 1–5 (5 = crystal clear what the app is and why to install)
- `what_works` — list of specific strengths
- `what_missing` — list of specific gaps (e.g. "no yield number", "no trust signal")
- `suggested_headline_tests` — 3 alternative headlines ≤ 30 chars

**Synthesis (Claude, free-form):**
All ads + per-ad analysis sent together. Output:
- What high-CTR/conversion ads have in common
- What low-CTR ads are missing
- 5 copy angles to test (with headline + description examples)
- Creative strategy recommendation (2-3 sentences)

**Graceful degradation:**
Gates on `AWS_ACCESS_KEY_ID`. If absent: returns raw copy data only (no analysis),
report section shows copy table without LLM columns.

**Known: APP_AD assets in GAQL use a different field path than RSA**
- RSA: `ad_group_ad.ad.responsive_search_ad.headlines`
- APP_AD: `ad_group_ad.ad.app_ad.headlines` — completely separate field
- Previous `get_ad_performance()` only selected RSA fields → empty copy for all app ads
- Fixed: both field paths now selected; parsed by `ad.type_.name` branch

---

## Report Generator Utility (`skills/report.py`)

### Decision: Rule-based Markdown report auto-generated from campaign data
**Date:** Mar 14 2026
**Status:** ✅ Implemented

**What was built:** `skills/report.py` — `generate(data: dict) -> str` takes the dict from
`campaign_analysis.run()` and produces a full Markdown report string. `agent.py` calls it
after campaign analysis and saves to `exports/campaign_report_{date}.md`.

**Report sections:**
1. **Overall Account Summary** — WoW table; auto-derives true CPA from SETUP_SECURE_PIN_SUCCESS and install CPA from first_open by scanning `in_app_actions_breakdown` event names
2. **Per-campaign breakdown** — primary event composition table + auto-diagnosis block
3. **Full conversion funnel** — all tracked events with CPAs, duplicate tagging, notes
4. **Measurement Issues** — auto-detected from data (see detection rules below)
5. **Prioritised Recommendations** — P0/P1/P2 derived from data
6. **Channel & Device split** — compact tables

**Auto-diagnosis rules (per campaign):**
- `first_open` share > 80% of primary conversions → "Effectively an install campaign"
- `first_open` share 50–80% → "Install-heavy bidding"
- `in_app_purchase` primary events < 50/month estimated → "Too sparse for Smart Bidding"
- `budget_util_pct` >= 95% → "Budget capped"
- `budget_util_pct` < 50% → "Under-delivering / bid strategy pullback"
- `spend_wow_pct` <= -30% → "Spend collapse — bid strategy confidence"

**Duplicate Firebase detection logic:**
For each `yubi-invest` prefixed action in `in_app_actions_breakdown`, extract the event
name suffix and check if a matching `Aspero Fixed Income` event exists. If counts are within
10% of each other → flag as "DUPLICATE — same users as Aspero property" in funnel table and
raise a P0 Measurement Issue.

**Decision: Rule-based first, LLM narrative layer later**
Built deterministic rule-based report first to establish a stable, testable baseline.
LLM (AWS Bedrock / Claude) will be added as a separate `skills/insights.py` on top for
narrative synthesis — same architecture as the funnel-optimization-agent's `reporter.py`.

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

| # | Item | Priority | Status |
|---|---|---|---|
| 1 | Link `KYC_BANK_VERIFIED_PD` + `_REVERSE_PD` to BankVerified Google Ads campaign | P0 | ⏳ Pending (Google Ads side) |
| 2 | Fix duplicate Firebase property tracking (yubi-invest vs Aspero property) | P0 | ⏳ Pending (Google Ads side) |
| 3 | Add `KYC_READY_FOR_TRADE` as conversion action for Smart Bidding signal | P1 | ⏳ Pending (Google Ads side) |
| 4 | Switch primary conversion from `VERIFY_OTP_SUCCESS` → `SETUP_SECURE_PIN_SUCCESS` | P1 | ⏳ Pending (Google Ads side) |
| 5 | Investigate PaymentSuccess -52.9% spend WoW drop | P1 | ⏳ Monitor after #3 fix |
| 6 | Build report generator utility (`skills/report.py`) | P2 | ✅ Done (Mar 14 2026) |
| 7 | Build Skill 2: creative analysis — own Google App Ad copy (`skills/creative_analysis.py`) | P2 | ✅ Done (Mar 14 2026) |
| 8 | Build `business_context.md` for growth marketing agent LLM system prompt | P2 | ⏳ Pending |
| 9 | Build Skill 3: competitor creative analysis via Meta Ad Library | P3 | ⏳ Pending |
| 10 | Add image analysis to Skill 2 (authenticated CDN fetch + Claude Vision) | P3 | ⏳ Pending |
