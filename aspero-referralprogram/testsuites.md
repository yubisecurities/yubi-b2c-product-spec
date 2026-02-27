# Aspero Referral Program — Test Suites

## Test Environment Setup

- **Browser**: Chrome, Safari, Firefox (latest versions)
- **Mobile devices**: iOS (Safari), Android (Chrome)
- **Viewport sizes**:
  - Desktop: 1440×900
  - Tablet: 768×1024
  - Mobile: 375×812, 412×915
- **Network**: 4G, LTE, WiFi (for share/download links)

---

## Test Suite 1: Page Navigation

**Goal**: Verify smooth navigation between all 3 pages and proper DOM state management.

### TC1.1: Landing Page Loads as Default
- **Steps**:
  1. Open `index.html` in browser
  2. Observe active page
- **Expected**: Page 1 (Landing) is visible; other pages are hidden
- **Evidence**: Only `.page.active` is `#page-landing`

### TC1.2: Landing → Dashboard Navigation
- **Steps**:
  1. On Landing page, click "My Dashboard →" button
  2. Wait for page transition
- **Expected**: Dashboard page appears; Landing page hidden; scroll to top
- **Evidence**: `showPage('page-dashboard')` called, `.active` moved to `#page-dashboard`

### TC1.3: Landing → Invitee Page Navigation
- **Steps**:
  1. On Landing page, click "Preview share page" button
  2. Wait for transition
- **Expected**: Invitee Share Page appears; scroll to top
- **Evidence**: `showPage('page-referral')` called

### TC1.4: Dashboard → Landing Navigation
- **Steps**:
  1. Navigate to Dashboard
  2. Click "← Home" button
  3. Observe
- **Expected**: Returns to Landing page
- **Evidence**: Active page is `#page-landing`

### TC1.5: Invitee Page → Landing Navigation
- **Steps**:
  1. Navigate to Invitee Share Page
  2. Click "aspero." logo
  3. Expected behavior: Navigate back to Landing page (if implemented) OR reload
- **Expected**: Either returns to Landing or reloads page
- **Evidence**: Page state resets or previous page shown

---

## Test Suite 2: Referral Code & Link Copying

**Goal**: Verify clipboard copy functionality and fallback behavior.

### TC2.1: Copy Referral Code (Clipboard API)
- **Prerequisites**: Test on Chrome/Safari with clipboard permissions
- **Steps**:
  1. On Landing page, locate referral code box
  2. Click "Copy" button next to code (e.g., `ARPIT2026`)
  3. Observe button text change
  4. Paste elsewhere (e.g., text field)
- **Expected**:
  - Button shows "✓ Copied!" temporarily
  - Clipboard contains `ARPIT2026`
  - Button reverts to "Copy" after ~2 seconds
- **Evidence**: `copyCode()` function executed; navigator.clipboard.writeText() success

### TC2.2: Copy Referral Link (Clipboard API)
- **Prerequisites**: Clipboard permissions enabled
- **Steps**:
  1. On Landing or Dashboard, click "Copy link" button
  2. Paste elsewhere
- **Expected**:
  - Clipboard contains full URL: `https://aspero.in/ref/ARPIT2026`
  - Button shows "✓ Copied!" then reverts
- **Evidence**: `copyLink()` function executed; URL validated

### TC2.3: Copy Code — Fallback Behavior (No Clipboard API)
- **Prerequisites**: Test on older browser or disable clipboard permission
- **Steps**:
  1. Mock or disable navigator.clipboard
  2. Click "Copy" button
  3. Observe fallback behavior
- **Expected**:
  - Fallback textarea created and selected
  - Code copied via `document.execCommand('copy')`
  - Textarea removed after copy
- **Evidence**: `fallbackCopy()` function executed; code still copied

### TC2.4: Copy Link — Fallback Behavior
- **Steps**:
  1. Disable clipboard API (if possible)
  2. Click "Copy link" button
- **Expected**: Fallback mechanism works; link copied to clipboard
- **Evidence**: `fallbackCopy(url)` called

---

## Test Suite 3: Social Sharing

**Goal**: Verify WhatsApp, Telegram, and email share deep links generate correctly.

### TC3.1: WhatsApp Share from Landing Page
- **Prerequisites**: Device with WhatsApp installed OR web.whatsapp.com available
- **Steps**:
  1. On Landing page, click "WhatsApp" share button
  2. Observe redirect
- **Expected**:
  - Opens WhatsApp (mobile) or web.whatsapp.com (desktop)
  - Pre-filled message contains referral code + link
  - Message format: "Invite friends & earn! Check out my referral link: [link]"
- **Evidence**: `shareWA()` function calls `window.open('https://wa.me/?text=...')`

### TC3.2: Telegram Share from Landing Page
- **Prerequisites**: Telegram installed or telegram.me accessible
- **Steps**:
  1. On Landing page, click "Telegram" share button
  2. Observe redirect
- **Expected**:
  - Opens Telegram
  - Pre-filled message with referral details
- **Evidence**: `shareTG()` function calls appropriate Telegram URL

### TC3.3: WhatsApp Share from Dashboard
- **Steps**:
  1. Navigate to Dashboard (filled state)
  2. Locate share strip (dark section)
  3. Click "WhatsApp" button
  4. Observe
- **Expected**: Same WhatsApp share behavior as Landing page
- **Evidence**: Same `shareWA()` function executed

### TC3.4: Download Buttons Redirect Correctly
- **Steps**:
  1. On Invitee Share Page or anywhere with download buttons
  2. Click "Get it on Google Play" button
  3. Observe URL/navigation
- **Expected**: Redirects to Google Play Store (Aspero app URL)
- **Evidence**: `dlApp('play')` calls `window.open('https://play.google.com/store/apps/details?id=...')`

### TC3.5: Download App Store Button
- **Steps**:
  1. On Invitee Share Page, click "Download on the App Store"
  2. Observe
- **Expected**: Redirects to Apple App Store
- **Evidence**: `dlApp('apple')` calls App Store URL

---

## Test Suite 4: Dashboard — Empty State

**Goal**: Verify dashboard behaves correctly with no referrals.

### TC4.1: Empty State Display
- **Prerequisites**: Dashboard demo toggle set to "No Referrals"
- **Steps**:
  1. Navigate to Dashboard
  2. Observe UI
- **Expected**:
  - `#dashEmpty` div is visible
  - `#dashFilled` div is hidden
  - Icon 🤝 displayed
  - Headline: "Start referring, earn up to ₹10,000/month"
  - Two buttons: "Share on WhatsApp" + "Copy Code"
  - Info box explaining how referral program works
- **Evidence**: DOM shows only `#dashEmpty` as visible

### TC4.2: WhatsApp Button in Empty State
- **Steps**:
  1. On empty Dashboard, click "Share on WhatsApp"
  2. Observe
- **Expected**: Opens WhatsApp with invite message
- **Evidence**: `shareWA()` executed

### TC4.3: Copy Code Button in Empty State
- **Steps**:
  1. On empty Dashboard, click "Copy Code: ARPIT2026"
  2. Paste
- **Expected**: Code copied to clipboard; button shows "✓ Copied!"
- **Evidence**: Clipboard contains referral code

### TC4.4: Toggle to Filled State
- **Prerequisites**: Dashboard page is active
- **Steps**:
  1. Click demo toggle button (👤 No Referrals)
  2. Observe state change
- **Expected**:
  - Toggle button text changes to "With Referrals" or similar
  - `#dashEmpty` hidden
  - `#dashFilled` shown with KPIs and referral table
- **Evidence**: `toggleDashEmpty()` function called; DOM updated

---

## Test Suite 5: Dashboard — Filled State (KPIs & Analytics)

**Goal**: Verify dashboard metrics, progress bar, and referral table display correctly.

### TC5.1: KPI Grid Display
- **Prerequisites**: Dashboard in filled state with referral data
- **Steps**:
  1. Navigate to Dashboard (filled state)
  2. Observe KPI cards at top
- **Expected**:
  - 4 KPI cards in a grid:
    - Total Referred: 6
    - Total Earned: ₹4,000 (in green)
    - Active Investors: 2
    - Pending Payout: ₹0 (with "all settled ✓" label)
  - Each card has label, value, and change indicator
- **Evidence**: DOM contains `.kpi` divs with correct values

### TC5.2: Monthly Progress Bar Animation
- **Steps**:
  1. Observe progress bar section
  2. Check for animation
- **Expected**:
  - Title: "February 2026 — Monthly Earnings Cap"
  - Numbers: "₹2,500 of ₹10,000"
  - Progress bar fills to 25% (2500/10000)
  - Animation smooth, completes within 1 second
  - Footer message: "You can earn ₹7,500 more this month..."
- **Evidence**: `.prog-fill` element has `width: 25%`; animation visible

### TC5.3: Share Strip Display
- **Steps**:
  1. Observe dark share strip on Dashboard
- **Expected**:
  - Text: "Refer more friends, earn more"
  - Shows code and link
  - Two buttons: "WhatsApp" (outline) + "Copy Link" (green)
- **Evidence**: `.share-strip` visible with correct content

### TC5.4: Referral Table Header
- **Steps**:
  1. On Dashboard (filled), scroll to referral table
  2. Observe header row
- **Expected**:
  - Columns visible: User, Joined, Status, Total Invested, Your Earnings, Action
  - Header row has `.hdr` class
  - Column labels clear and aligned
- **Evidence**: `.tbl-row.hdr` found with correct column structure

### TC5.5: Referral Table Data Rows
- **Steps**:
  1. Observe data rows in referral table
- **Expected**:
  - 6 referrals displayed (from REFERRALS array)
  - Each row shows:
    - User initials avatar + name + masked phone
    - Join date (e.g., "Jan 15, 2026")
    - Status pill (color-coded)
    - Total invested (formatted as ₹XXL or ₹XXK or —)
    - Earnings (formatted as ₹XXX or —)
    - Action button or dash
- **Evidence**: `.tbl-row` elements populated with referral data

### TC5.6: Status Pill Color-Coding
- **Steps**:
  1. In referral table, observe different status pills
- **Expected**:
  - Signup → blue pill (`.pill-signup`)
  - KYC Started → yellow pill (`.pill-kyc`)
  - Ready to Trade → green pill (`.pill-ready`)
  - First Trade → purple pill (`.pill-trade`)
  - Active Investor → gold pill (`.pill-active`)
- **Evidence**: Correct `.pill-*` class applied; colors match design

### TC5.7: Format Functions (Investment & Earnings)
- **Steps**:
  1. Check investment amounts in table
  2. Verify formatting
- **Expected**:
  - 250000 → "₹2.5L"
  - 100000 → "₹1L"
  - 50000 → "₹50K"
  - 0 → "—"
- **Evidence**: `fmtInv()` function correctly formats values

---

## Test Suite 6: Dashboard — Nudge Functionality

**Goal**: Verify nudge button appears for correct statuses and sends proper messages.

### TC6.1: Nudge Button Visibility (Signup Status)
- **Prerequisites**: Dashboard filled, referral with "Signup" status visible
- **Steps**:
  1. Locate referral with Signup status
  2. Check Action column
- **Expected**:
  - "👋 Nudge" button visible
  - Button clickable
- **Evidence**: `.nudge-btn` element present for Signup status

### TC6.2: Nudge Button Visibility (KYC Started Status)
- **Steps**:
  1. Locate referral with "KYC Started" status
  2. Observe Action column
- **Expected**: "👋 Nudge" button visible (nudging allowed)
- **Evidence**: `.nudge-btn` element present

### TC6.3: Nudge Button Visibility (Ready to Trade Status)
- **Steps**:
  1. Locate referral with "Ready to Trade" status
- **Expected**: "👋 Nudge" button visible
- **Evidence**: `.nudge-btn` element present

### TC6.4: Nudge Button Hidden (First Trade Status)
- **Steps**:
  1. Locate referral with "First Trade" status
  2. Check Action column
- **Expected**:
  - No nudge button
  - Displays "—" (dash)
- **Evidence**: `.nudge-none` element (or dash) shown

### TC6.5: Nudge Button Hidden (Active Investor Status)
- **Steps**:
  1. Locate referral with "Active Investor" status
  2. Check Action column
- **Expected**:
  - No nudge button
  - Displays "—"
- **Evidence**: `.nudge-none` shown

### TC6.6: Nudge Message Sends Correctly
- **Prerequisites**: WhatsApp installed or accessible
- **Steps**:
  1. Click "👋 Nudge" on "Signup" status referral
  2. Observe WhatsApp redirect
- **Expected**:
  - Opens WhatsApp with pre-filled nudge message
  - Message mentions: friend's name, current status, encouragement to complete action
  - Message format varies by status (e.g., "Complete KYC", "Make your first investment")
- **Evidence**: `nudgeFriend(name, wa, status)` called; WhatsApp opened

---

## Test Suite 7: Invitee Share Page

**Goal**: Verify the referred friend's landing page content and CTAs.

### TC7.1: Invite Badge Display
- **Steps**:
  1. Navigate to Invitee Share Page (Page 3)
  2. Observe hero section
- **Expected**:
  - Badge shows: "Arpit Goyal has invited you to Aspero"
  - Badge styled distinctly (green background)
- **Evidence**: `.invited-badge` visible with correct name

### TC7.2: Hero Headline & Subheading
- **Steps**:
  1. Observe hero section text
- **Expected**:
  - Headline: "Earn 12–18% returns on your money"
  - Subheading: Explains bond investment benefits
- **Evidence**: `.inv-h1` and `.inv-p` contain correct text

### TC7.3: Platform Stats Display
- **Steps**:
  1. Observe platform statistics
- **Expected**:
  - ₹1,200Cr+ Deployed
  - 50,000+ Investors
  - 4.8 ★ App Rating
  - SEBI Regulated
- **Evidence**: `.pstats` grid shows all 4 stats with correct values

### TC7.4: Download Buttons Present
- **Steps**:
  1. On hero section, locate download buttons
- **Expected**:
  - "Get it on Google Play" button visible
  - "Download on the App Store" button visible
  - Both are clickable
- **Evidence**: `.store-btn` elements present with correct text

### TC7.5: Why Invest Section (4 Feature Cards)
- **Steps**:
  1. Scroll down to "Why invest with Aspero?" section
  2. Observe feature cards
- **Expected**:
  - 4 cards displayed:
    1. 📈 High-yield bonds (11–18% YTM)
    2. 🔒 SEBI regulated & safe
    3. ⚡ Start with ₹5,000
    4. 💳 Monthly payouts
  - Each card has icon, heading, description, and tag
- **Evidence**: `.off-grid` contains 4 `.off-card` elements

### TC7.6: Testimonials Section (3 Reviews)
- **Steps**:
  1. Scroll to testimonials section
  2. Observe reviews
- **Expected**:
  - 3 customer testimonials displayed
  - Each has 5-star rating
  - Real names and city locations shown
  - Authentic quotes about bond investing experience
- **Evidence**: `.test-grid` contains 3 `.test-card` elements with correct content

### TC7.7: Final CTA Section
- **Steps**:
  1. Scroll to final CTA
- **Expected**:
  - Invite badge: "Invited by Arpit Goyal · Code: ARPIT2026"
  - Headline: "Start investing in 10 minutes"
  - Subheading: Explains signup process
  - Two download buttons (Play Store + App Store)
- **Evidence**: `.final-cta` section visible with correct content

### TC7.8: Sticky Bottom Bar Presence
- **Steps**:
  1. Scroll anywhere on the page
  2. Observe bottom of screen
- **Expected**:
  - Sticky bar remains fixed at bottom
  - Shows: "Ready to earn 12–18% on your money?"
  - Shows: "Invited by Arpit Goyal · Use code ARPIT2026"
  - "Sign Up Free →" button visible and clickable
- **Evidence**: `.sticky-bar` has `position: sticky`; visible at all times

### TC7.9: Download Button Clicks
- **Steps**:
  1. Click "Sign Up Free →" on sticky bar
  2. Observe redirect
- **Expected**: Opens Google Play Store (or App Store on iOS)
- **Evidence**: `dlApp('play')` executed

---

## Test Suite 8: Mobile Preview Feature

**Goal**: Verify in-page mobile phone frame preview works correctly.

### TC8.1: Phone FAB Visibility
- **Prerequisites**: Desktop/laptop view
- **Steps**:
  1. Open index.html on desktop browser
  2. Observe bottom-right corner
- **Expected**:
  - Floating phone icon/button visible (bottom-right, fixed)
  - Button text/icon: Phone emoji or similar
- **Evidence**: `#phoneFab` visible; clickable

### TC8.2: Phone FAB Click Opens Preview
- **Steps**:
  1. Click phone FAB button
  2. Observe modal/overlay
- **Expected**:
  - Phone frame overlay opens
  - Frame shows current page in mobile viewport (375px wide)
  - Phone has notch and home indicator mockup
  - Content rendered inside iframe
- **Evidence**: `#phoneOverlay` becomes visible; `#phoneFrame` src populated

### TC8.3: Phone Preview — Landing Page (Page 1)
- **Steps**:
  1. Open phone preview on Landing page
  2. Observe page switcher pills
- **Expected**:
  - Three pills below phone: "Landing", "Dashboard", "Share Page"
  - "Landing" pill is active/highlighted
  - Page 1 content rendered in phone frame
- **Evidence**: `pBtn0` has `.active` class; iframe src contains `?page=0`

### TC8.4: Phone Preview — Navigate to Dashboard (Page 2)
- **Steps**:
  1. While phone preview open, click "Dashboard" pill
  2. Observe page change in phone frame
- **Expected**:
  - "Dashboard" pill becomes active
  - Phone frame updates to show Page 2 (Dashboard)
  - "Landing" pill no longer active
- **Evidence**: `phoneNav(1)` called; iframe src updates with `?page=1`

### TC8.5: Phone Preview — Navigate to Share Page (Page 3)
- **Steps**:
  1. While phone preview open, click "Share Page" pill
  2. Observe update
- **Expected**:
  - "Share Page" pill active
  - Phone frame shows Invitee Share Page
- **Evidence**: `phoneNav(2)` called; iframe src has `?page=2`

### TC8.6: Phone Preview — Close Overlay
- **Steps**:
  1. Phone preview open
  2. Click outside frame or close button (if present)
  3. Observe
- **Expected**:
  - Phone frame closes or hides
  - Returns to normal view
- **Evidence**: `#phoneOverlay` hidden or removed from DOM

---

## Test Suite 9: Responsive Design & Mobile Layout

**Goal**: Verify layout adapts correctly across device sizes.

### TC9.1: Desktop Layout (1440×900)
- **Steps**:
  1. View page at 1440×900
  2. Observe layout
- **Expected**:
  - Full-width content
  - Stats strip shows all 4 metrics side-by-side
  - Tables visible without horizontal scroll
  - Multi-column layouts utilized
- **Evidence**: No horizontal scrolling; content fits screen

### TC9.2: Tablet Layout (768×1024)
- **Steps**:
  1. Resize viewport to 768×1024 (or rotate device)
  2. Observe layout changes
- **Expected**:
  - Content still readable
  - Single-column or 2-column grid (depending on section)
  - Font sizes adjusted
  - Buttons remain clickable with touch-friendly sizes (min 44×44px)
- **Evidence**: Content reflows; no horizontal scroll

### TC9.3: Mobile Layout (375×812)
- **Steps**:
  1. View on iPhone or 375px viewport
  2. Observe layout
- **Expected**:
  - Fully stacked, single-column layout
  - Hero section scaled for mobile
  - Stats strip stacks vertically or scrolls horizontally
  - Navigation buttons full-width or side-by-side
  - Table columns hidden or side-scrollable (e.g., "Total Invested" and "Your Earnings" marked with `.hide`)
  - Touch targets >= 44×44px
- **Evidence**: Content fully responsive; easy to navigate on mobile

### TC9.4: Large Mobile (412×915)
- **Steps**:
  1. View on Android (412×915) or larger mobile
- **Expected**:
  - Similar to smaller mobile but with more horizontal space
  - Some columns may appear that were hidden on 375px
  - Text readable without excessive zoom
- **Evidence**: Layout adjusted; content accessible

### TC9.5: Landscape Orientation
- **Steps**:
  1. Rotate device to landscape
- **Expected**:
  - Layout adjusts to landscape aspect ratio
  - Content remains readable
  - Navigation works correctly
- **Evidence**: No horizontal scroll; content optimized for landscape

---

## Test Suite 10: Cross-Browser Compatibility

**Goal**: Verify functionality across major browsers.

### TC10.1: Chrome (Latest)
- **Steps**:
  1. Open index.html in latest Chrome
  2. Test all major features
- **Expected**:
  - Page navigation works
  - Clipboard copy works natively
  - Share buttons open correctly
  - All styling renders as designed
  - Phone preview works
- **Evidence**: No console errors; all features functional

### TC10.2: Safari (Latest, iOS & macOS)
- **Steps**:
  1. Open on Safari (macOS)
  2. Test same features
- **Expected**:
  - All features work (may use fallback for clipboard on older Safari)
  - Touch interactions smooth on iOS
  - Notch/safe areas respected
- **Evidence**: Functional; touch-friendly on iOS

### TC10.3: Firefox (Latest)
- **Steps**:
  1. Open in Firefox
  2. Test core functionality
- **Expected**:
  - Navigation, copy, sharing all work
  - Layout renders correctly
  - No compatibility issues
- **Evidence**: No errors; all features work

### TC10.4: Edge (Latest)
- **Steps**:
  1. Open in Edge (Chromium-based)
- **Expected**:
  - Same as Chrome (Chromium engine)
  - All features functional
- **Evidence**: Consistent with Chrome experience

---

## Test Suite 11: Form Inputs & Interactions

**Goal**: Verify all buttons, links, and interactive elements respond correctly.

### TC11.1: Button States (Hover, Active, Disabled)
- **Steps**:
  1. Hover over buttons
  2. Click buttons
  3. Observe state changes
- **Expected**:
  - Hover state: Color/opacity change
  - Active/clicked state: Visual feedback (e.g., "✓ Copied!")
  - No disabled buttons (or if present, they appear disabled)
- **Evidence**: CSS and JavaScript state changes observed

### TC11.2: Links Open Correctly
- **Steps**:
  1. Test all referral links (WhatsApp, Telegram, Play Store, App Store)
  2. Observe redirects
- **Expected**:
  - Each link opens correct external app/website
  - No broken links
  - Deep links populated with referral code where applicable
- **Evidence**: Correct redirects; no 404 errors

### TC11.3: Table Row Interaction
- **Steps**:
  1. On Dashboard, click or hover over referral table rows
  2. Observe
- **Expected**:
  - Hover state: Row background changes
  - Nudge button clickable
  - No unintended selections or actions
- **Evidence**: Visual feedback; buttons respond correctly

---

## Test Suite 12: Data Persistence & State Management

**Goal**: Verify app state survives page interactions.

### TC12.1: Page State After Navigation
- **Steps**:
  1. On Landing page, navigate to Dashboard
  2. Modify demo toggle (if any input fields exist)
  3. Navigate back to Landing
  4. Go to Dashboard again
- **Expected**:
  - Dashboard retains its state (empty or filled based on toggle)
  - KPI values unchanged
  - No data loss
- **Evidence**: Demo toggle remains in chosen state; KPIs consistent

### TC12.2: Clipboard Copy Doesn't Clear on Navigation
- **Steps**:
  1. Copy referral code
  2. Navigate to another page
  3. Try to paste
- **Expected**:
  - Clipboard still contains code
  - No automatic clearing
- **Evidence**: Paste operation yields original code

---

## Test Suite 13: Accessibility

**Goal**: Verify app is usable for users with disabilities.

### TC13.1: Keyboard Navigation
- **Prerequisites**: Disable mouse
- **Steps**:
  1. Use Tab key to navigate through all interactive elements
  2. Use Enter to activate buttons
  3. Observe focus indicators
- **Expected**:
  - Focus visible on all buttons, links, and inputs
  - Tab order logical (left-to-right, top-to-bottom)
  - All interactive elements reachable via keyboard
- **Evidence**: Focus indicators visible; all features accessible

### TC13.2: Color Contrast
- **Steps**:
  1. Use accessibility checker (e.g., axe DevTools)
  2. Check all text against WCAG AA standard
- **Expected**:
  - All text meets WCAG AA (4.5:1 for normal text, 3:1 for large text)
  - Status pills distinguishable by more than color alone
- **Evidence**: Checker reports no contrast issues

### TC13.3: Screen Reader Compatibility
- **Prerequisites**: Screen reader installed (NVDA, JAWS, VoiceOver)
- **Steps**:
  1. Activate screen reader
  2. Navigate through page
  3. Verify readability of content
- **Expected**:
  - All headings read correctly
  - Button purposes clear
  - Table header/data relationships understood
  - No missing alt text for icons
- **Evidence**: Screen reader output is clear and complete

### TC13.4: Focus Management
- **Steps**:
  1. Open phone preview or modal
  2. Observe focus trap (if implemented)
- **Expected**:
  - Focus contained within modal/preview when open
  - Focus returns to trigger element when closed
- **Evidence**: Keyboard navigation stays within visible content

---

## Test Suite 14: Performance & Loading

**Goal**: Verify app loads and performs efficiently.

### TC14.1: Initial Load Time
- **Steps**:
  1. Open browser DevTools (Network tab)
  2. Reload page
  3. Measure time to interactive
- **Expected**:
  - Page interactive within 2-3 seconds
  - HTML file loads (54KB) within acceptable time
  - No render-blocking resources
- **Evidence**: DevTools shows acceptable load metrics

### TC14.2: Animation Smoothness
- **Steps**:
  1. Navigate between pages
  2. Observe scroll animations
  3. Animate progress bar
- **Expected**:
  - Animations smooth at 60fps
  - No stuttering or jank
  - Transitions complete within 1 second
- **Evidence**: DevTools Performance tab shows smooth frames

### TC14.3: Memory Usage
- **Prerequisites**: DevTools open
- **Steps**:
  1. Navigate between pages multiple times
  2. Observe memory usage
- **Expected**:
  - Memory stable
  - No continuous growth (memory leak)
  - Typical usage <50MB
- **Evidence**: DevTools Memory/Heap snapshot shows stability

### TC14.4: Large Referral List Performance
- **Steps**:
  1. Modify `REFERRALS` array to contain 100+ entries
  2. Render Dashboard table
  3. Observe rendering speed
- **Expected**:
  - Table still renders smoothly
  - No UI freeze
  - All rows rendered correctly
- **Evidence**: Performance remains acceptable

---

## Test Suite 15: Data Formatting & Localization

**Goal**: Verify number/currency formatting and locale support.

### TC15.1: Currency Formatting (INR)
- **Steps**:
  1. Check all currency values on page
- **Expected**:
  - ₹ symbol used consistently
  - Numbers formatted with Indian numbering system (lakhs, crores)
  - Examples: ₹2.5L, ₹50K, ₹1,20,000
- **Evidence**: `fmtInv()` and `fmtEarn()` produce correct format

### TC15.2: Date Formatting
- **Steps**:
  1. On Dashboard table, observe date columns
- **Expected**:
  - Dates formatted as "MMM DD, YYYY" (e.g., "Jan 15, 2026")
  - Timezone-aware if applicable
- **Evidence**: Date display matches specification

### TC15.3: Initialsgeneration
- **Steps**:
  1. In referral table, observe user initials
- **Expected**:
  - Initials taken from first letters of first and last name
  - Examples: "Priya Sharma" → "PS", "Rajesh M." → "RM"
- **Evidence**: `initials()` function produces correct abbreviations

---

## Regression Test Checklist

After any code changes, verify:

- [ ] All 3 pages navigate correctly
- [ ] Copy code/link functions work
- [ ] Share buttons (WhatsApp, Telegram) redirect properly
- [ ] Dashboard empty/filled states toggle
- [ ] KPI values display correctly
- [ ] Progress bar animates
- [ ] Referral table renders with all data
- [ ] Nudge buttons appear for correct statuses
- [ ] Mobile preview opens and switches pages
- [ ] Responsive layout works at all breakpoints
- [ ] No console errors in DevTools
- [ ] Keyboard navigation works
- [ ] Page load time acceptable

---

## Known Limitations & Future Enhancements

- **Offline Support**: Currently no service worker; page requires internet
- **Real Data Integration**: Dashboard uses mock data; future API integration needed
- **Analytics**: No event tracking/analytics yet (implement with GTM or Mixpanel)
- **Error Handling**: Limited error messages for failed shares; enhance UX
- **i18n**: Currently English-only; multi-language support future phase
- **Session Management**: No login/auth; assumes user is already authenticated
