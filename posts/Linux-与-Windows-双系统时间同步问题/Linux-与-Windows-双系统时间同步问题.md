<h2 id="问题根因">问题根因</h2>
<p>因为 Windows 和 Linux 对系统时间的处理方式不同</p>
<ul>
<li>Linux 将硬件时钟（BIOS/UEFI时钟）设置为 UTC（格林尼治标准时间），再根据时区换算显示</li>
<li>Windows 将硬件时钟设置为本地时间</li>
</ul>
<p>所以一换系统，Windows 一看主板时间“哦现在是 UTC 下午 2 点”，心想那就是我本地下午 2 点——结果你明明在东八区，直接给你倒退回早上 6 点，完美错开 8 小时。</p>
<h2 id="解决方法">解决方法</h2>
<h3 id="方案一将windows配置为使用utc时间推荐">方案一：将Windows配置为使用UTC时间（推荐）</h3>
<p>让 Windows 也学会把主板时间当 UTC 看。</p>
<ol>
<li>Win + R，输入 regedit 打开注册表</li>
<li>地址栏粘贴这串路径<code>HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\TimeZoneInformation</code></li>
<li>右边空白处右键 → 新建 → DWORD（32位）值，命名为 RealTimeIsUniversal</li>
<li>双击它，数值数据改成 1，确定</li>
<li>重启，完事</li>
</ol>
<h3 id="方案二将linux配置为使用本地时间">方案二：将Linux配置为使用本地时间</h3>
<ol>
<li>打开Ubuntu终端。</li>
<li>运行以下命令将硬件时钟设置为本地时间：<pre><code class="language-bash">timedatectl set-local-rtc 1 --adjust-system-clock
</code></pre>
</li>
<li>通过运行以下命令来验证更改：<pre><code class="language-bash">timedatectl
</code></pre>
你应该会看到类似 <code>RTC in local TZ: yes</code> 的输出。</li>
</ol>
<p><strong>额外提醒</strong>⚠️ Windows 的“快速启动”有时会捣乱，建议去电源设置里把它关掉，省得时间又抽风</p>