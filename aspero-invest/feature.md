# Feature Spec — Aspero Invest: Personalised Bond Discovery

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
Landing (Hero + Widget)
  ├── User sets amount (slider or quick chip)
  ├── User selects duration (6M / 12M / 18M / 2Y+)
  ├── User selects risk appetite (Conservative / Moderate / Aggressive)
  └── Floating CTA activates → "Find X Bonds"
        ↓
Results Page (top 5 bonds)
  ├── Filter chips show active criteria
  ├── Sort by: Best Match / Highest Returns / Lowest Returns / Safest First
  ├── Save Strip → prompts sign-up (unauthenticated)
  ├── "View All X Bonds" → All Bonds page
  └── "Invest Now" on a card:
        ├── Logged in → investment flow
        └── Not logged in → Auth modal → investment flow
              ↓
All Bonds Page (grouped: Great / Good / Fair)
  └── Same sort controls + filter chips
```

---

## 6. Sections & Components

### 6.1 Navigation Bar
- **Position:** Sticky top, `z-index: 200`
- **Height:** 62px
- **Background:** `#0D1F16` (darkest green)
- **Content:** Logo (`aspero.` with green dot accent `#01D464`) + user greeting (right)

---

### 6.2 Hero Section
- **Background:** Linear gradient `155deg → #0D1F16 → #0f2a1c → #1A3C34`
- **Decorative radial glows:** Two `::before`/`::after` overlays for depth
- **Content:**
  - Tag chip: `✦ Personalized for you` (green pill, `rgba(1,212,100,0.1)` bg)
  - H1: `"Find bonds that match your investment goals"` (42px, 800 weight, white; keyword in `#01D464`)
  - Subtitle: 16px, `rgba(255,255,255,0.5)`, max-width 480px
- **Padding:** 52px top, 64px bottom
- **Max content width:** 900px centered

---

### 6.3 Investment Widget (Core Interaction)

White card overlapping the hero bottom (`margin-bottom: -56px`).

- **Style:** White bg, `border-radius: 24px`, `box-shadow: 0 16px 56px rgba(0,0,0,0.14)`
- **Padding:** 36px all sides
- **Max width:** 900px centered

#### 6.3a. Amount Field
| Element | Detail |
|---|---|
| Label | `INVESTMENT AMOUNT` — 11px, 700 weight, uppercase, `#667085` |
| Display | Large ₹ amount — 44px, 800 weight, `#101828` |
| Slider | Custom range input with gradient fill (`#018E43 → #01D464`), 8px track height |
| Thumb | 24px white circle, 3px green border, shadow on hover |
| Scale | Logarithmic: `₹10K → ₹50L` (markers at ₹10K, ₹50K, ₹1L, ₹5L, ₹10L, ₹50L) |
| Quick chips | ₹10K · ₹25K · ₹50K · ₹1L · ₹5L · ₹10L · ₹25L — pill buttons, active = light green bg |
| Default | ₹10,000 (leftmost position, ₹10K chip active) |

#### 6.3b. Duration Pills
| Element | Detail |
|---|---|
| Label | `INVESTMENT DURATION` |
| Options | `6M` · `12M` · `18M` · `2Y+` |
| Active state | Light green bg (`#C9FFEA`), green border (`#6EE7A0`), green text, subtle shadow |
| Inactive | `#FAFAFA` bg, no border |
| Default | None selected |
| Behaviour | Tapping a chip activates it; page auto-scrolls to Risk Appetite section (smooth, 120ms delay, only if risk not yet selected) |

Duration values (months): `6M=6`, `12M=12`, `18M=18`, `2Y+=24`

#### 6.3c. Risk Appetite Cards
3-column grid of tappable cards.

| Risk | Icon | Rating Range | Return Range |
|---|---|---|---|
| Conservative | 🛡️ | AAA, AA+, AA, AA- | Dynamic — derived from live bond data |
| Moderate | ⚖️ | A+, A, A- | Dynamic — derived from live bond data |
| Aggressive | 🚀 | BBB+, BBB, BB & below | Dynamic — derived from live bond data |

- **Active state:** Green border, light green bg, shadow `0 4px 18px rgba(1,142,67,0.14)`
- **Return badge:** Small green pill at bottom of each card — shows computed `ytmMin–ytmMax% p.a.`
- **Unavailable state:** If no bonds exist for a bucket, card is greyed out and shows `"Currently unavailable"`
- **Single bond:** If only 1 bond exists in a bucket, show single value e.g. `"13.5% p.a."` instead of a range
- **Default:** None selected

#### 6.3c-i. Dynamic YTM Range Logic

YTM ranges on risk cards are **never hardcoded**. They are computed from live bond data on every homepage load.

**Data source:** `GET /bonds/buckets`

**Response shape:**
```json
{
  "conservative": { "ytmMin": 7.5, "ytmMax": 9.8, "count": 7 },
  "moderate":     { "ytmMin": 10.2, "ytmMax": 12.5, "count": 5 },
  "aggressive":   { "ytmMin": null, "ytmMax": null, "count": 0 }
}
```

**Backend computation rule per bucket:**
```
ytmMin = min(ret) of all active bonds in that bucket
ytmMax = max(ret) of all active bonds in that bucket
```

**Rating → Bucket mapping (owned by backend):**
```
conservative: AAA, AA+, AA, AA-
moderate:     A+, A, A-
aggressive:   BBB+, BBB, BB, BB-, and below
```

**Frontend behaviour:**
| Condition | Behaviour |
|---|---|
| `count > 1` | Show `"ytmMin–ytmMax% p.a."` |
| `count == 1` | Show `"ytmMin% p.a."` (single value) |
| `count == 0` | Disable card, show `"Currently unavailable"` |

---

### 6.4 Floating CTA (Bottom Bar)

Fixed to the bottom of the viewport. Appears/activates once user has interacted.

| State | Appearance |
|---|---|
| No selection | "Select your preferences above" — greyed out, "Show Bonds" button locked (disabled) |
| Has selection | "**N** bonds match your criteria" + criteria summary (e.g., `₹1L · 12M · Moderate`) — green "Show Bonds" button active |

- **Background:** `#0D1F16`
- **Height:** ~72px, padding 0 24px
- **Button:** Green CTA, 100px width, disabled = `#A8F8D5`
- **Locked state:** `cursor: not-allowed`
- **On locked tap:** Toast specifying only the missing selection(s):
  - Both missing → `"Please select your duration & risk appetite to find bonds"`
  - Duration only → `"Please select your duration to find bonds"`
  - Risk only → `"Please select your risk appetite to find bonds"`
  - Missing field group(s) pulse with amber glow (2 flashes, 1.6s); toast auto-dismisses after 2.8s; resets timer on repeated taps

---

### 6.5 Results Page

Shown after tapping "Show Bonds". Full-page overlay (no nav tabs visible).

#### Header / Sub-header
- Back button (`← Change Filters`) → returns to main widget
- Filter chips row: Shows active criteria (amount, duration, risk) — amount chip is editable (opens Amount Bottom Sheet)
- Count pill: `"X found"`
- Sort dropdown: Best Match / Highest Returns / Lowest Returns / Safest First
- **Always visible** while scrolling (position: sticky, below nav)

#### Bond Cards Grid
Responsive grid (3-col desktop → 1-col mobile). Shows top 5 results.

Each bond card contains:

| Element | Detail |
|---|---|
| Bond abbreviation | First 2 initials in light green circle (e.g., `HF` for HDFC Finance) |
| Match badge | Color-coded pill: `✦ Great Match` / `◆ Good Match` / `· Fair Match` |
| Bond name | 15px, 700 weight |
| Category | 12px, secondary text |
| Yield % | 28px, 800 weight, green (`#018E43`) |
| YTM · Duration | `"YTM · 12 Months"` — secondary label |
| Rating badge | Color-coded by rating tier (see Rating Colors below) |
| Min. Investment | Formatted amount (e.g., `₹10K`) |
| Estimated returns | Light green tint box — `"Est. returns on ₹1L"` + `"+₹8,500"` — live-updates when amount changes |
| CTA | `"Invest Now →"` — full-width green button |

#### No Match State
When 0 bonds match: shows empty state with icon + "No bonds match" heading + prompt to go back and adjust preferences.

#### Save Strip (between results + view all)
- Bell icon in rounded box
- Headline + "Sign up free" CTA
- Logged-in: strip is hidden
- Post sign-up: transforms to "You're in! Results saved." (green confirmation)

#### View All Row
Shown if > 5 results: `"Showing top 5 · N total matches"` + `"View All Matching Bonds →"` link

---

### 6.6 All Bonds Page

Full-page view of all filtered bonds, grouped by match tier.

**Groups:**
- `✦ Great Match` (score ≥ 70) — green header
- `◆ Good Match` (score ≥ 40) — yellow header
- `· Fair Match` (score < 40) — grey header

Each group shows: group label + count badge + bond cards grid.

- **Back action:** `"← Back to Home"` returns to Selection screen
- **Sticky subheader:** Same pattern as Results screen — title + count + sort + filter chips (including editable amount chip)
- **Sort dropdown:** Same options as Results screen, synced with Results sort state

---

### 6.7 Amount Bottom Sheet (Mobile)

Slides up from bottom when user taps the amount filter chip on results page.

- **Content:** Same slider + quick chips as widget
- **CTA:** `"Update Results"` — syncs results live on close
- **Overlay:** Semi-transparent backdrop; tapping outside does nothing (user must tap CTA to confirm)
- **Post-close:** `"✓ Updated"` badge animates on every visible est. returns box (fade in + scale pop → hold 700ms → fade out, total 1.4s)
- **Note:** Badge fires even if amount was not changed (harmless)

---

### 6.8 Auth Modal

Triggered when unauthenticated user taps "Invest Now".

- **Pattern:** Centred modal on desktop; bottom sheet on mobile (≤520px)
- **Overlay:** Blur backdrop (6px); tapping outside or pressing Escape dismisses

#### Bond Context Bar
- Green strip at top showing: bond abbreviation icon + bond name + `"Investing ₹X"`
- Purpose: reinforces why the user is being asked to sign in

#### Unified Sign In / Sign Up Flow
- **No tabs** — single screen handles both new and existing users
- **Heading:** `"Enter your mobile number"`
- **Sub-text:** `"We'll send you a one-time password to verify. New or existing user — we'll take care of the rest."`
- **Input:** 🇮🇳 +91 prefix + 10-digit mobile number field
- **Validation:** Must be exactly 10 digits; inline error `"Please enter a valid 10-digit mobile number"` if not
- **CTA:** `"Continue →"` — triggers simulated OTP verification
- **Terms note:** `"By continuing, you agree to Aspero's Terms & Privacy Policy"`

#### Post-Verification Flow
1. Button switches to `"Verifying…"` (disabled, 1.5s simulated)
2. Form replaced by success state: ✓ icon + `"You're in!"` + `"Redirecting you to complete your investment…"`
3. After 1.8s: modal closes → original `investNow` call fires with stored bond + amount
4. `isLoggedIn` flag set to `true` for session — subsequent "Invest Now" taps go straight through

---

## 7. Bond Matching Algorithm

### Scoring (max 65 pts)

```
Duration Score (max 40 pts):
  |bond.dur - selected_months| == 0   → +40
  |bond.dur - selected_months| <= 6   → +22
  |bond.dur - selected_months| <= 12  → +10
  else                                → +0

Risk Score (max 25 pts):
  |risk_rank_diff| == 0  → +25
  |risk_rank_diff| == 1  → +10
  else                   → +0

Risk rank: conservative=0, moderate=1, aggressive=2
```

### Filtering Rules
- Only bonds where `bond.min ≤ selected_amount` are shown
- Only bonds within 1 risk tier step of selected risk are shown (e.g., Moderate → shows Conservative, Moderate, Aggressive; Aggressive → shows Moderate, Aggressive only)

### Match Labels
| Score | Label | Badge Color |
|---|---|---|
| ≥ 70 | ✦ Great Match | `#BBFFD4` bg / `#14532D` text |
| ≥ 40 | ◆ Good Match | `#FEF9C3` bg / `#78350F` text |
| < 40 | · Fair Match | `#F3F4F6` bg / `#4B5563` text |

### Sort Modes
| Mode | Logic |
|---|---|
| Best Match | `score DESC` |
| Highest Returns | `ret DESC` |
| Lowest Returns | `ret ASC` |
| Safest First | `rs ASC` (risk score 1=safest, 8=riskiest) |

---

## 8. Amount Slider — Logarithmic Scale

```
sliderToAmt(pct) = round(exp(log(10000) + (pct/100) × (log(5000000) - log(10000))))
amtToSlider(amt) = ((log(amt) - log(10000)) / (log(5000000) - log(10000))) × 100
```

Estimated returns formula:
```
earnings = round(amount × (ret / 100) × (durMonths / 12))
```

---

## 9. Edge Cases

| Scenario | Handling |
|---|---|
| No bonds match filters | Empty state on Results screen with prompt to go back |
| Only 1–4 bonds match | Results screen shows all of them, "View All" hidden |
| User taps locked CTA repeatedly | Toast resets its timer on each tap (no stacking) |
| User changes amount after seeing results | Amount sheet live-updates cards; "✓ Updated" badge on close |
| Amount is higher than all bond minimums | All bonds pass the amount filter; score drives ranking |
| User opens amount sheet, closes without changing | "✓ Updated" badge still fires (harmless) |
| User taps "Invest Now" when not logged in | Auth modal opens with bond context pre-filled |
| User dismisses auth modal | pendingInvest cleared; no partial state left |
| User taps "Invest Now" after logging in | Proceeds directly — no modal shown again in session |
| Invalid phone number submitted | Inline error shown; form not submitted |
| Bucket has 0 active bonds | Risk card greyed out, shows "Currently unavailable" |
| Bucket has exactly 1 bond | YTM badge shows single value e.g. `"13.5% p.a."` |

---

## 10. Navigation Map

```
Selection ──(CTA active + tap)──► Results ──(View All)──► All Bonds
    ▲                                │   ▲                    │
    └────────(← Change Filters)──────┘   │                    │
    ◄────────────────────(← Back to Home)┘────────────────────┘
                                     │
                             (💰 chip tap)
                                     ▼
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

## 11. Rating Color System

| Rating | Background | Text |
|---|---|---|
| AAA | `#D1FAE5` | `#065F46` |
| AA+ | `#DBEAFE` | `#1E40AF` |
| AA | `#EDE9FE` | `#5B21B6` |
| AA- | `#FEF3C7` | `#92400E` |
| A+ | `#FFEDD5` | `#9A3412` |
| A | `#FEE2E2` | `#991B1B` |
| A- | `#FCE7F3` | `#831843` |
| BBB / BBB+ | `#F3F4F6` | `#374151` |

---

## 12. Design Tokens

| Token | Value | Usage |
|---|---|---|
| `--g` | `#018E43` | Primary CTA, yield text, active states |
| `--g-hov` | `#01B756` | CTA hover |
| `--g-act` | `#016530` | CTA pressed |
| `--g-dis` | `#A8F8D5` | CTA disabled |
| `--g-hi` | `#01D464` | Highlight green (hero accent, save strip) |
| `--g-dk` | `#1A3C34` | Dark green hero surface |
| `--g-dkr` | `#0D1F16` | Darkest green (nav, floating CTA) |
| `--g-lt` | `#C9FFEA` | Light green tint (active chips, risk card bg) |
| `--bg` | `#F2F4F7` | Screen background |
| `--card` | `#FFFFFF` | Card background |
| `--t1` | `#101828` | Primary text |
| `--t2` | `#667085` | Secondary text |
| `--t3` | `#98A2B3` | Muted text |
| `--border` | `#D0D5DD` | Border color |

**Typography:** Sofia Pro (commercial) → fallback Inter. Weights: 400, 500, 600, 700, 800.

**Border radii:** 24px (widget/cards), 16px (risk cards), 100px (pills/chips), 12px (rating badges).

**Shadows:**
- Default: `0 4px 20px rgba(0,0,0,0.07)`
- Large: `0 16px 56px rgba(0,0,0,0.14)` (widget card)

---

## 13. Responsive Breakpoints

| Breakpoint | Changes |
|---|---|
| > 600px | 3-col risk grid, full descriptions visible |
| ≤ 760px | Risk grid → single column; dual-field → stacked; bond grid → single column; hero font shrinks |
| ≤ 520px | Hero H1 → 28px; nav padding → 20px; widget padding → 20px; chips wrap; risk grid → 3-col compact, description hidden; auth modal → bottom sheet |

---

## 14. Animations

| Animation | Duration | Trigger |
|---|---|---|
| Slider thumb scale | 0.12s | Hover/drag |
| Chip/pill transition | 0.13s | Select |
| Risk card transition | 0.15s | Select |
| Field pulse (validation) | 1.6s ease-out | Missing field on CTA click |
| Auth modal slide+scale | 0.28s | Open |
| Bottom sheet slide | 0.32s cubic-bezier | Open/close |
| "Updated" badge pop | 1.45s | Post-sheet close |
| Floating CTA count update | CSS transition | Bond count change |

---

## 15. Bond Data Schema

```typescript
interface Bond {
  id: number;
  name: string;        // e.g. "HDFC Ltd"
  cat: string;         // e.g. "Housing Finance"
  rating: string;      // e.g. "AAA", "AA+", "A-", "BBB+"
  rs: number;          // Risk score 1–8 (1=safest, 8=riskiest)
  ret: number;         // Annual yield % e.g. 8.5
  dur: number;         // Duration in months e.g. 12
  min: number;         // Min investment ₹ e.g. 10000
  // Note: API does not return a `risk` field. Bucket classification
  // (conservative / moderate / aggressive) is derived from `rating`
  // by the backend using the agreed mapping in section 6.3c-i.
}
```

**Bucket summary endpoint:**
```typescript
interface BucketSummary {
  conservative: { ytmMin: number | null; ytmMax: number | null; count: number };
  moderate:     { ytmMin: number | null; ytmMax: number | null; count: number };
  aggressive:   { ytmMin: number | null; ytmMax: number | null; count: number };
}
```

---

## 16. Out of Scope (v1)

- Real-time bond pricing / live API data (v1 uses curated static data)
- Watchlist / save bonds (requires auth — post-login feature)
- Comparison view (select multiple bonds side-by-side)
- Push notifications for new bond alerts
- SIP / recurring investment setup
- Detailed bond prospectus within this flow
- Persisting preferences across sessions (local storage or API)
- "Why this bond?" explainer drawer
- Full OTP delivery and verification (backend integration)
