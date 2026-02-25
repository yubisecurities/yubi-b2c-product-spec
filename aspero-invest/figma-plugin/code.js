// ─── Aspero Invest — Figma Design Generator ─────────────────────────────────
figma.showUI(__html__, { width: 340, height: 500, title: 'Aspero Invest' });

// ─── DESIGN TOKENS — Aspero Phoenix Design System ────────────────────────────
const G = {
  // Brand greens
  main:     { r: 0.00392, g: 0.55686, b: 0.26275 },  // #018E43  Primary CTA default
  hov:      { r: 0.00392, g: 0.71765, b: 0.33725 },  // #01B756  CTA hover
  act:      { r: 0.00392, g: 0.39608, b: 0.18824 },  // #016530  CTA active/pressed
  dis:      { r: 0.65882, g: 0.97255, b: 0.83529 },  // #A8F8D5  CTA disabled
  hi:       { r: 0.00392, g: 0.83137, b: 0.39216 },  // #01D464  Special/O500 highlight
  dk:       { r: 0.102,   g: 0.235,   b: 0.204   },  // #1A3C34  Dark hero surface
  dkr:      { r: 0.051,   g: 0.122,   b: 0.086   },  // #0D1F16  Darkest hero surface
  lt:       { r: 0.78824, g: 1,       b: 0.91765 },  // #C9FFEA  SpecialWeak_O100
  // Surfaces / backgrounds
  bg:       { r: 0.94902, g: 0.95686, b: 0.96863 },  // #F2F4F7  BG2_Light_N200
  white:    { r: 1, g: 1, b: 1 },                     // BG1_Light_BW50
  bgDark:   { r: 0.06275, g: 0.09412, b: 0.15686 },  // #101828  BG1_Dark_N900
  bgDark2:  { r: 0.11373, g: 0.16078, b: 0.22353 },  // #1D2939  BG2_Dark_N800
  // Text colors
  t1:       { r: 0.06275, g: 0.09412, b: 0.15686 },  // #101828  H1_N900 / BT1_N900
  t2:       { r: 0.40000, g: 0.43922, b: 0.52157 },  // #667085  BT3_N500
  t3:       { r: 0.59608, g: 0.63529, b: 0.70196 },  // #98A2B3  BT4_N400
  // Borders
  border:   { r: 0.81569, g: 0.83529, b: 0.86667 },  // #D0D5DD  Tertiary_N300
  gray100:  { r: 0.97647, g: 0.98039, b: 0.98431 },  // #F9FAFB  BG2_N100
  // Match / tier badge colors (kept as-is — display-only)
  greatBg:  { r: 0.733, g: 1,     b: 0.831 },
  greatTxt: { r: 0.078, g: 0.325, b: 0.173 },
  goodBg:   { r: 0.996, g: 0.976, b: 0.765 },
  goodTxt:  { r: 0.471, g: 0.208, b: 0.059 },
  fairBg:   { r: 0.953, g: 0.957, b: 0.965 },
  fairTxt:  { r: 0.294, g: 0.337, b: 0.388 },
  // Rating badge colors
  rAAABg:   { r: 0.820, g: 0.980, b: 0.898 },
  rAAATxt:  { r: 0.024, g: 0.369, b: 0.275 },
  rAABg:    { r: 0.925, g: 0.906, b: 1     },
  rAATxt:   { r: 0.357, g: 0.129, b: 0.714 },
};

let HEAVY = 'Bold'; // resolved during font loading

// ─── SAMPLE DATA ─────────────────────────────────────────────────────────────
const BONDS = [
  { name: 'HDFC Ltd',         abbr: 'HD', cat: 'Housing Finance', rating: 'AAA', ret: '8.50',  dur: '12 Mo', min: 'Rs.10K',  tier: 'great', earn: 'Rs.8,500'  },
  { name: 'Sundaram Finance', abbr: 'SF', cat: 'NBFC',            rating: 'AA+', ret: '9.80',  dur: '12 Mo', min: 'Rs.10K',  tier: 'great', earn: 'Rs.9,800'  },
  { name: 'Shriram Finance',  abbr: 'SH', cat: 'NBFC',            rating: 'AA+', ret: '11.50', dur: '12 Mo', min: 'Rs.10K',  tier: 'good',  earn: 'Rs.11,500' },
  { name: 'Muthoot Finance',  abbr: 'MF', cat: 'Gold Finance',    rating: 'AA',  ret: '12.00', dur: '18 Mo', min: 'Rs.10K',  tier: 'good',  earn: 'Rs.18,000' },
  { name: 'Bajaj Finance',    abbr: 'BF', cat: 'NBFC',            rating: 'AAA', ret: '9.10',  dur: '24 Mo', min: 'Rs.25K',  tier: 'fair',  earn: 'Rs.18,200' },
];

// ─── FONT LOADING ────────────────────────────────────────────────────────────
// Aspero design system uses Sofia Pro. Falls back to Inter if unavailable in Figma.
let FONT_FAMILY = 'Inter';

async function loadFonts() {
  // Try Sofia Pro first (official Aspero / Phoenix design system font)
  try {
    for (const s of ['Regular', 'Medium', 'SemiBold', 'Bold', 'Black']) {
      await figma.loadFontAsync({ family: 'Sofia Pro', style: s });
    }
    FONT_FAMILY = 'Sofia Pro';
    HEAVY = 'Black';
    return;
  } catch (_) {}
  // Fallback: Inter
  for (const style of ['Regular', 'Medium', 'Semi Bold', 'Bold']) {
    await figma.loadFontAsync({ family: 'Inter', style });
  }
  for (const style of ['Extra Bold', 'Bold']) {
    try {
      await figma.loadFontAsync({ family: 'Inter', style });
      HEAVY = style;
      return;
    } catch (_) { /* try next */ }
  }
}

// ─── PRIMITIVE HELPERS ───────────────────────────────────────────────────────
const sf = (color, opacity = 1) => [{ type: 'SOLID', color, opacity }];

function mkRect(w, h, color, radius = 0) {
  const r = figma.createRectangle();
  r.resize(Math.max(w, 1), Math.max(h, 1));
  r.fills = sf(color);
  if (radius) r.cornerRadius = radius;
  return r;
}

async function mkTxt(str, size, style, color, opacity = 1) {
  const t = figma.createText();
  t.fontName = { family: FONT_FAMILY, style };
  t.characters = String(str);
  t.fontSize = size;
  t.fills = sf(color, opacity);
  return t;
}

// Fixed-size clipping frame
function mkFr(name, w, h, bg) {
  const f = figma.createFrame();
  f.name = name;
  f.resize(Math.max(w, 1), Math.max(h, 1));
  f.fills = bg ? sf(bg) : [];
  f.clipsContent = true;
  return f;
}

// VERTICAL auto-layout — grows in Y direction, width is counter axis
function vAuto(name, gap, pLR, pTB, bg) {
  const f = figma.createFrame();
  f.name = name;
  f.layoutMode = 'VERTICAL';
  f.itemSpacing = gap;
  f.paddingLeft = pLR; f.paddingRight = pLR;
  f.paddingTop = pTB;  f.paddingBottom = pTB;
  f.primaryAxisSizingMode = 'AUTO';   // height = sum of children
  f.counterAxisSizingMode = 'AUTO';   // width = widest child (changed by fixW)
  f.fills = bg ? sf(bg) : [];
  return f;
}

// HORIZONTAL auto-layout — grows in X direction, height is counter axis
function hAuto(name, gap, pLR, pTB, bg) {
  const f = figma.createFrame();
  f.name = name;
  f.layoutMode = 'HORIZONTAL';
  f.itemSpacing = gap;
  f.paddingLeft = pLR; f.paddingRight = pLR;
  f.paddingTop = pTB;  f.paddingBottom = pTB;
  f.primaryAxisSizingMode = 'AUTO';   // width = sum of children (changed by fixW)
  f.counterAxisSizingMode = 'AUTO';   // height = tallest child
  f.counterAxisAlignItems = 'CENTER';
  f.fills = bg ? sf(bg) : [];
  return f;
}

// Fix a frame to a specific width regardless of layout direction
function fixW(f, w) {
  w = Math.max(w, 1);
  if (f.layoutMode === 'VERTICAL') {
    // counter axis = X = width
    f.counterAxisSizingMode = 'FIXED';
  } else {
    // primary axis = X = width
    f.primaryAxisSizingMode = 'FIXED';
  }
  f.resize(w, Math.max(f.height, 1));
}

// ─── COMPONENTS ──────────────────────────────────────────────────────────────
async function mkPill(label, active) {
  const p = hAuto('Pill', 0, 12, 8, active ? G.main : G.gray100);
  p.cornerRadius = 100;
  p.strokes = sf(active ? G.main : G.border);
  p.strokeWeight = 1.5;
  p.strokeAlign = 'INSIDE';
  p.appendChild(await mkTxt(label, 13, 'Semi Bold', active ? G.white : G.t1));
  return p;
}

async function mkBadge(label, bg, color, radius = 100) {
  const b = hAuto('Badge', 0, 10, 4, bg);
  b.cornerRadius = radius;
  b.appendChild(await mkTxt(label, 11, 'Bold', color));
  return b;
}

async function mkRating(rating) {
  const isAAA = rating === 'AAA';
  return mkBadge(rating, isAAA ? G.rAAABg : G.rAABg, isAAA ? G.rAAATxt : G.rAATxt, 6);
}

async function mkBondCard(bond, W) {
  // Outer card — vertical, padded on all sides
  const card = vAuto('Bond - ' + bond.name, 0, 20, 20, G.white);
  card.cornerRadius = 20;
  card.strokes = sf(G.border);
  card.strokeWeight = 1.5;
  card.strokeAlign = 'INSIDE';
  fixW(card, W);

  const inner = W - 40; // available width after padding

  // ── Row 1: avatar + match badge ──────────────────────────────────────────
  // Use a fixed-size clip frame to manually position avatar (left) and badge (right)
  const topFr = mkFr('TopRow', inner, 42, null);
  const abbr = mkFr('Abbr', 42, 42, G.lt);
  abbr.cornerRadius = 12;
  const abbrT = await mkTxt(bond.abbr, 14, HEAVY, G.main);
  abbrT.x = Math.round((42 - abbrT.width) / 2);
  abbrT.y = Math.round((42 - abbrT.height) / 2);
  abbr.appendChild(abbrT);
  topFr.appendChild(abbr);

  const tm = { great:{bg:G.greatBg,txt:G.greatTxt,lbl:'Great Match'}, good:{bg:G.goodBg,txt:G.goodTxt,lbl:'Good Match'}, fair:{bg:G.fairBg,txt:G.fairTxt,lbl:'Fair Match'} }[bond.tier] || {bg:G.fairBg,txt:G.fairTxt,lbl:'Fair Match'};
  const badge = await mkBadge(tm.lbl, tm.bg, tm.txt);
  topFr.appendChild(badge);
  badge.x = inner - badge.width;
  badge.y = Math.round((42 - badge.height) / 2);
  card.appendChild(topFr);

  // ── Row 2: name, category ─────────────────────────────────────────────────
  card.appendChild(await mkTxt(bond.name, 15, 'Bold', G.t1));
  card.appendChild(await mkTxt(bond.cat, 12, 'Regular', G.t2));

  // ── Gap between category and stats row ────────────────────────────────────
  card.appendChild(mkRect(inner, 8, G.white));

  // ── Stats row: yield % | duration | rating — all on one line ──────────────
  const statsRow = hAuto('Stats', 0, 0, 0);
  statsRow.counterAxisAlignItems = 'CENTER';
  fixW(statsRow, inner);

  // Col 1 — Yield
  const yCol = vAuto('YC', 3, 0, 8);
  yCol.counterAxisAlignItems = 'MIN';
  yCol.appendChild(await mkTxt(bond.ret + '%', 26, HEAVY, G.main));
  yCol.appendChild(await mkTxt('Expected Returns', 11, 'Regular', G.t2));
  yCol.layoutGrow = 1;
  statsRow.appendChild(yCol);

  statsRow.appendChild(mkRect(1, 40, G.border)); // divider

  // Col 2 — Duration
  const dCol = vAuto('DC', 3, 16, 8);
  dCol.counterAxisAlignItems = 'MIN';
  dCol.appendChild(await mkTxt(bond.dur, 14, 'Bold', G.t1));
  dCol.appendChild(await mkTxt('Duration', 11, 'Regular', G.t2));
  dCol.layoutGrow = 1;
  statsRow.appendChild(dCol);

  statsRow.appendChild(mkRect(1, 40, G.border)); // divider

  // Col 3 — Rating
  const rCol = vAuto('RC', 3, 16, 8);
  rCol.counterAxisAlignItems = 'MIN';
  rCol.appendChild(await mkRating(bond.rating));
  rCol.appendChild(await mkTxt('Rating', 11, 'Regular', G.t2));
  rCol.layoutGrow = 1;
  statsRow.appendChild(rCol);

  card.appendChild(statsRow);
  card.appendChild(mkRect(inner, 12, G.white)); // gap between stats and bottom row

  // ── Row 5: Est. Earnings (green card, left) + compact CTA (right) ──────────
  const bottomRow = hAuto('Bottom', 12, 0, 0);
  bottomRow.counterAxisAlignItems = 'CENTER';
  fixW(bottomRow, inner);

  // Green-tinted earnings card — draws the eye to the key value
  const earnCol = vAuto('EL', 3, 12, 10, G.lt);
  earnCol.cornerRadius = 12;
  earnCol.appendChild(await mkTxt('Est. Earnings', 11, 'Semi Bold', G.main));
  earnCol.appendChild(await mkTxt(bond.earn, 15, 'Bold', G.t1));
  earnCol.layoutGrow = 1; // fill remaining width, pushing CTA to the right

  const cta = hAuto('CTA', 0, 20, 12, G.main);
  cta.primaryAxisAlignItems = 'CENTER';
  cta.cornerRadius = 6;  // Always 6px per Phoenix design system
  cta.appendChild(await mkTxt('Invest Now  ->', 13, 'Bold', G.white));

  bottomRow.appendChild(earnCol);
  bottomRow.appendChild(cta);
  card.appendChild(bottomRow);

  return card;
}

async function mkEarningsBar(W) {
  const bar = mkFr('EarningsBar', W, 68, G.dkr);

  async function ebItem(label, val, color, x) {
    const col = vAuto('EB', 4, 0, 0);
    col.appendChild(await mkTxt(label, 11, 'Semi Bold', G.white, 0.45));
    col.appendChild(await mkTxt(val, 16, 'Bold', color));
    col.x = x;
    col.y = Math.round((68 - col.height) / 2);
    bar.appendChild(col);
  }

  const quarter = Math.round(W / 4);
  await ebItem('Invested',     'Rs.1,00,000',  G.white, 20);
  await ebItem('Est. Returns', 'Rs.8,500',     G.hi,    quarter);
  await ebItem('Total Value',  'Rs.1,08,500',  G.hi,    quarter * 2);
  await ebItem('Bonds',        '5',            G.white, quarter * 3);
  return bar;
}

// ─── NAV BAR ─────────────────────────────────────────────────────────────────
async function mkNavBar(W) {
  const nav = mkFr('NavBar', W, 62, G.dkr);

  const logo = await mkTxt('aspero.', 21, HEAVY, G.white);
  logo.x = 20;
  logo.y = Math.round((62 - logo.height) / 2);
  nav.appendChild(logo);

  const badge = await mkBadge('KYC Verified', G.hi, G.hi);
  badge.fills = sf(G.hi, 0.12);
  badge.strokes = sf(G.hi, 0.25);
  badge.strokeWeight = 1;
  badge.strokeAlign = 'INSIDE';
  badge.x = W - badge.width - 16;
  badge.y = Math.round((62 - badge.height) / 2);
  nav.appendChild(badge);

  return nav;
}

// ─── HERO ────────────────────────────────────────────────────────────────────
async function mkHero(W) {
  const hero = mkFr('Hero', W, 185, G.dkr);

  const overlay = mkRect(W, 185, { r: 0.06, g: 0.16, b: 0.11 });
  overlay.opacity = 0.55;
  hero.appendChild(overlay);

  // tag
  const tagBg = mkRect(130, 27, G.hi, 100);
  tagBg.opacity = 0.1; tagBg.x = 20; tagBg.y = 26;
  hero.appendChild(tagBg);
  const tagT = await mkTxt('Discover Bonds', 12, 'Semi Bold', G.hi);
  tagT.x = 30; tagT.y = 33;
  hero.appendChild(tagT);

  const h1 = await mkTxt('Find Bonds That', 26, HEAVY, G.white);
  h1.x = 20; h1.y = 66;
  hero.appendChild(h1);

  const h2 = await mkTxt('Match Your Goals', 26, HEAVY, G.hi);
  h2.x = 20; h2.y = 96;
  hero.appendChild(h2);

  const sub = await mkTxt('Set your preferences and we show bonds matched for you.', 13, 'Regular', G.white, 0.45);
  sub.x = 20; sub.y = 148;
  hero.appendChild(sub);

  return hero;
}

// ─── WIDGET CARD (controls) ───────────────────────────────────────────────────
async function mkWidgetCard(W) {
  const card = vAuto('WidgetCard', 26, 26, 26, G.white);
  card.cornerRadius = 20;
  fixW(card, W);
  const innerW = W - 52; // available width inside card padding (26px each side)

  // Amount section
  const amtSec = vAuto('Amt', 12, 0, 0);
  amtSec.appendChild(await mkTxt('INVESTMENT AMOUNT', 11, 'Bold', G.t2));
  amtSec.appendChild(await mkTxt('Rs. 25,00,000', 34, HEAVY, G.t1));

  // Slider visual — frame is 24px tall; track is 8px, centered at y=8
  const sw = W - 52;
  const slFr = mkFr('Slider', sw, 24, null);
  const slTrack = mkRect(sw, 8, { r: 0.91, g: 0.92, b: 0.91 }, 4);
  slTrack.y = 8; // vertically center 8px track in 24px frame
  slFr.appendChild(slTrack);
  const slFill = mkRect(Math.round(sw * 0.50), 8, G.main, 4);
  slFill.y = 8;
  slFr.appendChild(slFill);
  const thumb = mkRect(24, 24, G.white, 12);
  thumb.x = Math.round(sw * 0.50) - 12;
  // thumb y=0 fills the full 24px frame height — track runs through its centre
  thumb.strokes = sf(G.main); thumb.strokeWeight = 3; thumb.strokeAlign = 'INSIDE';
  slFr.appendChild(thumb);
  amtSec.appendChild(slFr);

  // Markers
  const markFr = mkFr('Markers', sw, 18, null);
  const mL = await mkTxt('Rs. 10K', 11, 'Medium', { r: 0.61, g: 0.64, b: 0.69 });
  const mR = await mkTxt('Rs. 50L', 11, 'Medium', { r: 0.61, g: 0.64, b: 0.69 });
  mL.x = 0; mL.y = 0; mR.x = sw - mR.width; mR.y = 0;
  markFr.appendChild(mL); markFr.appendChild(mR);
  amtSec.appendChild(markFr);

  // Quick chips — start from 10K, single line (no wrap)
  const chipRow = hAuto('Chips', 8, 0, 0);
  chipRow.counterAxisAlignItems = 'MIN';
  for (const a of ['10K', '50K', '1L', '5L']) {
    const c = hAuto('C', 0, 14, 6, G.gray100);
    c.cornerRadius = 100;
    c.appendChild(await mkTxt('Rs.' + a, 12, 'Semi Bold', G.t2));
    chipRow.appendChild(c);
  }
  amtSec.appendChild(chipRow);
  card.appendChild(amtSec);
  card.appendChild(mkRect(W - 52, 1, G.border));

  // Duration
  const durSec = vAuto('Dur', 10, 0, 0);
  durSec.appendChild(await mkTxt('DURATION', 11, 'Bold', G.t2));
  const dp = hAuto('DP', 8, 0, 0);
  dp.counterAxisAlignItems = 'MIN';
  dp.layoutWrap = 'WRAP';
  fixW(dp, innerW);
  for (const [l,a] of [['6 Mo',false],['12 Mo',true],['18 Mo',false],['24 Mo',false]]) dp.appendChild(await mkPill(l,a));
  durSec.appendChild(dp);
  card.appendChild(durSec);

  // Risk cards (Duration → Risk is the full selection flow; no separate Returns section)
  const riskSec = vAuto('Risk', 10, 0, 0);
  riskSec.appendChild(await mkTxt('RISK APPETITE', 11, 'Bold', G.t2));
  const rr = hAuto('RR', 10, 0, 0);
  rr.counterAxisAlignItems = 'MIN';
  fixW(rr, innerW); // constrain row to available inner width
  const rcW = Math.floor((innerW - 20) / 3); // equal share: innerW minus 2×gap(10)
  const riskDefs = [
    {
      name: 'Conservative', desc: 'Capital safety first.', retRange: '7.5–10% p.a.', act: true,
      bg:  { r: 0.925, g: 0.992, b: 0.961 }, // #ECFDF5
      bd:  { r: 0.153, g: 0.682, b: 0.376 }, // #27AE60
      txt: { r: 0.024, g: 0.369, b: 0.275 }, // #065F46
    },
    {
      name: 'Moderate', desc: 'Balanced risk-reward.', retRange: '10–13% p.a.', act: false,
      bg:  { r: 1,     g: 0.984, b: 0.918 }, // #FFFBEB
      bd:  { r: 0.961, g: 0.620, b: 0.043 }, // #F59E0B
      txt: { r: 0.573, g: 0.251, b: 0.035 }, // #92400E
    },
    {
      name: 'Aggressive', desc: 'Higher returns, higher risk.', retRange: '13–16% p.a.', act: false,
      bg:  { r: 0.961, g: 0.953, b: 1.0   }, // #F5F3FF violet-50
      bd:  { r: 0.486, g: 0.227, b: 0.929 }, // #7C3AED violet-600
      txt: { r: 0.298, g: 0.114, b: 0.584 }, // #4C1D95 violet-900
    },
  ];
  for (const r of riskDefs) {
    const rc = vAuto('RC-' + r.name, 5, 12, 14, r.bg);
    rc.cornerRadius = 14;
    rc.strokes = sf(r.bd);
    rc.strokeWeight = r.act ? 2 : 1.5;
    rc.strokeAlign = 'INSIDE';
    rc.counterAxisAlignItems = 'CENTER';
    fixW(rc, rcW);
    rc.appendChild(await mkTxt(r.name, 12, 'Bold',    r.txt));
    rc.appendChild(await mkTxt(r.desc, 10, 'Regular', r.txt, 0.7));
    // Return range badge — always visible per PRD (green pill)
    const retBadge = await mkBadge(r.retRange, G.lt, G.main, 6);
    rc.appendChild(retBadge);
    rr.appendChild(rc);
  }
  riskSec.appendChild(rr);
  card.appendChild(riskSec);

  return card;
}

// ─── WIDGET FOOTER ───────────────────────────────────────────────────────────
async function mkWidgetFooter(W) {
  const footer = mkFr('WidgetFooter', W, 72, G.dkr);

  const info = vAuto('Info', 4, 0, 0);
  info.appendChild(await mkTxt('Matching bonds', 12, 'Regular', G.white, 0.5));
  const cr = hAuto('CR', 6, 0, 0);
  cr.appendChild(await mkTxt('12', 22, HEAVY, G.white));
  cr.appendChild(await mkTxt('found', 14, 'Regular', G.white, 0.5));
  info.appendChild(cr);
  info.x = 24; info.y = Math.round((72 - info.height) / 2);
  footer.appendChild(info);

  const btn = hAuto('Btn', 0, 20, 12, G.main);
  btn.cornerRadius = 6;  // Always 6px per Phoenix design system
  btn.appendChild(await mkTxt('Show Matches ->', 14, 'Bold', G.white));
  btn.x = W - btn.width - 20;
  btn.y = Math.round((72 - btn.height) / 2);
  footer.appendChild(btn);

  return footer;
}

// ─── FLOATING CTA ─────────────────────────────────────────────────────────────
async function mkFloatingCTA(W) {
  const bar = mkFr('FloatingCTA', W, 84, G.dkr);

  // Left: match count info — white text on dark background
  const info = vAuto('Info', 4, 0, 0);
  info.appendChild(await mkTxt('Showing top 5', 13, 'Semi Bold', G.white));
  info.appendChild(await mkTxt('12 total matches', 11, 'Regular', G.white, 0.5));
  info.x = 24;
  info.y = Math.round((84 - info.height) / 2);
  bar.appendChild(info);

  // Right: larger View All CTA button
  const btn = hAuto('ViewAllBtn', 0, 28, 18, G.main);
  btn.cornerRadius = 6;  // Always 6px per Phoenix design system
  btn.appendChild(await mkTxt('View All  ->', 14, 'Bold', G.white));
  btn.x = W - btn.width - 24;
  btn.y = Math.round((84 - btn.height) / 2);
  bar.appendChild(btn);

  return bar;
}

// ─── ALL BONDS NAV ───────────────────────────────────────────────────────────
async function mkAllBondsNav(W) {
  const nav = mkFr('AllBondsNav', W, 56, G.dkr);
  const back = await mkTxt('<- Back to filters', 14, 'Semi Bold', G.white);
  back.x = 20; back.y = Math.round((56 - back.height) / 2);
  nav.appendChild(back);
  const sort = await mkTxt('Best Match  v', 12, 'Semi Bold', G.white, 0.7);
  sort.x = W - sort.width - 20; sort.y = Math.round((56 - sort.height) / 2);
  nav.appendChild(sort);
  return nav;
}

// ─── FILTER CHIPS ─────────────────────────────────────────────────────────────
async function mkFilterChips(W) {
  const row = hAuto('Chips', 8, 20, 10);
  fixW(row, W);
  for (const lbl of ['Rs.10,000 ✎', '12 Months', 'Conservative']) {
    const c = hAuto('C', 0, 12, 5, G.dkr);
    c.cornerRadius = 100;
    c.appendChild(await mkTxt(lbl, 12, 'Semi Bold', G.white, 0.75));
    row.appendChild(c);
  }
  return row;
}

// ─── MATCH GROUP HEADER ───────────────────────────────────────────────────────
async function mkGroupHdr(label, count, bg, color, W) {
  const hdr = mkFr('GroupHdr', W, 44, bg);
  hdr.appendChild(await mkTxt(label, 14, 'Bold', color));
  const cnt = await mkBadge(count + ' bonds', { r: 1, g: 1, b: 1 }, color);
  cnt.fills = sf(color, 0.12);
  hdr.children[0].x = 20;
  hdr.children[0].y = Math.round((44 - hdr.children[0].height) / 2);
  cnt.x = W - cnt.width - 20;
  cnt.y = Math.round((44 - cnt.height) / 2);
  hdr.appendChild(cnt);
  return hdr;
}

// ─── RESULTS HEADER ──────────────────────────────────────────────────────────
async function mkResultsHeader(W) {
  const hdr = mkFr('ResultsHdr', W, 56, null);

  const titleRow = hAuto('TR', 10, 0, 0);
  titleRow.appendChild(await mkTxt('Matching Bonds', 20, HEAVY, G.t1));
  const cp = hAuto('CP', 0, 12, 4, G.lt);
  cp.cornerRadius = 100; cp.appendChild(await mkTxt('12', 13, 'Bold', G.main));
  titleRow.appendChild(cp);
  titleRow.x = 20; titleRow.y = Math.round((56 - titleRow.height) / 2);
  hdr.appendChild(titleRow);

  const sort = hAuto('Sort', 4, 12, 8, G.white);
  sort.cornerRadius = 10; sort.strokes = sf(G.border); sort.strokeWeight = 1.5; sort.strokeAlign = 'INSIDE';
  sort.appendChild(await mkTxt('Best Match  v', 12, 'Semi Bold', G.t1));
  sort.x = W - sort.width - 20; sort.y = Math.round((56 - sort.height) / 2);
  hdr.appendChild(sort);

  return hdr;
}

// ─── BUILDER: MOBILE MAIN WIDGET ─────────────────────────────────────────────
async function buildMobileWidget(offsetX) {
  const W = 390;
  const screen = vAuto('Mobile - Main Widget', 0, 0, 0, G.bg);
  screen.x = offsetX; screen.y = 0;
  fixW(screen, W);
  figma.currentPage.appendChild(screen); // on canvas before populating

  screen.appendChild(await mkNavBar(W));
  screen.appendChild(await mkHero(W));

  const wrap = vAuto('WW', 0, 20, 0);
  fixW(wrap, W);
  wrap.appendChild(await mkWidgetCard(W - 40));
  screen.appendChild(wrap);

  screen.appendChild(await mkWidgetFooter(W));

  return screen;
}

// ─── SAVE STRIP ──────────────────────────────────────────────────────────────
// Dark-gradient "Get alerts" strip shown on Results screen (between bonds & View All)
async function mkSaveStrip(W) {
  const stripW = W - 40;
  // Outer card — horizontal auto-layout, dark background matching hero
  const strip = hAuto('SaveStrip', 12, 20, 16, { r: 0.051, g: 0.122, b: 0.086 });
  strip.cornerRadius = 18;
  strip.strokes = sf(G.hi, 0.18);
  strip.strokeWeight = 1;
  strip.strokeAlign = 'INSIDE';
  fixW(strip, stripW);

  // Bell icon box
  const iconBox = mkRect(46, 46, G.dk, 13);
  strip.appendChild(iconBox);

  // Text column (grows to fill available space)
  const textCol = vAuto('Txt', 3, 0, 0);
  textCol.layoutGrow = 1;
  textCol.appendChild(await mkTxt('Get alerts for new matching bonds', 13, 'Bold', G.white));
  textCol.appendChild(await mkTxt('Free account · 30 seconds to set up', 11, 'Regular', G.white, 0.45));
  strip.appendChild(textCol);

  // CTA button
  const cta = hAuto('CTA', 0, 14, 10, G.hi);
  cta.cornerRadius = 6;  // Always 6px per Phoenix design system
  cta.appendChild(await mkTxt('Sign up free ->', 12, 'Bold', G.dkr));
  strip.appendChild(cta);

  return strip;
}

// ─── BUILDER: MOBILE BOND RESULTS ────────────────────────────────────────────
async function buildMobileResults(offsetX) {
  const W = 390;
  const screen = vAuto('Mobile - Bond Results', 0, 0, 0, G.bg);
  screen.x = offsetX; screen.y = 0;
  fixW(screen, W);
  figma.currentPage.appendChild(screen);

  screen.appendChild(await mkNavBar(W));
  screen.appendChild(await mkResultsHeader(W));
  screen.appendChild(await mkFilterChips(W));

  const bondsWrap = vAuto('Bonds', 16, 20, 20);
  fixW(bondsWrap, W);
  for (const bond of BONDS.slice(0, 3)) {
    bondsWrap.appendChild(await mkBondCard(bond, W - 40));
  }
  // Save strip — between bond cards and View All row
  bondsWrap.appendChild(await mkSaveStrip(W));
  screen.appendChild(bondsWrap);

  screen.appendChild(await mkFloatingCTA(W));

  return screen;
}

// ─── BUILDER: MOBILE ALL BONDS ────────────────────────────────────────────────
async function buildMobileAllBonds(offsetX) {
  const W = 390;
  const screen = vAuto('Mobile - All Bonds', 0, 0, 0, G.bg);
  screen.x = offsetX; screen.y = 0;
  fixW(screen, W);
  figma.currentPage.appendChild(screen);

  screen.appendChild(await mkAllBondsNav(W));
  screen.appendChild(await mkFilterChips(W));

  async function addGroup(bonds, lbl, bg, color) {
    if (!bonds.length) return;
    screen.appendChild(await mkGroupHdr(lbl, bonds.length, bg, color, W));
    const grp = vAuto('GRP', 16, 20, 16);
    fixW(grp, W);
    for (const b of bonds) grp.appendChild(await mkBondCard(b, W - 40));
    screen.appendChild(grp);
  }

  await addGroup(BONDS.filter(b => b.tier === 'great'), 'Great Match', G.greatBg, G.greatTxt);
  await addGroup(BONDS.filter(b => b.tier === 'good'),  'Good Match',  G.goodBg,  G.goodTxt);
  await addGroup(BONDS.filter(b => b.tier === 'fair'),  'Fair Match',  G.fairBg,  G.fairTxt);

  return screen;
}

// ─── BUILDER: DESKTOP ────────────────────────────────────────────────────────
async function buildDesktop(offsetX) {
  const W = 1440, H = 900;
  const screen = mkFr('Desktop - Full Page', W, H, G.bg);
  screen.x = offsetX; screen.y = 0;
  figma.currentPage.appendChild(screen);

  screen.appendChild(await mkNavBar(W));
  const hero = await mkHero(W);
  hero.y = 62; screen.appendChild(hero);

  const widgetW = 860;
  const widget = await mkWidgetCard(widgetW);
  widget.x = Math.round((W - widgetW) / 2);
  widget.y = 62 + 185 - 32;
  screen.appendChild(widget);

  return screen;
}

// ─── BUILDER: COMPONENTS ─────────────────────────────────────────────────────
async function buildComponents(offsetX) {
  const W = 800;
  const frame = vAuto('Component Samples', 32, 40, 40, G.bg);
  frame.x = offsetX; frame.y = 0;
  fixW(frame, W);
  figma.currentPage.appendChild(frame);

  frame.appendChild(await mkTxt('Pills', 16, 'Bold', G.t1));
  const pr = hAuto('P', 8, 0, 0);
  for (const [l,a] of [['6 Mo',false],['12 Mo',true],['10-12%',true],['14%+',false]]) pr.appendChild(await mkPill(l,a));
  frame.appendChild(pr);

  frame.appendChild(await mkTxt('Match Badges', 16, 'Bold', G.t1));
  const br = hAuto('B', 10, 0, 0);
  br.appendChild(await mkBadge('Great Match', G.greatBg, G.greatTxt));
  br.appendChild(await mkBadge('Good Match',  G.goodBg,  G.goodTxt));
  br.appendChild(await mkBadge('Fair Match',  G.fairBg,  G.fairTxt));
  frame.appendChild(br);

  frame.appendChild(await mkTxt('Bond Card', 16, 'Bold', G.t1));
  frame.appendChild(await mkBondCard(BONDS[0], 340));

  frame.appendChild(await mkTxt('Earnings Bar', 16, 'Bold', G.t1));
  frame.appendChild(await mkEarningsBar(W - 80));

  return frame;
}

// ─── BUILDER: NO-MATCH STATE ──────────────────────────────────────────────────
// Shows when no bonds match the selected filters; surfaces top picks + adjust CTA
async function buildNoMatch(offsetX) {
  const W = 390;
  const screen = vAuto('Mobile - No Match State', 0, 0, 0, G.bg);
  screen.x = offsetX; screen.y = 0;
  fixW(screen, W);
  figma.currentPage.appendChild(screen);

  screen.appendChild(await mkNavBar(W));
  screen.appendChild(await mkResultsHeader(W));
  screen.appendChild(await mkFilterChips(W));

  const content = vAuto('NoMatchContent', 16, 20, 36);
  fixW(content, W);
  content.counterAxisAlignItems = 'CENTER';

  // Icon + heading
  const icon = await mkTxt('🔍', 38, 'Regular', G.t2);
  content.appendChild(icon);

  const title = await mkTxt('No exact matches right now', 20, HEAVY, G.t1);
  content.appendChild(title);

  const sub = await mkTxt('Here are the top-rated bonds you can invest in today.', 14, 'Regular', G.t2);
  content.appendChild(sub);

  // "Top picks for you" divider
  const divRow = mkFr('Divider', W - 40, 24, null);
  const divLine = mkRect(W - 40, 1, G.border);
  divLine.y = 11;
  divRow.appendChild(divLine);
  const divLabel = await mkTxt('TOP PICKS FOR YOU', 10, 'Bold', G.t2);
  divLabel.x = Math.round((W - 40 - divLabel.width) / 2);
  divLabel.y = 6;
  divRow.appendChild(divLabel);
  content.appendChild(divRow);

  // 2 sample bond cards (top picks fallback)
  for (const bond of BONDS.slice(0, 2)) {
    content.appendChild(await mkBondCard(bond, W - 40));
  }

  // Adjust criteria button
  const adjBtn = hAuto('AdjBtn', 8, 20, 13, G.white);
  adjBtn.cornerRadius = 6;  // Always 6px per Phoenix design system
  adjBtn.strokes = sf(G.border);
  adjBtn.strokeWeight = 1.5;
  adjBtn.strokeAlign = 'INSIDE';
  adjBtn.primaryAxisAlignItems = 'CENTER';
  fixW(adjBtn, W - 40);
  adjBtn.appendChild(await mkTxt('<- Adjust my criteria', 14, 'Semi Bold', G.t2));
  content.appendChild(adjBtn);

  screen.appendChild(content);
  return screen;
}

// ─── ENTRY POINT ─────────────────────────────────────────────────────────────
figma.ui.onmessage = async (msg) => {
  if (msg.type === 'cancel') { figma.closePlugin(); return; }

  if (msg.type === 'generate') {
    const opts   = msg.options;
    const GAP    = 60;
    let cursor   = 0;
    const frames = [];

    try {
      await loadFonts();

      if (opts.mobileWidget) {
        const f = await buildMobileWidget(cursor);
        cursor += (f.width || 390) + GAP;
        frames.push(f);
      }
      if (opts.mobileResults) {
        const f = await buildMobileResults(cursor);
        cursor += (f.width || 390) + GAP;
        frames.push(f);
      }
      if (opts.mobileAllBonds) {
        const f = await buildMobileAllBonds(cursor);
        cursor += (f.width || 390) + GAP;
        frames.push(f);
      }
      if (opts.noMatch) {
        const f = await buildNoMatch(cursor);
        cursor += (f.width || 390) + GAP;
        frames.push(f);
      }
      if (opts.desktop) {
        const f = await buildDesktop(cursor);
        cursor += (f.width || 1440) + GAP;
        frames.push(f);
      }
      if (opts.components) {
        const f = await buildComponents(cursor);
        frames.push(f);
      }

      if (frames.length) figma.viewport.scrollAndZoomIntoView(frames);

      // Report success back to UI (don't auto-close — let user see result)
      figma.ui.postMessage({ type: 'done', count: frames.length });

    } catch (err) {
      // Post full error to plugin UI so it's visible
      figma.ui.postMessage({ type: 'error', text: String(err.stack || err.message || err) });
    }
  }
};
