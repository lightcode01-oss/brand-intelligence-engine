# Logo Recommendation Engine Design: Nomen

This document details how Nomen dynamically generates visual brand concepts, logo layouts, color palettes, and typography guidelines without relying on expensive, slow AI Image APIs.

---

## 1. Visual Composition Philosophy

Instead of generating raster PNGs using stable diffusion (which cannot be easily scaled or edited by a designer), Nomen constructs **scalable, clean vector SVGs** on the client browser. This is done by combining:
1. **Geometric Brandmarks**: Abstract SVG shapes (e.g., node maps, intersecting circles, geometric grids).
2. **First-Letter Monograms**: SVG container graphics framing the name's initial letter in selected typography.
3. **Wordmarks**: The brand name rendered in high-quality Google Fonts pairings.

---

## 2. Industry & Tone Design Mappings

The engine determines styling configurations based on user-selected verticals and tone parameters:

### 2.1. Color Palette Generator (HSL Coordinates)

| Vertical / Category | Primary Tone | Color 1 (Primary) | Color 2 (Secondary) | Rationale |
| :--- | :--- | :--- | :--- | :--- |
| **Fintech & Security** | Trust / Premium | Deep Navy (`hsl(222, 47%, 11%)`) | Electric Blue (`hsl(217, 91%, 60%)`) | Emphasizes security and modern speed. |
| **Health & Wellness** | Clean / Growth | Forest Green (`hsl(142, 76%, 36%)`) | Warm Sand (`hsl(33, 100%, 96%)`) | Conveys natural vitality and calmness. |
| **SaaS & Tech** | Clean / Modern | Cyber Violet (`hsl(262, 83%, 58%)`) | Slate Gray (`hsl(215, 25%, 27%)`) | Standard developer-centric aesthetics. |
| **Agency & Creative** | Playful / Bold | Coral Orange (`hsl(16, 100%, 50%)`) | Midnight Black (`hsl(240, 10%, 4%)`) | High contrast for artistic branding. |

### 2.2. Typography Pairing Engine

| Tone Selection | Heading Font | Body Font | Design Profile |
| :--- | :--- | :--- | :--- |
| **Futuristic / Cyber** | `Orbitron` | `Geist Mono` | Monospaced, tech-heavy, digital-first look. |
| **Corporate / Premium** | `Lora` | `Inter` | Editorial serif heading matched with ultra-clean sans-serif body. |
| **Modern / Startup** | `Outfit` | `Plus Jakarta Sans` | Friendly, geometric, high readability at small sizes. |
| **Minimalist / Sleek** | `Syncopate` | `DM Sans` | Wide-spaced, high-contrast structural look. |

---

## 3. SVG Layout Frameworks

The system supports three SVG layouts rendered via React components:

### 3.1. Inline Logo Template Example
```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 120" width="100%" height="100%">
  <!-- 1. Background Grid (Subtle Glassmorphism helper) -->
  <defs>
    <linearGradient id="brandGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="var(--primary-color)" />
      <stop offset="100%" stop-color="var(--secondary-color)" />
    </linearGradient>
  </defs>

  <!-- 2. Dynamic Abstract Geometric Icon (E.g. Intersecting Rings) -->
  <g transform="translate(10, 10)">
    <circle cx="50" cy="50" r="30" fill="url(#brandGrad)" opacity="0.85" />
    <circle cx="70" cy="50" r="20" fill="none" stroke="var(--primary-color)" stroke-width="4" />
  </g>

  <!-- 3. Dynamic Font Wordmark -->
  <text x="130" y="68" 
        font-family="var(--heading-font)" 
        font-size="32" 
        font-weight="bold" 
        fill="var(--text-color)">
    NOMEN
  </text>
</svg>
```
The CSS Custom Properties (`var(--primary-color)`, etc.) are bound to local React states. When the user changes themes on the details panel, the SVG colors update instantly in the browser DOM, bypassing API overhead.
