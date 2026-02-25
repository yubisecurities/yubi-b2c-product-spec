# Aspero Invest — Figma Design Generator

A Figma plugin that generates the Aspero Invest bond-discovery widget screens directly in your Figma file.

## Files

```
figma-plugin/
  manifest.json   ← plugin metadata (Figma reads this)
  code.js         ← main plugin logic (runs in Figma sandbox)
  ui.html         ← plugin UI panel
  README.md       ← this file
```

---

## How to Install (Figma Desktop)

> Figma Desktop app is required. The web browser version does not support loading local plugins.

1. **Open Figma Desktop** and open any file (or create a new one).

2. Go to the menu: **Main Menu → Plugins → Development → Import plugin from manifest…**

3. In the file picker, navigate to:
   ```
   /Users/arpit.goyal/aspero-invest/figma-plugin/manifest.json
   ```
   and click **Open**.

4. The plugin is now installed as a development plugin.

---

## How to Run

1. In Figma Desktop, go to **Main Menu → Plugins → Development → Aspero Invest Design Generator**.

2. The plugin panel opens. Choose which frames to generate:

   | Frame | Size | Description |
   |-------|------|-------------|
   | Mobile – Main Widget | 390 × auto | Amount slider, duration, returns & risk controls |
   | Mobile – Bond Results | 390 × auto | Top 5 bond cards + earnings bar + View All row |
   | Mobile – All Bonds | 390 × auto | Grouped by Great / Good / Fair match tier |
   | Desktop – Full Page | 1440 × 900 | Wide-screen layout with widget centred |
   | Component Samples | 800 × auto | Pills, badges, bond card, earnings bar |

3. Click **Generate Designs**. Frames are placed side-by-side on the current page and the viewport zooms to fit them.

---

## Design Tokens Used

| Token | Hex | Usage |
|-------|-----|-------|
| `--g` | `#27AE60` | Primary green (pills active, CTA, yield text) |
| `--g-hi` | `#4ADE80` | Green highlight (nav badge, earnings bar values) |
| `--g-dk` | `#1A3C34` | Dark green (hero background) |
| `--g-dkr` | `#0D1F16` | Darkest green (nav bar, widget footer, earnings bar) |
| `--g-lt` | `#ECFDF5` | Light green (abbr avatar bg, active risk card) |
| `--bg` | `#F5F7F5` | Page background |
| `--t1` | `#111827` | Primary text |
| `--t2` | `#6B7280` | Secondary/muted text |
| `--border` | `#E5E7EB` | Card borders, dividers |

---

## Notes

- The plugin uses **Inter** font (available by default in all Figma accounts).
- Frames use **auto-layout** so you can easily resize or rearrange elements.
- Bond data shown is sample/mock data — same 5 bonds used in the live widget.
- Re-running the plugin adds a fresh set of frames without removing previous ones.
