<h2 id="问题所在">问题所在</h2>
<p>在 Archlinux、Manjaro、Ubuntu、Fedora等最新的linux发行版中运行 <code>pip install</code> 时，通常会收到一个错误提示：error: externally-managed-environment。<br>
具体内容类似下面：</p>
<pre><code class="language-bash">❯ sudo python -m pip install --user xyz
error: externally-managed-environment

× This environment is externally managed
╰─&gt; To install Python packages system-wide, try apt install
    python3-xyz, where xyz is the package you are trying to
    install.
    
    If you wish to install a non-Debian-packaged Python package,
    create a virtual environment using python3 -m venv path/to/venv.
    Then use path/to/venv/bin/python and path/to/venv/bin/pip. Make
    sure you have python3-full installed.
    
    For more information visit http://rptl.io/venv

note: If you believe this is a mistake, please contact your Python installation or OS distribution provider. You can override this, at the risk of breaking your Python installation or OS, by passing --break-system-packages.
hint: See PEP 668 for the detailed specification.
</code></pre>
<h2 id="问题背后的原因">问题背后的原因</h2>
<p>“externally-managed-environment”错误背后的原因：Manjaro、Ubuntu、Fedora 以及其他的最新发行版中，正在使用 Python 包来实现此增强功能。<br>
这个更新是为了避免「操作系统包管理器 (如pacman、yum、apt) 和 pip 等特定于 Python 的包管理工具之间的冲突」。<br>
这些冲突包括 Python 级 API 不兼容和文件所有权冲突。</p>
<h2 id="解决方案">解决方案</h2>
<h3 id="安全的解决方案推荐">安全的解决方案（推荐）</h3>
<h4 id="方案1-使用系统包管理器">方案1: 使用系统包管理器</h4>
<pre><code class="language-bash"># debian 系的系统
sudo apt install [替换为你要安装的包的名字]
# archlinux 系的系统
sudo pacman -S [替换为你要安装的包的名字]
</code></pre>
<h4 id="方案2-创建虚拟环境">方案2: 创建虚拟环境</h4>
<p>要是坚持想使用 pip 可以试试这个方案。<br>
原理：创建一个隔离的环境来管理 Python 包而不影响系统。</p>
<pre><code class="language-bash"># debian 系的系统
sudo apt install python3-venv # 安装 venv
python3 -m venv myenv # 创建虚拟环境
source myenv/bin/activate # 激活虚拟环境
pip install some-package # 在虚拟环境下安装所需要的包

# archlinux 系的系统
python3 -m venv myenv # 创建虚拟环境
source myenv/bin/activate # 激活虚拟环境
pip install some-package # 在虚拟环境下安装所需要的包
</code></pre>
<h3 id="冒险但简单的解决方案">冒险但简单的解决方案</h3>
<h4 id="方案3--跳过系统限制">方案3:  跳过系统限制</h4>
<pre><code class="language-bash">pip install [替换为你要安装的包的名字] --break-system-packages
</code></pre>
<h4 id="方案4-移除-usrlibpython311externally-managed-">方案4: 移除 <code>/usr/lib/python3.11/EXTERNALLY-MANAGED </code></h4>
<p>要是想一劳永逸，就直接执行下面命令去掉提示：</p>
<pre><code class="language-bash">sudo mv /usr/lib/python3.11/EXTERNALLY-MANAGED /usr/lib/python3.11/EXTERNALLY-MANAGED.bak
</code></pre>
<p>再次使用 pip 安装你要的包，不出意外应该就可以顺利执行了。</p>