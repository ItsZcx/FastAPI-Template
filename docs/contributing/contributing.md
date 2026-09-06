# Contributing

Thanks for wanting to help improve **FastAPI-Template**! This guide mirrors the FAS contributor workflow you may have seen elsewhere, adapted for this single-repo Python template. PRs that respect these conventions merge cleanly into CI.

## 📂 Branch strategy

This template keeps it simple: you develop on feature branches off `main` and open a pull request.

```text
main ─────────────────────────►
      \ feat/12-add-xyz         \  PR → merge back to main
```

* `main` — the only long-lived branch; always passes CI.
* Work branches — `type/issue-short-description` (see naming below).
* A `dev`/staging branch can be introduced later if a team grows; the template doesn't assume one.

> ✅ **Tip**: if you plan to ship your own product from this template, introduce a `dev` (integration) branch between feature branches and `main`, especially with multiple contributors.

## ✍️ Naming: the shared convention

All **branches, commits and PR titles** use a `type` prefix. This powers labels, changelogs, and at-a-glance triage.

### Accepted types

| Type            | Meaning                                 |
| --------------- | --------------------------------------- |
| `feat`          | a new feature                           |
| `fix`           | a bug fix                               |
| `hotfix`        | an urgent critical fix                  |
| `refactor`      | restructure without behaviour change    |
| `style`         | formatting / non-functional             |
| `test`          | test-only changes                       |
| `docs`          | documentation changes (like this page!) |
| `chore`/`infra` | tooling, CI, deps                       |

### Commit & PR title

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

> Commits in this repo's history already follow this (`feat: add template auth`, `fix: Docker errors …`) — keep it that way.

## 🧑‍💻 Local setup (start dev quickly)

See [Local Development](../developer-manual/local_development.md) for a full walkthrough. Minimum:

```bash
uv sync
cp .env.example .env
docker compose up -d postgres
uv run alembic upgrade head
uv run uvicorn src.main:app --reload --port 8080
```

> **Tip**: read the [Conventions](../architecture/conventions.md) page before touching code — formatting, Pydantic v2 style, and ORM style are all covered there.

## 🧪 Before you open the PR

```bash
uv run ruff check .
uv run ruff format --check .
uv run pytest               # existing + your new tests
```

Install the pre-commit hooks to catch issues on every `git commit`:

```bash
uv run pre-commit install
```

## 🔁 Checklist for a PR to `main`

- [ ] One logical change per PR; clear `feat(...)`/`fix(...)` title.
- [ ] Code follows [Conventions](../architecture/conventions.md).
- [ ] New model → added to `alembic/env.py` imports; migration generated; `alembic upgrade head` verified.
- [ ] Tests added/updated and green, matching `tests/` to `src/`.
- [ ] Ruff lint & format pass.
- [ ] Docs updated if the change alters env vars, endpoints, or the package layout.
- [ ] Rate-limit / pagination / auth changes reviewed for side effects on other packages.

## 🗣️ Communication

- Prefer GitHub Issues for proposals/bugs and PRs for concrete changes.
- For cross-cutting architecture questions, open an issue with the `[RFC]` prefix so others can weigh in before a large diff.
- Mention how you tested and attach logs where relevant (logs help the most).

## 📄 By contributing

You agree that your contributions are licensed under the same terms as the project's [MIT LICENSE](../LICENSE).
