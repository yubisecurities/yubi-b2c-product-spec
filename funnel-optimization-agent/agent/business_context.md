# Aspero Business Context — Funnel Optimization Agent

## About Aspero
Aspero is a **SEBI-registered Online Bond Platform Provider (OBPP)**. We enable retail
investors to directly buy and sell bonds — government securities, corporate bonds, and NCDs
(Non-Convertible Debentures). This is a considered, high-trust financial product targeting
investors who want stable, predictable returns beyond traditional FDs and mutual funds.

---

## Target Audience

### Primary (High-Value)
- **Premium Android** (Samsung Galaxy S-series, OnePlus flagship, Google Pixel, POCO F-series)
  and **iOS** (iPhone) users — device price signals disposable income and investment capacity
- **Age group**: 30–55 years — salaried professionals, business owners, HNIs with investable
  surplus looking to diversify their portfolio
- **Income profile**: ₹15L+ annual income
- **Geography**: Metro + Tier-1 cities (Mumbai, Bangalore, Delhi, Hyderabad, Pune, Chennai)
- **Behaviour**: Research-driven, high trust bar, expect smooth UX — will abandon at any friction

### Secondary (Lower Value)
- **Mid Android** (Samsung A/M-series, Redmi Note, Realme) — younger audience, lower
  investment capacity; useful for volume but lower LTV
- **Low Android** (budget devices <₹10,000) — very low conversion to actual investment;
  high drop-off at email verification and PIN setup; CAC likely exceeds LTV

---

## Why Device Tier Is a Proxy for Investment Capacity

| Tier              | Income Signal          | Expected Conv (OTP→Email) | Expected Conv (Email→PIN) |
|-------------------|------------------------|--------------------------|--------------------------|
| Premium Android   | ₹20L+ (high)           | > 70%                    | > 90%                    |
| iOS               | ₹20L+ (high)           | > 70%                    | > 90%                    |
| Mid Android       | ₹8–20L (medium)        | 40–60%                   | 80–90%                   |
| Low Android       | < ₹8L (low)            | < 20%                    | 70–80%                   |
| Web               | Mixed (often desktop)  | 30–50%                   | varies                   |

---

## Key Business Metrics to Watch

1. **Premium Android + iOS share of registrations** — should be growing toward 50%+.
   If their combined share is < 35%, acquisition channels are sending the wrong audience.

2. **Email→PIN conversion for Premium + iOS** — must stay > 90%. Any drop signals UX
   friction that disproportionately hurts the highest-value users.

3. **OTP→Email rate (new-user proxy)** — how many mobile verifications turn into new
   registrations. Low ratios on Premium/iOS indicate most traffic is returning users, not growth.

4. **SSO adoption** — Google SSO eliminates the email OTP step (a known friction point,
   especially on iOS). Target: 40%+ adoption within 30 days of launch.

5. **Registration WoW trend** — sustained weekly growth signals product-market fit expansion;
   a drop > 15% WoW warrants immediate investigation (marketing pause, product regression, etc.).

---

## Alert Priorities (Business Context)

| Priority | Condition | Reason |
|----------|-----------|--------|
| 🔴 Critical | Premium Android or iOS Email→PIN < 80% | High-value users dropping at final step — revenue impact |
| 🔴 Critical | Low + Mid Android > 75% of total signups | Acquisition channels misaligned with target audience |
| ⚠️ Warning  | Weekly registrations down > 15% WoW | Product issue, marketing pause, or seasonality |
| ⚠️ Warning  | Premium Android + iOS combined < 35% of signups | Audience quality declining |
| ⚠️ Warning  | SSO adoption stagnates after launch | UX issue with SSO flow |
| 💡 Info     | Low Android OTP→Email < 10% | Mostly returning users; negligible new acquisition here |

---

## Investment Product Context

- Bond investment is a **considered purchase** — users research, compare, and return multiple
  times before registering. Email verification is the first high-trust step; drop-off here
  often means the user wasn't confident enough to proceed.
- PIN setup is the **final onboarding gate** — drop-off at this step usually means the user
  paused their decision (not a UX failure, but a conversion opportunity to nurture via retargeting).
- **Average investment ticket**: ₹50,000–₹5,00,000. Each lost registration = significant LTV.
- **KYC follows registration** — the funnel tracked here is pre-KYC. Post-KYC drop-off is
  a separate funnel stage not yet tracked in this agent.

---

## Growth Stage Context

Aspero is in **early growth phase**:
- SSO (Google sign-in for email verification) launched ~7 days ago to reduce friction on
  iOS and Premium Android, where the OTP email flow had higher abandonment.
- Target: SSO adoption > 40% within 30 days of launch.
- Weekly registration growth target: 10–15% WoW.
- Any Premium/iOS conversion regression should be treated as P0 — these users represent
  disproportionate revenue potential.
