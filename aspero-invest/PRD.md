# PRD — Aspero Invest: Personalised Bond Recommendation

**Product:** Aspero
**Feature:** Personalised Bond Discovery & Recommendation
**Status:** Prototype Complete
**Last Updated:** February 2026

---

## 1. Overview

Users on Aspero have difficulty discovering bonds that match their personal financial goals. The fixed bond catalogue requires users to manually evaluate each bond across multiple dimensions (return, tenure, rating, risk) — creating friction and drop-off.

This feature replaces the browse experience with a guided preference-capture flow that surfaces a ranked shortlist of bonds tailored to the user's investment context. Unauthenticated users are gated at the point of investment intent, not before — reducing sign-up friction.

---

## 2. Goals

| Goal | Metric |
|------|--------|
| Reduce time-to-first-investment | Users reach a matched bond list in < 60 seconds |
| Increase bond discovery engagement | CTR on bond cards ↑ vs. unfiltered catalogue |
| Reduce decision paralysis | % of sessions ending without any bond click ↓ |
| Improve first-investment conversion | % of new users who invest within session ↑ |

---

## 3. Non-Goals

- Does not replace the full bond catalogue (always accessible via "View All")
- Does not provide personalised financial advice or portfolio recommendations
- Does not persist user preferences across sessions (v1)
- Does not cover SIP or basket investing flows (separate features)

---

## 4. User Stories

**As a first-time user,**
I want to quickly tell Aspero what I'm looking for
So that I don't have to manually scan every bond to find one that fits me.

**As a returning user,**
I want to see bonds that match my risk comfort and investment horizon
So that I can make confident investment decisions faster.

**As a conservative investor,**
I want to understand what "Conservative" means in terms of expected returns
So that I can make a selection without needing financial expertise.

**As a user who hasn't decided yet,**
I want clear feedback when I haven't filled in everything
So that I know exactly what's missing before I can see results.

**As a user browsing bond results,**
I want to adjust my investment amount without leaving the results view
So that I can see how earnings change without losing my place.

**As an unauthenticated user who taps Invest Now,**
I want a single frictionless sign-in screen
So that I can complete my first investment without navigating away.

---

## 5. User Flow

```
Homepage / App Entry
        │
        ▼
┌─────────────────────┐
│   Selection Screen  │
│  ─────────────────  │
│  Investment Amount  │  ← Slider + quick-pick chips (default ₹10K)
│  Investment Duration│  ← Pill chips: 6M / 12M / 18M / 2Y+ (no default)
│                     │    Auto-scrolls to Risk section on selection
│  Risk Appetite      │  ← 3 cards with return range badge (no default)
│                     │
│  [CTA — locked]     │  ← Disabled until Duration + Risk both selected
└─────────────────────┘
        │  (all selections made)
        ▼
┌─────────────────────┐
│   Results Screen    │
│  ─────────────────  │
│  [Sticky subheader] │  ← Title + Count + Sort + Filter chips (always visible)
│   💰 ₹10K ✎ chip   │  ← Taps open Amount Edit Sheet
│  Top 5 bond cards   │
│  [View All →]       │
└─────────────────────┘
        │  (💰 chip tapped)
        ▼
┌─────────────────────┐
│  Amount Edit Sheet  │
│  ─────────────────  │
│  ₹ value display    │
│  Log-scale slider   │
│  Quick-pick chips   │
│  [Update Results]   │  ← Closes sheet; "✓ Updated" badge flashes on each
└─────────────────────┘     est. returns box

        │  (View All tapped)
        ▼
┌─────────────────────┐
│  All Bonds Screen   │
│  ─────────────────  │
│  All matched bonds  │
│  Sort dropdown      │
│  [← Back to Home]   │
└─────────────────────┘

        │  (Invest Now tapped — unauthenticated)
        ▼
┌─────────────────────┐
│    Auth Modal       │
│  ─────────────────  │
│  Bond context bar   │  ← Shows bond name + amount being invested
│  "Enter mobile no." │
│  🇮🇳 +91 input      │
│  [Continue →]       │  ← Validates 10 digits → simulates OTP → proceeds
└─────────────────────┘
```

---

## 6. Feature Specification

### 6.1 Selection Screen

#### Investment Amount
- **Input type:** Log-scale range slider + quick-pick chips
- **Range:** ₹10,000 – ₹50,00,000
- **Default:** ₹10,000 (leftmost position)
- **Quick-pick chips:** ₹10K (default active), ₹25K, ₹50K, ₹1L, ₹5L, ₹10L, ₹25L
- **Markers on slider:** ₹10K · ₹50K · ₹1L · ₹5L · ₹10L · ₹50L
- **Behaviour:** Slider and chips are in sync — selecting a chip snaps the slider; moving the slider deselects all chips

#### Investment Duration
- **Input type:** Pill chips (single-select)
- **Options:** 6 Months · 12 Months · 18 Months · 2 Years+
- **Default:** None selected
- **Behaviour:** Tapping a chip activates it; page auto-scrolls to Risk Appetite section (smooth, 120ms delay, only if risk not yet selected)

#### Risk Appetite
- **Input type:** Card chips (single-select, 3-column grid)
- **Options:**

| Option | Icon | Description | Return Range |
|--------|------|-------------|--------------|
| Conservative | 🛡️ | AAA & AA+ rated. Capital safety first. | 7.5 – 10% p.a. |
| Moderate | ⚖️ | AA rated bonds. Balanced risk-reward. | 10 – 13% p.a. |
| Aggressive | 🚀 | A & BBB rated. Higher returns, higher risk. | 13 – 16% p.a. |

- **Default:** None selected
- **Return range badge:** Always visible on the card (green pill), helps users understand expected YTM without needing financial literacy
- **Mobile (≤520px):** Description hidden, return badge remains visible below the name

#### Floating CTA
- **Always visible** at the bottom of the screen
- **Locked state** (duration OR risk not selected):
  - Greyed out, `cursor: not-allowed`
  - Primary text: "Select your preferences above"
  - No secondary text
- **Active state** (both duration AND risk selected):
  - Green background, clickable
  - Primary text: "X bonds match your criteria"
  - Secondary text: selected filter summary (e.g. "₹10K · 12 Mo · Conservative")
- **On locked tap:**
  - Toast message specifying only the missing selection(s):
    - Both missing → "Please select your duration & risk appetite to find bonds"
    - Duration only missing → "Please select your duration to find bonds"
    - Risk only missing → "Please select your risk appetite to find bonds"
  - Missing field group(s) pulse with a subtle amber glow animation (2 flashes, 1.6s)
  - Toast auto-dismisses after 2.8s

---

### 6.2 Results Screen

- **Triggered by:** Tapping the active CTA
- **Navigation:** Full-screen overlay (z-index above selection screen)
- **Back action:** "← Change Filters" returns to Selection screen

#### Sticky Subheader
- **Always visible** while scrolling through bond cards (position: sticky, below nav)
- Contains: "Matching Bonds" title · count pill · sort dropdown · filter chips
- **Editable amount chip:** `💰 ₹10,000 ✎` — tapping opens the Amount Edit Sheet
- Duration and Risk chips are display-only

#### Bond Cards (Top 5)
Each card displays:
- Bond abbreviation badge + match badge (Great Match / Good Match / Partial)
- Bond name + category
- YTM % (large) with label "YTM · X Months"
- Credit rating badge
- Minimum investment amount
- **Est. returns box:** "Est. returns on ₹X" + "+₹Y" (live-updates when amount changes)
  - On amount change: "✓ Updated" badge flashes in right side of the box (1.4s, then disappears)
- **Invest Now →** button (gated by auth state)

#### View All
- Shown when total matches > 5
- "Showing top 5 · N total matches" label
- "View All Matching Bonds →" button navigates to All Bonds screen

#### Empty State
- Icon + "No bonds match" heading
- Instructional text to go back and adjust preferences

---

### 6.3 Amount Edit Sheet

- **Triggered by:** Tapping the `💰 ₹X ✎` filter chip on Results or All Bonds screen
- **Pattern:** Bottom sheet (slides up from bottom, 320ms transition)
- **Overlay:** Semi-transparent backdrop; tapping outside does nothing (user must tap CTA to confirm)

#### Content
- **Amount display:** Large ₹ value (live-updates as slider/chips change)
- **Slider:** Same log-scale range as Selection screen (₹10K – ₹50L)
- **Quick-pick chips:** Same 7 options as Selection screen (synced)
- **CTA:** Full-width "Update Results" green button — closes sheet

#### Live Update Behaviour
- Bond cards re-render in real time as the slider moves
- On sheet close → "✓ Updated" badge animates on every visible est. returns box (fade in + scale pop → hold 700ms → fade out, total 1.4s)
- Main page slider and chips stay in sync with sheet state

---

### 6.4 Auth Modal

- **Triggered by:** Tapping "Invest Now →" when user is unauthenticated
- **Pattern:** Centred modal on desktop; bottom sheet on mobile (≤520px)
- **Overlay:** Blur backdrop (6px); tapping outside or pressing Escape dismisses

#### Bond Context Bar
- Green strip at top of modal showing:
  - Bond abbreviation icon (2-letter badge)
  - Bond name
  - "Investing ₹X" (current amount from state)
- Purpose: reinforces why the user is being asked to sign in

#### Unified Sign In / Sign Up Flow
- **No tabs** — single screen handles both new and existing users
- **Heading:** "Enter your mobile number"
- **Sub-text:** "We'll send you a one-time password to verify. New or existing user — we'll take care of the rest."
- **Input:** 🇮🇳 +91 prefix + 10-digit mobile number field
- **Validation:** Must be exactly 10 digits; inline error if not
- **CTA:** "Continue →" — triggers simulated OTP verification
- **Terms note:** "By continuing, you agree to Aspero's Terms & Privacy Policy"

#### Post-Verification Flow
1. Button switches to "Verifying…" (disabled, 1.5s simulated)
2. Form replaced by success state: ✓ icon + "You're in!" + "Redirecting you to complete your investment…"
3. After 1.8s: modal closes → original `investNow` call fires with the stored bond + amount
4. `isLoggedIn` flag set to `true` for the session — subsequent "Invest Now" taps go straight through

---

### 6.5 All Bonds Screen

- **Triggered by:** "View All" button on Results screen
- **Navigation:** Full-screen overlay (z-index above Results screen)
- **Back action:** "← Back to Home" returns to Selection screen
- **Content:** All matched bonds (not limited to 5), same card format as Results screen
- **Sticky subheader:** Same pattern as Results screen — title + count + sort + filter chips (including editable amount chip)
- **Sort dropdown:** Same options as Results screen, synced with Results sort state

---

## 7. Matching & Scoring Logic

### Filtering
Bonds are filtered by:
1. **Minimum investment:** `bond.minInvestment ≤ state.amount` (always applied)
2. **Risk:** If risk is selected, bonds outside ±1 risk tier are excluded

### Scoring (Match Score)
Bonds are ranked by a composite score (0–65 pts):

| Dimension | Exact match | Close match | Far match |
|-----------|------------|-------------|-----------|
| Duration  | +40 pts (0 mo diff) | +22 pts (≤6 mo diff) | +10 pts (≤12 mo diff) |
| Risk      | +25 pts (same tier) | +10 pts (±1 tier) | 0 pts |

### Match Badge Thresholds
| Badge | Score |
|-------|-------|
| ⭐ Great Match | ≥ 55 pts |
| ✓ Good Match | ≥ 30 pts |
| ~ Partial | < 30 pts |

---

## 8. Sort Options

| Option | Sort Key |
|--------|----------|
| Best Match | Score (desc) |
| Highest Returns | YTM % (desc) |
| Lowest Returns | YTM % (asc) |
| Safest First | Risk score (asc) — AAA first |

---

## 9. Bond Data Schema

```json
{
  "id": 1,
  "name": "HDFC Bank Bonds",
  "cat": "Private Bank",
  "rating": "AAA",
  "riskScore": 1,
  "ret": 8.5,
  "dur": 12,
  "min": 10000,
  "risk": "conservative"
}
```

---

## 10. Edge Cases

| Scenario | Handling |
|----------|----------|
| No bonds match filters | Empty state on Results screen with prompt to go back |
| Only 1–4 bonds match | Results screen shows all of them, "View All" hidden |
| User taps locked CTA repeatedly | Toast resets its timer on each tap (no stacking) |
| User changes amount after seeing results | Amount sheet live-updates cards; "✓ Updated" badge on close |
| Amount is higher than all bond minimums | All bonds pass the amount filter; score drives ranking |
| User opens amount sheet, closes without changing | "✓ Updated" badge still fires (harmless; amount unchanged) |
| User taps "Invest Now" when not logged in | Auth modal opens with bond context pre-filled |
| User dismisses auth modal | pendingInvest cleared; no partial state left |
| User taps "Invest Now" after logging in | Proceeds directly — no modal shown again in session |
| Invalid phone number submitted | Inline error shown; form not submitted |

---

## 11. Responsive Behaviour

| Breakpoint | Changes |
|------------|---------|
| > 600px | 3-col risk grid, full descriptions visible |
| ≤ 600px | Risk grid → single-column rows (icon left, text right) |
| ≤ 520px | Risk grid → 3-col compact, description hidden, return badge smaller (10px) |
| ≤ 520px | Auth modal → bottom sheet (border-radius on top corners only) |
| All sizes | Duration pills wrap, CTA always pinned to bottom, sticky subheader always visible |

---

## 12. Navigation Map

```
Selection ──(CTA active + tap)──► Results ──(View All)──► All Bonds
    ▲                                │   ▲                    │   ▲
    └────────(← Change Filters)──────┘   │                    │   │
    ◄────────────────────(← Back to Home)┘───────────────────┘   │
                                     │                            │
                             (💰 chip tap)                (💰 chip tap)
                                     ▼                            ▼
                              Amount Sheet ──(Update Results)──► [closes]
                                     │
                             (Invest Now tap — unauth)
                                     ▼
                              Auth Modal ──(Continue + OTP)──► investNow()
                                     │
                               (× / Escape)
                                     ▼
                                 [dismissed]
```

---

## 13. Out of Scope (v2 Considerations)

- Persisting preferences across sessions (local storage or API)
- "Why this bond?" explainer drawer
- Compare mode (side-by-side bond comparison)
- Watchlist / Save bond
- Full OTP delivery and verification (backend integration)
- Push notifications for matched new bond listings
