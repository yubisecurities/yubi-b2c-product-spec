# Performance Specification — Android Frozen Frames

## Definitions

| Term | Definition |
|------|-----------|
| **Frozen Frame** | A single UI frame that takes >700ms to render (Android definition) |
| **Slow Frame** | A frame that takes >16ms but <700ms to render |
| **Excessive Frozen Frames** | Google Play Vitals metric: % of user sessions with ≥1 frozen frame |
| **JS Thread Block** | A synchronous operation on the React Native JavaScript thread that prevents frame rendering |
| **TTI (Time to Interactive)** | Time from app launch until the user can meaningfully interact with the home screen |
| **Cold Start** | App launch from a completely stopped state (no cached JS bundle in memory) |
| **Warm Start** | App launch from background (cached state exists) |

---

## Acceptable Thresholds

### Google Play Console Vitals

| Metric | Bad | Needs Improvement | Good |
|--------|-----|-------------------|------|
| Excessive Frozen Frames | >4.7% | 2–4.7% | <2% |
| Slow Rendering | >33.3% | 20–33.3% | <20% |

### Internal Aspero Targets (post-fix)

| Metric | Current | Target | Stretch |
|--------|---------|--------|---------|
| Frozen Frames | 22.83% | <4.7% | <2% |
| App cold start (JS thread block) | ~1.5–2.5s | <300ms | <150ms |
| Home screen mount time | ~800ms+ | <200ms | <100ms |
| Carousel FPS (home screen) | ~30fps | 60fps | 60fps |

---

## Performance Budget

### Startup Phase (t=0 to first meaningful render)

| Operation | Budget | Current | Status |
|-----------|--------|---------|--------|
| Critical native init (SplashScreen.hide) | <50ms | ~50ms | OK |
| Token read from memory | <20ms | ~100–200ms | FAIL |
| Widget config preparation | <50ms | ~200–400ms | FAIL |
| Total startup JS block | <200ms | ~800–1,200ms | FAIL |

### Home Screen Mount Phase

| Operation | Budget | Current | Status |
|-----------|--------|---------|--------|
| Widget loop + component map | <30ms | ~200–400ms | FAIL |
| AsyncStorage reads | <20ms total | ~100–200ms | FAIL |
| Remote config application | <20ms | ~100–200ms + cascades | FAIL |
| Total home mount JS block | <100ms | ~500–800ms | FAIL |

### Ongoing (post-mount)

| Operation | Budget | Current | Status |
|-----------|--------|---------|--------|
| Carousel animation per frame | <8ms | JS thread (unbounded) | FAIL |
| Pusher event handler | <10ms | Not measured | TBD |
| State update + re-render | <16ms | Cascading, unmeasured | TBD |

---

## What Counts as a Fix

A fix is considered complete when:

1. **Frozen frames metric drops below 4.7%** as measured in Google Play Console Vitals over a rolling 28-day window post-deploy
2. **No regression** in iOS or web performance metrics
3. **Verified locally** using Android Profiler (CPU trace shows no JS thread spikes >700ms during startup)

A fix is NOT complete if:
- The metric improves but stays above 4.7%
- The fix solves one issue but introduces new blocked frames elsewhere
- The fix only works on flagship devices but not on mid-range or budget Android

---

## Target Devices

Frozen frames are most severe on mid-range and budget Android devices (the majority of the Indian user base).

| Priority | Device Class | Examples | Why It Matters |
|----------|-------------|---------|---------------|
| P0 | Budget (<₹15k) | Redmi 9A, Realme C21, Tecno Pop 6 | JS engine slower; most affected by thread blocks |
| P1 | Mid-range (₹15k–35k) | Redmi Note 12, Moto G84, Samsung M34 | Majority of active users |
| P2 | Flagship (>₹35k) | Pixel 7, Samsung S23, OnePlus 11 | Rarely affected; use for baseline |

---

## Tracking & Monitoring

### Google Play Console
- **Location:** Android Vitals → Core Vitals → Frozen frames
- **Update frequency:** Daily (28-day rolling window)
- **Filter by:** Android version, device RAM tier, app version

### Firebase Performance (recommended to add)
Add custom traces around critical startup phases to measure in production:

```ts
import perf from '@react-native-firebase/perf';

// In useMobileApp.ts
const trace = await perf().startTrace('app_startup');
await initialLoadOfMobileApp();
await trace.stop();

// In useHomePage.ts
const homeTrace = await perf().startTrace('home_screen_mount');
// ... mount logic
await homeTrace.stop();
```

### Flipper (local development)
- Use **React DevTools** plugin → Profiler tab to see render counts and durations
- Use **Hermes Debugger** for JS thread CPU traces
- Use **Android Studio Profiler** for native thread activity alongside JS

---

## Success Criteria Checklist

- [ ] Google Play Console frozen frames metric: **<4.7%** (currently 22.83%)
- [ ] Android Studio CPU trace: no JS thread spikes >700ms during cold start
- [ ] Home screen mounts within **200ms** of component tree initialization
- [ ] Carousel animation runs at **60fps** without JS thread interference
- [ ] No new frozen frame regressions on iOS (Xcode Instruments validation)
- [ ] Test verified on at least one budget Android device (e.g., Redmi 9A)
- [ ] Test verified on at least one mid-range Android device (e.g., Redmi Note 12)
