# 2026 AI4Polymer Web of Science 文献计量调研

本调研把 2026-04-21 从 Web of Science Core Collection 导出的 3178 条记录（检索式与导出文件见 [`references/wos/README.md`](../../references/wos/README.md)）解析为可复算的研究资料。所有数字由 [`parse_wos.py`](parse_wos.py) 从原始 `.ciw` 文件直接计算，未做人工筛选；机器生成的完整表格见 [`wos-summary.md`](wos-summary.md)，原始数值见 [`wos-summary.json`](wos-summary.json)。

复现命令：

```sh
python3 research/2026-wos-survey/parse_wos.py --wos references/wos --output research/2026-wos-survey/wos-summary.json
python3 research/2026-wos-survey/parse_wos.py --wos references/wos --output research/2026-wos-survey/wos-summary.md --format md
```

## 检索式与数据口径

检索式（与 AI4Polymer README 一致）：

```
(TI=(polymer* OR macromolecul* OR "polymeric material*" OR "high polymer" OR copolymer* OR biopolymer* OR elastomer*) AND PY=(2010-2027)) AND (AB=("machine learning" OR "deep learning" OR "neural network*" OR "reinforcement learning" OR "large language model" OR "AI Agent") AND PY=(2010-2027))
```

| 项目 | 值 |
|---|---|
| 数据库 | Web of Science Core Collection |
| 检索日期 | 2026-04-21 |
| 记录总数 | 3178 |
| 逐年合计 | 3178（与总数一致） |
| 年份范围 | 2010–2027 |
| 导出文件 | 4 个 `.ciw`（1000+1000+1000+178） |

检索式限定标题含高分子词汇、摘要含 AI 词汇，因此本语料是“高分子 × 机器学习”的交集，而非高分子全体或 AI 全体。主题计数仅表示字段中出现相应词项，不表示该文献以该主题为核心。

## 总量与逐年增长

| 年份 | 2010 | 2011 | 2012 | 2013 | 2014 | 2015 | 2016 | 2017 | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 | 2026 | 2027 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 记录数 | 26 | 21 | 19 | 32 | 26 | 21 | 29 | 45 | 35 | 90 | 117 | 207 | 296 | 353 | 480 | 699 | 677 | 5 |

关键事实：

- 2010–2018 九年合计 254 条，占 8.0%；2019–2026 合计 2919 条，占 91.9%。
- 2022–2026 五年合计 2505 条，占 78.8%；2025 与 2026 两年合计 1376 条，占 43.3%。
- 2025 年 699 条，为 2010 年 26 条的约 26.9 倍。
- 2026 年 677 条低于 2025 年，2027 年仅 5 条；这两年的计数不完整（见“数据质量”）。

## 学科分布

WoS 分类（`WC`，前 20；一条记录可属多个分类）：

| 分类 | 记录数 | 分类 | 记录数 |
|---|---|---|---|
| Materials Science, Multidisciplinary | 787 | Multidisciplinary Sciences | 127 |
| Polymer Science | 622 | Mechanics | 127 |
| Chemistry, Multidisciplinary | 410 | Instruments & Instrumentation | 120 |
| Chemistry, Physical | 408 | Materials Science, Composites | 120 |
| Nanoscience & Nanotechnology | 253 | Physics, Condensed Matter | 116 |
| Physics, Applied | 236 | Engineering, Electrical & Electronic | 115 |
| Engineering, Chemical | 221 | Engineering, Mechanical | 96 |
| Engineering, Multidisciplinary | 138 | Engineering, Civil | 95 |
| Computer Science, Interdisciplinary Applications | 137 | Physics, Atomic, Molecular & Chemical | 95 |
| Energy & Fuels | 131 | Chemistry, Analytical | 89 |

研究领域（`SC`，前 15）：

| 领域 | 记录数 | 领域 | 记录数 |
|---|---|---|---|
| Materials Science | 992 | Mechanics | 127 |
| Chemistry | 865 | Instruments & Instrumentation | 120 |
| Engineering | 786 | Biochemistry & Molecular Biology | 107 |
| Polymer Science | 622 | Pharmacology & Pharmacy | 76 |
| Physics | 417 | Automation & Control Systems | 65 |
| Science & Technology - Other Topics | 400 | Environmental Sciences & Ecology | 61 |
| Computer Science | 221 | Construction & Building Technology | 59 |
| Energy & Fuels | 131 | | |

材料科学（992，31.2%）、化学（865）、工程（786）与高分子科学（622）构成主体；计算机科学（221）占比不高，说明多数工作以材料／化学期刊为载体，计算方法嵌入领域研究而非独立 AI 论文。

## 期刊与机构／国家分布

期刊（`SO`，前 20）：

| 期刊 | 记录数 | 期刊 | 记录数 |
|---|---|---|---|
| POLYMERS | 97 | NPJ COMPUTATIONAL MATERIALS | 28 |
| JOURNAL OF POLYMER & COMPOSITES | 89 | ADVANCED FUNCTIONAL MATERIALS | 27 |
| MACROMOLECULES | 61 | CHEMICAL ENGINEERING JOURNAL | 27 |
| ACS APPLIED MATERIALS & INTERFACES | 56 | DIGITAL DISCOVERY | 27 |
| COMPUTATIONAL MATERIALS SCIENCE | 41 | NATURE COMMUNICATIONS | 23 |
| SCIENTIFIC REPORTS | 41 | COMPOSITE STRUCTURES | 22 |
| JOURNAL OF CHEMICAL PHYSICS | 33 | MATERIALS TODAY COMMUNICATIONS | 21 |
| POLYMER | 33 | JOURNAL OF APPLIED POLYMER SCIENCE | 20 |
| JOURNAL OF CHEMICAL INFORMATION AND MODELING | 32 | MATERIALS | 20 |
| JOURNAL OF PHYSICAL CHEMISTRY B | 28 | ACS APPLIED POLYMER MATERIALS | 19 |

前 10 期刊合计 511 条，占 16.1%；最高产的 POLYMERS 占 3.1%。期刊分布分散，没有单一主导载体。

机构（`C3`，前 20；同一条记录内去重）：

| 机构 | 记录数 | 机构 | 记录数 |
|---|---|---|---|
| Chinese Academy of Sciences | 104 | University of Science & Technology of China, CAS | 38 |
| United States Department of Energy (DOE) | 69 | Zhejiang University | 34 |
| University System of Georgia | 67 | Massachusetts Institute of Technology (MIT) | 33 |
| Indian Institute of Technology System (IIT System) | 63 | Shanghai Jiao Tong University | 32 |
| Georgia Institute of Technology | 58 | East China University of Science and Technology | 30 |
| Egyptian Knowledge Bank (EKB) | 46 | Fudan University | 29 |
| Tsinghua University | 46 | Amirkabir University of Technology | 28 |
| National Institute of Technology (NIT System) | 44 | Saveetha Institute of Medical & Technical Science | 28 |
| Centre National de la Recherche Scientifique (CNRS) | 42 | University of Chinese Academy of Sciences, CAS | 28 |
| University of California System | 39 | Xi'an Jiaotong University | 28 |

国家／地区（从 `C1` 地址尾段解析，前 20）：

| 国家/地区 | 记录数 | 国家/地区 | 记录数 |
|---|---|---|---|
| China | 924 | Australia | 104 |
| USA | 672 | Canada | 89 |
| India | 372 | Malaysia | 78 |
| Japan | 171 | Spain | 77 |
| Saudi Arabia | 162 | Pakistan | 75 |
| Iran | 152 | France | 68 |
| United Kingdom | 148 | Italy | 65 |
| South Korea | 147 | Russia | 60 |
| Germany | 137 | Egypt | 50 |
| Turkey | 115 | Singapore | 46 |

中国 924 条（29.1%）与美国 672 条（21.1%）居前两位，印度（372）随后；前 20 名中亚洲国家占比较高（中国、印度、日本、沙特阿拉伯、伊朗、韩国、马来西亚、巴基斯坦、新加坡等）。

## 关键词与主题聚类

作者关键词（`DE`）前 30（大小写归一后计数）：

| 关键词 | 记录数 | 关键词 | 记录数 |
|---|---|---|---|
| machine learning | 799 | random forest | 32 |
| artificial neural network | 158 | ann | 31 |
| deep learning | 133 | molecular dynamics | 29 |
| polymers | 121 | transfer learning | 26 |
| artificial intelligence | 106 | artificial neural network (ann) | 26 |
| polymer | 86 | polymer nanocomposites | 25 |
| neural network | 71 | polymer informatics | 25 |
| artificial neural networks | 67 | glass transition temperature | 24 |
| additive manufacturing | 52 | convolutional neural network | 23 |
| mechanical properties | 50 | bayesian optimization | 23 |
| polymer composites | 47 | materials informatics | 22 |
| neural networks | 46 | prediction | 21 |
| optimization | 44 | composites | 20 |
| genetic algorithm | 38 | machine learning (ml) | 20 |
| modeling | 37 | | |
| 3d printing | 35 | | |

Keywords-Plus（`ID`，前 15）：design (230)、prediction (229)、behavior (214)、performance (204)、model (172)、optimization (140)、mechanical-properties (134)、composites (99)、simulation (79)、temperature (79)、neural-networks (74)、dynamics (74)、strength (64)、nanocomposites (64)、nanoparticles (64)。

前 30 作者关键词的共现（同一记录内，记录数 ≥ 2 的靠前词对）：

| 词对 | 共现 | 词对 | 共现 |
|---|---|---|---|
| machine learning + polymers | 68 | machine learning + molecular dynamics | 15 |
| artificial intelligence + machine learning | 44 | glass transition temperature + machine learning | 14 |
| machine learning + polymer | 33 | machine learning + polymer nanocomposites | 14 |
| additive manufacturing + machine learning | 29 | 3d printing + machine learning | 13 |
| deep learning + machine learning | 26 | machine learning + optimization | 13 |
| machine learning + mechanical properties | 18 | machine learning + polymer informatics | 13 |
| machine learning + polymer composites | 18 | artificial neural network + genetic algorithm | 12 |
| machine learning + random forest | 17 | machine learning + materials informatics | 11 |
| artificial neural network + machine learning | 15 | machine learning + transfer learning | 10 |

共现结构以 `machine learning` 为中心，向外连接三类对象：材料对象（polymers、composites、nanocomposites）、任务（mechanical properties、glass transition temperature、prediction、optimization）与方法（deep learning、random forest、transfer learning、bayesian optimization、molecular dynamics）。尚未形成彼此分离的强聚类，说明该领域仍处于“通用 ML 方法 + 具体材料问题”的阶段。

## 方法演进时间线

主题正则匹配 `TI+AB+DE+ID` 的逐年计数（同一记录可命中多个主题）：

| 主题 | 合计 | 2010 | 2011 | 2012 | 2013 | 2014 | 2015 | 2016 | 2017 | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 | 2026 | 2027 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| machine learning | 1970 | 1 | 1 | 0 | 1 | 1 | 3 | 8 | 9 | 10 | 38 | 59 | 120 | 171 | 221 | 346 | 502 | 474 | 5 |
| neural network | 1481 | 25 | 20 | 18 | 30 | 24 | 18 | 21 | 37 | 24 | 51 | 64 | 104 | 159 | 165 | 182 | 274 | 265 | 0 |
| mechanical properties | 534 | 3 | 0 | 4 | 1 | 2 | 3 | 1 | 0 | 3 | 11 | 21 | 27 | 50 | 63 | 72 | 138 | 135 | 0 |
| representation/SMILES/descriptor/fingerprint | 510 | 5 | 3 | 4 | 3 | 2 | 2 | 2 | 3 | 4 | 12 | 24 | 24 | 41 | 44 | 95 | 102 | 139 | 1 |
| uncertainty/interpretability/SHAP | 394 | 1 | 2 | 0 | 0 | 3 | 1 | 0 | 3 | 1 | 5 | 6 | 12 | 27 | 33 | 64 | 98 | 137 | 1 |
| deep learning | 378 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 2 | 1 | 6 | 12 | 31 | 39 | 43 | 55 | 101 | 87 | 0 |
| membrane/separation | 375 | 1 | 2 | 1 | 1 | 1 | 3 | 2 | 6 | 5 | 3 | 15 | 39 | 43 | 54 | 54 | 67 | 76 | 2 |
| dielectric/energy storage/battery/electrolyte | 363 | 1 | 4 | 2 | 0 | 1 | 0 | 6 | 4 | 5 | 6 | 15 | 38 | 27 | 37 | 55 | 76 | 85 | 1 |
| molecular dynamics/DFT/coarse-grained | 347 | 1 | 1 | 1 | 1 | 1 | 2 | 4 | 3 | 4 | 9 | 17 | 27 | 30 | 35 | 54 | 79 | 77 | 1 |
| sustainability/recycling/biodegradation | 338 | 0 | 3 | 1 | 2 | 0 | 0 | 1 | 0 | 0 | 3 | 3 | 8 | 19 | 19 | 38 | 117 | 124 | 0 |
| self-driving lab/robotics/automation | 337 | 3 | 0 | 0 | 1 | 2 | 1 | 0 | 2 | 5 | 10 | 9 | 23 | 35 | 33 | 44 | 76 | 93 | 0 |
| solubility/Flory-Huggins/glass transition | 255 | 5 | 0 | 1 | 6 | 0 | 4 | 1 | 3 | 4 | 6 | 10 | 20 | 27 | 23 | 45 | 50 | 50 | 0 |
| polymer informatics/materials informatics | 190 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 2 | 3 | 2 | 3 | 18 | 22 | 29 | 25 | 36 | 48 | 0 |
| 3D printing/additive manufacturing | 170 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 2 | 6 | 2 | 17 | 15 | 33 | 51 | 43 | 0 |
| high-throughput screening | 161 | 0 | 0 | 1 | 1 | 1 | 1 | 0 | 0 | 1 | 10 | 6 | 13 | 16 | 20 | 21 | 30 | 40 | 0 |
| physics-informed | 143 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 1 | 3 | 4 | 12 | 13 | 38 | 71 | 0 |
| reinforcement learning/active learning/bayesian optimization | 138 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 2 | 2 | 3 | 3 | 6 | 8 | 10 | 24 | 35 | 43 | 1 |
| transfer learning/few-shot/pretraining | 134 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 1 | 2 | 10 | 15 | 11 | 31 | 26 | 37 | 0 |
| generative/VAE/GAN/diffusion | 112 | 0 | 1 | 2 | 0 | 0 | 1 | 0 | 1 | 0 | 1 | 5 | 8 | 8 | 14 | 13 | 28 | 29 | 1 |
| thermal conductivity | 96 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 1 | 5 | 10 | 5 | 17 | 25 | 31 | 0 |
| agent/agentic | 94 | 0 | 2 | 2 | 2 | 1 | 0 | 0 | 5 | 0 | 2 | 3 | 10 | 7 | 6 | 14 | 16 | 24 | 0 |
| GNN/graph | 89 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 2 | 8 | 11 | 16 | 25 | 26 | 0 |
| inverse design/de novo | 84 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 2 | 0 | 3 | 2 | 3 | 11 | 15 | 10 | 13 | 24 | 0 |
| transformer/LLM/foundation model | 67 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 2 | 2 | 11 | 22 | 29 | 0 |

时间线可读出的阶段：

- **2010–2018（基数小）**：以 `neural network` 为唯一稳定词项（2010 年 26 条中 25 条命中），`machine learning` 与 `deep learning` 尚少。这一阶段是神经网络用于高分子建模的早期。
- **2019–2021（方法扩散）**：`machine learning` 从 38（2019）升至 120（2021），`deep learning` 从 6 升至 31，`polymer informatics/materials informatics` 在 2021 年达到 18，`representation/SMILES/descriptor/fingerprint` 达到 24。
- **2022–2024（规模化与任务分化）**：`machine learning` 171→221→346，`mechanical properties` 50→63→72，`molecular dynamics/DFT/coarse-grained` 30→35→54，`dielectric/energy storage` 27→37→55，`sustainability` 19→19→38，`3D printing` 17→15→33。
- **2025–2026（新范式出现）**：`transformer/LLM/foundation model` 从 2023 年 2 条升至 2024 年 11、2025 年 22、2026 年 29；`agent/agentic` 2024 年 14、2026 年 24；`physics-informed` 2025 年 38、2026 年 71；`generative/VAE/GAN/diffusion` 2025 年 28、2026 年 29。绝对量仍小（合计 67–112 条），但增速高于整体。

按占比看（该年命中数／该年记录数）：`machine learning` 从 2019 年 42.2% 升至 2025 年 71.8%，已接近语料上限；而 `transformer/LLM/foundation model` 2026 年约 4.3%、`agent/agentic` 约 3.5%、`generative` 约 4.3%，说明新范式在高分子语料中仍处早期。逐年占比矩阵见 [`wos-summary.md`](wos-summary.md#主题逐年占比)。

## 高被引论文

按 `TC`（Web of Science 被引次数）排序前 20：

| 排名 | 被引 | 年份 | 标题 | 期刊 | DOI |
|---|---|---|---|---|---|
| 1 | 666 | 2022 | Recent Progress and Future Prospects on All-Organic Polymer Dielectrics for Energy Storage Capacitors | CHEMICAL REVIEWS | 10.1021/acs.chemrev.1c00793 |
| 2 | 608 | 2018 | A review on machinability of carbon fiber reinforced polymer (CFRP) and glass fiber reinforced polymer (GFRP) composite materials | DEFENCE TECHNOLOGY | 10.1016/j.dt.2018.02.001 |
| 3 | 521 | 2019 | Machine-learning-assisted discovery of polymers with high thermal conductivity using a molecular design algorithm | NPJ COMPUTATIONAL MATERIALS | 10.1038/s41524-019-0203-2 |
| 4 | 432 | 2018 | Polymer Genome: A Data-Powered Polymer Informatics Platform for Property Predictions | JOURNAL OF PHYSICAL CHEMISTRY C | 10.1021/acs.jpcc.8b02913 |
| 5 | 359 | 2019 | Accelerated Discovery of Organic Polymer Photocatalysts for Hydrogen Evolution from Water through the Integration of Experiment and Theory | JOURNAL OF THE AMERICAN CHEMICAL SOCIETY | 10.1021/jacs.9b03591 |
| 6 | 313 | 2019 | Phase-field modeling and machine learning of electric-thermal-mechanical breakdown of polymer-based dielectrics | NATURE COMMUNICATIONS | 10.1038/s41467-019-09874-8 |
| 7 | 281 | 2017 | Polymer Informatics: Opportunities and Challenges | ACS MACRO LETTERS | 10.1021/acsmacrolett.7b00228 |
| 8 | 258 | 2016 | Machine Learning Strategy for Accelerated Design of Polymer Dielectrics | SCIENTIFIC REPORTS | 10.1038/srep20952 |
| 9 | 251 | 2014 | Polymer memristor for information storage and neuromorphic applications | MATERIALS HORIZONS | 10.1039/c4mh00067f |
| 10 | 248 | 2022 | A biomimetic elastomeric robot skin using electrical impedance and acoustic tomography for tactile sensing | SCIENCE ROBOTICS | 10.1126/scirobotics.abm7187 |
| 11 | 248 | 2021 | Polymer informatics: Current status and critical next steps | MATERIALS SCIENCE & ENGINEERING R-REPORTS | 10.1016/j.mser.2020.100595 |
| 12 | 246 | 2020 | Designing exceptional gas-separation polymer membranes using machine learning | SCIENCE ADVANCES | 10.1126/sciadv.aaz4301 |
| 13 | 234 | 2020 | Machine-learning predictions of polymer properties with Polymer Genome | JOURNAL OF APPLIED PHYSICS | 10.1063/5.0023759 |
| 14 | 231 | 2019 | Critical Assessment of the Hildebrand and Hansen Solubility Parameters for Polymers | JOURNAL OF CHEMICAL INFORMATION AND MODELING | 10.1021/acs.jcim.9b00656 |
| 15 | 224 | 2020 | Recent advances in rational design of polymer nanocomposite dielectrics for energy storage | NANO ENERGY | 10.1016/j.nanoen.2020.104844 |
| 16 | 212 | 2018 | Computer-Aided Screening of Conjugated Polymers for Organic Solar Cell: Classification by Random Forest | JOURNAL OF PHYSICAL CHEMISTRY LETTERS | 10.1021/acs.jpclett.8b00635 |
| 17 | 211 | 2024 | Design of functional and sustainable polymers assisted by artificial intelligence | NATURE REVIEWS MATERIALS | 10.1038/s41578-024-00708-8 |
| 18 | 210 | 2021 | Benchmarking Machine Learning Models for Polymer Informatics: An Example of Glass Transition Temperature | JOURNAL OF CHEMICAL INFORMATION AND MODELING | 10.1021/acs.jcim.1c01031 |
| 19 | 208 | 2022 | Machine learning enables interpretable discovery of innovative polymers for gas separation membranes | SCIENCE ADVANCES | 10.1126/sciadv.abn9545 |
| 20 | 206 | 2021 | Polymer design using genetic algorithm and machine learning | COMPUTATIONAL MATERIALS SCIENCE | 10.1016/j.commatsci.2020.110067 |

高被引集合以两类文献为主：介电／储能与膜分离的功能高分子（第 1、6、8、12、15、19 条）和综述／平台（第 4、7、11 条 Polymer Genome 与聚合物信息学）。纯方法类高被引集中在遗传算法（第 20 条）、随机森林（第 16 条）与热导率分子设计（第 3 条），与关键词共现的“通用 ML 方法 + 具体材料问题”结构一致。

## 对本书章节的启示

下表把主题聚类映射到 16 章框架。主题计数来自上文；标注“直接证据弱”的章节在本语料中缺少独立词项，需要借助语料外的文献或案例补足。

| 章 | 主题 | 本语料证据 |
|---|---|---|
| 1 绪论：AI4Polymer 范式与本书结构 | machine learning、polymer informatics | machine learning 1970（62.0%）；polymer/materials informatics 190；综述高被引集中于此 |
| 2 高分子表示与描述符 | representation/SMILES/descriptor/fingerprint | 510；2026 年 139，为增长最快的主题之一 |
| 3 数据、数据库与基准 | 数据工程与基准（无独立词项） | 直接证据弱；Keywords-Plus 中 design 230、prediction 229 反映任务而非数据；Polymer Genome 类平台可作案例 |
| 4 高分子物理与结构—性能关系 | solubility/Flory-Huggins/glass transition | 255；glass transition temperature 关键词 24，且与 machine learning 共现 14 |
| 5 分子模拟与多尺度建模 | molecular dynamics/DFT/coarse-grained | 347；2025 年 79、2026 年 77 |
| 6 性能预测 | mechanical properties、thermal conductivity、dielectric/energy storage/battery/electrolyte | 534 / 96 / 363；mechanical-properties 在 Keywords-Plus 中 134 |
| 7 多任务、迁移与物理约束学习 | transfer learning/few-shot/pretraining、physics-informed | 134 / 143；physics-informed 2025 年 38、2026 年 71 |
| 8 表征与图像分析 | 表征／成像（无独立词项） | 直接证据弱；Instruments & Instrumentation（WC 120）为最接近的分类 |
| 9 生成模型与序列设计 | generative/VAE/GAN/diffusion、GNN/graph | 112 / 89；2025–2026 年显著上升 |
| 10 逆向设计与从头设计 | inverse design/de novo | 84；2026 年 24，为历史最高 |
| 11 主动学习、贝叶斯优化与强化学习 | reinforcement learning/active learning/bayesian optimization | 138；bayesian optimization 关键词 23 |
| 12 反应预测与可合成性 | 反应／可合成性（无独立词项） | 直接证据弱；语料以性质预测与设计为主，该章需外部证据 |
| 13 自驱动实验室与自动化 | self-driving lab/robotics/automation | 337；additive manufacturing 关键词 52、3d printing 35 |
| 14 基础模型与智能体 | transformer/LLM/foundation model、agent/agentic | 67 / 94；2024 年后开始出现，2026 年分别为 29、24 |
| 15 可持续高分子 | sustainability/recycling/biodegradation | 338；2025 年 117、2026 年 124，近两年跃升 |
| 16 端到端案例与展望 | high-throughput screening、membrane/separation、3D printing | 161 / 375 / 170；高被引中膜分离与介电储能案例集中 |

由此得到三条编写判断：

1. **性质预测与设计是成熟主线**，第 4–6、9–11 章有充足语料；表示与描述符（第 2 章）在 2024–2026 年快速增长，应作为方法章节的基础。
2. **新范式（LLM／基础模型／智能体／生成模型）仍在早期**（合计 67–112 条），第 9、14 章应以机制与边界讨论为主，避免夸大成熟度。
3. **表征成像与反应预测在本语料中证据最弱**（第 8、12 章），若成章需明确标注证据来源在检索式覆盖范围之外。

## 数据质量

- `DE` 缺失 763 条（3178 中 24.0%），`ID` 缺失 461 条，`DI` 缺失 100 条，`C1` 缺失 4 条，`WC`／`SC` 各缺失 5 条；`AB`、`PY`、`TC` 无缺失。
- 大小写归一后有 831 个作者关键词存在多种原始拼写（如 machine learning / Machine learning / Machine Learning；artificial intelligence 有 4 种）。本调研对 `DE`／`ID` 统一小写计数，展示时取出现最多的原始拼写；`artificial neural network` 与 `artificial neural networks`、`ann`、`artificial neural network (ann)` 等同义变体未合并，实际方法词频高于表中单词项。
- 导出文件内部 `DA`（date added）字段全部为 2026-09-16，晚于检索式所记的 access date 2026-04-21；本文以 2026-04-21 为准，但 2026／2027 年计数应视为不完整。
- 国家从 `C1` 地址尾段解析：England／Scotland／Wales／North Ireland 合并为 United Kingdom；香港地址尾段多为 `Peoples R China`，因此计入 China，未单列。
- 主题计数基于正则词项匹配，各主题不互斥，且部分正则较宽（如 `uncertainty/interpretability/SHAP` 含 `uncertaint`、`black-box`；`representation` 含 `embedding`），应作为趋势指标而非精确分类。
- 逐年合计 3178 与记录总数一致；脚本运行时会打印该一致性检查（`year_sum_ok=True`）。
