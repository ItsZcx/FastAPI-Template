# Contributing

Thanks for helping improve FastAPI-Template. Pull requests that follow these conventions merge cleanly into CI.

## Branch strategy

Develop on a feature branch off `main`, then open a pull request.

```text
main ─────────────────────────►
      \ feat/12-add-xyz         \  PR merges back to main
```

* `main` is the only long-lived branch. It always passes CI.
* Work branches follow `type/issue-short-description`. See the naming rules.
* The template assumes no `dev` or staging branch. Add one between feature branches and `main` if your team grows.

If you ship your own product from this template, add a `dev` integration branch between feature branches and `main`, especially with multiple contributors.

## Naming

Branches, commits, and pull request titles use a `type` prefix. This powers labels, changelogs, and triage.

### Accepted types

| Type       | Meaning                               |
| ---------- | ------------------------------------- |
| `feat`     | a new feature                         |
| `fix`      | a bug fix                             |
| `hotfix`   | an urgent critical fix                |
| `refactor` | restructure without behaviour change  |
| `style`    | formatting and non-functional changes |
| `test`     | test-only changes                     |
| `docs`     | documentation changes                 |
| `chore`    | tooling, CI, dependencies             |

### Commit and pull request title

```
<type>(<optional-scope>): short description
```

Examples:

```
feat(auth): add refresh token support
fix(db): make email unique index on users
docs(ci): document GitHub Actions workflow
```

### Branch name

```
<type>/<issue-number>-<short-description>
```

Examples:

```
feat/12-add-refresh-tokens
fix/10-username-not-updating-in-db
docs/7-clarify-quickstart
```

The repository history already follows this convention, such as `feat: add template auth` and `fix: Docker errors`. Keep it that way.

## Local setup

See [Local Development](../developer-manual/local_development.md) for the full walkthrough. The minimum:

```bash
uv sync
cp .env.example .env
docker compose up -d postgres
uv run alembic upgrade head
uv run uvicorn src.main:app --reload --port 8080
```

Read [Conventions](../architecture/conventions.md) before you change code. It covers formatting, Pydantic v2 style, and the SQLAlchemy style.

## Before you open the pull request

```bash
uv run ruff check .
uv run ruff format --check .
uv run pytest               # existing and new tests
```

Install the pre-commit hooks to catch issues on every commit:

```bash
uv run pre-commit install
```

## Checklist for a pull request

- [ ] One logical change per request, with a clear `feat(...)` or `fix(...)` title
- [ ] Follows [Conventions](../architecture/conventions.md)
- [ ] New model is under `src/<package>/models.py` and discovered automatically, with a migration generated and `alembic upgrade head` verified
- [ ] Tests pass and match `tests/` to `src/`
- [ ] Ruff lint and format pass
- [ ] Docs updated when the change alters environment variables, endpoints, or the package layout
- [ ] Rate-limit, pagination, or auth changes reviewed for effects on other packages

## Communication

* Prefer GitHub Issues for proposals and bugs, and pull requests for concrete changes.
* For architecture questions, open an issue with a `[RFC]` prefix so others weigh in before a large diff.
* Mention how you tested, and attach logs.

## By contributing

Your contributions are licensed under the same terms as the project's [MIT LICENSE](../LICENSE).
