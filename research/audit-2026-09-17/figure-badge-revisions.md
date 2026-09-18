# 图内证据徽标中文化 + 全书图重出 + 前言图 0-1

> 审计日期：2026-09-17 · 范围：`manuscripts/figure_style/__init__.py`、`manuscripts/chNN/build.py`、`manuscripts/chNN/` 下的图与索引 JSON、新建 `manuscripts/preface/`
>
> 目标：把印在书里的英文证据码 `DATA/LIT/CALC/SCHEMATIC` 换成中文标签，重出全书图，并为前言新增阅读路径图。

## A. 徽标标签映射

`manuscripts/figure_style/__init__.py` 保留原 API（`BADGE_KINDS`、`draw_badge`/`badge`、`Exporter.save(badge=...)`）与原有填充色，只把渲染文本从内部代码改为中文：

| 内部代码（kind） | 填充色 | 渲染标签 |
| --- | --- | --- |
| `DATA` | green | 数据结果图 |
| `LIT` | blue | 文献统计图 |
| `CALC` | orange | 复算结果图 |
| `SCHEMATIC` | gray | 示意图 |

其余行为不变：最小标签 11 pt、徽标与任何文字重叠即抛 `ValueError`、`pdf.fonttype=42`、白底、`matplotlib.use('Agg')`、徽标仍需通过 11 pt 下限与画布内校验。`BADGE_KINDS`、`BADGE_FILL` 的键仍是内部代码，`BADGE_LABEL` 只用于绘制。

## B. 全书图重出结果

`python3 manuscripts/chNN/build.py`（N=01…16）全部通过，每条输出 `min label 11 pt, 0 warnings`。

| 章 | 图数 | 警告 | 章 | 图数 | 警告 |
| --- | ---: | ---: | --- | ---: | ---: |
| ch01 | 7 | 0 | ch09 | 11 | 0 |
| ch02 | 9 | 0 | ch10 | 9 | 0 |
| ch03 | 9 | 0 | ch11 | 9 | 0 |
| ch04 | 10 | 0 | ch12 | 10 | 0 |
| ch05 | 11 | 0 | ch13 | 9 | 0 |
| ch06 | 10 | 0 | ch14 | 10 | 0 |
| ch07 | 9 | 0 | ch15 | 8 | 0 |
| ch08 | 9 | 0 | ch16 | 10 | 0 |

合计 150 张章节图，全部重出为 `.svg`、`.png`、`.pdf` 三种格式；`figure-index.json` 与 `teaching-layout-validation.json` 同步刷新。

### 因徽标变宽而调整的图（2 张，均在 ch12）

中文标签比英文码宽，以下两图的顶部文字与右上角徽标相撞，按"下移/左移、不缩字号、不挪徽标"处理：

| 图 | 冲突文字 | 调整 | 文件 |
| --- | --- | --- | --- |
| 图 12-6 mwd | 标题「分子量分布的形状：Flory 宽、Poisson 窄」 | 标题改为左对齐（`loc='left'`），右缘移出徽标区 | `manuscripts/ch12/build.py:206` |
| 图 12-10 worked-route | 右面板标题「可合成性漏斗（8910 候选）」 | 基线由 `y=0.965` 下移到 `y=0.94` | `manuscripts/ch12/build.py:303` |

其余 148 张无需调整。

## C. 渲染标签验证

`grep -rn "SCHEMATIC\|CALC\|LIT\|'DATA'" manuscripts/figure_style/__init__.py` 只命中内部字典的键与 kind 代码（第 74–78 行），无任何把英文码当可见标签渲染的位置。

抽取 ch01 图 1-1 的 PDF 文本：

```
python3 -c "import fitz; d=fitz.open('manuscripts/ch01/figure-1-1-panorama.pdf'); print(d[0].get_text())"
```

输出末尾为 `示意图`，不含 `SCHEMATIC`。`HAS 示意图: True | HAS SCHEMATIC: False`。

## D. 新增前言阅读路径图（图 0-1）

`manuscripts/00-前言.md:54` 已引用 `preface/figure-0-1-reading-paths.svg`（本次未改任何正文）。新建文件：

- `manuscripts/preface/build.py` — 沿用 ch01 约定：`sys.path.insert(0, HERE.parent)`、`from figure_style import COL, Exporter, arrow, box, canvas, text`、`--font` 参数、本地 `sources.json` 的 SHA256 校验、`Exporter(HERE)` + `exp.finish()`、写 `figure-index.json`。
- `manuscripts/preface/sources.json` — `{"date": "2026-09-17", "sources": []}`。
- `manuscripts/preface/figure-index.json` — `[{"figure": "0-1", "asset": "preface/figure-0-1-reading-paths.svg"}]`。
- `manuscripts/preface/figure-0-1-reading-paths.{svg,png,pdf}` — 三条泳道：材料背景读者（第 1–4 章 → 第 15 章（可持续）→ 按需第 5–6 章）、计算与机器学习背景读者（第 1–3 章 → 第 5–12 章 → 第 16 章）、落地工程读者（第 1、3 章 → 第 10、11、13 章 → 第 16 章）；每道以圆点为起点、箭头收尾，右上角徽标 `SCHEMATIC`（渲染为「示意图」）。
- `manuscripts/preface/teaching-layout-validation.json` — 由 `exp.finish()` 生成，`min_label_pt = 11.0`、`0 warnings`。

## E. 核心原则校验

`python3 scripts/verify_core_principles.py` → 退出码 0，`passed: true`，`errors: []`，`total_figures: 150`，无 stderr。本次未出现需转交正文负责人的残留错误。

## 未处理 / 后续

- `scripts/verify_core_principles.py` 只扫描 ch01–ch16，前言图 0-1 不在其统计内（`new_figures: 0`）；若需纳入全书图计数，需另开一轮扩展校验脚本。
- 徽标文字仍由 `figure_style/__init__.py` 集中定义，后续如新增 kind，需同时补 `BADGE_KINDS`、`BADGE_LABEL`、`BADGE_FILL`。
