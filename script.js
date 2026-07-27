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

  var PER_PAGE = 8;
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
  var items = document.querySelectorAll('.bookshelf-grid > .book-card');
  var pagination = document.getElementById('pagination');
  if (!items.length || !pagination) return;

  var PER_PAGE = 8;
  var total = items.length;
  var pages = Math.ceil(total / PER_PAGE);
  var currentPage = 1;

  function showPage(page) {
    currentPage = page;
    page = Math.max(1, Math.min(page, pages));
    var first = (page - 1) * PER_PAGE;
    var last = Math.min(page * PER_PAGE, total);
    for (var i = 0; i < items.length; i++) {
      items[i].style.display = (i >= first && i < last) ? '' : 'none';
    }
    var btns = pagination.querySelectorAll('button');
    for (var j = 0; j < btns.length; j++) {
      var btn = btns[j];
      if (btn.dataset.page) btn.classList.toggle('active', parseInt(btn.dataset.page) === page);
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
  var items = document.querySelectorAll('.gallery-grid > .gallery-item');
  var pagination = document.getElementById('pagination');
  if (!items.length || !pagination) return;

  var PER_PAGE = 8;
  var total = items.length;
  var pages = Math.ceil(total / PER_PAGE);
  var currentPage = 1;

  function showPage(page) {
    currentPage = page;
    page = Math.max(1, Math.min(page, pages));
    var first = (page - 1) * PER_PAGE;
    var last = Math.min(page * PER_PAGE, total);
    for (var i = 0; i < items.length; i++) {
      items[i].style.display = (i >= first && i < last) ? '' : 'none';
    }
    var btns = pagination.querySelectorAll('button');
    for (var j = 0; j < btns.length; j++) {
      var btn = btns[j];
      if (btn.dataset.page) btn.classList.toggle('active', parseInt(btn.dataset.page) === page);
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
  img.src = (window.location.pathname.includes('/posts/') ? '../' : '') + 'tux_pet.svg';
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
  var paused = true;

  function showQuote() {
    bubble.textContent = pickQuote();
    bubble.classList.add('visible');
    clearTimeout(hideTimer);
    tux.classList.add('tux-jump', 'tux-talking');
    hideTimer = setTimeout(function() {
      bubble.classList.remove('visible', 'tux-talking');
      tux.classList.remove('tux-jump');
    }, 5000);
  }

  function scheduleNext() {
    clearTimeout(autoTimer);
    if (paused) return;
    autoTimer = setTimeout(function() {
      showQuote();
      scheduleNext();
    }, 10000);
  }

  function togglePause() {
    paused = !paused;
    if (paused) {
      clearTimeout(autoTimer);
      clearTimeout(hideTimer);
      bubble.classList.remove('visible');
      tux.classList.remove('tux-jump', 'tux-talking');
    } else {
      showQuote();
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


  function showHint() {
    var lang = document.documentElement.lang;
    bubble.textContent = lang === 'en' ? 'Click me' : '点我';
    bubble.classList.add('visible');
  }
  showHint();
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

  var pageFull = document.querySelector('.page-full');
  if (!pageFull) return;
  pageFull.classList.add('has-toc');

  var sidebar = document.createElement('nav');
  sidebar.className = 'post-toc-sidebar';
  sidebar.setAttribute('aria-label', 'Table of contents');

  var title = document.createElement('h3');
  title.className = 'post-toc-title';
  title.textContent = 'Contents';
  sidebar.appendChild(title);

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
    });
    item.appendChild(link);
    list.appendChild(item);
  });

  sidebar.appendChild(list);
  pageFull.insertBefore(sidebar, pageFull.firstChild);

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

(function() {
  var btn = document.getElementById('searchToggle');
  if (!btn) return;

  var index = [
    { t: 'Flathub 是现代的 Linux 应用商店', u: 'posts/19887651.html', d: 'Flatpak 解决了依赖冲突和发行版碎片化的问题', m: '🐧 Arch Linux', b: '为什要使用 Flatpak 在 Linux 下装软件除了系统包管理器 apt pacman dnf 和 Snap 还有越来越流行的 Flatpak 它解决了依赖冲突和发行版碎片化的问题 优点 解释 跨发行版兼容 同一个 Flatpak 应用可以在不同的 Linux 发行版上运行 沙盒安全 应用运行在受限的环境中增强系统安全性 依赖隔离 应用自带所需依赖避免与系统库冲突 版' },
    { t: 'Archlinux下pacman的基本使用方法', u: 'posts/19887424.html', d: 'pacman 包管理器是 Arch Linux 的主要特色之一', m: '🐧 Arch Linux', b: 'Pacman 简介 以下是 Arch Wiki 的介绍 pacman 包管理器是 Arch Linux 的主要特色之一它将简单的二进制包格式与易于使用的 Arch 构建系统相结合pacman 的目标是能够轻松管理软件包无论是来自 官方仓库还是用户自己的构建 pacman 通过与主服务器同步软件包列表来保持系统更新这种服务器 客户端模型还允许用户通过一个简单的命令下载 安装软件包并包含' },
    { t: '使用 Waydroid 在 Archlinux 下无缝使用安卓软件', u: 'posts/19375968.html', d: 'Waydroid 只运行在 Wayland 中', m: '🐧 Arch Linux', b: '安装 Wadroid 桌面问题 Waydroid 只运行在 Wayland 中确保你在使用它 内核问题 Waydroid 需要 binder 模块一般默认就有如果是自己编译的内核请确保编译选项勾选该模块或使用 DKMS 安装 性能优化 推荐在 AMD CPU上安装 libndkIntel CPU上安装 libhoudini 安装 Waydroid yay S waydroid 其他发' },
    { t: 'Linux 下缺少打印机驱动的解决方法', u: 'posts/19125412.html', d: 'Linux 下缺少打印机驱动是常见问题', m: '💻 Linux', b: 'Linux 下缺少打印机驱动是常见问题Linux 在打印方面确实不如 windows 即插即用方便配置步骤还是颇为复杂的请各位耐心观看本文 安装 CPUS 不了解什么是cpus的可以看这里 https baike baidu com item cups 13007261 通用Unix打印系统 是Fe' },
    { t: '在 Archlinux 中添加 archlinuxcn 软件仓库', u: 'posts/19122518.html', d: 'ArchLinuxCN 是由 Arch Linux 中文社区维护的非官方用户存储库', m: '🐧 Arch Linux', b: 'Archlinuxcn简介 ArchLinuxCN 是由 Arch Linux 中文社区维护的非官方用户存储库它旨在为 Arch Linux 用户尤其是华语社区的用户提供对 Arch Linux 官方存储库中不可用的常用软件 工具 字体和自定义包的访问权限 它包括中国用户经常使用的软件和工具如字体和美化包 它由 Arch Linux 中文社区维护以满足官方存储库未涵盖的特定需求 更换国' },
    { t: 'Archlinux 更换镜像源', u: 'posts/19122512.html', d: '备份原来的 /etc/pacman.d/mirrorlist', m: '🐧 Arch Linux', b: '备份原来的 etc pacman d mirrorlist sudo mv etc pacman d mirrorlist etc pacman d mirrorlist bak 添加镜像源到 etc pacman d mirrorlist 自动换源 reflector 是一个 archlinux 官方提供的 python 脚本它可以从 archlinux 镜像状态页面检索最新的镜像列表' },
    { t: '在 Archlinux 中安装中文与日语输入法', u: 'posts/18881913.html', d: '安装及配置输入法框架', m: '🐧 Arch Linux', b: '安装及配置输入法框架 安装输入法框架 目前一共有两种选择Fcitx5和Ibus这里推荐使用更现代轻量Fcitx5 中文 Fcitx5 sudo pacman S fcitx5 fcitx5 chinese addons fcitx5 gtk fcitx5 qt fcitx5 configtool Ibus sudo pacman S ibus ibus rime 日语 ' },
    { t: '[Python] pygame 简单入门', u: 'posts/18697313.html', d: 'pygame 是用来写游戏的 python 模块集合', m: '🐍 Python', b: 'Pygame 的介绍 pygame 是用来写游戏的 python 模块集合使用 python 可以导入 pygame 来开发有意思的游戏pygame 小巧并且跨平台 安装 pygame 如果安装速度慢可以使用换源安装 pip install pygame 另一种方法 python m pip install user pygame 基本开发框架 import sys impo' },
    { t: '树莓派更新工具链', u: 'posts/18696663.html', d: '树莓派安装 neovim 0.10 遇到的 GLIBC 版本问题', m: '🥧 Raspberry Pi', b: '问题所在 今天本想在我的树梅派上安装个 neovim 0 10 版本结果通过运行后出现下面错误 nvim nvim lib aarch64 linux gnu libm so 6 version GLIBC 2 38 not found required by nvim nvim lib aarch64 linux gnu libc so 6 version GLIB' },
    { t: '解决Linux下 pip install 出现 externally-managed-environment问题', u: 'posts/18695807.html', d: 'python 外部环境管理错误解决方法', m: '💻 Linux', b: '问题所在 在 Archlinux Manjaro Ubuntu Fedora等最新的linux发行版中运行 pip install 时通常会收到一个错误提示 error externally managed environment 具体内容类似下面 sudo python m pip install user xyz error externally managed envir' },
    { t: 'Cargo 下载太慢？试试更换国内源', u: 'posts/18695607.html', d: 'Rust 官方默认的 Cargo 源服务器速度慢的解决方法', m: '💻 Linux', b: '问题所在 Rust 官方默认的 Cargo 源服务器和 crate 管理仓库为 crates io 并放置在 github 上 Cargo 的 注册表源 与 crates io 本身相同即 Cargo 也有一个在 github 存储库中提供的索引该存储库匹配 crates io index 的格式即github 仓库由该存储库的索引指示下载包的配置 但由于 Rust官方服务器部署在北美' },
    { t: '计算机组成原理学习笔记（未完成）', u: 'posts/18691470.html', d: '计算机组成原理 第三版 唐朔飞 学习笔记', m: '💻 Linux', b: '这篇blog用来记录我学习 计算机组成原理 第三版 唐朔飞 箸 这本书的笔记同时也希望能对阅读这片文章的你有所帮助 第一篇 概论 本篇主要介绍计算机系统的基本组成 应用与发展并通过对本书结构的介绍指出这本书的基本思路 第一章 计算机系统概论 1 1 计算机系统简介 1 1 1 计算机软硬件概念 计算机系统由 软件 和 硬件 两大部分组成 软件 计算机系统操作有关的计算机程序 规程 规' },
    { t: 'Git快速入门', u: 'posts/18646211.html', d: 'Git 版本控制工具的快速入门指南', m: '💻 Linux', b: '满汉全席之前 产看Git版本号 git v 绑定用户信息 绑定用户名 git config global user name 这里填你的名字 绑定用户邮箱 git config global user email 这里填你的邮箱 正式使用Git 创建一个本地的Git项目仓库 clone别人的仓库 git clone 项目地址 创建版本库 git init 项目所在目' },
    { t: '算法导论（原书第3版）', u: 'https://book.douban.com/subject/20432061/', d: 'Thomas H·Cormen · ⭐ 9.3', m: '📚 书籍' },
    { t: '深入理解计算机系统（第3版）', u: 'https://book.douban.com/subject/26912767/', d: 'Randal E. Bryant · ⭐ 9.8', m: '📚 书籍' },
    { t: 'C Primer Plus 中文版（第6版 2020版）', u: 'https://book.douban.com/subject/34987112/', d: 'Stephen Prata · ⭐ 9.6', m: '📚 书籍' },
    { t: 'C++ Primer Plus 中文版（第六版）', u: 'https://book.douban.com/subject/10789789/', d: 'Stephen Prata · ⭐ 8.5', m: '📚 书籍' },
    { t: '30天自制操作系统', u: 'https://book.douban.com/subject/11530329/', d: '川合秀实 · ⭐ 8.7', m: '📚 书籍' },
    { t: '鸟哥的Linux私房菜 基础学习篇 第四版', u: 'https://book.douban.com/subject/30359954/', d: '鸟哥 · ⭐ 9.1', m: '📚 书籍' },
    { t: '希腊古典神话', u: 'https://book.douban.com/subject/4872918', d: '古斯塔夫·施瓦布 · ⭐ 8.4', m: '📚 书籍' },
    { t: '只工作，不上班', u: 'https://book.douban.com/subject/34839849/', d: '林安 · ⭐ 7.6', m: '📚 书籍' }
  ];

  var overlay = document.createElement('div');
  overlay.className = 'search-overlay';
  overlay.innerHTML = '<div class="search-panel">'
    + '<div class="search-input-wrap">'
    + '<span class="search-icon">🔍</span>'
    + '<input type="text" id="searchInput" placeholder="' + (document.documentElement.lang === 'en' ? 'Search posts & books…' : '搜索博客或书籍…') + '" autocomplete="off">'
    + '<button class="search-close" id="searchClose">✕</button>'
    + '</div>'
    + '<div class="search-results" id="searchResults"></div>'
    + '</div>';
  document.body.appendChild(overlay);

  var input = document.getElementById('searchInput');
  var results = document.getElementById('searchResults');
  var closeBtn = document.getElementById('searchClose');
  var selIdx = -1;
  var curResults = [];

  function search(query) {
    var q = query.toLowerCase().trim();
    selIdx = -1;
    if (!q) { results.innerHTML = ''; curResults = []; return; }
    curResults = [];
    for (var i = 0; i < index.length; i++) {
      var item = index[i];
      if (item.t.toLowerCase().indexOf(q) !== -1
        || (item.d && item.d.toLowerCase().indexOf(q) !== -1)
        || (item.m && item.m.toLowerCase().indexOf(q) !== -1)
        || (item.b && item.b.toLowerCase().indexOf(q) !== -1)) {
        curResults.push(item);
      }
    }
    if (!curResults.length) {
      results.innerHTML = '<div class="search-empty">' + (document.documentElement.lang === 'en' ? 'No results found' : '未找到相关内容') + '</div>';
      return;
    }
    function snippet(text, query) {
      var lower = text.toLowerCase();
      var idx = lower.indexOf(query);
      if (idx === -1) return '';
      var start = Math.max(0, idx - 30);
      var end = Math.min(text.length, idx + query.length + 60);
      var s = text.slice(start, end).replace(/\s+/g, ' ');
      if (start > 0) s = '…' + s;
      if (end < text.length) s = s + '…';
      var qIdx = s.toLowerCase().indexOf(query);
      if (qIdx !== -1) {
        s = s.slice(0, qIdx) + '<mark>' + s.slice(qIdx, qIdx + query.length) + '</mark>' + s.slice(qIdx + query.length);
      }
      return s;
    }

    var html = '';
    for (var j = 0; j < curResults.length; j++) {
      var r = curResults[j];
      var isBook = r.u.indexOf('book.douban.com') !== -1;
      var desc = r.d || '';
      if (r.b && r.b.toLowerCase().indexOf(q) !== -1) {
        desc = snippet(r.b, q);
      }
      html += '<a class="search-result-item" href="' + (isBook ? r.u : r.u) + '"'
        + (isBook ? ' target="_blank"' : '') + ' data-idx="' + j + '">'
        + '<div class="result-title">' + r.t + '</div>'
        + '<div class="result-desc">' + desc + '</div>'
        + '<div class="result-meta">' + (r.m || '') + '</div>'
        + '</a>';
    }
    results.innerHTML = html;
  }

  function updateHighlight() {
    var items = results.querySelectorAll('.search-result-item');
    for (var i = 0; i < items.length; i++) {
      items[i].classList.toggle('highlighted', i === selIdx);
    }
    if (selIdx >= 0 && items[selIdx]) {
      items[selIdx].scrollIntoView({ block: 'nearest' });
    }
  }

  function navigate(delta) {
    var items = results.querySelectorAll('.search-result-item');
    if (!items.length) return;
    selIdx = Math.max(0, Math.min(items.length - 1, selIdx + delta));
    updateHighlight();
  }

  function go() {
    var items = results.querySelectorAll('.search-result-item');
    if (selIdx >= 0 && items[selIdx]) {
      window.location.href = items[selIdx].href;
      close();
    }
  }

  function open() {
    overlay.classList.add('open');
    setTimeout(function() { input.focus(); }, 100);
  }

  function close() {
    overlay.classList.remove('open');
    input.blur();
  }

  btn.addEventListener('click', open);
  closeBtn.addEventListener('click', close);
  overlay.addEventListener('click', function(e) {
    if (e.target === overlay) close();
  });

  input.addEventListener('input', function() {
    search(this.value);
  });

  input.addEventListener('keydown', function(e) {
    if (e.key === 'ArrowDown') { e.preventDefault(); navigate(1); }
    else if (e.key === 'ArrowUp') { e.preventDefault(); navigate(-1); }
    else if (e.key === 'Enter') { e.preventDefault(); go(); }
    else if (e.key === 'Escape') { close(); }
  });

  document.addEventListener('keydown', function(e) {
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
      e.preventDefault();
      if (overlay.classList.contains('open')) close();
      else open();
    }
  });
})();

// ── Category fold ──
(function() {
  document.addEventListener('click', function(e) {
    var header = e.target.closest('.category-header');
    if (!header) return;
    var list = header.nextElementSibling;
    if (!list || !list.classList.contains('category-list')) return;
    header.classList.toggle('collapsed');
    list.classList.toggle('hidden');
  });
})();

