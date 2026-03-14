# Creative Analysis — Report Format Reference

This document defines the standard format for Aspero's Google App Ad creative analysis.
Used by Claude (or `skills/creative_analysis.py` + `skills/report.py`) to produce
consistent creative reviews each week.

---

## Section Order

1. Raw Copy Table
2. Key Finding (lead insight)
3. Per-Ad Analysis
4. Cross-Ad Pattern Analysis
5. 5 Copy Angles to Test
6. Priority Fixes

---

## Section 1 — Raw Copy Table

One row per ad, sorted by impressions descending.

| Ad | Campaign | Impr | CTR | Headlines | Description 1 | Description 2 |
|---|---|---|---|---|---|---|
| 1 | [campaign_name short] | [N]K | [X]% | H1 \| H2 \| H3 | [D1 text] | [D2 text] |

**Rules:**
- Campaign name: abbreviated (PaymentSuccess / BankVerified)
- Impressions: in thousands (e.g. 627K)
- CTR: 2 decimal places with %
- Headlines: pipe-separated, bold the one that's unique/most interesting
- Show all headlines and both descriptions

---

## Section 2 — Key Finding

Lead with the single most important insight from the data — usually the CTR story.

Format:
> **"[Specific headline or copy element]" [explains / is responsible for] the CTR gap.**
>
> 1-2 paragraphs. Reference specific numbers. Don't genericize.

Example pattern:
> "Earn 9-15% Fixed Returns Today" appears only in BankVerified Ads 2 and 5. These share the
> highest CTRs in the set (2.72%, 2.70%). PaymentSuccess Ad 1 — running 89% of all impressions
> — has no yield number anywhere.
>
> The CTR story is almost entirely about this one headline. Specific yield (9-15%) outperforms
> generic benefit language every time.

---

## Section 3 — Per-Ad Analysis

For each ad, a structured block:

```
**Ad [N] — [Campaign short name] ([impr] impr, [CTR]% CTR)** — `Clarity: X/5`
- Primary value prop: [one phrase]
- Emotional hook: [aspiration | safety | returns | ease | trust | fomo | none]
- **What works:** [bullet points — reference actual copy]
- **What's missing:**
  - [specific gap 1 — e.g. "No yield number — biggest gap in the set"]
  - [specific gap 2]
```

**Clarity score guide (1–5):**
- 5 = Crystal clear what the app is, what the user gets, why install now
- 4 = Clear with one minor gap
- 3 = Understandable but generic — could be any fintech app
- 2 = Vague or passive — user can't tell what they'll get
- 1 = Misleading or confusing

**Rules for per-ad analysis:**
- Reference actual headline text, not paraphrases
- "What's missing" should be specific: "No yield number", "No SEBI trust signal", not "needs better copy"
- Emotional hook = the dominant hook; can have secondary but pick the primary one
- Explain WHY a high-CTR or low-CTR ad performed as it did — connect copy to outcome

---

## Section 4 — Cross-Ad Pattern Analysis

Numbered findings. Each one should:
- Start with the pattern in **bold**
- Explain the implication
- Reference data or specific copy

Typical patterns to check:
1. **Repeated headlines** — which headline appears in all ads? Is it table stakes or differentiated?
2. **Description quality comparison** — which campaign has stronger descriptions? Why?
3. **Best trust signal usage** — where does it appear? Should it be a headline?
4. **Duplicate creatives** — same copy in multiple ad slots wastes creative learning budget
5. **Missing angles** — what's completely absent from all ads (e.g. no competitor comparison, no FD comparison)?

---

## Section 5 — 5 Copy Angles to Test

Each angle must be currently absent or underused across the ad set.

Format per angle:

```
**Angle [N] — [Angle Name]** *(why it's worth testing — 1 line)*
- `[Headline 1 ≤30 chars]`
- `[Headline 2 ≤30 chars]`
- `[Headline 3 ≤30 chars]`
- Description: "[≤90 chars. Specific. Numbers where possible.]"
```

**Angle naming guide (pick angles that are data-driven):**
- Yield vs FD — specific return number vs bank alternative
- Zero Defaults / Trust — safety and track record
- SEBI Credibility — regulatory trust signal
- Speed to Start — time to first investment
- Portfolio Breadth — number of bonds, tenure range, issuer types
- Audience Mirror — "for salaried professionals" / "for FD investors"
- FOMO / Urgency — bond availability, limited window
- Simplicity — fewer steps than competitors

---

## Section 6 — Priority Fixes

Numbered. P0 = change this week, P1 = change next week.

Format:
```
**[N]. [Action verb] "[specific copy element]" [reason]**
Replace: [old copy]
With: [new copy option 1] / [new copy option 2] / [new copy option 3]
```

Rules:
- Always specify which exact headline/description to replace
- Give 2-3 replacement options, not just 1
- Lead with highest-impression item first (biggest impact per fix)
- Max 5 fixes — if more needed, move P1+ to next week

---

## Aspero Context (for analysis framing)

Always interpret copy through this lens:

| Dimension | Value |
|---|---|
| Product | SEBI-registered Online Bond Platform (OBPP) |
| Bond types | Government securities, corporate bonds, NCDs |
| Yield range | 8–12% p.a. (can cite 9-15% for range) |
| Audience | Salaried professionals, 30–55 years, ₹15L+ income, metro + Tier-1 |
| Investment ticket | ₹50,000 – ₹5,00,000 |
| Key trust signals | SEBI-registered, zero defaults since inception, senior secured bonds |
| Campaign goals | BankVerified = acquire users who complete bank KYC; PaymentSuccess = acquire users who invest |
| Ad placement | Google App Ads (MULTI_CHANNEL): Play Store, YouTube, Search, Display |
| Character limits | Headlines ≤30 chars, Descriptions ≤90 chars |
| Competitors | Wint Wealth, GoldenPi, Grip Invest, StableMoney, INDmoney, Groww |
| FD comparison | Standard bank FD: 7–8% p.a. — Aspero's primary implicit competition |

**The core creative insight for Aspero:**
The audience is already saving money (FDs, mutual funds). They're not being asked to change
behavior — they're being asked to move savings to a higher-yield instrument. The ad only needs
to do three things: (1) show a specific yield number, (2) signal safety/legitimacy, (3) make
the first step feel low-effort. Everything else is noise.

---

## Weekly Analysis Checklist

Before writing each week's analysis, confirm:

- [ ] How many unique creatives are running? (5 slots is the max for APP_AD)
- [ ] Are any two ads running identical copy? (duplicate waste)
- [ ] Which headline appears in all ads? (if same one, it's table stakes)
- [ ] Is there a yield number in PaymentSuccess? (historically absent — flag every time)
- [ ] What is the CTR spread? (>0.5% gap between best and worst = meaningful copy signal)
- [ ] Did any new creative launch this week? (compare to prior week CTR baselines)
- [ ] Are descriptions differentiated between creatives? (or is D2 copy-pasted across all?)
