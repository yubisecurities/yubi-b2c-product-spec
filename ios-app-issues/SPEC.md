# iOS Behaviour Specification

## What "Correct" Looks Like on iOS

This document defines the expected behaviour standards for each area where issues were found. Use this as the acceptance criteria when reviewing PRs for iOS fixes.

---

## 1. Push Notifications / APNs

### Standard
- APNs environment must be `development` in debug builds and `production` in release/TestFlight/App Store builds
- Users must be explicitly prompted for notification permission on first relevant app open (not necessarily cold start — an appropriate moment like after sign-in)
- After permission granted, the app must register for remote notifications and forward the APNs token to the backend
- On iOS 14+, the app must handle the provisional authorization option

### Acceptance Criteria
- [ ] Debug build connects to APNs sandbox; release build connects to APNs production
- [ ] Users see a "Allow Notifications?" system prompt on iOS at an appropriate moment
- [ ] Firebase `getToken()` returns a valid FCM token on iOS after permission granted
- [ ] Push notifications received and displayed when app is in foreground, background, and killed state
- [ ] Notification tap navigates to the correct in-app screen

### Configuration Requirements
```
Debug scheme   → Entitlements: aps-environment = development
Release scheme → Entitlements: aps-environment = production
```
Use two entitlement files (`Fin.entitlements` for debug, `Fin-Release.entitlements` for release) set per build configuration in Xcode target settings.

---

## 2. Safe Area / Notch Handling

### Standard
- No hardcoded pixel values for navigation offsets, padding, or insets
- All spacing that relates to the device boundary must come from `useSafeAreaInsets()`
- `KeyboardAvoidingView.keyboardVerticalOffset` must be computed dynamically

### Device Inset Reference

| Device | Top inset | Bottom inset |
|--------|-----------|--------------|
| iPhone SE (1st/2nd gen) | 20px | 0px |
| iPhone X / XS / 11 Pro | 44px | 34px |
| iPhone 12 / 13 / 14 | 47px | 34px |
| iPhone 14 Pro (Dynamic Island) | 59px | 34px |
| iPhone 15 Pro Max | 59px | 34px |

### Acceptance Criteria
- [ ] No form inputs obscured by keyboard on any device in the test matrix
- [ ] No content hidden under the notch or Dynamic Island
- [ ] Signature canvas fully visible and interactive on notched iPhones
- [ ] All KYC screens scroll correctly with keyboard open

### Correct Pattern
```tsx
import { useSafeAreaInsets } from 'react-native-safe-area-context';

const MyScreen = () => {
  const insets = useSafeAreaInsets();
  const navigationBarHeight = 44; // Standard RN navigation header
  const keyboardOffset = insets.top + navigationBarHeight;

  return (
    <KeyboardAvoidingView
      behavior="padding"
      keyboardVerticalOffset={Platform.OS === 'ios' ? keyboardOffset : undefined}
    >
      {/* content */}
    </KeyboardAvoidingView>
  );
};
```

---

## 3. Keyboard Types

### Standard
- Input fields must use a keyboard type that allows all valid characters for the field
- PAN: must allow uppercase letters and digits → use `default` keyboard with `autoCapitalize="characters"` and `maxLength={10}`
- DOB: use native `DatePicker` where possible; if text field, use `numeric` keyboard with manual `/` insertion
- Mobile number: `phone-pad`
- Email: `email-address`
- OTP / PIN: `number-pad`
- Search: `default` (not `ascii-capable` — this hides suggested text on newer iOS)

### PAN Acceptance Criteria
- [ ] User can type all 10 PAN characters (5 letters + 4 digits + 1 letter) on iOS
- [ ] Letters auto-capitalised
- [ ] Input capped at 10 characters
- [ ] Correct keyboard shown (default alphanumeric, not numbers-only)

---

## 4. File Download & Preview

### Standard
- `ios.presentPreview()` must always be wrapped in try/catch
- `onSuccess()` callback must only fire after the preview is confirmed open, not before
- `presentOpenInMenu` (share sheet) should be available in both debug and production — users should be able to share documents
- Downloaded files should be cleared from `DocumentDir` after 24 hours or on logout

### Acceptance Criteria
- [ ] Downloading a PDF on iOS opens the preview without crashing
- [ ] If file is missing or corrupt, user sees an error toast (not a crash)
- [ ] Share sheet ("Open in...") available in production builds
- [ ] `DocumentDir` size does not grow unboundedly between app sessions

---

## 5. Status Bar

### Standard
- `UIViewControllerBasedStatusBarAppearance` should be `true` to allow per-screen status bar control
- Every screen should explicitly set status bar style using `<StatusBar barStyle="..."/>`
- Light content (white text) on dark backgrounds; dark content (black text) on light backgrounds

### Acceptance Criteria
- [ ] Status bar text is legible on all screens (no white text on white background)
- [ ] Status bar style updates when navigating between screens with different background colours
- [ ] No visible status bar flicker during navigation transitions

---

## 6. Universal Links

### Standard
- Each domain in `Fin.entitlements` must serve a valid AASA file at `https://{domain}/.well-known/apple-app-site-association`
- AASA file must include the correct `appID` (Team ID + Bundle ID) and the paths to handle

### AASA File Format
```json
{
  "applinks": {
    "apps": [],
    "details": [
      {
        "appID": "TEAMID.com.aspero.app",
        "paths": ["*"]
      }
    ]
  }
}
```

### Acceptance Criteria
- [ ] Tapping an aspero.in link on iOS opens the app directly (not Safari)
- [ ] App navigates to the correct screen based on the URL path
- [ ] Deep links work when app is killed, backgrounded, and foregrounded

---

## 7. Permissions (Info.plist)

### Required Info.plist Keys

| Key | Required For |
|-----|-------------|
| `NSCameraUsageDescription` | KYC liveness, document scan |
| `NSPhotoLibraryUsageDescription` | KYC document upload from library |
| `NSPhotoLibraryAddOnlyUsageDescription` | Saving documents to photo library |
| `NSMicrophoneUsageDescription` | Video KYC (if applicable) |
| `NSFaceIDUsageDescription` | Biometric auth (if used) |
| `NSLocationWhenInUseUsageDescription` | Only if location features exist |

### Acceptance Criteria
- [ ] App Store submission passes privacy permission review
- [ ] Permission prompts show meaningful descriptions (not empty strings)
- [ ] App requests minimum required permissions (not "always" when "when in use" is sufficient)

---

## 8. Target Device Matrix

All P0 and P1 fixes must be verified on these devices:

| Priority | Device | iOS Version | Screen | Why |
|----------|--------|-------------|--------|-----|
| P0 | iPhone SE (3rd gen) | iOS 17 | 4.7" | No notch — tests baseline layout |
| P0 | iPhone 13 | iOS 17 | 6.1" | Standard notch — most common |
| P0 | iPhone 14 Pro | iOS 17 | 6.1" | Dynamic Island — newest form factor |
| P1 | iPhone 15 Pro Max | iOS 17 | 6.7" | Largest screen |
| P1 | iPhone X (or XS) | iOS 16 | 5.8" | First notch generation |
| P2 | iPhone SE (1st gen) | iOS 15 | 4" | Smallest supported screen |
| P2 | iPad (any) | iOS 17 | — | If iPad is supported |

---

## 9. Build Configuration Standards

| Config | APNs | Entitlements | Bundle ID |
|--------|------|-------------|-----------|
| Debug | `development` | `Fin.entitlements` | `com.aspero.app.dev` (or same) |
| Release (TestFlight) | `production` | `Fin-Release.entitlements` | `com.aspero.app` |
| Release (App Store) | `production` | `Fin-Release.entitlements` | `com.aspero.app` |

---

## 10. Success Criteria Summary

A fix is complete when:
- Behaviour matches the standard defined in this spec
- Tested on at least iPhone SE + iPhone 13 + iPhone 14 Pro
- No regressions on Android (cross-platform changes must be verified on Android too)
- No new Xcode warnings or build errors introduced
