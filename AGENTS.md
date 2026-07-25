# AGENTS.md — github_page

Static blog for JosiahBristow, hosted on GitHub Pages. No build step — files served as-is.

## Structure

All pages share `style.css`, `script.js`, `lang.js`. No inline `<style>`.

```
index.html        home — blog listing (paginated, 7 posts/page)
archive.html      posts grouped by year
categories.html   posts grouped by category
about.html        profile and bio
sync_posts.py     scraper: fetches cnblogs RSS → regenerates HTML pages
```

## Key conventions

- **Nav `.active` class** — current page must have this class.
- **i18n** — elements with `data-i18n="key"` translated by `lang.js`. Add new keys to the `i18n` object there. Toggle button id: `langToggle`.
- **Theme** — `#themeToggle` toggles `data-theme` on `<html>`, persisted in localStorage. Catppuccin Latte (light) / Mocha (dark).
- **Generated page markers** — `<!-- CONTENT_MAIN -->` and `<!-- SIDEBAR -->` delimit the sections `sync_posts.py` injects into. Keep markers intact when editing by hand.
- **Font** — JetBrains Mono via Google Fonts preconnect in `<head>`.

## sync_posts.py

Requires Python 3.8+ stdlib only (zero external deps). Scrapes cnblogs blog listing pages and:

1. Generates full post pages under `posts/{id}.html` (linked from listings instead of cnblogs)
2. Downloads images to `posts/images/`
3. Injects content into `index.html`, `archive.html`, `categories.html` via marker comments

Run:

```sh
python sync_posts.py
```

Post pages use template `POST_PAGE_TPL` and share `style.css`, `script.js`, `lang.js` via relative `../` paths. Image `src` attributes in post body are rewritten to local `images/` paths.

No CI workflow is set up yet — this is intended for a scheduled GitHub Actions run.

## Tooling

No package manager, framework, or test/lint/typecheck commands exist. If you introduce a build system, add verification commands here.

## Generated files

Per `.opencode/.gitignore`: `node_modules`, `package.json`, `package-lock.json`, `bun.lock` should not be committed.
