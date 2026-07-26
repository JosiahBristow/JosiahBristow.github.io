(function() {
  var toggle = document.getElementById('langToggle');
  if (!toggle) return;

  var i18n = {
    'nav-home': { zh: '首页', en: 'Home' },
    'nav-archive': { zh: '归档', en: 'Archive' },
    'nav-categories': { zh: '分类', en: 'Categories' },
    'nav-about': { zh: '关于', en: 'About' },
    'nav-bookshelf': { zh: '书架', en: 'Bookshelf' },
    'nav-gallery': { zh: '相册', en: 'Gallery' },
    'nav-friends': { zh: '友链', en: 'Friends' },
    'sidebar-stats': { zh: '统计数据', en: 'Stats' },
    'stat-posts': { zh: '随笔', en: 'Posts' },
    'stat-likes': { zh: '推荐', en: 'Likes' },
    'stat-reads': { zh: '阅读', en: 'Reads' },
    'stat-comments': { zh: '评论', en: 'Comments' },
    'sidebar-categories': { zh: '分类', en: 'Categories' },
    'archive-title': { zh: '归档', en: 'Archive' },
    'archive-count': { zh: '共 10 篇随笔', en: '10 posts total' },
    'categories-title': { zh: '分类', en: 'Categories' },
    'categories-count': { zh: '共 4 个分类', en: '4 categories total' },
    'about-title': { zh: '关于', en: 'About' },
    'about-me': { zh: '关于我', en: 'About Me' },
    'bio-1': { zh: '一名 Linux 爱好者，Arch Linux 用户。喜欢折腾各种开源软件，探索不同的技术可能性。从系统配置到软件开发，从内核问题到桌面美化，享受解决问题的过程。', en: 'A Linux enthusiast and Arch Linux user. I enjoy tinkering with open-source software and exploring different technical possibilities — from system config to software dev, kernel issues to desktop customization.' },
    'bio-2': { zh: '这个博客主要记录我在 Linux 使用过程中遇到的问题和解决方案，希望能帮助到遇到同样问题的朋友。', en: 'This blog documents issues I encounter while using Linux and their solutions, hoping to help others facing the same problems.' },
    'about-interests': { zh: '兴趣领域', en: 'Interests' },
    'interest-1': { zh: 'Arch Linux 系统管理与优化', en: 'Arch Linux system administration & optimization' },
    'interest-2': { zh: 'Linux 桌面环境与 Wayland', en: 'Linux desktop environments & Wayland' },
    'interest-3': { zh: 'Python / Shell 脚本开发', en: 'Python / Shell scripting' },
    'interest-4': { zh: '树莓派与嵌入式系统', en: 'Raspberry Pi & embedded systems' },
    'interest-5': { zh: '开源软件与社区', en: 'Open-source software & community' },
    'comments-title': { zh: '评论', en: 'Comments' },
    'about-site': { zh: '关于本站', en: 'About This Site' },
    'site-desc': { zh: '本站是使用纯 HTML + CSS 构建的静态博客，托管于 GitHub Pages。主题配色使用 Catppuccin 风格，支持明暗主题和中英文切换。', en: 'A static blog built with plain HTML + CSS, hosted on GitHub Pages. Catppuccin color scheme with dark/light mode and Chinese/English language toggle.' },
    'bookshelf-title': { zh: '书架', en: 'Bookshelf' },
    'bookshelf-desc': { zh: '读过和正在读的书', en: 'Books I have read or am reading' },
    'bookshelf-placeholder': { zh: '这里将展示你读过的书', en: 'Your books will appear here' },
    'bookshelf-reading': { zh: '阅读中', en: 'Reading' },
    'gallery-title': { zh: '相册', en: 'Gallery' },
    'gallery-desc': { zh: '一些照片和截图', en: 'Photos and screenshots' },
    'gallery-placeholder': { zh: '照片展示区域', en: 'Photos will appear here' },
    'friends-title': { zh: '友链', en: 'Friends' },
    'friends-desc': { zh: '朋友们的小站', en: 'My friends\' sites' },
    'friends-placeholder-name': { zh: '待添加', en: 'Pending' },
    'friends-placeholder-desc': { zh: '这里将展示你的朋友们', en: 'Your friends will appear here' },
    'stat-books': { zh: '书籍', en: 'Books' },
    'stat-reading': { zh: '在读', en: 'Reading' },
    'stat-photos': { zh: '照片', en: 'Photos' },
    'stat-albums': { zh: '相册', en: 'Albums' },
    'stat-friends': { zh: '友链', en: 'Friends' },
    'search-placeholder': { zh: '搜索博客或书籍…', en: 'Search posts & books…' },
    'search-empty': { zh: '未找到相关内容', en: 'No results found' },
    'tux-hint': { zh: '点我', en: 'Click me' }
  };

  function getLangFromURL() {
    var m = location.search.match(/[?&]lang=(zh|en)(?:&|$)/);
    return m ? m[1] : null;
  }

  function applyLanguage(lang) {
    document.documentElement.lang = lang;
    toggle.textContent = lang === 'zh' ? 'EN' : '中';
    var els = document.querySelectorAll('[data-i18n]');
    for (var i = 0; i < els.length; i++) {
      var el = els[i];
      var key = el.getAttribute('data-i18n');
      if (i18n[key] && i18n[key][lang]) {
        el.textContent = i18n[key][lang];
      }
    }
    var links = document.querySelectorAll('.nav-inner a, .header-title a');
    for (var i = 0; i < links.length; i++) {
      var href = links[i].getAttribute('href');
      if (!href || href.indexOf('://') !== -1 || href.indexOf('//') === 0) continue;
      href = href.replace(/[?&]lang=(zh|en)/g, '');
      href += (href.indexOf('?') === -1 ? '?' : '&') + 'lang=' + lang;
      links[i].setAttribute('href', href);
    }
    var searchInput = document.getElementById('searchInput');
    if (searchInput && i18n['search-placeholder']) {
      searchInput.placeholder = i18n['search-placeholder'][lang];
    }
    var searchEmpty = document.getElementById('searchResults');
    if (searchEmpty && searchEmpty.querySelector('.search-empty')) {
      searchEmpty.querySelector('.search-empty').textContent = i18n['search-empty'][lang];
    }
    var tuxBubble = document.querySelector('.tux-speech');
    if (tuxBubble) {
      var hintZh = i18n['tux-hint'].zh;
      var hintEn = i18n['tux-hint'].en;
      if (tuxBubble.textContent === hintZh || tuxBubble.textContent === 'Click me' || tuxBubble.textContent === hintEn || tuxBubble.textContent === '点我') {
        tuxBubble.textContent = i18n['tux-hint'][lang];
      }
    }
  }

  function loadLang() {
    var urlLang = getLangFromURL();
    if (urlLang) return urlLang;
    try {
      var saved = localStorage.getItem('lang');
      if (saved === 'zh' || saved === 'en') return saved;
    } catch (e) {}
    var wm = window.name.match(/^lang=(zh|en)$/);
    if (wm) return wm[1];
    return 'zh';
  }

  var currentLang = loadLang();
  applyLanguage(currentLang);

  function setGiscusLang(lang) {
    var iframe = document.querySelector('iframe.giscus-frame');
    if (iframe) {
      iframe.contentWindow.postMessage({
        giscus: { setConfig: { lang: lang === 'zh' ? 'zh-CN' : 'en' } }
      }, 'https://giscus.app');
    }
  }

  toggle.addEventListener('click', function() {
    currentLang = currentLang === 'zh' ? 'en' : 'zh';
    try { localStorage.setItem('lang', currentLang); } catch (e) {}
    window.name = 'lang=' + currentLang;
    history.replaceState(null, '', '?lang=' + currentLang);
    applyLanguage(currentLang);
    setGiscusLang(currentLang);
  });
})();
