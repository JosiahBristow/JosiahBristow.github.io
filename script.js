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

  var FALLBACK_SVG =
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 120" aria-hidden="true">' +
    '<path d="M50 22C32 22 18 34 16 54 14 72 18 88 28 100 36 110 44 112 50 112 56 112 64 110 72 100 82 88 86 72 84 54 82 34 68 22 50 22Z" fill="#1a1a1a"/>' +
    '<path d="M50 22C32 22 18 34 16 54 14 72 18 88 28 100 24 88 22 72 24 54 26 36 38 26 50 22Z" fill="#272727"/>' +
    '<path d="M50 50C36 50 26 64 24 82 22 96 34 108 50 110 66 108 78 96 76 82 74 64 64 50 50 50Z" fill="#f5f5f5"/>' +
    '<path class="tux-wing-l" d="M18 56C10 56 4 66 6 80 7 88 10 94 16 98 14 88 14 72 18 56Z" fill="#1a1a1a"/>' +
    '<path class="tux-wing-r" d="M82 56C90 56 96 66 94 80 93 88 90 94 84 98 86 88 86 72 82 56Z" fill="#1a1a1a"/>' +
    '<path d="M50 26C36 26 28 34 28 44 28 54 36 60 44 60 48 60 50 56 50 54 50 56 52 60 56 60 64 60 72 54 72 44 72 34 64 26 50 26Z" fill="#f5f5f5"/>' +
    '<g class="tux-eyes">' +
    '<circle cx="41" cy="38" r="4" fill="#1a1a1a"/>' +
    '<circle cx="59" cy="38" r="4" fill="#1a1a1a"/>' +
    '<circle cx="42" cy="36" r="1.5" fill="#fff"/>' +
    '<circle cx="60" cy="36" r="1.5" fill="#fff"/>' +
    '<circle cx="40" cy="39" r="0.6" fill="#fff"/>' +
    '<circle cx="58" cy="39" r="0.6" fill="#fff"/>' +
    '</g>' +
    '<path d="M42 46C46 44 54 44 58 46 56 52 52 54 50 55 48 54 44 52 42 46Z" fill="#f59e0b"/>' +
    '<path d="M44 47C47 46 53 46 56 47 54 50 51 52 50 52 49 52 46 50 44 47Z" fill="#fbbf24"/>' +
    '<ellipse cx="32" cy="114" rx="6" ry="3.5" fill="#f59e0b" transform="rotate(-25 32 114)"/>' +
    '<ellipse cx="40" cy="116" rx="6" ry="3.5" fill="#f59e0b"/>' +
    '<ellipse cx="48" cy="114" rx="6" ry="3.5" fill="#f59e0b" transform="rotate(25 48 114)"/>' +
    '<ellipse cx="52" cy="114" rx="6" ry="3.5" fill="#f59e0b" transform="rotate(-25 52 114)"/>' +
    '<ellipse cx="60" cy="116" rx="6" ry="3.5" fill="#f59e0b"/>' +
    '<ellipse cx="68" cy="114" rx="6" ry="3.5" fill="#f59e0b" transform="rotate(25 68 114)"/>' +
    '</svg>';

  function loadSvg(svgText) {
    var parser = new DOMParser();
    var doc = parser.parseFromString(svgText, 'image/svg+xml');
    var svgEl = doc.documentElement;
    if (svgEl && svgEl.tagName === 'svg') {
      svgEl.removeAttribute('width');
      svgEl.removeAttribute('height');
      svgEl.setAttribute('aria-hidden', 'true');
      tux.appendChild(svgEl);
    } else {
      tux.innerHTML = FALLBACK_SVG;
    }
    initTux();
  }

  if (window.location.protocol === 'file:') {
    loadSvg(FALLBACK_SVG);
  } else {
    fetch('tux.svg')
      .then(function(r) { return r.text(); })
      .then(loadSvg)
      .catch(function() { loadSvg(FALLBACK_SVG); });
  }

  function initTux() {
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

    var state = 'idle';
    var timer = null;

    function setState(s) {
      tux.classList.remove('tux-bounce', 'tux-jump', 'tux-talking');
      if (s === 'idle') tux.classList.add('tux-bounce');
      else if (s === 'jump') tux.classList.add('tux-jump');
      else if (s === 'talk') tux.classList.add('tux-talking');
      state = s;
    }

    function showQuote() {
      bubble.textContent = pickQuote();
      bubble.classList.add('visible');
      clearTimeout(timer);
      setState('jump');
      timer = setTimeout(function() {
        bubble.classList.remove('visible');
        setState('idle');
      }, 6000);
    }

    tux.addEventListener('animationend', function(e) {
      if (e.animationName === 'tux-jump' && state === 'jump') {
        setState('talk');
      }
    });

    function toggleQuote(e) {
      if (bubble.classList.contains('visible')) {
        bubble.classList.remove('visible');
        clearTimeout(timer);
        setState('idle');
      } else {
        showQuote();
      }
    }

    tux.addEventListener('click', toggleQuote);
    tux.addEventListener('keydown', function(e) {
      if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); toggleQuote(e); }
    });

    setState('idle');
    document.body.appendChild(tux);
  }
})();
