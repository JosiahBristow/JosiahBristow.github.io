# Josiah Bristow — personal blog

Static blog about Arch Linux, Linux tools, and developer life.
Hosted on [GitHub Pages](https://josiahbristow.github.io/), no build step required.

- **Stack:** Pure HTML + CSS + JS, no frameworks
- **Theme:** [Catppuccin](https://github.com/catppuccin/catppuccin) Latte (light) / Mocha (dark), persisted in localStorage
- **i18n:** Chinese & English, toggled via floating button. Keys in [`lang.js`](lang.js)

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
| `admin.html` | Admin dashboard |

## Content management

[`manage.py`](manage.py) is the unified CLI for all content:

```sh
python manage.py build          # Regenerate all HTML pages
python manage.py serve          # Preview at http://localhost:8000
python manage.py import         # Import existing content into data store

# Posts
python manage.py posts sync              # Sync from cnblogs
python manage.py posts add post.md       # Add custom markdown post
python manage.py posts list/edit/delete

# Books, photos, friends
python manage.py books/photos/friends add/list/edit/delete
```

Content is stored as JSON in [`data/`](data/).

## Auto-sync

A [GitHub Actions workflow](.github/workflows/sync.yml) runs daily at 6:00 UTC
to sync posts from [博客园](https://www.cnblogs.com/JosiahBristow).

## Local development

```sh
python -m http.server 8000
# or
npx serve .
```

## License

© 2024–2026 Josiah Bristow
