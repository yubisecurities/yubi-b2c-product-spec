# Agent Design Decisions & Brainstorming Log

This file captures key architectural choices, product reasoning, and open questions
discussed during the build of the Aspero Funnel Optimization Agent.
Updated incrementally — newest entries at the top.

---

## EMAIL_PAGE_VIEW as New-User OTP Proxy → Accurate New% and Em% Columns

### Decision: Replace single OTP→Em% with New% + Em% using EMAIL_PAGE_VIEW as denominator
**Date:** Mar 2025
**Status:** ✅ Implemented

**The problem with the old OTP→Em% metric:**
```
Old:  OTP→Em% = EMAIL_VERIFIED / VERIFY_OTP_SUCCESS
                                  ↑ includes returning users → denominator inflated → ~42% (misleading)
```
`VERIFY_OTP_SUCCESS` fires for every login (new + returning users), but `EMAIL_VERIFIED`
only fires for new users. Dividing new-user completions by a mixed denominator produces
a ratio that has no clear meaning and consistently reads low (~42% vs ~75% in dashboard).

**The insight (confirmed in Amplitude):**
`EMAIL_PAGE_VIEW` matches `VERIFY_OTP_SUCCESS (Event Historical Count = 1)` at **99.5%**.
Post-OTP, all new users are routed to the email verification page — both those who will
complete via OTP and those who will use Google SSO (SSO flow: user lands on email page →
taps "Sign in with Google" → `SSO_VERIFICATION_SUCCESS`). `EMAIL_PAGE_VIEW` fires for
both paths, making it a valid denominator for all new-user email conversions.

**Why this works via API:**
`EMAIL_PAGE_VIEW` is a standard event with no special filter needed — unlike
`Event Historical Count = 1` which is a UI-only filter unavailable in the Amplitude API.

**Solution: 4-step funnels + two conversion columns:**

Funnels changed from 3-step to 4-step (no extra API calls):
```
Funnel 1: OTP → EMAIL_PAGE_VIEW → EMAIL_VERIFY_OTP_SUCCESS → SIGNUP
Funnel 2: OTP → EMAIL_PAGE_VIEW → SSO_VERIFICATION_SUCCESS  → SIGNUP
```

**Final table design (after iteration):**

```
Tier              Mob. Verif   Email ✓   Signup    Em%    PIN%
──────────────────────────────────────────────────────────────
Low Android            1,510       950      820   62.9%  86.3%
Mid Android              890       720      680   80.9%  94.4%
Premium Android          310       290      280   93.5%  96.6%
iOS                      180       165      160   91.7%  97.0%
Web                       80        65       55   81.3%  84.6%
──────────────────────────────────────────────────────────────
TOTAL                  2,970     2,190    1,995   73.7%  91.1%
```

| Column | Source | Formula | What it tells you |
|--------|--------|---------|-------------------|
| `Mob. Verif` | `EMAIL_PAGE_VIEW` (funnel step[1]) | raw count | New users who completed mobile verification (99.5% proxy for first-time OTP) |
| `Email ✓` | `EMAIL_VERIFY_OTP_SUCCESS + SSO_VERIFICATION_SUCCESS` | raw count | New users who completed email verification (both paths combined) |
| `Signup` | `SETUP_SECURE_PIN_SUCCESS` | raw count | New users who completed signup |
| `Em%` | — | `Email ✓ / Mob. Verif` | Email completion rate among new users (UX friction signal) |
| `PIN%` | — | `Signup / Email ✓` | Signup completion rate among email-verified users |

**Design iterations:**
1. Original: `OTP ✓ | Eml OTP | Eml SSO | Signup | OTP→Em% | Em→PIN%` — OTP→Em% was misleading (~42%) because OTP denominator included returning users
2. Intermediate: Split into `New% + Em%` columns, kept OTP/SSO split — `New%` (ratio) felt confusing; OTP/SSO split added noise
3. Final: Dropped raw OTP column (returning users not useful here), merged OTP+SSO into `Email ✓`, kept `Mob. Verif` as the count (not ratio). Cleaner and tells the complete new-user journey.

**Other format changes made alongside this:**
- `Registrations` renamed to `Signups` throughout (header, trend section, alerts, wins)
- Removed `📧 OTP 77.7% · SSO 22.3%` from header summary — OTP/SSO split cluttered the header and rendered the email emoji as an image icon in Slack
- Alert section title changed from `⚠️ Needs Attention Today` to `Needs Attention` (emoji in section title renders as image in Slack Block Kit; individual alert lines still carry severity emoji)

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

## device_family vs device_type for Funnel Grouping

### Decision: Use device_type (not device_family) — improve classifier to handle hardware codes
**Date:** Mar 2026
**Status:** ✅ Implemented (reverted after live failure)

**Background:** The Amplitude UI shows "Device Family" as a breakdown option, returning
marketing names like "Samsung Galaxy S22". We assumed the API parameter for this was
`device_family` and switched the Funnel API `group_by` to it.

**What happened:** `device_family` is NOT a valid Amplitude Funnel API `g` parameter.
The API returned HTTP 200 with empty data — no error, just silently zero results.
This caused the entire report to show 0 signups, 0 OTP, no device table.

**Correct parameter:** `device_type` is the valid `g` parameter for the Funnel API.
The Amplitude UI's "Device Family" display is a UI-layer enrichment, not a separate API property.

**`device_type` returns hardware model codes** for many events:

| `device_type` from API | Actual device          |
|------------------------|------------------------|
| `SM-S901B`             | Samsung Galaxy S22     |
| `SM-A525F`             | Samsung Galaxy A52s    |
| `2201116TG`            | Xiaomi Redmi Note 11   |
| `RMX3511`              | Realme 9 SE            |

**Fix:** Keep `device_type` in the API call. Add hardware model code patterns to
`classify_device_type()` in `insights.py` BEFORE the marketing-name patterns:

| Code pattern          | Tier            | Examples                          |
|-----------------------|-----------------|-----------------------------------|
| `SM-S*`, `SM-F*`      | Premium Android | Galaxy S22/S23/S24, Fold, Flip    |
| `SM-A*`, `SM-M*`      | Mid Android     | Galaxy A52, M32                   |
| `SM-J*`               | Low Android     | Galaxy J2/J7                      |
| `^2[012]\d{8,}`       | Mid Android     | Redmi Note 11 (2201116TG), POCO X |
| `RMX\d{4}`            | Mid Android     | Realme 9/10/11 (RMX3511)          |
| `CPH\d{4}`            | Mid Android     | OPPO A/F series                   |
| `V[12]\d{3}`/`T\d{4}` | Mid Android     | Vivo V/T series                   |

**Remaining Unknown Android:** Devices that match no hardware code pattern AND no
marketing-name pattern — genuinely obscure OEMs or unusual SDK configurations.

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

**SSO adoption tracking:** Google SSO launched **6 March 2026** to reduce friction on iOS
(known abandonment point for email OTP). Target: 40%+ adoption within 30 days (by ~5 Apr 2026).
`SSO_LAUNCH_DATE = date(2026, 3, 6)` in `config.py` — days since launch and days remaining
are auto-computed in alerts and wins messages.

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
| 3 | ~~OTP "new users only" via API~~ | ✅ Resolved — `EMAIL_PAGE_VIEW` matches first-time OTP at 99.5% and is accessible via API. Used as denominator for `New%` column. See EMAIL_PAGE_VIEW section above. |
| 4 | City/geography breakdown | Business context says Metro + Tier-1 is target; could add city-level breakdown if Amplitude has geo data |
| 5 | ~~SSO adoption 30-day tracker~~ | ✅ Resolved — `SSO_LAUNCH_DATE = date(2026, 3, 6)` in config.py; days since launch and days remaining auto-computed in alerts/wins |
