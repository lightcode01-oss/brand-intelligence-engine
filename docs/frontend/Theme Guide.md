# Theme Management Guide: Nomen

This guide details Nomen's strategy for light, dark, and system theme switching.

---

## 1. Theme Configuration

Nomen tracks theme preferences inside `useThemeStore` and writes selections to local storage (`theme_preference` key).

- **Light Mode**: Modifies the root class to `light`. Semantic colors map to clean backgrounds.
- **Dark Mode**: Modifies the root class to `dark`. CSS styles toggle automatically.
- **System Mode**: Detects matches dynamically:
  ```typescript
  const systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  ```

---

## 2. Dynamic Styles Application

Tailwind utility classes apply automatically in dark contexts by appending the `dark:` prefix:

```tsx
<div className="bg-white dark:bg-slate-950 text-slate-900 dark:text-white" />
```
This guarantees smooth transitions across panels without script calculations.
