<h2 id="cargo-下载缓慢的原因">cargo 下载缓慢的原因</h2>
<p>Rust 官方默认的 Cargo 源服务器和 crate 管理仓库为 crates.io，并放置在 github 上。<br>
Cargo 的“注册表源”与 crates.io 本身相同，即 Cargo 也有一个在 github 存储库中提供的索引。该存储库匹配 crates.io index 的格式，即<a href="https://github.com/rust-lang/crates.io-index" target="_blank" rel="noopener nofollow">github 仓库</a>，由该存储库的索引指示下载包的配置。<br>
但由于 Rust官方服务器部署在北美洲，所以国内用户下载速度很慢，所以为 Cargo 切换国内镜像源，可以显著提升依赖包的下载速度，解决网络延迟或连接失败的问题。</p>
<h2 id="切换镜像源">切换镜像源</h2>
<h3 id="好用的国内镜像源">好用的国内镜像源</h3>
<p>以下是几个主流且稳定的国内镜像源，选择一个使用即可。</p>
<ol>
<li><strong>清华大学镜像源 (Tuna)</strong></li>
</ol>
<blockquote>
<p>tuna 源的配置使用了“稀疏索引”（<code>sparse+</code>），如果你的 Cargo 版本 <strong>≥ 1.68</strong>，这个配置能获得更快的索引更新速度。（Cargo 版本 <strong>&lt; 1.68</strong> 删去下面配置的<code>sparse+</code>就行）</p>
</blockquote>
<pre><code class="language-toml">[source.crates-io]
replace-with = 'mirror'

[source.mirror]
registry = "sparse+https://mirrors.tuna.tsinghua.edu.cn/crates.io-index/"
</code></pre>
<ol start="2">
<li><strong>中国科学技术大学镜像源 (USTC)</strong></li>
</ol>
<pre><code class="language-toml">[source.crates-io]
replace-with = 'ustc'

[source.ustc]
registry = "https://mirrors.ustc.edu.cn/crates.io-index"
</code></pre>
<ol start="3">
<li><strong>上海交通大学镜像源 (SJTU)</strong></li>
</ol>
<pre><code class="language-toml">[source.crates-io]
replace-with = 'sjtu'

[source.sjtu]
registry = "https://mirrors.sjtug.sjtu.edu.cn/crates.io-index"
</code></pre>
<ol start="4">
<li><strong>Rustcc 镜像源</strong></li>
</ol>
<pre><code class="language-toml">[source.crates-io]
replace-with = 'rustcc'

[source.rustcc]
registry = "https://code.aliyun.com/rustcc/crates.io-index.git"
</code></pre>
<h3 id="修改-cargo-配置文件">修改 Cargo 配置文件</h3>
<h4 id="两种方式">两种方式</h4>
<ul>
<li>
<ol>
<li>全局：可以通过 $HOME/.cargo/config.toml 配置文件</li>
</ol>
</li>
<li>
<ol start="2">
<li>单个项目：或者在项目工程结构中，与 Cargo.toml 同级目录的 .cargo 文件夹下创建 config.toml 文件。</li>
</ol>
</li>
</ul>
<h4 id="修改-cargo-配置文件-1">修改 Cargo 配置文件</h4>
<p>Cargo 的配置文件为 <code>config.toml</code>，通常位于用户目录下的 <code>.cargo</code> 文件夹内。</p>
<ol>
<li>
<p><strong>创建或编辑配置文件</strong></p>
<ul>
<li><strong>Linux/macOS</strong>: <code>~/.cargo/config.toml</code></li>
<li><strong>Windows</strong>: <code>%USERPROFILE%\.cargo\config.toml</code><br>
PS：如果文件或目录不存在，可以手动创建。</li>
</ul>
</li>
<li>
<p><strong>写入镜像配置</strong><br>
将上方任一镜像源的配置内容写入到到 <code>config.toml</code> 文件中。<br>
如果你懒得写，你可以直接复制笔者我的配置文件（推荐使用清华源），如下：</p>
</li>
</ol>
<pre><code class="language-toml">[source.crates-io]
registry = "https://github.com/rust-lang/crates.io-index"

# 指定镜像
replace-with = 'tuna' # 如：tuna、sjtu、ustc，或者 rustcc
 
# 中国科学技术大学
[source.ustc]
# registry = "https://mirrors.ustc.edu.cn/crates.io-index"
registry = "sparse+https://mirrors.ustc.edu.cn/crates.io-index"

# 清华大学
[source.tuna]
registry = "https://mirrors.tuna.tsinghua.edu.cn/git/crates.io-index.git"

# 上海交通大学
[source.sjtu]
registry = "https://mirrors.sjtug.sjtu.edu.cn/crates.io-index"

# Ruxtcc 社区
[source.rustcc]
registry = "https://code.aliyun.com/rustcc/crates.io-index.git"

</code></pre>
<h2 id="验证与故障排查">验证与故障排查</h2>
<ul>
<li><strong>清理并重建</strong>：配置完成后，建议先清理项目缓存，再重新构建，以测试新源是否生效。<pre><code class="language-bash">cargo clean
cargo build
</code></pre>
</li>
<li><strong>检查 Cargo 版本</strong>：确保你的 Cargo 版本足够新，以支持稀疏索引等新特性。<pre><code class="language-bash">cargo --version
</code></pre>
</li>
<li><strong>解决 <code>git-fetch-with-cli</code> 问题</strong>：如果遇到 Git 相关的网络问题，可以在配置文件中添加如下内容：<pre><code class="language-toml">[net]
git-fetch-with-cli = true
</code></pre>
</li>
</ul>
<h2 id="进阶工具crm-cargo-registry-manager">进阶工具：<code>crm</code> (Cargo Registry Manager)</h2>
<p><code>crm</code> 是一个用 Rust 编写的命令行工具，可以帮你快速列出、添加和切换不同的 Cargo 镜像源。</p>
<ul>
<li><strong>安装</strong>：<code>cargo install crm</code></li>
<li><strong>使用</strong>：安装后，可以通过 <code>crm</code> 命令查看帮助。例如，<code>crm tuna</code> 可以一键切换到清华镜像源。</li>
</ul>
<h2 id="补充配置-rustup-镜像可选">补充：配置 <code>rustup</code> 镜像（可选）</h2>
<p>除了 Cargo 依赖包，<code>rustup</code> 工具链本身的下载和更新也可以通过镜像加速。建议在 shell 配置文件（如 <code>~/.bashrc</code> 或 <code>~/.zshrc</code>）中添加以下环境变量：</p>
<pre><code class="language-bash">export RUSTUP_DIST_SERVER=https://mirrors.tuna.tsinghua.edu.cn/rustup
export RUSTUP_UPDATE_ROOT=https://mirrors.tuna.tsinghua.edu.cn/rustup/rustup
</code></pre>