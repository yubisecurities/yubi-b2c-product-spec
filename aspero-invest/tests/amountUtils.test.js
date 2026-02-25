/**
 * Unit tests — Amount Utilities
 * Refs: testsuite.md §1 (SLIDER-01…SLIDER-07), PRD §6.1
 *
 * Covers: sliderToAmt, amtToSlider, fmtAmt, fmtAmtFull, earnings
 *
 * Run: npx jest tests/amountUtils.test.js
 */

// ─── Pure functions extracted from index.html ───────────────────────────────

const AMT_MIN = 10000;
const AMT_MAX = 5000000;

/**
 * Convert slider percentage (0–100) to a rupee amount using log scale.
 * @param {number} pct - 0 to 100
 * @returns {number}
 */
function sliderToAmt(pct) {
  const lmin = Math.log(AMT_MIN);
  const lmax = Math.log(AMT_MAX);
  return Math.round(Math.exp(lmin + (pct / 100) * (lmax - lmin)));
}

/**
 * Convert a rupee amount to slider percentage (0–100) using log scale.
 * @param {number} amt
 * @returns {number}
 */
function amtToSlider(amt) {
  const lmin = Math.log(AMT_MIN);
  const lmax = Math.log(AMT_MAX);
  return ((Math.log(amt) - lmin) / (lmax - lmin)) * 100;
}

/**
 * Format amount in short Indian notation.
 * @param {number} n
 * @returns {string}
 */
function fmtAmt(n) {
  if (n >= 10000000) return '₹' + (n / 10000000).toFixed(1) + 'Cr';
  if (n >= 100000)   return '₹' + (n / 100000).toFixed(n % 100000 === 0 ? 0 : 1) + 'L';
  if (n >= 1000)     return '₹' + (n / 1000).toFixed(0) + 'K';
  return '₹' + n;
}

/**
 * Format amount in full Indian locale format.
 * @param {number} n
 * @returns {string}
 */
function fmtAmtFull(n) {
  return '₹' + n.toLocaleString('en-IN');
}

/**
 * Calculate estimated earnings.
 * @param {number} amount - principal ₹
 * @param {number} ret - annual yield %
 * @param {number} durMonths - duration in months
 * @returns {number}
 */
function earnings(amount, ret, durMonths) {
  return Math.round(amount * (ret / 100) * (durMonths / 12));
}

// ─── sliderToAmt ─────────────────────────────────────────────────────────────

describe('sliderToAmt', () => {
  // SLIDER-01: leftmost position = ₹10,000
  test('pct=0 → AMT_MIN (₹10,000)', () => {
    expect(sliderToAmt(0)).toBe(10000);
  });

  // SLIDER-03: rightmost = ₹50,00,000
  test('pct=100 → AMT_MAX (₹50,00,000)', () => {
    expect(sliderToAmt(100)).toBe(5000000);
  });

  // SLIDER-03: log midpoint is NOT linear midpoint
  test('pct=50 → log midpoint (~₹2,23,607), not linear midpoint (₹25,05,000)', () => {
    const mid = sliderToAmt(50);
    // log midpoint: exp((log(10000) + log(5000000)) / 2) = sqrt(10000 * 5000000) ≈ 223607
    expect(mid).toBeGreaterThan(200000);
    expect(mid).toBeLessThan(250000);
    // Definitely not linear midpoint
    expect(mid).not.toBe(2505000);
  });

  // Quick-chip snap positions
  test('pct for ₹25K → converts back to ~₹25,000', () => {
    const pct = amtToSlider(25000);
    const amt = sliderToAmt(pct);
    expect(amt).toBe(25000);
  });

  test('pct for ₹1L → converts back to ~₹1,00,000', () => {
    const pct = amtToSlider(100000);
    const amt = sliderToAmt(pct);
    expect(amt).toBe(100000);
  });

  test('pct for ₹25L → converts back to ~₹25,00,000', () => {
    const pct = amtToSlider(2500000);
    const amt = sliderToAmt(pct);
    expect(amt).toBe(2500000);
  });

  test('returns an integer (Math.round applied)', () => {
    for (let pct = 0; pct <= 100; pct += 5) {
      expect(sliderToAmt(pct)).toBe(Math.floor(sliderToAmt(pct)));
    }
  });
});

// ─── amtToSlider ─────────────────────────────────────────────────────────────

describe('amtToSlider', () => {
  test('AMT_MIN → pct = 0', () => {
    expect(amtToSlider(10000)).toBeCloseTo(0, 5);
  });

  test('AMT_MAX → pct = 100', () => {
    expect(amtToSlider(5000000)).toBeCloseTo(100, 5);
  });

  test('result is always between 0 and 100', () => {
    [10000, 25000, 50000, 100000, 500000, 1000000, 2500000, 5000000].forEach(amt => {
      const pct = amtToSlider(amt);
      expect(pct).toBeGreaterThanOrEqual(0);
      expect(pct).toBeLessThanOrEqual(100);
    });
  });
});

// ─── Round-trip: sliderToAmt ↔ amtToSlider ───────────────────────────────────

describe('sliderToAmt / amtToSlider — round-trip fidelity', () => {
  // SLIDER-06: all quick chips
  const QUICK_AMOUNTS = [10000, 25000, 50000, 100000, 500000, 1000000, 2500000];

  test.each(QUICK_AMOUNTS)('round-trip for ₹%d', (amt) => {
    const pct = amtToSlider(amt);
    const recovered = sliderToAmt(pct);
    // Allow ±1 rupee due to floating point + rounding
    expect(Math.abs(recovered - amt)).toBeLessThanOrEqual(1);
  });

  test('slider moves monotonically (higher pct → higher amount)', () => {
    let prev = sliderToAmt(0);
    for (let pct = 1; pct <= 100; pct++) {
      const cur = sliderToAmt(pct);
      expect(cur).toBeGreaterThanOrEqual(prev);
      prev = cur;
    }
  });
});

// ─── fmtAmt ──────────────────────────────────────────────────────────────────

describe('fmtAmt', () => {
  // SLIDER-07
  test('₹10,000 → "₹10K"', () => {
    expect(fmtAmt(10000)).toBe('₹10K');
  });

  test('₹25,000 → "₹25K"', () => {
    expect(fmtAmt(25000)).toBe('₹25K');
  });

  test('₹50,000 → "₹50K"', () => {
    expect(fmtAmt(50000)).toBe('₹50K');
  });

  test('₹1,00,000 → "₹1L"', () => {
    expect(fmtAmt(100000)).toBe('₹1L');
  });

  test('₹5,00,000 → "₹5L"', () => {
    expect(fmtAmt(500000)).toBe('₹5L');
  });

  test('₹10,00,000 → "₹10L"', () => {
    expect(fmtAmt(1000000)).toBe('₹10L');
  });

  test('₹25,00,000 → "₹25L"', () => {
    expect(fmtAmt(2500000)).toBe('₹25L');
  });

  test('₹1,50,000 → "₹1.5L" (non-round lakh)', () => {
    expect(fmtAmt(150000)).toBe('₹1.5L');
  });

  test('₹1,00,00,000 → "₹1.0Cr"', () => {
    expect(fmtAmt(10000000)).toBe('₹1.0Cr');
  });

  test('₹999 → "₹999" (below 1K)', () => {
    expect(fmtAmt(999)).toBe('₹999');
  });
});

// ─── fmtAmtFull ──────────────────────────────────────────────────────────────

describe('fmtAmtFull', () => {
  test('returns string starting with ₹', () => {
    expect(fmtAmtFull(10000)).toMatch(/^₹/);
  });

  test('₹10,000 → "₹10,000"', () => {
    expect(fmtAmtFull(10000)).toBe('₹10,000');
  });

  test('₹1,00,000 → "₹1,00,000"', () => {
    expect(fmtAmtFull(100000)).toBe('₹1,00,000');
  });

  test('₹25,00,000 → "₹25,00,000"', () => {
    expect(fmtAmtFull(2500000)).toBe('₹25,00,000');
  });
});

// ─── earnings ────────────────────────────────────────────────────────────────

describe('earnings', () => {
  // formula: round(amount × (ret/100) × (durMonths/12))

  test('₹10,000 at 8.5% for 12 months → ₹850', () => {
    expect(earnings(10000, 8.5, 12)).toBe(850);
  });

  test('₹1,00,000 at 12% for 18 months → ₹18,000', () => {
    expect(earnings(100000, 12, 18)).toBe(18000);
  });

  test('₹50,000 at 10.5% for 24 months → ₹10,500', () => {
    expect(earnings(50000, 10.5, 24)).toBe(10500);
  });

  test('₹10,000 at 9.2% for 6 months → ₹460', () => {
    expect(earnings(10000, 9.2, 6)).toBe(460);
  });

  test('returns an integer (Math.round applied)', () => {
    // Non-round inputs
    expect(earnings(10000, 7.8, 24)).toBe(Math.round(10000 * 0.078 * 2));
  });

  test('scales linearly with amount', () => {
    const e1 = earnings(10000, 8.5, 12);
    const e2 = earnings(20000, 8.5, 12);
    expect(e2).toBe(e1 * 2);
  });

  test('scales linearly with duration', () => {
    const e1 = earnings(10000, 8.5, 12);
    const e2 = earnings(10000, 8.5, 24);
    expect(e2).toBe(e1 * 2);
  });

  test('zero amount → zero earnings', () => {
    expect(earnings(0, 10, 12)).toBe(0);
  });

  test('zero duration → zero earnings', () => {
    expect(earnings(100000, 10, 0)).toBe(0);
  });
});

// ─── Integration: amount display pipeline ─────────────────────────────────────

describe('Amount display pipeline', () => {
  test('chip ₹1L → slider pct → back to ₹1L → fmtAmtFull shows ₹1,00,000', () => {
    const chipValue = 100000;
    const pct = amtToSlider(chipValue);
    const recovered = sliderToAmt(pct);
    expect(fmtAmtFull(recovered)).toBe('₹1,00,000');
  });

  test('slider at 0% → fmtAmt shows ₹10K', () => {
    expect(fmtAmt(sliderToAmt(0))).toBe('₹10K');
  });

  test('slider at 100% → fmtAmt shows ₹50L', () => {
    expect(fmtAmt(sliderToAmt(100))).toBe('₹50L');
  });
});
