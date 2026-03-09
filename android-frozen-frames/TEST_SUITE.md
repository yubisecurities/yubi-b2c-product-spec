# Test Suite — Android Frozen Frames

This document covers how to measure frozen frames before and after fixes, both locally and in production.

---

## Test Environment Setup

### Required Tools
- Android Studio (for CPU Profiler)
- Flipper (for React DevTools + Hermes profiler)
- Physical Android test device (preferred over emulator — emulators don't accurately reproduce timing)
- Google Play Console access (for production metrics)

### Recommended Test Devices

| Priority | Device | Why |
|----------|--------|-----|
| P0 | Redmi 9A / Realme C21 | Budget device, worst-case performance — most affected |
| P0 | Redmi Note 12 / Samsung M34 | Mid-range — majority of user base |
| P1 | OnePlus Nord / Moto G84 | Upper mid-range |
| P2 | Pixel 7 / Samsung S23 | Flagship baseline |

### Build Configuration
Always test in **release mode** (not debug). Debug builds have the JS bundler overhead and Hermes inspector enabled, which skews timing significantly.

```bash
# Build release APK for testing
cd android && ./gradlew assembleRelease
adb install app/build/outputs/apk/release/app-release.apk
```

---

## Test Suite 1: Baseline Measurement (Before Fixes)

**Goal:** Establish the current frozen frame profile before any changes.

### TC1.1: Android Studio CPU Trace — Cold Start

**Steps:**
1. Open Android Studio → Run → Profile app (Release configuration)
2. Select **CPU Profiler** → **Java/Kotlin Method Trace** or **Callstack Sample**
3. Force-stop the app on device: `adb shell am force-stop com.aspero.app`
4. Start the CPU trace recording
5. Launch the app from the homescreen icon
6. Wait until the home screen is fully loaded and interactive
7. Stop the trace

**What to look for:**
- Threads view: Find the `mqt_js` thread (React Native JS thread)
- Look for any execution gaps or spikes on this thread lasting >700ms
- These are your frozen frame candidates

**Expected baseline (before fixes):**
- At least 1 spike of >700ms during cold start
- Typically 1–3 spikes between t=0 and t=3000ms

**Record:**
- Number of JS thread spikes >700ms
- Duration of longest spike
- Time of first spike after launch

---

### TC1.2: Systrace / Perfetto — Frame Rendering Timeline

**Steps:**
1. Connect device via ADB
2. Run Perfetto trace:
   ```bash
   adb shell perfetto -o /data/misc/perfetto-traces/trace.pftrace -t 10s \
     -c - <<EOF
   buffers: { size_kb: 63488 }
   data_sources: { config { name: "android.surfaceflinger.frametimeline" } }
   data_sources: { config { name: "track_event" } }
   EOF
   adb pull /data/misc/perfetto-traces/trace.pftrace ~/frozen-baseline.pftrace
   ```
3. Open `frozen-baseline.pftrace` at [ui.perfetto.dev](https://ui.perfetto.dev)
4. Search for `com.aspero.app` in the frame timeline
5. Red frames = slow (>16ms); Dark red = frozen (>700ms)

**Record:**
- Screenshot of frame timeline during cold start
- Count of red frames in first 5 seconds
- Count of dark red (frozen) frames in first 5 seconds

---

### TC1.3: Flipper — React DevTools Component Render Profile

**Steps:**
1. Open Flipper → Connect to device → React DevTools plugin
2. Click **Profiler** tab → Enable "Record why each component rendered"
3. Click **Record**
4. Cold-start the app
5. Wait for home screen to load
6. Stop recording

**What to look for:**
- Components rendering >10 times before first meaningful content (indicates re-render cascade)
- `useHomePage` render count during mount phase
- Total commit duration for home screen mount

**Record:**
- Home screen mount commit duration (ms)
- Number of renders for `HomePage` component during mount
- Which components triggered the most re-renders

---

## Test Suite 2: Measuring Individual Fixes

### TC2.1: Startup JS Block — Before/After InteractionManager Deferral

**Steps:**
1. Add `console.time` markers around startup operations:
   ```ts
   // In useMobileApp.ts — temporary logging
   console.time('startup_total');
   console.time('startup_critical'); // SplashScreen.hide
   SplashScreen.hide();
   console.timeEnd('startup_critical');

   InteractionManager.runAfterInteractions(() => {
     console.time('startup_deferred');
     // ... deferred work
     console.timeEnd('startup_deferred');
   });
   console.timeEnd('startup_total');
   ```
2. Run cold start and read Metro logs
3. Compare times before and after deferral

**Pass criteria:** `startup_critical` < 50ms; `startup_deferred` can be anything (it's off the critical path)

---

### TC2.2: Widget Config Loop — Before/After Memoization

**Steps:**
1. Add timing around the widget loop:
   ```ts
   // In useHomePage.ts — temporary logging
   console.time('widget_config');
   prepareDashboardHomeConfig();
   console.timeEnd('widget_config');
   ```
2. Run home screen mount 3 times (warm start), record average
3. Implement the `useMemo` fix
4. Repeat and compare

**Pass criteria:** `widget_config` < 30ms (from current ~200–400ms)

---

### TC2.3: Remote Config State Updates — Render Count

**Steps:**
1. Temporarily add a render counter to a component subscribed to `configState`:
   ```ts
   // In a component using configState
   const renderCount = useRef(0);
   renderCount.current += 1;
   console.log('render count:', renderCount.current);
   ```
2. Launch app, observe how many renders happen after `isRemoteConfigFetched` becomes true
3. Implement the batch `.set()` fix
4. Re-run and compare render count

**Pass criteria:** Render count triggered by remote config resolution drops from ~15+ to 1–2

---

### TC2.4: AsyncStorage Reads — Parallel vs Sequential

**Steps:**
1. Add timing to `updateAppVisitCount`:
   ```ts
   console.time('asyncstorage_reads');
   await updateAppVisitCount();
   console.timeEnd('asyncstorage_reads');
   ```
2. Record time before fix (sequential)
3. Apply `Promise.all` fix
4. Record time after fix

**Pass criteria:** Time drops from ~100–200ms to <40ms

---

## Test Suite 3: Full Regression Testing (Post All Fixes)

### TC3.1: Frozen Frame Check — Release Build on Budget Device

**Steps:**
1. Build release APK with all fixes applied
2. Install on a budget device (e.g., Redmi 9A)
3. Force-stop the app
4. Run Android Studio CPU trace for cold start (same as TC1.1)
5. Check for JS thread spikes >700ms

**Pass criteria:** Zero JS thread spikes >700ms during cold start to home screen mount

---

### TC3.2: Frame Rate Check — Home Screen Carousel

**Steps:**
1. On home screen with carousel animation active
2. Open developer options on device → **Show GPU rendering profile**
3. Observe the bar chart — bars should stay within the green 16ms line
4. Alternatively, in adb:
   ```bash
   adb shell dumpsys gfxinfo com.aspero.app framestats | head -50
   ```

**Pass criteria:** No frames in the carousel section exceed 16ms (green line) once the JS thread is unblocked

---

### TC3.3: iOS Regression Check

**Steps:**
1. Run same cold start test on iOS using Xcode Instruments → Time Profiler
2. Verify that deferred startup init doesn't break iOS behavior (ZohoSalesIQ, GoogleSignin, etc.)
3. Verify home screen loads correctly

**Pass criteria:** No new frozen frames or regressions on iOS; all deferred services initialize correctly

---

### TC3.4: End-to-End Flow Test

Verify these flows work correctly after all changes:

| Flow | Steps | Pass Criteria |
|------|-------|---------------|
| Cold start | Launch app from stopped state | Home screen loads, no blank screen |
| Sign in | Enter mobile → OTP → Home | All steps complete, analytics events fire |
| Home screen carousel | Auto-advances after 5s | Smooth animation at 60fps |
| Deep link on cold start | Open app via deep link | Deep link handled correctly (not lost due to deferral) |
| Remote config gate | App respects feature flags | enableBondBasket, enableRecaptcha apply correctly |
| Logout + re-login | Log out, log back in | Cached token cleared, fresh auth works |

---

## Test Suite 4: Production Validation

### TC4.1: Play Console Vitals — 28-Day Rolling Metric

**Steps:**
1. Deploy fix to production (or staged rollout — start with 10%)
2. Check Play Console → Android Vitals → Frozen frames
3. Monitor daily for 7 days

**Dashboard location:**
- [Google Play Console](https://play.google.com/console) → Select app → Android Vitals → Core Vitals

**Pass criteria:** Frozen frame percentage drops from 22.83% toward <4.7% within 7–14 days of reaching 100% rollout

---

### TC4.2: Firebase Performance Traces (Post-Integration)

If Firebase Performance custom traces are added (see SPEC.md):

**Steps:**
1. Deploy with custom traces added to `useMobileApp.ts` and `useHomePage.ts`
2. Open Firebase Console → Performance → Custom traces
3. Filter by `app_startup` and `home_screen_mount` traces
4. Compare P50 and P95 durations before and after fix

**Pass criteria:**
- `app_startup` P95 < 1,000ms (from current ~2,500ms+)
- `home_screen_mount` P95 < 300ms (from current ~800ms+)

---

## Regression Test Checklist

Run before merging any frozen frames fix PR:

- [ ] Cold start on budget Android device — no JS thread spikes >700ms (Android Profiler)
- [ ] Cold start on mid-range Android device — same check
- [ ] Home screen carousel plays smoothly — no jank visible
- [ ] All analytics events fire correctly (check Amplitude debugger)
- [ ] Remote config feature flags apply correctly (test with enableBondBasket toggle)
- [ ] Deep link handling works on cold start
- [ ] Sign in flow works end-to-end
- [ ] iOS cold start — no regressions (Xcode Instruments)
- [ ] No new console errors or warnings introduced
- [ ] Deferred services (Zoho, AppsFlyer) initialize correctly after interaction
