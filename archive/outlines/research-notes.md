# 调研记录

> 调研范围、方法与未决问题 · 2026-09-16

## 调研范围

| 来源 | 规模 | 用途 | 记录位置 |
| --- | --- | --- | --- |
| Web of Science 检索 | 3178 条（2010–2027） | 主题分布、增长趋势、期刊与机构、代表文献 | `research/2026-wos-survey/` |
| AI4Polymer 资源清单 | 设计发现、性质预测、AI 方法、数据与工具四类 | 领域任务与工具分类 | `references/sources.tsv` |
| 数据集与基准 | PoLyInfo、PI1M、Open Macromolecular Genome、SMiPoly、Kaggle 2025 | 第 3 章数据与基准 | `references/sources.tsv` |
| 方法论文 | 表示、图网络、等变网络、生成、贝叶斯优化、自驱动实验室、智能体 | 第 2、5–14 章 | `references/sources.tsv` |

## 关键统计（来自 WoS 3178 条）

- 年发文量从 2010 年 26 篇增长到 2025 年 699 篇；2019 年后加速，2019–2026 占 91.9%。
- 主题上，`machine learning` 命中 1970 条（62.0%），`neural network` 1481 条（46.6%）；增长最快的是 LLM/transformer/基础模型、物理信息学习与智能体。
- 期刊分布以 `POLYMERS`、`JOURNAL OF POLYMER & COMPOSITES`、`MACROMOLECULES`、`ACS APPLIED MATERIALS & INTERFACES` 为主。
- 被引最高的文献集中在聚合物介电、聚合物基因组、气体分离膜与可持续高分子。
- 机构以中国科学院、美国能源部系统、佐治亚理工、清华、MIT 为主；国家以中国、美国、日本、韩国居前。

详细表格与主题时间序列见 `research/2026-wos-survey/wos-summary.md`。

## 方法

1. 解析 4 个 `.ciw` 导出文件为结构化记录（`research/2026-wos-survey/parse_wos.py`）。
2. 统计年份、文献类型、期刊、学科类别、关键词、被引、机构与国家。
3. 用关键词正则统计主题随年份的变化，识别增长最快的方向。
4. 交叉 AI4Polymer 清单，得到章节任务与工具映射。
5. 依据统计与领域结构设计 16 章框架，并把代表文献登记到 `references/sources.tsv`。

## 数据质量说明

- `DE`（作者关键词）在 763/3178 条记录中缺失，`ID` 在 461 条中缺失。
- 831 个规范化关键词存在大小写变体；同义词未合并，方法频次被低估。
- 导出文件的内部 `DA` 字段统一为 2026-09-16，晚于声明的访问日期 2026-04-21；2026/2027 计数不完整。
- 主题计数为非互斥正则指示，不是分类结果。

## 未决问题

- `Open Macromolecular Genome` 与 `PolyUniverse` 的规模数字未核实，保持 `null`，不进入正文。
- 部分 2026 年记录为 Early Access，最终卷期可能变化。
- 国内研究团队与代表性工作的覆盖仍不完整，后续按章补充。
- 每个核心实验的真实数据集、软件版本与硬件条件待第 2 轮调研确定。
