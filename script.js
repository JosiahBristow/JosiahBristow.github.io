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

  function setGiscusTheme(theme) {
    var iframe = document.querySelector('iframe.giscus-frame');
    if (iframe) {
      iframe.contentWindow.postMessage({
        giscus: { setConfig: { theme: giscusTheme[theme] } }
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
    setGiscusTheme(next);
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
