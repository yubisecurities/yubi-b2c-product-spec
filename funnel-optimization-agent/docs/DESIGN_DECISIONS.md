# Agent Design Decisions & Brainstorming Log

This file captures key architectural choices, product reasoning, and open questions
discussed during the build of the Aspero Funnel Optimization Agent.
Updated incrementally — newest entries at the top.

---

## Executive Briefing Report (Two-Report Architecture)

### Decision: Pure Python executive report posted first, detailed Block Kit/LLM report second
**Date:** Mar 13 2026
**Status:** ✅ Implemented

**Problem statement:**
The existing Block Kit report is data-rich but not executive-friendly. The CEO/CPO/CMO audience
needs a verdict-first, ~18-line morning briefing — not a table-first data dump.

**Decision: Two reports, same channel, sequential posting**

```
Report 1 (exec briefing):   pure Python → verdict-first text → posted first
Report 2 (detailed):        Block Kit / LLM fallback → full table → posted second
```

Both reports post to the same `SLACK_WEBHOOK_URL`. No separate webhook needed during testing.

**Why pure Python for the exec report (not LLM):**

| Option | Verdict |
|--------|---------|
| A: LLM via AWS Bedrock | Needs AWS IAM setup, introduces non-determinism, may vary tone day to day |
| B: LLM via Anthropic SDK | Needs separate Anthropic console account + new API key |
| C: Pure Python template | ✅ Chosen — deterministic, always runs, consistent format execs can pattern-match |

Executives reading a daily briefing benefit from *consistency*, not prose quality.
The same layout every day means faster scanning. A rule-based template guarantees this.

**Exec report format (18 lines):**
```
*Aspero Signup Briefing — Fri 13 Mar 2026*   🟢/🟡/🔴
──────────────────────────────────────────
*Signups:* 312  (+8.3% WoW)
*Yesterday:* 44 (slightly above daily average of 41)
*Trend:* 3rd consecutive week of growth
*Audience:* Premium+iOS = 47% of signups — healthy mix
──────────────────────────────────────────
*KYC Funnel (offset cohort, 7-day window)*
• KYC Start:    71.2%  (+2.1pp WoW)
• KYC Done:     58.4%  (-0.8pp WoW)
──────────────────────────────────────────
*Needs Attention*
• 🔴 Android OTP→Email: 24.3% (below 26% warning threshold)
──────────────────────────────────────────
*Wins*
• ✅ Google SSO adoption: 28.4% (Day 7 of 30, target: 40%)
──────────────────────────────────────────
*Funnel by Segment*
```Segment         Mob→Em   Em→PIN   →KYCSt   →KYCDo
Low Android       38.2%    82.1%    61.2%    52.3%
...```
```

**Status logic:** 🟢 = no critical alerts, 🟡 = warnings present, 🔴 = critical alerts

**Consecutive trend detection:** Compares current-week WoW % to prior-prior week WoW % to detect
"3rd consecutive week of growth/decline" — requires no extra API calls (prior-prior signup count
already fetched for WoW calculation).

**Yesterday context:** Shown as "above/below/well below daily average" (average = cur_signup / 7).
"Well below" = yesterday < 70% of average. Adds reading context without requiring a separate API call.

**NOT done and why:**
- ❌ Separate Slack channel for exec report — same channel for testing; can split later
- ❌ LLM for exec briefing — consistency > prose; execs pattern-match the format daily
- ❌ Yesterday KYC snapshot — KYC is a lagged conversion (days to complete), daily snapshot is noisy
  and not comparable to same-session events like signup. Not shown anywhere in exec report.

---

## KYC Funnel Tracking

### Decision: Offset window cohort (signups 8–14d ago → completions 1–7d ago)
**Date:** Mar 13 2026
**Status:** ✅ Implemented

**KYC events:**
- `KYC_RISKDETAILS_SUBMIT` = KYC start (first risk details form submitted)
- `KYC_READY_FOR_TRADE` = KYC complete (account activated and ready to trade)

**Why offset window (not rolling 7d for headline metrics):**
KYC completion is a lagged conversion — users typically complete it days after signup, not in the
same session. Using the same 7-day window for both signups and KYC completions would mix cohorts:
recent signups who haven't had time to complete KYC would drag down the completion rate.

**Offset window logic:**
```
current_period:       today-7d  → today-1d  (7 days)
prior_signup_cohort:  today-14d → today-8d  (7 days — signups who had 7d to start KYC)
prior_prior_cohort:   today-21d → today-15d (7 days — for WoW comparison)

kyc_start_pct  = KYC_RISKDETAILS_SUBMIT [today-14d → today-8d] / signups [today-14d → today-8d]
kyc_done_pct   = KYC_READY_FOR_TRADE    [today-7d  → today-1d] / KYC_RISKDETAILS_SUBMIT [today-14d → today-8d]
```
Numerator and denominator are from *different* date windows, intentionally.
The denominator (signups 8–14d ago) represents the cohort that *entered* KYC; the numerator
(completions 1–7d ago) represents what *came out* of that cohort. This correctly measures the
7-day conversion window that users actually have.

User confirmed: 7 days is the appropriate completion window for Aspero's users.

**WoW calculation:** Shift both windows back by 7 days. Same offset logic applied.

**API calls for KYC (4 total, segmentation API — NOT funnel API):**
```
[13] KYC_RISKDETAILS_SUBMIT  today-14d → today-8d  (current cohort starts)
[14] KYC_READY_FOR_TRADE     today-7d  → today-1d  (current period completions)
[15] KYC_RISKDETAILS_SUBMIT  today-21d → today-15d (prior cohort starts, for WoW)
[16] KYC_READY_FOR_TRADE     today-14d → today-8d  (prior period completions, for WoW)
```

**Why NOT Funnel API for KYC steps:**
The `n` (conversion window) parameter on the Funnel API causes HTTP 400. Without it, the Funnel
API uses Amplitude's default conversion window which may not match our 7-day requirement.
Segmentation API calls per event give us full control over the date range.
Step-level KYC health monitoring (flagging individual steps down by >X%) is a future item.

**KYC funnel V2 (Mar 10 2026):**
Wet signature step (`KYC_WET_SIGNATURE_VERIFIED`) was added between Liveness and eSign.
`KYC_DEMAT_VERIFIED` moved from step 5 to step 8 (after eSign). Total steps: 8 → 9.

Handled via `kyc_v2_recent` flag:
```python
days_since_kyc_v2 = (date.today() - KYC_FUNNEL_V2_DATE).days   # KYC_FUNNEL_V2_DATE = 2026-03-10
kyc_v2_recent     = 0 <= days_since_kyc_v2 <= 14               # shows context note for 14 days, then disappears
```
The exec report auto-appends `_(funnel restructured Mar 10 — completion rate may be temporarily lower)_`
while `kyc_v2_recent` is True, then silently removes it after 14 days.

**KYC by device type (rolling 7d — NOT offset window):**
For the funnel tier table (relative comparison), rolling 7d is used instead of offset window.
Rationale: The table shows *relative* performance across tiers (Low vs Mid vs Premium Android),
not absolute cohort conversion. Rolling window is simpler and good enough for tier ranking.
Offset window for this table would require 2× more API calls with minimal added insight.

**Total API calls: 18 (up from 12)**
```
[1–4]   Device-type funnels — OTP/SSO paths, current + prior 7d (funnel API)
[5–12]  Milestone event totals — 4 events × current + prior 7d (segmentation API)
[13–16] KYC cohort — start + complete × current + prior offset windows (segmentation API)
[17–18] KYC by device type — starts + completions, rolling 7d (segmentation API)
```

**NOT done and why:**
- ❌ No yesterday KYC snapshot — KYC takes days to complete; a single-day number is noisy and
  not comparable to same-session signup events
- ❌ No offset window for device-tier KYC — rolling 7d is sufficient for relative tier comparison;
  offset adds 2+ API calls for marginal accuracy gain in a ranking table
- ❌ No step-level KYC health monitoring (yet) — would need events for each intermediate KYC step
  and a WoW comparison. Added to Open Questions for future build.
- ❌ No separate KYC Slack report — KYC metrics added to existing exec report (same channel,
  same message); a dedicated KYC deep-dive report may come later

---

## LLM Report Generation via AWS Bedrock

### Decision: Replace Block Kit template with Claude narrative report (via AWS Bedrock)
**Date:** Mar 2026
**Status:** ✅ Implemented

**Problem with rule-based Block Kit reports:**
The original report used hardcoded `build_message_v2()` — Slack Block Kit with templated
strings and pre-computed alert/win bullets. It could show numbers but couldn't interpret
them. Every insight required hand-written `if/else` rules, and the output read like a
spreadsheet dump, not a morning briefing.

**Decision:** Python fetches all Amplitude data + computes derived metrics + pre-formats
the device tier table. Claude (via AWS Bedrock) writes the full narrative Slack report
using the writing guide as system prompt.

**Architecture (clean separation of concerns):**
```
Python:   fetch → compute → structure data dict → pre-format table
Claude:   interpret → narrate → write Slack report
```
Claude receives a structured JSON payload and the full writing guide (7 sections +
formatting rules + critical rules) as the system prompt. It outputs plain Slack mrkdwn.

**Why Bedrock over Anthropic SDK:**
- Yubi has AWS access already configured; no separate Anthropic console account needed
- Credentials via standard `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` env vars
- IAM-based access management (can scope permissions precisely)
- Model: `anthropic.claude-opus-4-5`, region: `ap-south-1`

**Fallback:** If `AWS_ACCESS_KEY_ID` is not set OR if the Bedrock call fails for any
reason (network error, model not enabled, quota exceeded), the agent automatically falls
back to the legacy Block Kit `build_message_v2()` format. The workflow never fails silently
due to missing LLM credentials.

**New secrets required in GitHub Actions:**
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
(Previous `ANTHROPIC_API_KEY` removed)

---

## SSO Quality: A Better Path, Not Just a Feature Metric

### Insight: SSO adoption should be framed as "users choosing the better flow"
**Date:** Mar 2026
**Status:** ✅ Encoded in system prompt

**Data (Amplitude funnel, Mar 6–13 2026):**

| Path | Steps | End-to-end conversion | Completion rate after click |
|------|-------|-----------------------|-----------------------------|
| Email OTP | 6 | 50.3% (923/1,835) | 69.6% (923/1,326) |
| Google SSO | 4 | 18.4% (337/1,835) | 89.6% (337/376) |

**Key insight:**
The 18.4% end-to-end SSO rate is NOT because SSO is worse — it's because only 20.5% of
users click the Google button. Of those who do, 89.6% complete it. OTP has a 6-step flow
with ~30% abandonment after clicking; SSO has a 4-step flow with ~10% abandonment.

**The problem is discovery, not quality.** Most users default to OTP because it's the
primary/familiar CTA. They're taking a harder path that loses more of them.

**Why this matters for the report:**
Before this insight, SSO adoption was framed as "we want more users to use this new feature."
After: "X% of users are still taking the harder 6-step flow when a faster, higher-success
option is available to them." The gap to 40% target = users unnecessarily at higher risk of
abandonment.

**OTP flow events (6 steps):**
`EMAIL_PAGE_VIEW → EMAIL_PAGE_VERIFY_CLICKED → EMAIL_PAGE_VERIFY_API_SUCCESS`
`→ EMAIL_VERIFY_OTP_PAGE_VIEW → EMAIL_VERIFY_OTP_ENTERED → EMAIL_VERIFY_OTP_SUCCESS`

**SSO flow events (4 steps):**
`EMAIL_PAGE_VIEW → GOOGLE_VERIFY_CLICK → GOOGLE_VERIFY_SUCCESS → SSO_VERIFICATION_SUCCESS`

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
- `AWS_ACCESS_KEY_ID` — For Claude via Bedrock (LLM report). Optional — falls back to Block Kit if absent.
- `AWS_SECRET_ACCESS_KEY` — Paired with above

**Manual trigger:** `workflow_dispatch` enabled — use GitHub Actions → Run workflow for
ad-hoc runs or testing.

---

## Open Questions / Future Work

| # | Question | Notes |
|---|----------|-------|
| 1 | Expand `DEVICE_TIER_PATTERNS` to classify more models | Would reduce the Unknown Android bucket. Could periodically audit the `unknown_android` rows in Amplitude to find common unclassified models and add them |
| 2 | ~~Post-KYC funnel tracking~~ | ✅ Partially resolved (Mar 13 2026) — KYC start% and KYC done% now tracked via offset window cohort. KYC by device tier added to funnel table. Remaining: step-level health monitoring (see #6) and KYC→investment funnel |
| 3 | ~~OTP "new users only" via API~~ | ✅ Resolved — `EMAIL_PAGE_VIEW` matches first-time OTP at 99.5% and is accessible via API. Used as denominator for `New%` column. See EMAIL_PAGE_VIEW section above. |
| 4 | City/geography breakdown | Business context says Metro + Tier-1 is target; could add city-level breakdown if Amplitude has geo data |
| 5 | ~~SSO adoption 30-day tracker~~ | ✅ Resolved — `SSO_LAUNCH_DATE = date(2026, 3, 6)` in config.py; days since launch and days remaining auto-computed in alerts/wins |
| 6 | Step-level KYC health monitoring | Flag if any individual KYC step's conversion drops >X% WoW. Requires events for each intermediate step (9 steps in V2 funnel). Options: Funnel API (current period, no `n` param) or Segmentation per step with WoW. Decision pending. |
| 7 | AWS Bedrock credentials for detailed LLM report | `AWS_ACCESS_KEY_ID` + `AWS_SECRET_ACCESS_KEY` not yet added to GitHub Actions secrets. Detailed report currently runs Block Kit fallback. Add when IAM access is available. |
