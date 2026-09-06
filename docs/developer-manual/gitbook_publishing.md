# GitBook Publishing Guide

These Markdown pages are published to **[GitBook](https://www.gitbook.com)** through GitBook's **Site Git Sync**. This guide explains how the repository maps onto the published book and how to keep editing consistent.

> 🎯 **Outcome**: content lives in this repository under `docs/`; pushing to `main` republishes it automatically at your GitBook site URL (e.g. `https://zcx.gitbook.io/zcx-docs`).

## 🧩 How this documentation is organised

The docs are published as **one GitBook book (a single space)** rooted at `docs/`. A `gitbook-docs.yaml` maps that space to the `docs/` directory, and a `SUMMARY.md` at the space root defines the reading order and groupings.

Because it is a single space, every page in the book lives in the **same** content directory. That is what lets pages link to each other using normal relative Markdown links (`<file>.md`), which GitBook rewrites into **internal in-site links** rather than GitHub links.

```
docs/
├── gitbook-docs.yaml               # GitBook site config: single space -> ./ (this dir)
├── SUMMARY.md                      # space table of contents (reading order & groups)
├── README.md                       # Introduction (landing page / top of the book)
├── developer-manual/               # "Developer Manual" group pages
│   ├── technology_stack.md
│   ├── quickstart.md
│   ├── local_development.md
│   ├── configuration.md
│   ├── database_migrations.md
│   ├── core_crosscutting.md
│   ├── deployment.md
│   └── gitbook_publishing.md       # this page
├── architecture/                   # "Architecture" group pages
└── contributing/                   # "Contributing" group pages
```

Notes on conventions:

* **One space, one directory.** Keep all authorable pages inside `docs/`; `docs/gitbook-docs.yaml` maps a single space to that directory (`content.directory: .`).
* **Navigation is driven by `SUMMARY.md`.** Add pages there under the right group heading. `## ` headings create groups in the sidebar.
* **Linking internally** — use the **relative Markdown path** to the target page. Pages in the same space link with normal relative paths, e.g. `[Quickstart](quickstart.md)` (same folder) or `[Conventions](../architecture/conventions.md)`. Because everything is one space, GitBook resolves these to internal links automatically.
* Emoji 🧰 / 🚀 / ✅ and callouts (`> 💡 Tip:`) are encouraged for scannability.

> ⚠️ **Why one space?** GitBook keeps each mapped space directory **self-contained** and does not resolve relative links that leave it. When the docs were split into several sibling spaces, links between them leaked out to GitHub. A single space makes cross-page links internal.

## ✅ How publishing works (Git sync)

1. **Structure** — `docs/gitbook-docs.yaml` declares the space and points `content.directory` at the project directory (`./`). GitBook reads it as the project directory when configured to root at `docs/`.
2. **Navigation** — `docs/SUMMARY.md` at that directory defines the book's order and groups.
3. **Content** — the Markdown files are read as pages of that one space.
4. **Sync** — pushing to the synced branch republishes. With auto-publish on, a merge to `main` updates the live site.
5. **Confirm** — open your site (e.g. `https://zcx.gitbook.io/zcx-docs`) and check the pages and links; trigger a re-sync from GitBook if needed.

> ℹ️ GitBook may have created/generated its own `SUMMARY.md` when you changed navigation in the editor. Keep the file under Git Sync pointed at the one you edit here to avoid conflicts.

## 🔍 After a change

* Verify the sidebar reflects `docs/SUMMARY.md`’s groupings: **Introduction**, then **Developer Manual / Architecture / Contributing** groups.
* Click each cross-page link to confirm it navigates **inside** the site (not to GitHub).

## 🏗️ Editing tips

* **Add a page** — drop a `.md` file under a group folder, then add a single line in `docs/SUMMARY.md` (and link to it from related pages).
* **Reorder pages / groups** — reorder the lines / headings in `docs/SUMMARY.md`.
* **Rename a page** — update its file, its `SUMMARY.md` entry, and any in-page links to it.
* **Keep it evergreen** — update the matching page in the same PR as the code/env/migration change.

> ⚠️ Avoid editing *published* content directly in the GitBook editor if you use Git Sync — your next local commit overwrites it. Edit in the repo and let the sync push it.
