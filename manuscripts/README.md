# 正文

本目录是全书正文的唯一来源。网站与 PDF 都由这里的 Markdown 生成，因此不要在其他位置维护第二份正文。

## 文件约定

- `00-前言.md`：前言，正文中不编号。
- `NN-<章名>.md`：第 `NN` 章正文，编号与标题必须与 [`archive/outlines/chapters.json`](../archive/outlines/chapters.json) 一致。
- `chNN/`：该章配图与生成脚本。
  - `figure-N-Y-<slug>.svg`、`.png`、`.pdf`：同一张图的三种输出。
  - `figure-index.json`：图号与文件、正文引用位置的对照。
  - `sources.json`：该章引用来源与本地归档文件的对应。
  - `build.py`：由脚本生成配图，不手工编辑图片。

## 写作约定

- 结构来自 [`archive/outlines/`](../archive/outlines/) 的章节大纲与扩写资料；正文的节号、实验号与图号必须与大纲一致。
- 章末顺序固定为：练习、实验、误区、查阅表、延伸阅读，最后是 `## 本章小结`。正文不设"参考资料与证据范围"一类小节，来源一律用脚注。
- 所有数字来自 [`calculations/`](../calculations/) 的复算结果或 [`references/`](../references/) 的归档来源，正文只给结论与量级，推导放在扩写资料中。
- 术语首次出现时给出中英文全称与定义；正文保持肯定、连续、无免责声明的叙述。
- 配图采用《Hands-On Large Language Models》的体例：白底、浅色实体、深色细轮廓、大标签，最小字号 11 pt。

## 构建

```bash
python3 scripts/build_site.py          # 生成网站到 build/site/
bash book/build_pdf.sh                 # 生成 PDF 到 build/
```

两处构建都要求 `manuscripts/` 下 16 章齐备。写作进行中可先用 `bash book/build_pdf.sh --chapter N` 单章预览。
