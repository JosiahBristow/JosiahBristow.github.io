#!/usr/bin/env python3
"""Fetch posts from cnblogs and regenerate static HTML pages.

Requires: Python 3.8+, no external packages.
Runs as a GitHub Actions scheduled workflow.
"""

import re
import os
import sys
import urllib.request
import urllib.error
from html import unescape
from collections import defaultdict

CNBLOGS_URL = "https://www.cnblogs.com/JosiahBristow"
ROOT = os.path.dirname(os.path.abspath(__file__))

# ── post templates ──────────────────────────────────────────
POST_TPL = '''\
    <article class="post">
      <div class="post-header">
        <img class="post-thumb" src="{thumb}" alt="{alt}" loading="lazy">
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
                url=p['url'], title=p['title'],
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
    lines.append(f'    <h1 data-i18n="archive-title">归档</h1>')
    lines.append(f'    <p data-i18n="archive-count">共 {len(posts)} 篇随笔</p>')
    lines.append('  </div>')
    for year in sorted(years, reverse=True):
        lines.append('  <div class="archive-year">')
        lines.append(f'    <div class="archive-year-header">{year}</div>')
        lines.append('    <ul class="archive-list">')
        for p in years[year]:
            lines.append(ARCHIVE_TPL.format(date=p['date'], url=p['url'], title=p['title']))
        lines.append('    </ul>')
        lines.append('  </div>')
    return '\n'.join(lines)

def build_categories(posts):
    cats = _categorize(posts)
    lines = []
    lines.append('  <div class="page-heading">')
    lines.append(f'    <h1 data-i18n="categories-title">分类</h1>')
    lines.append(f'    <p data-i18n="categories-count">共 {len(cats)} 个分类</p>')
    lines.append('  </div>')
    for name in sorted(cats):
        plist = cats[name]
        lines.append('  <div class="category-section">')
        lines.append('    <div class="category-header">')
        lines.append(f'      {name}')
        lines.append(f'      <span class="category-count">{len(plist)} 篇</span>')
        lines.append('    </div>')
        lines.append('    <ul class="category-list">')
        for p in plist:
            lines.append(CAT_POST_TPL.format(url=p['url'], title=p['title']))
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
        f'      <span class="tag">{n} <span class="post-count">{len(cats[n])}</span></span>\n'
        for n in sorted(cats)
    )
    return f'''\
  <div class="sidebar-card">
    <h3 data-i18n="sidebar-stats">统计数据</h3>
    <div class="stat-grid">
      <div>
        <div class="stat-value">{total}</div>
        <div class="stat-label" data-i18n="stat-posts">随笔</div>
      </div>
      <div>
        <div class="stat-value">{t_likes}</div>
        <div class="stat-label" data-i18n="stat-likes">推荐</div>
      </div>
      <div>
        <div class="stat-value">{_fmt(t_views)}</div>
        <div class="stat-label" data-i18n="stat-reads">阅读</div>
      </div>
      <div>
        <div class="stat-value">{t_comments}</div>
        <div class="stat-label" data-i18n="stat-comments">评论</div>
      </div>
    </div>
  </div>

  <div class="sidebar-card">
    <h3 data-i18n="sidebar-categories">分类</h3>
    <div class="tag-list">
{tag_items}    </div>
  </div>'''

# ── helpers ─────────────────────────────────────────────────
def _alt(title):
    s = re.sub(r'[\[\]()（）]', '', title).strip()
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
        ('镜像源', 'Arch Linux'), ('输入法', 'Arch Linux'),
        ('打印机', 'Linux'), ('pip install', 'Linux'),
        ('pygame', 'Python'), ('树莓派', 'Raspberry Pi'),
    ]
    cats = defaultdict(list)
    for p in posts:
        cat = next((c for k, c in kw if k in p['title']), 'Arch Linux')
        cats[cat].append(p)
    return dict(cats)

# ── network ─────────────────────────────────────────────────
def fetch_html():
    req = urllib.request.Request(CNBLOGS_URL, headers={
        'User-Agent': 'Mozilla/5.0 (compatible; BlogSync/1.0)'
    })
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode('utf-8', errors='replace')

def parse_posts(html):
    posts = []
    # split by day blocks
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

            views = _extract_count(desc_html, '阅读')
            comments = _extract_count(desc_html, '评论')
            likes = _extract_count(desc_html, '推荐')

            posts.append({
                'title': title, 'url': url, 'thumb': thumb,
                'excerpt': excerpt, 'date': post_date, 'time': post_time,
                'views': views, 'comments': comments, 'likes': likes,
            })
    return posts

def _extract_count(text, label):
    m = re.search(rf'{label}[^)]*(\d+)', text)
    return m.group(1) if m else '0'

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
    try:
        html = fetch_html()
        posts = parse_posts(html)
    except Exception as e:
        print(f'Error: {e}', file=sys.stderr)
        return 1

    if not posts:
        print('No posts found — aborting.', file=sys.stderr)
        return 1

    posts.sort(key=lambda p: p['date'] + p['time'], reverse=True)
    print(f'Found {len(posts)} posts')

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
