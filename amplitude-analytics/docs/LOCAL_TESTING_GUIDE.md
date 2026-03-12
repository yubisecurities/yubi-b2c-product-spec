# 🚀 Local Testing Guide - Signin Bug Reproduction

## Dev Server Status
- Command running: `npm run start:web:dev`
- Expected startup time: 30-60 seconds (webpack compilation)
- Port: Check console output (typically http://localhost:8080 or http://localhost:8081)

## What You'll See

### Step 1: Open Browser
1. Wait for "Compiled successfully" message in terminal
2. Navigate to: **http://localhost:8080** (or the port shown)

### Step 2: Observe the Bug

**TIMELINE:**
```
t=0s:     Page loads, you see...
          ┌────────────────────────┐
          │ Get Started             │
          │ Please enter your       │
          │ Aadhaar linked number   │
          │                        │  ← BLANK HERE (BUG!)
          │    (loading...)         │
          └────────────────────────┘

t=2-3s:   Form suddenly appears
          ┌────────────────────────┐
          │ Get Started             │
          │ Please enter your       │
          │ Aadhaar linked number   │
          │                        │
          │ [_______________]       │
          │ (Mobile input)          │
          │                        │
          │ [Continue] Button       │
          └────────────────────────┘
```

### Step 3: Open Dev Tools to See Warnings

**On Mac:** Cmd + Option + I
**On Windows:** F12

**Console tab:**
- Look for React warnings about invalid return
- You may see: ⚠️ "Did not return anything from render"

**Network tab:**
- Look for API calls being made
- You can see the delay is from config fetching

## File Locations

**Broken File:**
```
src/molecules/MobileNoForm/MobileNoForm.web.tsx
```

**What needs fixing:**
```typescript
// Current (BROKEN):
export const MobileNoForm = (props: MobileNumberFormProps) => {
  const { isRemoteConfigFetched } = useRemoteConfigState();

  if (isRemoteConfigFetched.get()) {
    return <SignInForm {...props} />;
  }
  // ❌ Returns undefined - causes blank screen
};

// Should be (FIXED):
export const MobileNoForm = (props: MobileNumberFormProps) => {
  const { isRemoteConfigFetched } = useRemoteConfigState();

  if (isRemoteConfigFetched.get()) {
    return <SignInForm {...props} />;
  }
  return null; // ✅ Explicit return
};
```

## Testing the Fix

After the code is fixed:

1. **Save the file** - webpack should auto-recompile
2. **Refresh browser** - (Cmd+R or F5)
3. **Observe:**
   - ✅ Form appears **immediately**
   - ✅ No blank screen
   - ✅ No more delay
   - ✅ Console warnings gone

## Other Resources Created

1. **BROKEN_BUG_DEMO.html**
   - Open in browser for visual side-by-side demo
   - Click animation button to see the bug

2. **BROKEN_EXPERIENCE_EXPLANATION.md**
   - Detailed technical explanation
   - Timeline diagrams
   - Code comparisons

## Troubleshooting

### Dev server not starting?
```bash
# Kill any existing process
lsof -ti:8080 | xargs kill -9

# Try again
npm run start:web:dev
```

### Port already in use?
```bash
# Find what's using it
lsof -i :8080

# Use different port
PORT=8081 npm run start:web:dev
```

### HTTPS certificate issues?
- It's expected for local dev
- Click through any warnings
- This is development only

### Still seeing blank screen?
- Hard refresh: Cmd+Shift+R (Mac) or Ctrl+Shift+R (Windows)
- Clear browser cache
- Restart dev server

## Next Steps

1. See the bug in action ✅ (this is what you're doing now)
2. Understand the code ✅ (files created above)
3. Fix the code (ready when you are!)
4. Verify the fix works
5. Deploy!

---

**Need help?** Check the visual demos or ask me to fix the code immediately.
