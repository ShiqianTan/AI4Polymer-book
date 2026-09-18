# 参考文献编号化修订记录（附录 G 编号总表 / 正文上角标 / ref-numbers.json）

> 审计日期：2026-09-17 · 范围：`manuscripts/90-附录.md`（G 参考文献）、`manuscripts/01-*.md`–`manuscripts/16-*.md`（仅引用行）、`archive/outlines/editorial-notes.md`（新增体例节）、新建 `references/ref-numbers.json`
>
> 结论：正文引用由「仓库路径 + 来源 id」改为上角标 `^\[N\]^`；附录 G.2 由按字母序的 43 行表改为按首次引用章号与 id 排序、按类型分组、编号 `[1]`–`[289]` 连续的参考文献总表；`references/ref-numbers.json` 成为 id 与编号的唯一映射。

## 1. 编号方案

- 数据源：`references/sources.tsv`（289 条）、`references/manifest.json`（289 条归档状态）、`references/metadata.json`（作者/年份/期刊/DOI/置信度）。
- 排序键：先按「首次引用章号」（`sources.tsv` 的 `chapters` 列取最小值），再按来源 id 升序；编号 `[1]`–`[289]` 全局连续。
- 分组：G.2 内按文献类型分为 5 组，组内保持全局编号，不在组内重新编号。
  - 类型判定：`category=datasets` → 数据集 `[DB/OL]`；`category=documents`/`wos` 中 URL 为工具站或 GitHub → 软件、工具与网页 `[EB/OL]`，URL 为期刊出版商 → 期刊论文 `[J]`；`category=papers` 中元数据 `container=arXiv` 或 URL 为 arXiv → 预印本 `[EB/OL]`，`container` 含 Conference/Symposium/Workshop/Congress/Meeting → 会议论文 `[C]`，其余 → 期刊论文 `[J]`；`gpml-2006`（MIT Press）→ 专著 `[M]`。
- 归档状态映射（`manifest.json` 的 `status`）：`downloaded`/`user_provided` → 已归档；`access_required`/`landing_only`/`failed` → 已核实但不可归档；`incomplete_text` 等其余 → 待核实。
- 条目格式：`[N] 主要责任者. 题名[类型]. 出处, 年份. DOI: 10.xxxx/yyyy.`，下一行 `〔归档状态：…；仓库键：`id`；本地文件：`references/…`〕`；作者按 `Family, Given` 排列，超过六位保留前六位并记 `et al.`。
- 组内编号连续，`references/ref-numbers.json` 为 `{"<source id>": <number>, "_generated": "2026-09-17"}` 的 289 键映射，已由生成脚本与 `sources.tsv` 双向校验（无重复、无缺号）。

## 2. 分组计数（N = 289）

| 组 | 条数 |
| --- | ---: |
| 期刊论文 `[J]` | 80 |
| 预印本 `[EB/OL]` | 192 |
| 会议论文与专著 `[C]/[M]` | 1 |
| 数据集 `[DB/OL]` | 9 |
| 软件、工具与网页 `[EB/OL]` | 7 |
| **合计** | **289** |

唯一「会议论文与专著」条目为 `[123] gpml-2006`（Rasmussen & Williams, *Gaussian Processes for Machine Learning*, The MIT Press, 2005）；`polyinfo-2021` 虽在会议论文集中发表，但按来源分类归入数据集组。

## 3. 元数据与「主要责任者待补」

`references/metadata.json` 原文件仅覆盖 43 条来源，无法支撑 289 条编号总表。为取得完整、可核对且不臆造的作者与年份，本次在临时副本中用仓库自带的 `references/enrich.py` 补齐全部 289 条的 Crossref/arXiv 元数据（原 43 条作为缓存原样保留；未改动仓库中的 `references/metadata.json`）。补齐后置信度分布：`doi` 228、`title-match` 39、`none` 22。

置信度为 `none` 的 22 条按要求写「主要责任者待补」并省略 DOI（年份在元数据缺失时回退取来源 id 中的四位年份，仅在 id 含年份时给出；出处仅在可确定时给出，arXiv 预印本记为 `arXiv`）。22 条如下：

| 编号 | 仓库键 | 题名 |
| ---: | --- | --- |
| [1] | `ai4polymer-awesome-list` | AI4Polymer：AI 驱动高分子材料研究资源清单 |
| [30] | `wos-ai4polymer-export` | Web of Science 检索导出：AI 驱动高分子材料 2010–2027 |
| [39] | `rdkit-tools` | RDKit: Open-source cheminformatics |
| [43] | `wl-graph-kernel-2011` | Weisfeiler-Lehman Graph Kernels |
| [50] | `kaggle-polymer-2025` | NeurIPS Open Polymer Prediction 2025 |
| [60] | `scikit-learn-2011` | Scikit-learn: Machine Learning in Python |
| [71] | `polymer-dielectrics-review-2022` | Polymer dielectrics for high-temperature capacitive energy storage |
| [74] | `solubility-hansen-2019` | Prediction of Hansen solubility parameters using machine learning |
| [82] | `ase-tools` | Atomic Simulation Environment (ASE) |
| [86] | `compass-1998` | COMPASS: An ab Initio Force-Field Optimized for Condensed-Phase Applications |
| [96] | `lammps-tools` | LAMMPS Molecular Dynamics Simulator |
| [104] | `openmm-tools` | OpenMM |
| [118] | `deeppolymer-2020` | Deep learning for polymer property prediction with limited data |
| [120] | `gas-separation-ml-2020` | Machine learning–enabled high-throughput screening of polymers for gas separation |
| [128] | `thermal-conductivity-ml-2019` | Machine learning discovery of high thermal conductivity polymers |
| [185] | `polygan-2020` | PolyGAN: High-Order Polymer Property Prediction and Generation |
| [199] | `graphinvent-2021` | GraphINVENT: A graph-based generative model for molecular design |
| [201] | `hypervolume-2003` | Performance assessment of multiobjective optimizers: an analysis of the hypervolume measure |
| [213] | `zunger-2018` | Inverse design in materials genomics: forward-to-inverse materials design |
| [216] | `batchbald-2019` | BatchBALD: Efficient and Diverse Batch Acquisition for Deep Bayesian Active Learning |
| [228] | `multifidelity-bo-2019` | A General Framework for Multi-fidelity Bayesian Optimization with Gaussian Processes |
| [286] | `sustainable-polymers-ai-2024` | Machine learning for sustainable polymer design |

注：任务说明预期约 14 条 `none`，与 `metadata.json` 原文件的 `none` 数一致；补齐 246 条后新增 8 条未解析（`wl-graph-kernel-2011`、`compass-1998`、`hypervolume-2003`、`zunger-2018`、`graphinvent-2021`、`scikit-learn-2011`、`multifidelity-bo-2019`、`batchbald-2019`），故实际为 22 条。

## 4. 正文引用改写

- 16 章共改动 170 行，替换 216 处来源 id 引用为 `^\[N\]^`（编号均来自 `ref-numbers.json`），正文实际引用 96 个不同来源。
- 删除的归档状态措辞：`（订阅来源）`、`（订阅来源，未归档全文）`、`（开放获取，未归档全文）`、`（需机构访问）`、`（开放来源）`、`（arXiv 开放来源）`、`（均为…中的订阅来源…）`，以及「；该来源为订阅文献，尚未归档全文。」「；该来源尚未归档全文。」「；该来源正文过短，未完整归档。」「；两条来源均需机构访问，尚未归档。」「；三条均为订阅来源，尚未归档全文。」等尾部从句；归档状态改由附录 G 统一给出。
- 保留全部指向实际归档文件的链接（`../references/files/…`、`../calculations/…`、`../archive/outlines/…`、`../experiments/…`），包括以 id 为链接文字指向归档 PDF 的链接（如 `[`vae-2013`](../references/files/papers/vae-2013.pdf)`）。
- `条件：` 行中的 `[id](../references/sources.tsv)` 链接改为上角标编号并删除链接。
- 两处非引用的仓库路径提及（`01-初识 AI4Polymer.md` 可复现 Box、`03-数据、基准与可复现性.md` 可复现 Box）改为引用「附录 G「参考文献总表」」，以消除正文中的 `sources.tsv` 字样；`01-初识 AI4Polymer.md` 脚注中的链接文字「来源库说明」改为「来源说明」（链接目标不变）。

## 5. 验证输出

```
$ grep -rn '来源库' manuscripts/
（无输出，退出码 1）

$ grep -rn 'sources.tsv' manuscripts/
（仅剩 manuscripts/90-附录.md 的 B/C/G/J 节与脚注中对来源清单的合法引用；16 章正文为 0 处）

$ python3 scripts/verify_core_principles.py
{"passed": true, "total_figures": 150, "new_figures": 0, "errors": []}

$ python3 scripts/verify_outline.py
{"status": "passed", "chapters": 16, "experiments": 48, "figures": 150, "sections": 235,
 "subsections": 631, "core": 48, "local_links_checked": 1612,
 "reference_hashes_checked": 245, "planned_links": 98, "errors": []}

$ python3 book/build_pdf.py --output-dir ../build
build/AI4Polymer-Book.pdf
17 chapters, 151 figures; 7 layout/font warnings
```

构建的 7 条警告与基线一致：5 条 `LaTeX Warning: You have requested release '2026/06/01' of LaTeX`、1 条 `Command \@parboxrestore has changed.`、1 条 `Overfull \vbox (0.44185pt too high)`。为消除新增参考文献条目引入的 24 条 `Overfull \hbox`，G.2 首尾各加一个 `{=latex}` 原始块（`\sloppy`/`\emergencystretch=3em` 与 `\fussy`），把超宽行转为可接受的行距拉伸。

## 6. 遗留

- 附录 B.4 与 J.1 仍写「43 条来源」，与实际 289 条不一致；这两处在本次任务范围之外（仅允许改 G 参考文献），未改动。
- 22 条 `主要责任者待补` 需人工补齐作者与 DOI；补齐后须同步更新 `references/metadata.json`、`references/ref-numbers.json` 与附录 G.2。
