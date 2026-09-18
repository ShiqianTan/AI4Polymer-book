# references/wos — AI4Polymer Web of Science 原始导出

本目录保存 2026 年 AI4Polymer 文献计量调研所用的原始 Web of Science 导出文件，供复核与重算。

## 来源与检索

- 数据库：Clarivate Web of Science Core Collection。
- 检索式：

  ```
  (TI=(polymer* OR macromolecul* OR "polymeric material*" OR "high polymer" OR copolymer* OR biopolymer* OR elastomer*) AND PY=(2010-2027)) AND (AB=("machine learning" OR "deep learning" OR "neural network*" OR "reinforcement learning" OR "large language model" OR "AI Agent") AND PY=(2010-2027))
  ```

- 检索日期（access date）：2026-04-21。
- 导出格式：Clarivate tagged plain text（`.ciw`），每记录以 `PT ` 开始、以 `ER` 结束，字段代码为 2 字符，续行缩进 3 个空格。

## 文件

| 文件 | 记录数 |
|---|---|
| `ai4polymer-wos-1-1000.ciw` | 1000 |
| `ai4polymer-wos-1001-2000.ciw` | 1000 |
| `ai4polymer-wos-2001-3000.ciw` | 1000 |
| `ai4polymer-wos-3001-3178.ciw` | 178 |
| 合计 | **3178** |

四个文件为 Web of Science 的原始导出，未做任何修改；仅按导出批次拆分。MD5 校验值（复制自 `/Users/shiqian/Documents/github/ShiqianTan/AI4Polymer/wos/`）：

```
10f195ee5411f44cb20d27b5c89b7e05  ai4polymer-wos-1-1000.ciw
762dc1bf74786b6ed4ad5dfea8dd3b19  ai4polymer-wos-1001-2000.ciw
ed1be80efc7c3b2fc6a528900bb07012  ai4polymer-wos-2001-3000.ciw
98556026dae3dd13fee995b8ca4e7330  ai4polymer-wos-3001-3178.ciw
```

## 重算

解析与统计脚本位于 [`../../research/2026-wos-survey/parse_wos.py`](../../research/2026-wos-survey/parse_wos.py)：

```sh
python3 research/2026-wos-survey/parse_wos.py --wos references/wos --output research/2026-wos-survey/wos-summary.json
```
