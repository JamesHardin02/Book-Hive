# Definition of Done (DoD)

Use this checklist for Trello cards and PRs.

## Code quality

- [ ] Code compiles/runs locally (no runtime crash on startup)
- [ ] Formatting run (Prettier / Ruff / ESLint) and no new lint warnings
- [ ] CI checks pass (lint/format/tests)
- [ ] No secrets committed (no `.env`, keys, passwords, tokens)

## Tests

- [ ] Unit tests added/updated when behavior changes
- [ ] Tests pass locally (`npm run test`)

## Documentation

- [ ] README updated if setup/run behavior changed
- [ ] RUNBOOK updated if a new common failure mode was introduced
- [ ] Any new env vars are documented in `.env.example` and docs

## Review + tracking

- [ ] Trello card linked in PR
- [ ] Task ID referenced in PR (e.g., 1.4)
- [ ] PR reviewed/approved (CODEOWNERS)
- [ ] Squash-merge preferred (clean history)
