<p><a href="https://git-scm.com/" target="_blank" rel="noopener nofollow"><img src="images/3586302-20250101193235807-1721128320.png" alt="git"  loading="lazy"></a></p>
<h2 id="满汉全席之前">满汉全席之前</h2>
<h3 id="产看git版本号">产看Git版本号</h3>
<pre><code class="language-bash">git -v
</code></pre>
<h3 id="绑定用户信息">绑定用户信息</h3>
<pre><code class="language-bash">#绑定用户名
git config --global user.name "这里填你的名字"

#绑定用户邮箱
git config --global user.email "这里填你的邮箱"
</code></pre>
<h2 id="正式使用git">正式使用Git</h2>
<h3 id="创建一个本地的git项目仓库">创建一个本地的Git项目仓库</h3>
<pre><code class="language-bash">#clone别人的仓库
git clone [项目地址]

#创建版本库
git init [项目所在目录] #执行该指令Git将会在此文件夹下自动创建.git文件
</code></pre>
<h3 id="提交文件">提交文件</h3>
<pre><code class="language-bash">#把代码提交到仓库
git add [文件名] #执行该指令Git将把修改的代码添加到暂存区

#要是你想把该目录下所有文件添加到暂存区可以执行这个命令
git add .
</code></pre>
<h3 id="放入仓库">放入仓库</h3>
<pre><code class="language-bash">git commit -m "备注内容" #这将把你放在暂存区的代码放进仓库里
</code></pre>
<h3 id="查看记录">查看记录</h3>
<pre><code class="language-bash">#查看提交记录
git log

#若想查看更详细的信息，执行下面指令
git log --static # 查看提交时修改了哪些文件

#查看某次提交修改的文件
git diff [commit id]
</code></pre>
<h3 id="代码回溯">代码回溯</h3>
<pre><code class="language-bash">#回溯到某个节点
git reset --hard [commit id]
#或者是这样
git checkout [commit id]
</code></pre>
<h3 id="分支">分支</h3>
<pre><code class="language-bash">#创建分支
git checkout -b [branch name]

#查看分支
git branch

#切换分支
git checkout [branch name]

#合并分支
git merge [branch name] #执行该命令前先切换到你要合并的分支，如master分支
</code></pre>
<h2 id="总结">总结</h2>
<p>通过阅读本文你应该可以学会写Git的基本用法，也许你开始你记不住这么多的命令，但如果你能在实际项目中多尝试使用它，相信聪明的你一定会慢慢掌握。<br>
但如果你想掌握git的原理这远远不够，你需要进一步学习。<br>
还有这只是最基本的用法，更加高级的特性，还要根据你的需求另外学习。</p>