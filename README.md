# Josiah Bristow — personal blog

Static blog hosted on [GitHub Pages](https://josiahbristow.github.io/).  
No build step required — files are served as-is.

A blog about Arch Linux, Linux tools, and developer life. Built with pure HTML + CSS + JS, themed with [Catppuccin](https://github.com/catppuccin/catppuccin) (Latte / Mocha), with i18n support for Chinese and English.

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

## Usage

### Browse locally

Serve the root directory with any static file server:

```sh
python -m http.server 8000
# or
npx serve .
```

### Sync posts from cnblogs

[`sync_posts.py`](sync_posts.py) scrapes [博客园](https://www.cnblogs.com/JosiahBristow) and regenerates all blog listings and post pages.

```sh
python sync_posts.py
```

Requires Python 3.8+ (stdlib only, no external dependencies).  
Downloads images to `posts/images/` and rewrites `src` attributes to local paths.

### i18n

Pages include Chinese and English translations. Toggle with the floating `EN`/`中` button.  
Add new translation keys in [`lang.js`](lang.js).

### Theme

Toggle between light (Latte) and dark (Mocha) with the floating moon/sun button.  
Persisted in `localStorage`.

## Content management (CLI)

[`manage.py`](manage.py) is the unified content manager — add, edit, delete, and sync all content from the command line.

```sh
# First run: import existing content from HTML pages
python manage.py import
python manage.py build

# Sync posts from cnblogs
python manage.py posts sync

# Add a custom blog post (markdown)
python manage.py posts add post.md

# List / edit / delete posts
python manage.py posts list
python manage.py posts edit <id>
python manage.py posts delete <id>

# Manage books (interactive prompts)
python manage.py books add
python manage.py books list
python manage.py books edit <id>
python manage.py books delete <id>

# Add a photo
python manage.py photos add photo.jpg "Caption"
python manage.py photos list
python manage.py photos delete <id>

# Manage friend links (interactive prompts)
python manage.py friends add
python manage.py friends list
python manage.py friends edit <id>
python manage.py friends delete <id>
```

After any change, run `python manage.py build` to regenerate all HTML pages.
Run `python manage.py serve` to preview locally at `http://localhost:8000`.

Deduplication: when syncing from cnblogs and adding custom markdown posts,
if title and content (ignoring image URLs) match, only one is kept.

## License

© 2024-2026 Josiah Bristow.
