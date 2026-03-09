# Recommended Fixes — Android Frozen Frames

Fixes are ordered by priority. P0 fixes alone should bring frozen frames below the 4.7% threshold on most devices.

---

## P0 — Fix 1: Defer non-critical startup services

**File:** `src/hooks/mobileApp/useMobileApp.ts`
**Impact:** 300–500ms reduction in startup JS block

Only `SplashScreen.hide()` needs to run immediately. Everything else should run after the app is interactive.

```ts
// BEFORE
useEffect(() => {
  initialLoadOfMobileApp(); // All 5 native calls fire immediately
}, []);

// AFTER
useEffect(() => {
  // Only critical init runs immediately
  SplashScreen.hide();

  // Everything else deferred until after first meaningful render
  InteractionManager.runAfterInteractions(() => {
    Hyperkyc?.prefetch({ ... });
    initializeRecaptcha();
    GoogleSignin.configure({ ... });
    useZohoSalesIQ.initZohoChat();
  });
}, []);
```

**Same pattern for `useAppLaunchConfig.ts`:**

```ts
// BEFORE
useEffect(() => {
  const services = [];
  services.push({ type: 'WebEngage' });
  services.push({ type: 'Firebase' });
  services.push({ type: 'Amplitude', props: { ... } });
  services.push({ type: 'FB' });
  services.push({ type: 'AppsFlyer', props: { ... } });
  Analytics.getInstance().initialize(services);
}, []);

// AFTER
useEffect(() => {
  // Firebase first — needed for remote config (which gate-keeps home screen)
  Analytics.getInstance().initialize([{ type: 'Firebase' }]);

  // All attribution/marketing SDKs deferred
  InteractionManager.runAfterInteractions(() => {
    const deferredServices = [
      { type: 'WebEngage' },
      { type: 'Amplitude', props: { ... } },
      { type: 'FB' },
      { type: 'AppsFlyer', props: { ... } },
    ];
    Analytics.getInstance().initialize(deferredServices);
  });
}, []);
```

---

## P0 — Fix 2: Memoize `WIDGET_COMPONENT_MAP` — call once, not per widget

**File:** `src/screens/homeRevamp/hooks/useHomePage.ts` (Lines 112–190)
**Impact:** 200–400ms reduction in home screen mount time

```ts
// BEFORE — widgetMap rebuilt for every widget in the loop
const prepareDashboardHomeConfigWithoutData = () => {
  _forEach(widgets, (widget: Widget) => {
    const enableBasket = configState.enableBondBasket.get(); // .get() inside loop
    const widgetMap = WIDGET_COMPONENT_MAP(themeContextValue, widgets, enableBasket); // Rebuilt N times
    const widgetComp = widgetMap[widget.config.widget_type];
    dashBoardConfigArray.push({ ...widgetComp, getWidgetProps: ... });
  });
};

// AFTER — widgetMap built once outside the loop, memoized
const enableBasket = configState.enableBondBasket.get();

const widgetMap = useMemo(
  () => WIDGET_COMPONENT_MAP(themeContextValue, widgets, enableBasket),
  [themeContextValue, widgets, enableBasket]
);

const prepareDashboardHomeConfigWithoutData = () => {
  _forEach(widgets, (widget: Widget) => {
    const widgetComp = widgetMap[widget.config.widget_type]; // O(1) lookup, no rebuild
    dashBoardConfigArray.push({ ...widgetComp, getWidgetProps: ... });
  });
};
```

---

## P0 — Fix 3: Batch remote config state updates

**File:** `src/hooks/useRemoteConfig.ts` (Lines 15–76)
**Impact:** Eliminates 14 unnecessary render waves; reduces re-render cascade

```ts
// BEFORE — 15 individual .set() calls, each triggering a render wave
configState.enableBondBasket.set(parseJson(data?.enable_bond_basket?._value) ?? false);
configState.enableRecaptcha.set(parseJson(data?.enable_recaptcha?._value) ?? true);
// ... 13 more .set() calls
configState.isRemoteConfigFetched.set(true);

// AFTER — parse all values first, then apply in one batch
const parsed = {
  enableBondBasket: parseJson(data?.enable_bond_basket?._value) ?? false,
  enableRecaptcha: parseJson(data?.enable_recaptcha?._value) ?? true,
  showReferral: parseJson(data?.show_referral?._value) ?? false,
  // ... all other values
};

// Hookstate batch update — all subscribers notified once
configState.batch(() => {
  configState.enableBondBasket.set(parsed.enableBondBasket);
  configState.enableRecaptcha.set(parsed.enableRecaptcha);
  configState.showReferral.set(parsed.showReferral);
  // ... all others
  configState.isRemoteConfigFetched.set(true);
});

// If Hookstate batch API is not available, use a single top-level config object:
configState.set({
  ...configState.get(),
  ...parsed,
  isRemoteConfigFetched: true,
});
```

---

## P1 — Fix 4: Parallelize AsyncStorage reads

**File:** `src/screens/homeRevamp/hooks/useHomePage.ts` (Lines 262–283)
**File:** `src/hooks/useAuth.ts` (Lines 195–202)
**Impact:** 50–150ms reduction per affected flow

```ts
// BEFORE — sequential reads, each waits for the previous
const updateAppVisitCount = async () => {
  const whatsAppConfirmationDone = await LocalAsyncStorage.getObject(WHATSAPP_CONFIRMATION);
  const currentCount = await LocalAsyncStorage.getObject(APP_VISIT_COUNT);
  LocalAsyncStorage.setObject(APP_VISIT_COUNT, currentCount + 1);
};

// AFTER — parallel reads via Promise.all
const updateAppVisitCount = async () => {
  const [whatsAppConfirmationDone, currentCount] = await Promise.all([
    LocalAsyncStorage.getObject(WHATSAPP_CONFIRMATION),
    LocalAsyncStorage.getObject(APP_VISIT_COUNT),
  ]);
  LocalAsyncStorage.setObject(APP_VISIT_COUNT, (currentCount ?? 0) + 1);
};
```

**For useAuth.ts — cache token in memory after first read:**

```ts
// Module-level cache — avoids repeated AsyncStorage reads
let cachedToken: string | null = null;

const getTokenFromMemory = async () => {
  if (cachedToken !== null) return cachedToken; // Return cached, no AsyncStorage hit
  cachedToken = await LocalAsyncStorage.getObject(TOKEN_KEY);
  return cachedToken;
};

// Clear cache on logout
export const clearTokenCache = () => { cachedToken = null; };
```

---

## P1 — Fix 5: Remove `.get()` calls from `useEffect` dependency arrays

**File:** `src/screens/homeRevamp/hooks/useHomePage.ts` (Lines 320, 384, 415–417)
**Impact:** Eliminates cascading re-subscription loop

```ts
// BEFORE — .get() in dep array causes re-subscription on every render
useEffect(() => {
  managePageRefresh();
}, [pusherEvent.get()]); // Called on every render, not just when value changes

useEffect(() => {
  checkForHomePageRefresh();
}, [userProfile.userCategory.get()]); // Same problem

// AFTER — extract value before the effect
const pusherEventValue = useHookstate(pusherEvent);
const userCategory = useHookstate(userProfile.userCategory);

useEffect(() => {
  managePageRefresh();
}, [pusherEventValue]); // Stable reference, only re-runs when value actually changes

useEffect(() => {
  checkForHomePageRefresh();
}, [userCategory.get()]); // Or use a derived local variable
```

---

## P2 — Fix 6: Switch carousel to native driver

**File:** `src/screens/homeRevamp/components/webBanner/components/useCarousel.tsx` (Lines 32–37)
**Impact:** Removes per-frame JS thread load; enables 60fps independent of JS work

The carousel width animation uses `useNativeDriver: false` because it's animating `width` — which cannot be natively driven. The fix requires switching to `transform: [{ scaleX }]` or migrating to `react-native-reanimated`.

**Option A — Use `transform` (simpler, same visual result):**

```ts
// BEFORE
Animated.timing(widthAnim, {
  toValue: progress,
  duration,
  easing: Easing.linear,
  useNativeDriver: false, // Width animation — JS thread only
}).start();

// AFTER — use scaleX transform instead of width
// The progress indicator is a fixed-width element that scales
const scaleAnim = useRef(new Animated.Value(0)).current;

Animated.timing(scaleAnim, {
  toValue: progress, // 0 to 1
  duration,
  easing: Easing.linear,
  useNativeDriver: true, // Now runs on native UI thread
}).start();

// In the component:
<Animated.View
  style={{
    width: TOTAL_WIDTH, // Fixed width
    transform: [{ scaleX: scaleAnim }], // Scale instead of width change
    transformOrigin: 'left', // Needs reanimated or workaround
  }}
/>
```

**Option B — Migrate to `react-native-reanimated` (recommended for new work):**

```ts
import Animated, { useSharedValue, withTiming, Easing } from 'react-native-reanimated';

const progress = useSharedValue(0);

const startAnimation = (toValue: number) => {
  progress.value = withTiming(toValue, { duration, easing: Easing.linear });
};

// Runs entirely on UI thread — zero JS thread involvement
<Animated.View style={useAnimatedStyle(() => ({ width: progress.value * TOTAL_WIDTH }))} />
```

---

## Validation After Each Fix

After implementing each fix:

1. Run Android Profiler CPU trace during a cold start
2. Check that JS thread shows no spikes >700ms in the startup + home mount window
3. Check Play Console Vitals 24 hours after deploy to staging (if Play Console is configured for staging track)

See [`TEST_SUITE.md`](TEST_SUITE.md) for full testing procedures.
