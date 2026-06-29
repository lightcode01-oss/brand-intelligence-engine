# Frontend Design System Guide: Nomen

This guide details Nomen's centralized frontend design tokens, theme configurations, and custom layout styling values.

---

## 1. Centralized Theme Tokens (`src/config/theme/`)

To guarantee design consistency and avoid arbitrary values, all variables are structured as static properties:

- **`colors.ts`**: Curated colors palette mapping Slate backgrounds and Indigo branding primary hooks.
- **`spacing.ts`**: Standard margin and padding bounds scale (4px grid layout scale).
- **`typography.ts`**: System fonts families (Outfit / Inter) and size/weight scale values.
- **`radius.ts`**: Card edges rounded settings (4px, 8px, 12px, 16px).
- **`shadows.ts`**: Focus shadow and glassmorphism settings.
- **`animations.ts`**: Framer Motion spring presets and hover transition metrics.

---

## 2. Dynamic Colors Mapping (Tailwind variables)

Semantics variables are dynamically bound inside `globals.css`:
- Light Theme: slate backgrounds (`bg-slate-50`), dark slate text (`text-slate-900`), and indigo primary actions.
- Dark Theme: slate backgrounds (`bg-slate-900`), slate text (`text-slate-100`), and indigo primary actions.
