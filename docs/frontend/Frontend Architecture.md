# Frontend Architecture Guide: Nomen

This guide details Nomen's frontend directory structure, layouts segmentation, state management, and API clients interceptors.

---

## 1. Routing & Layouts Structure

Nomen segments routing using Next.js 15 App Router grouping slots:

- **`(marketing)`**: Landing page routes using sticky header/footer layouts wrapper.
- **`(auth)`**: Sign-in, verification, and registration views using center-aligned grids background.
- **`(dashboard)`**: Admin panel pages utilizing the collapsable sidebar navigation menu.

---

## 2. API Communication Client (`src/lib/api/`)

The Axios API Client includes automated network layers:
- **Request Correlation**: Generates unique `X-Request-ID` UUID headers to trace requests across the API service log.
- **JWT Refresh Interceptor**: Automatically intercepts HTTP 401 Unauthorized status codes, triggers `/auth/refresh` endpoint to rotate access token cookies, and retries the original request.

---

## 3. Zustand Global States Stores

Global properties are separated into isolated stores:
- `useThemeStore`: Light/dark/system mode tracker.
- `useSidebarStore`: Sidebar collapsed layout toggles.
- `useWorkspaceStore`: Active workspace object parameters.
