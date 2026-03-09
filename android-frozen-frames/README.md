# Android Frozen Frames — Performance Investigation

## Overview

**Metric:** Excessive Frozen Frames (frames taking >700ms to render)
**Current:** 22.83% | **Acceptable limit:** 4.7% | **Gap:** 18.13 percentage points

**Platform:** Android only (tracked via Google Play Console Vitals)
**Source repo:** [yubi-b2c-mobile](https://github.com/yubisecurities/yubi-b2c-mobile)

**Status:** Root cause identified. Fixes ready for implementation.

---

## What Are Frozen Frames?

A frozen frame is any frame that takes **>700ms** to render. Android tracks this separately from slow frames (<16ms). Excessive frozen frames directly cause the app to appear **completely unresponsive** to the user — taps don't register, scroll is stuck, content doesn't load.

Google considers >4.7% frozen frames as "bad behaviour" in Play Console Vitals. At 22.83%, Aspero is ~5x over the acceptable threshold.

---

## Project Structure

```
android-frozen-frames/
├── README.md                    # This file — project overview & quick start
├── ROOT_CAUSE_ANALYSIS.md       # All identified issues with file/line callouts
├── SPEC.md                      # Performance targets, definitions, success criteria
├── RECOMMENDED_FIXES.md         # Prioritised fixes with code examples
└── TEST_SUITE.md                # How to verify and measure improvements
```

---

## Key Findings Summary

The root cause is **cumulative JS thread blocking during app startup and home screen mount**, totaling an estimated 1.5–2.5 seconds of blocking per session.

| # | Issue | File | Est. JS Block |
|---|-------|------|---------------|
| 1 | App init cascade (5 native calls on mount) | `useMobileApp.ts` | 300–500ms |
| 2 | Analytics init — 5 SDKs in one useEffect | `useAppLaunchConfig.ts` | 200–400ms |
| 3 | Widget config loop — WIDGET_COMPONENT_MAP rebuilt per widget | `useHomePage.ts:112-190` | 200–400ms |
| 4 | Remote config — 15+ sequential `.set()` calls | `useRemoteConfig.ts` | 100–200ms |
| 5 | Sequential AsyncStorage reads on home mount | `useHomePage.ts:262-283` | 100–200ms |
| 6 | `.get()` in useEffect dependency arrays | `useHomePage.ts:320,384,415` | 150–250ms |
| 7 | JS-thread carousel animation (useNativeDriver: false) | `useCarousel.tsx:32-37` | 100–300ms/frame |
| 8 | Auth AsyncStorage reads on startup | `useAuth.ts:195-202` | 100–200ms |

---

## Quick Start for Engineers

### Step 1 — Understand the problem
Read [`ROOT_CAUSE_ANALYSIS.md`](ROOT_CAUSE_ANALYSIS.md) for file-level breakdowns with code snippets.

### Step 2 — Understand the target
Read [`SPEC.md`](SPEC.md) for performance definitions, thresholds, and success criteria.

### Step 3 — Implement fixes
Read [`RECOMMENDED_FIXES.md`](RECOMMENDED_FIXES.md) for prioritised fixes with before/after code.

### Step 4 — Verify
Follow [`TEST_SUITE.md`](TEST_SUITE.md) to measure improvements before and after.

---

## Implementation Order

### P0 — Do these first (highest impact, lowest risk)
1. Defer non-critical startup services using `InteractionManager.runAfterInteractions()`
2. Memoize `WIDGET_COMPONENT_MAP` — move outside the `_forEach` loop
3. Batch remote config state — parse all 15 values, then do one bulk update

### P1 — High impact, moderate effort
4. Parallelize AsyncStorage reads with `Promise.all()`
5. Fix `useEffect` dependency arrays — remove `.get()` calls from deps

### P2 — Medium impact
6. Switch carousel animation to `useNativeDriver: true`

---

## Expected Outcome

| Metric | Before | After (expected) |
|--------|--------|------------------|
| Frozen Frames | 22.83% | <4.7% |
| App startup block | ~1.5–2.5s | <300ms |
| Home screen mount | ~800ms+ | <200ms |

---

## Files to Modify in yubi-b2c-mobile

```
src/hooks/mobileApp/useMobileApp.ts                          ← P0
src/hooks/useAppLaunchConfig.ts                              ← P0
src/screens/homeRevamp/hooks/useHomePage.ts                  ← P0, P1
src/hooks/useRemoteConfig.ts                                 ← P0
src/hooks/useAuth.ts                                         ← P1
src/screens/homeRevamp/components/webBanner/useCarousel.tsx  ← P2
```

---

*Created: 2026-03-09*
*Play Console metric date: March 2026*
*Severity: HIGH — 5x over acceptable threshold, visible app freezing*
