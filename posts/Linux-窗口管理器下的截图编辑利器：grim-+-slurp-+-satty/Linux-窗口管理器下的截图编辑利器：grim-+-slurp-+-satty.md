<p>在 Wayland 环境下，传统的 X11 截图工具 Flameshot 常常面临兼容性问题。而 <code>grim</code>、<code>slurp</code> 和 <code>satty</code> 三者都是为 Wayland 原生设计的工具，组合起来能够提供流畅的截图与标注体验。</p>
<ul>
<li><strong>slurp</strong>：交互式选择屏幕区域，输出区域坐标</li>
<li><strong>grim</strong>：Wayland 原生截图工具，从合成器中抓取图像</li>
<li><strong>satty</strong>：现代化截图标注工具，灵感来自 Swappy 和 Flameshot</li>
</ul>
<h2 id="解决方案">解决方案</h2>
<p>直接把下面命令配置为你的 wm 的截图方式</p>
<pre><code class="language-bash">grim -t ppm -g "$(slurp -d)" - | satty -f - --initial-tool=arrow --copy-command=wl-copy --actions-on-escape="save-to-clipboard,exit" --brush-smooth-history-size=5 --disable-notifications
</code></pre>
<p>三个工具各司其职，通过管道（pipe）串联成一个完整的截图编辑流程</p>
<h2 id="安装">安装</h2>
<h3 id="arch-linux">Arch Linux</h3>
<pre><code class="language-bash">sudo pacman -S grim slurp satty
</code></pre>
<h3 id="debianubuntu">Debian/Ubuntu</h3>
<pre><code class="language-bash">sudo apt install grim slurp
# satty 可能需要从源码或第三方仓库安装
</code></pre>
<h3 id="fedora">Fedora</h3>
<pre><code class="language-bash">sudo dnf install grim slurp

# satty 官方仓库没有，需要通过第三方仓库 COPRE 安装：
sudo dnf copr enable mineiro/satty
sudo dnf install satty
</code></pre>
<h2 id="主流-wm-的配置方法">主流 WM 的配置方法</h2>
<p>在 Hyprland 中绑定快捷键：</p>
<pre><code class="language-lua">bind = , XF86SELECTIVESCREENSHOT, exec, grim -t ppm -g "$(slurp -d)" - | satty -f - --initial-tool=arrow --copy-command=wl-copy --actions-on-escape="save-to-clipboard,exit" --brush-smooth-history-size=5 --disable-notifications
</code></pre>
<p>在 niri 中绑定快捷键：</p>
<pre><code>Mod+Shift+S { spawn-sh "grim -t ppm -g "$(slurp -d)" - | satty -f - --initial-tool=arrow --copy-command=wl-copy --actions-on-escape="save-to-clipboard,exit" --brush-smooth-history-size=5 --disable-notifications"}
</code></pre>
<h1 id="faq-常见问题与回答">FAQ 常见问题与回答</h1>
<h3 id="satty-无法启动或显示异常">satty 无法启动或显示异常</h3>
<p>检查是否安装了 Wayland 相关的依赖库。satty 需要 Wayland 环境支持。</p>
<h3 id="剪贴板不工作">剪贴板不工作</h3>
<p>确保安装了 <code>wl-clipboard</code>（提供 <code>wl-copy</code> 和 <code>wl-paste</code> 命令）。</p>