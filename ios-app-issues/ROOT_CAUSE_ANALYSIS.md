# Root Cause Analysis — iOS App Issues

**Audit date:** March 2026
**Codebase:** yubi-b2c-mobile (React Native)

---

## CRITICAL

### Issue 1: APNs environment hardcoded to `development`

**File:** `ios/Fin/Fin.entitlements` (Line 6)
**Severity:** 🔴 Critical

```xml
<key>aps-environment</key>
<string>development</string>
```

**What's wrong:** The Apple Push Notification service (APNs) has two separate environments — `development` (for debug/simulator builds) and `production` (for App Store and TestFlight). The entitlements file is hardcoded to `development`.

**Impact:** Every push notification sent from the production backend is routed to the APNs production environment. The app signed with `development` entitlements cannot receive these. Result: **all push notifications are silently dropped in production**. This includes order updates, KYC status, investment confirmations.

**Why it happens:** The entitlements file is committed as a single file and not conditionally set per build scheme.

---

### Issue 2: No iOS notification permission request

**File:** `src/hooks/notificationPermissions/useNotificationPermission.ts`
**Severity:** 🔴 Critical

```ts
// The entire function only handles Android
const checkNotificationPermissionForAndroid = () => {
  if (isPostAndroidAPI32) {
    requestNotifications(['alert', 'sound']).then((value) => {
      // ...
    });
  }
};
```

**What's wrong:** iOS requires an explicit user permission prompt before it will deliver any push notifications or issue an APNs device token. This prompt must be triggered via `requestUserPermission()` from `@react-native-firebase/messaging` (or equivalent). No such call exists anywhere in the codebase.

**Impact:** iOS users are never asked for notification permission. The app never registers for APNs. Even if Issue 1 (entitlements) is fixed, the app still won't receive push notifications on iOS because there is no device token.

---

## HIGH

### Issue 3: `useSafeAreaInsets` never used — hardcoded keyboard offsets

**Files:**
- `src/screens/kycV2/Kyc.tsx` (Line 33)
- `src/screens/kycV2/steps/bank/bankVerify/BankVerify.tsx` (Line 42)
- `src/screens/kycV2/steps/dematNominee/components/addNominee/AddNominee.tsx` (Line 107)
- `src/molecules/keyboardAvoidingViewWrapper/KeyboardAvoidingViewWrapper.tsx` (Line 24)

**Severity:** 🟠 High

```tsx
// Kyc.tsx — Line 33
<KeyboardAvoidingView
  keyboardVerticalOffset={isIOS() ? 64 : undefined}
  behavior={'padding'}
/>

// BankVerify.tsx — Line 42
keyboardVerticalOffset={isIOS() ? 24 : undefined}

// AddNominee.tsx — Line 107
keyboardVerticalOffset={isIOS() ? 24 : undefined}
```

**What's wrong:** The `keyboardVerticalOffset` should equal the height of any UI above the `KeyboardAvoidingView` — typically the navigation header + status bar + notch inset. This value is different for every device:
- iPhone SE (1st gen): ~44px
- iPhone 13: ~47px (navigation bar) + 44px (status bar) = ~91px
- iPhone 14 Pro (Dynamic Island): ~59px

Hardcoded values of 24 and 64 are wrong for most modern iPhones. The keyboard overlaps input fields on taller devices and over-compensates on shorter ones.

**Why `useSafeAreaInsets` is never used:** A global search finds zero usages of `useSafeAreaInsets` in the codebase. The package `react-native-safe-area-context` is installed (it ships with React Navigation) but the hook is never imported or called.

---

### Issue 4 & 9: Wrong keyboard type for PAN input — users cannot type letters

**File:** `src/screens/kycV2/steps/AadhaarPan/components/panHufScreen/hooks/usePanHuf.ts` (Line 338)
**Severity:** 🟠 High

```ts
keyboardType: isIOS() ? 'numbers-and-punctuation' : ('number-pad' as KeyboadTypes)
```

**What's wrong:** A valid Indian PAN is exactly 10 characters: 5 letters + 4 digits + 1 letter (e.g. `ABCDE1234F`). The `numbers-and-punctuation` keyboard type on iOS shows only numbers and symbols. **There is no way to type letters.** This makes PAN entry completely broken on iOS.

**Impact:** Any iOS user reaching the PAN entry step in KYC is blocked. They cannot complete KYC. This is a full conversion blocker for iOS users.

---

### Issue 5 & 8: `ios.presentPreview()` has no error handling

**File:** `src/manager/downloadDocument/DownloadDocument.ts` (Lines 91–96, 217–218)
**Severity:** 🟠 High

```ts
// Line 91-96
if (isIOS()) {
  if (__DEV__) {
    ios.presentOpenInMenu(filePath);
  } else {
    ios.presentPreview(filePath); // No try/catch
  }
}

// Line 217-218
if (isIOS()) {
  ios.presentPreview(path); // No try/catch, onSuccess() already called above
}
```

**What's wrong:**
1. `ios.presentPreview()` is a native call that throws if the file path doesn't exist, is corrupted, or the file type is unsupported. There is no try/catch.
2. `onSuccess()` is called *before* `presentPreview()`. If the preview fails, the user sees a success toast but no document.
3. In production (`!__DEV__`), `presentOpenInMenu` is never used — users cannot share or open documents in other apps.

**Impact:** When document download succeeds but preview fails (e.g. network wrote partial file), the app crashes silently with an unhandled native exception.

---

### Issue 6: Signature pad extends under notch via `absoluteFill`

**File:** `src/screens/kycV2/steps/wetSignature/SignaturePad.tsx` (Line 71)
**Severity:** 🟠 High

```tsx
<View style={StyleSheet.absoluteFill}>
  <SignatureCanvas ... />
</View>
```

**What's wrong:** `StyleSheet.absoluteFill` is `{position: 'absolute', top: 0, left: 0, right: 0, bottom: 0}`. On iPhones with a notch or Dynamic Island, `top: 0` puts the canvas behind the notch. The top portion of the signature canvas is physically unreachable — users cannot draw in that area, and the canvas origin is offset from where the finger touches.

**Impact:** Wet signature step in KYC is broken on notched iPhones. The drawn signature may not match the rendered output, causing KYC failure.

---

### Issue 7: `UNUserNotificationCenter` delegate set but permission never requested

**File:** `ios/Fin/AppDelegate.mm` (Lines 39–74)
**Severity:** 🟠 High

```objc
UNUserNotificationCenter *center = [UNUserNotificationCenter currentNotificationCenter];
center.delegate = self;
// requestAuthorizationWithOptions is never called
```

**What's wrong:** Setting the delegate allows the app to *handle* notifications, but on iOS 10+ the app must also call `requestAuthorizationWithOptions:completionHandler:` to *receive* them. Without this call, the system never grants the app permission and no APNs token is issued.

This is separate from Issue 2 (the JS-side permission). Both the native (AppDelegate) and JS (Firebase messaging) permission requests serve different purposes and both need to exist.

---

## MEDIUM

### Issue 10: DOB field uses `numbers-and-punctuation` on iOS

**File:** `src/screens/kycV2/steps/dematNominee/components/addNominee/AddNominee.tsx` (Line 96)
**Severity:** 🟡 Medium

```ts
const dobKeyboardType = isIOS() ? ('numbers-and-punctuation' as any) : ('number-pad' as any);
```

Date of birth in DD/MM/YYYY format needs `/` separators. `numbers-and-punctuation` technically allows this, but the keyboard layout is unfamiliar for date entry. iOS provides `decimal-pad` or the `UIDatePicker` native component which gives a much better UX.

---

### Issue 11: Inconsistent keyboard offsets across KYC screens

Already detailed in Issue 3. Specific values:
- `Kyc.tsx`: 64
- `BankVerify.tsx`: 24
- `AddNominee.tsx`: 24

No rationale for the discrepancy. All should use a shared hook.

---

### Issue 12: `UIViewControllerBasedStatusBarAppearance = false` blocks per-screen customization

**File:** `ios/Fin/Info.plist` (Lines 131–132)
**Severity:** 🟡 Medium

```xml
<key>UIViewControllerBasedStatusBarAppearance</key>
<false/>
```

**What's wrong:** This setting locks status bar appearance to a single global value controlled by the `StatusBar` React Native component. Screens with dark backgrounds need `light-content`, screens with light backgrounds need `dark-content`. With this set to `false`, React Native's `StatusBar` component is the *only* way to change it — which requires the `StatusBar` component to be rendered on every screen with the right `barStyle`. Any screen missing it will show the wrong colour.

---

### Issue 13: `StatusBar translucent` — content bleeds under notch area

**File:** `src/molecules/themeAdjustedStatusBar/ThemeAdjustedStatusBar.tsx` (Line 19)
**Severity:** 🟡 Medium

```tsx
return <StatusBar translucent backgroundColor='transparent' barStyle={barStyle} />;
```

**What's wrong:** `translucent={true}` on iOS means content renders under the status bar (clock/battery area). This is intentional for full-bleed backgrounds, but requires every screen to add `SafeAreaView` or top padding equal to `safeAreaInsets.top`. Screens that don't do this will have their headers clipped under the notch.

---

### Issue 14: `transparentModal` presentation without platform-specific handling

**File:** `src/navigation/privateRoutesList.ts` (Line 288)
**Severity:** 🟡 Medium

```ts
options: { presentation: 'transparentModal' }
```

`transparentModal` maps to `UIModalPresentationOverFullScreen` on iOS. On Android it behaves differently — the previous screen may flash or the background transparency may not work correctly. No `Platform.select` guard exists.

---

### Issue 15: `NSPhotoLibraryAddOnlyUsageDescription` missing from Info.plist

**File:** `ios/Fin/Info.plist`
**Severity:** 🟡 Medium

`NSPhotoLibraryUsageDescription` is present but `NSPhotoLibraryAddOnlyUsageDescription` is absent. Since iOS 11, apps that only save photos (not read them) must use the "add only" key. App Store review may reject builds that request full library access when only save access is needed.

---

### Issue 16: Document downloads accumulate in `DocumentDir` with no cleanup

**File:** `src/manager/downloadDocument/DownloadDocument.ts` (Line 57)
**Severity:** 🟡 Medium

```ts
const aPath = Platform.select({ ios: DocumentDir, android: DownloadDir });
```

Every downloaded PDF/XLSX goes to the iOS Documents directory. This directory is user-visible in the Files app. No cleanup or TTL mechanism exists. Over time, especially for users who download statements frequently, this grows the app's footprint significantly and may cause user confusion in Files.

---

### Issue 17: Universal Links — AASA files not verified

**File:** `ios/Fin/Fin.entitlements` (Lines 8–14)
**Severity:** 🟡 Medium

```xml
<string>applinks:www.aspero.in</string>
<string>applinks:aspero.app.link</string>
<string>applinks:aspero.onelink.me</string>
<string>applinks:invest-qa.aspero.co.in</string>
<string>applinks:invest-uat.aspero.co.in</string>
```

Five domains are declared as Universal Link hosts. For iOS to route links into the app instead of Safari, each domain must serve an `apple-app-site-association` (AASA) JSON file at `/.well-known/apple-app-site-association` with the correct team ID and bundle ID. If any of these files are missing, malformed, or not served with `Content-Type: application/json`, Universal Links silently fall back to Safari.

---

### Issue 18: Custom fonts not validated for iOS registration

**File:** `src/utils/FontUtils.ts` (Lines 25–28)
**Severity:** 🟡 Medium

```ts
export const getFontWeightStyle = (fontWeightString: string) => {
  if (isAndroid()) {
    return undefined; // Android uses filename-based font weights
  }
  return fontWeightMap[fontWeightString]; // iOS uses PostScript name + weight
};
```

On iOS, custom fonts must be:
1. Bundled in the `ios/` directory
2. Listed under `UIAppFonts` in `Info.plist` using the exact PostScript name

If `Sofia Pro` (or any other custom font) is not registered exactly as iOS expects, the `fontFamily` style silently falls back to the system font. The app would then render with San Francisco / Helvetica instead of the design system font — making the entire app look visually incorrect without any error.

---

### Issue 19: Podfile patches `RCT-Folly/Portability.h` directly

**File:** `ios/Podfile` (Lines 248–252)
**Severity:** 🟡 Medium

```ruby
Dir.glob("Pods/RCT-Folly/folly/Portability.h").each do |file|
  text = File.read(file)
  new_contents = text.gsub('#define FOLLY_HAS_COROUTINES 1', '#define FOLLY_HAS_COROUTINES 0')
  File.open(file, "w") { |file| file.puts new_contents }
end
```

This `post_install` hook mutates a file inside `Pods/` to disable C++ coroutines in `folly`. It's a known workaround for a build issue but is fragile:
- If RCT-Folly changes the exact string in a future RN upgrade, the gsub silently does nothing and the build breaks with a cryptic compiler error
- `pod install` must be re-run after any dependency change to reapply the patch
- Not compatible with caching in CI/CD unless the patch is applied before caching

---

### Issue 20: Deep link URL decoding may be insufficient for iOS

**File:** `src/utils/deepLinkHandler.ts` (Line 11)
**Severity:** 🟡 Medium

```ts
const parsedURL = parse(decodeURIComponent(url), true);
```

iOS Universal Links and push notification payloads can double-encode URLs. A single `decodeURIComponent` handles one encoding layer. If the URL was encoded twice (common with AppsFlyer and Branch deep links), parameters arrive as encoded strings instead of decoded values, breaking routing logic.

---

## LOW

### Issue 21: `gestureEnabled: false` set globally without iOS exception

**File:** `src/navigation/privateRoutesList.ts` (multiple lines)
iOS swipe-back (right-to-left pan gesture) is a core navigation pattern. Disabling it globally on screens where it's not needed (e.g. informational screens) breaks the expected iOS UX.

### Issue 22: Launch screen image has fixed dimensions

**File:** `ios/Fin/LaunchScreen.storyboard` (Lines 20–26)
Hard-coded `width: 177, height: 56` constraints. Appears too small on Pro Max, too large on SE.

### Issue 23: `bounces={false}` set without Android `overScrollMode` equivalent

**File:** `src/molecules/keyboardAvoidingViewWrapper/KeyboardAvoidingViewWrapper.tsx` (Line 25)
iOS-only prop used without the Android counterpart `overScrollMode="never"`.

### Issue 24: `lineHeight` not iOS-specific

**File:** `src/theme/lightThemeJson.ts`
iOS and Android render `lineHeight` differently with custom fonts. No platform-specific overrides exist. Text spacing may look off on iOS.
