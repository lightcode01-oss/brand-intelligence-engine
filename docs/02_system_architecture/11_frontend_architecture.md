# Frontend Architecture: Nomen

This document details the frontend architecture of Nomen, built using **Next.js 15 (App Router)**, **React 19**, and **TypeScript**.

---

## 1. Directory Structure

```text
apps/web/
├── app/                        <-- Next.js 15 routing folder
│   ├── layout.tsx              <-- Global layout (Providers, Fonts)
│   ├── page.tsx                <-- Landing Page (Server Component)
│   ├── search/                 <-- Search Results Page (Client/Server hybrid)
│   └── dashboard/              <-- User Dashboard Pages (Client-rendered Shell)
├── components/                 <-- Reusable UI elements
│   ├── ui/                     <-- shadcn primitives (button, dialog, input)
│   ├── search/                 <-- Search specific components (card, sidebar)
│   ├── branding/               <-- Logo preview and mockup frames
│   └── layout/                 <-- Header, Sidebar, Footer wrappers
├── hooks/                      <-- Custom React hooks
│   ├── use-search-polling.ts   <-- Polls Celery tasks for completion
│   └── use-brand-palette.ts    <-- Color palette generation helpers
├── lib/                        <-- Utility code
│   ├── api-client.ts           <-- Axios/Fetch wrapper with JWT handling
│   └── utils.ts                <-- Tailwind merge helpers
├── store/                      <-- Zustand store (Local UI states)
│   └── mockup-store.ts         <-- Shared styling settings for visual mockups
├── styles/
│   └── globals.css             <-- Global CSS system and custom gradients
├── public/                     <-- Static assets
└── package.json
```

---

## 2. Server vs. Client Component Boundaries

To optimize performance, SEO, and initial page load (FCP), we separate layout rendering from interactive state boundaries:

### 2.1. Server Components (RSC)
- **Marketing Pages (`/`, `/about`, `/pricing`)**: Delivered as static HTML with Tailwind styling. Contains zero runtime JavaScript for high performance and SEO.
- **API Layout Prefetching**: Prefetches user metadata on `/dashboard` load, preventing layout shift before child client components mount.

### 2.2. Client Components (`"use client"`)
- **Search Panel (`/search/page.tsx`)**: Manages real-time filtering, layout grids, and active drawers.
- **Mockup Canvas (`/search/[name]/page.tsx`)**: Coordinates Canvas element rendering, HSL color palette swaps, and interactive preview triggers.
- **Forms & Auth Modals**: User inputs, validation states, and auth submissions.

---

## 3. State Management Matrix

| State Type | Solution | Rationale |
| :--- | :--- | :--- |
| **Server State** | TanStack Query v5 | Handles fetch caching, automatic background refetching of portfolios, API polling mechanisms, and query invalidation on mutation. |
| **Search Queries** | URL Search Parameters | Storing inputs like `?q=brand+intelligence&style=compound` directly in the URL enables direct page bookmarking and back/forward navigation. |
| **UI Configs** | Zustand | A lightweight global store is used to share visual mockup states (e.g. active color hexes, active typography selection) across sidebar and mockup canvas. |
| **Simple States** | React `useState` | Isolated component toggles (e.g., dropdown open, modal state). |

---

## 4. Brand Visualization Layer (Mockups)

Rather than rendering heavy iframe applications to showcase names in context, the frontend uses highly optimized CSS Grid layouts and Vector graphics:
- **Interactive CSS Panels**: Pre-built mockups of landing page headers, business card structures, and phone containers styled with Tailwind.
- **Typography Engine**: Generates dynamic stylesheet link injections pointing to Google Fonts:
  ```typescript
  const link = document.createElement('link');
  link.href = `https://fonts.googleapis.com/css2?family=${selectedFont}:wght@400;700&display=swap`;
  link.rel = 'stylesheet';
  document.head.appendChild(link);
  ```
- This allows instantaneous typography swaps on mockups without reloading the underlying page.

---

## 5. Animations & Micro-interactions
We leverage **Framer Motion** to deliver a premium, premium feel:
- **Staggered Entry**: Search result cards fade in sequentially:
  ```typescript
  const cardVariants = {
    hidden: { opacity: 0, y: 15 },
    visible: (i: number) => ({
      opacity: 1,
      y: 0,
      transition: { delay: i * 0.05 }
    })
  };
  ```
- **Smooth Layout Morphing**: When clicking a name, the detail card expands or slides out a side drawer seamlessly using layout transitions (`layoutId`).
- **Pulsing Load States**: Dynamic skeleton elements matching the shape of name cards pulse smoothly while polling Celery.
