# Workflow (Branching + PR Process)

## Branching (Sprint-based)

- `main` → production/stable sprint releases
- `develop` → active sprint integration branch
- feature branches from `develop`:
  - `task/x.y-short-name`
  - `bug/short-description`
  - `docs/...`, `chore/...`, `refactor/...`

## PR Workflow

1. Create a branch from `develop`
2. Make small commits
3. Open PR into `develop`
4. CI runs automatically (lint/format/tests)
5. CODEOWNER review required
6. Squash merge into `develop`
7. At sprint end:
   - `develop` → `main` (sprint release merge)

## When to use `main`

Only merge to `main` during sprint release windows (or emergency hotfixes).

## Checklist expectations

- Code builds/runs locally
- Lint + format passes
- Tests pass (if present)
- Docs updated if behavior changes
