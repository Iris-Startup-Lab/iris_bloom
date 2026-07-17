---
name: Synthetic Precision
colors:
  surface: '#0b1326'
  surface-dim: '#0b1326'
  surface-bright: '#31394d'
  surface-container-lowest: '#060e20'
  surface-container-low: '#131b2e'
  surface-container: '#171f33'
  surface-container-high: '#222a3d'
  surface-container-highest: '#2d3449'
  on-surface: '#dae2fd'
  on-surface-variant: '#c2c6d6'
  inverse-surface: '#dae2fd'
  inverse-on-surface: '#283044'
  outline: '#8c909f'
  outline-variant: '#424754'
  surface-tint: '#adc6ff'
  primary: '#adc6ff'
  on-primary: '#002e6a'
  primary-container: '#4d8eff'
  on-primary-container: '#00285d'
  inverse-primary: '#005ac2'
  secondary: '#d0bcff'
  on-secondary: '#3c0091'
  secondary-container: '#571bc1'
  on-secondary-container: '#c4abff'
  tertiary: '#4edea3'
  on-tertiary: '#003824'
  tertiary-container: '#00a572'
  on-tertiary-container: '#00311f'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#d8e2ff'
  primary-fixed-dim: '#adc6ff'
  on-primary-fixed: '#001a42'
  on-primary-fixed-variant: '#004395'
  secondary-fixed: '#e9ddff'
  secondary-fixed-dim: '#d0bcff'
  on-secondary-fixed: '#23005c'
  on-secondary-fixed-variant: '#5516be'
  tertiary-fixed: '#6ffbbe'
  tertiary-fixed-dim: '#4edea3'
  on-tertiary-fixed: '#002113'
  on-tertiary-fixed-variant: '#005236'
  background: '#0b1326'
  on-background: '#dae2fd'
  surface-variant: '#2d3449'
typography:
  headline-xl:
    fontFamily: Inter
    fontSize: 40px
    fontWeight: '700'
    lineHeight: 48px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Inter
    fontSize: 32px
    fontWeight: '600'
    lineHeight: 40px
    letterSpacing: -0.02em
  headline-lg-mobile:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
  headline-md:
    fontFamily: Inter
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 28px
  body-lg:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  label-md:
    fontFamily: JetBrains Mono
    fontSize: 13px
    fontWeight: '500'
    lineHeight: 16px
  label-sm:
    fontFamily: JetBrains Mono
    fontSize: 11px
    fontWeight: '500'
    lineHeight: 14px
    letterSpacing: 0.05em
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  base: 4px
  xs: 4px
  sm: 8px
  md: 16px
  lg: 24px
  xl: 40px
  gutter: 20px
  container-max: 1440px
---

## Brand & Style

The design system is engineered for professional AI practitioners who require high-density data visualization without cognitive fatigue. The brand personality is **Intelligent, Reliable, Precise, and Innovative**. It avoids the "playful" tropes of consumer AI in favor of a sophisticated, tool-oriented aesthetic.

The visual style is a hybrid of **Modern Corporate** and **Glassmorphism**. It utilizes deep, layered surfaces to create a sense of focused workspace. Precision is communicated through razor-sharp borders, consistent alignment, and a strict adherence to a logic-driven information hierarchy. Interaction is signaled through vibrant, high-energy accents that contrast against the monochromatic base.

## Colors

The palette is optimized for a **Dark Mode** first experience to reduce eye strain during prolonged technical sessions.

- **Primary (AI Blue):** `#3B82F6`. Used for primary actions, active states, and AI-driven insights.
- **Secondary (Deep Purple):** `#8B5CF6`. Used for model differentiation, experimental features, and complex data relationships.
- **Neutral (Deep Slate/Charcoal):** The foundation consists of `#0F172A` (Background), `#1E293B` (Surface), and `#334155` (Border).
- **Semantic Accents:** `#10B981` (Success/Validation), `#F59E0B` (Warning/Processing), and `#EF4444` (Error).

Surface colors should use subtle translucency when layered over background gradients to achieve a professional glassmorphic effect.

## Typography

This design system utilizes **Inter** for all UI elements to ensure maximum legibility in high-density data environments. It is a systematic, utilitarian typeface that remains neutral.

For technical contexts—such as model IDs, code previews, and data terminal outputs—**JetBrains Mono** is employed. This distinction helps users instantly differentiate between "interface language" and "machine data."

Typography scales emphasize clarity. Headlines use tight letter-spacing and heavy weights for impact, while labels use uppercase styling and monospaced fonts to signify metadata and system statuses.

## Layout & Spacing

The layout follows a **Fluid Grid** model with strict 4px increments (base unit). 

- **Desktop:** 12-column grid, 20px gutters, and 40px side margins.
- **Tablet:** 8-column grid, 16px gutters, 24px side margins.
- **Mobile:** 4-column grid, 12px gutters, 16px side margins.

Data-heavy views (Notebooks/Dashboards) may bypass standard container constraints to utilize the full width of the viewport. Navigation is handled via a persistent, slim left-hand sidebar (64px collapsed, 240px expanded) to maximize horizontal space for data columns.

## Elevation & Depth

Hierarchy is established through **Tonal Layers** combined with **Glassmorphism**. 

1. **Floor (Level 0):** `#0F172A`. The darkest base layer.
2. **Surface (Level 1):** `#1E293B`. Used for cards and main content areas.
3. **Overlay (Level 2):** `#1E293B` with 80% opacity and a 12px backdrop blur. Used for modals, dropdowns, and floating toolbars.

Instead of heavy shadows, this design system uses **Low-Contrast Outlines**. Borders are 1px thick, using `#334155` for inactive states and a subtle 10% opacity primary color tint for active elements. Ambient glows (50px blur, 5% opacity) are used sparingly behind primary AI components to suggest "energy."

## Shapes

The shape language is **Soft (0.25rem)**. This provides a professional, "tooled" feel that is more approachable than sharp 90-degree angles but more disciplined than pill-shaped consumer apps.

- **Standard Buttons/Inputs:** 4px (rounded-sm)
- **Data Cards:** 8px (rounded-lg)
- **Modals/Large Containers:** 12px (rounded-xl)

Toggle switches and status pips are the only exceptions, utilizing a fully rounded (pill) shape to indicate state and interactivity.

## Components

- **Data Cards:** High-contrast containers with a 1px `#334155` border. Headers should use a subtle top-border accent (Primary or Secondary) to categorize the data type.
- **Status Indicators:** Small, circular pips with a soft outer glow. Green (Validated), Amber (Processing), Gray (Queued), Red (Failed).
- **Model Toggles:** Sleek, segmented controls. The active selection uses a subtle gradient (Blue to Purple) with white text, while the inactive state remains slate.
- **Code/Notebook Previews:** Containers using Level 0 background (`#0F172A`) to distinguish from the UI. Syntax highlighting must follow a high-contrast dark theme (e.g., Nord or Monokai-inspired).
- **Primary Buttons:** Solid `#3B82F6` with white text. No gradients.
- **Input Fields:** Dark background, 1px border. On focus, the border transitions to Primary Blue with a 2px outer "soft glow" (0% spread).
- **Chips:** Monospaced text (JetBrains Mono) inside a subtle `#334155` filled container with 4px radius. Used for metadata tags and file types.