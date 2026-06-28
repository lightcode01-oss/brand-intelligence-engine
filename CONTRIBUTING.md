# Contributing to Nomen

Thank you for contributing to Nomen! To maintain a production-grade codebase, please adhere to the following development practices.

---

## 1. Branch Strategy

We follow a structured branching model:
- **`main`**: Production-ready code only. Fully tested, secure, and approved by lead developers.
- **`develop`**: Integration branch for features and fixes.
- **`feature/*`**: New capabilities or architectures (e.g. `feature/phonetic-cache`).
- **`fix/*`**: Bug fixes (e.g. `fix/whois-timeout`).
- **`release/*`**: Preparation logs for new versions (e.g. `release/v0.2.0`).
- **`hotfix/*`**: Emergency production patches branching off `main`.

---

## 2. Conventional Commits Standards

We enforce the **Conventional Commits** specification. Commits must match this syntax:

```text
<type>(<scope>): <description>

[optional body]

[optional footer]
```

### Types
- **`feat`**: A new feature (e.g., `feat(api): add domain status lookup`).
- **`fix`**: A bug fix (e.g., `fix(scorer): solve divide-by-zero on double vowels`).
- **`docs`**: Documentation adjustments (e.g., `docs(setup): specify python paths`).
- **`style`**: White-space, semi-colon additions, formatting changes (no functional modifications).
- **`refactor`**: Code changes that neither fix bugs nor add features.
- **`test`**: Creating or fixing unit/integration test code.
- **`chore`**: Adjusting build tooling, dependencies, or workspace configs (e.g. `chore(deps): update pnpm lock`).

---

## 3. Pull Request Guidelines

1. Make sure all local linters and formatting commands resolve cleanly:
   ```bash
   pnpm run lint
   pnpm run format:check
   ```
2. Your branch must have passing unit tests.
3. Push your branch to GitHub and create a Pull Request targeting the `develop` branch.
4. Fill out the pull request template completely.
5. Obtain at least **one approved review** from a maintainer before merging.
