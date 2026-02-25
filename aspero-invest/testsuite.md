# Test Suite — Aspero Invest: Find Your Bond

**Feature:** Personalised Bond Discovery & Recommendation
**Ref:** PRD.md §6–12, feature.md
**Last Updated:** February 2026

---

## Test Scope

| Area | Coverage |
|---|---|
| Amount Slider & Quick Chips | Logarithmic scale, sync, defaults |
| Duration Pills | Selection, auto-scroll trigger |
| Risk Cards | Selection, active state, display |
| Floating CTA | Locked / active states, toast, pulse |
| Bond Matching Algorithm | Score, filter, sort |
| Results Page | Rendering, top-5 limit, sort, count |
| View All Page | Grouping, sort sync, back navigation |
| No Match / Empty State | Fallback bonds, zero-result state |
| Amount Edit Sheet | Slide-up, live sync, Updated badge |
| Auth Modal | Validation, context bar, success flow |
| Navigation | Page transitions, back actions |
| Responsive | 760px, 520px breakpoints |
| Edge Cases | From PRD §10 |
| Accessibility | Keyboard nav, ARIA, focus management |

---

## Test IDs

Format: `[AREA]-[NN]`
Example: `SLIDER-01`, `MATCH-03`, `AUTH-02`

---

## 1. Amount Slider & Quick Chips

### SLIDER-01 — Default state on load
**Precondition:** Page freshly loaded
**Steps:** Observe the amount field
**Expected:**
- Slider is at leftmost position
- Amount display shows `₹10,000`
- `₹10K` quick chip is in active state
- All other chips are inactive

---

### SLIDER-02 — Slider moves amount display
**Steps:** Drag slider thumb to midpoint (~50%)
**Expected:**
- Amount display updates in real time (no lag)
- Displayed value is approximately `₹2,24,000` (log midpoint of ₹10K–₹50L)
- No quick chip is active (mid-point doesn't match any chip value)

---

### SLIDER-03 — Logarithmic scale validation
**Steps:** Move slider to 100%
**Expected:**
- Amount shows `₹50,00,000` (₹50L), not a linear extrapolation

**Steps:** Move slider to 0%
**Expected:**
- Amount shows `₹10,000`

---

### SLIDER-04 — Quick chip snaps slider
**Steps:** Click `₹1L` chip
**Expected:**
- Amount display updates to `₹1,00,000`
- Slider thumb moves to the correct log-scale position for ₹1L
- Only `₹1L` chip is active; all others are inactive

---

### SLIDER-05 — Chip active state clears when slider moves away
**Steps:**
1. Click `₹50K` chip (chip goes active)
2. Drag slider slightly left or right
**Expected:**
- `₹50K` chip is no longer active
- Amount display reflects new slider value

---

### SLIDER-06 — All 7 quick chips covered
**Steps:** Click each chip in sequence: ₹10K, ₹25K, ₹50K, ₹1L, ₹5L, ₹10L, ₹25L
**Expected (for each):**
- Only that chip is active
- Amount display matches chip value exactly
- Slider thumb is at the correct log-scale position

---

### SLIDER-07 — Amount formats correctly
| Amount | Expected display |
|---|---|
| ₹10,000 | `₹10,000` |
| ₹1,00,000 | `₹1,00,000` |
| ₹25,00,000 | `₹25,00,000` |

**Steps:** Set each amount via chip
**Expected:** Amount shows in Indian locale format (lakh separators)

---

## 2. Duration Pills

### DUR-01 — Default state (no selection)
**Precondition:** Page freshly loaded
**Expected:**
- No duration pill is active
- All 4 pills (`6M`, `12M`, `18M`, `2Y+`) are visible and inactive

---

### DUR-02 — Single selection
**Steps:** Click `12M`
**Expected:**
- `12M` pill becomes active (green bg + border)
- All other pills are inactive
- CTA shows match count if risk is also selected

---

### DUR-03 — Only one pill active at a time
**Steps:**
1. Click `6M` (active)
2. Click `18M`
**Expected:**
- `18M` is now active
- `6M` is no longer active

---

### DUR-04 — Auto-scroll to Risk section (risk not yet selected)
**Steps:**
1. Ensure no risk card is selected
2. Click any duration pill
**Expected:**
- Page smoothly scrolls to the Risk Appetite section within ~120ms
- Risk section comes into view

---

### DUR-05 — No auto-scroll when risk already selected
**Steps:**
1. Select a risk card first
2. Then click a duration pill
**Expected:**
- Page does NOT auto-scroll (risk section is already complete)

---

## 3. Risk Appetite Cards

### RISK-01 — Default state (no selection)
**Expected:**
- No risk card is active
- All 3 cards visible: Conservative, Moderate, Aggressive
- Each card shows: icon, name, rating range description, return range badge

---

### RISK-02 — Single selection
**Steps:** Click `Moderate`
**Expected:**
- `Moderate` card has active state (green border + `#C9FFEA` bg + shadow)
- Conservative and Aggressive are inactive

---

### RISK-03 — Only one card active at a time
**Steps:**
1. Click `Conservative`
2. Click `Aggressive`
**Expected:**
- `Aggressive` is active
- `Conservative` is inactive

---

### RISK-04 — Return badge always visible
**Expected (for each card):**
- Conservative: `7.5–10% p.a.`
- Moderate: `10–13% p.a.`
- Aggressive: `13–16% p.a.`
- Badge is visible in both active and inactive states

---

### RISK-05 — Active state styling
**Steps:** Click `Conservative`
**Expected:**
- Border: `var(--g)` green
- Background: `#C9FFEA` light green
- Shadow: `0 4px 18px rgba(1,142,67,0.14)`
- Return badge background darkens slightly (`rgba(1,142,67,0.22)`)

---

## 4. Floating CTA

### CTA-01 — Locked by default
**Precondition:** Page freshly loaded (no duration, no risk)
**Expected:**
- CTA bar is visible at bottom
- Primary text: `"Select your preferences above"`
- No secondary text
- Button is disabled / greyed out

---

### CTA-02 — Locked with duration only
**Steps:** Select a duration pill, leave risk unselected
**Expected:**
- CTA remains locked
- Button remains disabled

---

### CTA-03 — Locked with risk only
**Steps:** Select a risk card, leave duration unselected
**Expected:**
- CTA remains locked

---

### CTA-04 — Active when both duration + risk selected
**Steps:** Select `12M` + `Moderate`
**Expected:**
- Primary text: `"X bonds match your criteria"` (X = actual bond count)
- Secondary text: `"₹10K · 12 Mo · Moderate"` (reflects current state)
- Button is active (green)

---

### CTA-05 — Bond count updates when amount changes
**Steps:**
1. Select `12M` + `Aggressive`
2. Set amount to `₹10L` (some bonds require higher min)
3. Then reduce amount to `₹10K`
**Expected:**
- Bond count in CTA primary text changes reactively when amount changes (bonds with min > amount are excluded)

---

### CTA-06 — Toast on locked tap (both missing)
**Steps:**
1. Ensure no duration and no risk selected
2. Tap the locked CTA button
**Expected:**
- Toast appears: `"Please select your duration & risk appetite to find bonds"`
- Duration field group pulses amber (2 flashes over ~1.6s)
- Risk field group pulses amber
- Toast auto-dismisses after 2.8s

---

### CTA-07 — Toast on locked tap (duration only missing)
**Steps:**
1. Select a risk card, leave duration unselected
2. Tap locked CTA
**Expected:**
- Toast: `"Please select your duration to find bonds"`
- Only duration field group pulses

---

### CTA-08 — Toast on locked tap (risk only missing)
**Steps:**
1. Select a duration, leave risk unselected
2. Tap locked CTA
**Expected:**
- Toast: `"Please select your risk appetite to find bonds"`
- Only risk field group pulses

---

### CTA-09 — Toast timer resets on repeated taps
**Steps:**
1. Tap locked CTA (toast appears, timer starts)
2. Wait 1.5s
3. Tap locked CTA again
**Expected:**
- Toast does NOT disappear then reappear
- Timer resets — toast stays for another full 2.8s from the second tap
- Toast does not stack / duplicate

---

### CTA-10 — Secondary text reflects current criteria
**Steps:**
1. Select `6M` + `Conservative` + leave amount at ₹10K
2. Observe secondary text
3. Change amount to ₹5L via chip
4. Observe secondary text again
**Expected:**
- Step 2: `"₹10K · 6 Mo · Conservative"`
- Step 4: `"₹5L · 6 Mo · Conservative"`

---

## 5. Bond Matching Algorithm

### MATCH-01 — Duration exact match scores 40 pts
**Input:** Bond with `dur=12`, selected duration `12M` (12 months)
**Expected:** Duration contribution = **+40 pts**

---

### MATCH-02 — Duration close match (≤6 mo diff) scores 22 pts
**Input:** Bond with `dur=6`, selected duration `12M` (diff = 6 months)
**Expected:** Duration contribution = **+22 pts**

---

### MATCH-03 — Duration medium match (≤12 mo diff) scores 10 pts
**Input:** Bond with `dur=6`, selected duration `18M` (diff = 12 months)
**Expected:** Duration contribution = **+10 pts**

---

### MATCH-04 — Duration far match (>12 mo diff) scores 0 pts
**Input:** Bond with `dur=6`, selected duration `2Y+` (24 months, diff = 18 months)
**Expected:** Duration contribution = **+0 pts**

---

### MATCH-05 — Risk exact match scores 25 pts
**Input:** Bond `risk=moderate`, selected `Moderate`
**Expected:** Risk contribution = **+25 pts**

---

### MATCH-06 — Risk adjacent (±1 tier) scores 10 pts
**Input:** Bond `risk=conservative`, selected `Moderate` (rank diff = 1)
**Expected:** Risk contribution = **+10 pts**

---

### MATCH-07 — Risk far (±2 tiers) scores 0 pts
**Input:** Bond `risk=conservative`, selected `Aggressive` (rank diff = 2)
**Expected:** Risk contribution = **+0 pts**

---

### MATCH-08 — Great Match threshold (score ≥ 70)
**Input:** Bond with dur=12, risk=moderate; selected `12M` + `Moderate`
**Score:** 40 (dur exact) + 25 (risk exact) = **65 pts**
**Expected:** Match badge = **"Good Match"** (note: 65 < 70, so just misses Great)

**Input:** Bond with dur=12, risk=moderate; selected `12M` + `Moderate`, and bond has rs=1
**Note:** Score 65 is just below Great Match threshold per feature.md (≥70), but PRD says ≥55 for Great. Test against the implementation's actual threshold.

---

### MATCH-09 — Amount filter (bond.min > amount excluded)
**Input:** Bond with `min=50000`, amount set to `₹25,000`
**Expected:** Bond is **excluded** from results

**Input:** Same bond, amount set to `₹50,000`
**Expected:** Bond is **included**

---

### MATCH-10 — Risk tier adjacency filter (>1 tier diff excluded)
**Input:** Bond `risk=conservative`, selected `Aggressive` (diff = 2)
**Expected:** Bond is **excluded** from filtered results

**Input:** Bond `risk=conservative`, selected `Moderate` (diff = 1)
**Expected:** Bond is **included**

---

### MATCH-11 — Sort: Best Match (default)
**Steps:** Set duration + risk, observe results default sort
**Expected:** Bonds are ordered by score descending; highest score card is first

---

### MATCH-12 — Sort: Highest Returns
**Steps:** Change sort to `Highest Returns`
**Expected:** Bonds ordered by `ret` descending; highest yield first

---

### MATCH-13 — Sort: Lowest Returns
**Steps:** Change sort to `Lowest Returns`
**Expected:** Bonds ordered by `ret` ascending; lowest yield first

---

### MATCH-14 — Sort: Safest First
**Steps:** Change sort to `Safest First`
**Expected:** Bonds ordered by `rs` ascending; `rs=1` (AAA) comes first

---

### MATCH-15 — Null duration skips duration scoring
**Input:** Duration not selected (null), Risk = Moderate
**Expected:** All bonds score 0 for duration dimension; only risk scoring applies; CTA is locked (no results shown)

---

## 6. Results Page

### RESULTS-01 — Results page opens on active CTA tap
**Steps:**
1. Select `12M` + `Moderate`
2. Tap active CTA
**Expected:**
- Results page is visible (selection page hidden)
- Count pill shows `"X found"`
- Top 5 bond cards rendered

---

### RESULTS-02 — Shows max 5 bonds
**Steps:** Set criteria that matches > 5 bonds
**Expected:**
- Exactly 5 bond cards rendered in results grid
- "View All" row visible: `"View all X bonds →"`

---

### RESULTS-03 — Shows all bonds when ≤ 5 match
**Steps:** Set criteria that matches exactly 3 bonds
**Expected:**
- 3 bond cards shown
- "View All" row is **hidden**

---

### RESULTS-04 — Filter chips show active criteria
**Steps:** Set amount=₹1L, duration=12M, risk=Conservative → open results
**Expected:**
- `💰 ₹1L ✎` chip visible (editable)
- `⏱ 12 Months` chip visible
- `🎯 Conservative` chip visible

---

### RESULTS-05 — Editable amount chip opens Amount Sheet
**Steps:** Tap the `💰 ₹X ✎` filter chip
**Expected:**
- Amount Edit Sheet slides up from bottom
- Current amount is pre-filled in sheet

---

### RESULTS-06 — Sort dropdown changes order
**Steps:**
1. Open results
2. Change sort to `Highest Returns`
**Expected:**
- Bond cards re-render in new order without page reload

---

### RESULTS-07 — Bond card estimated returns reflect current amount
**Steps:**
1. Set amount to ₹50K, open results
2. Observe "Est. returns on ₹50K" on first card
**Expected:** Returns value is `round(50000 × (ret/100) × (dur/12))`

---

### RESULTS-08 — Match badge labels and colors
**Expected (for each match class):**

| Match | Badge text | Badge bg | Badge text color |
|---|---|---|---|
| Great | `✦ Great Match` | `#BBFFD4` | `#14532D` |
| Good | `◆ Good Match` | `#FEF9C3` | `#78350F` |
| Fair | `· Fair Match` | `#F3F4F6` | `#4B5563` |

---

### RESULTS-09 — Rating badge colors
**Expected (by rating):**

| Rating | Bg | Text |
|---|---|---|
| AAA | `#D1FAE5` | `#065F46` |
| AA+ | `#DBEAFE` | `#1E40AF` |
| AA | `#EDE9FE` | `#5B21B6` |
| A | `#FEE2E2` | `#991B1B` |
| BBB+ | `#F3F4F6` | `#374151` |

---

### RESULTS-10 — Back button returns to selection screen
**Steps:** Tap `"← Change Filters"` / back button
**Expected:**
- Results page hidden
- Selection screen visible with all previous selections intact (amount, duration, risk preserved)

---

## 7. All Bonds Page

### ALL-01 — View All opens all bonds
**Steps:** Tap `"View all X bonds →"` on results page
**Expected:**
- All Bonds page is visible
- Count pill matches results count
- All (not just 5) matched bonds shown

---

### ALL-02 — Grouped by match tier
**Steps:** Open All Bonds page
**Expected:**
- Bonds grouped under: `✦ Great Match` → `◆ Good Match` → `· Fair Match`
- Groups only shown if they have ≥ 1 bond
- Each group header shows label + count badge (e.g., `3 bonds`)

---

### ALL-03 — Sort is synced with results page
**Steps:**
1. On Results page, change sort to `Highest Returns`
2. Tap View All
**Expected:**
- All Bonds sort dropdown is set to `Highest Returns`
- Bonds are already sorted accordingly

---

### ALL-04 — Sort change on All Bonds syncs back to Results
**Steps:**
1. Open All Bonds
2. Change sort to `Safest First`
3. Go back to Results
**Expected:**
- Results page sort dropdown is now `Safest First`

---

### ALL-05 — Back button goes to selection screen
**Steps:** Tap `"← Back to Home"` on All Bonds page
**Expected:**
- All Bonds page hidden
- Selection screen shown (not Results page)
- Previous selections preserved

---

## 8. No Match / Empty State

### EMPTY-01 — Zero results shows empty state
**Steps:** Set amount very low (₹10K) + duration 2Y+ + Aggressive
*(Set a scenario where no bonds pass the filter)*
**Expected:**
- `"No bonds match"` empty state shown
- Instructional text to adjust preferences
- `"Adjust my criteria"` button visible

---

### EMPTY-02 — Zero exact matches shows top picks fallback
**Steps:** Set criteria where duration filter has no matches but risk filter has some
**Expected:**
- `"No exact matches right now"` heading
- Up to 3 top-rated bonds for the selected risk tier shown
- Message: `"Here are the top-rated [Risk] bonds you can invest in today"`
- `"Adjust my criteria"` button

---

### EMPTY-03 — "Adjust my criteria" returns to selection
**Steps:** On empty state, tap `"Adjust my criteria"`
**Expected:**
- Returns to Selection screen
- All previous selections are preserved (not reset)

---

### EMPTY-04 — Save strip hidden on zero results
**Steps:** Navigate to empty state
**Expected:**
- Save strip is **not shown** (only visible when there are results)

---

## 9. Amount Edit Sheet

### SHEET-01 — Sheet slides up on chip tap
**Steps:** On results page, tap `💰 ₹X ✎` chip
**Expected:**
- Sheet slides up from bottom (transition ~320ms)
- Overlay backdrop visible behind sheet
- Current amount pre-filled in sheet amount display and slider

---

### SHEET-02 — Sheet slider and chips are synced with main state
**Steps:**
1. Set amount to ₹1L on main widget
2. Open sheet
**Expected:**
- Sheet amount display shows `₹1,00,000`
- Slider is at correct log-scale position for ₹1L
- `₹1L` chip is active in sheet

---

### SHEET-03 — Changing slider in sheet updates live
**Steps:**
1. Open sheet
2. Move slider
**Expected:**
- Sheet amount display updates in real time
- Main widget amount display also updates in real time
- Bond cards re-render with new estimated returns

---

### SHEET-04 — "Update Results" closes sheet
**Steps:** Tap `"Update Results"` CTA
**Expected:**
- Sheet slides down and closes (~320ms)
- Main page slider and amount display are in sync with sheet's final value

---

### SHEET-05 — "Updated" badge flashes on estimated returns
**Steps:**
1. Change amount in sheet
2. Tap `"Update Results"`
**Expected (after ~350ms delay):**
- `"✓ Updated"` badge appears on every visible bond card's estimated returns box
- Badge fades out after ~1.45s total (not remaining permanently)

---

### SHEET-06 — Updated badge fires even if amount unchanged
**Steps:**
1. Open sheet, do not change amount
2. Tap `"Update Results"`
**Expected:**
- `"✓ Updated"` badge still animates (harmless, per PRD §10 edge case)

---

### SHEET-07 — Main page amount is updated even without changing
**Steps:**
1. Set amount to ₹50K on main widget
2. Open sheet (shows ₹50K)
3. Close via `"Update Results"` without changing
**Expected:**
- Main page still shows ₹50K — no unintended reset

---

## 10. Auth Modal

### AUTH-01 — Modal opens on "Invest Now" (unauthenticated)
**Steps:** Tap `"Invest Now →"` on any bond card
**Expected:**
- Auth modal appears with backdrop
- Bond context bar visible: bond abbreviation + bond name + `"Investing ₹X"`

---

### AUTH-02 — Bond context bar is correct
**Steps:** Tap "Invest Now" on `"HDFC Ltd"` bond with amount `₹1L`
**Expected:**
- Bond icon shows `"HD"` (first 2 initials)
- Bond name: `"HDFC Ltd"`
- Amount: `"Investing ₹1,00,000"`

---

### AUTH-03 — Phone input validation — invalid (< 10 digits)
**Steps:** Enter `"9876"` → tap Continue
**Expected:**
- Error shown: `"Please enter a valid 10-digit mobile number"`
- Form not submitted

---

### AUTH-04 — Phone input validation — invalid (letters)
**Steps:** Enter `"abcdefghij"` → tap Continue
**Expected:**
- Validation error shown
- Form not submitted

---

### AUTH-05 — Phone input validation — valid (10 digits)
**Steps:** Enter `"9876543210"` → tap Continue
**Expected:**
- Button changes to `"Verifying…"` (disabled)
- No error message shown

---

### AUTH-06 — Success state after verification
**Steps:** Enter valid phone → Continue → wait 1.5s
**Expected:**
- Form section replaced by success state
- Checkmark icon visible
- `"You're in!"` heading
- `"Redirecting you to complete your investment…"` sub-text

---

### AUTH-07 — Modal closes and investment proceeds after success
**Steps:** Complete auth flow (valid phone → Continue → wait)
**Expected:**
- After ~1.8s post-success display, modal closes
- `investNow()` is called with the stored bond context
- Investment alert appears

---

### AUTH-08 — Closing modal clears pending state
**Steps:**
1. Tap "Invest Now" on Bond A
2. Close modal via `×` button (or Escape key)
3. Tap "Invest Now" on Bond B
**Expected:**
- Bond B's context is shown (Bond A's context is cleared)
- No ghost state from Bond A

---

### AUTH-09 — Backdrop click dismisses modal
**Steps:** Click on the overlay outside the modal card
**Expected:**
- Modal closes
- Pending invest state cleared

---

### AUTH-10 — Escape key dismisses modal
**Steps:** Press Escape key while modal is open
**Expected:**
- Modal closes

---

### AUTH-11 — Subsequent "Invest Now" after login goes straight through
**Steps:**
1. Complete auth flow on Bond A
2. Tap "Invest Now" on Bond B
**Expected:**
- Auth modal does **not** appear for Bond B
- `investNow()` fires immediately

---

### AUTH-12 — Save flow (Save Strip "Sign up free")
**Steps:** Tap `"Sign up free"` on the save strip
**Expected:**
- Auth modal opens
- Bond context bar is **hidden** (not shown for save flow)
- Title: `"Save your results"`
- Sub-text: `"Create a free account to bookmark these bonds…"`
- CTA text: `"Create Account →"`

---

### AUTH-13 — Save flow success transforms strip
**Steps:** Complete save flow auth
**Expected:**
- Modal closes
- Save strip transforms to: `"You're in! Results saved."` (green text)
- Strip auto-hides after 4s

---

## 11. Navigation & Page Transitions

### NAV-01 — Selection → Results (CTA tap)
**Expected:** Results page visible, selection page hidden, no full page reload

### NAV-02 — Results → Selection (back tap)
**Expected:** Selection visible with previous choices intact

### NAV-03 — Results → All Bonds (View All tap)
**Expected:** All Bonds page visible

### NAV-04 — All Bonds → Selection (Back to Home tap)
**Expected:** Selection visible (NOT results page)

### NAV-05 — Amount chip → Sheet → close
**Expected:** Sheet visible, then hidden; results page still visible beneath

### NAV-06 — Invest Now → Auth → complete
**Expected:** Modal opens, closes, `investNow()` fires

### NAV-07 — Invest Now → Auth → dismiss
**Expected:** Modal closes, results page remains, user can tap Invest Now again

---

## 12. Responsive Behaviour

### RESP-01 — Risk grid at > 760px
**Expected:** 3-column grid layout; all card descriptions visible

### RESP-02 — Risk grid at 520px–760px
**Expected:** Single-column layout (icon on left, text on right)

### RESP-03 — Risk grid at ≤ 520px
**Expected:** 3-column compact layout; descriptions hidden; return badge still visible (10px font)

### RESP-04 — Auth modal at ≤ 520px
**Expected:** Modal displays as bottom sheet (border-radius only on top corners)

### RESP-05 — Duration pills wrap on small screens
**Expected:** Pills wrap to next line at ≤ 520px without overflow or horizontal scroll

### RESP-06 — Floating CTA always pinned to bottom
**Expected:** CTA remains at bottom of viewport at all tested screen sizes

### RESP-07 — Sticky subheader always visible on scroll
**Expected:** Results page subheader stays in view when scrolling through bond cards

### RESP-08 — Hero H1 font size at ≤ 520px
**Expected:** H1 scales down to ~28px (not clipped, not overflowing)

---

## 13. Edge Cases (from PRD §10)

### EDGE-01 — User taps locked CTA repeatedly
**Expected:** Toast does not stack; timer resets on each tap

### EDGE-02 — Amount higher than all bond minimums
**Steps:** Set amount to ₹50L
**Expected:** All bonds pass amount filter; only score/sort drives ranking

### EDGE-03 — Only 1 bond matches
**Expected:** 1 bond card shown; "View All" row hidden

### EDGE-04 — Exactly 5 bonds match
**Expected:** 5 bonds shown; "View All" row hidden (count not > 5)

### EDGE-05 — Exactly 6 bonds match
**Expected:** 5 bonds shown in results; "View All" visible showing 6 total

### EDGE-06 — User dismisses auth mid-flow
**Expected:** `pendingInvest` is null; next "Invest Now" tap opens fresh modal with correct bond

### EDGE-07 — Amount sheet opened and closed without changing value
**Expected:** "✓ Updated" badge animates; amount and results unchanged

### EDGE-08 — User logs in then views more bonds
**Steps:** Log in via Bond A, then tap "Invest Now" on Bond B
**Expected:** No modal; direct `investNow()` call with Bond B's details

---

## 14. Accessibility

### A11Y-01 — Keyboard navigation in widget
**Steps:** Tab through the widget form
**Expected:** Focus order: Amount slider → Quick chips → Duration pills → Risk cards → CTA

### A11Y-02 — Slider operable via keyboard
**Steps:** Focus slider → use Arrow keys
**Expected:** Amount changes in steps; display updates

### A11Y-03 — Pills and cards operable via keyboard
**Steps:** Tab to a duration pill → press Enter/Space
**Expected:** Pill activates; same behaviour as click

### A11Y-04 — Modal focus trap
**Steps:** Open auth modal → press Tab repeatedly
**Expected:** Focus cycles within modal; never moves to background page elements

### A11Y-05 — Modal focus returns on close
**Steps:** Open modal → close it
**Expected:** Focus returns to the "Invest Now" button that triggered the modal

### A11Y-06 — Escape closes modal
**Steps:** Open modal → press Escape
**Expected:** Modal closes (also covered in AUTH-10)

### A11Y-07 — Sufficient color contrast
**Expected:** Match badges, bond card text, CTA labels all meet WCAG AA (4.5:1 for normal text)

---

## 15. Unit Tests (Pure Functions)

These are verified by the test files in `tests/`:

| Test File | Coverage |
|---|---|
| `tests/bondMatcher.test.js` | `matchScore`, `scoreBonds`, `getFiltered`, `sorted` |
| `tests/amountUtils.test.js` | `sliderToAmt`, `amtToSlider`, `fmtAmt`, `fmtAmtFull`, `earnings` |

See those files for detailed assertions covering all MATCH-* and SLIDER-* cases above.

---

## Test Execution Checklist

### Manual Regression (per release)
- [ ] SLIDER-01 through SLIDER-07
- [ ] DUR-01 through DUR-05
- [ ] RISK-01 through RISK-05
- [ ] CTA-01 through CTA-10
- [ ] RESULTS-01 through RESULTS-10
- [ ] ALL-01 through ALL-05
- [ ] EMPTY-01 through EMPTY-04
- [ ] SHEET-01 through SHEET-07
- [ ] AUTH-01 through AUTH-13
- [ ] NAV-01 through NAV-07
- [ ] EDGE-01 through EDGE-08

### Automated (unit tests)
- [ ] `npm test` passes all assertions in `tests/`

### Responsive (cross-browser)
- [ ] Chrome desktop ≥ 1280px
- [ ] Chrome mobile emulation 375px (iPhone SE)
- [ ] Safari mobile (real device or simulator)
- [ ] Firefox desktop

### Device sizes to test
| Width | Scenario |
|---|---|
| 1280px | Desktop |
| 900px | Tablet landscape |
| 768px | Tablet portrait (just above 760px breakpoint) |
| 700px | Just below 760px breakpoint |
| 540px | Just above 520px breakpoint |
| 390px | iPhone 14 |
| 375px | iPhone SE |
| 320px | Smallest modern device |
