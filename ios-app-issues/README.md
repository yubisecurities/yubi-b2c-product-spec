# iOS App Issues — B2C Mobile

## Overview

Comprehensive audit of iOS-specific bugs and misconfigurations in the `yubi-b2c-mobile` React Native app.

**Total issues found: 36**
- 🔴 Critical: 2
- 🟠 High: 8
- 🟡 Medium: 15
- 🔵 Low: 11

**Source repo:** [yubi-b2c-mobile](https://github.com/yubisecurities/yubi-b2c-mobile)
**Audit date:** March 2026

---

## Project Structure

```
ios-app-issues/
├── README.md                  # This file — overview, issue index, quick start
├── ROOT_CAUSE_ANALYSIS.md     # All 36 issues with file paths, line numbers, code snippets
├── SPEC.md                    # iOS-specific behaviour standards and acceptance criteria
├── RECOMMENDED_FIXES.md       # Prioritised fixes with before/after code
└── TEST_SUITE.md              # Device matrix, test cases, regression checklist
```

---

## Issue Index

| # | Issue | File | Severity |
|---|-------|------|----------|
| 1 | APNs environment hardcoded to `development` | `ios/Fin/Fin.entitlements:6` | 🔴 Critical |
| 2 | No iOS notification permission request | `useNotificationPermission.ts` | 🔴 Critical |
| 3 | `useSafeAreaInsets` never used — hardcoded offsets everywhere | Multiple screens | 🟠 High |
| 4 | Wrong keyboard type for PAN input on iOS | `usePanHuf.ts:338` | 🟠 High |
| 5 | `ios.presentPreview()` has no error handling | `DownloadDocument.ts:217` | 🟠 High |
| 6 | Signature pad `absoluteFill` hidden under notch | `SignaturePad.tsx:71` | 🟠 High |
| 7 | `UNUserNotificationCenter` configured but permission never requested | `AppDelegate.mm:39` | 🟠 High |
| 8 | No error boundary for iOS-only file APIs | `DownloadDocument.ts` | 🟠 High |
| 9 | PAN input — users cannot type letters on iOS | `usePanHuf.ts:338` | 🟠 High |
| 10 | DOB field uses wrong keyboard type on iOS | `AddNominee.tsx:96` | 🟡 Medium |
| 11 | Keyboard offsets inconsistent across KYC screens | `Kyc.tsx`, `BankVerify.tsx`, `AddNominee.tsx` | 🟡 Medium |
| 12 | `UIViewControllerBasedStatusBarAppearance = false` | `Info.plist:131` | 🟡 Medium |
| 13 | `StatusBar translucent` — content bleeds under notch | `ThemeAdjustedStatusBar.tsx:19` | 🟡 Medium |
| 14 | `transparentModal` without Android fallback | `privateRoutesList.ts:288` | 🟡 Medium |
| 15 | `NSPhotoLibraryAddOnlyUsageDescription` missing | `Info.plist` | 🟡 Medium |
| 16 | Document downloads accumulate in DocumentDir, no cleanup | `DownloadDocument.ts:57` | 🟡 Medium |
| 17 | Universal Links — AASA files may not be configured | `Fin.entitlements:8-14` | 🟡 Medium |
| 18 | Custom fonts not validated for iOS registration | `FontUtils.ts:25` | 🟡 Medium |
| 19 | Podfile patches `RCT-Folly/Portability.h` directly | `Podfile:248` | 🟡 Medium |
| 20 | Deep link URL decoding insufficient for iOS | `deepLinkHandler.ts:11` | 🟡 Medium |
| 21 | `gestureEnabled: false` set globally — breaks iOS swipe-back | `privateRoutesList.ts` | 🔵 Low |
| 22 | Launch screen image has fixed dimensions | `LaunchScreen.storyboard:20` | 🔵 Low |
| 23 | `bounces={false}` without Android `overScrollMode` equivalent | `KeyboardAvoidingViewWrapper.tsx:25` | 🔵 Low |
| 24 | `lineHeight` not iOS-specific | `lightThemeJson.ts` | 🔵 Low |

---

## Quick Start for Engineers

### Step 1 — Understand root causes
Read [`ROOT_CAUSE_ANALYSIS.md`](ROOT_CAUSE_ANALYSIS.md) — all issues with exact file paths, line numbers, and why each is broken on iOS.

### Step 2 — Understand the standard
Read [`SPEC.md`](SPEC.md) — what correct iOS behaviour looks like, acceptance criteria, and device targets.

### Step 3 — Implement
Read [`RECOMMENDED_FIXES.md`](RECOMMENDED_FIXES.md) — prioritised P0/P1/P2 fixes with before/after code.

### Step 4 — Verify
Follow [`TEST_SUITE.md`](TEST_SUITE.md) — device matrix, test cases per issue, regression checklist.

---

## Implementation Order

### P0 — Fix immediately (production broken)
1. **APNs environment** — production push notifications not working
2. **iOS notification permission** — users never prompted, no push token

### P1 — Fix before next release (user-facing bugs)
3. **PAN keyboard type** — iOS users can't type PAN number
4. **Safe area / keyboard offsets** — replace all hardcoded values with `useSafeAreaInsets()`
5. **File preview error handling** — silent crashes on document open
6. **Signature pad notch** — content hidden under Dynamic Island

### P2 — Fix in upcoming sprint
7. **Status bar config** — per-screen status bar appearance
8. **Font validation** — confirm Sofia Pro registered in Info.plist
9. **DOB keyboard type** — same fix as PAN
10. **Universal Links** — verify AASA files on all 5 domains

---

## Files to Modify in yubi-b2c-mobile

```
ios/Fin/Fin.entitlements                                           ← P0
ios/Fin/Info.plist                                                 ← P0, P2
ios/Fin/AppDelegate.mm                                             ← P0
src/hooks/notificationPermissions/useNotificationPermission.ts     ← P0
src/screens/kycV2/steps/AadhaarPan/.../usePanHuf.ts               ← P1
src/screens/kycV2/Kyc.tsx                                          ← P1
src/screens/kycV2/steps/bank/bankVerify/BankVerify.tsx             ← P1
src/screens/kycV2/steps/dematNominee/.../AddNominee.tsx            ← P1
src/screens/kycV2/steps/wetSignature/SignaturePad.tsx              ← P1
src/manager/downloadDocument/DownloadDocument.ts                   ← P1
src/molecules/themeAdjustedStatusBar/ThemeAdjustedStatusBar.tsx    ← P2
src/navigation/privateRoutesList.ts                                ← P2
src/utils/FontUtils.ts                                             ← P2
```

---

*Created: 2026-03-09*
*Audit scope: Full codebase — iOS-specific paths, entitlements, AppDelegate, hooks, screens, navigation*
*Severity: 2 issues causing silent production failures (push notifications)*
