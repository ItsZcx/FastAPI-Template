# GitBook Publishing Guide

These Markdown pages publish to [GitBook](https://www.gitbook.com) through GitBook's Site Git Sync. This guide explains how the repository maps onto the published book and how to keep edits consistent.

Content lives in this repository under `docs/`. Pushing to `main` republishes it at your GitBook site URL, for example `https://zcx.gitbook.io/fastapi-template`.

## How this documentation is organised

The docs publish as one GitBook book, a single space, rooted at `docs/`. `gitbook-docs.yaml` maps that space to the `docs/` directory. `SUMMARY.md` at the space root defines the reading order and groups.

Because it is one space, every page lives in the same content directory. Pages link to each other with ordinary relative Markdown links such as `configuration.md`. GitBook rewrites these into internal in-site links, not GitHub links.

```
docs/
├── gitbook-docs.yaml               # GitBook site config: single space pointing at .
├── SUMMARY.md                      # reading order and groups
├── README.md                       # Introduction, the landing page
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

Conventions:

* One space, one directory. Keep every authorable page inside `docs/`. `gitbook-docs.yaml` maps the single space there with `content.directory: .`.
* `SUMMARY.md` drives navigation. Add pages there under the right group heading. `##` headings create groups in the sidebar.
* Link internally with the relative Markdown path. `[Quickstart](quickstart.md)` for the same folder, `[Conventions](../architecture/conventions.md)` for a sibling. GitBook resolves these to internal links.

Why one space? GitBook keeps each mapped space directory self-contained and does not resolve relative links that leave it. When the docs lived in several sibling spaces, links between them leaked out to GitHub. One space keeps cross-page links internal.

## How publishing works

1. `gitbook-docs.yaml` declares the space and points `content.directory` at the project directory.
2. `SUMMARY.md` in that directory defines the book's order and groups.
3. The Markdown files become the pages of that one space.
4. Pushing to the synced branch republishes. With auto-publish on, merging to `main` updates the live site.
5. Open your site and check the pages and links. Trigger a re-sync from GitBook if needed.

GitBook may generate its own `SUMMARY.md` when you change navigation in the editor. Keep Git Sync pointed at the file you edit in the repo to avoid conflicts.

## After a change

* Check that the sidebar matches the groupings in `SUMMARY.md`.
* Click each cross-page link to confirm it navigates inside the site, not to GitHub.

## Editing tips

* **Add a page.** Drop a `.md` file under a group folder, then add a line in `SUMMARY.md`.
* **Reorder pages and groups.** Reorder the lines and headings in `SUMMARY.md`.
* **Rename a page.** Update its file, its `SUMMARY.md` entry, and any in-page links to it.
* **Keep it current.** Update the matching page in the same pull request as the code, environment, or migration change.

Do not edit published content directly in the GitBook editor when you use Git Sync. Your next local commit overwrites it. Edit in the repo and let the sync push it.
