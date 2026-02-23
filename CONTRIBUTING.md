# Contributing to BookHive

Thanks for contributing to the BookHive capstone project!

## Branching strategy

We use a simple sprint/task branch scheme:

- `main` — production / sprint releases
- `develop` — integration branch for current sprint work
- Task branches created from `develop`:
  - `task/x.y-short-name` (x = sprint, y = task)
  - `bug/short-description`
  - optional: `docs/...`, `chore/...`, `refactor/...`

### Flow

1. Branch off `develop`
2. Work locally, commit small logical changes
3. Push your branch
4. Open a PR into `develop`
5. After each sprint, `develop` is merged into `main`

## Pull requests

### Before opening a PR

- Pull latest `develop`
- Merge `develop` into your work branch such as task/...
- Run formatting + linting
- Run tests (if applicable)
- Push your branch now synced with develop to your work branch
- Now feel free to open a pull request into `develop` as the base branch

#### Backend checks

```bash
cd backend
source .venv/Scripts/activate
ruff check .
ruff format .
python -m unittest discover -s tests -p "test_*.py" -v
```

#### Frontend checks

```bash
cd frontend
npm run lint
npm run format
npm run test:unit
```

### PR rules

- PRs must pass CI checks
- PRs require review (CODEOWNERS)
- Prefer squash merges to keep history clean
- Link the Trello card in the PR body

### Commit style

- feat: ...
- fix: ...
- docs: ...
- chore: ...
- refactor: ...

### Security note

- Do not commit `.env` files or secrets
- Use `.env.example` for documenting variables
- Keep tokens/passwords out of logs and screenshots
