# AI4Polymer：人工智能驱动的高分子材料设计

[![Build](https://github.com/ShiqianTan/AI4Polymer-book/actions/workflows/book-site.yml/badge.svg)](https://github.com/ShiqianTan/AI4Polymer-book/actions/workflows/book-site.yml)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)
[![Stars](https://img.shields.io/github/stars/ShiqianTan/AI4Polymer-book?style=social)](https://github.com/ShiqianTan/AI4Polymer-book)

> [!TIP]
> ### 下载全书 PDF
>
> <!-- TODO: release -->
> **推荐下载 PDF 阅读。** 书中有大量公式、表格、脚注和交叉引用，GitHub 直接显示 Markdown 时，LaTeX 公式和部分排版常常渲染不全或错位。PDF 由 XeLaTeX 排版，每次更新 `main` 后自动构建并发布到 [Releases](https://github.com/ShiqianTan/AI4Polymer-book/releases)。首次发布后，固定下载链接为 `https://github.com/ShiqianTan/AI4Polymer-book/releases/latest/download/AI4Polymer-Book.pdf`，始终指向最新版。下方目录链接到各章 Markdown 源文件，便于查找原文和提交勘误；通读全书，仍建议下载 PDF。

高分子材料的设计长期依赖经验与试错：同一条链的化学组成、序列、构象与聚集形态共同决定宏观性能，设计空间极其庞大。人工智能提供了一条新路径——用数据与模型在高维空间中发现规律，加速筛选与发现。《AI4Polymer：人工智能驱动的高分子材料设计》系统介绍这条路径上的方法、工具与实践。

本书贯穿的主线是**把领域知识编码进模型**。高分子不是任意字符串：它遵循聚合化学、热力学与动力学约束，具有明确的多尺度结构。表示与描述符、物理信息损失、数据基准与可复现性，决定了模型能否泛化到训练集之外；生成模型、逆向设计与主动学习，则决定我们能否在巨大的设计空间中高效搜索。本书反复追问：**用什么表示、用什么数据、用什么模型、如何验证、如何闭环。**

更多写作背景见[前言](manuscripts/00-前言.md)。目前书稿仍是初稿，正在持续修订。

## 内容目录

### 第一部分 基础与表示

| 章 | 主题 |
| :--: | --- |
| 1 | [初识 AI4Polymer](<manuscripts/01-初识 AI4Polymer.md>) |
| 2 | [高分子表示与描述符](manuscripts/02-高分子表示与描述符.md) |
| 3 | [数据、基准与可复现性](manuscripts/03-数据、基准与可复现性.md) |
| 4 | [高分子物理与结构–性能关系](manuscripts/04-高分子物理与结构–性能关系.md) |

### 第二部分 模拟与预测

| 章 | 主题 |
| :--: | --- |
| 5 | [分子模拟与多尺度计算](manuscripts/05-分子模拟与多尺度计算.md) |
| 6 | [性质预测模型](manuscripts/06-性质预测模型.md) |
| 7 | [多任务、迁移与物理信息学习](manuscripts/07-多任务、迁移与物理信息学习.md) |
| 8 | [表征、成像与光谱的 AI 分析](manuscripts/08-表征、成像与光谱的 AI 分析.md) |

### 第三部分 生成与设计

| 章 | 主题 |
| :--: | --- |
| 9 | [生成模型与高分子序列设计](manuscripts/09-生成模型与高分子序列设计.md) |
| 10 | [逆向设计与多目标材料设计](manuscripts/10-逆向设计与多目标材料设计.md) |
| 11 | [主动学习、贝叶斯优化与强化学习](manuscripts/11-主动学习、贝叶斯优化与强化学习.md) |
| 12 | [反应预测、聚合建模与可合成性](manuscripts/12-反应预测、聚合建模与可合成性.md) |

### 第四部分 自动化与前沿

| 章 | 主题 |
| :--: | --- |
| 13 | [自驱动实验室与高通量自动化](manuscripts/13-自驱动实验室与高通量自动化.md) |
| 14 | [高分子基础模型与智能体系统](manuscripts/14-高分子基础模型与智能体系统.md) |
| 15 | [可持续高分子与环境应用](manuscripts/15-可持续高分子与环境应用.md) |
| 16 | [端到端案例与工程实践](manuscripts/16-端到端案例与工程实践.md) |

## 适合谁读

如果你有化学、材料或高分子背景，想了解如何用机器学习加速研究与开发，这本书可以作为起点；如果你有机器学习背景，想进入材料与高分子领域，书中会交代必要的领域概念与数据特点。相关方向的研究人员和学生也能从表示、基准与闭环设计的讨论中受益。

阅读时需要一些 Python、线性代数与基础化学知识。建议先读第 1—3 章，建立表示、数据与可复现性的共同基础，再根据兴趣选择重点：

- 关注性质预测与模拟，可以重点读第 4—7 章，理解结构–性能关系与多尺度计算。
- 关注生成与设计，可以重点读第 9—11 章，再看第 12 章的可合成性约束。
- 关注实验自动化与前沿，可以重点读第 8、13、14 章，了解表征分析、自驱动实验室与基础模型。
- 希望系统学习，可以按目录顺序阅读，并结合配套计算与案例逐步核对理解。

遇到书中的方法或案例，不妨先自己思考表示与数据是否合理，再看推导与结果。也可以换成你熟悉的高分子体系，看看结论是否改变。

## 配套计算与实验

<!-- TODO: 计算工具与案例仍在补充，接口稳定后在此补充可复算示例。 -->
[计算项目](calculations/)用于复算书中的数值与图，[案例与实验](case-studies/)按章节组织可复现的案例。仓库使用 [Git LFS](https://git-lfs.com/) 保存原始数据与较大的输入与测量记录。为避免克隆时全部下载，[.lfsconfig](.lfsconfig) 默认跳过所有 LFS 文件，工作区中只留下指针；正文、配图和静态计算都不需要它们。复现某个案例时，只下载对应目录：

```bash
git lfs install
git lfs pull --include="references/files/**" --exclude=""
```

复现或引用结果时，请留意所用的书稿版本、数据划分、模型与随机种子。

## 本地构建

**阅读网站**（Python 3.10+）：

```bash
python3 -m venv .venv-site
source .venv-site/bin/activate
python -m pip install -r website/requirements.txt
python scripts/build_site.py
python scripts/check_site.py
python scripts/build_site.py --serve
```

预览地址为 <http://127.0.0.1:8000>。生成文件位于 `build/`，详细说明见[网站构建与发布](website/README.md)。

**全书 PDF**（另需 Pandoc、XeLaTeX 和字体）：

```bash
bash book/build_pdf.sh
```

依赖、字体及单章编译方法见 [PDF 编译说明](book/README.md)。GitHub Actions 会检查 Pull Request 的网站与 PDF 构建；推送到 `main` 后自动生成 Release 并部署 Pages。

## 仓库结构

| 目录 | 内容 |
| --- | --- |
| [manuscripts/](manuscripts/) | 前言、十六章正文、配图与绘图脚本 |
| [case-studies/](case-studies/) | 按章节组织的案例研究 |
| [calculations/](calculations/) | 计算工具、固定输入与复算结果 |
| [references/](references/) | 引用资料、来源清单与版本快照 |
| [book/](book/README.md) | PDF 模板、构建与校验工具 |
| [website/](website/README.md)、[scripts/](scripts/README.md) | 网站资源、构建与检查脚本 |
| [archive/](archive/) | 历史大纲与写作协调记录 |

## 参与贡献

书稿仍是初稿，欢迎读者参与改进。以下几个方向都有价值，欢迎认领：

- **指出并修正错误**：概念、公式、数据或引用有误。发现一处就值得提一处，[勘误 Issue](https://github.com/ShiqianTan/AI4Polymer-book/issues/new?template=erratum.yml) 或直接提 PR 都可以。
- **改写讲得不清楚的地方**：推导跳步、概念没有在首次出现时交代、例子不好懂。读不顺的地方多半是书写得不好，欢迎[提出来](https://github.com/ShiqianTan/AI4Polymer-book/issues/new?template=question.yml)，也欢迎直接给出更好的写法。
- **补充遗漏的重要内容**：某个该讲的方法、模型或材料体系没有写进来。
- **修复配套代码的 bug**：`calculations/` 与 `case-studies/` 中的代码，欢迎修正错误、补充测试或改进可用性。
- **改进网页版**：在线阅读版的排版、导航、搜索和移动端体验都还有提升空间。
- **翻译**：欢迎将本书翻译为英文或其他语言，翻译前请先开 Issue 说明计划，便于协调进度、避免重复劳动。

正文的唯一来源是 `manuscripts/` 下的 Markdown，网页版和 PDF 都由它构建生成，改正文请直接改这里。

## 作者与致谢

作者：Shiqian Tan（谭诗乾）。

感谢相关论文、开源项目与技术文档的作者，以及参与勘误与案例复现的读者。引用来源见正文脚注和[参考资料库](references/)。本书 PDF 沿用《深入理解 AI Agent》/《深入理解 AI Infra》的 ElegantBook / XeLaTeX 模板。

## 许可

本书原创正文、配图及配套代码采用 [Apache License 2.0](LICENSE) 许可。Copyright © 2026 Shiqian Tan。

仓库中的第三方代码、字体、模板与参考资料保留各自的版权和许可声明，不因收录于本仓库而改用 Apache-2.0；具体来源和使用条件见相应目录。
