# Agent Design Decisions & Brainstorming Log

This file captures key architectural choices, product reasoning, and open questions
discussed during the build of the Aspero Funnel Optimization Agent.
Updated incrementally — newest entries at the top.

---

## Device Tier Classification

### Decision: Show "Unknown Android†" as a separate row with footnote
**Date:** Mar 2025
**Status:** ✅ Implemented

**Problem:** Some Android devices in Amplitude's `device_type` field don't match any of
the Low/Mid/Premium patterns in `DEVICE_TIER_PATTERNS`. These "Other Android" devices were
appearing as a large, unexplained bucket in the Slack table.

**Options considered:**
| Option | Verdict |
|--------|---------|
| Default to Mid Android | ❌ Rejected — can't justify inflating Mid with unknown models |
| Default to Low Android | ❌ Rejected — same issue, directionally better but still wrong |
| Keep as "Other Android" | ❌ Rejected — user explicitly doesn't want this label |
| Show as "Unknown Android†" with footnote | ✅ Chosen |

**Rationale for footnote approach:**
- We genuinely don't know the tier — it's honest to say so
- But the footnote gives business context: *"Most likely Low tier — flagship and popular
  mid-range models are explicitly listed. If a device doesn't match any known pattern,
  it is almost certainly not a premium or mid-range device."*
- This is better than silently mis-attributing users to the wrong tier

**Classification logic (in `insights.py → classify_device_type()`):**
1. Apple devices → `ios`
2. Desktop OS signals → `web`
3. Android tiers checked in order: `premium_android` → `mid_android` → `low_android`
4. Known vendor but unmatched model (Samsung, Redmi, etc.) → `unknown_android`
5. Generic "android" string or unknown OEM → `unknown_android`

**Why premium-first order matters:**
`DEVICE_TIER_PATTERNS` is checked premium → mid → low. This prevents e.g. "Samsung Galaxy
S22" matching a mid pattern before hitting the premium pattern.

---

## Funnel API vs Segmentation API

### Decision: Use Funnel API for device-tier table (eliminates Em→PIN >100%)
**Date:** Mar 2025
**Status:** ✅ Implemented

**Problem:** Initial implementation used independent Segmentation API calls per event
(OTP, Email, Signup) grouped by `device_type`. This caused `Em→PIN %` to exceed 100%
for iOS (123.5%) and Web (144.4%).

**Root cause:** Timing boundary artefact. Each segmentation query captures a different
user population within the 7-day window. A user who verified email on Day 6 might be
counted in Email but not OTP if they did OTP on Day 0 (outside the window). Independent
queries don't track the same user across steps.

**Fix:** Two Funnel API calls (`/api/2/funnels`) with `group_by=device_type`:
1. OTP → `EMAIL_VERIFY_OTP_SUCCESS` → `SETUP_SECURE_PIN_SUCCESS`
2. OTP → `SSO_VERIFICATION_SUCCESS` → `SETUP_SECURE_PIN_SUCCESS`

The Funnel API tracks the **same user** across all steps within the window.
`cumulativeRaw[i+1] ≤ cumulativeRaw[i]` is mathematically guaranteed → Em→PIN always ≤ 100%.

**Why two funnels?** Email OTP and SSO are mutually exclusive paths to email verification.
Signup = funnel1.step3 + funnel2.step3 (no overlap expected).

**API calls: 7 total**
- [1–2] Device-type funnels for current 7d (OTP→Email→Signup via OTP path and SSO path)
- [3–6] Event totals for prior 7d (WoW)
- [7] Event totals for yesterday (daily snapshot)

---

## OTP→Email Rate: Known Discrepancy vs Amplitude Dashboard

### Decision: Accept the discrepancy, document it
**Date:** Mar 2025
**Status:** ✅ Accepted limitation

**Problem:** In the Amplitude dashboard, OTP→Email rate looks healthy (~72%). In our
agent's table, it appears much lower (~42%).

**Root cause:** The Amplitude UI lets you filter by `Event Historical Count = 1` — i.e.
"first time this user ever fired this event." This filters returning users and shows only
new users going through OTP for the first time. The Amplitude API (`/api/2/events/segmentation`)
does **not** support this filter.

**Impact:** The OTP column in our table includes both new and returning users. OTP→Email %
appears artificially low because many OTP verifications are returning users who won't
proceed to email (they're already registered).

**Decision:** Accept this as a known limitation. OTP column = all mobile verifications
(new + returning). Email & Signup columns = new users only. This is documented in the
table subtitle and in the code comments.

**Why not fix it?** Would require a separate "new users only OTP" segmentation, which
isn't directly available via API. The Funnel API approach is the closest proxy.

**Cross-device switching:** User confirmed cross-pollination (e.g. OTP on mobile, signup
on web) is small enough to ignore. Funnel API solves the >100% problem without needing
to account for this.

---

## Report Format

### Decision: 4-section compact Slack report
**Date:** Mar 2025
**Status:** ✅ Implemented (v2 format)

**Sections:**
1. **Header** — Date, health status, registration count, WoW delta, OTP/SSO split
2. **Yesterday Snapshot | 7-Day Trend** — Two-column fields block
3. **Device Tier Table** — Fixed-width code block with 7 columns
4. **Needs Attention + Wins** — Business-context-aware alerts and positive signals

**Table columns:** Tier | OTP ✓ | Eml OTP | Eml SSO | Signup | OTP→Em% | Em→PIN%

**Column separator:** 2-space (`S = "  "`) between every column for readability.

**Why code block for the table?** Slack doesn't support HTML tables or true fixed-width
in regular markdown. A ` ``` ` code block renders in monospace — the only way to achieve
aligned columns.

---

## Business Context: Target Audience

### Decision: Alert when Low+Mid Android dominates registrations
**Date:** Mar 2025
**Status:** ✅ Implemented in `generate_alerts_v2()`

**Context (from `business_context.md`):**
- Aspero = SEBI-registered OBPP (bond investment platform)
- Target audience = Premium Android + iOS, age 30–55, ₹15L+ income
- Low Android = budget devices <₹10K, very low LTV, CAC likely exceeds LTV
- Average investment ticket = ₹50K–₹5L → each lost Premium/iOS registration = significant LTV

**Alert thresholds:**
| Condition | Severity |
|-----------|----------|
| Premium+iOS Em→PIN < 80% | 🔴 Critical |
| Low+Mid Android > 60% of signups | 📊 Audience quality warning |
| Premium+iOS Em→PIN 80–90% | ⚠️ Warning |
| Registrations down > 20% WoW | 🔴 Critical |
| Registrations down 10–20% WoW | ⚠️ Warning |
| Low Android OTP→Email < 10% | 💡 Info (mostly returning users) |

**SSO adoption tracking:** Google SSO launched ~7 days ago to reduce friction on iOS
(known abandonment point for email OTP). Target: 40%+ adoption within 30 days.

---

## Automation: GitHub Actions

### Decision: Daily 8:00 AM IST via GitHub Actions
**Date:** Mar 2025
**Status:** ✅ Deployed

**Schedule:** `cron: "30 2 * * *"` = 02:30 UTC = 08:00 IST

**Workflow:** `.github/workflows/daily-signup-report.yml`

**Secrets required (set in repo Settings → Secrets → Actions):**
- `AMPLITUDE_API_KEY` — Amplitude Project 506002
- `AMPLITUDE_SECRET_KEY`
- `SLACK_WEBHOOK_URL` — Incoming webhook for the target channel

**Manual trigger:** `workflow_dispatch` enabled — use GitHub Actions → Run workflow for
ad-hoc runs or testing.

---

## Open Questions / Future Work

| # | Question | Notes |
|---|----------|-------|
| 1 | Expand `DEVICE_TIER_PATTERNS` to classify more models | Would reduce the Unknown Android bucket. Could periodically audit the `unknown_android` rows in Amplitude to find common unclassified models and add them |
| 2 | Post-KYC funnel tracking | Current funnel is pre-KYC (registration only). KYC completion → investment is the next funnel stage not yet tracked |
| 3 | OTP "new users only" via API | `Event Historical Count = 1` not available in API — workaround would be a user-level query (expensive) |
| 4 | City/geography breakdown | Business context says Metro + Tier-1 is target; could add city-level breakdown if Amplitude has geo data |
| 5 | SSO adoption 30-day tracker | Current note hardcodes "launched 7 days ago" — should eventually auto-compute days since SSO launch |
