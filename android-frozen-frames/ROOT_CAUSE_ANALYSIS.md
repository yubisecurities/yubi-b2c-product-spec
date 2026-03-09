# Root Cause Analysis — Android Frozen Frames

**Metric:** Excessive Frozen Frames = 22.83% (limit: 4.7%)
**Source:** Google Play Console Vitals, March 2026

---

## What Causes a Frozen Frame?

On Android, a frozen frame occurs when a single frame takes **>700ms** to render. This is almost always caused by the **JS thread being blocked** — either by synchronous operations, cascading re-renders, or heavy computations running at the wrong time.

The issues below compound: they all fire during the same window (app launch + home screen mount), stacking on the JS thread and easily crossing the 700ms threshold.

---

## CRITICAL — App Startup

### Issue 1: App initialization cascade — all blocking native calls on mount

**File:** `src/hooks/mobileApp/useMobileApp.ts` (Lines 27–29)
**Estimated block:** 300–500ms

A single `useEffect` fires `initialLoadOfMobileApp()` on mount, which calls:
- `Hyperkyc.prefetch()` — native module call
- `SplashScreen.hide()` — native UI call
- `initializeRecaptcha()` — network + JS computation
- `GoogleSignin.configure()` — native initialization
- `ZohoSalesIQ.initWithCallback()` — native module + theme setup

All of these compete for the JS thread before the first meaningful frame is painted.

```ts
// useMobileApp.ts — Lines 27-29
useEffect(() => {
  initialLoadOfMobileApp(); // All 5 native calls run here, sequentially
}, []);
```

**Why it causes frozen frames:** Native module calls are bridged via the React Native bridge — they block the JS thread until the bridge call resolves. Running 5 in sequence before the first frame = guaranteed frozen frame on cold start.

---

### Issue 2: Analytics initialization — 5 SDKs in one useEffect

**File:** `src/hooks/useAppLaunchConfig.ts` (Lines 6–37)
**Estimated block:** 200–400ms

WebEngage, Firebase, Amplitude, Facebook, and AppsFlyer are all initialized in a single `useEffect` on app mount, in sequence.

```ts
// useAppLaunchConfig.ts — Lines 6-37
useEffect(() => {
  services.push({ type: 'WebEngage' });
  services.push({ type: 'Firebase' });
  services.push({ type: 'Amplitude', props: { amplitudeApiKey: ... } });
  services.push({ type: 'FB' });
  services.push({ type: 'AppsFlyer', props: { devKey, appId, isDebug } });

  if (services.length > 0) Analytics.getInstance().initialize(services);
}, []);
```

**Why it causes frozen frames:** Each SDK initialization hits native modules (bridge calls). Firebase and AppsFlyer are particularly heavy. Running all 5 synchronously during startup is a major JS thread block.

---

### Issue 3: Remote config — 15+ sequential `.set()` calls triggering render waves

**File:** `src/hooks/useRemoteConfig.ts` (Lines 15–76)
**Estimated block:** 100–200ms (plus cascading re-renders)

After Firebase Remote Config resolves, each config value is parsed and committed to state individually:

```ts
// useRemoteConfig.ts — Lines 15-76
configState.enableBondBasket.set(parseJson(data?.enable_bond_basket?._value) ?? false);
configState.enableRecaptcha.set(parseJson(data?.enable_recaptcha?._value) ?? true);
configState.showReferral.set(parseJson(data?.show_referral?._value) ?? false);
// ... 12 more .set() calls
configState.isRemoteConfigFetched.set(true); // Final trigger — global re-render
```

**Why it causes frozen frames:** Each `.set()` call notifies all Hookstate subscribers synchronously, which triggers re-render cycles. With 15+ calls, the app runs 15+ re-render waves in quick succession — each of which puts load on the JS thread. Components subscribed to `isRemoteConfigFetched` (like the home screen) then re-render in full after all 15 updates.

---

## CRITICAL — Home Screen

### Issue 4: Widget config loop — `WIDGET_COMPONENT_MAP` rebuilt per widget on every mount

**File:** `src/screens/homeRevamp/hooks/useHomePage.ts` (Lines 112–190)
**Estimated block:** 200–400ms

`prepareDashboardHomeConfig()` iterates all widgets and calls `WIDGET_COMPONENT_MAP(themeContextValue, widgets, enableBasket)` **inside the loop body** — so the entire map is reconstructed N times per mount (once per widget).

```ts
// useHomePage.ts — Lines 112-146
const prepareDashboardHomeConfigWithoutData = () => {
  _forEach(widgets, (widget: Widget) => {
    const enableBasket = configState.enableBondBasket.get(); // .get() inside loop
    const widgetMap = WIDGET_COMPONENT_MAP(themeContextValue, widgets, enableBasket); // Rebuilt every iteration
    const widgetComp = widgetMap[widget.config.widget_type];
    dashBoardConfigArray.push({ ...widgetComp, getWidgetProps: ... });
  });
};
```

**Why it causes frozen frames:** `WIDGET_COMPONENT_MAP` is an expensive function that constructs a map of all widget types. Calling it once per widget means if the home screen has 10 widgets, the map is built 10 times. On Android mid-range devices, this alone can take 200–400ms.

---

### Issue 5: Multiple sequential `AsyncStorage` reads on home screen mount

**File:** `src/screens/homeRevamp/hooks/useHomePage.ts` (Lines 262–283)
**Estimated block:** 100–200ms

`updateAppVisitCount()` and `checkShowDisclaimer()` each make 2+ sequential `AsyncStorage.getObject()` calls. Because they are sequentially awaited, each call must fully resolve before the next starts.

```ts
// useHomePage.ts — Lines 262-283
const updateAppVisitCount = async () => {
  const whatsAppConfirmationDone = await LocalAsyncStorage.getObject(WHATSAPP_CONFIRMATION);
  const currentCount = await LocalAsyncStorage.getObject(APP_VISIT_COUNT); // Waits for above
  LocalAsyncStorage.setObject(APP_VISIT_COUNT, currentCount + 1);
};

const checkShowDisclaimer = async () => {
  const value = await LocalAsyncStorage.getObject(SHOW_DISCLAIMER);
  await LocalAsyncStorage.setObject(SHOW_DISCLAIMER, false);
};
```

**Why it causes frozen frames:** AsyncStorage on Android uses a separate thread but the JS thread suspends at each `await` until the read resolves. Sequential awaits on 4 reads = 4 round-trips through the bridge before the home screen can proceed.

---

### Issue 6: `.get()` calls inside `useEffect` dependency arrays

**File:** `src/screens/homeRevamp/hooks/useHomePage.ts` (Lines 320, 384, 415–417)
**Estimated block:** 150–250ms (repeated re-renders across session)

Hookstate `.get()` calls inside dependency arrays cause effects to re-subscribe and re-run on every state tick:

```ts
// useHomePage.ts — Line 320
useEffect(() => {
  checkForHomePageRefresh();
}, [userProfile.userCategory.get()]); // .get() evaluated on every render, creates new subscription

// useHomePage.ts — Lines 415-417
useEffect(() => {
  managePageRefresh();
}, [pusherEvent.get()]); // Re-runs on every Pusher event, even unrelated ones
```

**Why it causes frozen frames:** Each time the component re-renders (which is frequent given Issue 3), the dependency comparison re-evaluates `.get()`, which triggers Hookstate to create a new subscription. This causes cascading re-renders: state changes → re-render → `.get()` re-subscribed → more state changes → another re-render.

---

## MEDIUM — Animations & Auth

### Issue 7: Carousel animation using `useNativeDriver: false`

**File:** `src/screens/homeRevamp/components/webBanner/components/useCarousel.tsx` (Lines 32–37)
**Estimated block:** 100–300ms per animation frame

```ts
// useCarousel.tsx — Lines 32-37
Animated.timing(widthAnim, {
  toValue: progress,
  duration,
  easing: Easing.linear,
  useNativeDriver: false, // Runs on JS thread, not native UI thread
}).start();
```

Combined with a `setInterval` auto-advancing the carousel, this continuously sends animation work to the JS thread.

**Why it causes frozen frames:** With `useNativeDriver: false`, every animation frame (at 60fps = ~16ms per frame) is computed on the JS thread. Any other work happening simultaneously (like a Pusher event or state update) can cause the animation frame to miss its deadline and spike above 700ms.

---

### Issue 8: Auth setup with sequential AsyncStorage reads on startup

**File:** `src/hooks/useAuth.ts` (Lines 195–202)
**Estimated block:** 100–200ms

```ts
// useAuth.ts — Lines 195-202
useEffect(() => {
  const startAuthentication = async () => {
    await addDeviceInfoToHeader();      // Device info fetch
    apiClient.addInterceptor(...);
    getTokenFromMemory();               // AsyncStorage read
  };
  if (!featureFlag?.get()?.isSSOEnabled) startAuthentication();
}, []);
```

**Why it causes frozen frames:** This runs on startup, adding another sequential AsyncStorage read to the already-packed startup window. Overlapping with Issues 1 and 2, this contributes to the cumulative block.

---

## Cumulative Impact

All issues fire during the same window — cold start to home screen fully loaded. The JS thread receives all of this work simultaneously:

```
t=0ms     App launch
t=0ms     useMobileApp.ts: 5 native calls fire             [+300-500ms]
t=0ms     useAppLaunchConfig.ts: 5 analytics SDKs fire      [+200-400ms]
t=0ms     useAuth.ts: AsyncStorage token read               [+100-200ms]
t=~200ms  Home screen mounts
t=~200ms  useHomePage.ts: widget config loop fires          [+200-400ms]
t=~200ms  useHomePage.ts: AsyncStorage reads fire           [+100-200ms]
t=~300ms  useRemoteConfig.ts resolves: 15x .set() fires    [+100-200ms + re-renders]
t=~400ms  Carousel mounts: JS-thread animation starts       [ongoing]

Total cumulative block: ~1,250–2,450ms
Frozen frame threshold: 700ms
```

This means nearly every cold-start session will produce at least one frozen frame, and many will produce multiple.
