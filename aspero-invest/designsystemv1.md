# Design System v1 — Yubi B2C Mobile

> This document is a living reference for all feature development in this codebase. Always build UI using the components, tokens, and patterns defined here. Do not use raw React Native primitives where a design system equivalent exists.

---

## Table of Contents

1. [Architecture](#1-architecture)
2. [Typography](#2-typography)
3. [Color Tokens](#3-color-tokens)
4. [Spacing Tokens](#4-spacing-tokens)
5. [Border Radius Tokens](#5-border-radius-tokens)
6. [Font Size Tokens](#6-font-size-tokens)
7. [Button Component](#7-button-component)
8. [Input Component](#8-input-component)
9. [Component Library Reference](#9-component-library-reference)
10. [Rules: What NOT to Do](#10-rules-what-not-to-do)

---

## 1. Architecture

The component system is structured in three layers. Always prefer the lowest applicable layer.

```
@yubi/yb-core-*            ← npm packages (source of truth, do not use directly)
        ↓
src/b2c-components/core/   ← thin wrappers around @yubi packages (USE THESE)
        ↓
src/b2c-components/        ← domain-specific reusable components
        ↓
src/molecules/             ← composite/screen-level reusable components
        ↓
src/screens/               ← screen files (consume all layers above)
```

**Theme provider:** All `@yubi` components require the Phoenix theme provider to be mounted above them in the tree. The active theme is `lightThemeV2` from `src/b2c-themes/lightThemeV2.ts`.

**Font family:** `Sofia Pro` — used across all button labels and UI text.

---

## 2. Typography

**Component:** `src/b2c-components/core/Typography/index.tsx`
**Underlying package:** `@yubi/yb-core-typography`
**Export name:** `PhoenixTypography`

### Props

| Prop | Type | Notes |
|---|---|---|
| `variant` | `TypographyVariants` | See table below. Defaults to body if omitted. |
| `color` | `string` | Any hex or theme color token |
| `textAlign` | `'center' \| 'left' \| 'right' \| 'justify'` | |
| `transform` | `'capitalize' \| 'lowercase' \| 'uppercase' \| 'none'` | |
| `textDecoration` | `'underline' \| 'line-through' \| 'none' \| 'underline line-through'` | |
| `ellipsis` | `boolean` | Single-line truncation |
| `numberOfLines` | `number` | Multi-line clamp |
| `onClick` | `PressableProps['onPress']` | Wraps text in `Pressable` with `accessibilityRole='button'` |
| `testID` | `string` | |

### Type Scale

#### Special / Display
| Variant | Size | Line Height | Weight | Use Case |
|---|---|---|---|---|
| `sp1` | 72 | 108 | 700 | Hero numbers, large stats |
| `sp2` | 60 | 90 | 700 | Large display text |
| `sp3` | 54 | 82 | 700 | Section hero |
| `d1` | 48 | 72 | 600 | Display heading |

#### Headers — weight `600`, normal
| Variant | Size | Line Height |
|---|---|---|
| `h1` | 36 | 54 |
| `h2` | 28 | 42 |
| `h3` | 24 | 36 |
| `h4` | 18 | 28 |
| `h5` | 16 | 25 |
| `h6` | 14 | 20 |

#### Sub-Headers — size `16`, line height `24`
| Variant | Weight | Style | Decoration |
|---|---|---|---|
| `sh1` | 700 | normal | none |
| `sh2` | 600 | normal | none |
| `sh3` | 500 | normal | none |
| `sh4` | 400 | normal | none |
| `sh5` | 400 | italic | none |
| `sh6` | 400 | normal | underline |

#### Body — size `14`, line height `20`
| Variant | Weight | Style | Decoration |
|---|---|---|---|
| `b1` | 700 | normal | none |
| `b2` | 600 | normal | none |
| `b3` | 500 | normal | none |
| `b4` | 400 | normal | none |
| `b5` | 400 | italic | none |
| `b6` | 400 | normal | underline |

#### Small — size `12`, line height `18`
| Variant | Weight | Style |
|---|---|---|
| `s1` | 700 | normal |
| `s2` | 500 | normal |
| `s3` | 500 | normal |
| `s4` | 400 | normal |
| `s5` | 400 | italic |

#### Tiny — size `10`, line height `14`
| Variant | Weight | Style |
|---|---|---|
| `t1` | 600 | normal |
| `t2` | 400 | normal |

### Usage Pattern

```tsx
import PhoenixTypography from 'src/b2c-components/core/Typography';

// Standard body text
<PhoenixTypography variant="b4" color={theme.semantic.colors.text.text.t1}>
  Account balance
</PhoenixTypography>

// Clickable label
<PhoenixTypography variant="b2" color={theme.semantic.Color.TextColors.Link.Default_POL500} onClick={handlePress}>
  View details
</PhoenixTypography>

// Truncated header
<PhoenixTypography variant="h4" numberOfLines={1} ellipsis>
  Bond name here
</PhoenixTypography>
```

---

## 3. Color Tokens

All color tokens live in `src/b2c-themes/lightThemeV2.ts`. Access via the `semantic` key.

### Brand Colors

| Token | Hex | Use |
|---|---|---|
| Primary green | `#018E43` | CTA buttons, active states, brand accents |
| Primary green hover | `#01B756` | Hover state |
| Primary green active | `#016530` | Pressed state |
| Primary green disabled | `#A8F8D5` | Disabled state |
| Special / Accent | `#01D464` | Highlights, badges |
| Link blue | `#2254B5` | Links, active borders |

### Neutral Scale (Greys)

| Token Name | Hex | Typical Use |
|---|---|---|
| N900 / `#101828` | `#101828` | Primary text, darkest surfaces |
| N800 / `#1D2939` | `#1D2939` | Dark backgrounds, primary borders |
| N700 / `#344054` | `#344054` | Secondary text, icon primary |
| N600 / `#475467` | `#475467` | Subheader text |
| N500 / `#667085` | `#667085` | Body text muted, icon secondary |
| N400 / `#98A2B3` | `#98A2B3` | Placeholder, icon tertiary |
| N300 / `#D0D5DD` | `#D0D5DD` | Borders, dividers |
| N200 / `#F2F4F7` | `#F2F4F7` | Light backgrounds, disabled fill |
| N100 / `#F9FAFB` | `#F9FAFB` | Card backgrounds |
| N50 / `#FCFDFD` | `#FCFDFD` | Page backgrounds |
| White / `#FFFFFF` | `#FFFFFF` | |

### Semantic Text Colors (`semantic.Color.TextColors`)

| Group | Token | Hex |
|---|---|---|
| Header | `H1_N900` | `#101828` |
| Header | `H2_N600` | `#475467` |
| Header | `White` | `#FFFFFF` |
| SubHeader | `SH1_N900` | `#101828` |
| SubHeader | `SH2_N700` | `#344054` |
| SubHeader | `SH3_N600` | `#475467` |
| BodyText | `BT1_N900` | `#101828` |
| BodyText | `BT2_N600` | `#475467` |
| BodyText | `BT3_N500` | `#667085` |
| BodyText | `BT4_N400` | `#98A2B3` |
| Link | `Default_POL500` | `#2254B5` |
| Link | `DefaultStrong_O500` | `#01D464` |

### Feedback Colors (`semantic.Color.Feedback`)

| State | Strong | Weak |
|---|---|---|
| Success | `#2D671F` | `#DDF6C7` |
| Critical / Error | `#CD3546` | `#FBE8F1` |
| Caution / Warning | `#F79009` | `#FFFAEB` |
| Special | `#01D464` | `#C9FFEA` |
| Info | `#1D2939` | `#F2F4F7` |

### Text Feedback Colors (`semantic.Color.TextColors.TextFeedback`)

| State | Strong | Weak |
|---|---|---|
| Success | `#3F902B` | `#70CD59` |
| Critical | `#CD3546` | `#EAA9B1` |
| Caution | `#F79009` | `#FEDF89` |
| Special | `#01D464` | `#86F1BF` |

### Surface / Background Colors (`semantic.Color.Surface`)

| Token | Hex | Use |
|---|---|---|
| `BG1_Light_BW50` | `#FFFFFF` | Default screen background (light) |
| `BG2_Light_N200` | `#F2F4F7` | Secondary screen background |
| `BG1_Dark_N900` | `#101828` | Dark screen background |
| `BG2_Dark_N800` | `#1D2939` | Dark secondary background |

### Background Scale (`semantic.colors.backgroundColors`)

`bg1` (#FFFFFF) → `bg2` (#F8FAFC) → `bg3` (#EEF2F6) → `bg4` (#E3E8EF) → `bg5` (#CDD5DF) → … → `bg6` (#121926)

Feedback backgrounds: `bg11` (success #2D671F), `bg12` (success light #DDF6C7), `bg13` (error #B22D3C), `bg15` (caution #F79009), `bg17` (brand #01D464)

### Action States (`semantic.colors.actionColors`)

| Set | Default | Hover | Active | Disabled |
|---|---|---|---|---|
| `a1` (Primary green fill) | `#018E43` | `#01B756` | `#016530` | `#A8F8D5` |
| `a2` (Primary ghost) | `#FFFFFF` | `#E4FFF5` | `#C9FFEA` | `#FFFFFF` |
| `a3` (Tertiary/neutral) | `#FFFFFF` | `#EEF2F6` | `#E3E8EF` | `#FFFFFF` |
| `a4` (Success) | `#3F902B` | `#26581A` | `#204916` | `#A6E097` |
| `a5` (Error/delete) | `#CD3546` | `#B22D3C` | `#952532` | `#F4D4D8` |
| `a6` (Special blue) | `#4065C5` | `#3554A4` | `#2B4383` | `#9FB2E2` |

### Card / Banner Colors (`semantic.Color.Surface.Card`)

Named after planets — use for bond card, banner, and card gradient backgrounds:

| Token | Hex |
|---|---|
| `JUP500` | `#213056` |
| `EAR500` | `#0B135E` |
| `NEP500` | `#425C8F` |
| `MER500` | `#C5D6EF` |
| `VEN500` | `#DEEAFC` |
| `LUC500` | `#7990B0` |
| `APO500` | `#5E79A0` |

### Solid Color Scale (`SolidColors`)

`EAR500` (#0B135E) → `JUP500` (#213056) → `URA500` (#1F2A37) → `NEP500` (#425C8F) → `APO500` (#5E79A0) → `LUC500` (#7990B0) → `MER500` (#C5D6EF) → `VEN500` (#DEEAFC)

### Special Tag Colors (`SpecialTags`)

| Token | Hex |
|---|---|
| `LAC500` | `#F3F4F6` |
| `KAP500` | `#DEEAFC` |
| `MOO500` | `#C4E5FB` |
| `GRO500` | `#F8D8E7` |
| `VEG500` | `#F1E7FD` |
| `ARI500` | `#B0EDEF` |

---

## 4. Spacing Tokens

From `lightThemeV2.spacing`. Always use named tokens; avoid magic numbers.

### Named Scale

| Token | Value (px) |
|---|---|
| `6xs` | 2 |
| `5xs` | 4 |
| `4xs` | 6 |
| `3xs` | 8 |
| `2xs` | 10 |
| `xs` | 12 |
| `s` | 16 |
| `xxs` | 20 |
| `m` | 24 |
| `l` | 32 |
| `xl` | 40 |
| `2xl` | 48 |

### Common Values Available as Numeric Strings

`0, 1, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 28, 30, 32, 36, 40, 44, 48, 52, 56, 60, 64, 80, 96, 104, 120, 140, 160, 240`

### Button Padding Spacing

| Button Size | paddingLeft/Right | paddingTop/Bottom |
|---|---|---|
| `s` | 16 | 8 |
| `m` | 24 | 10 |
| `l` | 16 | 16 |

---

## 5. Border Radius Tokens

From `lightThemeV2.borderRadius`.

| Token | Value | Use |
|---|---|---|
| `borderRadius0` / `none` | 0 | No rounding |
| `2xs` | 2 | Minimal rounding (switches) |
| `xs` | 4 | Subtle rounding (tags, chips) |
| `s` | 6 | Buttons (all sizes), inputs small |
| `m` | 8 | Cards, inputs medium |
| `l` | 10 | Larger cards |
| `xl` | 12 | Modals, large containers, inputs large |
| `3xl` | 24 | Pill-like containers |
| `full` | 9999 | Fully rounded (avatars, loaders, floating buttons) |

### Component-specific Radius

| Component | Radius |
|---|---|
| Buttons (all sizes) | `6` |
| Inputs small | `6` |
| Inputs medium | `8` |
| Inputs large | `12` |
| Feedback banners | `12` |
| Avatar | `9999` (full) |
| Floating button | `9999` (full) |

---

## 6. Font Size Tokens

From `lightThemeV2.fontSizes`.

| Token | Value |
|---|---|
| `xxxs` | 6 |
| `xxs` | 8 |
| `xs` | 10 |
| `s` | 12 |
| `m` | 14 |
| `l` | 16 |
| `ml` | 18 |
| `xl` | 20 |
| `2xl` | 24 |
| `3xl` | 28 |
| `4xl` | 36 |
| `5xl` | 48 |
| `6xl` | 54 |

These align directly with the typography variant sizes. Prefer using `PhoenixTypography` with the correct `variant` rather than setting `fontSize` manually.

---

## 7. Button Component

**Component:** `src/b2c-components/core/Button/index.tsx`
**Underlying package:** `@yubi/yb-core-button`
**Export name:** `Button` (default)

### Sizes

| Size | Height | Horizontal Padding | Border Radius |
|---|---|---|---|
| `s` | 32 | 12 | 6 |
| `m` | 40 | 16 | 6 |
| `l` | 48 | 24 | 6 |

Label font: `Sofia Pro`, size 14, line height 20.

### Variants

| Variant | Default BG | Text Color | Border Color | Disabled BG |
|---|---|---|---|---|
| `primary` | `#018E43` | `#FFFFFF` | `#018E43` | `#A8F8D5` |
| `secondary` | `#FFFFFF` | `#018E43` | `#018E43` | `#FFFFFF` (text `#9AA4B2`) |
| `tertiary` | `#FFFFFF` | `#4B5565` | `#E3E8EF` | `#FFFFFF` (text `#9AA4B2`) |
| `success` | `#3F902B` | `#FFFFFF` | `#3F902B` | `#A6E097` |
| `delete` | `#CD3546` | `#FFFFFF` | `#CD3546` | (disabled style) |

### Usage Pattern

```tsx
import Button from 'src/b2c-components/core/Button';

// Primary CTA
<Button variant="primary" size="l" label="Invest Now" onPress={handleInvest} />

// Secondary action
<Button variant="secondary" size="m" label="Learn More" onPress={handleLearnMore} />

// Destructive
<Button variant="delete" size="m" label="Remove" onPress={handleRemove} />

// Disabled
<Button variant="primary" size="l" label="Continue" disabled onPress={handleContinue} />
```

**Never use `TouchableOpacity`, `Pressable`, or `TouchableHighlight` for button-like actions.** Use `Button` from the component library.

---

## 8. Input Component

**Component:** `src/b2c-components/core/Input/index.tsx`
**Underlying package:** `@yubi/yb-core-input`

### Key Props

| Prop | Type | Notes |
|---|---|---|
| `value` | `string` | Required |
| `label` | `string` | Field label |
| `placeholder` | `string` | |
| `caption` | `string` | Helper text below input |
| `error` | `string` | Error message (also triggers error state) |
| `required` | `boolean` | Shows required indicator |
| `disabled` | `boolean` | |
| `size` | `'s' \| 'm' \| 'l'` | Default `m` |
| `leftIcon` | `string` | Icon name |
| `rightIcon` | `string` | Icon name |
| `showClearIcon` | `boolean` | |
| `prefix` | `PrefixSuffix` | Left prefix (text, list, or icon) |
| `suffix` | `PrefixSuffix` | Right suffix |
| `multiline` | `boolean` | Textarea mode |
| `maxLength` | `number` | |
| `secureTextEntry` | `boolean` | Password field |
| `keyboardType` | `KeyboardTypeOptions` | |

Also available: `src/b2c-components/textInputWrapper` and `src/molecules/dropDownTextField` for wrapped field + label patterns.

**Never use raw `TextInput` from React Native** for user-facing form fields.

---

## 9. Component Library Reference

### Core Primitives (`src/b2c-components/core/`)

These wrap `@yubi/yb-core-*` packages. Always use these, never the npm packages directly.

| Component | Path | Replaces |
|---|---|---|
| `Button` | `src/b2c-components/core/Button` | `TouchableOpacity`, `Pressable` for CTAs |
| `PhoenixTypography` | `src/b2c-components/core/Typography` | Raw `<Text>` |
| `Input` | `src/b2c-components/core/Input` | Raw `TextInput` |
| `Card` | `src/b2c-components/core/Card` | `View` with manual shadow/elevation |
| `Chips` | `src/b2c-components/core/Chips` | Custom chip implementations |
| `Icons` | `src/b2c-components/core/Icons` | Custom icon components |
| `Tabs` | `src/b2c-components/core/Tabs` | Custom tab bar implementations |
| `Tags` | `src/b2c-components/core/Tags` | Custom tag/badge implementations |
| `Tooltip` | `src/b2c-components/core/Tooltip` | Custom tooltip |
| `ModalOrBottomSheet` | `src/b2c-components/core/ModalOrBottomSheet` | Raw `Modal` from RN |
| `OptionChooserModal` | `src/b2c-components/core/OptionChooserModal` | Custom option modals |
| `Table` | `src/b2c-components/core/Table` | Custom table layouts |
| `TableMobileDataCard` | `src/b2c-components/core/TableMobileDataCard` | Mobile table row cards |
| `Breadcrumbs` | `src/b2c-components/core/Breadcrumbs` | Custom breadcrumb nav |
| `TitleRowComponent` | `src/b2c-components/core/TitleRowComponent` | Section title+action rows |
| `Typography (key-value)` | `src/b2c-components/core/keyValueDisplay` | Custom key-value layouts |
| `MediaCard` | `src/b2c-components/core/MediaCard` | Image+text card layouts |
| `logo` | `src/b2c-components/core/logo` | Logo rendering |

### Domain Components (`src/b2c-components/`)

| Component | Purpose |
|---|---|
| `bondCard` | Bond listing card |
| `newBondCard` | Refreshed bond card |
| `revampBondCard` | Latest bond card design |
| `newBondListItem` | Bond list row item |
| `fdCard` | Fixed deposit card |
| `expandableCard` | Collapsible card container |
| `CardShadowWrapper` | Adds standard card shadow |
| `statusScreen` | Full-screen status/result states |
| `ErrorAlert` | Inline error alert |
| `formField` | Form field container with label |
| `textInputWrapper` | Styled input wrapper |
| `searchbar` | Search input |
| `RangeSlider` | Numeric range slider |
| `CustomCheckBox` | Checkbox input |
| `infiniteScrollList` | Paginated FlatList wrapper |
| `horizontalScrollList` | Horizontal scroll container |
| `infoLabel` | Label + info icon |
| `requiredLabel` | Field required indicator |
| `separator` | Horizontal divider |
| `highlightText` | Text with highlighted segment |
| `avatar` | User avatar |
| `profileImage` | Profile photo display |
| `confetti` | Celebration animation |
| `widget-skeleton` | Skeleton loading placeholder |
| `titleWithValueWidget` | Title/value display pair |
| `BottomButtonContainer` | Fixed bottom CTA container |
| `ButtonComponentWrapper` | Button with platform-aware styling |
| `SEO` | Web SEO meta tags |
| `kraDetails` | KRA detail display |
| `kraPopupBanner` | KRA status banner |
| `newBankAccountStatusCard` | Bank account status card |
| `iconPreview` | Icon preview component |
| `horizontalScrollList` | Horizontal list scroller |

### Molecules (`src/molecules/`)

Composite components built for specific screen patterns.

| Component | Purpose |
|---|---|
| `header` | Screen header bar |
| `backButton` | Navigation back button |
| `headerRightButton` | Header right action button |
| `footer` | Screen footer |
| `baseScreen` | Base screen wrapper with header/footer |
| `bottomSheetContainer` | Bottom sheet wrapper |
| `modalWrapper` | Modal container |
| `shimmer` | Shimmer loading animation |
| `formSkeleton` | Form skeleton loader |
| `circularLoader` | Spinner/loading indicator |
| `lottifyanimation` | Lottie animation player |
| `errorBanner` | Top-of-screen error banner |
| `staticBanner` | Info/marketing banner |
| `networkError` | Network error state |
| `disclaimer` | Legal/info disclaimer block |
| `hyperlink` | Styled tappable link |
| `radioButton` | Radio button input |
| `dropDownTextField` | Select/dropdown field |
| `expandableSection` | Accordion section |
| `webView` | In-app browser |
| `pdfViewer` | PDF rendering |
| `imageViewer` | Full-screen image viewer |
| `thumbnail` | Image thumbnail |
| `toastWrapper` | Toast notification |
| `customToastList` | Multiple toast manager |
| `resendOtp` | OTP resend with countdown |
| `counter` | Numeric increment/decrement |
| `listingBonds` | Bond list container |
| `uploadDocument` | Document upload flow |
| `uploadDocumentPopup` | Upload options popup |
| `statusPreview` | Status display |
| `statusBarView` | Status bar configuration |
| `themeAdjustedStatusBar` | Theme-aware status bar |
| `keyboardAvoidingViewWrapper` | KeyboardAvoidingView wrapper |
| `marginWidget` | Spacing utility component |
| `dashedHorizontalLine` | Dashed divider |
| `dashedVerticalLine` | Dashed vertical rule |
| `logicalOrSeparator` | "OR" divider |
| `rowTextsWithDot` | Dot-separated inline text row |
| `infoListCell` | Icon + label list row |
| `helpCard` | Help/support card |
| `requestCallback` | Callback request widget |
| `immutableSearchHeader` | Non-editable search display |
| `searchButton` | Search trigger button |
| `recentSearch` | Recent search list |
| `restrictScreenCaptureWidget` | Screenshot prevention |
| `restrictTransactionBottomSheet` | Transaction restriction sheet |
| `restrictDebarredUser` | Debarred user blocker |
| `rootedDeviceScreen` | Rooted device warning |
| `softDeleteUserPopup` | Account deletion confirmation |
| `kycStatusBanner` | KYC status indicator |
| `kycFailedBanner` | KYC failure state |
| `kycIncompleteBanner` | KYC incomplete state |
| `kycNotStartedBanner` | KYC not started state |
| `kycUnderReview` | KYC review in progress |
| `exitKyc` | KYC exit confirmation |
| `exitBottomPopup` | Generic exit confirmation |
| `removeBottomPopup` | Remove item confirmation |
| `portfolio-card` | Portfolio summary card |
| `portfolio-starter-card` | Empty portfolio starter |
| `collectionsCard` | Collections display card |
| `bond` | Bond display molecule |
| `bankDetailsForm` | Bank account form |
| `MobileNoForm` | Mobile number entry form |
| `documentItem` | Document list item |
| `PhoenixWrapper` | Phoenix theme provider wrapper |
| `CustomCameraWrapper` | Camera access wrapper |
| `webHeader` | Web-specific header |
| `TableCard` | Tabular data card |

---

## 10. Rules: What NOT to Do

These rules exist to maintain consistency and enable theming. Violating them introduces detached UI that won't respond to theme changes.

### Typography
- **Do not use `<Text>` from `react-native`** for any user-visible text. Use `PhoenixTypography` with the appropriate `variant`.
- **Do not set `fontSize`, `fontWeight`, `lineHeight`, or `fontFamily` manually** in `StyleSheet`. Use a typography variant.

### Buttons & Interactivity
- **Do not use `TouchableOpacity`, `Pressable`, or `TouchableHighlight`** for button-like actions. Use `Button` from `src/b2c-components/core/Button`.
- Exception: `Pressable` is acceptable for non-button interactive wrappers (e.g., navigable card rows, dismissable overlays) where `Button` semantics don't apply.

### Inputs
- **Do not use raw `TextInput`** for user-facing form fields. Use `Input` from `src/b2c-components/core/Input` or `textInputWrapper` / `dropDownTextField` from molecules.

### Colors
- **Do not hardcode hex color values** in `StyleSheet`. Always reference `lightThemeV2.semantic.colors.*` or `lightThemeV2.semantic.Color.*` tokens.
- Exception: transparent, black, white as layout utilities are acceptable.

### Spacing & Layout
- **Do not use magic numbers** for padding/margin. Reference spacing tokens from `lightThemeV2.spacing`.
- **Do not recreate a separator** with `<View style={{ height: 1, backgroundColor: '...' }}>`. Use `src/b2c-components/separator` or `src/molecules/dashedHorizontalLine`.

### Cards
- **Do not add `shadowColor` / `elevation` inline** to create card effects. Use `src/b2c-components/CardShadowWrapper` or `src/b2c-components/core/Card`.

### Modals
- **Do not use `Modal` from `react-native`** directly. Use `src/b2c-components/core/ModalOrBottomSheet` or `src/molecules/modalWrapper` / `src/molecules/bottomSheetContainer`.

### Lists
- **Do not use `FlatList` directly** for paginated data. Use `src/b2c-components/infiniteScrollList`. Raw `FlatList` is acceptable for simple, non-paginated static lists only.

### Loading States
- **Do not use ad-hoc loading spinners.** Use `src/molecules/shimmer`, `src/molecules/formSkeleton`, or `src/b2c-components/widget-skeleton`.

### Chips
- **Do not build custom chip/pill UI.** Use `src/b2c-components/core/Chips`.

---

## Quick Reference: Import Paths

```tsx
// Typography
import PhoenixTypography from 'src/b2c-components/core/Typography';

// Button
import Button from 'src/b2c-components/core/Button';

// Input
import Input from 'src/b2c-components/core/Input';

// Card
import Card from 'src/b2c-components/core/Card';

// Chips
import Chips from 'src/b2c-components/core/Chips';

// Tags
import Tags from 'src/b2c-components/core/Tags';

// Tabs
import Tabs from 'src/b2c-components/core/Tabs';

// Tooltip
import Tooltip from 'src/b2c-components/core/Tooltip';

// Modal / Bottom Sheet
import ModalOrBottomSheet from 'src/b2c-components/core/ModalOrBottomSheet';

// Icons
import Icons from 'src/b2c-components/core/Icons';

// Separator
import Separator from 'src/b2c-components/separator';

// Shimmer
import Shimmer from 'src/molecules/shimmer';

// Infinite scroll list
import InfiniteScrollList from 'src/b2c-components/infiniteScrollList';

// Card shadow wrapper
import CardShadowWrapper from 'src/b2c-components/CardShadowWrapper';

// Status screen
import StatusScreen from 'src/b2c-components/statusScreen';

// Bottom button container
import BottomButtonContainer from 'src/b2c-components/BottomButtonContainer';

// Theme
import lightThemeV2 from 'src/b2c-themes/lightThemeV2';
```
