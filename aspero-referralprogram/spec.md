# Aspero Referral Program — Specification

## Overview

The Aspero Referral Program is a web-based dashboard and marketing prototype that allows existing users to refer friends and earn commission-based rewards. Users earn **1% of every rupee their referred friends invest**, credited to their Aspero wallet within 24 hours, with a monthly cap of **₹10,000 per referral code**.

---

## Program Terms

| Term | Value |
|------|-------|
| Commission Rate | 1% of total referred investment |
| Monthly Cap | ₹10,000 per referral code |
| Settlement Time | Within 24 hours of referred investment |
| Referral Validity | No expiry; lifetime earnings |

---

## Architecture

The prototype is a **single-page HTML application** with three pages:
1. **Landing Page** — for the referrer (personal referral hub)
2. **Dashboard** — referral analytics and management
3. **Invitee Share Page** — marketing page shown to referred friends

All three pages share the same DOM but are hidden/shown via CSS and JavaScript (`display: none / block`).

---

## Page 1: Landing Page

**Purpose**: Personal referral hub where users share their unique code and see earnings stats.

### Header
- Dark navigation bar (rgba(13,31,22,0.94) with backdrop blur)
- Aspero logo
- Button: "Preview share page" → navigates to Page 3
- Button: "My Dashboard →" → navigates to Page 2

### Hero Section
- **Headline**: "Invite friends. Earn real money."
- **Subheading**: "Get 1% of every rupee your friends invest on Aspero — credited to your wallet every month. Cap: ₹10,000/month."
- **Referral Code Box**:
  - Displays user's unique code (e.g., `ARPIT2026`)
  - "Copy" button with clipboard integration (fallback to textarea)
  - Displays full referral link: `aspero.in/ref/ARPIT2026`
  - "Copy link" button
- **Share Buttons**:
  - WhatsApp (`shareWA()` function)
  - Telegram (`shareTG()` function)
  - "Preview page" (links to Page 3)

### Stats Strip
Four key metrics in a horizontal card:
1. **Referred**: Total number of referred friends (e.g., 6)
2. **Total Earned**: Lifetime commission (e.g., ₹4,000)
3. **This Month**: Current month's earnings (e.g., ₹2,500)
4. **More to Earn**: Remaining capacity in monthly cap (e.g., ₹7,500)

### How It Works Section
Three-step journey:
1. 🔗 **Share your code** — Copy and share via WhatsApp/Telegram
2. 📲 **Friend downloads & invests** — Completes KYC and invests using referral code
3. 💰 **You earn 1% instantly** — Commission credited within 24 hours

### The Deal Section
Three highlight cards on dark background:
1. 💸 **1%** — Of every investment (recurring, not one-time)
2. 🏆 **₹10,000** — Monthly cap per referral code
3. ⚡ **24 hrs** — Wallet credit after investment processing

### Dashboard CTA
Call-to-action bar: "Track referrals in real-time" + button "Open Dashboard →"

---

## Page 2: Dashboard

**Purpose**: Analytics and referral management for the referrer.

### Header
- Dark navigation bar with:
  - Back button ("← Home")
  - Aspero logo
  - Demo toggle button (👤 No Referrals / With Referrals)
- Header section showing user name, current month/year, referral code

### Empty State
Shown when user has no referrals or when demo toggle is "No Referrals":
- Icon: 🤝
- Headline: "Start referring, earn up to ₹10,000/month"
- Description + action buttons
- Info box explaining the process

### Filled State (KPIs)
Four metrics in a 2×2 grid:
1. **Total Referred**: Number of referred users (e.g., 6)
2. **Total Earned**: Lifetime commission (e.g., ₹4,000)
3. **Active Investors**: Count of referred friends who have invested (e.g., 2)
4. **Pending Payout**: Amount awaiting settlement (e.g., ₹0)

### Monthly Progress Bar
- Title: "February 2026 — Monthly Earnings Cap"
- Displays: "₹2,500 of ₹10,000"
- Animated horizontal progress bar
- Footer: "You can earn ₹7,500 more this month. Keep referring to maximise!"

### Share Strip (Dark)
- Text: "Refer more friends, earn more"
- Shows: Code (e.g., `ARPIT2026`) and link
- Buttons: "WhatsApp" + "Copy Link"

### Referral Table
Displays list of all referred users with columns:
- **User**: Name + masked phone number (e.g., "Priya Sharma | 98****1234")
- **Joined**: Date referred (e.g., "Jan 15, 2026")
- **Status**: Pill with one of five statuses:
  - 🔵 **Signup** — Just signed up
  - 🟡 **KYC Started** — Completed signup, begun KYC
  - 🟢 **Ready to Trade** — KYC complete, account funded
  - 💎 **First Trade** — Made first investment
  - 🎖️ **Active Investor** — Actively investing
- **Total Invested**: Amount invested (formatted as ₹XXL, ₹XXK, or —)
- **Your Earnings**: Commission earned (formatted or —)
- **Action**: Nudge button for early-stage referrals (Signup, KYC Started, Ready to Trade)

#### Nudge Functionality
- Button text: "👋 Nudge"
- Available only for statuses: Signup, KYC Started, Ready to Trade
- Sends templated message to referral's WhatsApp (using wa:// deep link)
- Message template may vary by status

### Sample Referral Data
```
[
  { name:"Priya Sharma",  phone:"98****1234", date:"Jan 15, 2026", status:"Active Investor", inv:250000, earn:2500 },
  { name:"Vikram Singh",  phone:"99****7890", date:"Feb 3, 2026",  status:"Active Investor", inv:100000, earn:1000 },
  { name:"Neha Joshi",    phone:"88****2345", date:"Feb 8, 2026",  status:"First Trade",     inv:50000,  earn:500  },
  { name:"Rahul Verma",   phone:"87****5678", date:"Feb 12, 2026", status:"Ready to Trade",  inv:0,      earn:0    },
  { name:"Amit Gupta",    phone:"76****9012", date:"Feb 16, 2026", status:"KYC Started",     inv:0,      earn:0    },
  { name:"Sneha Patel",   phone:"95****3456", date:"Feb 19, 2026", status:"Signup",          inv:0,      earn:0    },
]
```

---

## Page 3: Invitee Share Page

**Purpose**: Marketing landing page shown to a referred friend to encourage signup and investment.

### Header Navigation
- Aspero logo
- Button: "Download App" (green CTA)

### Hero Section
- **Badge**: "Arpit Goyal has invited you to Aspero"
- **Headline**: "Earn 12–18% returns on your money"
- **Subheading**: "Aspero lets you invest in curated high-yield bonds from top-rated companies — safer than stocks, far better than fixed deposits."
- **Platform Stats** (4 cards):
  - ₹1,200Cr+ Deployed
  - 50,000+ Investors
  - 4.8 ★ App Rating
  - SEBI Regulated
- **Download Buttons**:
  - Google Play Store (▶ Get it on Google Play)
  - App Store (🍎 Download on the App Store)

### Why Invest with Aspero Section
Four feature cards:
1. 📈 **High-yield bonds** — 11–18% YTM (tag: "Up to 18% YTM")
2. 🔒 **SEBI regulated & safe** — Fully regulated, demat account (tag: "Fully regulated")
3. ⚡ **Start with ₹5,000** — Low minimum (tag: "Min ₹5,000")
4. 💳 **Monthly payouts** — Predictable income (tag: "Predictable income")

### Testimonials Section
Three 5-star reviews from Aspero users (real names, cities, authentic feedback).

### Final CTA
- Badge reminder: "Invited by Arpit Goyal · Code: ARPIT2026"
- Headline: "Start investing in 10 minutes"
- Subheading: "Complete KYC, browse bonds rated from AAA to BB, and make your first investment today."
- Download buttons (Google Play + App Store)

### Sticky Bottom Bar
- Fixed at bottom (sticky positioning)
- Text: "Ready to earn 12–18% on your money?"
- Text: "Invited by Arpit Goyal · Use code ARPIT2026"
- CTA Button: "Sign Up Free →"

---

## Design System

### Color Palette
```css
--g:      #27AE60;    /* Primary green */
--g-hi:   #4ADE80;    /* Highlight green */
--g-dk:   #1A3C34;    /* Dark green */
--g-dkr:  #0D1F16;    /* Darker green */
--g-mid:  #152D1E;    /* Mid green */
--g-lt:   #ECFDF5;    /* Light green */
--bg:     #F5F7F5;    /* Background */
--card:   #FFFFFF;    /* Card background */
--t1:     #111827;    /* Primary text */
--t2:     #6B7280;    /* Secondary text */
--border: #E5E7EB;    /* Borders */
--sh:     0 4px 20px rgba(0,0,0,0.07);  /* Shadow */
```

### Typography
- Font family: **Inter** (Google Fonts)
- Weights: 400 (regular), 500 (medium), 600 (semibold), 700 (bold), 800 (extra bold)
- Responsive: scales from mobile to desktop

### Components
- **Buttons**: Ghost, Outline, Green, White variants
- **Pills**: Status indicators (Signup, KYC, Ready, Trade, Active)
- **Cards**: Shadow-based depth, rounded corners (16px)
- **Forms**: Inline, minimal styling

---

## Mobile Preview Feature

### Phone Overlay
A floating phone FAB (Floating Action Button) at bottom-right opens an iframe preview:
- Shows full Pages 1, 2, 3 in a mobile phone frame (320px width)
- Includes notch, home indicator
- Uses hash parameter `?page=0|1|2` to navigate between pages

### Page Switcher
Three pills below the phone frame:
- "Landing" (Page 1)
- "Dashboard" (Page 2)
- "Share Page" (Page 3)

---

## Responsiveness

- **Desktop** (>768px): Full 2-column layouts, expanded tables
- **Tablet** (768px–480px): Condensed, single-column
- **Mobile** (<480px): Stacked, touch-optimized, hidden columns in table

---

## JavaScript Functions

| Function | Purpose |
|----------|---------|
| `showPage(id)` | Switch between pages; scroll to top |
| `copyCode(e)` | Copy referral code to clipboard |
| `copyLink(e)` | Copy referral link to clipboard |
| `fallbackCopy(text)` | Fallback clipboard for older browsers |
| `shareWA()` | Open WhatsApp with pre-filled message |
| `shareTG()` | Open Telegram with pre-filled message |
| `nudgeFriend(name, wa, status)` | Send nudge message via WhatsApp |
| `dlApp(store)` | Deep link to Google Play or App Store |
| `toggleDashEmpty()` | Toggle dashboard empty/filled state (demo) |
| `renderList()` | Render referral table dynamically |
| `animateProgress()` | Animate progress bar on dashboard |
| `openPhone()` | Open mobile preview overlay |
| `phoneNav(idx)` | Navigate between pages in phone preview |

---

## API Integration Points (Future)

When integrated with Aspero backend:
1. **Fetch referral data**: GET `/api/referrals/` → populate dashboard
2. **Submit referral code**: POST `/api/referrals/share` → track share actions
3. **Fetch analytics**: GET `/api/referrals/analytics` → KPIs and progress
4. **Nudge referral**: POST `/api/referrals/{id}/nudge` → send reminder
5. **Validate referral code**: GET `/api/referrals/validate/{code}` → for invitee

---

## Accessibility & Compliance

- ✓ Semantic HTML5 structure
- ✓ ARIA labels on buttons
- ✓ Color contrast (WCAG AA)
- ✓ Keyboard navigation support
- ✓ Mobile-friendly viewport
- ✓ SEBI compliance messaging (regulated, demat account safety)
