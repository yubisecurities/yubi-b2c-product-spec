# Recommended Fixes — iOS App Issues

Fixes are ordered by priority. P0 fixes address production failures and should be deployed immediately.

---

## P0 — Fix 1: Split APNs entitlements by build configuration

**File:** `ios/Fin/Fin.entitlements` + Xcode project settings
**Issue:** APNs hardcoded to `development` — production push notifications broken

### Step 1: Create a release entitlements file

Duplicate `ios/Fin/Fin.entitlements` → `ios/Fin/Fin-Release.entitlements`

Change the APNs environment in the release file:
```xml
<!-- ios/Fin/Fin-Release.entitlements -->
<key>aps-environment</key>
<string>production</string>  <!-- was: development -->
```

Keep `ios/Fin/Fin.entitlements` as-is (development) for debug builds.

### Step 2: Assign entitlements per build configuration in Xcode

1. Open `ios/Fin.xcworkspace` in Xcode
2. Select the **Fin** target → **Build Settings** tab
3. Search for "Code Signing Entitlements"
4. Set:
   - **Debug**: `Fin/Fin.entitlements`
   - **Release**: `Fin/Fin-Release.entitlements`

### Step 3: Add the release entitlements to source control
```bash
git add ios/Fin/Fin-Release.entitlements
```

---

## P0 — Fix 2: Add iOS notification permission request

**File:** `src/hooks/notificationPermissions/useNotificationPermission.ts`
**Issue:** iOS users never prompted for push permission

```ts
// BEFORE — only handles Android
const checkNotificationPermissionForAndroid = () => {
  if (isPostAndroidAPI32) {
    requestNotifications(['alert', 'sound']).then(...);
  }
};

// AFTER — handles both platforms
import messaging from '@react-native-firebase/messaging';

const requestNotificationPermission = async () => {
  if (isIOS()) {
    const authStatus = await messaging().requestPermission();
    const enabled =
      authStatus === messaging.AuthorizationStatus.AUTHORIZED ||
      authStatus === messaging.AuthorizationStatus.PROVISIONAL;

    if (enabled) {
      const token = await messaging().getToken();
      // Send token to backend
      updateDevicePushToken(token);
    }
  } else if (isPostAndroidAPI32) {
    requestNotifications(['alert', 'sound']).then((result) => {
      if (result.status === 'granted') {
        messaging().getToken().then(updateDevicePushToken);
      }
    });
  }
};

// Call this at the right moment — after sign-in, not on cold start
export const useNotificationPermission = () => {
  const requestPermission = useCallback(() => {
    requestNotificationPermission();
  }, []);

  return { requestPermission };
};
```

Also ensure AppDelegate.mm explicitly requests authorization (belt-and-suspenders):

```objc
// ios/Fin/AppDelegate.mm — add inside application:didFinishLaunchingWithOptions:
UNUserNotificationCenter *center = [UNUserNotificationCenter currentNotificationCenter];
center.delegate = self;
// Add this:
[center requestAuthorizationWithOptions:(UNAuthorizationOptionAlert | UNAuthorizationOptionSound | UNAuthorizationOptionBadge)
                      completionHandler:^(BOOL granted, NSError * _Nullable error) {
  if (granted) {
    dispatch_async(dispatch_get_main_queue(), ^{
      [[UIApplication sharedApplication] registerForRemoteNotifications];
    });
  }
}];
```

---

## P1 — Fix 3: Replace hardcoded keyboard offsets with `useSafeAreaInsets`

**Files:** `Kyc.tsx`, `BankVerify.tsx`, `AddNominee.tsx`, and all other KYC screens
**Issue:** Keyboard overlaps input fields on modern iPhones

### Create a shared hook

```ts
// src/hooks/useKeyboardOffset.ts (new file)
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { Platform } from 'react-native';

const NAVIGATION_HEADER_HEIGHT = 44;

export const useKeyboardOffset = () => {
  const insets = useSafeAreaInsets();
  if (Platform.OS !== 'ios') return undefined;
  return insets.top + NAVIGATION_HEADER_HEIGHT;
};
```

### Update each KYC screen

```tsx
// BEFORE — Kyc.tsx Line 33
<KeyboardAvoidingView
  keyboardVerticalOffset={isIOS() ? 64 : undefined}
  behavior={'padding'}
>

// AFTER
import { useKeyboardOffset } from 'src/hooks/useKeyboardOffset';

const Kyc = () => {
  const keyboardOffset = useKeyboardOffset();

  return (
    <KeyboardAvoidingView
      keyboardVerticalOffset={keyboardOffset}
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
    >
```

Apply the same change to `BankVerify.tsx` (line 42) and `AddNominee.tsx` (line 107).

---

## P1 — Fix 4: Fix PAN keyboard type to allow alphanumeric input

**File:** `src/screens/kycV2/steps/AadhaarPan/components/panHufScreen/hooks/usePanHuf.ts` (Line 338)
**Issue:** iOS users cannot type letters in PAN field

```ts
// BEFORE
keyboardType: isIOS() ? 'numbers-and-punctuation' : ('number-pad' as KeyboadTypes)

// AFTER
keyboardType: 'default',          // Shows full keyboard on both platforms
autoCapitalize: 'characters',     // Forces uppercase (PAN is always uppercase)
autoCorrect: false,               // Disable autocorrect for PAN
maxLength: 10,                    // PAN is exactly 10 chars
```

The input validation (regex for valid PAN format) should happen on blur or submit, not on keyboard type.

---

## P1 — Fix 5: Add error handling to `ios.presentPreview()`

**File:** `src/manager/downloadDocument/DownloadDocument.ts` (Lines 91–96, 217–218)
**Issue:** Silent crash when file preview fails

```ts
// BEFORE
if (isIOS()) {
  if (__DEV__) {
    ios.presentOpenInMenu(filePath);
  } else {
    ios.presentPreview(filePath); // No try/catch
  }
}
onSuccess(); // Called before preview opens

// AFTER
if (isIOS()) {
  try {
    // Use presentOpenInMenu in all builds so users can share documents
    await ios.presentOpenInMenu(filePath);
    onSuccess();
  } catch (error) {
    console.error('iOS file preview failed:', error);
    onFailure?.('Could not open document. Please try again.');
  }
} else {
  // Android path
}

// Second occurrence at line 217-218:
if (isIOS()) {
  try {
    ios.presentPreview(path);
    onSuccess();
  } catch (error) {
    onFailure?.('Unable to preview this document.');
  }
}
```

---

## P1 — Fix 6: Fix signature pad notch overlap

**File:** `src/screens/kycV2/steps/wetSignature/SignaturePad.tsx` (Line 71)
**Issue:** Canvas extends under the notch on iPhones

```tsx
// BEFORE
<View style={StyleSheet.absoluteFill}>
  <SignatureCanvas ... />
</View>

// AFTER
import { useSafeAreaInsets } from 'react-native-safe-area-context';

const SignaturePad = () => {
  const insets = useSafeAreaInsets();

  return (
    <View style={[
      StyleSheet.absoluteFill,
      {
        top: insets.top,
        bottom: insets.bottom,
      }
    ]}>
      <SignatureCanvas ... />
    </View>
  );
};
```

---

## P2 — Fix 7: Fix status bar configuration

**File:** `ios/Fin/Info.plist` (Lines 131–132)

```xml
<!-- BEFORE -->
<key>UIViewControllerBasedStatusBarAppearance</key>
<false/>

<!-- AFTER -->
<key>UIViewControllerBasedStatusBarAppearance</key>
<true/>
```

Then ensure every screen (or the root navigator) renders a `StatusBar` component with the correct `barStyle`:

```tsx
// In each screen or in the navigation container
<StatusBar
  barStyle={isDarkBackground ? 'light-content' : 'dark-content'}
  translucent={false}
/>
```

---

## P2 — Fix 8: Fix DOB keyboard type

**File:** `src/screens/kycV2/steps/dematNominee/components/addNominee/AddNominee.tsx` (Line 96)

```ts
// BEFORE
const dobKeyboardType = isIOS() ? ('numbers-and-punctuation' as any) : ('number-pad' as any);

// AFTER — use a native date picker if available, else numeric keyboard
// Option A: Native date picker (best UX)
import DateTimePicker from '@react-native-community/datetimepicker';
// Replace text input with DateTimePicker on both platforms

// Option B: If a text input is required
const dobKeyboardType = 'numeric'; // Same on both platforms; add masking library for DD/MM/YYYY
```

---

## P2 — Fix 9: Add `NSPhotoLibraryAddOnlyUsageDescription` to Info.plist

**File:** `ios/Fin/Info.plist`

```xml
<!-- Add after NSPhotoLibraryUsageDescription -->
<key>NSPhotoLibraryAddOnlyUsageDescription</key>
<string>Aspero needs access to save documents to your photo library.</string>
```

---

## P2 — Fix 10: Verify Universal Links AASA files

For each domain in `Fin.entitlements`, verify the AASA file exists and is valid:

```bash
# Check each domain
curl -s https://www.aspero.in/.well-known/apple-app-site-association | python3 -m json.tool
curl -s https://aspero.app.link/.well-known/apple-app-site-association | python3 -m json.tool
```

Each should return valid JSON with your Team ID and Bundle ID:
```json
{
  "applinks": {
    "apps": [],
    "details": [{
      "appID": "YOUR_TEAM_ID.com.aspero.app",
      "paths": ["*"]
    }]
  }
}
```

If any return 404 or invalid JSON, the backend team needs to host the AASA file on that domain.

---

## P2 — Fix 11: Add document cleanup on logout

**File:** `src/manager/downloadDocument/DownloadDocument.ts`

```ts
import RNFS from 'react-native-fs';

// Call this on logout
export const clearDownloadedDocuments = async () => {
  if (Platform.OS !== 'ios') return;
  try {
    const files = await RNFS.readDir(RNFS.DocumentDirectoryPath);
    const toDelete = files.filter(f => {
      const ageMs = Date.now() - new Date(f.mtime).getTime();
      return ageMs > 24 * 60 * 60 * 1000; // Older than 24 hours
    });
    await Promise.all(toDelete.map(f => RNFS.unlink(f.path)));
  } catch (e) {
    // Non-critical — log but don't surface to user
    console.warn('Document cleanup failed:', e);
  }
};
```
