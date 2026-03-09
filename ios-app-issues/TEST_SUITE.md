# Test Suite — iOS App Issues

---

## Test Environment Setup

### Required
- Mac with Xcode 15+
- At least 2 physical iOS devices (see device matrix below)
- Apple Developer account with provisioning profile for the app
- Release build (not debug) for push notification and APNs tests

### Simulator Limitations
| Test | Use Simulator? | Notes |
|------|---------------|-------|
| Push notifications | No | Simulators cannot receive APNs |
| Notch / safe area | Yes (with caution) | Use iPhone 14 Pro simulator for Dynamic Island |
| Keyboard overlap | Yes | Reasonably accurate |
| Camera / liveness | No | No camera hardware |
| Deep links | Yes | Universal Links work in simulator |
| Document preview | Yes | File system accessible |

### Device Matrix

| Device | iOS | Priority | What it tests |
|--------|-----|----------|---------------|
| iPhone SE (3rd gen) | 17 | P0 | No notch — baseline keyboard/layout |
| iPhone 13 | 17 | P0 | Standard notch — most common user device |
| iPhone 14 Pro | 17 | P0 | Dynamic Island — newest layout constraints |
| iPhone X or XS | 16 | P1 | First-gen notch, older iOS |
| iPhone 15 Pro Max | 17 | P1 | Large screen, latest hardware |

---

## Test Suite 1: Push Notifications / APNs (P0)

### TC1.1: APNs environment — production build receives notifications

**Prerequisites:**
- Release build signed with production provisioning profile
- Backend has the production APNs certificate configured
- Test device registered with the backend (signed-in account)

**Steps:**
1. Install release IPA on a physical device
2. Sign in to the app
3. Observe: does the OS show a "Allow Notifications?" prompt?
4. Grant permission
5. From the backend/admin panel, send a test push notification to the test device
6. Observe: does the notification arrive?

**Pass criteria:**
- [ ] Notification prompt shown on first appropriate app open after sign-in
- [ ] Test push notification delivered to device within 30 seconds
- [ ] Tapping the notification opens the app and navigates to the correct screen

**Fail indicators:**
- No notification prompt ever appears
- Notification sent but never arrives on device
- `aps-environment` mismatch error in device console (check via Xcode → Devices & Simulators → device logs)

---

### TC1.2: APNs environment — debug build does NOT break on device

**Steps:**
1. Install debug build on physical device
2. Sign in
3. Trigger a notification from backend (targeted at development APNs)

**Pass criteria:**
- [ ] Debug build connects to APNs sandbox
- [ ] No crash or error related to APNs

---

### TC1.3: iOS notification permission prompt timing

**Steps:**
1. Fresh install of the app
2. Complete sign-in flow
3. Navigate through the app normally

**Pass criteria:**
- [ ] Notification permission prompt appears at an appropriate moment (e.g. after sign-in, not at cold start)
- [ ] If permission denied, app handles gracefully — no crash, no persistent prompting

---

## Test Suite 2: Safe Area & Keyboard Handling (P1)

### TC2.1: KYC PAN screen — keyboard does not overlap input on iPhone 14 Pro

**Steps:**
1. Navigate to KYC → PAN entry screen on iPhone 14 Pro
2. Tap the PAN input field
3. Observe the keyboard

**Pass criteria:**
- [ ] PAN input field is fully visible above the keyboard
- [ ] No part of the input is behind the keyboard
- [ ] Form scroll position adjusts when keyboard appears

**Fail indicators:**
- Input field hidden behind keyboard
- Screen does not scroll when keyboard opens

---

### TC2.2: KYC Bank Verify — keyboard offset correct on iPhone SE

**Steps:**
1. Navigate to KYC → Bank Verification screen on iPhone SE
2. Tap an input field
3. Observe layout

**Pass criteria:**
- [ ] Input visible above keyboard with appropriate spacing (not excessive gap)
- [ ] No content cut off at top of screen

---

### TC2.3: KYC Nominee — keyboard handling on iPhone 13

**Steps:**
1. Navigate to KYC → Nominee → Add Nominee
2. Tap DOB field, then name field, then address field in sequence
3. Each time, verify the active field is above the keyboard

**Pass criteria:**
- [ ] All fields accessible with keyboard open
- [ ] Scrolling within the form works while keyboard is visible

---

### TC2.4: Signature pad — fully visible and interactive on iPhone 14 Pro

**Steps:**
1. Navigate to KYC → Wet Signature screen on iPhone 14 Pro
2. Observe the canvas area

**Pass criteria:**
- [ ] Canvas starts below the Dynamic Island (not under it)
- [ ] Drawing in the top portion of the canvas registers correctly
- [ ] The drawn position matches where the finger touches

**Fail indicators:**
- Canvas top edge is behind the Dynamic Island
- Touch events offset from drawn lines

---

## Test Suite 3: PAN & DOB Input (P1)

### TC3.1: PAN field accepts letters on iOS

**Steps:**
1. Navigate to KYC → AadhaarPan → PAN entry on any iPhone
2. Tap the PAN input field
3. Attempt to type: `ABCDE1234F`

**Pass criteria:**
- [ ] Full alphanumeric keyboard appears (not numbers-only keyboard)
- [ ] Letters can be typed
- [ ] Letters auto-capitalise
- [ ] Input capped at 10 characters
- [ ] `ABCDE1234F` entered successfully

**Fail indicators:**
- Only numbers and symbols keyboard shows up
- Letters cannot be typed

---

### TC3.2: DOB field — date entry is user-friendly

**Steps:**
1. Navigate to KYC → Nominee → Add Nominee → DOB field
2. Tap the field

**Pass criteria:**
- [ ] Either a date picker appears (native iOS UX) OR
- [ ] A numeric keyboard appears that accepts date separators
- [ ] User can enter a valid date without friction

---

## Test Suite 4: Document Download & Preview (P1)

### TC4.1: PDF downloads and opens without crash

**Steps:**
1. Navigate to any screen that triggers a document download (e.g. statement download, KYC document)
2. Trigger the download
3. Wait for completion
4. Observe the preview

**Pass criteria:**
- [ ] PDF preview opens
- [ ] "Share" / "Open In" sheet available
- [ ] No crash
- [ ] `onSuccess` callback fires only after preview opens

**Fail indicators:**
- App crashes after download
- Success toast shown but no preview appears
- Native exception in device logs

---

### TC4.2: Document preview handles missing file gracefully

**Steps:**
1. Download a document
2. Before opening the preview, delete the file from the device's Documents directory (via Files app or adb shell equivalent)
3. Attempt to open the preview

**Pass criteria:**
- [ ] App shows an error message ("Could not open document")
- [ ] App does NOT crash
- [ ] User can retry

---

### TC4.3: Document directory does not grow unboundedly

**Steps:**
1. Download 5+ documents over 2+ sessions
2. Log out and log back in
3. Check app's Documents directory size (Xcode → Devices & Simulators → select device → select app → "Disk" section)

**Pass criteria:**
- [ ] Documents older than 24 hours are not present after logout
- [ ] Storage used by the app's Documents directory is bounded

---

## Test Suite 5: Status Bar (P2)

### TC5.1: Status bar legible on all key screens

**Steps:**
1. Visit each of the following screens: Home, KYC intro, Sign-in, Onboarding, Wallet
2. On each screen, observe the status bar (time, battery, signal)

**Pass criteria:**
- [ ] On dark-background screens: status bar text is white and legible
- [ ] On light-background screens: status bar text is dark and legible
- [ ] No screen has invisible (white on white or black on black) status bar

---

### TC5.2: Status bar style updates during navigation

**Steps:**
1. Start on a light-background screen (e.g. Sign-in)
2. Navigate to a dark-background screen (e.g. Home dark header)
3. Navigate back

**Pass criteria:**
- [ ] Status bar style changes when navigating between screens
- [ ] No visible flicker during the transition

---

## Test Suite 6: Universal Links (P2)

### TC6.1: aspero.in links open the app

**Prerequisites:** App installed on device

**Steps:**
1. Open Safari on the test device
2. Type `https://www.aspero.in/any-path` and navigate
3. Observe: does the app open or does Safari load the website?

**Pass criteria:**
- [ ] App opens (not Safari)
- [ ] App navigates to the correct screen matching the URL path

---

### TC6.2: Push notification deep link opens correct screen

**Steps:**
1. Send a push notification with a deep link URL in the payload
2. Tap the notification when app is killed

**Pass criteria:**
- [ ] App opens and navigates directly to the linked screen
- [ ] Not just the home screen

---

## Test Suite 7: End-to-End KYC Flow on iOS (Regression)

Run after all P0 and P1 fixes are merged.

| Step | Device | Pass Criteria |
|------|--------|---------------|
| Sign in | iPhone 13 | OTP received and verified |
| PAN entry | iPhone 14 Pro | Full PAN typed successfully; keyboard doesn't cover field |
| Bank verification | iPhone SE | Fields visible above keyboard |
| Signature | iPhone 14 Pro | Canvas fully visible; signature captured correctly |
| Nominee — DOB | iPhone 13 | DOB entered; no keyboard issues |
| Document download | iPhone 13 | PDF opens without crash |

---

## Regression Test Checklist

Run before merging any iOS fix PR:

- [ ] Push notification prompt appears after sign-in (physical device, release build)
- [ ] PAN field accepts letters on iOS (iPhone 13 or 14)
- [ ] No keyboard overlap on KYC screens (iPhone 14 Pro)
- [ ] Signature pad fully visible on iPhone 14 Pro (Dynamic Island)
- [ ] Document PDF opens without crash
- [ ] Status bar legible on all main screens
- [ ] Universal Links open app instead of Safari
- [ ] No regressions on Android — all changed files verified on Android device
- [ ] No new Xcode warnings or build errors
- [ ] Xcode Console shows no native exceptions during the test flows
