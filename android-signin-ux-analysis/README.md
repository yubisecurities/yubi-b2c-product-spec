# Android Sign-In UX Analysis: 64% Drop-off Root Cause Investigation

## 📊 Project Overview

**Issue:** 64.2% user drop-off at mobile number entry step on Android devices
- Android completion: **35.8%**
- iOS completion: **58.1%** (1.8x higher)
- Web completion: **67.8%** (1.9x higher)

**Impact:** Only 29.2% of Android users complete signup vs 53.8% on iOS

**Status:** ✅ Root cause identified and fixes provided

---

## 📁 Project Structure

```
android-signin-ux-analysis/
├── README.md                          # This file
├── ANALYSIS_REPORT.md                 # Comprehensive problem analysis
├── ROOT_CAUSE_ANALYSIS.md             # Detailed root cause breakdown
├── CODE_SAMPLES_PROBLEMATIC.md        # Exact problematic code found
├── RECOMMENDED_FIXES.md               # Complete fix implementation guide
└── VERIFICATION_TESTING_GUIDE.md      # Testing & validation procedures
```

---

## 🔍 Key Findings

### 5 Critical Issues Found

| # | Issue | File | Severity | Impact |
|---|-------|------|----------|--------|
| 1 | Input field disabled on Android with phone hint | `SignInForm.tsx` (L48-71) | 🔴 CRITICAL | Can't enter mobile number |
| 2 | Phone hint has no error recovery | `usePhoneHint.ts` | 🟠 HIGH | No fallback when hint fails |
| 3 | Wrong keyboard layout mode | `AndroidManifest.xml` (L38) | 🟠 HIGH | Form hidden on small screens |
| 4 | Keyboard awareness disabled | `Utils.ts` & `FormSkeleton.tsx` | 🟡 MEDIUM | Field hidden by keyboard |
| 5 | Silent input validation | `useMobileNumberScreen.tsx` | 🟡 MEDIUM | User confusion about errors |

### Root Cause (PRIMARY)

**Location:** `src/molecules/MobileNoForm/SignInForm.tsx`, Lines 48-71

```typescript
// When phone hint is enabled on Android, field becomes non-editable
{isAndroid() && showPhoneHint ? (
  <TouchableOpacity onPress={handlePhoneHint}>
    <View pointerEvents='none'>
      <InputField
        editable={false}           // ❌ FIELD DISABLED
        multiline={true}           // ❌ WRONG VALUE
        // ...
      />
    </View>
  </TouchableOpacity>
) : (
  // iOS version has editable={true}
)}
```

**Why it's broken:**
- Input field set to `editable={false}` on Android with phone hint
- When phone hint fails (common scenario), no fallback to manual entry
- User attempts to enter number → field is non-responsive → User leaves

---

## 💡 Business Impact

### Current State (64% Drop-off)
```
100 Android users land on signin
  ↓
35.8 enter mobile number (64.2% LOST)
  ↓
29.2 complete signup
  ↓
Result: Only 29.2% conversion
```

### After Fix (Expected 54-62% Improvement)
```
100 Android users land on signin
  ↓
55-67 enter mobile number (matching iOS)
  ↓
50-62 complete signup
  ↓
Result: 50-62% conversion (+54-62% improvement!)
```

**Potential Impact:** Could mean thousands of additional registered users per week

---

## 📖 Document Guide

### For Quick Understanding
1. Start with: **ANALYSIS_REPORT.md** (Executive summary)
2. Then read: **CODE_SAMPLES_PROBLEMATIC.md** (See the exact issues)

### For Implementation
1. Read: **RECOMMENDED_FIXES.md** (All 5 fixes with code examples)
2. Follow: **VERIFICATION_TESTING_GUIDE.md** (How to test each fix)

### For Deep Dive
1. **ROOT_CAUSE_ANALYSIS.md** (Detailed technical breakdown)
2. **CODE_SAMPLES_PROBLEMATIC.md** (Exact problematic code)

---

## 🚀 Quick Start - What to Do

### Phase 1: Verify Issue (1 hour)
```bash
# 1. Read the analysis
cat ANALYSIS_REPORT.md

# 2. Check the problematic code
cat CODE_SAMPLES_PROBLEMATIC.md

# 3. Test on Android device
# Open app → Go to signin → Try to tap input field
# Expected: Field is non-responsive (bug confirmed)
```

### Phase 2: Implement Fixes (2-4 hours)
```bash
# Create feature branch
git checkout -b fix/android-signin-mobile-number-input

# Follow fixes in this order:
# 1. CRITICAL: Fix SignInForm.tsx (editable input field)
# 2. HIGH: Fix usePhoneHint.ts (error handling)
# 3. HIGH: Fix AndroidManifest.xml (keyboard mode)
# 4. MEDIUM: Fix keyboard awareness
# 5. MEDIUM: Fix validation feedback

# Use: RECOMMENDED_FIXES.md (complete code samples provided)
```

### Phase 3: Test & Validate (2-3 hours)
```bash
# Follow all testing steps in VERIFICATION_TESTING_GUIDE.md

# Build and test on multiple Android devices:
npm run android

# Run regression tests on iOS/Web:
npm run ios
npm start

# Monitor Amplitude for improvement after deploy
```

---

## 📊 Expected Metrics After Fix

### Amplitude Events to Monitor

**Before Fix:**
```
SIGNIN_PAGE_VIEW: 100%
SIGNIN_PAGE_NUMBER_ENTERED: 35.8% (Android) ← 64% DROP-OFF
VERIFY_OTP_SUCCESS: 29.2% (Android)
```

**After Fix (Expected):**
```
SIGNIN_PAGE_VIEW: 100%
SIGNIN_PAGE_NUMBER_ENTERED: 55-67% (Android) ← RECOVERED
VERIFY_OTP_SUCCESS: 50-62% (Android)
```

### Success Criteria
- [ ] Android SIGNIN_PAGE_NUMBER_ENTERED ≥ 50%
- [ ] Android/iOS gap < 1.2x (currently 1.8x)
- [ ] Overall Android signup completion ≥ 45%
- [ ] No regression on iOS/Web

---

## 🔧 Files to Modify

```
Primary (CRITICAL):
├── src/molecules/MobileNoForm/SignInForm.tsx
├── src/molecules/MobileNoForm/hooks/usePhoneHint.ts

Secondary (HIGH):
├── android/app/src/main/AndroidManifest.xml

Tertiary (MEDIUM):
├── src/molecules/formSkeleton/FormSkeleton.tsx
├── src/molecules/keyboardAvoidingViewWrapper/helper/Utils.ts
└── src/screens/onboarding/MobileNumberFlow/mobileNumberVerification/hooks/useMobileNumberScreen.tsx
```

---

## 🧪 Testing Devices

**Recommended Test Devices:**
```
Priority 1 (Most affected):
- Redmi 9 / 9A / 9C (budget, 360×720)
- Realme 6i / 7i / 8i (budget, 360×720)
- Infinix Note 10 (budget, 360×720)

Priority 2:
- Moto G8 / G9 (mid-range)
- OnePlus Nord (mid-range)

Priority 3:
- Pixel 5/6/7 (flagship)
- Samsung Galaxy S22 (flagship)
```

---

## 📈 Analytics Breakdown

**Current Funnel (Android):**
```
Stage 1: Mobile Number Entry ← CRITICAL DROP-OFF HERE
├── PAGE_VIEW: 100% → NUMBER_ENTERED: 35.8% (64% drop-off)
│
Stage 2: OTP Verification (smooth)
├── OTP_PAGE_VIEW: 31.6% → OTP_SUCCESS: 29.2% (small drops)
│
Stage 3: Email + PIN (smooth)
└── EMAIL & PIN: ~29% → SIGNUP_SUCCESS: 29.2%
```

**After Fix (Projected):**
```
Stage 1: Mobile Number Entry ✅ FIXED
├── PAGE_VIEW: 100% → NUMBER_ENTERED: 58-67% (matching iOS)
│
Stage 2: OTP Verification (smooth, unchanged)
├── OTP_PAGE_VIEW: 56% → OTP_SUCCESS: ~55%
│
Stage 3: Email + PIN (smooth, unchanged)
└── EMAIL & PIN: ~55% → SIGNUP_SUCCESS: 50-62%
```

---

## ⏱️ Implementation Timeline

| Phase | Duration | Tasks |
|-------|----------|-------|
| **Analysis & Review** | 1 hour | Read docs, understand issues |
| **Implementation** | 2-4 hours | Implement all 5 fixes |
| **Testing** | 2-3 hours | Test on multiple devices |
| **Code Review** | 1 hour | Get feedback from team |
| **Deployment** | 1 hour | Deploy to staging/prod |
| **Monitoring** | Ongoing | Track Amplitude metrics |

**Total: ~8-11 hours**

---

## 🎯 Key Takeaways

### The Problem
- Android users have 64% drop-off at mobile number entry
- Root cause: Input field disabled when phone hint is enabled
- No fallback when phone hint fails
- Additional issues with keyboard handling and validation

### The Solution
- Make input field always editable (even with phone hint)
- Add proper error handling and user feedback
- Change Android keyboard configuration
- Enable keyboard awareness
- Add validation feedback

### The Impact
- Could improve Android signup completion by 54-62%
- Close 75% of Android/iOS performance gap
- Potential for thousands of additional signups

---

## 🔗 Related Files

- **Amplitude Project ID:** 506002
- **Related Repository:** https://github.com/yubisecurities/yubi-b2c-mobile
- **Signup Funnel Events:** See `AMPLITUDE_CONTEXT.md` in this repo

---

## 📞 Questions?

Refer to specific documents:
- **Why is this happening?** → See `ANALYSIS_REPORT.md`
- **What's the exact code?** → See `CODE_SAMPLES_PROBLEMATIC.md`
- **How do I fix it?** → See `RECOMMENDED_FIXES.md`
- **How do I test it?** → See `VERIFICATION_TESTING_GUIDE.md`

---

## ✅ Checklist Before Starting

- [ ] Read ANALYSIS_REPORT.md (understand the problem)
- [ ] Review CODE_SAMPLES_PROBLEMATIC.md (see the issues)
- [ ] Check recommended fixes in RECOMMENDED_FIXES.md
- [ ] Have Android device or emulator ready
- [ ] Have test accounts for signin flow
- [ ] Have access to Amplitude dashboard
- [ ] Create feature branch

---

*Project Created: 2026-03-09*
*Status: Ready for Implementation*
*Severity: CRITICAL - Blocking 64% of Android signups*
