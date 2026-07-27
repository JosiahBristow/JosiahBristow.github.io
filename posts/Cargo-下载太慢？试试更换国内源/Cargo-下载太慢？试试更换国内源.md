<h2 id="问题所在">问题所在</h2>
<p>Rust 官方默认的 Cargo 源服务器和 crate 管理仓库为 crates.io，并放置在 github 上。<br>
Cargo 的“注册表源”与 crates.io 本身相同，即 Cargo 也有一个在 github 存储库中提供的索引。该存储库匹配 crates.io index 的格式，即<a href="https://github.com/rust-lang/crates.io-index" target="_blank" rel="noopener nofollow">github 仓库</a>，由该存储库的索引指示下载包的配置。<br>
但由于 Rust官方服务器部署在北美洲，所以国内用户下载速度很慢。</p>
<h2 id="解决方案">解决方案</h2>
<p>因为 Cargo 支持用另一个来源更换一个来源的能力，可根据镜像或 vendoring 依赖关系来表达倾向。所以我们可以使用国内镜像源来提高下载速度。</p>
<ul>
<li>可以通过 $HOME/.cargo/config 配置文件</li>
<li>或者在项目工程结构中，与 Cargo.toml 同级目录的 .cargo 文件夹下创建 config 文件。</li>
</ul>
<p>config 文件格式如下:</p>
<pre><code class="language-toml"># `source` 表下，就是存储有关要更换的来源名称
[source]

# 在`source` 表格之下的，可为一定数量的有关来源名称. 示例下面就# 定义了一个新源， 叫 `my-awesome-source`， 其内容来自本地 # `vendor`目录 ，其相对于包含`.cargo/config`文件的目录
[source.my-awesome-source]
directory = "vendor"

# Git sources 也指定一个 branch/tag/rev
git = "https://example.com/path/to/repo"
# branch = "master"
# tag = "v1.0.1"
# rev = "313f44e8"

# The crates.io 默认源 在"crates-io"名称下， 且在这里我们使用 `replace-with` 字段指明 默认源更换成"my-awesome-source"源
[source.crates-io]
replace-with = "my-awesome-source"

</code></pre>
<h2 id="笔者的配置文件">笔者的配置文件</h2>
<p>如果你懒得写，你可以直接复制笔者我的配置文件（推荐使用中科大源），如下：</p>
<pre><code class="language-toml">[source.crates-io]
registry = "https://github.com/rust-lang/crates.io-index"
# 指定镜像
replace-with = 'ustc' # 如：tuna、sjtu、ustc，或者 rustcc

# 中国科学技术大学
[source.ustc]
registry = "https://mirrors.ustc.edu.cn/crates.io-index"
</code></pre>
<p>当然除了中科大，你也可以用别的源</p>
<pre><code class="language-toml"># 根据个人情况，更改上面代码的6～8行

# 上海交通大学
[source.sjtu]
registry = "https://mirrors.sjtug.sjtu.edu.cn/git/crates.io-index/"

# 清华大学
[source.tuna]
registry = "https://mirrors.tuna.tsinghua.edu.cn/git/crates.io-index.git"

# rustcc社区
[source.rustcc]
registry = "https://code.aliyun.com/rustcc/crates.io-index.git"
</code></pre>
<h2 id="参考引用">参考引用</h2>
<ul>
<li><a href="https://doc.rust-lang.org/cargo/reference/source-replacement.html" target="_blank" rel="noopener nofollow">The Hitchhiker's Guide to Rust | 3.3.2 Source Replacement</a></li>
<li><a href="https://rustwiki.org/en/cargo/reference/source-replacement.html" target="_blank" rel="noopener nofollow">The Cargo Book | 3.11 Source Replacement</a></li>
</ul>