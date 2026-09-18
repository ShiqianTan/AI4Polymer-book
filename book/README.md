# AI4Polymer Book · LaTeX 排版

沿用 AI Agent Book 系列的 ElegantBook 模板，生成真正由 XeLaTeX 排版的 PDF。正文读取 `manuscripts/01-*.md` 至 `16-*.md` 以及 `manuscripts/00-前言.md`，不维护另一套章节副本。

<!-- TODO: release -->
全书 PDF 由 GitHub Actions 从 `main` 自动构建并发布到 [Releases](https://github.com/ShiqianTan/AI4Polymer-book/releases)。首次发布前暂无固定下载链接；构建完成后可在此处补充 `<https://github.com/ShiqianTan/AI4Polymer-book/releases/latest/download/AI4Polymer-Book.pdf>`。

编译生成的 PDF、封面和 `*-build.json` 构建记录不纳入版本控制（见 `book/.gitignore`）。

## 编译

在仓库根目录执行：

```bash
# 十六章、封面和目录
bash book/build_pdf.sh

# 只看第二章，保留原来的第 2 章及 2.x 编号
bash book/build_pdf.sh --chapter 2
```

依赖为 Python 3.9+、Pandoc 3.x 和含 XeLaTeX 的 TeX Live/MacTeX。普通正文保留 AI Agent Book 的 Songti SC（宋体），代码使用 Menlo；中文粗体与章节标题使用项目自带的思源黑体 Bold，图注和图表也统一使用思源黑体。字体文件与 OFL 许可证见 `manuscripts/figure_style/fonts/`，无需另行安装思源黑体。没有 Songti SC 时保留原模板的 Noto Sans CJK SC 回退。可选的 Poppler（`pdfseparate`、`pdftoppm`）用于从全书导出独立封面 PDF 和 PNG；若安装 Ghostscript（`gs`），封面 PDF 只保留本页使用的字体和资源。封面和章节 PDF 中的日期是编译日期。

`build_pdf.py` 先调用 Pandoc 生成 LaTeX，再执行三遍 XeLaTeX，稳定目录、交叉引用和跨页表格。各次日志、中间 Markdown、LaTeX 和辅助文件保存在 `book/build/`，不会覆盖正文。输出与构建记录保存在 `book/AI4Polymer-Book*.pdf` 和 `*-build.json`，这些文件只留在本地，不提交到仓库。

图表使用正文对应的 PDF 矢量文件，缺少 PDF 时使用 PNG；编译前如修改过图表，应先运行相应章节的图表构建脚本。构建器会合并图片说明与紧随其后的图注，避免重复显示，保留原有手工图号。所有表格保持竖向页面，短表接排正文，长表按需跨页。Markdown 脚注保留为 PDF 页脚注，各章脚注互不冲突。指向计算记录和参考材料的文件链接相对于本仓库目录保留，因此这些附件需随仓库一起访问。

## 模板与封面

`template/agent-book-preamble.tex`、`template/agent-book-cover.tex` 和 `template/agent-book-build_pdf.sh` 直接复制自相邻仓库 `ai-infra-book/book/`，原件保持不变。`template/provenance.json` 记录来源、哈希与 Apache-2.0 许可说明。`elegantbook.cls` 固定使用 ElegantBook 4.6，保留原始版权及 LPPL 许可声明。

`preamble.tex` 加载原模板并追加本书需要的适配：中文无衬线字体按正常字号显示、原生数学排版、图表浮动、长链接换行和竖向矩阵表。正文继续使用原系列的深蓝标题与页眉、宋体正文、浅色代码框和引文框。

`cover.tex` 是本书的新封面：保留原系列的白底、深蓝色带、标题和作者排布，中心不放置任何图案，只保留书名、副标题、作者与版本日期。标题固定在距页顶 5.2 cm 处，副标题为 6.6 cm，分隔线为 7.7 cm，版本日期距页底 3.95 cm，留白不再受正文段落高度影响。文字与线条均为矢量，可直接修改颜色、标题和几何形状，无需外部图片。

## 校验

运行 `python3 book/verify_pdf.py` 检查书名、章节、字体嵌入、页面文字边界与 LaTeX 关键警告。结果保存到 `pdf-validation.json`。CI 使用 `book/check_ci_pdf.py` 检查全书 PDF 的章节书签、正文可读性、字体一致性与警告，并渲染代表页面供人工复核；编译前用 `book/check_build_fonts.py` 确认 macOS 字体齐全。上述校验脚本依赖 Poppler 与 PyMuPDF（`book/requirements-ci.txt`）。

## 紧凑图文排版

正文配图等比缩放，宽度上限为正文行宽的 68%，高度上限为正文区高度的 38%。较高的图保留足够空间，让小字仍可阅读；标题、图注不随图片缩放。图片采用 `!htbp` 浮动，优先放在引用处，放不下时移至页顶、页底或浮动页，让文字继续排下去。浮动页中的图采用正常间距，不把空白拉伸到整页。

所有表格按正常正文页宽排版：列间距缩小为 2.5 pt，表格宽度控制在行宽以内，中文及长公式可在单元格中换行。表格直接接排正文，长表按需跨页并重复表头；不使用旋转页面或强制单表独占一页。短表标题随表体一起排版。

公式直接交给 Pandoc / LaTeX 的原生数学环境，保持正文对应的数学字号及正常上下标，不经过 `adjustbox`、`resizebox` 或图片宽度设置。全局图形宽高均已清空，尺寸限制只作用于真正的图片。构建产物采用原子替换，打开 PDF 时不会读到编译中的半份文件。

## 中文字体体例

普通正文维持宋体；中文粗体（包括 Markdown 粗体、章标题和各级小节标题）映射到真正的思源黑体 Bold，不再对宋体做合成加粗。图注与所有章节配图也统一为思源黑体。拉丁字母与原生公式保留原模板字体。

思源黑体随项目提供，Apple 字体使用 macOS 系统安装版本；使用的字体嵌入 PDF。SVG 图中文字转为矢量轮廓，避免阅读端缺少字体时回退。字体来源和许可证见 `manuscripts/figure_style/fonts/README.md`。

## 自动构建与 Release

每次 push 到 `main`，工作流在 macOS 15 上从当前 Markdown 自动编译十六章全书、封面 PDF/PNG，检查章节与字体并保存样页和日志。PDF 与网站构建都通过后，自动创建该提交对应的 GitHub Release，并部署网站至 Pages；完整说明见 [发布流程](../website/README.md)。

云端输出写入 `build/pdf/`，不回写仓库中的 PDF。使用 `--source-ref` 参数的发布版会将资料链接改为对应提交的 GitHub 链接。发布构建与本地均使用 Songti SC、Menlo、Arial Unicode MS 和 Heiti SC；通过 Homebrew 安装 TeX Live，Pandoc 固定为 3.7.0.2。编译前运行 `python3 book/check_build_fonts.py` 检查字体是否齐全，编译后检查 PDF 实际使用的字体，缺失或回退即失败。导入的系列模板原件保持不变。

GitHub Release 只上传完整的 `AI4Polymer-Book.pdf`。封面、来源记录、校验结果以及网站压缩包保留在 Actions 的构建产物中，日志与样页保留在诊断产物中，不作为 Release 下载附件。
