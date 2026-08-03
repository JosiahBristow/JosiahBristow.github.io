# Josiah Bristow — personal blog

Static blog about Arch Linux, Linux tools, and developer life.
Hosted on [GitHub Pages](https://josiahbristow.github.io/), no build step required.

- **Stack:** Pure HTML + CSS + JS, no frameworks
- **Theme:** [Catppuccin](https://github.com/catppuccin/catppuccin) Latte (light) / Mocha (dark), persisted in localStorage
- **i18n:** Chinese & English, toggled via floating button. Keys in [`lang.js`](lang.js)
- **Search:** client-side search over posts & books via [`data/search-index.json`](data/search-index.json), triggered by the `🔍` button

## Pages

| Page | Description |
|---|---|
| `index.html` | Blog listing, paginated (7 posts/page) |
| `archive.html` | Posts grouped by year |
| `categories.html` | Posts grouped by category |
| `about.html` | Profile and bio |
| `bookshelf.html` | Book list |
| `gallery.html` | Photo gallery |
| `friends.html` | Friend links |
| `posts/*.html` | Individual blog posts |
| `admin.html` | Admin dashboard (only used via `manage.py serve`) |

## Content management

[`manage.py`](manage.py) is the unified CLI for all content:

```sh
python manage.py build          # Regenerate all HTML pages + search index
python manage.py serve          # Serve site + admin dashboard at http://localhost:8000
python manage.py import         # Import existing content into data store

# Posts
python manage.py posts sync              # Sync from cnblogs
python manage.py posts add post.md       # Add custom markdown post (optional --cover)
python manage.py posts list/edit/delete

# Books, photos, friends
python manage.py books/photos/friends add/list/edit/delete
```

Content is stored as JSON in [`data/`](data/) (`posts.json`, `books.json`,
`gallery.json`, `friends.json`, `categories.json`). `posts/*.html` pages live
under [`posts/`](posts/), with downloaded images in `posts/images/`.

`manage.py serve` starts a local server that serves both the site and the
`admin.html` dashboard (add/edit/delete posts, books, photos, friends right in
the browser). `manage.py posts sync` also exists as an alternative to
[`sync_posts.py`](sync_posts.py).

## Auto-sync

A [GitHub Actions workflow](.github/workflows/sync.yml) runs daily at 6:00 UTC.
It executes [`sync_posts.py`](sync_posts.py), which scrapes posts from
[博客园](https://www.cnblogs.com/JosiahBristow), writes them under `posts/`,
and regenerates `index.html`, `archive.html`, `categories.html`.

## Local development

```sh
python -m http.server 8000
# or
npx serve .
```

## License

© 2024–2026 Josiah Bristow
