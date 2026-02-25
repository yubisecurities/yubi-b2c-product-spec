# Feature: Find Your Bond — Aspero Invest Homepage

## Overview

An interactive, personalized bond discovery tool that replaces the traditional static homepage. Users configure three inputs — investment amount, duration preference, and risk appetite — and instantly see a curated, scored list of matching bonds with estimated returns. The goal is to reduce friction from "I want to invest" to "I found my bond" in a single screen.

---

## User Flow

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

## Sections & Components

### 1. Navigation Bar
- **Position:** Sticky top, `z-index: 200`
- **Height:** 62px
- **Background:** `#0D1F16` (darkest green)
- **Content:** Logo (`aspero.` with green dot accent `#01D464`) + user greeting (right)

---

### 2. Hero Section
- **Background:** Linear gradient `155deg → #0D1F16 → #0f2a1c → #1A3C34`
- **Decorative radial glows:** Two `::before`/`::after` overlays for depth
- **Content:**
  - Tag chip: `✦ Personalized for you` (green pill, `rgba(1,212,100,0.1)` bg)
  - H1: `"Find bonds that match your investment goals"` (42px, 800 weight, white; keyword in `#01D464`)
  - Subtitle: 16px, `rgba(255,255,255,0.5)`, max-width 480px
- **Padding:** 52px top, 64px bottom
- **Max content width:** 900px centered

---

### 3. Investment Widget (Core Interaction)

White card overlapping the hero bottom (`margin-bottom: -56px`).

- **Style:** White bg, `border-radius: 24px`, `box-shadow: 0 16px 56px rgba(0,0,0,0.14)`
- **Padding:** 36px all sides
- **Max width:** 900px centered

#### 3a. Amount Field
| Element | Detail |
|---|---|
| Label | `INVESTMENT AMOUNT` — 11px, 700 weight, uppercase, `#667085` |
| Display | Large ₹ amount — 44px, 800 weight, `#101828` |
| Slider | Custom range input with gradient fill (`#018E43 → #01D464`), 8px track height |
| Thumb | 24px white circle, 3px green border, shadow on hover |
| Scale | Logarithmic: `₹10K → ₹50L` (markers at ₹10K, ₹50K, ₹1L, ₹5L, ₹10L, ₹50L) |
| Quick chips | ₹10K · ₹25K · ₹50K · ₹1L · ₹5L · ₹10L · ₹25L — pill buttons, active = light green bg |

#### 3b. Duration Pills
| Element | Detail |
|---|---|
| Label | `INVESTMENT DURATION` |
| Options | `6M` · `12M` · `18M` · `2Y+` |
| Active state | Light green bg (`#C9FFEA`), green border (`#6EE7A0`), green text, subtle shadow |
| Inactive | `#FAFAFA` bg, no border |

Duration values (months): `6M=6`, `12M=12`, `18M=18`, `2Y+=24`

#### 3c. Risk Appetite Cards
3-column grid of tappable cards.

| Risk | Icon | Rating Range | Return Range |
|---|---|---|---|
| Conservative | 🛡️ | AAA & AA+ | 7.5–10% p.a. |
| Moderate | ⚖️ | AA rated | 10–13% p.a. |
| Aggressive | 🚀 | A & BBB | 13–16% p.a. |

- **Active state:** Green border, light green bg, shadow `0 4px 18px rgba(1,142,67,0.14)`
- **Return badge:** Small green pill at bottom of each card

---

### 4. Floating CTA (Bottom Bar)

Fixed to the bottom of the viewport. Appears/activates once user has interacted.

| State | Appearance |
|---|---|
| No selection | "Select your preferences above" — greyed out, "Show Bonds" button locked (disabled) |
| Has selection | "**N** bonds match your criteria" + criteria summary (e.g., `₹1L · 12M · Moderate`) — green "Show Bonds" button active |

- **Background:** `#0D1F16`
- **Height:** ~72px, padding 0 24px
- **Button:** Green CTA, 100px width, disabled = `#A8F8D5`

---

### 5. Results Page

Shown after tapping "Show Bonds". Full-page overlay (no nav tabs visible).

#### Header / Sub-header
- Back button → returns to main widget
- Filter chips row: Shows active criteria (amount, duration, risk) — amount chip is editable (opens Amount Bottom Sheet)
- Count pill: `"X found"`
- Sort dropdown: Best Match / Highest Returns / Lowest Returns / Safest First

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
| Estimated returns | Light green tint box — `"Est. returns on ₹1L"` + `"+₹8,500"` |
| CTA | `"Invest Now →"` — full-width green button |

#### No Match State
When 0 bonds match: shows top 3 bonds by risk proximity with message "No exact matches right now — here are top picks for you."

#### Save Strip (between results + view all)
- Bell icon in rounded box
- Headline + "Sign up free" CTA
- Logged-in: strip is hidden
- Post sign-up: transforms to "You're in! Results saved." (green confirmation)

#### View All Row
Shown if > 5 results: `"View all X bonds →"` link

---

### 6. All Bonds Page

Full-page view of all filtered bonds, grouped by match tier.

**Groups:**
- `✦ Great Match` (score ≥ 70) — green header
- `◆ Good Match` (score ≥ 40) — yellow header
- `· Fair Match` (score < 40) — grey header

Each group shows: group label + count badge + bond cards grid.

---

### 7. Auth Modal

Triggered when unauthenticated user taps "Invest Now" or "Sign up free".

- **Context header:** Bond abbreviation + bond name + `"Investing ₹X"` (shown for Invest Now flow, hidden for Save flow)
- **Title/CTA text:** Changes based on trigger (`"Enter your mobile number"` vs `"Save your results"`)
- **Input:** Indian phone number (`+91` prefix, 10-digit validation)
- **Error state:** `"Please enter a valid 10-digit mobile number"` inline
- **Success state:** Checkmark icon + `"You're in!"` + redirect message
- **Dismiss:** Outside click or Escape key

---

### 8. Amount Bottom Sheet (Mobile)

Slides up from bottom when user taps the amount filter chip on results page.

- **Content:** Same slider + quick chips as widget
- **CTA:** `"Update Results"` — syncs results live on close
- **Post-close:** "✓ Updated" badge briefly appears on all estimated returns boxes

---

## Bond Matching Algorithm

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

### Match Labels
| Score | Label | Badge Color |
|---|---|---|
| ≥ 70 | ✦ Great Match | `#BBFFD4` bg / `#14532D` text |
| ≥ 40 | ◆ Good Match | `#FEF9C3` bg / `#78350F` text |
| < 40 | · Fair Match | `#F3F4F6` bg / `#4B5563` text |

### Filtering Rules
- Only bonds where `bond.min ≤ selected_amount` are shown
- Only bonds within 1 risk tier step of selected risk are shown (e.g., Moderate → shows Conservative, Moderate, Aggressive; Aggressive → shows Moderate, Aggressive only)

### Sort Modes
| Mode | Logic |
|---|---|
| Best Match | `score DESC` |
| Highest Returns | `ret DESC` |
| Lowest Returns | `ret ASC` |
| Safest First | `rs ASC` (risk score 1=safest, 8=riskiest) |

---

## Amount Slider — Logarithmic Scale

Amount slider uses log scale for better UX across a large range (₹10K–₹50L).

```
sliderToAmt(pct) = round(exp(log(10000) + (pct/100) × (log(5000000) - log(10000))))
amtToSlider(amt) = ((log(amt) - log(10000)) / (log(5000000) - log(10000))) × 100
```

Estimated returns formula:
```
earnings = round(amount × (ret / 100) × (durMonths / 12))
```

---

## Rating Color System

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

## Design Tokens

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

## Responsive Breakpoints

| Breakpoint | Changes |
|---|---|
| ≤ 760px | Risk grid → single column; dual-field → stacked; bond grid → single column; hero font shrinks |
| ≤ 520px | Hero H1 → 28px; nav padding → 20px; widget padding → 20px; chips wrap |

---

## Animations

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

## Bond Data Schema

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
  risk: 'conservative' | 'moderate' | 'aggressive';
}
```

---

## Out of Scope (v1)

- Real-time bond pricing / live API data (v1 uses curated static data)
- Watchlist / save bonds (requires auth — post-login feature)
- Comparison view (select multiple bonds side-by-side)
- Push notifications for new bond alerts
- SIP / recurring investment setup
- Detailed bond prospectus within this flow
