# Frozen Frames Analysis — B2C Mobile (Android)

**Date:** 2026-03-08
**Context:** Google Play Store vitals showing Excessive Frozen Frames at **22.83%** vs acceptable limit of **4.7%**

---

## Root Cause Summary

The primary cause is **cumulative JS thread blocking during app startup and home screen mount**, totaling an estimated **1.5–2.5 seconds** of blocking operations. Frozen frames on Android are defined as frames taking >700ms to render. The issues below compound on each other, making startup and first meaningful render extremely slow.

---

## CRITICAL — App Startup

### 1. Analytics initialization — 5 services in one `useEffect`
**File:** `src/hooks/useAppLaunchConfig.ts` (Lines 6–37)
**Estimated block:** 200–400ms

WebEngage, Firebase, Amplitude, Facebook, and AppsFlyer are all initialized sequentially inside a single `useEffect` on app mount. Each SDK hits native modules, which blocks the JS thread.

```ts
useEffect(() => {
  services.push({ type: 'WebEngage' });
  services.push({ type: 'Firebase' });
  services.push({ type: 'Amplitude', props: { amplitudeApiKey: ... } });
  services.push({ type: 'FB' });
  services.push({ type: 'AppsFlyer', props: { devKey, appId, isDebug } });

  if (services.length > 0) Analytics.getInstance().initialize(services);
}, []);
```

**Fix:** Defer non-critical services (Amplitude, AppsFlyer) using `InteractionManager.runAfterInteractions()` after TTI.

---

### 2. App initialization cascade — all blocking calls on mount
**File:** `src/hooks/mobileApp/useMobileApp.ts` (Lines 27–29)
**Estimated block:** 300–500ms

A single `useEffect` fires `initialLoadOfMobileApp()` which calls:
- `Hyperkyc.prefetch()` — native module
- `SplashScreen.hide()` — native call
- `initializeRecaptcha()` — network + JS heavy
- `GoogleSignin.configure()` — native initialization
- `ZohoSalesIQ.initWithCallback()` — native module + theme setup

All of these run on the JS thread before the first frame is painted.

**Fix:** Break this into critical (SplashScreen.hide) and deferred (Zoho, Recaptcha) groups. Run deferred tasks after `InteractionManager.runAfterInteractions()`.

---

### 3. Remote config — 15+ sequential `.set()` calls causing 15+ render waves
**File:** `src/hooks/useRemoteConfig.ts` (Lines 15–76)
**Estimated block:** 100–200ms

After fetching Firebase Remote Config, each value is parsed and set individually:

```ts
configState.enableBondBasket.set(parseJson(data?.enable_bond_basket?._value) ?? false);
configState.enableRecaptcha.set(parseJson(data?.enable_recaptcha?._value) ?? true);
// ... 13 more .set() calls
configState.isRemoteConfigFetched.set(true); // Triggers global re-render
```

Each `.set()` call notifies all subscribers and triggers a re-render wave. With 15+ calls, this creates 15+ cascading render cycles.

**Fix:** Parse all values first into a plain object, then do a single bulk state update.

---

## CRITICAL — Home Screen

### 4. Widget configuration loop — `WIDGET_COMPONENT_MAP` called per widget on every mount
**File:** `src/screens/homeRevamp/hooks/useHomePage.ts` (Lines 112–190)
**Estimated block:** 200–400ms

`prepareDashboardHomeConfig()` iterates through all widgets and calls `WIDGET_COMPONENT_MAP(themeContextValue, widgets, enableBasket)` **inside the loop** on every iteration. This map is expensive to construct and is re-built N times per mount (once per widget).

```ts
_forEach(widgets, (widget: Widget) => {
  const enableBasket = configState.enableBondBasket.get();
  const widgetMap = WIDGET_COMPONENT_MAP(themeContextValue, widgets, enableBasket); // Expensive — called per widget
  const widgetComp = widgetMap[widget.config.widget_type];
  dashBoardConfigArray.push({ ...widgetComp, getWidgetProps: ... });
});
```

**Fix:** Call `WIDGET_COMPONENT_MAP(...)` once before the loop and reuse the result. Memoize with `useMemo`.

---

### 5. Multiple sequential `AsyncStorage` reads on home screen mount
**File:** `src/screens/homeRevamp/hooks/useHomePage.ts` (Lines 262–283)
**Estimated block:** 100–200ms

`updateAppVisitCount()` and `checkShowDisclaimer()` make 3–4 sequential `AsyncStorage.getObject()` calls each. AsyncStorage is async but still competes for the JS thread, and sequential awaits mean each call must complete before the next starts.

```ts
// updateAppVisitCount
const whatsAppConfirmationDone = await LocalAsyncStorage.getObject(...);
const currentCount = await LocalAsyncStorage.getObject(...);
LocalAsyncStorage.setObject(...);

// checkShowDisclaimer
const value = await LocalAsyncStorage.getObject(...);
await LocalAsyncStorage.setObject(...);
```

**Fix:** Parallelize reads using `Promise.all([...])` where values are independent.

---

### 6. `.get()` calls inside `useEffect` dependency arrays — cascading re-subscriptions
**File:** `src/screens/homeRevamp/hooks/useHomePage.ts` (Lines 320, 384, 415–417)
**Estimated block:** 150–250ms (repeated re-renders)

Hookstate `.get()` calls inside dependency arrays cause effects to re-run on every state change tick:

```ts
useEffect(() => {
  managePageRefresh();
}, [pusherEvent.get()]); // .get() evaluated on every render

useEffect(() => {
  // ...
}, [userProfile.userCategory.get()]); // Re-runs on every category change
```

**Fix:** Extract `.get()` values into variables above the effect, or use `useHookstate` selectors to subscribe only to specific fields.

---

## MEDIUM — Animations & Auth

### 7. Carousel animation using `useNativeDriver: false`
**File:** `src/screens/homeRevamp/components/webBanner/components/useCarousel.tsx` (Lines 32–37)
**Estimated block:** 100–300ms per animation frame

```ts
Animated.timing(widthAnim, {
  toValue: progress,
  duration,
  easing: Easing.linear,
  useNativeDriver: false, // Forces animation onto JS thread
}).start();
```

With `useNativeDriver: false`, every animation frame is calculated on the JS thread. Combined with a `setInterval` auto-advance, this continuously interrupts other JS work.

**Fix:** Switch to `useNativeDriver: true` (requires using transforms/opacity instead of width). Consider using `react-native-reanimated` for layout animations.

---

### 8. Auth setup with sequential `AsyncStorage` reads on startup
**File:** `src/hooks/useAuth.ts` (Lines 195–202)
**Estimated block:** 100–200ms

Authentication setup on mount awaits `AsyncStorage` reads sequentially before proceeding:

```ts
useEffect(() => {
  const startAuthentication = async () => {
    await addDeviceInfoToHeader();
    apiClient.addInterceptor(...);
    getTokenFromMemory(); // Blocking AsyncStorage read
  };
  if (!featureFlag?.get()?.isSSOEnabled) startAuthentication();
}, []);
```

**Fix:** Read token from a faster in-memory cache (e.g., MMKV or a module-level variable after first load). Avoid awaiting AsyncStorage in startup paths.

---

## Summary Table

| # | Issue | File | Lines | Estimated JS Block |
|---|-------|------|-------|--------------------|
| 1 | Analytics init (5 services) | `useAppLaunchConfig.ts` | 6–37 | 200–400ms |
| 2 | App init cascade | `useMobileApp.ts` | 27–29 | 300–500ms |
| 3 | Remote config 15x `.set()` | `useRemoteConfig.ts` | 15–76 | 100–200ms |
| 4 | Widget config loop (per-widget map rebuild) | `useHomePage.ts` | 112–190 | 200–400ms |
| 5 | Sequential AsyncStorage on home mount | `useHomePage.ts` | 262–283 | 100–200ms |
| 6 | `.get()` in useEffect deps | `useHomePage.ts` | 320, 384, 415 | 150–250ms |
| 7 | JS-thread carousel animation | `useCarousel.tsx` | 32–37 | 100–300ms/frame |
| 8 | Auth AsyncStorage on startup | `useAuth.ts` | 195–202 | 100–200ms |
| | **Total potential block** | | | **~1,250–2,450ms** |

---

## Recommended Fix Priority

### P0 — Biggest wins, lowest risk
1. **Defer non-critical startup services** (`useMobileApp.ts`, `useAppLaunchConfig.ts`)
   Wrap Amplitude, AppsFlyer, ZohoSalesIQ, Recaptcha, GoogleSignin in `InteractionManager.runAfterInteractions()`. Only `SplashScreen.hide()` needs to run immediately.

2. **Memoize `WIDGET_COMPONENT_MAP`** (`useHomePage.ts:112-190`)
   Move the map construction outside the `_forEach` loop. Wrap in `useMemo` with widget/theme/config as dependencies.

3. **Batch remote config state updates** (`useRemoteConfig.ts`)
   Parse all remote config values into a plain JS object first, then apply in a single state update instead of 15 individual `.set()` calls.

### P1 — High impact, moderate effort
4. **Parallelize AsyncStorage reads** (`useHomePage.ts:262-283`, `useAuth.ts`)
   Replace sequential `await getObject()` chains with `Promise.all([...])`.

5. **Fix `useEffect` dependency arrays** (`useHomePage.ts:320,384,415`)
   Extract `.get()` calls into variables before the effect. Use Hookstate's scoped subscriptions.

### P2 — Medium impact
6. **Switch carousel to `useNativeDriver: true`** (`useCarousel.tsx`)
   Refactor animation to use `transform` properties, or migrate to `react-native-reanimated`.

---

## Tools for Verification

- **Android Studio Profiler** — CPU trace to confirm JS thread blocking during startup
- **Flipper + React DevTools** — Component render count and flamegraph
- **React Native Performance Monitor** — `perf monitor` in dev menu to watch FPS live
- **Firebase Performance SDK** — Add custom traces around startup phases to measure in production
