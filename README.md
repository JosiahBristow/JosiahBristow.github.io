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

## How to add content

### ✍️ Add a blog post

**Option A — via cnblogs (recommended):** Write on [博客园](https://www.cnblogs.com/JosiahBristow), then run `python sync_posts.py` to pull it in.

**Option B — manually:** Create `posts/<id>.html` (copy an existing post as template), then insert a matching entry into `index.html`, `archive.html`, and `categories.html` between the `<!-- CONTENT_MAIN -->` / `<!-- /CONTENT_MAIN -->` markers.

### 📚 Add a book

1. Save the cover image to `images/books/<filename>.jpg`
2. Copy a `.book-card` block in `bookshelf.html` (lines 47-57) and fill in title, author, rating, description, and link
3. Update the sidebar stat count (`.stat-value` for books) if needed

```html
<div class="book-card">
  <a href="https://book.douban.com/subject/..." target="_blank" class="book-cover-link">
    <img class="book-cover" src="images/books/<filename>.jpg" alt="书名" loading="lazy">
  </a>
  <div class="book-info">
    <div class="book-title">书名</div>
    <div class="book-author">作者</div>
    <div class="book-rating">⭐ 9.0</div>
    <div class="book-desc">简介文字</div>
  </div>
</div>
```

### 📷 Add a photo

1. Save the image file to `images/gallery/`
2. Copy a `.gallery-item` block in `gallery.html` (lines 43-46) and fill in the path and caption

```html
<div class="gallery-item">
  <img class="gallery-img" src="images/gallery/<filename>.jpg" alt="标题" loading="lazy">
  <div class="gallery-caption">标题</div>
</div>
```

## License

© 2024-2026 Josiah Bristow.
