<p>在 Arch Linux 的高 DPI 屏幕上，部分软件字体过小，根源在于这些软件仍遵循过时的 96 DPI 标准-19，而现代高分辨率屏幕的 DPI 远高于此。只要调整软件的缩放即可解决问题</p>
<h2 id="qt-应用">Qt 应用</h2>
<p>对于类似 wechat-bin 的 qt 应用<br>
编辑 .desktop 文件即可</p>
<p><strong>下面是微信的例子</strong></p>
<pre><code class="language-bash">sudo vim /usr/share/applications/wechat.desktop
</code></pre>
<p>打开后你应该看到这样：</p>
<pre><code>[Desktop Entry]
Name=wechat
Name[zh_CN]=微信
Exec=/opt/wechat/wechat %U
StartupNotify=true
Terminal=false
Icon=/usr/share/icons/hicolor/256x256/apps/wechat.png
Type=Application
Categories=Utility;
Comment=Wechat Desktop
Comment[zh_CN]=微信桌面版
</code></pre>
<p>把<code>Exec=</code>这一行行改为 <code>Exec=env QT_SCALE_FACTOR=2 /opt/wechat/wechat %U</code> 即可</p>
<h2 id="electron-应用">Electron 应用</h2>
<p>对于类似 linux-qq, wemeet-bin 的 electron 应用<br>
同样编辑 .desktop 文件即可</p>
<p><strong>下面是QQ的例子</strong></p>
<pre><code class="language-bash">sudo vim /usr/share/applications/qq.desktop
</code></pre>
<p>打开后你应该看到这样：</p>
<pre><code>[Desktop Entry]
Name=QQ
Exec=linuxqq %U
Terminal=false
Type=Application
Icon=qq
StartupWMClass=QQ
Categories=Network;
Comment=QQ
</code></pre>
<p>把<code>Exec=</code>这一行行改为 <code>Exec=linuxqq %U --force-device-scale-factor=2</code>即可</p>
<h2 id="-wine-应用">🍷 Wine 应用</h2>
<p>对于 Wine 程序，可以调整其内部的 DPI 设置</p>
<ul>
<li>打开 Wine 配置：在终端中运行 winecfg</li>
<li>调整 DPI：在“显示” (Graphics) 选项卡中，找到“DPI”设置</li>
<li>设置合适的值：将 DPI 设置为与你的缩放匹配的值。缩放为 2.0，此处应设为 192</li>
</ul>