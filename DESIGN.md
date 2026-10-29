---
name: Tiny Desk Trend
description: Backstage casting call on warm paper; your photo goes on lead.
colors:
  paper: "oklch(97.4% .024 80)"
  paper-2: "oklch(94.2% .036 78)"
  card: "oklch(99.4% .01 85)"
  ink: "oklch(21% .025 48)"
  ink-2: "oklch(36% .03 52)"
  muted: "oklch(46% .035 58)"
  line: "oklch(84% .035 75)"
  tomato: "oklch(56% .2 33)"
  tomato-2: "oklch(49% .19 32)"
  sun: "oklch(88% .16 92)"
  sun-2: "oklch(80% .16 85)"
  sea: "oklch(50% .115 245)"
  sea-2: "oklch(46% .11 248)"
  mint: "oklch(84% .1 160)"
  on-color: "oklch(99% .01 80)"
  ok: "oklch(45% .13 150)"
  bad: "oklch(50% .2 28)"
typography:
  display:
    fontFamily: "Fraunces, ui-serif, Georgia, serif"
    fontSize: "clamp(2.3rem, 1.3rem + 3.2vw, 4.25rem)"
    fontWeight: 900
    lineHeight: 1.05
    letterSpacing: "-0.02em"
    fontVariation: "\"SOFT\" 100"
  headline:
    fontFamily: "Fraunces, ui-serif, Georgia, serif"
    fontSize: "clamp(1.9rem, 1.3rem + 2vw, 3rem)"
    fontWeight: 900
    lineHeight: 1.05
    letterSpacing: "-0.02em"
    fontVariation: "\"SOFT\" 100"
  title:
    fontFamily: "Fraunces, ui-serif, Georgia, serif"
    fontSize: "1.35rem"
    fontWeight: 900
    lineHeight: 1.1
    letterSpacing: "-0.01em"
    fontVariation: "\"SOFT\" 100"
  body:
    fontFamily: "Bricolage Grotesque, ui-sans-serif, system-ui, sans-serif"
    fontSize: "1rem"
    fontWeight: 400
    lineHeight: 1.6
  lead:
    fontFamily: "Bricolage Grotesque, ui-sans-serif, system-ui, sans-serif"
    fontSize: "clamp(1.05rem, .98rem + .3vw, 1.2rem)"
    fontWeight: 400
    lineHeight: 1.6
  label:
    fontFamily: "Bricolage Grotesque, ui-sans-serif, system-ui, sans-serif"
    fontSize: "0.78rem"
    fontWeight: 800
    letterSpacing: "0.02em"
rounded:
  pill: "999px"
  object: "20px"
  field: "12px"
  inset: "14px"
  phone: "30px"
  paper: "6px"
spacing:
  gutter: "20px"
  card: "22px"
  grid: "16px"
  column-gap: "48px"
  section: "84px"
  section-sm: "60px"
components:
  button-primary:
    backgroundColor: "{colors.tomato}"
    textColor: "{colors.on-color}"
    rounded: "{rounded.pill}"
    padding: "12px 20px"
  button-primary-hover:
    backgroundColor: "{colors.tomato-2}"
    textColor: "{colors.on-color}"
  button-ghost:
    backgroundColor: "{colors.card}"
    textColor: "{colors.ink}"
    rounded: "{rounded.pill}"
    padding: "12px 20px"
  button-ghost-hover:
    backgroundColor: "{colors.sun}"
  button-sun:
    backgroundColor: "{colors.sun}"
    textColor: "{colors.ink}"
    rounded: "{rounded.pill}"
    padding: "12px 20px"
  button-disabled:
    backgroundColor: "{colors.paper-2}"
    textColor: "{colors.muted}"
    rounded: "{rounded.pill}"
  pill:
    backgroundColor: "{colors.card}"
    textColor: "{colors.ink}"
    typography: "{typography.label}"
    rounded: "{rounded.pill}"
    padding: "3px 11px"
  pill-sun:
    backgroundColor: "{colors.sun}"
    textColor: "{colors.ink}"
    rounded: "{rounded.pill}"
  pill-mint:
    backgroundColor: "{colors.mint}"
    textColor: "{colors.ink}"
    rounded: "{rounded.pill}"
  sticker:
    backgroundColor: "{colors.sun}"
    textColor: "{colors.ink}"
    rounded: "{rounded.pill}"
    padding: "7px 14px"
  card:
    backgroundColor: "{colors.card}"
    textColor: "{colors.ink}"
    rounded: "{rounded.object}"
    padding: "22px"
  input-field:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.ink}"
    rounded: "{rounded.field}"
    padding: "11px 12px"
  stage-band:
    backgroundColor: "{colors.sea}"
    padding: "40px 0 44px"
  faq-item:
    backgroundColor: "{colors.card}"
    textColor: "{colors.ink}"
    rounded: "16px"
    padding: "16px 20px"
  modal:
    backgroundColor: "{colors.card}"
    textColor: "{colors.ink}"
    rounded: "{rounded.object}"
    padding: "28px"
    width: "min(430px, 92vw)"
---

# Design System: Tiny Desk Trend

## Overview

**Creative North Star: "The Backstage Casting Call"**

The site is a cramped, cheerful backstage wall: warm cream paper, everything outlined in a deep brown-black ink, objects stuck down with hard zero-blur shadows like cut-out card lifted a few millimetres off the wall. A fat, soft Fraunces display does the shouting; Bricolage Grotesque does the explaining. Colour comes in solid poster blocks (tomato, sun, sea, mint), never as gradients or glows.

The world is user-pinned: the user chose the visual style of intothememe.com (cream ground, ink outlines with hard offset shadows, chunky soft serif display, tomato/sun/sea palette, pill tags, marquee) as the reference. This system translates that style into its own identity; it is not a copy of that site's brand, marks, or copy. Hard offset shadows are native to this world, not decoration borrowed from elsewhere.

Density is generous and object-led: each thing on the page is a discrete stuck-down object (card, ticket, set-list sheet, sticker, phone) with a 2px ink outline, sitting on paper or on the sea-blue stage band. Theatre props carry the metaphor: a set list taped to the wall, ticket-stub price packs, a "now on lead" sticker slapped onto the sample phone.

**Key Characteristics:**
- Warm paper ground (paper, paper-2 bands), card-white objects.
- 2px ink outline on every interactive or object surface.
- Zero-blur ink lift: 3px standard, 5px for hero objects, 2px for small controls.
- Fraunces 900 with SOFT 100 for every display moment; Bricolage 400–800 for everything else.
- Pills everywhere: buttons, tags, stickers, tabs, credit counter.
- Small tilts (-7deg to 8deg) on stickers, the phone, and the set list; content blocks stay square.

## Colors

Solid poster colours on warm paper, held together by one ink.

### Primary
- **Stage Tomato** (tomato; hover tomato-2): the action colour. Primary buttons, the first casting tile, the "Most popular" badge, "Now on lead" labels, set-list numerals, the closing CTA band, link text (tomato-2).

### Secondary
- **Spotlight Sun** (sun; hover sun-2): stickers, highlights and selected states. The hero headline highlighter stripe, the "your face goes here" sticker, the popular ticket, credit pill, ghost-button hover, logo mark, text selection, FAQ footer headings on ink.
- **Stage Sea** (sea): the full-bleed generator stage band behind the hero card and phone, the account avatar, one casting tile. Also the focus-ring colour.

### Tertiary
- **Green-Room Mint** (mint): the reassurance tone. "Credits back if it fails" pill, one casting tile, marquee dots.

### Neutral
- **Warm Paper** (paper): page ground, input and drop-zone fill.
- **Deep Paper** (paper-2): alternating section bands, tab track, nav hover, disabled buttons.
- **Card White** (card): every lifted object surface.
- **Backstage Ink** (ink): text, all outlines, all shadows, marquee strip, footer ground, modal backdrop (at 60%).
- **Soft Ink** (ink-2): lead and secondary copy, dashed drop-zone outline.
- **Muted Ink** (muted): meta text, hints.
- **Pencil Line** (line): hairline dividers, dashed set-list rules, fact chips.
- **On-Colour Cream** (on-color): text on tomato and sea fills.
- **ok / bad**: inline status messages only.

### Named Rules
**The One Ink Rule.** Outlines, shadows, dividers on objects and dark grounds all use the single ink. No grey borders on objects, no black, no coloured shadows.

**The Solid Block Rule.** Colour is applied as flat fills on whole objects (a tile, a ticket, a band). The only gradients are the sun highlighter stripe behind headline words and the faint dot grid on the sea stage.

## Typography

**Display Font:** Fraunces, self-hosted variable 700–900 with the SOFT axis (fallback ui-serif, Georgia, serif)
**Body Font:** Bricolage Grotesque, self-hosted variable 400–800 (fallback ui-sans-serif, system-ui, sans-serif)

**Character:** A chubby, soft-cornered serif at 900 that reads like hand-cut poster letters, against a lively grotesque that stays plain in body copy and gets loud only at 800 for buttons and pills.

### Hierarchy
- **Display** (Fraunces 900, SOFT 100, clamp 2.3rem to 4.25rem on the hero, up to 4.6rem for generic h1, line-height 1.05, -0.02em, balanced wrap): the hero headline, with a sun highlighter stripe behind the key word.
- **Headline** (Fraunces 900, clamp 1.9rem to 3rem): section titles; the CTA band goes up to 4rem at 16ch.
- **Title** (Fraunces 900, 1.3–1.6rem, -0.01em): card heads, casting tile names, set-list steps, pack names; also set-list numerals (2.4rem, tomato), pack prices (3.4rem, tabular), and the marquee (1.35rem).
- **Body** (Bricolage 400, 1rem, line-height 1.6): running copy; reading pages at 1.06rem, 68ch max.
- **Lead** (Bricolage 400, clamp 1.05rem to 1.2rem, ink-2, 52ch max): the line under section and hero titles.
- **Label** (Bricolage 800, 0.78–0.9rem): pills, stickers, buttons (800 at 1rem), FAQ summaries (700).

### Named Rules
**The Soft Display Rule.** Every Fraunces use is weight 900 with `"SOFT" 100`. Never set Fraunces light or sharp, and never set body copy in it.

## Layout

Single centred container (1160px max, 20px gutter; 760px narrow for reading pages). Sections are 84px tall-padded (60px under 760px), alternating paper and paper-2 bands separated by 2px ink rules. Two-column splits use asymmetric fractions (1.1/0.9 stage, 0.85/1.15 set list, 0.75/1.5 FAQ) with a 48px gap and collapse to one column at 900px. The casting grid is 12 columns with deliberately uneven spans (7/5, then 4/4/4), going to full width under 760px. Pricing is three equal tickets at 980px max, stacking to a single 420px column on phones.

The hero stage is a full-bleed band, not a contained card: the sea-blue strip runs edge to edge between ink rules, directly under the headline, with an ink marquee strip below it. On phones the order is headline, generator, sample.

Header is sticky, 66px, translucent paper with blur and a 2px ink bottom rule; nav collapses into a burger panel at 900px.

## Elevation & Depth

Depth is printed, not lit. Every lifted object casts a solid ink shadow with zero blur offset down-right, as if a cut-out card sits a few millimetres off the wall. There are no ambient or blurred shadows anywhere. Pressing a button pushes it flat into its shadow.

### Shadow Vocabulary
- **Lift** (`box-shadow: 3px 3px 0 0 var(--ink)`): default for cards, casting tiles, FAQ items, guide list, account menu, buttons, stickers, cast sticker when on.
- **Lift Large** (`box-shadow: 5px 5px 0 0 var(--ink)`): hero-weight objects: the phone frame, set-list sheet, auth modal, popular ticket (as drop-shadow).
- **Lift Small** (`box-shadow: 2px 2px 0 0 var(--ink)`): small controls: small buttons, logo mark, avatar, burger, phone control stickers.
- **Ticket lift** (`filter: drop-shadow(3px 3px 0 var(--ink))`): used on ticket packs so the shadow follows the masked notches.

### Named Rules
**The Press-In Rule.** Hover raises a button 1px into a 4px lift; active translates it 3px into a zero shadow. Interaction is mechanical, never a glow or scale.

## Shapes

Three corner families: full pills (999px) for anything you tap or read as a tag; 20px rounded objects for cards, tiles, tickets and the modal; 12–16px for inner pieces (fields, drop zone, FAQ items, thumbnails). The phone frame is 30px with a 3px outline. The set-list sheet is nearly square (6px) because it is paper. Circles for the account avatar and the cast photo sticker.

Ticket stubs carry semicircle notches on both sides at the tear line, cut with a CSS mask on the ticket and redrawn as half-circle ink rings by pseudo-elements, with a 3px dashed ink tear rule. Dashed strokes mean "paper": tear lines, set-list rules, the drop zone.

## Components

### Buttons
Chunky pills that press into the wall.
- **Shape:** full pill (999px), 2px ink outline, 3px lift.
- **Primary:** tomato fill, on-color text, Bricolage 800 1rem, 12px 20px. `big` is 1.1rem at 15px 26px; `sm` is 0.9rem at 7px 14px with the small lift.
- **Hover / Focus:** tomato-2, lift to 4px with a 1px raise; active pushes flat. Focus is a 3px sea outline at 3px offset.
- **Ghost:** card fill, ink text, sun on hover. **Sun:** sun fill, sun-2 on hover (used on the tomato CTA band).
- **Disabled:** paper-2 fill, muted text, line-coloured outline, no lift.

### Pills
- **Style:** card, sun or mint fill, 2px ink outline, Bricolage 800 0.78rem, no lift. Used for hero facts and the credit counter. Lighter fact chips (1px line outline, paper fill, no ink) list generator specs.

### Stickers
- **Style:** sun pill with ink outline and lift, tilted -7deg, pinned off the edge of the phone frame with a star icon. Tomato label stickers ("Now on lead", "Most popular") tilt -3 to 8deg.
- **Peel:** when a photo is accepted the guide sticker rotates -30deg, slides away and fades (0.45s).

### Cards / Containers
- **Corner Style:** 20px.
- **Background:** card; casting tiles use solid tomato, sun, card, mint, sea in grid order.
- **Shadow Strategy:** Lift; see Elevation.
- **Border:** 2px ink.
- **Internal Padding:** 22px (tiles 20px 22px).

### Inputs / Fields
- **Style:** paper fill, 2px ink outline, 12px radius, 11px 12px padding.
- **Focus:** 3px sea outline. Checkboxes use tomato accent-color.
- **Drop zone:** 2px dashed ink-2, 16px radius, paper fill; hover warms toward sun and the outline goes full ink. Sun icon tile at 58px.

### Navigation
Bricolage 600 0.95rem ink links in pill hit areas, paper-2 on hover. Logo is a sun rounded-square mark with lift beside Fraunces 900. Under 900px a burger (42px, 12px radius, small lift) opens a full-width paper panel with hairline-divided rows.

### Ticket-Stub Pack
Price card shaped as a ticket: face (pack name, Fraunces 3.4rem price) above a dashed tear line with masked notches, stub below (credits, check list, button). The popular pack is sun-filled, raised 8px, with a 5px drop-shadow and a tomato tilted badge.

### Set-List Paper
An ordered list on a card sheet with 6px corners, rotated -1.2deg, Lift Large, a translucent sun tape strip across the top edge, tomato Fraunces counters, dashed line rules between steps.

### Casting Tiles
Uneven 12-column grid of solid-colour tiles, Fraunces 900 name over a body line; the first tile is the largest and loudest (tomato, up to 2.3rem).

### FAQ Details
Card-filled native details elements, 16px radius, 2px ink, Lift. A CSS chevron (ink border corner) rotates on open; the open item warms to a pale sun.

### Sea Stage Band
Full-bleed sea strip between 2px ink rules with a faint white dot grid (18px), holding the generator card and the sample phone side by side.

### Ink Phone Frame
9:16 sample video in a 3px ink frame, 30px radius, ink fill, Lift Large, rotated 2deg. Bottom-right control stickers (card pills with small lift): play/pause icon toggle and a "Sound on" toggle that turns sun when pressed.

### Cast Sticker
104px circular photo with a 3px ink outline pinned on the phone's upper left. On a passed face check it pops from scale 0 at -12deg to full at 8deg, then its lift arrives; a tomato "Now on lead" label pops under it, and the drop-zone thumbnail slaps down from 1.5x at -14deg.

### Marquee
Ink strip under the stage with a looping (38s, linear) row of Fraunces 900 phrases separated by sun, tomato and mint dots. Decorative and aria-hidden.

### Auth Modal
Native dialog, card fill, 20px radius, 2px ink, Lift Large, 430px max, 60% ink backdrop. Round close button top right, a pill tab track (paper-2) whose active tab is solid ink with paper text, ink-outlined fields, full-width primary button.

## Do's and Don'ts

### Do:
- **Do** outline every object and control with the 2px ink, and lift it with a zero-blur ink shadow (2px, 3px or 5px by size).
- **Do** set every display line in Fraunces 900 with `"SOFT" 100`.
- **Do** use tomato for the one primary action in a view; use sun for stickers, highlights and selected states.
- **Do** keep all styles in the same-origin stylesheet and fonts self-hosted; the CSP allows same-origin styles and fonts only, so state changes are class toggles (`on`, `peeled`, `cast-on`, `paused`), never inline `style` attributes.
- **Do** keep motion on the shared ease `cubic-bezier(.16,1,.3,1)` and let reduced motion collapse all transitions and animations, stop the marquee, and leave the sample paused.
- **Do** keep the unofficial disclaimer visible in its outlined disclaimer box.

### Don't:
- **Don't** use blurred, ambient or coloured shadows; depth is ink only.
- **Don't** draw grey or coloured outlines on objects; the ink is the only object border (pencil line is for hairline dividers and fact chips).
- **Don't** load fonts or styles from a third-party origin, or use inline style attributes.
- **Don't** copy intothememe.com's brand, marks or copy; the reference is the style, not the identity.
- **Don't** use NPR or Tiny Desk logos or official assets.
