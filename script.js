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

  function showPage(page) {
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
    pagination.innerHTML = '<button data-dir="prev">\u2039</button>';
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

