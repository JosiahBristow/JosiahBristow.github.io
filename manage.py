#!/usr/bin/env python3
"""manage.py — content manager for JosiahBristow.github.io

Usage:
    manage.py posts sync                   Sync posts from cnblogs
    manage.py posts list                   List all posts
    manage.py posts add <file.md> [--cover <img>]  Add custom markdown post (optional cover)
    manage.py posts edit <id> [--cover <img>]  Edit post cover (--cover for any post, else opens $EDITOR for custom)
    manage.py posts delete <id>            Delete post

    manage.py books list                   List books
    manage.py books add                    Add book (interactive prompts)
    manage.py books edit <id>              Edit book (interactive prompts)
    manage.py books delete <id>            Delete book

    manage.py photos list                  List photos
    manage.py photos add <file> [caption]  Add photo
    manage.py photos delete <id>           Delete photo

    manage.py friends list                 List friends
    manage.py friends add                  Add friend (interactive prompts)
    manage.py friends edit <id>            Edit friend (interactive prompts)
    manage.py friends delete <id>          Delete friend

    manage.py import                       Import existing content into data store
    manage.py build                        Regenerate all HTML pages
    manage.py serve                        Start local dev server on :8000
"""

import os, sys, re, json, hashlib, shutil, subprocess, argparse
import urllib.request, urllib.error
from html import unescape
from collections import defaultdict
from datetime import datetime

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(ROOT, "data")
POSTS_DIR = os.path.join(ROOT, "posts")
IMAGES_DIR = os.path.join(POSTS_DIR, "images")
GALLERY_DIR = os.path.join(ROOT, "images", "gallery")
BOOKS_IMG_DIR = os.path.join(ROOT, "images", "books")

for d in [DATA_DIR, POSTS_DIR, IMAGES_DIR, GALLERY_DIR, BOOKS_IMG_DIR]:
    os.makedirs(d, exist_ok=True)

POSTS_JSON = os.path.join(DATA_DIR, "posts.json")
BOOKS_JSON = os.path.join(DATA_DIR, "books.json")
GALLERY_JSON = os.path.join(DATA_DIR, "gallery.json")
FRIENDS_JSON = os.path.join(DATA_DIR, "friends.json")

CNBLOGS_URL = "https://www.cnblogs.com/JosiahBristow"

CAT_EMOJI = {
    'Arch Linux': '🐧', 'Linux': '💻', 'Python': '🐍', 'Raspberry Pi': '🥧',
}

CATEGORIES_JSON = os.path.join(DATA_DIR, "categories.json")

def _load_categories():
    cats = _load_json(CATEGORIES_JSON)
    if not cats:
        cats = dict(CAT_EMOJI)
        _save_json(CATEGORIES_JSON, cats)
    return cats

def _save_categories(cats):
    _save_json(CATEGORIES_JSON, cats)

INJECT_PAGES = ['index.html', 'archive.html', 'categories.html',
                'bookshelf.html', 'gallery.html', 'friends.html']

MAX_TITLE_PREVIEW = 50

# ═══════════════════════════════════════════════════════════
#  Data helpers
# ═══════════════════════════════════════════════════════════

def _load_json(path):
    if not os.path.exists(path):
        return []
    with open(path, encoding='utf-8') as f:
        return json.load(f)

def _save_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def _next_id(data):
    ids = [x.get('id', 0) for x in data if isinstance(x.get('id'), int)]
    return max(ids) + 1 if ids else 1

def _slug(text):
    s = re.sub(r'[^\w\s-]', '', text.lower())
    s = re.sub(r'[-\s]+', '-', s.strip('-'))
    return s or 'untitled'

def _dir_name(title):
    safe = re.sub(r'[\\/:*?"<>|]', '', title)
    safe = re.sub(r'\s+', '-', safe.strip())
    if len(safe) > 80:
        safe = safe[:80].rstrip('-')
    return safe or 'untitled'

def _fmt_count(n):
    n = int(n)
    if n >= 10000: return f'{n//1000}K'
    if n >= 1000:  return f'{n/1000:.1f}K'
    return str(n)

# ═══════════════════════════════════════════════════════════
#  Content hashing (for dedup)
# ═══════════════════════════════════════════════════════════

def _normalize_html(html):
    """Strip image src URLs, HTML tags, and normalize whitespace."""
    html = re.sub(r'<img[^>]+src="[^"]*"[^>]*>', '', html)
    html = re.sub(r'<[^>]+>', '', html)
    html = re.sub(r'\s+', ' ', html).strip()
    return html.lower()

def _content_hash(html):
    return hashlib.sha256(_normalize_html(html).encode()).hexdigest()

# ═══════════════════════════════════════════════════════════
#  Markdown → HTML (stdlib only)
# ═══════════════════════════════════════════════════════════

def md_to_html(text):
    lines = text.split('\n')
    html_parts = []
    i = 0

    def finish_block(buf, tag):
        if not buf: return ''
        inner = '\n'.join(buf)
        if tag == 'p':
            return f'<p>{inner}</p>\n'
        return f'<{tag}>\n{inner}\n</{tag}>\n'

    def parse_inline(s):
        s = re.sub(r'~~(.*?)~~', r'<del>\1</del>', s)
        s = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', s)
        s = re.sub(r'__(.*?)__', r'<strong>\1</strong>', s)
        s = re.sub(r'\*(.*?)\*', r'<em>\1</em>', s)
        s = re.sub(r'_(.*?)_', r'<em>\1</em>', s)
        s = re.sub(r'`([^`]+)`', r'<code>\1</code>', s)
        s = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', s)
        s = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', r'<img src="\2" alt="\1" loading="lazy">', s)
        return s

    while i < len(lines):
        line = lines[i]

        # fenced code block
        if line.startswith('```'):
            lang = line[3:].strip()
            code_lines = []
            i += 1
            while i < len(lines) and not lines[i].startswith('```'):
                code_lines.append(lines[i])
                i += 1
            i += 1
            code = '\n'.join(code_lines)
            lang_attr = f' class="language-{lang}"' if lang else ''
            html_parts.append(f'<pre><code{lang_attr}>{_escape_html(code)}</code></pre>\n')
            continue

        # horizontal rule
        if re.match(r'^[-*_]{3,}\s*$', line):
            html_parts.append('<hr>\n')
            i += 1
            continue

        # headings
        hm = re.match(r'^(#{1,6})\s+(.+)$', line)
        if hm:
            level = len(hm.group(1))
            text = hm.group(2).strip()
            anchor = re.sub(r'[^\w\u4e00-\u9fff]+', '-', text).strip('-').lower() or 'heading'
            content = parse_inline(text)
            html_parts.append(f'<h{level} id="{anchor}">{content}</h{level}>\n')
            i += 1
            continue

        # blockquote
        if line.startswith('> '):
            qlines = []
            while i < len(lines) and lines[i].startswith('> '):
                qlines.append(lines[i][2:])
                i += 1
            inner = '\n'.join(qlines)
            html_parts.append(f'<blockquote>\n{md_to_html(inner.strip())}\n</blockquote>\n')
            continue

        # unordered list
        ulm = re.match(r'^[-*+]\s+(.+)$', line)
        if ulm:
            items = []
            while i < len(lines):
                m = re.match(r'^[-*+]\s+(.+)$', lines[i])
                if not m: break
                items.append(f'  <li>{parse_inline(m.group(1).strip())}</li>')
                i += 1
            html_parts.append('<ul>\n' + '\n'.join(items) + '\n</ul>\n')
            continue

        # ordered list
        olm = re.match(r'^\d+\.\s+(.+)$', line)
        if olm:
            items = []
            while i < len(lines):
                m = re.match(r'^\d+\.\s+(.+)$', lines[i])
                if not m: break
                items.append(f'  <li>{parse_inline(m.group(1).strip())}</li>')
                i += 1
            html_parts.append('<ol>\n' + '\n'.join(items) + '\n</ol>\n')
            continue

        # paragraph
        if line.strip():
            para = []
            while i < len(lines) and lines[i].strip() and not lines[i].startswith('#'):
                para.append(lines[i])
                i += 1
            html_parts.append(f'<p>{parse_inline(" ".join(para))}</p>\n')
        else:
            i += 1

    return ''.join(html_parts)

def _escape_html(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

def _parse_front_matter(text):
    """Parse YAML-like front matter from markdown content."""
    lines = text.split('\n')
    fm = {}
    body_lines = lines
    if lines and lines[0].strip() == '---':
        end = 1
        while end < len(lines) and lines[end].strip() != '---':
            end += 1
        for line in lines[1:end]:
            m = re.match(r'^(\w+):\s*(.+)$', line)
            if m:
                val = m.group(2).strip().strip('"\'')
                fm[m.group(1).lower()] = val
        body_lines = lines[end+1:]
    return fm, '\n'.join(body_lines).strip()

# ═══════════════════════════════════════════════════════════
#  Post management
# ═══════════════════════════════════════════════════════════

def _load_posts():
    return _load_json(POSTS_JSON)

def _save_posts(posts):
    _save_json(POSTS_JSON, posts)

def _category_for(title):
    kw = [
        ('Flathub', 'Arch Linux'), ('pacman', 'Arch Linux'),
        ('Waydroid', 'Arch Linux'), ('archlinuxcn', 'Arch Linux'),
        ('镜像源', 'Arch Linux'), ('输入法', 'Arch Linux'),
        ('打印机', 'Linux'), ('pip install', 'Linux'),
        ('pygame', 'Python'), ('树莓派', 'Raspberry Pi'),
    ]
    return next((c for k, c in kw if k in title), 'Arch Linux')

def _find_duplicate(posts, title, html_content):
    """Check if a post with similar title+content already exists."""
    new_hash = _content_hash(html_content)
    norm_title = re.sub(r'\s+', '', title).lower()
    for p in posts:
        pt = re.sub(r'\s+', '', p['title']).lower()
        if pt == norm_title and p.get('content_hash') == new_hash:
            return p
    return None

def cmd_posts_list(args):
    posts = _load_posts()
    if not posts:
        print("No posts.")
        return
    print(f"{'ID':<24} {'Source':<10} {'Title':<{MAX_TITLE_PREVIEW}} {'Date':<12}")
    print('-' * 100)
    for p in posts:
        tid = p.get('id', '?')
        src = p.get('source', '?')
        title = p['title'][:MAX_TITLE_PREVIEW]
        date = p.get('date', '?')
        print(f"{tid:<24} {src:<10} {title:<{MAX_TITLE_PREVIEW}} {date:<12}")

def cmd_posts_sync(args):
    """Run sync_posts.py then import into data store."""
    sync_script = os.path.join(ROOT, 'sync_posts.py')
    if not os.path.exists(sync_script):
        print("sync_posts.py not found.")
        return 1
    print("Running sync_posts.py...")
    r = subprocess.run([sys.executable, sync_script], cwd=ROOT)
    if r.returncode != 0:
        print("sync_posts.py failed.")
        return r.returncode
    # Import cnblogs posts into data store
    posts = _load_posts()
    existing_map = {p['id']: p for p in posts if p.get('source') == 'cnblogs'}
    new_count = 0
    update_count = 0
    for fname in os.listdir(POSTS_DIR):
        fpath = os.path.join(POSTS_DIR, fname)
        if not os.path.isdir(fpath) or fname.startswith('custom-') or fname == 'images':
            continue
        index_path = os.path.join(fpath, 'index.html')
        if not os.path.exists(index_path):
            continue
        with open(index_path, encoding='utf-8') as f:
            content = f.read()
        meta_m = re.search(r'<script id="post-meta" type="application/json">(.*?)</script>', content, re.DOTALL)
        thumb = ''
        excerpt = ''
        views = '0'
        comments = '0'
        likes = '0'
        post_id = fname
        if meta_m:
            try:
                meta = json.loads(meta_m.group(1))
                post_id = meta.get('id', fname)
                thumb = meta.get('thumb', '')
                excerpt = meta.get('excerpt', '')
                views = meta.get('views', '0')
                comments = meta.get('comments', '0')
                likes = meta.get('likes', '0')
            except json.JSONDecodeError:
                pass
        title_m = re.search(r'<h1 class="post-article-title">(.*?)</h1>', content)
        title = unescape(title_m.group(1)) if title_m else post_id
        date_m = re.search(r'<span>🕐 (\d{4}-\d{2}-\d{2}) (\d{2}:\d{2})</span>', content)
        date = date_m.group(1) if date_m else '1970-01-01'
        time = date_m.group(2) if date_m else '00:00'
        body_m = re.search(r'<div class="post-article-body">(.*?)</div>', content, re.DOTALL)
        body = body_m.group(1).strip() if body_m else ''
        entry = {
            'id': post_id,
            'source': 'cnblogs',
            'title': title,
            'slug': _slug(title),
            'dir': fname,
            'date': date,
            'time': time,
            'excerpt': excerpt[:200],
            'thumb': thumb,
            'category': _category_for(title),
            'views': views,
            'comments': comments,
            'likes': likes,
            'content_hash': _content_hash(body),
        }
        if post_id in existing_map:
            existing = existing_map[post_id]
            changed = False
            for k in ('title', 'date', 'time', 'excerpt', 'thumb', 'views', 'comments', 'likes', 'dir'):
                if existing.get(k) != entry[k]:
                    existing[k] = entry[k]
                    changed = True
            if changed:
                update_count += 1
        else:
            posts.append(entry)
            new_count += 1
    _save_posts(posts)
    print(f"Imported {new_count} new, updated {update_count} existing cnblogs posts.")
    cmd_build(args)

def cmd_posts_add(args):
    """Add a custom markdown post."""
    md_file = args.file
    if not os.path.exists(md_file):
        print(f"File not found: {md_file}")
        return 1
    with open(md_file, encoding='utf-8') as f:
        text = f.read()
    fm, body = _parse_front_matter(text)
    title = fm.get('title', os.path.splitext(os.path.basename(md_file))[0])
    date = fm.get('date', datetime.now().strftime('%Y-%m-%d'))
    time = fm.get('time', datetime.now().strftime('%H:%M'))
    category = fm.get('category', _category_for(title))
    html_body = md_to_html(body)
    excerpt = re.sub(r'<[^>]+>', '', html_body)[:200].strip()
    slug = _slug(title)
    post_id = f'custom-{slug}'
    # Check for duplicates
    posts = _load_posts()
    dup = _find_duplicate(posts, title, html_body)
    if dup:
        print(f"Duplicate found: '{dup['title']}' (id: {dup['id']}). Skipping.")
        return 0
    # Generate post page
    dir_name = _dir_name(title)
    post_dir = os.path.join(POSTS_DIR, dir_name)
    post_imgs_dir = os.path.join(post_dir, 'images')
    os.makedirs(post_imgs_dir, exist_ok=True)

    # Handle images: download remote, copy local
    def _post_img_src(m):
        attrs = m.group(1)
        src_m = re.search(r'src\s*=\s*"([^"]+)"', attrs)
        alt_m = re.search(r'alt\s*=\s*"([^"]*)"', attrs)
        src = unescape(src_m.group(1)) if src_m else ''
        alt = alt_m.group(1) if alt_m else ''
        if not src:
            return m.group(0)
        if src.startswith(('http://', 'https://')):
            local = _download_image(src, post_imgs_dir)
            if local:
                return f'<img {attrs}src="{local}" alt="{alt}" loading="lazy">'
        elif src.startswith(('images/', './')) or not src.startswith('/'):
            fname = os.path.basename(src)
            dest = os.path.join(post_imgs_dir, fname)
            if os.path.exists(src) and src != dest:
                shutil.copy2(src, dest)
            return f'<img {attrs}src="images/{fname}" alt="{alt}" loading="lazy">'
        return m.group(0)
    html_body = re.sub(r'<img\s+([^>]*?)>', _post_img_src, html_body)
    # Handle cover image
    cover = args.cover or fm.get('cover', '')
    thumb = ''
    if cover:
        cover_path = os.path.join(post_imgs_dir, os.path.basename(cover.split('?')[0]))
        if cover.startswith(('http://', 'https://')):
            if not os.path.exists(cover_path):
                _download_file(cover, cover_path)
            thumb = f'/posts/{dir_name}/images/{os.path.basename(cover_path)}'
        elif os.path.exists(cover):
            if os.path.abspath(cover) != os.path.abspath(cover_path):
                shutil.copy2(cover, cover_path)
            thumb = f'/posts/{dir_name}/images/{os.path.basename(cover_path)}'
    post_page = _custom_post_page(title, date, time, html_body, thumb, excerpt)
    fpath = os.path.join(post_dir, 'index.html')
    with open(fpath, 'w', encoding='utf-8') as f:
        f.write(post_page)
    with open(os.path.join(post_dir, f'{dir_name}.md'), 'w', encoding='utf-8') as f:
        f.write(text)
    # Add to data store
    posts.append({
        'id': post_id,
        'source': 'custom',
        'title': title,
        'slug': slug,
        'dir': dir_name,
        'date': date,
        'time': time,
        'excerpt': excerpt,
        'thumb': thumb,
        'category': category,
        'views': '0',
        'comments': '0',
        'likes': '0',
        'content_hash': _content_hash(html_body),
    })
    _save_posts(posts)
    print(f"Added post: {title} ({post_id})")
    cmd_build(args)

def cmd_posts_edit(args):
    posts = _load_posts()
    post = next((p for p in posts if p['id'] == args.id), None)
    if not post:
        print(f"Post not found: {args.id}")
        return 1
    if args.cover:
        thumb = _handle_post_cover(args.cover, args.id)
        if thumb:
            post['thumb'] = thumb
            print(f"Cover updated: {thumb}")
        else:
            print("Failed to update cover.")
            return 1
        _save_posts(posts)
        cmd_build(args)
        return 0
    if post['source'] != 'custom':
        print("Can only edit title/body of custom posts. Use --cover to change the cover.")
        return 1
    fpath = os.path.join(POSTS_DIR, post['dir'], f'{post["dir"]}.md')
    if not os.path.exists(fpath):
        print(f"File not found: {fpath}")
        return 1
    editor = os.environ.get('EDITOR', 'vim')
    subprocess.call([editor, fpath])
    # Re-read and regenerate
    with open(fpath, encoding='utf-8') as f:
        text = f.read()
    fm, body = _parse_front_matter(text)
    title = fm.get('title', post['title'])
    date = fm.get('date', post['date'])
    time = fm.get('time', post.get('time', '00:00'))
    category = fm.get('category', _category_for(title))
    html_body = md_to_html(body)
    excerpt = re.sub(r'<[^>]+>', '', html_body)[:200].strip()
    # Re-process images
    def _post_img_src(m):
        attrs = m.group(1)
        src_m = re.search(r'src\s*=\s*"([^"]+)"', attrs)
        alt_m = re.search(r'alt\s*=\s*"([^"]*)"', attrs)
        src = unescape(src_m.group(1)) if src_m else ''
        alt = alt_m.group(1) if alt_m else ''
        if not src:
            return m.group(0)
        if src.startswith(('http://', 'https://')):
            local = _download_image(src, os.path.join(POSTS_DIR, post['dir'], 'images'))
            if local:
                return f'<img {attrs}src="{local}" alt="{alt}" loading="lazy">'
        return m.group(0)
    html_body = re.sub(r'<img\s+([^>]*?)>', _post_img_src, html_body)
    thumb = post.get('thumb', '')
    if fm.get('cover'):
        cover_path = os.path.join(POSTS_DIR, post['dir'], 'images', os.path.basename(fm['cover'].split('?')[0]))
        if fm['cover'].startswith(('http://', 'https://')):
            if not os.path.exists(cover_path):
                _download_file(fm['cover'], cover_path)
            thumb = f'/posts/{post["dir"]}/images/{os.path.basename(cover_path)}'
    post_page = _custom_post_page(title, date, time, html_body, thumb, excerpt)
    index_path = os.path.join(POSTS_DIR, post['dir'], 'index.html')
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(post_page)
    post['title'] = title
    post['date'] = date
    post['time'] = time
    post['category'] = category
    post['thumb'] = thumb
    post['excerpt'] = excerpt
    post['content_hash'] = _content_hash(html_body)
    _save_posts(posts)
    cmd_build(args)
    print(f"Edited: {args.id}")

def cmd_posts_delete(args):
    posts = _load_posts()
    post = next((p for p in posts if p['id'] == args.id), None)
    if not post:
        print(f"Post not found: {args.id}")
        return 1
    dir_name = post.get('dir', _dir_name(post.get('title', '')))
    fpath = os.path.join(POSTS_DIR, dir_name)
    if os.path.isdir(fpath):
        shutil.rmtree(fpath)
    elif os.path.isfile(fpath + '.html'):
        os.remove(fpath + '.html')
    posts = [p for p in posts if p['id'] != args.id]
    _save_posts(posts)
    print(f"Deleted: {args.id}")
    cmd_build(args)

# ═══════════════════════════════════════════════════════════
#  Book management
# ═══════════════════════════════════════════════════════════

def cmd_books_list(args):
    books = _load_json(BOOKS_JSON)
    if not books:
        print("No books.")
        return
    print(f"{'ID':<5} {'Title':<{MAX_TITLE_PREVIEW}} {'Rating':<7}")
    print('-' * 70)
    for b in books:
        print(f"{b['id']:<5} {b['title'][:MAX_TITLE_PREVIEW]:<{MAX_TITLE_PREVIEW}} {b.get('rating', '?'):<7}")

def cmd_books_add(args):
    books = _load_json(BOOKS_JSON)
    print("Add a book (URL is required, other fields auto-fetched if blank):")
    url = input("  URL (douban/amazon): ").strip()
    if not url:
        print("Cancelled.")
        return
    fetched = _fetch_book_meta(url)
    title = input(f"  Title [{fetched.get('title', '')}]: ").strip() or fetched.get('title', '')
    author = input(f"  Author [{fetched.get('author', '')}]: ").strip() or fetched.get('author', '')
    rating = input(f"  Rating [{fetched.get('rating', '')}]: ").strip() or fetched.get('rating', '')
    desc = input(f"  Description [{fetched.get('description', '')}]: ").strip() or fetched.get('description', '')
    cover_input = input(f"  Cover [{fetched.get('cover', '(auto)')}]: ").strip()
    cover_dest = ''
    if cover_input:
        cover_dest = _handle_cover_image(cover_input, title or _slug(url))
    elif fetched.get('cover'):
        if _download_and_save_cover(fetched['cover'], title or _slug(url)):
            cover_dest = f'images/books/{_slug(title or _slug(url))}.jpg'
    books.append({
        'id': _next_id(books),
        'title': title,
        'author': author,
        'rating': rating,
        'description': desc,
        'url': url,
        'cover': cover_dest,
    })
    _rename_cover_to_title(books[-1])
    _save_json(BOOKS_JSON, books)
    print(f"Added book: {title}")
    cmd_build(args)

def cmd_books_edit(args):
    books = _load_json(BOOKS_JSON)
    book = next((b for b in books if b['id'] == args.id), None)
    if not book:
        print(f"Book not found: {args.id}")
        return 1
    old_url = book.get('url', '')
    print(f"Editing '{book['title']}' (enter = keep current):")
    for key, label in [('url', 'URL'), ('title', 'Title'), ('author', 'Author'),
                        ('rating', 'Rating'), ('description', 'Description')]:
        val = input(f"  {label} [{book.get(key, '')}]: ").strip()
        if val:
            book[key] = val
    url_changed = book.get('url', '') != old_url
    if url_changed and book.get('url'):
        fetched = _fetch_book_meta(book['url'])
        if not book.get('title'): book['title'] = fetched.get('title', '')
        if not book.get('author'): book['author'] = fetched.get('author', '')
        if not book.get('rating'): book['rating'] = fetched.get('rating', '')
        if not book.get('description'): book['description'] = fetched.get('description', '')
        if not book.get('cover') and fetched.get('cover'):
            if _download_and_save_cover(fetched['cover'], book.get('title', '')):
                book['cover'] = f'images/books/{_slug(book.get("title", ""))}.jpg'
    cover = input(f"  Cover [{book.get('cover', '')}] (new path/URL, or blank to skip): ").strip()
    if cover:
        book['cover'] = _handle_cover_image(cover, book.get('title', ''))
    _rename_cover_to_title(book)
    _save_json(BOOKS_JSON, books)
    print(f"Updated: {book['title']}")
    cmd_build(args)

def cmd_books_delete(args):
    books = _load_json(BOOKS_JSON)
    book = next((b for b in books if b['id'] == args.id), None)
    if not book:
        print(f"Book not found: {args.id}")
        return 1
    books = [b for b in books if b['id'] != args.id]
    _save_json(BOOKS_JSON, books)
    print(f"Deleted: {book['title']}")
    cmd_build(args)

def _handle_cover_image(src, title):
    if not src:
        return ''
    fname = _slug(title) + os.path.splitext(src)[1] or '.jpg'
    dest = os.path.join(BOOKS_IMG_DIR, fname)
    if src.startswith(('http://', 'https://')):
        _download_file(src, dest)
    elif os.path.exists(src):
        if os.path.abspath(src) != os.path.abspath(dest):
            shutil.copy2(src, dest)
    else:
        print(f"  Warning: {src} not found, skipping cover.")
        return ''
    return f'images/books/{fname}'

def _rename_cover_to_title(book):
    """Rename cover file to match book title if it doesn't already."""
    cover = book.get('cover', '')
    title = book.get('title', '')
    if not cover or not title or not cover.startswith('images/books/'):
        return cover
    old_fname = os.path.basename(cover)
    new_fname = f'{_slug(title)}{os.path.splitext(old_fname)[1]}'
    if old_fname == new_fname:
        return cover
    old_path = os.path.join(BOOKS_IMG_DIR, old_fname)
    new_path = os.path.join(BOOKS_IMG_DIR, new_fname)
    if os.path.exists(old_path):
        shutil.move(old_path, new_path)
        print(f'  Renamed cover: {old_fname} -> {new_fname}')
    book['cover'] = f'images/books/{new_fname}'
    return book['cover']

class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if 'sec.douban.com' in newurl:
            return None
        return super().redirect_request(req, fp, code, msg, headers, newurl)

def _fetch_book_meta(book_url):
    """Scrape book metadata (title, author, rating, description, cover) from a URL."""
    meta = {'title': '', 'author': '', 'rating': '', 'description': '', 'cover': ''}
    if not book_url or not book_url.startswith(('http://', 'https://')):
        return meta
    try:
        opener = urllib.request.build_opener(_NoRedirect)
        req = urllib.request.Request(book_url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Referer': 'https://book.douban.com/',
        })
        resp = opener.open(req, timeout=15)
        actual_url = resp.geturl()
        if 'sec.douban.com' in actual_url:
            print("  Blocked by Douban security page — try a different URL or add book manually")
            return meta
        html = resp.read().decode('utf-8', errors='replace')
    except urllib.error.HTTPError as e:
        if e.code in (302, 301, 303, 307, 308):
            print("  Blocked by Douban security redirect — try a different URL or add book manually")
        else:
            print(f"  Failed to fetch page: {e}")
        return meta
    except Exception as e:
        print(f"  Failed to fetch page: {e}")
        return meta

    # ── Douban-specific ──
    if 'douban.com' in book_url:
        # title (use sub-title div, fall back to og:title stripped of suffix)
        m = re.search(r'<div\s+class=["\']sub-title["\'][^>]*>([^<]+)</div>', html)
        if m: meta['title'] = unescape(m.group(1)).strip()
        if not meta['title']:
            m = re.search(r'<meta\s+property=["\']og:title["\']\s+content=["\']([^"\']+)["\']', html, re.I)
            if m: meta['title'] = unescape(m.group(1)).replace(' - 图书', '').replace(' - 豆瓣', '').strip()
        # author (first segment in sub-meta before /)
        m = re.search(r'<div\s+class=["\']sub-meta["\'][^>]*>\s*(.+?)\s*</div>', html, re.DOTALL)
        if m:
            meta_text = unescape(m.group(1)).strip()
            parts = [p.strip() for p in re.split(r'<br\s*/?>', meta_text) if p.strip()]
            if parts:
                first_seg = parts[0]
                # Take everything before the first /
                author = re.split(r'\s*/\s*', first_seg)[0].strip()
                if author:
                    meta['author'] = author
        # rating (microdata)
        m = re.search(r'<meta\s+itemprop=["\']ratingValue["\']\s+content=["\']([\d.]+)["\']', html)
        if m: meta['rating'] = m.group(1)
        # description
        m = re.search(r'<meta\s+property=["\']og:description["\']\s+content=["\']([^"\']+)["\']', html, re.I)
        if m: meta['description'] = unescape(m.group(1)).strip()
    # ── General (og tags) ──
    else:
        m = re.search(r'<meta\s+property=["\']og:title["\']\s+content=["\']([^"\']+)["\']', html, re.I)
        if m: meta['title'] = unescape(m.group(1)).strip()
        m = re.search(r'<meta\s+property=["\']og:description["\']\s+content=["\']([^"\']+)["\']', html, re.I)
        if m: meta['description'] = unescape(m.group(1)).strip()
        # Try schema.org Product for author
        m = re.search(r'"author"\s*:\s*"([^"]+)"', html)
        if m: meta['author'] = unescape(m.group(1)).strip()
        # Try JSON-LD
        m = re.search(r'"aggregateRating"\s*:\s*\{[^}]*"ratingValue"\s*:\s*"([^"]+)"', html)
        if m: meta['rating'] = m.group(1).strip()

    # ── Cover image ──
    img_url = ''
    m = re.search(r'<meta\s+property=["\']og:image["\']\s+content=["\']([^"\']+)["\']', html, re.I)
    if m: img_url = unescape(m.group(1))
    if not img_url:
        m = re.search(r'<meta\s+content=["\']([^"\']+)["\']\s+property=["\']og:image["\']', html, re.I)
        if m: img_url = unescape(m.group(1))
    if img_url and re.search(r'\.(jpg|jpeg|png|gif|webp)(\?|$)', img_url, re.I):
        # Keep Douban medium size (large may be blocked)
        meta['cover'] = img_url

    return meta

def _download_and_save_cover(img_url, title):
    fname = f'{_slug(title)}.jpg'
    dest = os.path.join(BOOKS_IMG_DIR, fname)
    if os.path.exists(dest):
        return True
    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
        'Referer': 'https://book.douban.com/',
    }
    # Retry with medium size if large is blocked
    urls_to_try = [img_url]
    if '/l/public/' in img_url:
        urls_to_try.append(img_url.replace('/l/public/', '/m/public/'))
    for url in urls_to_try:
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=15) as resp:
                with open(dest, 'wb') as f:
                    shutil.copyfileobj(resp, f)
            print(f"  Downloaded cover: {fname}")
            return True
        except urllib.error.HTTPError as e:
            if e.code in (403, 418) and url == urls_to_try[0] and len(urls_to_try) > 1:
                continue
            print(f"  Failed to download cover {url}: {e}")
            return False
        except Exception as e:
            print(f"  Failed to download cover {url}: {e}")
            return False
    return False

def _download_file(url, dest):
    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (compatible; ManageBot/1.0)'
        })
        with urllib.request.urlopen(req, timeout=30) as resp:
            with open(dest, 'wb') as f:
                shutil.copyfileobj(resp, f)
        print(f"  Downloaded: {os.path.basename(dest)}")
    except Exception as e:
        print(f"  Download failed: {e}")

def _download_image(url, dest_dir):
    fname = os.path.basename(url.split('?')[0])
    if not fname:
        return None
    dest = os.path.join(dest_dir, fname)
    if os.path.exists(dest):
        return f'images/{fname}'
    _download_file(url, dest)
    return f'images/{fname}' if os.path.exists(dest) else None

def _handle_post_cover(cover, post_id):
    if not cover:
        return ''
    fname = os.path.basename(cover.split('?')[0])
    dest = os.path.join(IMAGES_DIR, fname)
    prefix = f'/posts/images/'
    if cover.startswith(('http://', 'https://')):
        if os.path.exists(dest):
            return f'{prefix}{fname}'
        try:
            req = urllib.request.Request(cover, headers={
                'User-Agent': 'Mozilla/5.0 (compatible; ManageBot/1.0)'
            })
            with urllib.request.urlopen(req, timeout=30) as resp:
                with open(dest, 'wb') as f:
                    shutil.copyfileobj(resp, f)
            print(f'  downloaded cover: {fname}')
            return f'{prefix}{fname}'
        except Exception as e:
            print(f'  failed to download cover {cover}: {e}')
            return cover
    if os.path.exists(cover):
        if os.path.abspath(cover) != os.path.abspath(dest):
            shutil.copy2(cover, dest)
        return f'{prefix}{fname}'
    return cover

# ═══════════════════════════════════════════════════════════
#  Photo management
# ═══════════════════════════════════════════════════════════

def cmd_photos_list(args):
    photos = _load_json(GALLERY_JSON)
    if not photos:
        print("No photos.")
        return
    print(f"{'ID':<5} {'Caption':<{MAX_TITLE_PREVIEW}} {'File':<30}")
    print('-' * 90)
    for p in photos:
        print(f"{p['id']:<5} {p.get('caption', '')[:MAX_TITLE_PREVIEW]:<{MAX_TITLE_PREVIEW}} {p.get('filename', ''):<30}")

def cmd_photos_add(args):
    photos = _load_json(GALLERY_JSON)
    src = args.file
    caption = args.caption or os.path.splitext(os.path.basename(src))[0]
    if not os.path.exists(src):
        print(f"File not found: {src}")
        return 1
    ext = os.path.splitext(src)[1].lower()
    if ext not in ('.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg'):
        print(f"Unsupported format: {ext}")
        return 1
    fname = _slug(caption) + ext
    dest = os.path.join(GALLERY_DIR, fname)
    shutil.copy2(src, dest)
    photos.append({
        'id': _next_id(photos),
        'filename': fname,
        'caption': caption,
    })
    _save_json(GALLERY_JSON, photos)
    print(f"Added photo: {caption}")
    cmd_build(args)

def cmd_photos_delete(args):
    photos = _load_json(GALLERY_JSON)
    photo = next((p for p in photos if p['id'] == args.id), None)
    if not photo:
        print(f"Photo not found: {args.id}")
        return 1
    fpath = os.path.join(GALLERY_DIR, photo['filename'])
    if os.path.exists(fpath):
        os.remove(fpath)
    photos = [p for p in photos if p['id'] != args.id]
    _save_json(GALLERY_JSON, photos)
    print(f"Deleted: {photo['caption']}")
    cmd_build(args)

# ═══════════════════════════════════════════════════════════
#  Friend management
# ═══════════════════════════════════════════════════════════

def cmd_friends_list(args):
    friends = _load_json(FRIENDS_JSON)
    if not friends:
        print("No friends.")
        return
    print(f"{'ID':<5} {'Name':<20} {'Description':<{MAX_TITLE_PREVIEW}}")
    print('-' * 80)
    for f in friends:
        print(f"{f['id']:<5} {f.get('name', '')[:20]:<20} {f.get('description', '')[:MAX_TITLE_PREVIEW]:<{MAX_TITLE_PREVIEW}}")

def cmd_friends_add(args):
    friends = _load_json(FRIENDS_JSON)
    print("Add a friend (leave blank to skip):")
    name = input("  Name: ").strip()
    if not name:
        print("Cancelled.")
        return
    url = input("  URL: ").strip()
    desc = input("  Description: ").strip()
    emoji = input("  Emoji (default 🌐): ").strip() or '🌐'
    friends.append({
        'id': _next_id(friends),
        'name': name,
        'url': url,
        'description': desc,
        'emoji': emoji,
    })
    _save_json(FRIENDS_JSON, friends)
    print(f"Added friend: {name}")
    cmd_build(args)

def cmd_friends_edit(args):
    friends = _load_json(FRIENDS_JSON)
    friend = next((f for f in friends if f['id'] == args.id), None)
    if not friend:
        print(f"Friend not found: {args.id}")
        return 1
    print(f"Editing '{friend['name']}' (enter = keep current):")
    for key, label in [('name', 'Name'), ('url', 'URL'),
                        ('description', 'Description'), ('emoji', 'Emoji')]:
        val = input(f"  {label} [{friend.get(key, '')}]: ").strip()
        if val:
            friend[key] = val
    _save_json(FRIENDS_JSON, friends)
    print(f"Updated: {friend['name']}")
    cmd_build(args)

def cmd_friends_delete(args):
    friends = _load_json(FRIENDS_JSON)
    friend = next((f for f in friends if f['id'] == args.id), None)
    if not friend:
        print(f"Friend not found: {args.id}")
        return 1
    friends = [f for f in friends if f['id'] != args.id]
    _save_json(FRIENDS_JSON, friends)
    print(f"Deleted: {friend['name']}")
    cmd_build(args)

# ═══════════════════════════════════════════════════════════
#  HTML generation
# ═══════════════════════════════════════════════════════════

# ── Post templates (matching sync_posts.py style) ──

POST_TPL = '''\
    <article class="post">
      <div class="post-header">
        {thumb_html}
        <div>
          <h2 class="post-title"><a href="{url}">{title}</a></h2>
          <div class="post-excerpt">{excerpt}</div>
        </div>
      </div>
      <div class="post-meta">
        <span>\U0001f550 {time}</span>
        <span>\U0001f441\ufe0f {views}</span>
        <span>\U0001f4ac {comments}</span>
        <span>\U0001f44d {likes}</span>
      </div>
    </article>'''

ARCHIVE_TPL = '''\
      <li class="archive-item">
        <span class="archive-date">{date}</span>
        <a class="archive-link" href="{url}">{title}</a>
      </li>'''

CAT_POST_TPL = '''\
      <li class="category-item"><a href="{url}">{title}</a></li>'''

CUSTOM_POST_PAGE_TPL = '''\
<!DOCTYPE html>
<html lang="zh-cn">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} - Josiah Bristow</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:ital,wght@0,400;0,600;0,700;1,400&display=swap" rel="stylesheet">
<link rel="stylesheet" href="../../style.css">
<link rel="icon" type="image/svg+xml" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🐧</text></svg>">
<link rel="alternate icon" href="https://avatars.githubusercontent.com/u/123633729?s=32&v=4">
{post_meta}
</head>
<body>

<header class="header">
  <div class="header-title"><a href="../../index.html">Josiah Bristow</a></div>
  <div class="header-prompt">Just For Fun!</div>
  <div class="header-sub">Arch Linux, Linux tools, and developer life</div>
</header>

<nav class="nav">
  <div class="nav-inner">
    <a href="../../index.html">\U0001f3e0 <span data-i18n="nav-home">\u9996\u9875</span></a>
    <a href="../../archive.html">\U0001f4e6 <span data-i18n="nav-archive">\u5f52\u6863</span></a>
    <a href="../../categories.html">\U0001f3f7\ufe0f <span data-i18n="nav-categories">\u5206\u7c7b</span></a>
    <a href="../../about.html">\U0001f464 <span data-i18n="nav-about">\u5173\u4e8e</span></a>
    <a href="../../bookshelf.html">📚 <span data-i18n="nav-bookshelf">\u4e66\u67b6</span></a>
    <a href="../../gallery.html">📷 <span data-i18n="nav-gallery">\u76f8\u518c</span></a>
    <a href="../../friends.html">🤝 <span data-i18n="nav-friends">\u53cb\u94fe</span></a>
    <a target="_blank" rel="noopener" href="https://josiahbristow.github.io/ai-signal/index.html">📡 <span data-i18n="nav-signal">AI \u4fe1\u53f7</span></a>
    <button class="nav-search-btn" id="searchToggle" aria-label="\u641c\u7d22">🔍</button>
  </div>
</nav>

<div class="page-full">

<article class="post-article">
  <div class="post-article-heading">
    {cover_html}
    <h1 class="post-article-title">{title}</h1>
    <div class="post-article-meta">
      <span>\U0001f550 {date} {time}</span>
    </div>
  </div>
  <div class="post-article-body">
{body}
  </div>
</article>

<div class="post-comments">
  <h2 class="post-comments-title">\U0001f4ac <span data-i18n="comments-title">\u8bc4\u8bba</span></h2>
  <div id="giscus-container"></div>
  <script>
    (function() {{
      var theme = 'catppuccin_latte';
      var lang = 'zh-CN';
      try {{
        var ts = localStorage.getItem('theme');
        if (ts === 'dark') theme = 'catppuccin_mocha';
        var ls = localStorage.getItem('lang');
        if (ls === 'en') lang = 'en';
      }} catch(e) {{}}
      var c = document.getElementById('giscus-container');
      var sc = document.createElement('script');
      sc.src = 'https://giscus.app/client.js';
      sc.setAttribute('data-repo', 'JosiahBristow/JosiahBristow.github.io');
      sc.setAttribute('data-repo-id', 'R_kgDOTi7MtA');
      sc.setAttribute('data-category', 'Announcements');
      sc.setAttribute('data-category-id', 'DIC_kwDOTi7MtM4DB-Fn');
      sc.setAttribute('data-mapping', 'pathname');
      sc.setAttribute('data-strict', '0');
      sc.setAttribute('data-reactions-enabled', '1');
      sc.setAttribute('data-emit-metadata', '0');
      sc.setAttribute('data-input-position', 'bottom');
      sc.setAttribute('data-theme', theme);
      sc.setAttribute('data-lang', lang);
      sc.setAttribute('crossorigin', 'anonymous');
      sc.async = true;
      c.appendChild(sc);
    }})();
  </script>
</div>

</div>

<div class="float-group">
  <button class="float-btn" id="langToggle" aria-label="\u5207\u6362\u8bed\u8a00">EN</button>
  <button class="float-btn" id="themeToggle" aria-label="\u5207\u6362\u4e3b\u9898">\U0001f319</button>
  <button class="back-to-top" id="backToTop" aria-label="\u8fd4\u56de\u9876\u90e8">\u2191</button>
</div>

<footer class="footer">
  <p>\U0001f427 &copy; 2024-2026 Josiah Bristow. Built with \u2764\ufe0f for <a href="https://pages.github.com/">GitHub Pages</a>.</p>
</footer>

<script src="../../script.js"></script>
<script src="../../lang.js"></script>
</body>
</html>'''

def _custom_post_page(title, date, time, body, thumb='', excerpt=''):
    import json as _json
    post_meta = _json.dumps({
        'thumb': thumb, 'excerpt': excerpt,
        'views': '0', 'comments': '0', 'likes': '0',
    }, ensure_ascii=False)
    post_meta_html = f'<script id="post-meta" type="application/json">{post_meta}</script>'
    cover_html = f'<img class="post-article-cover" src="{thumb}" alt="{_alt(title)}" loading="lazy">' if thumb else ''
    return CUSTOM_POST_PAGE_TPL.format(
        title=title, date=date, time=time, body=body,
        cover_html=cover_html, post_meta=post_meta_html,
    )

def _alt(title):
    s = re.sub(r'[\[\]()（）]', '', title).strip()
    return s[:20]

def _thumb_tag(thumb, title):
    if thumb:
        return f'<img class="post-thumb" src="{thumb}" alt="{_alt(title)}" loading="lazy" referrerpolicy="no-referrer">'
    return '<div class="post-thumb post-thumb-missing"></div>'

def _build_index(posts):
    groups = defaultdict(list)
    for p in posts:
        groups[p['date']].append(p)
    lines = []
    lines.append('  <div class="post-grid" data-view="list">')
    for date_str in sorted(groups, reverse=True):
        lines.append('  <div class="day-group">')
        lines.append(f'    <div class="day-title">{date_str}</div>')
        for p in groups[date_str]:
            url = f'posts/{p.get("dir", _dir_name(p.get("title", "")))}/'
            thumb_html = _thumb_tag(p.get('thumb', ''), p['title'])
            lines.append(POST_TPL.format(
                url=url, title=p['title'],
                thumb_html=thumb_html,
                excerpt=p.get('excerpt', ''),
                time=p.get('time', ''),
                views=p.get('views', '0'),
                comments=p.get('comments', '0'),
                likes=p.get('likes', '0'),
            ))
        lines.append('  </div>')
    lines.append('  </div>')
    return '\n'.join(lines)

def _build_archive(posts):
    years = defaultdict(list)
    for p in posts:
        years[p['date'][:4]].append(p)
    lines = []
    lines.append('  <div class="page-heading">')
    lines.append('    <h1>\U0001f4e6 <span data-i18n="archive-title">\u5f52\u6863</span></h1>')
    lines.append('  </div>')
    for year in sorted(years, reverse=True):
        lines.append('  <div class="archive-year">')
        lines.append(f'    <div class="archive-year-header">\U0001f4c5 {year} <span class="fold-icon">▼</span></div>')
        lines.append('    <ul class="archive-list">')
        for p in years[year]:
            url = f'posts/{p.get("dir", _dir_name(p.get("title", "")))}/'
            lines.append(ARCHIVE_TPL.format(date=p['date'], url=url, title=p['title']))
        lines.append('    </ul>')
        lines.append('  </div>')
    return '\n'.join(lines)

def _build_categories(posts, cat_emoji=None):
    cats = defaultdict(list)
    for p in posts:
        cats[p.get('category', 'Arch Linux')].append(p)
    if cat_emoji is None:
        cat_emoji = _load_categories()
    lines = []
    lines.append('  <div class="page-heading">')
    lines.append('    <h1>\U0001f3f7\ufe0f <span data-i18n="categories-title">\u5206\u7c7b</span></h1>')
    lines.append('  </div>')
    for name in sorted(cats):
        plist = cats[name]
        emoji = cat_emoji.get(name, '📄')
        lines.append('  <div class="category-section">')
        lines.append('    <div class="category-header">')
        lines.append(f'      {emoji} {name}')
        lines.append(f'      <span class="category-count">{len(plist)} \u7bc7</span>')
        lines.append('      <span class="fold-icon">▼</span>')
        lines.append('    </div>')
        lines.append('    <ul class="category-list">')
        for p in plist:
            url = f'posts/{p.get("dir", _dir_name(p.get("title", "")))}/'
            lines.append(CAT_POST_TPL.format(url=url, title=p['title']))
        lines.append('    </ul>')
        lines.append('  </div>')
    return '\n'.join(lines)

def _build_bookshelf(books):
    lines = []
    lines.append('  <div class="page-heading">')
    lines.append('    <h1>📚 <span data-i18n="bookshelf-title">\u4e66\u67b6</span></h1>')
    lines.append('    <p data-i18n="bookshelf-desc">\u8bfb\u8fc7\u548c\u6b63\u5728\u8bfb\u7684\u4e66</p>')
    lines.append('  </div>')
    lines.append('  <div class="view-toggle">')
    lines.append('    <button class="active" data-view="list" aria-label="\u5217\u8868\u89c6\u56fe">☰</button>')
    lines.append('    <button data-view="grid" aria-label="\u7f51\u683c\u89c6\u56fe">▦</button>')
    lines.append('  </div>')
    lines.append('  <div class="bookshelf-grid" data-view="list">')
    for b in books:
        rating = b.get('rating', '')
        rating_html = f'⭐ {rating}' if rating else ''
        url = b.get('url', '')
        cover = b.get('cover', '')
        cover_html = ''
        if cover:
            cover_html = f'<img class="book-cover" src="{cover}" alt="{b["title"]}" loading="lazy">'
        elif url:
            cover_html = f'<div class="book-cover-placeholder">📖</div>'
        else:
            cover_html = '<div class="book-cover-placeholder">📖</div>'
        lines.append('    <div class="book-card">')
        if url:
            lines.append(f'      <a href="{url}" target="_blank" class="book-cover-link">')
            lines.append(f'        {cover_html}')
            lines.append('      </a>')
        else:
            lines.append(f'      {cover_html}')
        lines.append('      <div class="book-info">')
        title_escaped = b['title']
        lines.append(f'        <div class="book-title">{title_escaped}</div>')
        lines.append(f'        <div class="book-author">{b.get("author", "")}</div>')
        if rating_html:
            lines.append(f'        <div class="book-rating">{rating_html}</div>')
        lines.append(f'        <div class="book-desc">{b.get("description", "")}</div>')
        lines.append('      </div>')
        lines.append('    </div>')
    lines.append('  </div>')
    return '\n'.join(lines)

def _build_gallery(photos):
    lines = []
    lines.append('  <div class="page-heading">')
    lines.append('    <h1>📷 <span data-i18n="gallery-title">\u76f8\u518c</span></h1>')
    lines.append('    <p data-i18n="gallery-desc">\u4e00\u4e9b\u7167\u7247\u548c\u622a\u56fe</p>')
    lines.append('  </div>')
    lines.append('  <div class="gallery-grid">')
    for p in photos:
        fname = p.get('filename', '')
        caption = p.get('caption', '')
        lines.append('    <div class="gallery-item">')
        lines.append(f'      <img class="gallery-img" src="images/gallery/{fname}" alt="{caption}" loading="lazy">')
        lines.append(f'      <div class="gallery-caption">{caption}</div>')
        lines.append('    </div>')
    lines.append('  </div>')
    return '\n'.join(lines)

def _build_friends(friends):
    lines = []
    lines.append('  <div class="page-heading">')
    lines.append('    <h1>🤝 <span data-i18n="friends-title">\u53cb\u94fe</span></h1>')
    lines.append('    <p data-i18n="friends-desc">\u670b\u53cb\u4eec\u7684\u5c0f\u7ad9</p>')
    lines.append('  </div>')
    lines.append('  <div class="friends-list">')
    for f in friends:
        name = f.get('name', '')
        url = f.get('url', '')
        desc = f.get('description', '')
        emoji = f.get('emoji', '🌐')
        lines.append(f'    <a class="friend-card" target="_blank" href="{url}">')
        lines.append('      <div class="friend-avatar-placeholder">')
        lines.append(f'        <span>{emoji}</span>')
        lines.append('      </div>')
        lines.append('      <div class="friend-info">')
        lines.append(f'        <div class="friend-name">{name}</div>')
        lines.append(f'        <div class="friend-desc">{desc}</div>')
        lines.append('      </div>')
        lines.append('    </a>')
    lines.append('  </div>')
    return '\n'.join(lines)

def _build_sidebar(posts, books=None, photos=None, friends_count=0, cat_emoji=None):
    total = len(posts)
    t_views = sum(int(p['views']) for p in posts if p.get('views', '0').isdigit())
    t_likes = sum(int(p['likes']) for p in posts if p.get('likes', '0').isdigit())
    t_comments = sum(int(p['comments']) for p in posts if p.get('comments', '0').isdigit())
    cats = defaultdict(list)
    for p in posts:
        cats[p.get('category', 'Arch Linux')].append(p)
    if cat_emoji is None:
        cat_emoji = _load_categories()
    tag_items = ''.join(
        f'      <span class="tag">{cat_emoji.get(n, "\U0001f4c4")} {n} <span class="post-count">{len(cats[n])}</span></span>\n'
        for n in sorted(cats)
    )
    stats = [
        ('\U0001f4dd', 'stat-posts', '\u968f\u7b14', str(total)),
        ('\U0001f44d', 'stat-likes', '\u63a8\u8350', str(t_likes)),
        ('\U0001f441\ufe0f', 'stat-reads', '\u9605\u8bfb', _fmt_count(t_views)),
        ('\U0001f4ac', 'stat-comments', '\u8bc4\u8bba', str(t_comments)),
    ]
    sidebar = f'''\
  <div class="sidebar-card profile">
    <img class="profile-avatar" src="https://avatars.githubusercontent.com/u/123633729?s=96&v=4" alt="avatar" loading="lazy">
    <div class="profile-name">Josiah Bristow</div>
    <div class="profile-bio">Arch Linux user \u00b7 Linux enthusiast \u00b7 I just want to go out and see if there are another way to live life.</div>
    <div class="profile-links">
      <a target="_blank" href="https://github.com/josiahbristow">\U0001f419 GitHub</a>
      <a target="_blank" href="https://josiahbristow.github.io/">\U0001f310 Blog</a>
    </div>
  </div>

  <div class="sidebar-card">
    <h3 data-i18n="sidebar-stats">\u7edf\u8ba1\u6570\u636e</h3>
    <div class="stat-grid">
'''
    for emoji, i18n_key, label, val in stats:
        sidebar += f'''\
      <div>
        <div class="stat-value">{val}</div>
        <div class="stat-label">{emoji} <span data-i18n="{i18n_key}">{label}</span></div>
      </div>
'''
    sidebar += f'''\
    </div>
  </div>

  <div class="sidebar-card">
    <h3 data-i18n="sidebar-categories">\u5206\u7c7b</h3>
    <div class="tag-list">
{tag_items}    </div>
  </div>'''
    return sidebar

def _build_search_index(posts, books):
    import json as _json
    cat_emoji = _load_categories()
    index = []
    for p in posts:
        cat = p.get('category', '')
        emoji = cat_emoji.get(cat, '📄')
        dir_name = p.get('dir', _dir_name(p.get('title', '')))
        url = f'posts/{dir_name}/'
        index.append({
            't': p['title'],
            'u': url,
            'd': p.get('excerpt', ''),
            'm': f'{emoji} {cat}' if cat else '',
        })
    for b in books:
        author = b.get('author', '')
        rating = b.get('rating', '')
        desc_parts = [author, f'⭐ {rating}'] if rating else [author]
        index.append({
            't': b['title'],
            'u': b.get('url', ''),
            'd': ' · '.join(filter(None, desc_parts)),
            'm': '📚 书籍',
        })
    dest = os.path.join(DATA_DIR, 'search-index.json')
    with open(dest, 'w', encoding='utf-8') as f:
        _json.dump(index, f, ensure_ascii=False)
    print("  search-index.json")

def _inject(filepath, marker, new_content):
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()
    text = re.sub(
        rf'<!--\s*{marker}\s*-->.*?<!--\s*/\s*{marker}\s*-->',
        f'<!-- {marker} -->\n{new_content}\n<!-- /{marker} -->',
        text, flags=re.DOTALL
    )
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(text)

def _inject_sidebar(filepath, sidebar_html):
    _inject(filepath, 'SIDEBAR', sidebar_html)

def cmd_build(args=None):
    posts = _load_posts()
    books = _load_json(BOOKS_JSON)
    photos = _load_json(GALLERY_JSON)
    friends = _load_json(FRIENDS_JSON)

    posts.sort(key=lambda p: p['date'] + p.get('time', '00:00'), reverse=True)

    cat_emoji = _load_categories()

    # Index
    content = _build_index(posts)
    _inject(os.path.join(ROOT, 'index.html'), 'CONTENT_MAIN', content)
    print("  index.html")

    # Archive
    content = _build_archive(posts)
    _inject(os.path.join(ROOT, 'archive.html'), 'CONTENT_MAIN', content)
    print("  archive.html")

    # Categories
    content = _build_categories(posts, cat_emoji)
    _inject(os.path.join(ROOT, 'categories.html'), 'CONTENT_MAIN', content)
    print("  categories.html")

    # Bookshelf
    # Ensure all covers exist locally with title-based names
    for b in books:
        cover = b.get('cover', '')
        if cover and cover.startswith(('http://', 'https://')):
            if _download_and_save_cover(cover, b['title']):
                b['cover'] = f'images/books/{_slug(b["title"])}.jpg'
        elif cover and cover.startswith('images/books/'):
            local_path = os.path.join(ROOT, cover)
            if not os.path.exists(local_path) and b.get('url'):
                fetched = _fetch_book_meta(b['url'])
                if fetched.get('cover') and _download_and_save_cover(fetched['cover'], b['title']):
                    b['cover'] = f'images/books/{_slug(b["title"])}.jpg'
        _rename_cover_to_title(b)
    _save_json(BOOKS_JSON, books)
    content = _build_bookshelf(books)
    _inject(os.path.join(ROOT, 'bookshelf.html'), 'CONTENT_MAIN', content)
    print("  bookshelf.html")

    # Gallery
    content = _build_gallery(photos)
    _inject(os.path.join(ROOT, 'gallery.html'), 'CONTENT_MAIN', content)
    print("  gallery.html")

    # Friends
    content = _build_friends(friends)
    _inject(os.path.join(ROOT, 'friends.html'), 'CONTENT_MAIN', content)
    print("  friends.html")

    # Sidebar for all pages
    sidebar = _build_sidebar(posts, books, photos, len(friends), cat_emoji)
    for page in ['index.html', 'archive.html', 'categories.html',
                 'bookshelf.html', 'gallery.html', 'friends.html']:
        _inject_sidebar(os.path.join(ROOT, page), sidebar)
    print("  sidebar updated for all pages")

    print("Build complete.")

    # ── Search index ──
    _build_search_index(posts, books)

# ═══════════════════════════════════════════════════════════
#  Import existing content from HTML pages
# ═══════════════════════════════════════════════════════════

def cmd_import(args):
    """Import existing content from HTML files into data store."""
    print("Importing existing content...")

    # ── import posts from index.html ──
    idx_path = os.path.join(ROOT, 'index.html')
    if os.path.exists(idx_path):
        with open(idx_path, encoding='utf-8') as f:
            html = f.read()
        # find content between CONTENT_MAIN markers
        m = re.search(r'<!--\s*CONTENT_MAIN\s*-->(.*?)<!--\s*/\s*CONTENT_MAIN\s*-->', html, re.DOTALL)
        if m:
            content = m.group(1)
            posts = _load_posts()
            existing_ids = {p['id'] for p in posts}
            count = 0
            # parse post entries
            post_articles = re.findall(
                r'<article class="post">(.*?)</article>', content, re.DOTALL)
            for pa in post_articles:
                url_m = re.search(r'<a href="posts/([^"]+\.html)">', pa)
                if not url_m:
                    continue
                post_id = url_m.group(1).replace('.html', '')
                if post_id in existing_ids:
                    continue
                title_m = re.search(r'<h2 class="post-title"><a[^>]*>(.*?)</a></h2>', pa)
                title = unescape(title_m.group(1)) if title_m else post_id
                excerpt_m = re.search(r'<div class="post-excerpt">(.*?)</div>', pa, re.DOTALL)
                excerpt = unescape(excerpt_m.group(1)) if excerpt_m else ''
                thumb_m = re.search(r'<img class="post-thumb" src="([^"]+)"', pa)
                thumb = thumb_m.group(1) if thumb_m else ''
                views_m = re.search(r'<span>👁️\s*([\d.]+K?)</span>', pa)
                views_raw = views_m.group(1) if views_m else '0'
                views = str(int(float(views_raw.replace('K', '')) * 1000)) if 'K' in views_raw else views_raw
                comments_m = re.search(r'<span>💬\s*(\d+)</span>', pa)
                comments = comments_m.group(1) if comments_m else '0'
                likes_m = re.search(r'<span>👍\s*(\d+)</span>', pa)
                likes = likes_m.group(1) if likes_m else '0'
                time_m = re.search(r'<span>🕐\s*([\d:]+)</span>', pa)
                time_str = time_m.group(1) if time_m else '00:00'
                date_m = re.search(r'<div class="day-title">(\d{4}-\d{2}-\d{2})</div>', pa)
                date_str = ''
                if date_m:
                    date_str = date_m.group(1)
                else:
                    # look backwards in content for the day-title
                    pos = pa[:0]
                    d2 = re.findall(
                        r'<div class="day-title">(\d{4}-\d{2}-\d{2})</div>', content)
                    date_str = d2[-1] if d2 else '1970-01-01'

                # find date from day-group
                post_start = content.find(pa)
                before = content[:post_start]
                day_m = re.findall(r'<div class="day-title">(\d{4}-\d{2}-\d{2})</div>', before)
                date_str = day_m[-1] if day_m else '1970-01-01'

                posts.append({
                    'id': post_id,
                    'source': 'cnblogs',
                    'title': title,
                    'slug': _slug(title),
                    'date': date_str,
                    'time': time_str if ':' in time_str else '00:00',
                    'excerpt': excerpt[:200],
                    'thumb': thumb,
                    'category': _category_for(title),
                    'views': views,
                    'comments': comments,
                    'likes': likes,
                    'content_hash': '',
                })
                count += 1
            _save_posts(posts)
            print(f"  Imported {count} posts.")

    # ── import books ──
    bk_path = os.path.join(ROOT, 'bookshelf.html')
    if os.path.exists(bk_path):
        with open(bk_path, encoding='utf-8') as f:
            html = f.read()
        m = re.search(r'<!--\s*CONTENT_MAIN\s*-->(.*?)<!--\s*/\s*CONTENT_MAIN\s*-->', html, re.DOTALL)
        if m:
            content = m.group(1)
            books = _load_json(BOOKS_JSON)
            if books:
                print("  Books data already exists, skipping.")
            else:
                count = 0
                cards = re.findall(
                    r'<div class="book-card">(.*?)</div>\s*</div>', content, re.DOTALL)
                for card in cards:
                    title_m = re.search(r'<div class="book-title">(.*?)</div>', card)
                    title = unescape(title_m.group(1)) if title_m else ''
                    if not title:
                        continue
                    author_m = re.search(r'<div class="book-author">(.*?)</div>', card)
                    author = unescape(author_m.group(1)) if author_m else ''
                    rating_m = re.search(r'<div class="book-rating">.*?([\d.]+)', card)
                    rating = rating_m.group(1) if rating_m else ''
                    desc_m = re.search(r'<div class="book-desc">(.*?)</div>', card)
                    desc = unescape(desc_m.group(1)) if desc_m else ''
                    url_m = re.search(r'<a href="([^"]+)"', card)
                    url = unescape(url_m.group(1)) if url_m else ''
                    cover_m = re.search(r'<img class="book-cover" src="([^"]+)"', card)
                    cover = cover_m.group(1) if cover_m else ''
                    books.append({
                        'id': _next_id(books),
                        'title': title,
                        'author': author,
                        'rating': rating,
                        'description': desc,
                        'url': url,
                        'cover': cover,
                    })
                    count += 1
                _save_json(BOOKS_JSON, books)
                print(f"  Imported {count} books.")

    # ── import photos ──
    gl_path = os.path.join(ROOT, 'gallery.html')
    if os.path.exists(gl_path):
        with open(gl_path, encoding='utf-8') as f:
            html = f.read()
        m = re.search(r'<!--\s*CONTENT_MAIN\s*-->(.*?)<!--\s*/\s*CONTENT_MAIN\s*-->', html, re.DOTALL)
        if m:
            content = m.group(1)
            photos = _load_json(GALLERY_JSON)
            if photos:
                print("  Photos data already exists, skipping.")
            else:
                count = 0
                items = re.findall(
                    r'<div class="gallery-item">\s*<img[^>]+src="images/gallery/([^"]+)"[^>]*>\s*<div class="gallery-caption">([^<]*)</div>\s*</div>',
                    content)
                for fname, caption in items:
                    photos.append({
                        'id': _next_id(photos),
                        'filename': fname,
                        'caption': caption,
                    })
                    count += 1
                _save_json(GALLERY_JSON, photos)
                print(f"  Imported {count} photos.")

    # ── import friends ──
    fr_path = os.path.join(ROOT, 'friends.html')
    if os.path.exists(fr_path):
        with open(fr_path, encoding='utf-8') as f:
            html = f.read()
        m = re.search(r'<!--\s*CONTENT_MAIN\s*-->(.*?)<!--\s*/\s*CONTENT_MAIN\s*-->', html, re.DOTALL)
        if m:
            content = m.group(1)
            friends = _load_json(FRIENDS_JSON)
            if friends:
                print("  Friends data already exists, skipping.")
            else:
                count = 0
                cards = re.findall(
                    r'<a class="friend-card".*?</a>', content, re.DOTALL)
                for card in cards:
                    name_m = re.search(r'<div class="friend-name">(.*?)</div>', card)
                    desc_m = re.search(r'<div class="friend-desc">(.*?)</div>', card)
                    url_m = re.search(r'href="([^"]+)"', card)
                    emoji_m = re.search(r'<span>(.)</span>', card)
                    name = unescape(name_m.group(1)) if name_m else ''
                    if not name:
                        continue
                    friends.append({
                        'id': _next_id(friends),
                        'name': name,
                        'url': url_m.group(1) if url_m else '',
                        'description': desc_m.group(1) if desc_m else '',
                        'emoji': emoji_m.group(1) if emoji_m else '🌐',
                    })
                    count += 1
                _save_json(FRIENDS_JSON, friends)
                print(f"  Imported {count} friends.")

    print("Import complete. Run 'manage.py build' to regenerate pages.")

# ═══════════════════════════════════════════════════════════
#  Admin web server
# ═══════════════════════════════════════════════════════════

import json as json_lib
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs, unquote

ADMIN_HTML = os.path.join(ROOT, 'admin.html')

def _json_response(handler, data, status=200):
    handler.send_response(status)
    handler.send_header('Content-Type', 'application/json; charset=utf-8')
    handler.send_header('Access-Control-Allow-Origin', '*')
    handler.end_headers()
    handler.wfile.write(json_lib.dumps(data, ensure_ascii=False).encode())

def _json_error(handler, msg, status=400):
    _json_response(handler, {'error': msg}, status)

def _read_body(handler):
    length = int(handler.headers.get('Content-Length', 0))
    return handler.rfile.read(length) if length > 0 else b''

def _parse_multipart(body, content_type):
    """Minimal multipart/form-data parser."""
    boundary = None
    for part in content_type.split(';'):
        part = part.strip()
        if part.startswith('boundary='):
            boundary = part[9:].strip('"').encode()
            break
    if not boundary:
        return {}
    result = {}
    parts = body.split(b'--' + boundary)
    for p in parts:
        if p.strip(b'\r\n') in (b'', b'--', b'.'):
            continue
        header_end = p.find(b'\r\n\r\n')
        if header_end < 0:
            continue
        headers_raw = p[:header_end].decode('utf-8', errors='replace')
        data = p[header_end + 4:]
        if data.endswith(b'\r\n'):
            data = data[:-2]
        name = None
        filename = None
        for line in headers_raw.split('\r\n'):
            if line.lower().startswith('content-disposition:'):
                for kv in line.split(';'):
                    kv = kv.strip()
                    if kv.startswith('name='):
                        name = kv[5:].strip('"')
                    elif kv.startswith('filename='):
                        filename = kv[9:].strip('"')
        if name:
            if filename:
                result[name] = {'filename': filename, 'data': data}
            else:
                result[name] = data.decode('utf-8', errors='replace')
    return result

class AdminHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip('/')

        if path == '/admin' or path == '/admin.html':
            self._serve_admin()
        elif path.startswith('/api/'):
            self._handle_api('GET')
        else:
            super().do_GET()

    def do_POST(self):
        self._handle_api('POST')

    def do_PUT(self):
        self._handle_api('PUT')

    def do_DELETE(self):
        self._handle_api('DELETE')

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def _serve_admin(self):
        if not os.path.exists(ADMIN_HTML):
            self.send_error(404, 'admin.html not found')
            return
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        with open(ADMIN_HTML, 'rb') as f:
            shutil.copyfileobj(f, self.wfile)

    def _handle_api(self, method):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip('/')
        segs = path.split('/')
        # /api/<entity>[/<action_or_id>]
        if len(segs) < 3 or segs[1] != 'api':
            return _json_error(self, 'Invalid API path')

        entity = unquote(segs[2])
        action = unquote(segs[3]) if len(segs) > 3 else None

        try:
            if method == 'GET':
                self._api_get(entity, action)
            elif method == 'POST':
                body = _read_body(self)
                ct = self.headers.get('Content-Type', '')
                if 'multipart/form-data' in ct:
                    data = _parse_multipart(body, ct)
                else:
                    data = json_lib.loads(body.decode()) if body else {}
                self._api_post(entity, action, data)
            elif method == 'PUT':
                raw = _read_body(self)
                body = json_lib.loads(raw.decode()) if raw else {}
                self._api_put(entity, action, body)
            elif method == 'DELETE':
                self._api_delete(entity, action)
        except Exception as e:
            _json_error(self, str(e), 500)
            import traceback
            traceback.print_exc()

    def _api_get(self, entity, action):
        if entity == 'posts' and not action:
            posts = _load_posts()
            # strip content_hash from response
            for p in posts:
                p.pop('content_hash', None)
            _json_response(self, posts)
        elif entity == 'books' and action == 'fetch-meta':
            params = parse_qs(urlparse(self.path).query)
            url = (params.get('url') or [''])[0]
            if not url:
                return _json_error(self, 'Missing url parameter')
            meta = _fetch_book_meta(url)
            # Download cover locally if found
            if meta.get('cover') and meta['cover'].startswith(('http://', 'https://')):
                meta['_cover_title'] = meta.get('title') or _slug(url)
                if _download_and_save_cover(meta['cover'], meta['_cover_title']):
                    meta['cover'] = f'images/books/{_slug(meta["_cover_title"])}.jpg'
            _json_response(self, meta)
        elif entity == 'books' and not action:
            _json_response(self, _load_json(BOOKS_JSON))
        elif entity == 'photos' and not action:
            _json_response(self, _load_json(GALLERY_JSON))
        elif entity == 'friends' and not action:
            _json_response(self, _load_json(FRIENDS_JSON))
        elif entity == 'categories' and not action:
            _json_response(self, _load_categories())
        else:
            _json_error(self, 'Not found', 404)

    def _api_post(self, entity, action, data):
        if entity == 'posts' and action == 'sync':
            _run_and_build('sync')
            _json_response(self, {'ok': True, 'message': 'Sync complete'})
        elif entity == 'posts' and action == 'add':
            title = data.get('title', 'Untitled')
            body = data.get('body', '')
            date = data.get('date', datetime.now().strftime('%Y-%m-%d'))
            time = data.get('time', datetime.now().strftime('%H:%M'))
            category = data.get('category', _category_for(title))
            cover = data.get('cover', '')
            # Write temp markdown file
            fm_lines = [f'title: {title}', f'date: {date}', f'time: {time}', f'category: {category}']
            if cover:
                fm_lines.append(f'cover: {cover}')
            md_content = '---\n' + '\n'.join(fm_lines) + '\n---\n\n' + body
            tmp = os.path.join(ROOT, '.tmp_post.md')
            with open(tmp, 'w', encoding='utf-8') as f:
                f.write(md_content)
            try:
                args = argparse.Namespace(file=tmp, cover=cover)
                cmd_posts_add(args)
            finally:
                if os.path.exists(tmp):
                    os.remove(tmp)
            # Register category emoji if provided
            if data.get('emoji'):
                cat_name = category
                cats = _load_categories()
                if cat_name not in cats:
                    cats[cat_name] = data['emoji']
                    _save_categories(cats)
            _json_response(self, {'ok': True, 'message': f'Post added: {title}'})
        elif entity == 'build' and not action:
            cmd_build(None)
            _json_response(self, {'ok': True, 'message': 'Build complete'})
        elif entity == 'posts' and action == 'build':
            cmd_build(None)
            _json_response(self, {'ok': True, 'message': 'Build complete'})
        elif entity == 'books' and not action:
            books = _load_json(BOOKS_JSON)
            url = data.get('url', '')
            title = data.get('title', '').strip()
            cover = data.get('cover', '').strip()
            author = data.get('author', '').strip()
            rating = data.get('rating', '').strip()
            desc = data.get('description', '').strip()
            # Auto-fetch from URL if title is missing
            if not title and url:
                fetched = _fetch_book_meta(url)
                if not title: title = fetched['title']
                if not author: author = fetched['author']
                if not rating: rating = fetched['rating']
                if not desc: desc = fetched['description']
                if not cover: cover = fetched['cover']
            if cover:
                if cover.startswith(('http://', 'https://')):
                    _download_and_save_cover(cover, title or _slug(url))
                    cover = f'images/books/{_slug(title or _slug(url))}.jpg'
                else:
                    cover = _handle_cover_image(cover, title or _slug(url))
            books.append({
                'id': _next_id(books),
                'title': title or _slug(url),
                'author': author,
                'rating': rating,
                'description': desc,
                'url': url,
                'cover': cover,
            })
            _rename_cover_to_title(books[-1])
            _save_json(BOOKS_JSON, books)
            cmd_build(None)
            _json_response(self, {'ok': True})
        elif entity == 'photos' and not action:
            photos = _load_json(GALLERY_JSON)
            caption = ''
            file_data = None
            if isinstance(data.get('file'), dict) and 'data' in data['file']:
                # multipart upload
                file_info = data['file']
                ext = os.path.splitext(file_info['filename'])[1].lower() or '.jpg'
                caption = data.get('caption', '') or os.path.splitext(file_info['filename'])[0]
                fname = _slug(caption) + ext
                dest = os.path.join(GALLERY_DIR, fname)
                with open(dest, 'wb') as f:
                    f.write(file_info['data'])
                photos.append({'id': _next_id(photos), 'filename': fname, 'caption': caption})
                _save_json(GALLERY_JSON, photos)
                cmd_build(None)
                _json_response(self, {'ok': True})
            else:
                _json_error(self, 'No file provided')
        elif entity == 'friends' and not action:
            friends = _load_json(FRIENDS_JSON)
            friends.append({
                'id': _next_id(friends),
                'name': data.get('name', ''),
                'url': data.get('url', ''),
                'description': data.get('description', ''),
                'emoji': data.get('emoji', '🌐'),
            })
            _save_json(FRIENDS_JSON, friends)
            cmd_build(None)
            _json_response(self, {'ok': True})
        elif entity == 'categories' and not action:
            cats = _load_categories()
            name = data.get('name', '')
            emoji = data.get('emoji', '📄')
            if name:
                cats[name] = emoji
                _save_categories(cats)
                cmd_build(None)
                _json_response(self, {'ok': True})
            else:
                _json_error(self, 'Missing name', 400)
        elif entity == 'upload' and not action:
            if isinstance(data.get('file'), dict) and 'data' in data['file']:
                f_info = data['file']
                ext = os.path.splitext(f_info['filename'])[1].lower() or '.bin'
                fname = _slug(os.path.splitext(f_info['filename'])[0]) + ext
                dest = os.path.join(IMAGES_DIR, fname)
                for i in range(1, 100):
                    if not os.path.exists(dest):
                        break
                    fname = _slug(os.path.splitext(f_info['filename'])[0]) + f'_{i}' + ext
                    dest = os.path.join(IMAGES_DIR, fname)
                with open(dest, 'wb') as f:
                    f.write(f_info['data'])
                _json_response(self, {'ok': True, 'url': f'/posts/images/{fname}'})
            else:
                _json_error(self, 'No file provided')
        else:
            _json_error(self, 'Not found', 404)

    def _api_put(self, entity, action, data):
        if entity == 'posts' and action:
            segs = self.path.rstrip('/').split('/')
            post_id = action
            posts = _load_posts()
            post = next((p for p in posts if p['id'] == post_id), None)
            if not post:
                return _json_error(self, 'Not found', 404)
            # PUT /api/posts/<id>/cover
            if len(segs) >= 5 and segs[4] == 'cover':
                cover = data.get('cover', '')
                if cover:
                    thumb = _handle_post_cover(cover, post_id)
                    if thumb:
                        post['thumb'] = thumb
                        _save_posts(posts)
                        cmd_build(None)
                        _json_response(self, {'ok': True, 'thumb': thumb})
                    else:
                        _json_error(self, 'Failed to process cover', 400)
                else:
                    _json_error(self, 'Missing cover', 400)
            # PUT /api/posts/<id> — edit post properties
            elif len(segs) == 4:
                category = data.get('category', post.get('category', 'Arch Linux'))
                emoji = data.get('emoji', '')
                post['category'] = category
                # Register new category emoji if provided
                if emoji:
                    cats = _load_categories()
                    cats[category] = emoji
                    _save_categories(cats)
                # Handle cover
                cover = data.get('cover', '')
                if cover:
                    thumb = _handle_post_cover(cover, post['id'])
                    if thumb:
                        post['thumb'] = thumb
                elif 'thumb' in post and not cover:
                    del post['thumb']
                # For custom posts, also allow title/slug/date/time
                if post.get('source') == 'custom':
                    title = data.get('title', post['title'])
                    slug = data.get('slug', post['dir'])
                    date = data.get('date', post['date'])
                    time = data.get('time', post.get('time', '00:00'))
                    old_dir = post.get('dir', _dir_name(post['id']))
                    new_dir = slug
                    # Rename directory if slug changed
                    if new_dir != old_dir:
                        old_path = os.path.join(POSTS_DIR, old_dir)
                        new_path = os.path.join(POSTS_DIR, new_dir)
                        if os.path.exists(old_path):
                            shutil.move(old_path, new_path)
                        elif os.path.exists(old_path + '.html'):
                            os.makedirs(new_path, exist_ok=True)
                            shutil.move(old_path + '.html', os.path.join(new_path, 'index.html'))
                        post['dir'] = new_dir
                    # Rewrite markdown front matter
                    md_path = os.path.join(POSTS_DIR, new_dir, f'{new_dir}.md')
                    if not os.path.exists(md_path):
                        md_path = os.path.join(POSTS_DIR, new_dir, f'{old_dir}.md')
                    if os.path.exists(md_path):
                        raw = open(md_path, encoding='utf-8').read()
                        _, body = _parse_front_matter(raw)
                        fm_lines = [f'title: {title}', f'date: {date}', f'time: {time}', f'category: {category}']
                        with open(md_path, 'w', encoding='utf-8') as f:
                            f.write('---\n' + '\n'.join(fm_lines) + '\n---\n\n' + body)
                    post['title'] = title
                    post['date'] = date
                    post['time'] = time
                _save_posts(posts)
                cmd_build(None)
                _json_response(self, {'ok': True, 'message': f'Post updated: {post["title"]}'})
        elif entity == 'books' and action:
            books = _load_json(BOOKS_JSON)
            bid = int(action)
            book = next((b for b in books if b['id'] == bid), None)
            if not book:
                return _json_error(self, 'Not found', 404)
            url_changed = 'url' in data and data['url'] != book.get('url')
            for key in ('title', 'author', 'rating', 'description', 'url'):
                if key in data:
                    book[key] = data[key]
            if url_changed:
                # URL changed: auto-fetch missing fields
                needs_fetch = not book.get('title') or not book.get('author')
                if needs_fetch and book.get('url'):
                    fetched = _fetch_book_meta(book['url'])
                    if not book.get('title'): book['title'] = fetched['title']
                    if not book.get('author'): book['author'] = fetched['author']
                    if not book.get('rating'): book['rating'] = fetched['rating']
                    if not book.get('description'): book['description'] = fetched['description']
                    if not book.get('cover') and fetched['cover']:
                        title = book.get('title', '')
                        if _download_and_save_cover(fetched['cover'], title):
                            book['cover'] = f'images/books/{_slug(title)}.jpg'
            if 'cover' in data:
                if data['cover']:
                    book['cover'] = _handle_cover_image(data['cover'], book.get('title', ''))
            _rename_cover_to_title(book)
            _save_json(BOOKS_JSON, books)
            cmd_build(None)
            _json_response(self, {'ok': True})
        elif entity == 'friends' and action:
            friends = _load_json(FRIENDS_JSON)
            fid = int(action)
            friend = next((f for f in friends if f['id'] == fid), None)
            if not friend:
                return _json_error(self, 'Not found', 404)
            for key in ('name', 'url', 'description', 'emoji'):
                if key in data:
                    friend[key] = data[key]
            _save_json(FRIENDS_JSON, friends)
            cmd_build(None)
            _json_response(self, {'ok': True})
        else:
            _json_error(self, 'Not found', 404)

    def _api_delete(self, entity, action):
        if entity == 'posts' and action:
            args = argparse.Namespace(id=action)
            cmd_posts_delete(args)
            _json_response(self, {'ok': True})
        elif entity == 'books' and action:
            books = _load_json(BOOKS_JSON)
            bid = int(action)
            books = [b for b in books if b['id'] != bid]
            _save_json(BOOKS_JSON, books)
            cmd_build(None)
            _json_response(self, {'ok': True})
        elif entity == 'photos' and action:
            photos = _load_json(GALLERY_JSON)
            pid = int(action)
            photo = next((p for p in photos if p['id'] == pid), None)
            if photo:
                fpath = os.path.join(GALLERY_DIR, photo['filename'])
                if os.path.exists(fpath):
                    os.remove(fpath)
            photos = [p for p in photos if p['id'] != pid]
            _save_json(GALLERY_JSON, photos)
            cmd_build(None)
            _json_response(self, {'ok': True})
        elif entity == 'friends' and action:
            friends = _load_json(FRIENDS_JSON)
            fid = int(action)
            friends = [f for f in friends if f['id'] != fid]
            _save_json(FRIENDS_JSON, friends)
            cmd_build(None)
            _json_response(self, {'ok': True})
        elif entity == 'categories' and action:
            cats = _load_categories()
            name = unquote(action)
            if name in cats:
                del cats[name]
                _save_categories(cats)
                cmd_build(None)
                _json_response(self, {'ok': True})
            else:
                _json_error(self, 'Not found', 404)
        else:
            _json_error(self, 'Not found', 404)

def _run_and_build(action):
    if action == 'sync':
        cmd_posts_sync(argparse.Namespace(file=None))
    cmd_build(None)

def cmd_serve(args):
    port = args.port
    print(f"Admin panel: http://localhost:{port}/admin")
    print(f"Site:       http://localhost:{port}")
    os.chdir(ROOT)
    server = HTTPServer(('0.0.0.0', port), AdminHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\nServer stopped.')

def main():
    parser = argparse.ArgumentParser(
        description='Content manager for JosiahBristow.github.io')
    parser.add_argument('--port', type=int, default=8000, help='Port for serve (default: 8000)')
    sub = parser.add_subparsers(dest='cmd')

    # posts
    p = sub.add_parser('posts')
    ps = p.add_subparsers(dest='sub')
    ps.add_parser('list').set_defaults(func=cmd_posts_list)
    ps.add_parser('sync').set_defaults(func=cmd_posts_sync)
    pa = ps.add_parser('add')
    pa.add_argument('file', help='Markdown file')
    pa.add_argument('--cover', help='Cover image URL or local path')
    pa.set_defaults(func=cmd_posts_add)
    pe = ps.add_parser('edit')
    pe.add_argument('id', help='Post ID')
    pe.add_argument('--cover', help='New cover image URL or local path')
    pe.set_defaults(func=cmd_posts_edit)
    pd = ps.add_parser('delete')
    pd.add_argument('id', help='Post ID')
    pd.set_defaults(func=cmd_posts_delete)

    # books
    p = sub.add_parser('books')
    bs = p.add_subparsers(dest='sub')
    bs.add_parser('list').set_defaults(func=cmd_books_list)
    bs.add_parser('add').set_defaults(func=cmd_books_add)
    be = bs.add_parser('edit')
    be.add_argument('id', type=int, help='Book ID')
    be.set_defaults(func=cmd_books_edit)
    bd = bs.add_parser('delete')
    bd.add_argument('id', type=int, help='Book ID')
    bd.set_defaults(func=cmd_books_delete)

    # photos
    p = sub.add_parser('photos')
    gs = p.add_subparsers(dest='sub')
    gs.add_parser('list').set_defaults(func=cmd_photos_list)
    ga = gs.add_parser('add')
    ga.add_argument('file', help='Image file path')
    ga.add_argument('caption', nargs='?', default=None, help='Caption')
    ga.set_defaults(func=cmd_photos_add)
    gd = gs.add_parser('delete')
    gd.add_argument('id', type=int, help='Photo ID')
    gd.set_defaults(func=cmd_photos_delete)

    # friends
    p = sub.add_parser('friends')
    fs = p.add_subparsers(dest='sub')
    fs.add_parser('list').set_defaults(func=cmd_friends_list)
    fs.add_parser('add').set_defaults(func=cmd_friends_add)
    fe = fs.add_parser('edit')
    fe.add_argument('id', type=int, help='Friend ID')
    fe.set_defaults(func=cmd_friends_edit)
    fd = fs.add_parser('delete')
    fd.add_argument('id', type=int, help='Friend ID')
    fd.set_defaults(func=cmd_friends_delete)

    sub.add_parser('build').set_defaults(func=cmd_build)
    sub.add_parser('import').set_defaults(func=cmd_import)
    sub.add_parser('serve').set_defaults(func=cmd_serve)

    args = parser.parse_args()
    if not args.cmd:
        parser.print_help()
        return 1

    # Pass through common args to func
    func_args = argparse.Namespace(**{k: v for k, v in vars(args).items()
                                      if k not in ('cmd', 'sub', 'func', 'port')})
    func_args.port = args.port

    return args.func(func_args)

if __name__ == '__main__':
    exit(main())
