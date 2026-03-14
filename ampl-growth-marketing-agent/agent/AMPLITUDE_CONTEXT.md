<!-- SYNCED FROM: ../../../funnel-optimization-agent/AMPLITUDE_CONTEXT.md -->
<!-- To update: run scripts/sync_context.sh from the repo root -->

# 📊 Amplitude Events Context - Aspero Bond Investment App

**Project:** Aspero B2C Mobile - Bond Investment Platform
**Amplitude Project ID:** 506002
**Last Updated:** 2026-03-09
**Status:** ✅ Complete Signup Funnel Events Documented

---

## 🎯 Event Funnels Overview

```
SIGNUP FUNNEL - COMPLETE
├── Stage 1: Mobile Number Verification
│   ├── SIGNIN_PAGE_VIEW (Multiple)
│   ├── SIGNIN_PAGE_NUMBER_ENTERED (Multiple)
│   ├── SIGNIN_PAGE_VERIFY_OTP_SENT (Multiple)
│   ├── VERIFY_OTP_PAGE_VIEW (Multiple)
│   ├── VERIFY_OTP_ENTERED (Multiple)
│   └── VERIFY_OTP_SUCCESS (Multiple - can repeat on login)
│
├── Stage 2: Email Verification
│   ├── EMAIL_PAGE_VIEW (Once)
│   ├── EMAIL_PAGE_VERIFY_CLICKED (Once)
│   ├── EMAIL_PAGE_VERIFY_API_SUCCESS (Once)
│   ├── EMAIL_VERIFY_OTP_PAGE_VIEW (Once)
│   ├── EMAIL_VERIFY_OTP_ENTERED (Once)
│   └── EMAIL_VERIFY_OTP_SUCCESS (Once - Signup only)
│
└── Stage 3: Secure PIN Setup
    ├── SETUP_SECURE_PIN_PAGE_VIEW (Once)
    ├── SETUP_SECURE_PIN_SUBMIT_CLICK (Once)
    └── SETUP_SECURE_PIN_SUCCESS (Once - USER REGISTERED!)

🔄 PENDING:
├── KYC_FUNNEL (To be shared)
├── INVESTMENT_FUNNEL (To be shared)
└── OTHER_FUNNELS (To be shared)
```

---

## 📋 COMPLETE SIGNUP FUNNEL - ALL EVENTS

### **Stage 1: Mobile Number Verification (Repeatable)**

| # | Event | Type | Occurs | Quality | Description |
|---|---|---|---|---|---|
| 1 | **SIGNIN_PAGE_VIEW** | Page View | Multiple | ⭐⭐ | User lands on signin page to enter mobile number |
| 2 | **SIGNIN_PAGE_NUMBER_ENTERED** | User Action | Multiple | ⭐⭐ | User enters mobile number |
| 3 | **SIGNIN_PAGE_VERIFY_OTP_SENT** | System Action | Multiple | ⭐⭐ | OTP sent to mobile number via SMS/API |
| 4 | **VERIFY_OTP_PAGE_VIEW** | Page View | Multiple | ⭐⭐ | User navigates to OTP entry page |
| 5 | **VERIFY_OTP_ENTERED** | User Action | Multiple | ⭐⭐⭐ | User enters OTP code from mobile |
| 6 | **VERIFY_OTP_SUCCESS** | ✅ Conversion | **Multiple** | **⭐⭐⭐⭐** | **Mobile verified - User can login (repeatable each login)** |
| 7 | **VERIFY_OTP_FAILED** | ❌ Failure | Multiple | ⭐ | OTP verification failed (wrong code, expired, etc.) |

### **Stage 2: Email Verification (One-Time During Signup)**

| # | Event | Type | Occurs | Quality | Description |
|---|---|---|---|---|---|
| 8 | **EMAIL_PAGE_VIEW** | Page View | Once | ⭐⭐ | User lands on email verification page |
| 9 | **EMAIL_PAGE_VERIFY_CLICKED** | User Action | Once | ⭐⭐ | User clicks "Verify" or "Send OTP" button |
| 10 | **EMAIL_PAGE_VERIFY_API_SUCCESS** | System Action | Once | ⭐⭐ | API successfully sends OTP to user's email |
| 11 | **EMAIL_VERIFY_OTP_PAGE_VIEW** | Page View | Once | ⭐⭐ | User navigates to email OTP entry page |
| 12 | **EMAIL_VERIFY_OTP_ENTERED** | User Action | Once | ⭐⭐⭐ | User enters OTP code from email |
| 13 | **EMAIL_VERIFY_OTP_SUCCESS** | ✅ Conversion | **Once** | **⭐⭐⭐⭐** | **Email verified - Signup-only event** |
| 14 | **EMAIL_PAGE_VERIFY_API_FAILED** | ❌ Failure | Once | ⭐ | Failed to send OTP to email (API error, invalid email, etc.) |
| 15 | **EMAIL_VERIFY_OTP_FAILED** | ❌ Failure | Once | ⭐ | Email OTP verification failed (wrong code, expired, etc.) |

### **Stage 3: Secure PIN Setup (One-Time During Signup)**

| # | Event | Type | Occurs | Quality | Description |
|---|---|---|---|---|---|
| 16 | **SETUP_SECURE_PIN_PAGE_VIEW** | Page View | Once | ⭐⭐ | User lands on PIN setup page |
| 17 | **SETUP_SECURE_PIN_SUBMIT_CLICK** | User Action | Once | ⭐⭐ | User clicks submit button for PIN setup |
| 18 | **SETUP_SECURE_PIN_SUCCESS** | ✅ Conversion | **Once** | **⭐⭐⭐⭐⭐** | **USER REGISTERED - Can now use platform for KYC & Investment** |
| 19 | **SETUP_SECURE_PIN_FAILED** | ❌ Failure | Once | ⭐ | PIN setup failed (validation error, API error, etc.) |

---

## 🎯 EVENT CLASSIFICATION

### **By Occurrence Type**

**Repeatable Events (Can happen multiple times per user):**
- SIGNIN_PAGE_VIEW
- SIGNIN_PAGE_NUMBER_ENTERED
- SIGNIN_PAGE_VERIFY_OTP_SENT
- VERIFY_OTP_PAGE_VIEW
- VERIFY_OTP_ENTERED
- VERIFY_OTP_SUCCESS ← Can repeat on each login
- VERIFY_OTP_FAILED

**One-Time Events (Only during signup, unique per user):**
- EMAIL_PAGE_VIEW
- EMAIL_PAGE_VERIFY_CLICKED
- EMAIL_PAGE_VERIFY_API_SUCCESS
- EMAIL_VERIFY_OTP_PAGE_VIEW
- EMAIL_VERIFY_OTP_ENTERED
- EMAIL_VERIFY_OTP_SUCCESS ← Signup-only
- EMAIL_PAGE_VERIFY_API_FAILED
- EMAIL_VERIFY_OTP_FAILED
- SETUP_SECURE_PIN_PAGE_VIEW
- SETUP_SECURE_PIN_SUBMIT_CLICK
- SETUP_SECURE_PIN_SUCCESS ← USER REGISTERED (Most important!)
- SETUP_SECURE_PIN_FAILED

---

## ⭐ QUALITY TIER SYSTEM

### **⭐ LOW QUALITY (1 star)**
- Page views (navigation signal only, not completion)
- Generic user actions (clicking, entering)
- Failed events (indicate drop-off)

Examples:
- SIGNIN_PAGE_VIEW (just landing)
- VERIFY_OTP_FAILED (user couldn't verify)

### **⭐⭐ MEDIUM QUALITY (2 stars)**
- Page interactions (user took action)
- System confirmations (OTP sent)
- User input capture (number entered)

Examples:
- SIGNIN_PAGE_NUMBER_ENTERED
- EMAIL_PAGE_VERIFY_API_SUCCESS

### **⭐⭐⭐ HIGH QUALITY (3 stars)**
- User verification steps
- Completed user actions
- Second-factor verification

Examples:
- VERIFY_OTP_ENTERED (user verified code)
- EMAIL_VERIFY_OTP_ENTERED (verified email OTP)

### **⭐⭐⭐⭐ VERY HIGH QUALITY (4 stars)**
- Successful verification events
- Email verified
- Mobile verified
- Ready for signup completion

Examples:
- VERIFY_OTP_SUCCESS (mobile verified)
- EMAIL_VERIFY_OTP_SUCCESS (email verified)

### **⭐⭐⭐⭐⭐ CRITICAL QUALITY (5 stars)**
- USER REGISTERED
- Can use platform
- Ready for KYC and Investment flows

Examples:
- **SETUP_SECURE_PIN_SUCCESS** ← This is the most important event!

---

## 📊 FUNNEL FLOW DIAGRAM

```
START: User lands on app
           ↓
SIGNIN_PAGE_VIEW (100% - all users)
           ↓
SIGNIN_PAGE_NUMBER_ENTERED (Android: 35.8%, iOS: 58.1%, Web: 67.8%)
  [⚠️ Major drop: 64.2% Android, 41.9% iOS, 32.2% Web]
           ↓
SIGNIN_PAGE_VERIFY_OTP_SENT (31.7%)
           ↓
VERIFY_OTP_PAGE_VIEW (31.6%)
           ↓
VERIFY_OTP_ENTERED (30.4%)
  [Small drop: ~4%]
           ↓
✅ VERIFY_OTP_SUCCESS (29.2% Android, 53.8% iOS, 51.3% Web)
   [Mobile verified - user can login]
           ↓
EMAIL_PAGE_VIEW (Once during signup)
           ↓
EMAIL_PAGE_VERIFY_CLICKED
           ↓
EMAIL_PAGE_VERIFY_API_SUCCESS
           ↓
EMAIL_VERIFY_OTP_PAGE_VIEW
           ↓
EMAIL_VERIFY_OTP_ENTERED
           ↓
✅ EMAIL_VERIFY_OTP_SUCCESS
   [Email verified - continues signup]
           ↓
SETUP_SECURE_PIN_PAGE_VIEW
           ↓
SETUP_SECURE_PIN_SUBMIT_CLICK
           ↓
⭐⭐⭐⭐⭐ SETUP_SECURE_PIN_SUCCESS
   [USER REGISTERED! Ready for KYC & Investment]
           ↓
END: User account active
```

---

## 🔑 KEY CHARACTERISTICS

### **Important Notes on Events:**

1. **VERIFY_OTP_SUCCESS is repeatable**
   - Fires every time user logs in (authenticates with OTP)
   - NOT just during signup
   - Use EMAIL_VERIFY_OTP_SUCCESS + SETUP_SECURE_PIN_SUCCESS to identify NEW signups

2. **Email & PIN Setup are ONE-TIME**
   - Only fire during initial signup
   - Never fire again for returning users
   - Perfect for identifying first-time user funnel

3. **Device/Platform Breakdown Available**
   - Android: 29.2% completion rate
   - iOS: 53.8% completion rate
   - Web: 51.3% completion rate
   - Gap: iOS/Web are 1.85x higher than Android

4. **Biggest Drop-off Points**
   - PAGE_VIEW → NUMBER_ENTERED: 64% drop (especially Android)
   - Likely UX issue in number entry field

---

## 💡 ANALYSIS OPPORTUNITIES

### **For User Quality Analysis:**

**Use SETUP_SECURE_PIN_SUCCESS to identify:**
- ✅ New registered users
- ✅ Users who completed entire signup flow
- ✅ Base population for KYC tracking

**Use EMAIL_VERIFY_OTP_SUCCESS to identify:**
- ✅ Users who completed email verification
- ✅ Users who have verified contact info
- ✅ Potential high-quality leads

**Use VERIFY_OTP_SUCCESS with device_model to:**
- ✅ Segment by device tier (Premium/Mid-range/Budget)
- ✅ Analyze signup completion by device quality
- ✅ Identify low-income users in signup funnel

---

## 🚀 RECOMMENDATIONS

### **For Immediate Analysis:**

1. **Filter for first-time users only**
   - Use: SETUP_SECURE_PIN_SUCCESS as marker
   - Exclude VERIFY_OTP_SUCCESS (repeatable)

2. **Analyze by device tier**
   - Get device_model from SETUP_SECURE_PIN_SUCCESS events
   - Classify as Premium/Mid-range/Budget
   - Compare conversion rates

3. **Identify drop-off patterns**
   - Largest drop: SIGNIN_PAGE_VIEW → NUMBER_ENTERED (64% Android)
   - Needs Android UX investigation

4. **Track completion by platform**
   - Web & iOS: ~51-54% complete signup
   - Android: ~29% complete signup
   - Significant platform gap needs addressing

---

## 📋 PENDING INFORMATION

🔄 **To be collected:**

- [ ] **Actual funnel numbers** (user counts per event)
- [ ] **KYC Funnel events** (KYC_STARTED → KYC_COMPLETED)
- [ ] **Investment Funnel events** (INVESTMENT_INITIATED → COMPLETED)
- [ ] **Other Funnels** (Payment, Withdrawal, etc.)
- [ ] **Custom event properties** (retry_count, time_taken, etc.)

---

## 📚 FILE HISTORY

| Date | Change | Status |
|---|---|---|
| 2026-03-07 | Initial context file created | ✅ |
| 2026-03-07 | Added complete Signup Funnel | ✅ |
| 2026-03-09 | API troubleshooting completed | ✅ |
| 2026-03-09 | Complete event documentation | ✅ |
| PENDING | Add funnel numbers/metrics | 🔄 |
| PENDING | Add KYC Funnel | 🔄 |
| PENDING | Add Investment Funnel | 🔄 |

---

## ✅ SUMMARY

**Complete Signup Funnel Documented:**
- ✅ 19 events identified
- ✅ Quality ratings assigned
- ✅ Event flow documented
- ✅ Platform-specific data noted
- ✅ One-time vs repeatable classified

**Next Steps:**
1. 📊 Export funnel numbers from Amplitude
2. 🎯 Add actual user counts per event
3. 📈 Create KYC Funnel documentation
4. 💰 Create Investment Funnel documentation
