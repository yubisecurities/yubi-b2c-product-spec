/**
 * Unit tests — Bond Matching Algorithm
 * Refs: testsuite.md §5 (MATCH-01 … MATCH-15), PRD §7, feature.md §Bond Matching Algorithm
 *
 * Run: npx jest tests/bondMatcher.test.js
 */

// ─── Pure functions extracted from index.html ───────────────────────────────

const RISK_RANK = { conservative: 0, moderate: 1, aggressive: 2 };

/**
 * Compute match score for a single bond given current state selections.
 * @param {object} bond - { dur, risk, rs, ret, min, ... }
 * @param {number|null} selectedDurationMonths - null = not selected
 * @param {string|null} selectedRisk - 'conservative' | 'moderate' | 'aggressive' | null
 * @returns {number} score 0–65
 */
function matchScore(bond, selectedDurationMonths, selectedRisk) {
  let s = 0;
  if (selectedDurationMonths !== null) {
    const dd = Math.abs(bond.dur - selectedDurationMonths);
    if (dd === 0) s += 40;
    else if (dd <= 6) s += 22;
    else if (dd <= 12) s += 10;
  }
  if (selectedRisk !== null) {
    const rd = Math.abs(RISK_RANK[bond.risk] - RISK_RANK[selectedRisk]);
    if (rd === 0) s += 25;
    else if (rd === 1) s += 10;
  }
  return s;
}

/**
 * Filter bonds by amount and risk (±1 tier adjacency).
 * @param {object[]} bonds
 * @param {number} amount
 * @param {string|null} selectedRisk
 * @returns {object[]} filtered list with { ...bond, score }
 */
function getFiltered(bonds, amount, selectedDurationMonths, selectedRisk) {
  return bonds
    .filter(b => {
      if (b.min > amount) return false;
      if (selectedRisk !== null && Math.abs(RISK_RANK[b.risk] - RISK_RANK[selectedRisk]) > 1) return false;
      return true;
    })
    .map(b => ({ ...b, score: matchScore(b, selectedDurationMonths, selectedRisk) }));
}

/**
 * Sort a list of scored bonds.
 * @param {object[]} bonds
 * @param {'match'|'high'|'low'|'safe'} sortMode
 * @returns {object[]} sorted copy
 */
function sorted(bonds, sortMode) {
  const copy = [...bonds];
  switch (sortMode) {
    case 'high': return copy.sort((a, b) => b.ret - a.ret);
    case 'low':  return copy.sort((a, b) => a.ret - b.ret);
    case 'safe': return copy.sort((a, b) => a.rs - b.rs);
    default:     return copy.sort((a, b) => b.score - a.score);
  }
}

/** Returns match badge label for a given score. */
function matchLabel(score) {
  if (score >= 70) return 'Great Match';
  if (score >= 40) return 'Good Match';
  return 'Fair Match';
}

// ─── Test data ───────────────────────────────────────────────────────────────

const BONDS = [
  { id: 1,  name: 'HDFC Ltd',             cat: 'Housing Finance',     rating: 'AAA',  rs: 1, ret: 8.50,  dur: 12, min: 10000,  risk: 'conservative' },
  { id: 2,  name: 'Bajaj Finance',        cat: 'Consumer Finance',    rating: 'AAA',  rs: 1, ret: 9.20,  dur: 18, min: 10000,  risk: 'conservative' },
  { id: 3,  name: 'LIC Housing Finance',  cat: 'Housing Finance',     rating: 'AAA',  rs: 1, ret: 8.80,  dur: 6,  min: 25000,  risk: 'conservative' },
  { id: 4,  name: 'REC Limited',          cat: 'Govt. Enterprise',    rating: 'AAA',  rs: 1, ret: 7.50,  dur: 6,  min: 10000,  risk: 'conservative' },
  { id: 5,  name: 'IRFC',                 cat: 'Railway Finance',     rating: 'AAA',  rs: 1, ret: 7.80,  dur: 24, min: 25000,  risk: 'conservative' },
  { id: 6,  name: 'Power Finance Corp',   cat: 'Govt. Enterprise',    rating: 'AAA',  rs: 1, ret: 7.90,  dur: 6,  min: 10000,  risk: 'conservative' },
  { id: 7,  name: 'Sundaram Finance',     cat: 'NBFC',                rating: 'AA+',  rs: 2, ret: 9.80,  dur: 12, min: 10000,  risk: 'conservative' },
  { id: 8,  name: 'Tata Capital',         cat: 'NBFC',                rating: 'AA+',  rs: 2, ret: 10.50, dur: 24, min: 25000,  risk: 'moderate' },
  { id: 9,  name: 'Shriram Finance',      cat: 'NBFC',                rating: 'AA+',  rs: 2, ret: 11.50, dur: 12, min: 10000,  risk: 'moderate' },
  { id: 10, name: 'Mahindra Finance',     cat: 'Vehicle Finance',     rating: 'AA+',  rs: 2, ret: 10.20, dur: 18, min: 10000,  risk: 'moderate' },
  { id: 11, name: 'Muthoot Finance',      cat: 'Gold Finance',        rating: 'AA',   rs: 3, ret: 12.00, dur: 18, min: 10000,  risk: 'moderate' },
  { id: 12, name: 'Manappuram Finance',   cat: 'Gold Finance',        rating: 'AA',   rs: 3, ret: 11.75, dur: 12, min: 10000,  risk: 'moderate' },
  { id: 13, name: 'Cholamandalam Inv.',   cat: 'Vehicle Finance',     rating: 'AA',   rs: 3, ret: 10.80, dur: 24, min: 25000,  risk: 'moderate' },
  { id: 14, name: 'Piramal Capital',      cat: 'Real Estate Finance', rating: 'AA-',  rs: 4, ret: 13.50, dur: 24, min: 25000,  risk: 'aggressive' },
  { id: 15, name: 'IIFL Finance',         cat: 'NBFC',                rating: 'AA-',  rs: 4, ret: 13.00, dur: 18, min: 10000,  risk: 'aggressive' },
  { id: 16, name: 'Aptus Value Housing',  cat: 'Housing Finance',     rating: 'A+',   rs: 5, ret: 13.75, dur: 12, min: 25000,  risk: 'aggressive' },
  { id: 17, name: 'Edelweiss ARC',        cat: 'Asset Reconst.',      rating: 'A',    rs: 6, ret: 14.50, dur: 12, min: 50000,  risk: 'aggressive' },
  { id: 18, name: 'Northern Arc Capital', cat: 'NBFC',                rating: 'A',    rs: 6, ret: 14.00, dur: 18, min: 25000,  risk: 'aggressive' },
  { id: 19, name: 'Vivriti Capital',      cat: 'NBFC',                rating: 'A-',   rs: 7, ret: 15.50, dur: 12, min: 50000,  risk: 'aggressive' },
  { id: 20, name: 'Ugro Capital',         cat: 'SME Finance',         rating: 'BBB+', rs: 8, ret: 16.00, dur: 24, min: 100000, risk: 'aggressive' },
];

// ─── Duration scoring ────────────────────────────────────────────────────────

describe('matchScore — duration dimension', () => {
  const bond = (dur) => ({ dur, risk: 'moderate', rs: 3 });

  // MATCH-01
  test('exact duration match → +40 pts', () => {
    expect(matchScore(bond(12), 12, null)).toBe(40);
  });

  // MATCH-02
  test('duration diff exactly 6 months → +22 pts', () => {
    expect(matchScore(bond(6), 12, null)).toBe(22);
  });

  test('duration diff exactly 6 months (other direction) → +22 pts', () => {
    expect(matchScore(bond(18), 12, null)).toBe(22);
  });

  // MATCH-03
  test('duration diff exactly 12 months → +10 pts', () => {
    expect(matchScore(bond(6), 18, null)).toBe(10);
  });

  test('duration diff exactly 12 months (other direction) → +10 pts', () => {
    expect(matchScore(bond(24), 12, null)).toBe(10);
  });

  // MATCH-04
  test('duration diff > 12 months → +0 pts', () => {
    expect(matchScore(bond(6), 24, null)).toBe(0);
  });

  test('duration diff = 18 months → +0 pts', () => {
    expect(matchScore(bond(6), 24, null)).toBe(0);
  });

  // MATCH-15
  test('null duration → duration dimension contributes 0', () => {
    const score = matchScore(bond(12), null, null);
    expect(score).toBe(0);
  });
});

// ─── Risk scoring ─────────────────────────────────────────────────────────────

describe('matchScore — risk dimension', () => {
  const bond = (risk) => ({ dur: 12, risk, rs: 2 });

  // MATCH-05
  test('exact risk match → +25 pts', () => {
    expect(matchScore(bond('moderate'), null, 'moderate')).toBe(25);
  });

  // MATCH-06
  test('adjacent risk (±1 tier) → +10 pts', () => {
    expect(matchScore(bond('conservative'), null, 'moderate')).toBe(10);
    expect(matchScore(bond('aggressive'),   null, 'moderate')).toBe(10);
  });

  // MATCH-07
  test('far risk (±2 tiers) → +0 pts', () => {
    expect(matchScore(bond('conservative'), null, 'aggressive')).toBe(0);
    expect(matchScore(bond('aggressive'),   null, 'conservative')).toBe(0);
  });

  test('null risk → risk dimension contributes 0', () => {
    expect(matchScore(bond('moderate'), null, null)).toBe(0);
  });
});

// ─── Combined scoring ────────────────────────────────────────────────────────

describe('matchScore — combined', () => {
  // Perfect match: 40 + 25 = 65 (max possible)
  test('perfect duration + risk match → 65 pts', () => {
    const bond = { dur: 12, risk: 'moderate', rs: 3 };
    expect(matchScore(bond, 12, 'moderate')).toBe(65);
  });

  test('exact duration + adjacent risk → 40 + 10 = 50 pts', () => {
    const bond = { dur: 12, risk: 'conservative', rs: 2 };
    expect(matchScore(bond, 12, 'moderate')).toBe(50);
  });

  test('close duration + exact risk → 22 + 25 = 47 pts', () => {
    const bond = { dur: 6, risk: 'moderate', rs: 3 };
    expect(matchScore(bond, 12, 'moderate')).toBe(47);
  });

  test('null duration + exact risk → 0 + 25 = 25 pts (CTA locked but score computed)', () => {
    const bond = { dur: 12, risk: 'moderate', rs: 3 };
    expect(matchScore(bond, null, 'moderate')).toBe(25);
  });
});

// ─── Match label thresholds ───────────────────────────────────────────────────

describe('matchLabel', () => {
  // MATCH-08
  test('score ≥ 70 → Great Match', () => {
    // Note: max possible is 65 with current scoring; Great Match currently unreachable
    // This test documents the threshold as specified in feature.md
    expect(matchLabel(70)).toBe('Great Match');
    expect(matchLabel(100)).toBe('Great Match');
  });

  test('score 40–69 → Good Match', () => {
    expect(matchLabel(40)).toBe('Good Match');
    expect(matchLabel(65)).toBe('Good Match');
    expect(matchLabel(69)).toBe('Good Match');
  });

  test('score < 40 → Fair Match', () => {
    expect(matchLabel(39)).toBe('Fair Match');
    expect(matchLabel(25)).toBe('Fair Match');
    expect(matchLabel(0)).toBe('Fair Match');
  });

  test('boundary: score exactly 40 → Good Match (not Fair)', () => {
    expect(matchLabel(40)).toBe('Good Match');
  });

  test('boundary: score exactly 39 → Fair Match (not Good)', () => {
    expect(matchLabel(39)).toBe('Fair Match');
  });
});

// ─── Amount filter ────────────────────────────────────────────────────────────

describe('getFiltered — amount filter', () => {
  // MATCH-09
  test('excludes bonds where bond.min > selected amount', () => {
    const result = getFiltered(BONDS, 24999, null, null);
    result.forEach(b => expect(b.min).toBeLessThanOrEqual(24999));
  });

  test('includes bonds where bond.min === selected amount', () => {
    // Bond id=3 has min=25000
    const result = getFiltered(BONDS, 25000, null, null);
    expect(result.some(b => b.id === 3)).toBe(true);
  });

  test('includes bonds where bond.min < selected amount', () => {
    const result = getFiltered(BONDS, 100000, null, null);
    expect(result.some(b => b.min === 10000)).toBe(true);
  });

  test('excludes bond id=20 (min=₹1L) when amount=₹99,999', () => {
    const result = getFiltered(BONDS, 99999, null, null);
    expect(result.some(b => b.id === 20)).toBe(false);
  });

  test('includes bond id=20 (min=₹1L) when amount=₹1L exactly', () => {
    const result = getFiltered(BONDS, 100000, null, null);
    expect(result.some(b => b.id === 20)).toBe(true);
  });
});

// ─── Risk adjacency filter ────────────────────────────────────────────────────

describe('getFiltered — risk adjacency filter', () => {
  // MATCH-10
  test('excludes bonds ±2 risk tiers away from selection', () => {
    // conservative (rank 0) selected; aggressive (rank 2) → diff = 2 → excluded
    const result = getFiltered(BONDS, 500000, null, 'conservative');
    result.forEach(b => {
      expect(Math.abs(RISK_RANK[b.risk] - RISK_RANK['conservative'])).toBeLessThanOrEqual(1);
    });
  });

  test('includes bonds ±1 risk tier away from selection', () => {
    // moderate selected → conservative (diff=1) and aggressive (diff=1) both included
    const result = getFiltered(BONDS, 500000, null, 'moderate');
    expect(result.some(b => b.risk === 'conservative')).toBe(true);
    expect(result.some(b => b.risk === 'moderate')).toBe(true);
    expect(result.some(b => b.risk === 'aggressive')).toBe(true);
  });

  test('aggressive selected excludes conservative bonds', () => {
    const result = getFiltered(BONDS, 500000, null, 'aggressive');
    expect(result.some(b => b.risk === 'conservative')).toBe(false);
  });

  test('conservative selected excludes aggressive bonds', () => {
    const result = getFiltered(BONDS, 500000, null, 'conservative');
    expect(result.some(b => b.risk === 'aggressive')).toBe(false);
  });

  test('null risk applies no risk filter — all risk tiers included', () => {
    const result = getFiltered(BONDS, 500000, null, null);
    expect(result.some(b => b.risk === 'conservative')).toBe(true);
    expect(result.some(b => b.risk === 'moderate')).toBe(true);
    expect(result.some(b => b.risk === 'aggressive')).toBe(true);
  });
});

// ─── Score attached to filtered results ──────────────────────────────────────

describe('getFiltered — score attached', () => {
  test('each returned bond has a numeric score', () => {
    const result = getFiltered(BONDS, 100000, 12, 'moderate');
    result.forEach(b => {
      expect(typeof b.score).toBe('number');
      expect(b.score).toBeGreaterThanOrEqual(0);
    });
  });

  test('HDFC Ltd (dur=12, risk=conservative) vs 12M + moderate → score = 40 + 10 = 50', () => {
    const result = getFiltered([BONDS[0]], 100000, 12, 'moderate');
    expect(result[0].score).toBe(50);
  });
});

// ─── Sort modes ───────────────────────────────────────────────────────────────

describe('sorted', () => {
  const testBonds = [
    { id: 1, ret: 8.5,  rs: 1, score: 65 },
    { id: 2, ret: 13.0, rs: 4, score: 50 },
    { id: 3, ret: 11.5, rs: 2, score: 40 },
    { id: 4, ret: 15.5, rs: 7, score: 22 },
    { id: 5, ret: 7.5,  rs: 1, score: 10 },
  ];

  // MATCH-11
  test('sort: match (default) — descending by score', () => {
    const result = sorted(testBonds, 'match');
    expect(result.map(b => b.score)).toEqual([65, 50, 40, 22, 10]);
  });

  // MATCH-12
  test('sort: high — descending by ret', () => {
    const result = sorted(testBonds, 'high');
    expect(result.map(b => b.ret)).toEqual([15.5, 13.0, 11.5, 8.5, 7.5]);
  });

  // MATCH-13
  test('sort: low — ascending by ret', () => {
    const result = sorted(testBonds, 'low');
    expect(result.map(b => b.ret)).toEqual([7.5, 8.5, 11.5, 13.0, 15.5]);
  });

  // MATCH-14
  test('sort: safe — ascending by rs', () => {
    const result = sorted(testBonds, 'safe');
    expect(result.map(b => b.rs)).toEqual([1, 1, 2, 4, 7]);
  });

  test('sort does not mutate the original array', () => {
    const original = [...testBonds];
    sorted(testBonds, 'high');
    expect(testBonds).toEqual(original);
  });
});

// ─── Full pipeline integration ────────────────────────────────────────────────

describe('Full pipeline: filter → score → sort', () => {
  test('12M + Moderate + ₹10K returns correct top result', () => {
    const filtered = getFiltered(BONDS, 10000, 12, 'moderate');
    const result = sorted(filtered, 'match');

    // Expect non-empty results
    expect(result.length).toBeGreaterThan(0);

    // Top result should have the highest score
    for (let i = 1; i < result.length; i++) {
      expect(result[0].score).toBeGreaterThanOrEqual(result[i].score);
    }
  });

  test('6M + Conservative + ₹25K excludes bonds with min > ₹25K', () => {
    const result = getFiltered(BONDS, 25000, 6, 'conservative');
    result.forEach(b => expect(b.min).toBeLessThanOrEqual(25000));
  });

  test('2Y+ + Aggressive + ₹1L excludes conservative bonds', () => {
    const result = getFiltered(BONDS, 100000, 24, 'aggressive');
    expect(result.some(b => b.risk === 'conservative')).toBe(false);
  });

  test('very low amount (₹9,999) returns no bonds', () => {
    const result = getFiltered(BONDS, 9999, 12, 'moderate');
    expect(result.length).toBe(0);
  });

  test('very high amount (₹50L) includes all bonds (amount filter passes all)', () => {
    const result = getFiltered(BONDS, 5000000, null, null);
    expect(result.length).toBe(BONDS.length);
  });

  test('results page top-5 slice', () => {
    const filtered = getFiltered(BONDS, 500000, 12, 'moderate');
    const result = sorted(filtered, 'match');
    const topFive = result.slice(0, 5);
    expect(topFive.length).toBeLessThanOrEqual(5);
  });
});

// ─── Fallback / no-match top picks ────────────────────────────────────────────

describe('getTopPicksForRisk (fallback for no-match state)', () => {
  /**
   * When duration filter yields 0 results, the UI shows top 3 bonds
   * by ret for the selected risk tier (dropping the duration filter).
   */
  function getTopPicksForRisk(bonds, amount, riskTier) {
    return bonds
      .filter(b => {
        if (b.min > amount) return false;
        if (riskTier !== null && Math.abs(RISK_RANK[b.risk] - RISK_RANK[riskTier]) > 1) return false;
        return true;
      })
      .sort((a, b) => b.ret - a.ret)
      .slice(0, 3);
  }

  test('returns max 3 bonds', () => {
    const picks = getTopPicksForRisk(BONDS, 100000, 'moderate');
    expect(picks.length).toBeLessThanOrEqual(3);
  });

  test('returns bonds sorted by ret descending', () => {
    const picks = getTopPicksForRisk(BONDS, 100000, 'moderate');
    for (let i = 1; i < picks.length; i++) {
      expect(picks[i - 1].ret).toBeGreaterThanOrEqual(picks[i].ret);
    }
  });

  test('respects amount filter', () => {
    const picks = getTopPicksForRisk(BONDS, 10000, 'moderate');
    picks.forEach(b => expect(b.min).toBeLessThanOrEqual(10000));
  });

  test('returns empty array when no bonds pass filter', () => {
    const picks = getTopPicksForRisk(BONDS, 9999, 'aggressive');
    expect(picks.length).toBe(0);
  });
});
