# GitBook Publishing Guide

These Markdown pages are published to **[GitBook](https://www.gitbook.com)** through GitBook's **Site Git Sync**. This guide explains how the repository maps onto the site, and the conventions to follow so edits stay consistent.

> 🎯 **Outcome**: content lives in this repository under `docs/`; a `gitbook-docs.yaml` there describes the site; pushing to `main` republishes it automatically at your GitBook site URL (e.g. `https://zcx.gitbook.io/zcx-docs`).

## 🧩 How this documentation is organised

Each **space** is backed by one content directory inside `docs/` (a directory is read as one "book" of pages). An **Introduction** space acts as the landing/hub; the rest map to the guides.

```
docs/
├── gitbook-docs.yaml               # GitBook site config: maps directories onto spaces
├── introduction/                   # "Introduction" space  (site landing / default)
│   └── README.md
├── developer-manual/               # "Developer Manual" space
│   ├── technology_stack.md
│   ├── quickstart.md
│   ├── local_development.md
│   ├── configuration.md
│   ├── database_migrations.md
│   ├── core_crosscutting.md
│   ├── gitbook_publishing.md       # this page
│   └── deployment.md
├── architecture/                   # "Architecture" space
└── contributing/                   # "Contributing" space
```

The authoritative mapping lives in `gitbook-docs.yaml`. Check it after adding or removing a space:

```yaml
site:
  title: FastAPI Template
  structure:
    - { type: space, key: introduction, title: Introduction, path: introduction, default: true,
        content: { directory: ./introduction } }
    - { type: space, key: developer-manual, title: Developer Manual, path: developer-manual,
        content: { directory: ./developer-manual } }
    - { type: space, key: architecture, title: Architecture, path: architecture,
        content: { directory: ./architecture } }
    - { type: space, key: contributing, title: Contributing, path: contributing,
        content: { directory: ./contributing } }
```

Notes on conventions:

* **One directory = one space.** Add new pages to an existing space's folder, or create a new folder and register it in `gitbook-docs.yaml` as a new space.
* `content.directory` paths are **relative to the `docs/` project directory** (e.g. `./introduction` reads `docs/introduction` in the repo).
* Emoji 🧰 / 🚀 / ✅ prefix headings to keep pages scannable; callouts are plain Markdown block quotes (`> 💡 Tip:`, `> ⚠️ Caution:`).
* Exactly **one space should be `default: true`** — the one opened when the site is visited. Currently the **Introduction** space.

> 💡 GitBook automatically exposes each page in Markdown and generates a sitemap and an `llms.txt` index.

## ✅ How publishing works (Git sync)

1. **Structure** — `docs/gitbook-docs.yaml` names the space layout. GitBook reads it as the project directory when configured to root at `docs/`.
2. **Content** — each space's `content.directory` is read on import.
3. **Sync** — pushing to the synced branch republishes. With auto-publish on, merges to `main` update the live site automatically.
4. **Confirm** — after a push, open your site (e.g. `https://zcx.gitbook.io/zcx-docs`) and check the new content appears; if not, trigger a re-sync from GitBook.

> ⚠️ If content does not appear after moving a space's directory, check that the `content.directory` value still exists **relative to the `docs/` folder** and re-run the sync.

## 🔍 After a change

* Verify the site layout matches `docs/gitbook-docs.yaml`: **Introduction**, **Developer Manual**, **Architecture**, **Contributing**.
* Open the **Introduction** page and confirm its navigation links point at the other spaces.
* If you add cross-space navigation, use the page's deployed URL or relative paths within a space — GitBook renders each space separately.

## 🏗️ Editing tips

* **Add a page** — drop a `.md` file into the matching space folder under `docs/`.
* **Add a whole space** — create `docs/<name>/…` and add a `space` entry to `gitbook-docs.yaml`.
* **Reorder spaces** — change the order of entries in `docs/gitbook-docs.yaml`.
* **Rename a space/page** — update its path/title in `gitbook-docs.yaml` and fix incoming links.
* **Keep it evergreen** — update the matching page in the same PR as the code/env/migration change.

> ⚠️ Do **not** hand-edit published content in the GitBook editor if you use Git sync — your next local commit will overwrite it. Edit in the repo and let the sync push it.
