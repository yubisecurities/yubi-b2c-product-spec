# Verification & Testing Guide - Android Sign-In Issue

This guide helps you verify the issues exist and validate fixes work correctly.

---

## 🔍 Step 1: Verify Issue Exists

### Quick Verification (5 minutes)

**What to look for:**
```
On Android device:
1. Open app
2. Go to sign-in screen
3. Look for "Auto-detect phone" button/UI
4. Try to tap the input field directly
5. Keyboard should NOT appear
6. Field should be unresponsive
```

**Expected result if bug exists:**
- ✅ Phone hint prompt visible
- ❌ Input field non-responsive
- ❌ Can't type anything
- ❌ Keyboard doesn't appear when tapping field

### Code Inspection (2 minutes)

**Check SignInForm.tsx:**
```bash
cd /Users/arpit.goyal/aspero\ repos/yubi-b2c-mobile
grep -n "editable={false}" src/molecules/MobileNoForm/SignInForm.tsx

# Expected output:
# Line containing: editable={false} with isAndroid() condition
```

**Check for pointerEvents:**
```bash
grep -n "pointerEvents" src/molecules/MobileNoForm/SignInForm.tsx

# Expected output:
# Line containing: pointerEvents='none'
```

---

## 🧪 Step 2: Test Scenarios

### Test 1: Phone Hint Enabled (Bug Reproduced)

**Prerequisites:**
- Android device with Google Play Services
- Device has phone account configured

**Steps:**
```
1. Build and run app: npm run android
2. Open app
3. Navigate to signin/mobile number screen
4. Observe phone hint prompt appears
5. Tap the input field (not the button)
6. Result: Nothing should happen ❌ (BUG)
```

**Expected if bug exists:**
```
- Phone hint button is tappable
- Input field is NOT tappable
- No keyboard appears
- No cursor visible
- Can't type anything
```

**Evidence of bug:**
- iOS: Input field would be tappable ✅
- Android with phone hint: Input field NOT tappable ❌

### Test 2: Phone Hint Failure Scenario

**Prerequisites:**
- Android device without phone account, OR
- Deny phone hint permission

**Steps:**
```
1. Open app
2. Navigate to signin/mobile number screen
3. If prompted for permissions, DENY
4. Click phone hint button
5. Wait for it to fail
6. Result: Input field should become editable ❌ (BUG - currently doesn't)
```

**Expected if bug exists:**
```
- Phone hint fails
- No error message shown
- Input field still appears disabled or non-responsive
- User confused
```

### Test 3: Keyboard Behavior on Small Screen

**Prerequisites:**
- Budget Android phone (small screen: 320-360px)
- Or use Android emulator with small screen size

**Steps:**
```
1. Open app on small screen device
2. Navigate to signin
3. Tap mobile number input field
4. Keyboard appears
5. Check what's visible:
   - Is input field visible above keyboard?
   - Is submit button visible?
   - Can you see what you're typing?
```

**Expected if bug exists:**
```
- Input field partially or completely hidden
- Submit button hidden behind keyboard
- Can't see text being typed
- On very small screens: Form completely unusable
```

### Test 4: Input Validation Feedback

**Prerequisites:**
- App running on any device

**Steps:**
```
1. Navigate to signin
2. Try to paste/enter number with 11+ digits
3. Observe response
4. Try to enter invalid number (letters, symbols)
5. Observe response
```

**Expected if bug exists:**
```
- Pasting 11 digits: Field unchanged, no error message
- Invalid input: No error message shown
- Button disabled but user doesn't know why
- No helper text showing digit count
```

---

## 📱 Device Test Matrix

### Test on Various Android Versions:

| Android Version | Device Type | Screen | Test Focus | Expected Issue |
|-----------------|-------------|--------|------------|----------------|
| 10 | Budget (Redmi 9) | Small (360×720) | Keyboard mode | Form hidden |
| 11 | Mid-range (Moto G) | Medium (360×720) | Input disabled | Can't enter |
| 12 | Mid-range (Realme 6i) | Medium (360×720) | Phone hint | No fallback |
| 13 | Budget (Infinix) | Small (360×720) | All issues | All broken |
| 14 | Flagship (Pixel) | Large (411×869) | Minor issues | Might work |

### Test Devices We Should Target:

```
Priority 1 (Most Common in India):
- Redmi 9 / 9A / 9C (budget, small screen)
- Realme 6i / 7i / 8i (budget, small screen)
- Infinix Note 10 (budget, small screen)
- Moto G8 / G9 (budget, small screen)

Priority 2 (Mid-range):
- OnePlus N10 / Nord
- Moto G30 / G40
- Samsung A12 / A13

Priority 3 (Flagship):
- Pixel 5 / 6 / 7
- Samsung S21 / S22
```

---

## 🔧 Step 3: Debug the Issue

### Method 1: Logcat Inspection

```bash
# Connect Android device and run:
adb logcat | grep -i "SIGNIN\|MobileNo\|PhoneHint"

# You should see these events:
# SIGNIN_PAGE_VIEW
# (missing) SIGNIN_PAGE_NUMBER_ENTERED ← Should appear but doesn't
# PHONE_NUMBER_HINT_ERROR or similar

# Absence of SIGNIN_PAGE_NUMBER_ENTERED confirms the bug
```

### Method 2: React DevTools

```bash
# Install React Native DevTools
npm install -g react-devtools

# In separate terminal:
react-devtools

# On device, shake menu → Debug → Connect to debugger
# Inspect component tree:
  FormSkeleton
    └─ MobileNoForm
        └─ SignInForm
            └─ TouchableOpacity (phone hint button)
                └─ InputField (INSPECT THIS)
                   - Check: editable={false} ✅ Confirms bug
                   - Check: pointerEvents='none' ✅ Confirms bug
```

### Method 3: Breakpoint Debugging

```javascript
// In SignInForm.tsx, add breakpoints:

const handlePhoneHint = useCallback(() => {
  debugger; // ← Add breakpoint here
  // ...
}, []);

// Check state values:
// showPhoneHint: true or false?
// mobileNumberText: what's the value?
// What props are passed to InputField?
```

### Method 4: Amplitude Events

```bash
# Check your Amplitude dashboard for:
1. SIGNIN_PAGE_VIEW: Should see 100%
2. SIGNIN_PAGE_NUMBER_ENTERED: Should see 35.8% on Android
3. PHONE_NUMBER_HINT_ERROR: Check error count
4. PHONE_NUMBER_HINT_MOBILE_NUMBER_ENTERED: Check success count

# Gap between SIGNIN_PAGE_VIEW and SIGNIN_PAGE_NUMBER_ENTERED
# should be ~64% on Android = users stuck at input field
```

---

## ✅ Step 4: Validate Fixes

### After Implementing Fix #1 (Editable Input)

**Test:**
```
1. Rebuild app with fix
2. Navigate to signin
3. See phone hint prompt
4. Tap input field directly (not button)
5. Keyboard SHOULD appear ✅
6. SHOULD be able to type ✅
7. SHOULD see cursor ✅
```

**Expected result:**
```
- Input field immediately responsive
- Keyboard appears when tapped
- Can type numbers
- Can also tap phone hint button separately
```

**Verify in code:**
```bash
grep -n "editable={true}" src/molecules/MobileNoForm/SignInForm.tsx
# Should find: editable={true} for Android case

grep -n "pointerEvents='none'" src/molecules/MobileNoForm/SignInForm.tsx
# Should NOT find this (removed)
```

### After Implementing Fix #2 (Error Handling)

**Test:**
```
1. Open app on device without phone account
2. Click phone hint button
3. SHOULD see error message ✅
4. SHOULD still be able to enter number manually ✅
```

**Expected result:**
```
- Clear error message shown: "Phone hint not available"
- Input field still editable
- No confusion about what happened
```

**Monitor Amplitude:**
```
- PHONE_NUMBER_HINT_ERROR event with error details
- SIGNIN_PAGE_NUMBER_ENTERED increases (fallback works)
```

### After Implementing Fix #3 (AndroidManifest)

**Test:**
```
1. Rebuild on small screen device
2. Open app
3. Tap input field
4. Keyboard appears
5. Entire form should be visible ✅
6. Submit button should be accessible ✅
7. Can scroll if needed ✅
```

**Expected result:**
```
- No more "form pushed off-screen"
- All UI elements reachable
- Works on all screen sizes
```

### After Implementing Fix #4 (Keyboard Awareness)

**Test:**
```
1. Rebuild app
2. On small screen device
3. Tap input field
4. Observe layout behavior
5. Input should stay visible ✅
6. Should auto-scroll if needed ✅
```

### After Implementing Fix #5 (Validation Feedback)

**Test:**
```
1. Rebuild app
2. Try to enter 11+ digits
3. Should see error: "Only 10 digits" ✅
4. Try invalid number
5. Should see: "Invalid mobile number" ✅
6. Enter valid number
7. Should see: "10/10 digits" ✅ and button enabled
```

---

## 📊 Step 5: Measure Impact

### Before Fix (Current State)

**Amplitude Data:**
```
SIGNIN_PAGE_VIEW: 100% (1000 users)
SIGNIN_PAGE_NUMBER_ENTERED: 35.8% (358 users) ← 64% DROP
VERIFY_OTP_SUCCESS: 29.2% (292 users)

Android Signup Completion: 29.2%
iOS Signup Completion: 53.8%
Gap: -24.6 percentage points
```

### After Fix (Expected)

**Amplitude Data (after 1-2 weeks):**
```
SIGNIN_PAGE_VIEW: 100% (1000 users)
SIGNIN_PAGE_NUMBER_ENTERED: 55-67% (550-670 users) ← RECOVERED
VERIFY_OTP_SUCCESS: 50-62% (500-620 users)

Expected Android Signup Completion: 50-62%
Expected iOS Signup Completion: 53.8% (unchanged)
New Gap: 0-8 percentage points (FIXED!)

Improvement: +54-62% more signups on Android
```

### KPIs to Monitor

```
1. SIGNIN_PAGE_NUMBER_ENTERED conversion rate
   Before: 35.8%
   Target: 55-67% (matching iOS)
   Success: ≥ 50%

2. Android vs iOS parity
   Before: 1.8x worse
   Target: <1.1x worse
   Success: <1.2x

3. PHONE_NUMBER_HINT error rate
   Monitor: How many phone hint errors occur?
   Target: <10% of attempts
   Success: Errors don't block manual entry

4. Overall signup completion
   Before: 29.2% Android
   Target: 50%+ Android
   Success: 45%+
```

---

## 🚀 Step 6: Performance & Regression Testing

### Performance Tests

```bash
# Before fix:
npm run android -- --profile
# Measure: Frame drops at signin screen

# After fix:
npm run android -- --profile
# Expected: No regression in performance
# Should be: Same or better performance
```

### Regression Testing

**Test on iOS:**
```
1. Rebuild on iOS
2. Go through entire signin flow
3. Verify nothing broke
4. Should work exactly as before ✅
```

**Test on Web:**
```
1. Rebuild web
2. Go through signin flow
3. Verify nothing broke
4. Should work exactly as before ✅
```

**Test other flows:**
```
1. Returning user login
2. Forgot password flow
3. Email verification
4. PIN setup
5. KYC flow
6. Investment flow

Expected: All unchanged and working
```

---

## 📋 Testing Checklist

### Pre-Implementation
- [ ] Verify bug exists on Android (phone hint scenario)
- [ ] Verify iOS works correctly (for comparison)
- [ ] Check AndroidManifest for adjustPan
- [ ] Check SignInForm for editable={false}
- [ ] Confirm Amplitude shows 64% drop-off

### Implementation
- [ ] Create feature branch: `fix/android-signin-mobile-number-input`
- [ ] Implement Fix #1: Editable input field
- [ ] Implement Fix #2: Error handling
- [ ] Implement Fix #3: AndroidManifest keyboard mode
- [ ] Implement Fix #4: Keyboard awareness
- [ ] Implement Fix #5: Validation feedback

### Unit Testing
- [ ] SignInForm renders correctly
- [ ] usePhoneHint handles all error cases
- [ ] onChangeText validates correctly
- [ ] All text edge cases handled

### Integration Testing
- [ ] Phone hint success path works
- [ ] Phone hint failure path shows error
- [ ] Manual entry as fallback works
- [ ] Keyboard behavior correct

### Device Testing
- [ ] Test on Android 10, 11, 12, 13, 14
- [ ] Test on budget phones (small screens)
- [ ] Test on flagship phones (large screens)
- [ ] Test on both orientations (portrait/landscape)
- [ ] Test with various keyboard types

### Regression Testing
- [ ] iOS signin still works
- [ ] Web signin still works
- [ ] Other flows unaffected
- [ ] No performance regression

### Analytics Validation
- [ ] SIGNIN_PAGE_NUMBER_ENTERED increases
- [ ] PHONE_NUMBER_HINT_ERROR properly tracked
- [ ] Overall signup completion rate improves
- [ ] Android/iOS gap closes

---

## 📞 Support & Troubleshooting

### If Tests Fail After Fix

**Problem:** Input field still not editable
```
Check:
1. Are you running latest code? (npm start, rebuild)
2. Is editable={true} actually in code?
3. Is pointerEvents removed?
4. Try: npm run android -- --reset-cache
```

**Problem:** Keyboard doesn't appear on tap
```
Check:
1. Is keyboardType='number-pad' set?
2. Is autoFocus working?
3. Is InputField component correct?
4. Check: TextInput component implementation
```

**Problem:** Phone hint still shows error
```
Check:
1. Device has Google Play Services?
2. Phone account configured on device?
3. App has required permissions?
4. Try: Clear app data, reinstall
```

**Problem:** Form still hidden on small screen
```
Check:
1. Is AndroidManifest using adjustResize?
2. Is keyboard awareness enabled?
3. Try: test on different device with smaller screen
```

---

*Last Updated: 2026-03-09*
*For issues or questions, refer to the ANALYSIS_REPORT.md*
