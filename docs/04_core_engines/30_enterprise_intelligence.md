# Enterprise Intelligence & Analytics Platform

This document describes Nomen's Phase 4.1 Enterprise analytics, insights, recommendations, admin dashboard, saved reports, and provider monitoring structures.

---

## 1. Analytics & Monitoring Architecture

Enterprise telemetry reads metrics from database models (`GenerationJob`, `GeneratedName`, `BrandScore`, `Export`, `WorkspaceMember`, `CreditTransaction`) to map live statistics:

- **Generations volumes**: Cumulative counts of names generated inside the workspace.
- **Credit consumption**: Time-series logs of workspace debit operations.
- **Success rates**: The percentage of async celery generation tasks resolving with state `SUCCESS`.
- **AI performance monitoring**: Tracks average latency milliseconds and cost estimates across providers (`gemini-1.5-flash`, `gpt-4o`, `claude-3-sonnet`).

---

## 2. AI Insights Engine

Exposes naming suggestions analytics using the `InsightsEngine`:
- **Trends analysis**: Computes style preferences (e.g. abstract vs compound) and duplicate candidate ratios.
- **Recommendations generation**: Offers structural suggestions:
  - *"Shorter names perform 17% better in trademark clearances."*
  - *"Technology companies prefer 2 syllable names."*
  - *"Finance brands tend toward Latin-inspired names."*

---

## 3. Recommendation Engine

Provides customized clearance tips based on prompt profiles:
- Suggests optimized alternative prompts.
- Identifies slogan options.
- Matches vector typography (Outfit, Inter) and brand color hues.

---

## 4. Saved Reports System

Allows users to create and download historical workspace summaries:
- **Formats supported**: PDF, Markdown, JSON, CSV.
- **Data contents**: Summarizes total jobs, Brand Score parameters averages, and AI recommendations.
- **Versioning**: Tracks multiple updates to the same report name using incremental version counters.

---

## 5. Security & Administrative Controls

The admin dashboard (`/admin`) handles enterprise settings:
- **User Roles management**: Dynamic updates to role levels (e.g. `FREE_USER` to `PRO_USER`).
- **Maintenance Mode**: An administrative toggle immediately updating `settings.MAINTENANCE_MODE` to return `503 Service Unavailable` for all incoming client queries.
- **Audit logs feed**: Searchable request audit trails filtering actor actions and trace request IDs.
