# GitBook Publishing Guide

These Markdown pages are authored to be published to **[GitBook](https://www.gitbook.com)**. This guide explains the two supported ways to deploy them and the conventions used, so the rendered docs feel consistent.

> 🎯 **Outcome**: after following one path below, your docs are live at `https://<you>.gitbook.io/<space>/`, are versioned next to the code, and updates publish automatically.

## 🧩 How this documentation is organised

Every page is a normal Markdown file inside `docs/`:

```
docs/
├── SUMMARY.md                      # GitBook table of contents (source of truth for the sidebar)
├── README.md                       # landing page (Introduction)
├── developer-manual/               # "Developer Manual" group
│   ├── technology_stack.md
│   ├── quickstart.md
│   ├── local_development.md
│   ├── configuration.md
│   ├── database_migrations.md
│   ├── core_crosscutting.md
│   ├── deployment.md
│   └── gitbook_publishing.md
├── architecture/                   # "Architecture" group
└── contributing/
```

Notes on conventions used (see also [Conventions](../architecture/conventions.md)):

* **Folders = GitBook groups**; `SUMMARY.md` defines the order and grouping of the sidebar.
* Emoji 🧰 / 🚀 / ✅ prefix the page headings to reinforce purpose (scannable).
* Callouts are plain Markdown block quotes — `> 💡 Tip:`, `> ⚠️ Caution:`, `> ✅ Verdict:`.
* Relative links use GitBook-style paths (e.g. `../architecture/auth.md`).

> 💡 GitBook automatically exposes each page in Markdown (append `.md`), and a machine-readable `llms.txt` index — great for LLM tooling and offline review.

## ✅ Recommended workflow: Git sync (GitHub-connected space)

GitBook can **sync a folder of a GitHub repository** and turn it into a published space. It is the most maintainable setup (docs live beside the code, PR-reviewable).

### Steps

1. **Push this `docs/` folder to your repository.** E.g. `main` branch at `docs/`.

2. **Create a GitBook space.**
   Go to <https://www.gitbook.com> → *New space* → choose the **"Git"** integration.

3. **Connect the repository.**
   Select your GitHub repo (authorize GitBook to read it) and set:
   * Branch: choose the branch you want to publish from (e.g. `main` or a dedicated `docs`).
   * Path / Root: `docs`
   * Content format: **Markdown**

4. **Let GitBook import.** It will read `docs/SUMMARY.md` as the table of contents.

5. **Publish** your space (Publish → *Publish updates*). GitBook hosts it at a URL like `https://<space>.gitbook.io/docs`.

6. **Enable automatic updates** (recommended): turn on *auto-publish on push* so every merge into `main` republishes the docs.

> ✅ **Why this is preferred**: single source of truth, no manual content uploads, and Markdown-only (no lock-in to GitBook-specific editing tricks).

## 🧰 Alternative: create from folder (GitBook editor)

If you don't want Git sync, GitBook can generate a space from these files via its API/import tools:

1. At *Create space*, choose **"Import"** (or the GitBook CLI/`API Import`).
2. Provide the structured Markdown. GitBook reads `README.md` as the landing page and `SUMMARY.md` for the sidebar.
3. Because the docs use only portable Markdown, the rendering is faithful.

> When importing by hand, prefer `SUMMARY.md` over raw *drag-and-drop* so the sidebar ordering is preserved exactly.

## 🔍 After it is live

* Verify the four groups render: **Developer Manual**, **Architecture**, **Contributing**.
* Check every **relative link** resolves (lint with a Markdown link checker in CI if you like).
* For SEO/AI discovery, GitBook generates a sitemap and an `llms.txt` automatically.

## 🏗️ Editing tips for the future

* **Add a page**: create a new `.md` under a group folder, then add a `* [Title](relative/path.md)` line in `SUMMARY.md`.
* **Rename a page**: update the file and fix its `SUMMARY.md` entry + incoming links (GitBook does not auto-redirect).
* **Reorder**: change the order of lines in `SUMMARY.md`.
* **Keep it evergreen**: if an env var, migration, or endpoint changes, update the matching page in the same PR as the code.

> ⚠️ Do **not** edit live content in the GitBook editor if you use Git sync — your local commit will overwrite it. Always edit in the repo and let the sync push it.

## 🤖 Deploying for a team / CI

If you already use GitHub Actions (see [Deployment](https://github.com/ItsZcx/FastAPI-Template/blob/main/.github/workflows/ci.yml)), you can optionally enforce documentation hygiene in the same pipeline — e.g. link checks on `docs/`. Installing GitBook's `gitbook` CLI is not required for the hosted Git-sync flow described above.
