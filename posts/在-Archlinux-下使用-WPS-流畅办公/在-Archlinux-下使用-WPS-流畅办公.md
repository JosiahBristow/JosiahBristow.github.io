<h2 id="linux-版-wps-简介">Linux 版 WPS 简介</h2>
<p>下面是 Arch Wiki 的描述</p>
<blockquote>
<p>WPS Office for Linux 是金山公司推出的、运行于 Linux 平台上的全功能办公软件。与 Microsoft Office 高度兼容，且更加尊重 Linux 用户特定的使用习惯，并自带方正字体集。</p>
</blockquote>
<h2 id="安装-wps">安装 WPS</h2>
<p>WPS Office for Linux 根据不同的需求被打包成了：</p>
<table>
<thead>
<tr>
<th style="text-align: center">软件包名称</th>
<th style="text-align: center">说明</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: center">wps-office-cn</td>
<td style="text-align: center">WPS</td>
</tr>
<tr>
<td style="text-align: center">wps-office</td>
<td style="text-align: center">WPS 国际版</td>
</tr>
<tr>
<td style="text-align: center">wps-office-365</td>
<td style="text-align: center">WPS 365</td>
</tr>
<tr>
<td style="text-align: center">wps-office-365-edu</td>
<td style="text-align: center">WPS 365 教育版</td>
</tr>
</tbody>
</table>
<p>国内用户推荐安装 <code>wps-office-cn</code>。</p>
<pre><code class="language-bash"># 安装 wps 和
yay -S wps-office-cn
</code></pre>
<h2 id="设置中文">设置中文</h2>
<p>因为 wps 默认是英文且不自带中文语言包，还需要安装中文语言包 <code>wps-office-mui-zh-cn</code>。</p>
<pre><code class="language-bash"># 安装中文语言包
yay -S wps-office-mui-zh-cn
</code></pre>
<p>安装好语言包后，使用编辑器打开 <code>$XDG_CONFIG_HOME/Kingsoft/Office.conf</code> (如果系统没有定义$XDG_CONFIG_HOME， 改成 <code>~/Kingsoft/Office.conf</code> 就行) 文件添加以下内容，重启后即可显示中文：</p>
<pre><code>[General]
languages=zh_CN
</code></pre>
<h2 id="fcitx5-输入法配置">Fcitx5 输入法配置</h2>
<p>如果你在 wps 中无法使用 Fcitx5 输入法，可以试试下面的方案</p>
<pre><code class="language-bash"># 编辑 wps 的启动脚本
sudo vim /usr/bin/wps
</code></pre>
<p>把下面内容添加到 <code>gOpt=</code> 下面</p>
<pre><code>export GTK_IM_MODULE=fcitx
export QT_IM_MODULE=fcitx5
export XMODIFIERS=@im=fcitx
</code></pre>
<p><img src="images/3586302-20260730185224800-917437888.png" alt="image"  loading="lazy"></p>
<h2 id="解决字体缺失问题">解决字体缺失问题</h2>
<p><img src="images/3586302-20260730180905785-129642148.png" alt="Screenshot from 2026-07-30 18-07-10"  loading="lazy"></p>
<p>可安装 WPS 字体如：<code>ttf-wps-fonts</code> 或 <code>ttf-wps-win10</code> 或 <code>wps-office-fonts</code> 或 <code>wps-office-365-edu-fonts</code>（针对wps-office-365-eduAUR）解决。</p>
<pre><code class="language-bash"># 推荐安装 `ttf-wps-fonts`
yay -S ttf-wps-fonts
</code></pre>