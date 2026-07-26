(function() {
  var toggle = document.getElementById('themeToggle');
  if (!toggle) return;
  var html = document.documentElement;
  var STORAGE_KEY = 'theme';

  function getPreferredTheme() {
    var saved = localStorage.getItem(STORAGE_KEY);
    if (saved === 'dark' || saved === 'light') return saved;
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  }

  var giscusTheme = { light: 'catppuccin_latte', dark: 'catppuccin_mocha' };

  function setGiscusConfig(theme) {
    var iframe = document.querySelector('iframe.giscus-frame');
    if (iframe) {
      var lang = document.documentElement.lang === 'en' ? 'en' : 'zh-CN';
      iframe.contentWindow.postMessage({
        giscus: { setConfig: { theme: giscusTheme[theme], lang: lang } }
      }, 'https://giscus.app');
    }
  }

  function setTheme(theme) {
    html.setAttribute('data-theme', theme);
    toggle.textContent = theme === 'dark' ? '☀️' : '🌙';
    localStorage.setItem(STORAGE_KEY, theme);
  }

  setTheme(getPreferredTheme());

  toggle.addEventListener('click', function() {
    var current = html.getAttribute('data-theme');
    var next = current === 'dark' ? 'light' : 'dark';
    setTheme(next);
    setGiscusConfig(next);
  });
})();

(function() {
  var btn = document.getElementById('backToTop');
  if (!btn) return;

  function onScroll() {
    if (window.scrollY > 300) {
      btn.classList.add('visible');
    } else {
      btn.classList.remove('visible');
    }
  }

  window.addEventListener('scroll', onScroll);
  onScroll();

  btn.addEventListener('click', function() {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  });
})();

(function() {
  var groups = document.querySelectorAll('.day-group');
  var pagination = document.getElementById('pagination');
  if (!groups.length || !pagination) return;

  var postList = [];
  for (var g = 0; g < groups.length; g++) {
    var posts = groups[g].querySelectorAll('.post');
    for (var p = 0; p < posts.length; p++) {
      postList.push({ el: posts[p], gi: g });
    }
  }

  var PER_PAGE = 7;
  var total = postList.length;
  var pages = Math.ceil(total / PER_PAGE);
  var currentPage = 1;

  function showPage(page) {
    currentPage = page;
    page = Math.max(1, Math.min(page, pages));
    var first = (page - 1) * PER_PAGE;
    var last = Math.min(page * PER_PAGE, total);

    var vis = {};
    for (var i = first; i < last; i++) vis[postList[i].gi] = true;

    for (var g = 0; g < groups.length; g++) {
      groups[g].style.display = vis[g] ? '' : 'none';
    }

    var btns = pagination.querySelectorAll('button');
    for (var j = 0; j < btns.length; j++) {
      var btn = btns[j];
      if (btn.dataset.page) {
        btn.classList.toggle('active', parseInt(btn.dataset.page) === page);
      }
      if (btn.dataset.dir === 'prev') btn.disabled = page <= 1;
      if (btn.dataset.dir === 'next') btn.disabled = page >= pages;
    }

    var hash = '#page-' + page;
    if (window.location.hash !== hash) history.replaceState(null, '', hash);
  }

  function render() {
    var prev = document.createElement('button');
    prev.dataset.dir = 'prev';
    prev.textContent = '\u2039';
    prev.addEventListener('click', function() { showPage(currentPage - 1); });
    pagination.appendChild(prev);
    for (var p = 1; p <= pages; p++) {
      var btn = document.createElement('button');
      btn.textContent = p;
      btn.dataset.page = p;
      btn.addEventListener('click', function() { showPage(parseInt(this.dataset.page)); });
      pagination.appendChild(btn);
    }
    var next = document.createElement('button');
    next.dataset.dir = 'next';
    next.textContent = '\u203a';
    next.addEventListener('click', function() { showPage(currentPage + 1); });
    pagination.appendChild(next);
  }

  render();
  var initial = 1;
  var m = window.location.hash.match(/^#page-(\d+)$/);
  if (m) initial = parseInt(m[1]);
  showPage(initial);
})();

(function() {
  var toggles = document.querySelectorAll('.view-toggle');
  toggles.forEach(function(toggle) {
    var container = toggle.parentElement.querySelector('.bookshelf-grid[data-view], .post-grid[data-view]');
    if (!container) return;
    var btns = toggle.querySelectorAll('button');
    var key = container.classList.contains('bookshelf-grid') ? 'bookshelf-view' : 'post-view';
    var saved = localStorage.getItem(key);
    if (saved === 'grid') {
      btns.forEach(function(b) { b.classList.toggle('active', b.dataset.view === 'grid'); });
      container.classList.add('grid-mode');
      container.dataset.view = 'grid';
    }
    btns.forEach(function(btn) {
      btn.addEventListener('click', function() {
        var view = this.dataset.view;
        btns.forEach(function(b) { b.classList.toggle('active', b.dataset.view === view); });
        container.classList.toggle('grid-mode', view === 'grid');
        container.dataset.view = view;
        localStorage.setItem(key, view);
      });
    });
  });
})();

(function() {
  var quotes = [
    { zh: '空谈无益，放码过来。', en: 'Talk is cheap. Show me the code.' },
    { zh: '智慧就是避免做无用功，同时还能把事做成。', en: 'Intelligence is the ability to avoid doing work, yet getting the work done.' },
    { zh: '真正的开源——你有权掌控自己的命运。', en: 'In real open source, you have the right to control your own destiny.' },
    { zh: '大多数优秀程序员写代码，不为钱也不为名，只是因为编程很有趣。', en: 'Most good programmers do programming not because they expect to get paid or get adulation by the public, but because it is fun to program.' },
    { zh: '差程序员操心代码，好程序员操心数据结构。', en: 'Bad programmers worry about the code. Good programmers worry about data structures and their relationships.' },
    { zh: 'Linux 的哲学就是"自己动手"。没错，就是这样。', en: 'The Linux philosophy is \'Do it yourself\'. Yes, that\'s it.' },
    { zh: '软件就像性：免费的时候更好。', en: 'Software is like sex: it\'s better when it\'s free.' },
    { zh: '我是个自大狂，但也是个该死的优秀程序员。', en: 'I\'m an egomaniac, but I\'m also a damn good programmer.' }
  ];

  var tux = document.createElement('div');
  tux.className = 'tux-mascot';
  tux.setAttribute('role', 'button');
  tux.setAttribute('tabindex', '0');
  tux.setAttribute('aria-label', 'Tux, Linux mascot');

  var img = document.createElement('img');
  img.src = 'tux_pet.svg';
  img.alt = '';
  img.style.transform = 'scaleX(-1)';
  tux.appendChild(img);

  var bubble = document.createElement('div');
  bubble.className = 'tux-speech';
  tux.appendChild(bubble);

  var lastIdx = -1;
  function pickQuote() {
    var idx;
    do { idx = Math.floor(Math.random() * quotes.length); }
    while (idx === lastIdx && quotes.length > 1);
    lastIdx = idx;
    var lang = document.documentElement.lang;
    return quotes[idx][lang === 'en' ? 'en' : 'zh'];
  }

  var hideTimer = null;
  var autoTimer = null;
  var paused = false;

  function showQuote() {
    bubble.textContent = pickQuote();
    bubble.classList.add('visible');
    clearTimeout(hideTimer);
    tux.classList.add('tux-jump');
    hideTimer = setTimeout(function() {
      bubble.classList.remove('visible');
      tux.classList.remove('tux-jump');
    }, 6000);
  }

  function scheduleNext() {
    clearTimeout(autoTimer);
    if (paused) return;
    autoTimer = setTimeout(function() {
      showQuote();
      scheduleNext();
    }, 8000 + Math.random() * 15000);
  }

  function togglePause() {
    paused = !paused;
    if (paused) {
      clearTimeout(autoTimer);
      clearTimeout(hideTimer);
      bubble.classList.remove('visible');
      tux.classList.remove('tux-jump');
    } else {
      scheduleNext();
    }
  }

  tux.addEventListener('animationend', function(e) {
    if (e.animationName === 'tux-jump') {
      tux.classList.remove('tux-jump');
    }
  });

  tux.addEventListener('click', togglePause);
  tux.addEventListener('keydown', function(e) {
    if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); togglePause(e); }
  });

  showQuote();
  scheduleNext();
  document.body.appendChild(tux);
})();

(function() {
  var pres = document.querySelectorAll('.post-article-body pre');
  if (!pres.length) return;

  pres.forEach(function(pre) {
    var code = pre.querySelector('code');
    var lang = '';
    if (code) {
      var m = code.className.match(/language-(\w+)/);
      if (m) lang = m[1];
    }

    var wrap = document.createElement('div');
    wrap.className = 'code-block-wrap';

    var bar = document.createElement('div');
    bar.className = 'code-titlebar';

    var dots = document.createElement('div');
    dots.className = 'code-dots';
    'ryg'.split('').forEach(function(c) {
      var dot = document.createElement('span');
      dot.className = 'code-dot ' + ({ r: 'red', y: 'yellow', g: 'green' })[c];
      dots.appendChild(dot);
    });
    bar.appendChild(dots);

    if (lang) {
      var lbl = document.createElement('span');
      lbl.className = 'code-lang';
      lbl.textContent = lang.charAt(0).toUpperCase() + lang.slice(1);
      bar.appendChild(lbl);
    }

    var actions = document.createElement('div');
    actions.className = 'code-actions';

    var copyBtn = document.createElement('button');
    copyBtn.className = 'code-btn code-copy';
    copyBtn.textContent = 'Copy';
    copyBtn.addEventListener('click', function() {
      var text = pre.textContent;
      navigator.clipboard.writeText(text).then(function() {
        copyBtn.textContent = 'Copied';
        setTimeout(function() { copyBtn.textContent = 'Copy'; }, 1500);
      });
    });
    actions.appendChild(copyBtn);

    var foldBtn = document.createElement('button');
    foldBtn.className = 'code-btn code-fold';
    foldBtn.textContent = '\u2212';
    foldBtn.addEventListener('click', function() {
      wrap.classList.toggle('collapsed');
      foldBtn.textContent = wrap.classList.contains('collapsed') ? '+' : '\u2212';
    });
    actions.appendChild(foldBtn);

    bar.appendChild(actions);
    pre.parentNode.insertBefore(wrap, pre);
    wrap.appendChild(bar);
    wrap.appendChild(pre);
  });
})();

(function() {
  var codes = document.querySelectorAll('.post-article-body pre code[class*="language-"]');
  if (!codes.length) return;

  var lightCSS = document.createElement('link');
  lightCSS.rel = 'stylesheet';
  lightCSS.href = 'https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github.min.css';
  lightCSS.id = 'hljs-light';
  document.head.appendChild(lightCSS);

  var darkCSS = document.createElement('link');
  darkCSS.rel = 'stylesheet';
  darkCSS.href = 'https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github-dark.min.css';
  darkCSS.id = 'hljs-dark';
  darkCSS.disabled = true;
  document.head.appendChild(darkCSS);

  var html = document.documentElement;
  function syncHLJSTheme() {
    var dark = html.getAttribute('data-theme') === 'dark';
    lightCSS.disabled = dark;
    darkCSS.disabled = !dark;
  }
  syncHLJSTheme();

  var toggle = document.getElementById('themeToggle');
  if (toggle) {
    toggle.addEventListener('click', syncHLJSTheme);
  }

  var sc = document.createElement('script');
  sc.src = 'https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js';
  sc.async = true;
  sc.onload = function() { hljs.highlightAll(); };
  document.head.appendChild(sc);
})();

(function() {
  var body = document.querySelector('.post-article-body');
  if (!body) return;

  var headings = body.querySelectorAll('h2, h3');
  if (headings.length < 2) return;

  headings.forEach(function(h) {
    if (!h.id) {
      var base = h.textContent.toLowerCase().replace(/[^\w\u4e00-\u9fff]+/g, '-').replace(/^-+|-+$/g, '');
      h.id = base || 'h-' + Math.random().toString(36).slice(2, 7);
    }
  });

  var overlay = document.createElement('div');
  overlay.className = 'toc-overlay';

  var panel = document.createElement('div');
  panel.className = 'toc-panel';

  var closeBtn = document.createElement('button');
  closeBtn.className = 'toc-close';
  closeBtn.textContent = '\u2715';
  closeBtn.addEventListener('click', closeTOC);
  panel.appendChild(closeBtn);

  var title = document.createElement('h3');
  title.textContent = 'Contents';
  panel.appendChild(title);

  var list = document.createElement('ul');
  list.className = 'toc-list';

  headings.forEach(function(h) {
    var item = document.createElement('li');
    item.className = 'toc-item';
    var link = document.createElement('a');
    link.className = 'toc-link';
    if (h.tagName === 'H3') link.classList.add('h3');
    link.href = '#' + h.id;
    link.textContent = h.textContent;
    link.addEventListener('click', function(e) {
      e.preventDefault();
      h.scrollIntoView({ behavior: 'smooth' });
      closeTOC();
    });
    item.appendChild(link);
    list.appendChild(item);
  });

  panel.appendChild(list);
  overlay.addEventListener('click', closeTOC);
  document.body.appendChild(overlay);
  document.body.appendChild(panel);

  var floatGroup = document.querySelector('.float-group');
  if (floatGroup) {
    var tocBtn = document.createElement('button');
    tocBtn.className = 'float-btn';
    tocBtn.id = 'tocToggle';
    tocBtn.textContent = '\u2630';
    tocBtn.setAttribute('aria-label', 'Table of contents');
    tocBtn.addEventListener('click', toggleTOC);
    floatGroup.insertBefore(tocBtn, floatGroup.firstChild);
  }

  function toggleTOC() {
    overlay.classList.toggle('open');
    panel.classList.toggle('open');
  }

  function closeTOC() {
    overlay.classList.remove('open');
    panel.classList.remove('open');
  }

  var tocLinks = list.querySelectorAll('.toc-link');
  function updateActive() {
    var minDiff = Infinity;
    var active = null;
    headings.forEach(function(h, i) {
      var rect = h.getBoundingClientRect();
      var diff = Math.abs(rect.top);
      if (diff < minDiff) {
        minDiff = diff;
        active = i;
      }
    });
    tocLinks.forEach(function(l, i) {
      l.classList.toggle('active', i === active);
    });
  }

  window.addEventListener('scroll', updateActive);
  updateActive();
})();

(function() {
  var body = document.querySelector('.post-article-body');
  if (!body) return;

  var lightboxEl = document.createElement('div');
  lightboxEl.className = 'lightbox';
  var lbImg = document.createElement('img');
  lightboxEl.appendChild(lbImg);
  document.body.appendChild(lightboxEl);

  function openLightbox(src) {
    lbImg.src = src;
    lightboxEl.classList.add('open');
  }

  function closeLightbox() {
    lightboxEl.classList.remove('open');
  }

  lightboxEl.addEventListener('click', closeLightbox);
  document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') closeLightbox();
  });

  body.querySelectorAll('img').forEach(function(img) {
    var wrap = document.createElement('div');
    wrap.className = 'img-wrap';

    var parent = img.parentNode;
    var isLinked = parent.tagName === 'A';

    if (isLinked) {
      parent.parentNode.insertBefore(wrap, parent);
      wrap.appendChild(parent);
    } else {
      parent.insertBefore(wrap, img);
      wrap.appendChild(img);
    }

    var foldBtn = document.createElement('button');
    foldBtn.className = 'img-fold-btn';
    foldBtn.textContent = '\u2212';
    foldBtn.addEventListener('click', function(e) {
      e.stopPropagation();
      wrap.classList.toggle('collapsed');
      foldBtn.textContent = wrap.classList.contains('collapsed') ? '+' : '\u2212';
    });
    wrap.appendChild(foldBtn);

    img.addEventListener('click', function(e) {
      if (isLinked) e.preventDefault();
      openLightbox(img.src);
    });
  });
})();

