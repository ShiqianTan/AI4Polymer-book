# 在线阅读与自动发布

正文维护在 `manuscripts/`，包含前言和十六章 Markdown；网站目录直接从正文生成。MkDocs Material 从这些源文件构建中文阅读网站，提供章节导航、全文搜索、数学公式、脚注、深色模式和手机阅读布局。

## 本地构建

在仓库根目录运行（Python 3.10+）：

```bash
python3 -m venv .venv-site
source .venv-site/bin/activate
pip install -r website/requirements.txt
python scripts/build_site.py
python scripts/check_site.py
```

输出全部位于被 Git 忽略的 `build/site/`。预览运行 `python scripts/build_site.py --serve`，打开 `http://127.0.0.1:8000`；修改正文后重新运行命令以重新整理源文件。临时 Markdown 位于 `build/docs/`，由构建器覆盖，不应手动维护。公式使用固定版本的 MathJax CDN，首次阅读需要网络。

构建只复制正文与引用的图片；实验、计算记录和原始资料链接指向构建提交对应的 GitHub 文件，避免网站携带庞大的研究归档。缺失的本地引用或未下载的图片 LFS 指针会使构建失败。

## 推送即发布

每次 push 到 `main`，GitHub Actions 自动执行：

1. 从同一提交的 Markdown 构建网站与十六章全书 PDF。
2. 检查网站链接、图片、PDF 章节、文字及字体；保存 PDF 日志和代表页面预览。
3. 创建 `build-<完整提交 SHA>` 对应的 GitHub Release，只上传完整的 `AI4Polymer-Book.pdf`。重复运行同一提交会更新全书 PDF 并移除旧的辅助附件。封面、网站压缩包、来源和校验记录保留在 Actions 产物中。
4. 将网站部署到 GitHub Pages。只有 PDF 和网站都构建成功后才发布；Release 与 Pages 分别执行，Pages 设置问题不会阻止 Release 附件发布。

不需要手工打标签或创建 Release。也可在默认分支手动运行 `Build and publish book` 工作流。Pull Request 只构建、检查和上传 Actions 产物，不发布 Release 或 Pages。GitHub Actions 同一分支的发布串行执行；快速连续推送时，GitHub 可能替换尚未启动的待运行任务，以最新提交为准。

PDF 在 macOS 15 使用 Pandoc 3.7.0.2 和 Homebrew TeX Live / XeLaTeX 构建，与本地一致使用 Songti SC 正文、Menlo 代码，以及 Arial Unicode MS / Heiti SC 特殊字符；项目提供的思源黑体用于中文粗体与图注。编译前检查必需字体，编译后核对实际 PDF 字体，防止缺少字体时静默替换。发布版中的资料链接指向该提交的 GitHub 文件，下载 PDF 后仍可访问来源（私有仓库需要登录）。

## GitHub Pages 首次启用

仓库设置 **Settings → Pages → Build and deployment → Source** 需选择 **GitHub Actions**。目标地址：

<https://ShiqianTan.github.io/AI4Polymer-book/>

首次发布前启用上述设置，再推送到 `main` 或手动运行工作流；部署成功后即可在线阅读。

## 下载和本地复现

<!-- TODO: release 发布后补充固定下载链接 -->
最新版全书 PDF 将随 Release 发布，固定下载链接形如 `https://github.com/ShiqianTan/AI4Polymer-book/releases/latest/download/AI4Polymer-Book.pdf`，始终指向最近一次标记为 Latest 的 Release。网站可直接通过 GitHub Pages 阅读；如需离线网站，从 Actions 的 `book-site-download` 产物取得 `ai4polymer-book-site.tar.gz`，解压后运行 `python -m http.server`。

已有 PDF 编译依赖时，在仓库根目录运行：

```bash
bash book/build_pdf.sh --output-dir ../build/pdf --source-ref "$(git rev-parse HEAD)"
python3 -m pip install -r book/requirements-ci.txt
python3 book/check_ci_pdf.py build/pdf
```

`--output-dir` 相对于 `book/`；CI 的 PDF 产物放在忽略目录 `build/pdf/`，不覆盖仓库内已有 PDF。省略 `--source-ref` 时保留本地资料链接；发布构建传入提交 SHA 生成可独立下载的版本。
