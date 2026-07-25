(function() {
  var toggle = document.getElementById('langToggle');
  if (!toggle) return;
  var STORAGE_KEY = 'lang';

  var i18n = {
    'nav-home': { zh: '首页', en: 'Home' },
    'nav-archive': { zh: '归档', en: 'Archive' },
    'nav-categories': { zh: '分类', en: 'Categories' },
    'nav-about': { zh: '关于', en: 'About' },
    'sidebar-stats': { zh: '统计数据', en: 'Stats' },
    'stat-posts': { zh: '随笔', en: 'Posts' },
    'stat-likes': { zh: '推荐', en: 'Likes' },
    'stat-reads': { zh: '阅读', en: 'Reads' },
    'stat-comments': { zh: '评论', en: 'Comments' },
    'sidebar-categories': { zh: '分类', en: 'Categories' },
    'next-page': { zh: '下一页 →', en: 'Next →' },
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
    'about-site': { zh: '关于本站', en: 'About This Site' },
    'site-desc': { zh: '本站是使用纯 HTML + CSS 构建的静态博客，托管于 GitHub Pages。主题配色使用 Catppuccin 风格，支持明暗主题和中英文切换。', en: 'A static blog built with plain HTML + CSS, hosted on GitHub Pages. Catppuccin color scheme with dark/light mode and Chinese/English language toggle.' }
  };

  function getPreferredLang() {
    var saved = localStorage.getItem(STORAGE_KEY);
    if (saved === 'zh' || saved === 'en') return saved;
    return 'zh';
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
    localStorage.setItem(STORAGE_KEY, lang);
  }

  applyLanguage(getPreferredLang());

  toggle.addEventListener('click', function() {
    var current = document.documentElement.lang || 'zh';
    applyLanguage(current === 'zh' ? 'en' : 'zh');
  });
})();
