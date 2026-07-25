#!/usr/bin/env python3
"""Fetch posts from cnblogs and regenerate static HTML pages.

Requires: Python 3.8+, no external packages.
Runs as a GitHub Actions scheduled workflow.
"""

import re
import os
import sys
import shutil
import urllib.request
import urllib.error
from html import unescape
from collections import defaultdict

CNBLOGS_URL = "https://www.cnblogs.com/JosiahBristow"
ROOT = os.path.dirname(os.path.abspath(__file__))
POSTS_DIR = os.path.join(ROOT, "posts")
IMAGES_DIR = os.path.join(POSTS_DIR, "images")

# ── post templates ──────────────────────────────────────────
POST_TPL = '''\
    <article class="post">
      <div class="post-header">
        <img class="post-thumb" src="{thumb}" alt="{alt}" loading="lazy" referrerpolicy="no-referrer">
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

POST_PAGE_TPL = '''\
<!DOCTYPE html>
<html lang="zh-cn">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} - JosiahBristow</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:ital,wght@0,400;0,600;0,700;1,400&display=swap" rel="stylesheet">
<link rel="stylesheet" href="../style.css">
<link rel="icon" type="image/svg+xml" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🐧</text></svg>">
<link rel="alternate icon" href="https://avatars.githubusercontent.com/u/123633729?s=32&v=4">
</head>
<body>

<header class="header">
  <div class="header-title"><a href="../index.html">JosiahBristow</a></div>
  <div class="header-prompt">Just For Fun!</div>
  <div class="header-sub">Arch Linux, Linux tools, and developer life</div>
</header>

<nav class="nav">
  <div class="nav-inner">
    <a href="../index.html">\U0001f3e0 <span data-i18n="nav-home">\u9996\u9875</span></a>
    <a href="../archive.html">\U0001f4e6 <span data-i18n="nav-archive">\u5f52\u6863</span></a>
    <a href="../categories.html">\U0001f3f7\ufe0f <span data-i18n="nav-categories">\u5206\u7c7b</span></a>
    <a href="../about.html">\U0001f464 <span data-i18n="nav-about">\u5173\u4e8e</span></a>
  </div>
</nav>

<div class="page-full">

<article class="post-article">
  <div class="post-article-heading">
    <h1 class="post-article-title">{title}</h1>
    <div class="post-article-meta">
      <span>\U0001f550 {date} {time}</span>
      <span>\U0001f441\ufe0f {views}</span>
      <span>\U0001f4ac {comments}</span>
      <span>\U0001f44d {likes}</span>
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
  <p>\U0001f427 &copy; 2024-2026 JosiahBristow. Built with \u2764\ufe0f for <a href="https://pages.github.com/">GitHub Pages</a>.</p>
</footer>

<script src="../script.js"></script>
<script src="../lang.js"></script>
</body>
</html>'''

# ── page builders ───────────────────────────────────────────
def build_index(posts):
    groups = defaultdict(list)
    for p in posts:
        groups[p['date']].append(p)
    lines = []
    for date_str in sorted(groups, reverse=True):
        lines.append('  <div class="day-group">')
        lines.append(f'    <div class="day-title">{date_str}</div>')
        for p in groups[date_str]:
            lines.append(POST_TPL.format(
                url=p['local_url'], title=p['title'],
                thumb=p['thumb'], alt=_alt(p['title']),
                excerpt=p['excerpt'],
                time=p['time'], views=p['views'],
                comments=p['comments'], likes=p['likes'],
            ))
        lines.append('  </div>')
    return '\n'.join(lines)

def build_archive(posts):
    years = defaultdict(list)
    for p in posts:
        years[p['date'][:4]].append(p)
    lines = []
    lines.append('  <div class="page-heading">')
    lines.append(f'    <h1>\U0001f4e6 <span data-i18n="archive-title">\u5f52\u6863</span></h1>')
    lines.append(f'    <p>\U0001f4c4 <span data-i18n="archive-count">\u5171 {len(posts)} \u7bc7\u968f\u7b14</span></p>')
    lines.append('  </div>')
    for year in sorted(years, reverse=True):
        lines.append('  <div class="archive-year">')
        lines.append(f'    <div class="archive-year-header">\U0001f4c5 {year}</div>')
        lines.append('    <ul class="archive-list">')
        for p in years[year]:
            lines.append(ARCHIVE_TPL.format(date=p['date'], url=p['local_url'], title=p['title']))
        lines.append('    </ul>')
        lines.append('  </div>')
    return '\n'.join(lines)

CAT_EMOJI = {
    'Arch Linux': '\U0001f427',
    'Linux': '\U0001f4bb',
    'Python': '\U0001f40d',
    'Raspberry Pi': '\U0001f967',
}

def build_categories(posts):
    cats = _categorize(posts)
    lines = []
    lines.append('  <div class="page-heading">')
    lines.append(f'    <h1>\U0001f3f7\ufe0f <span data-i18n="categories-title">\u5206\u7c7b</span></h1>')
    lines.append(f'    <p>\U0001f4c2 <span data-i18n="categories-count">\u5171 {len(cats)} \u4e2a\u5206\u7c7b</span></p>')
    lines.append('  </div>')
    for name in sorted(cats):
        plist = cats[name]
        emoji = CAT_EMOJI.get(name, '\U0001f4c4')
        lines.append('  <div class="category-section">')
        lines.append('    <div class="category-header">')
        lines.append(f'      {emoji} {name}')
        lines.append(f'      <span class="category-count">{len(plist)} \u7bc7</span>')
        lines.append('    </div>')
        lines.append('    <ul class="category-list">')
        for p in plist:
            lines.append(CAT_POST_TPL.format(url=p['local_url'], title=p['title']))
        lines.append('    </ul>')
        lines.append('  </div>')
    return '\n'.join(lines)

def build_sidebar(posts):
    total = len(posts)
    t_views = sum(int(p['views']) for p in posts if p['views'].isdigit())
    t_likes = sum(int(p['likes']) for p in posts if p['likes'].isdigit())
    t_comments = sum(int(p['comments']) for p in posts if p['comments'].isdigit())
    cats = _categorize(posts)
    tag_items = ''.join(
        f'      <span class="tag">{CAT_EMOJI.get(n, "\U0001f4c4")} {n} <span class="post-count">{len(cats[n])}</span></span>\n'
        for n in sorted(cats)
    )
    return f'''\
  <div class="sidebar-card profile">
    <img class="profile-avatar" src="https://avatars.githubusercontent.com/u/123633729?s=96&v=4" alt="avatar" loading="lazy">
    <div class="profile-name">JosiahBristow</div>
    <div class="profile-bio">Arch Linux user \u00b7 Linux enthusiast \u00b7 I just want to go out and see if there are another way to live life.</div>
    <div class="profile-links">
      <a target="_blank" href="https://github.com/josiahbristow">\U0001f419 GitHub</a>
      <a target="_blank" href="https://josiahbristow.github.io/">\U0001f310 Blog</a>
    </div>
  </div>

  <div class="sidebar-card">
    <h3 data-i18n="sidebar-stats">\u7edf\u8ba1\u6570\u636e</h3>
    <div class="stat-grid">
      <div>
        <div class="stat-value">{total}</div>
        <div class="stat-label">\U0001f4dd <span data-i18n="stat-posts">\u968f\u7b14</span></div>
      </div>
      <div>
        <div class="stat-value">{t_likes}</div>
        <div class="stat-label">\U0001f44d <span data-i18n="stat-likes">\u63a8\u8350</span></div>
      </div>
      <div>
        <div class="stat-value">{_fmt(t_views)}</div>
        <div class="stat-label">\U0001f441\ufe0f <span data-i18n="stat-reads">\u9605\u8bfb</span></div>
      </div>
      <div>
        <div class="stat-value">{t_comments}</div>
        <div class="stat-label">\U0001f4ac <span data-i18n="stat-comments">\u8bc4\u8bba</span></div>
      </div>
    </div>
  </div>

  <div class="sidebar-card">
    <h3 data-i18n="sidebar-categories">\u5206\u7c7b</h3>
    <div class="tag-list">
{tag_items}    </div>
  </div>'''

# ── helpers ─────────────────────────────────────────────────
def _alt(title):
    s = re.sub(r'[\[\]()\uff08\uff09]', '', title).strip()
    return s[:20]

def _fmt(n):
    if n >= 10000:
        return f'{n//1000}K'
    if n >= 1000:
        return f'{n/1000:.1f}K'
    return str(n)

def _categorize(posts):
    kw = [
        ('Flathub', 'Arch Linux'), ('pacman', 'Arch Linux'),
        ('Waydroid', 'Arch Linux'), ('archlinuxcn', 'Arch Linux'),
        ('\u955c\u50cf\u6e90', 'Arch Linux'), ('\u8f93\u5165\u6cd5', 'Arch Linux'),
        ('\u6253\u5370\u673a', 'Linux'), ('pip install', 'Linux'),
        ('pygame', 'Python'), ('\u6811\u8393\u6d3e', 'Raspberry Pi'),
    ]
    cats = defaultdict(list)
    for p in posts:
        cat = next((c for k, c in kw if k in p['title']), 'Arch Linux')
        cats[cat].append(p)
    return dict(cats)

def _post_id(url):
    return url.rstrip('/').split('/')[-1]

def _local_url(url):
    return f'posts/{_post_id(url)}.html'

def _local_path(url):
    return os.path.join(POSTS_DIR, f'{_post_id(url)}.html')

# ── network ─────────────────────────────────────────────────
def fetch_page(page=1):
    url = f'{CNBLOGS_URL}?page={page}' if page > 1 else CNBLOGS_URL
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (compatible; BlogSync/1.0)'
    })
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode('utf-8', errors='replace')

def parse_posts(html):
    posts = []
    day_blocks = re.findall(
        r'<div class="day[^"]*"[^>]*>.*?</div>\s*</div>\s*</div>',
        html, re.DOTALL
    )
    for day_html in day_blocks:
        date_m = re.search(r'class="dayTitle"[^>]*>\s*<a[^>]*>([^<]+)', day_html)
        date_str = date_m.group(1).strip() if date_m else ''

        for pm in re.finditer(
            r'<div class="postTitle[^"]*"[^>]*>.*?<a class="postTitle2[^"]*"\s*href="([^"]+)"[^>]*>.*?<span>([^<]*)</span>.*?</a>.*?</div>\s*'
            r'<div class="postCon">(.*?)</div>\s*<div class="clear"></div>\s*'
            r'<div class="postDesc">(.*?)</div>',
            day_html, re.DOTALL
        ):
            url = pm.group(1).strip()
            title = unescape(pm.group(2).strip())
            con_html = pm.group(3)
            desc_html = pm.group(4)

            thumb_m = re.search(r'<img[^>]+src="([^"]+)"[^>]*class="desc_img"', con_html)
            thumb = unescape(thumb_m.group(1)) if thumb_m else ''

            excerpt_m = re.search(r'class="c_b_p_desc"[^>]*>(.*?)<a[^>]+class="c_b_p_desc_readmore"', con_html, re.DOTALL)
            excerpt = re.sub(r'<[^>]+>', '', excerpt_m.group(1) if excerpt_m else '').strip()
            excerpt = unescape(excerpt)

            time_m = re.search(r'posted @ (\d{4}-\d{2}-\d{2}) (\d{2}:\d{2})', desc_html)
            post_date = time_m.group(1) if time_m else date_str
            post_time = time_m.group(2) if time_m else '00:00'

            views = _extract_count(desc_html, '\u9605\u8bfb')
            comments = _extract_count(desc_html, '\u8bc4\u8bba')
            likes = _extract_count(desc_html, '\u63a8\u8350')

            posts.append({
                'title': title, 'url': url,
                'thumb': thumb, 'excerpt': excerpt,
                'date': post_date, 'time': post_time,
                'views': views, 'comments': comments, 'likes': likes,
            })
    return posts

def _extract_count(text, label):
    m = re.search(rf'{label}\((\d+)\)', text)
    return m.group(1) if m else '0'

# ── article fetching ────────────────────────────────────────
def fetch_article(post_url):
    req = urllib.request.Request(post_url, headers={
        'User-Agent': 'Mozilla/5.0 (compatible; BlogSync/1.0)'
    })
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode('utf-8', errors='replace')

def extract_body(html):
    m = re.search(
        r'<div id="cnblogs_post_body"[^>]*>(.*?)</div>\s*<div class="clear"></div>',
        html, re.DOTALL
    )
    if not m:
        return ''
    body = m.group(1).strip()
    # remove CNBlogs injected elements like next/prev anchors
    body = re.sub(r'<a\s+id="[^"]*next_[^"]*"[^>]*>.*?</a>', '', body)
    return body

def _download_image(img_url, images_dir):
    filename = os.path.basename(img_url.split('?')[0])
    if not filename:
        return None
    local_path = os.path.join(images_dir, filename)
    if os.path.exists(local_path):
        return f'images/{filename}'
    try:
        req = urllib.request.Request(img_url, headers={
            'User-Agent': 'Mozilla/5.0 (compatible; BlogSync/1.0)'
        })
        with urllib.request.urlopen(req, timeout=30) as resp:
            with open(local_path, 'wb') as f:
                shutil.copyfileobj(resp, f)
        print(f'    downloaded image: {filename}')
        return f'images/{filename}'
    except Exception as e:
        print(f'    failed to download {img_url}: {e}')
        return None

def process_images(body, images_dir):
    def _replace(m):
        src = unescape(m.group(1))
        local = _download_image(src, images_dir)
        if local:
            attrs = m.group(2) or ''
            attrs = re.sub(r'\breferrerpolicy\s*=\s*"[^"]*"', '', attrs)
            return f'<img src="{local}"{attrs} loading="lazy"'
        return m.group(0)
    return re.sub(
        r'<img\s+([^>]*?)src="([^"]+)"([^>]*)>',
        lambda m: _replace_img_tag(m),
        body
    )

def _replace_img_tag(m):
    prefix = m.group(1) or ''
    src = unescape(m.group(2))
    suffix = m.group(3) or ''
    local = _download_image(src, IMAGES_DIR)
    if local:
        suffix = re.sub(r'\breferrerpolicy\s*=\s*"[^"]*"', '', suffix)
        suffix = re.sub(r'\bloading\s*=\s*"[^"]*"', '', suffix)
        return f'<img {prefix}src="{local}"{suffix} loading="lazy">'
    return m.group(0)

def generate_post_page(post, body):
    return POST_PAGE_TPL.format(
        title=post['title'],
        body=body,
        date=post['date'],
        time=post['time'],
        views=post['views'],
        comments=post['comments'],
        likes=post['likes'],
    )

# ── file injection ──────────────────────────────────────────
BUILDERS = {
    'index.html': ('CONTENT_MAIN', build_index),
    'archive.html': ('CONTENT_MAIN', build_archive),
    'categories.html': ('CONTENT_MAIN', build_categories),
}

INJECT_ALL = ['index.html', 'archive.html', 'categories.html']

def inject(filepath, marker, new_content):
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()
    text = re.sub(
        rf'<!--\s*{marker}\s*-->.*?<!--\s*/\s*{marker}\s*-->',
        f'<!-- {marker} -->\n{new_content}\n<!-- /{marker} -->',
        text, flags=re.DOTALL
    )
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(text)

# ── main ────────────────────────────────────────────────────
def main():
    print('Fetching posts from cnblogs...')
    posts = []
    try:
        for page in range(1, 100):
            html = fetch_page(page)
            batch = parse_posts(html)
            if not batch:
                break
            posts.extend(batch)
            print(f'  page {page}: {len(batch)} posts')
        if not posts:
            print('No posts found \u2014 aborting.', file=sys.stderr)
            return 1
    except Exception as e:
        print(f'Error: {e}', file=sys.stderr)
        return 1

    posts.sort(key=lambda p: p['date'] + p['time'], reverse=True)
    print(f'Found {len(posts)} posts')

    # add local link info
    for p in posts:
        p['local_url'] = _local_url(p['url'])

    # ── generate post pages ──────────────────────────────────
    os.makedirs(POSTS_DIR, exist_ok=True)
    os.makedirs(IMAGES_DIR, exist_ok=True)

    # remove stale post HTML files (keep images)
    for fname in os.listdir(POSTS_DIR):
        if fname.endswith('.html'):
            os.remove(os.path.join(POSTS_DIR, fname))

    for p in posts:
        local = _local_path(p['url'])
        if os.path.exists(local):
            print(f'  skipping (exists): {_post_id(p["url"])}.html')
            continue
        print(f'  fetching article: {p["title"][:40]}...')
        try:
            html = fetch_article(p['url'])
            body = extract_body(html)
            if not body:
                print(f'    warning: empty body for {p["url"]}')
                body = '<p><em>Content could not be fetched.</em></p>'
            else:
                body = process_images(body, IMAGES_DIR)
            page = generate_post_page(p, body)
            with open(local, 'w', encoding='utf-8') as f:
                f.write(page)
            print(f'    wrote {_post_id(p["url"])}.html')
        except Exception as e:
            print(f'    failed: {e}')
            # write a stub so the link doesn't 404
            page = generate_post_page(p, '<p><em>Failed to fetch content.</em></p>')
            with open(local, 'w', encoding='utf-8') as f:
                f.write(page)

    # ── update listing pages ─────────────────────────────────
    for filename, (marker, builder) in BUILDERS.items():
        path = os.path.join(ROOT, filename)
        content = builder(posts)
        inject(path, marker, content)
        print(f'  updated {filename}')

    sidebar = build_sidebar(posts)
    for filename in INJECT_ALL:
        path = os.path.join(ROOT, filename)
        inject(path, 'SIDEBAR', sidebar)
        print(f'  updated sidebar in {filename}')

    print('Done.')
    return 0

if __name__ == '__main__':
    exit(main())
