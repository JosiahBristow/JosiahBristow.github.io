# AGENTS.md — github_page

A GitHub Pages site. Currently a blank project with only OpenCode config.

## Directory structure

```
.opencode/
  .gitignore          # ignores node_modules, package.json, lockfiles
  skills/frontend-design/  # UI design guidance for agents (SKILL.md)
style.css             # all styles (Catppuccin Latte/Mocha, shared across pages)
script.js             # theme toggle with localStorage persistence
lang.js               # zh/en i18n toggle with localStorage persistence
index.html            # home — blog post listing
archive.html          # posts grouped by year
categories.html       # posts grouped by category
about.html            # profile and bio
sync_posts.py         # scraper: fetches cnblogs RSS → regenerates HTML pages
.github/workflows/sync.yml  # daily GitHub Actions sync
```

All style lives in `style.css` (avoid inline `<style>`). All pages share `style.css`, `script.js`, and `lang.js`. No build step — files are served as-is from GitHub Pages.

The navbar marks the current page via `.active` class — keep this consistent when adding pages.

Text marked with `data-i18n="key"` is translated by `lang.js`. Add new keys to the `i18n` object in `lang.js`. The toggle button has id `langToggle`.

Generated pages (`index.html`, `archive.html`, `categories.html`) contain marker comments (`<!-- CONTENT_MAIN -->`, `<!-- SIDEBAR -->`) used by `sync_posts.py` to inject content. Keep these markers intact when editing by hand.

No tests, linting, or typechecking established yet.

## Available agent skills

- `frontend-design` — load via `skill` tool when building or reshaping UI. Provides design principles, typography, palette, and layout guidance.

## Tooling

- No package manager, framework, or build tool chosen yet.
- No test, lint, or typecheck commands exist. These need to be established before adding source code.
- If you introduce a build system, add lint/typecheck/test commands to AGENTS.md after verifying they work.

## Generated files

Per `.opencode/.gitignore`: `node_modules`, `package.json`, `package-lock.json`, `bun.lock`, and `node_modules` directories should not be committed.
