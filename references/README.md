# 本地参考资料库

本书正文引用的原始论文、综述、数据集与官方文档按章登记于此。每条来源先在 `sources.tsv` 登记，再由 `fetch.py` 下载、生成可搜索文本并写入 `manifest.json`。

当前清单 289 项：已取得正文 227 项，其中 PDF 199 份。其余项目的获取状态见文末。

[来源清单](sources.tsv) · [下载与校验记录](manifest.json) · [待补充清单](NEEDED.md) · [本地索引](index.md)

PDF 原件位于 `files/`，可搜索文本位于 `text/`。网页同时保存原始 HTML 与离线文本。不得把网页入口记作规范全文。

`manifest.json` 记录获取时间、来源地址、校验值、字节数、PDF 页数及可从正文识别出的 arXiv 版本。网页按本地文件的 SHA-256 固定快照；下载完成不代表已经逐页审阅。

`user_provided` 表示作者提供的原件，保留原文件名并记录校验值。清单中的 `local:` 地址只用于读取本资料库内的文件，不发起网络请求。

`landing_only` 是索引入口，`incomplete_text` 表示未取得完整正文，`access_required` 表示来源要求机构访问，`failed` 表示请求失败。

## 第 1 章 初识 AI4Polymer

| 资料 | 本地文件 | 用途 |
| --- | --- | --- |
| [Web of Science 检索导出：AI 驱动高分子材料 2010–2027](https://www.webofscience.com/) | [原件](wos/README.md) · [文本](text/wos-ai4polymer-export.txt)（user_provided） | 3178 条记录的元数据导出，检索式、文件清单与访问日期见 references/wos/README.md |
| [AI4Polymer：AI 驱动高分子材料研究资源清单](https://github.com/ShiqianTan/AI4Polymer) | [原件](files/documents/ai4polymer-awesome-list.html) · [文本](text/ai4polymer-awesome-list.txt) | 领域资源分类：设计发现、性质预测、AI 方法、数据与工具 |
| [Polymer Informatics: Opportunities and Challenges](https://pubs.acs.org/doi/10.1021/acsmacrolett.6b00936) | 未获取（failed） | 高分子信息学奠基综述 |
| [Polymer Genome: A Data-Powered Polymer Informatics Platform for Property Predictions](https://pubs.acs.org/doi/10.1021/acs.jpcc.8b02913) | 未获取（failed） | 多性质预测平台与描述符体系 |
| [Polymer Informatics: Current Status and Critical Next Steps](https://www.sciencedirect.com/science/article/pii/S0927796X20300613) | [原件](files/papers/polymer-informatics-next-2021.html) · [文本](text/polymer-informatics-next-2021.txt)（incomplete_text） | 数据、表示与可迁移性的关键问题 |
| [Extended-Connectivity Fingerprints](https://pubs.acs.org/doi/10.1021/ci100050t) | 未获取（failed） | ECFP/Morgan 指纹定义 |
| [Mordred: a molecular descriptor calculator](https://jcheminf.biomedcentral.com/articles/10.1186/s13321-018-0258-y) | [原件](files/papers/mordred-2018.html) · [文本](text/mordred-2018.txt) | 二维描述符集合 |
| [PolyBERT: a chemical language model to enable fully machine-driven ultrafast polymer informatics](https://www.nature.com/articles/s41467-023-39868-6) | [原件](files/papers/polybert-2023.pdf) · [文本](text/polybert-2023.txt) | 聚合物语言模型与表示 |
| [Neural Message Passing for Quantum Chemistry](https://arxiv.org/abs/1704.01212) | [原件](files/papers/mpnn-2017.pdf) · [文本](text/mpnn-2017.txt) | 消息传递图神经网络 |
| [SchNet: A continuous-filter convolutional neural network for modeling quantum interactions](https://arxiv.org/abs/1706.08566) | [原件](files/papers/schnet-2017.pdf) · [文本](text/schnet-2017.txt) | 等变/连续滤波网络 |
| [E(3)-equivariant graph neural networks for data-efficient and accurate interatomic potentials](https://www.nature.com/articles/s41467-022-29939-5) | [原件](files/papers/nequip-2022.pdf) · [文本](text/nequip-2022.txt) | 等变力场 |
| [PI1M: A Benchmark Database for Polymer Informatics](https://pubs.acs.org/doi/10.1021/acs.jcim.0c00726) | 未获取（failed） | 百万级聚合物虚拟库 |
| [A self-driving laboratory for accelerated discovery of thin-film materials](https://www.science.org/doi/10.1126/sciadv.aaz8867) | 未获取（failed） | 自驱动实验室案例 |
| [Autonomous experimentation systems for materials development](https://www.nature.com/articles/s41578-023-00587-5) | [原件](files/papers/self-driving-lab-review-2023.html) · [文本](text/self-driving-lab-review-2023.txt)（access_required） | 自主实验系统综述 |
| [An autonomous laboratory for the accelerated synthesis of novel materials](https://www.nature.com/articles/s41586-023-06734-w) | [原件](files/papers/alab-2023.html) · [文本](text/alab-2023.txt)（access_required） | A-Lab 自主合成 |
| [Autonomous chemical research with large language models](https://www.nature.com/articles/s41586-023-06792-0) | [原件](files/papers/coscientist-2023.html) · [文本](text/coscientist-2023.txt)（access_required） | LLM 驱动的自主化学研究 |
| [ChemCrow: Augmenting large-language models with chemistry tools](https://www.science.org/doi/10.1126/sciadv.adk1059) | 未获取（failed） | 化学工具调用智能体 |
| [Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks](https://arxiv.org/abs/2005.11401) | [原件](files/papers/rag-2020.pdf) · [文本](text/rag-2020.txt) | 检索增强生成 |
| [ChemBERTa: Large-Scale Self-Supervised Pretraining for Molecular Property Prediction](https://arxiv.org/abs/2010.09885) | [原件](files/papers/chemberta-2022.pdf) · [文本](text/chemberta-2022.txt) | 字符串自监督预训练表示 |
| [TransPolymer: a Transformer-based language model for polymer property predictions](https://www.nature.com/articles/s41524-023-01016-5) | [原件](files/papers/transpolymer-2023.pdf) · [文本](text/transpolymer-2023.txt) | 聚合物 Transformer 表示与预训练 |
| [Second-Order Transition Temperatures and Related Properties of Polystyrene](https://pubs.aip.org/aip/jap/article-abstract/21/6/581/158211) | 未获取（failed） | Fox–Flory 关系的原始工作（领域定位，订阅来源） |
| [A foundation model for atomistic materials chemistry](https://arxiv.org/abs/2401.00096) | [原件](files/papers/mace-mp-0-2023.pdf) · [文本](text/mace-mp-0-2023.txt) | 通用基础势：MACE-MP-0 与跨材料迁移 |
| [Auto-Encoding Variational Bayes](https://arxiv.org/abs/1312.6114) | [原件](files/papers/vae-2013.pdf) · [文本](text/vae-2013.txt) | 变分自编码器、重参数化与证据下界 |
| [Generative Adversarial Networks](https://arxiv.org/abs/1406.2661) | [原件](files/papers/gan-2014.pdf) · [文本](text/gan-2014.txt) | 生成对抗网络与对抗训练 |
| [Denoising Diffusion Probabilistic Models](https://arxiv.org/abs/2006.11239) | [原件](files/papers/ddpm-2020.pdf) · [文本](text/ddpm-2020.txt) | 去噪扩散概率模型与噪声预测目标 |
| [AI-guided inverse design and discovery of recyclable vitrimeric polymers](https://arxiv.org/abs/2312.03690) | [原件](files/papers/vitrimer-inverse-2023.pdf) · [文本](text/vitrimer-inverse-2023.txt) | 可回收聚合物的生成式逆向设计 |
| [On-the-fly closed-loop materials discovery via Bayesian active learning](https://www.nature.com/articles/s41467-020-19597-w) | [原件](files/papers/kusne-2020.html) · [文本](text/kusne-2020.txt)（access_required） | 闭环主动学习与实验回流（开放获取） |
| [Attention Is All You Need](https://arxiv.org/abs/1706.03762) | [原件](files/papers/transformer-2017.pdf) · [文本](text/transformer-2017.txt) | Transformer：自注意力架构 |
| [Machine learning enables interpretable discovery of innovative polymers for gas separation membranes](https://doi.org/10.1126/sciadv.abn9545) | [原件](files/papers/polymer-gas-membrane-ml-2022.md) · [文本](text/polymer-gas-membrane-ml-2022.txt) | 气体分离膜渗透率数据仓库与可解释机器学习 |
| [Retrieval-Augmented Generation for Large Language Models: A Survey](https://arxiv.org/abs/2312.10997) | [原件](files/papers/rag-survey-2023.pdf) · [文本](text/rag-survey-2023.txt) | 检索增强生成综述 |

## 第 2 章 高分子表示与描述符

| 资料 | 本地文件 | 用途 |
| --- | --- | --- |
| [AI4Polymer：AI 驱动高分子材料研究资源清单](https://github.com/ShiqianTan/AI4Polymer) | [原件](files/documents/ai4polymer-awesome-list.html) · [文本](text/ai4polymer-awesome-list.txt) | 领域资源分类：设计发现、性质预测、AI 方法、数据与工具 |
| [Polymer Genome: A Data-Powered Polymer Informatics Platform for Property Predictions](https://pubs.acs.org/doi/10.1021/acs.jpcc.8b02913) | 未获取（failed） | 多性质预测平台与描述符体系 |
| [SMILES, a chemical language and information system](https://pubs.acs.org/doi/10.1021/ci00057a005) | 未获取（failed） | 字符串表示的原始工作 |
| [BigSMILES: A Structurally-Based Line Notation for Describing Macromolecules](https://pubs.acs.org/doi/10.1021/acscentsci.9b00476) | 未获取（failed） | 随机结构高分子的字符串表示 |
| [Extended-Connectivity Fingerprints](https://pubs.acs.org/doi/10.1021/ci100050t) | 未获取（failed） | ECFP/Morgan 指纹定义 |
| [Mordred: a molecular descriptor calculator](https://jcheminf.biomedcentral.com/articles/10.1186/s13321-018-0258-y) | [原件](files/papers/mordred-2018.html) · [文本](text/mordred-2018.txt) | 二维描述符集合 |
| [PolyBERT: a chemical language model to enable fully machine-driven ultrafast polymer informatics](https://www.nature.com/articles/s41467-023-39868-6) | [原件](files/papers/polybert-2023.pdf) · [文本](text/polybert-2023.txt) | 聚合物语言模型与表示 |
| [PI1M: A Benchmark Database for Polymer Informatics](https://pubs.acs.org/doi/10.1021/acs.jcim.0c00726) | 未获取（failed） | 百万级聚合物虚拟库 |
| [RDKit: Open-source cheminformatics](https://www.rdkit.org/) | [原件](files/documents/rdkit-tools.html) · [文本](text/rdkit-tools.txt) | 指纹、描述符与分子处理 |
| [Self-Referencing Embedded Strings (SELFIES): A 100% robust molecular string representation](https://arxiv.org/abs/1905.13741) | [原件](files/papers/selfies-2020.pdf) · [文本](text/selfies-2020.txt) | 机器学习可用的鲁棒字符串表示 |
| [MoleculeNet: A Benchmark for Molecular Machine Learning](https://pubs.rsc.org/en/content/articlelanding/2018/sc/c7sc02664a) | [原件](files/papers/moleculenet-2018.pdf) · [文本](text/moleculenet-2018.txt) | 小分子基准与划分策略 |
| [ChemBERTa: Large-Scale Self-Supervised Pretraining for Molecular Property Prediction](https://arxiv.org/abs/2010.09885) | [原件](files/papers/chemberta-2022.pdf) · [文本](text/chemberta-2022.txt) | 字符串自监督预训练表示 |
| [Weisfeiler-Lehman Graph Kernels](https://www.jmlr.org/papers/v12/shervashidze11a.html) | [原件](files/papers/wl-graph-kernel-2011.pdf) · [文本](text/wl-graph-kernel-2011.txt) | 迭代图核与消息传递的理论前身 |
| [TransPolymer: a Transformer-based language model for polymer property predictions](https://www.nature.com/articles/s41524-023-01016-5) | [原件](files/papers/transpolymer-2023.pdf) · [文本](text/transpolymer-2023.txt) | 聚合物 Transformer 表示与预训练 |
| [Most Ligand-Based Classification Benchmarks Reward Memorization Rather than Generalization](https://pubs.acs.org/doi/10.1021/acs.jcim.8b00025) | [原件](files/papers/scaffold-memorization-2018.pdf) · [文本](text/scaffold-memorization-2018.txt) | 随机划分高估性能与去泄漏 |
| [A graph representation of molecular ensembles for polymer property prediction](https://arxiv.org/abs/2205.08619) | [原件](files/papers/polymer-ensemble-gnn-2022.pdf) · [文本](text/polymer-ensemble-gnn-2022.txt) | 聚合物集合图表示 |
| [Polymer informatics at-scale with multitask graph neural networks](https://arxiv.org/abs/2209.13557) | [原件](files/papers/polymer-multitask-gnn-2023.pdf) · [文本](text/polymer-multitask-gnn-2023.txt) | 多任务图网络与大规模筛选 |
| [Geometric Deep Learning: Grids, Groups, Graphs, Geodesics, and Gauges](https://arxiv.org/abs/2104.13478) | [原件](files/papers/geometric-deep-learning-2021.pdf) · [文本](text/geometric-deep-learning-2021.txt) | 几何深度学习的对称性与不变性框架 |
| [Potentials and challenges of polymer informatics: exploiting machine learning for polymer design](https://arxiv.org/abs/2010.07683) | [原件](files/papers/polymer-informatics-challenges-2020.pdf) · [文本](text/polymer-informatics-challenges-2020.txt) | 高分子信息学的表示与数据挑战综述 |
| [Mol2vec: Unsupervised Machine Learning Approach with Chemical Intuition](https://pubs.acs.org/doi/10.1021/acs.jcim.7b00616) | 未获取（failed） | 子结构嵌入表示 |
| [The Generation of a Unique Machine Description for Chemical Structures](https://pubs.acs.org/doi/10.1021/c160017a018) | 未获取（failed） | 拓扑指纹的早期工作 |

## 第 3 章 数据、基准与可复现性

| 资料 | 本地文件 | 用途 |
| --- | --- | --- |
| [Web of Science 检索导出：AI 驱动高分子材料 2010–2027](https://www.webofscience.com/) | [原件](wos/README.md) · [文本](text/wos-ai4polymer-export.txt)（user_provided） | 3178 条记录的元数据导出，检索式、文件清单与访问日期见 references/wos/README.md |
| [AI4Polymer：AI 驱动高分子材料研究资源清单](https://github.com/ShiqianTan/AI4Polymer) | [原件](files/documents/ai4polymer-awesome-list.html) · [文本](text/ai4polymer-awesome-list.txt) | 领域资源分类：设计发现、性质预测、AI 方法、数据与工具 |
| [Polymer Informatics: Current Status and Critical Next Steps](https://www.sciencedirect.com/science/article/pii/S0927796X20300613) | [原件](files/papers/polymer-informatics-next-2021.html) · [文本](text/polymer-informatics-next-2021.txt)（incomplete_text） | 数据、表示与可迁移性的关键问题 |
| [Benchmarking machine learning models for polymer informatics: glass transition temperature](https://pubs.acs.org/doi/10.1021/acs.jcim.0c01336) | 未获取（failed） | Tg 预测基准与数据划分 |
| [PoLyInfo polymer database](https://polymer.nims.go.jp/) | [原件](files/datasets/polyinfo-2021.html) · [文本](text/polyinfo-2021.txt) | 实验与计算聚合物性质数据库 |
| [PI1M: A Benchmark Database for Polymer Informatics](https://pubs.acs.org/doi/10.1021/acs.jcim.0c00726) | 未获取（failed） | 百万级聚合物虚拟库 |
| [Open Macromolecular Genome](https://github.com/TheJacksonLab/OpenMacromolecularGenome) | [原件](files/datasets/open-macromolecular-genome.html) · [文本](text/open-macromolecular-genome.txt) | 可合成聚合物的开放基因组 |
| [SMiPoly: Generation of a Synthesizable Polymer Virtual Library](https://pubs.acs.org/doi/10.1021/acs.jcim.3c00277) | 未获取（failed） | 可合成虚拟库生成 |
| [NeurIPS Open Polymer Prediction 2025](https://www.kaggle.com/competitions/neurips-open-polymer-prediction-2025) | [原件](files/datasets/kaggle-polymer-2025.html) · [文本](text/kaggle-polymer-2025.txt)（incomplete_text） | 多性质预测竞赛与盲测 |
| [MoleculeNet: A Benchmark for Molecular Machine Learning](https://pubs.rsc.org/en/content/articlelanding/2018/sc/c7sc02664a) | [原件](files/papers/moleculenet-2018.pdf) · [文本](text/moleculenet-2018.txt) | 小分子基准与划分策略 |
| [Most Ligand-Based Classification Benchmarks Reward Memorization Rather than Generalization](https://pubs.acs.org/doi/10.1021/acs.jcim.8b00025) | [原件](files/papers/scaffold-memorization-2018.pdf) · [文本](text/scaffold-memorization-2018.txt) | 随机划分高估性能与去泄漏 |
| [POINT2: A Polymer Informatics Training and Testing Database](https://arxiv.org/abs/2503.23491) | [原件](files/papers/point2-2025.pdf) · [文本](text/point2-2025.txt) | 多性质训练/测试基准与划分 |
| [Open Polymer Challenge: Post-Competition Report](https://arxiv.org/abs/2512.08896) | [原件](files/papers/open-polymer-challenge-2025.pdf) · [文本](text/open-polymer-challenge-2025.txt) | 竞赛赛后报告与基准记录 |
| [Leakage and the Reproducibility Crisis in ML-based Science](https://arxiv.org/abs/2207.07048) | [原件](files/papers/kapoor-narayanan-2023.pdf) · [文本](text/kapoor-narayanan-2023.txt) | 数据泄漏与复现危机 |
| [Benchmarking Materials Property Prediction Methods: The Matbench Test Set and Automatminer Reference Algorithm](https://arxiv.org/abs/2005.00707) | [原件](files/papers/matbench-2020.pdf) · [文本](text/matbench-2020.txt) | 材料基准的测试集与划分 |
| [Deep Learning Scaling is Predictable, Empirically](https://arxiv.org/abs/1712.00409) | [原件](files/papers/hestness-2017.pdf) · [文本](text/hestness-2017.txt) | 幂律学习曲线的经验形式 |
| [A Constructive Prediction of the Generalization Error Across Scales](https://arxiv.org/abs/1909.12673) | [原件](files/papers/rosenfeld-2020.pdf) · [文本](text/rosenfeld-2020.txt) | 跨尺度泛化误差预测 |
| [A survey of cross-validation procedures for model selection](https://arxiv.org/abs/0907.4728) | [原件](files/papers/arlot-celisse-2010.pdf) · [文本](text/arlot-celisse-2010.txt) | 交叉验证与模型选择 |
| [DOME: Recommendations for supervised machine learning validation in biology](https://arxiv.org/abs/2006.16189) | [原件](files/papers/dome-2021.pdf) · [文本](text/dome-2021.txt) | 监督学习报告规范 |
| [Improving Reproducibility in Machine Learning Research](https://arxiv.org/abs/2003.12206) | [原件](files/papers/neurips-reproducibility-2020.pdf) · [文本](text/neurips-reproducibility-2020.txt) | 复现性检查表与实践 |
| [The FAIR Guiding Principles for scientific data management and stewardship](https://www.nature.com/articles/sdata201618) | [原件](files/documents/fair-principles-2016.html) · [文本](text/fair-principles-2016.txt)（access_required） | 数据可发现、可访问、可互操作、可复用原则 |
| [Datasheets for Datasets](https://arxiv.org/abs/1803.09010) | [原件](files/papers/datasheets-datasets-2018.pdf) · [文本](text/datasheets-datasets-2018.txt) | 数据集文档规范 |
| [In Search of Lost Domain Generalization](https://arxiv.org/abs/2007.01434) | [原件](files/papers/domainbed-2021.pdf) · [文本](text/domainbed-2021.txt) | 分布偏移下的评测协议 |
| [Show Your Work: Improved Reporting of Experimental Results](https://arxiv.org/abs/1909.03004) | [原件](files/papers/show-your-work-2019.pdf) · [文本](text/show-your-work-2019.txt) | 误差棒与结果选择 |
| [Understanding deep learning requires rethinking generalization](https://arxiv.org/abs/1611.03530) | [原件](files/papers/rethinking-generalization-2017.pdf) · [文本](text/rethinking-generalization-2017.txt) | 记忆与外推的对照 |
| [Scikit-learn: Machine Learning in Python](https://www.jmlr.org/papers/v12/pedregosa11a.html) | [原件](files/papers/scikit-learn-2011.html) · [文本](text/scikit-learn-2011.txt) | Python 机器学习工具与实现细节 |

## 第 4 章 高分子物理与结构–性能关系

| 资料 | 本地文件 | 用途 |
| --- | --- | --- |
| [Polymer dielectrics for high-temperature capacitive energy storage](https://pubs.acs.org/doi/10.1021/acs.chemrev.1c00968) | 未获取（failed） | 介电储能综述，被引最高的领域文献 |
| [Benchmarking machine learning models for polymer informatics: glass transition temperature](https://pubs.acs.org/doi/10.1021/acs.jcim.0c01336) | 未获取（failed） | Tg 预测基准与数据划分 |
| [Prediction of Hansen solubility parameters using machine learning](https://pubs.acs.org/doi/10.1021/acs.jcim.9b00485) | 未获取（failed） | 溶解度参数与 QSPR |
| [POINT2: A Polymer Informatics Training and Testing Database](https://arxiv.org/abs/2503.23491) | [原件](files/papers/point2-2025.pdf) · [文本](text/point2-2025.txt) | 多性质训练/测试基准与划分 |
| [Open Polymer Challenge: Post-Competition Report](https://arxiv.org/abs/2512.08896) | [原件](files/papers/open-polymer-challenge-2025.pdf) · [文本](text/open-polymer-challenge-2025.txt) | 竞赛赛后报告与基准记录 |
| [Assessing and Improving Machine Learning Model Predictions of Polymer Glass Transition Temperatures](https://arxiv.org/abs/1908.02398) | [原件](files/papers/tg-ml-assess-2019.pdf) · [文本](text/tg-ml-assess-2019.txt) | Tg 数据质量与模型评估 |
| [Explainability and Transferability of Machine Learning Models for Predicting the Glass Transition Temperature of Polymers](https://arxiv.org/abs/2308.09898) | [原件](files/papers/tg-ml-explain-2023.pdf) · [文本](text/tg-ml-explain-2023.txt) | Tg 模型的可解释性与迁移 |
| [Determination of Glass Transition Temperature of Polyimides from Atomistic Molecular Dynamics Simulations and Machine-Learning Algorithms](https://arxiv.org/abs/2001.08889) | [原件](files/papers/polyimide-tg-md-ml-2020.pdf) · [文本](text/polyimide-tg-md-ml-2020.txt) | 模拟标签与 Tg 预测 |
| [Dynamics and Stress Relaxation of Bidisperse Polymer Melts with Unentangled and Moderately Entangled Chains](https://arxiv.org/abs/2104.05020) | [原件](files/papers/bidisperse-melts-2021.pdf) · [文本](text/bidisperse-melts-2021.txt) | 分子量分布与应力松弛 |
| [Evolution of Free Volume Elements in Amorphous Polymers Undergoing Uniaxial Deformation: a Molecular Dynamics Simulation Study](https://arxiv.org/abs/2307.12460) | [原件](files/papers/free-volume-deformation-2023.pdf) · [文本](text/free-volume-deformation-2023.txt) | 形变下的自由体积演化 |
| [Artificial Neural Networks for Predicting Mechanical Properties of Crystalline Polyamide12 via Molecular Dynamics Simulations](https://arxiv.org/abs/2307.10139) | [原件](files/papers/mech-props-ann-md-2023.pdf) · [文本](text/mech-props-ann-md-2023.txt) | 力学性质的模拟与学习 |
| [Superior Polymeric Gas Separation Membrane Designed by Explainable Graph Machine Learning](https://arxiv.org/abs/2404.10903) | [原件](files/papers/gas-separation-gnn-2024.pdf) · [文本](text/gas-separation-gnn-2024.txt) | 可解释图学习与气体分离膜 |
| [Structure, Dynamics and Hydrogen Transport in Amorphous Polymers: An Analysis of the Interplay Between Free Volume Element Distribution and Local Segmental Dynamics](https://arxiv.org/abs/2209.09142) | [原件](files/papers/free-volume-hydrogen-2022.pdf) · [文本](text/free-volume-hydrogen-2022.txt) | 自由体积与输运的分子模拟 |
| [Exploring high thermal conductivity polymers via interpretable machine learning with physical descriptors](https://arxiv.org/abs/2301.03030) | [原件](files/papers/thermal-cond-interpretable-2023.pdf) · [文本](text/thermal-cond-interpretable-2023.txt) | 物理描述符与可解释模型 |
| [Tutorial: AI-assisted exploration and active design of polymers with high intrinsic thermal conductivity](https://arxiv.org/abs/2403.15887) | [原件](files/papers/thermal-cond-tutorial-2024.pdf) · [文本](text/thermal-cond-tutorial-2024.txt) | 热导设计的方法流程 |
| [Machine Learning-Assisted Exploration of Thermally Conductive Polymers Based on High-Throughput Molecular Dynamics Simulations](https://arxiv.org/abs/2109.02794) | [原件](files/papers/thermal-cond-md-2021.pdf) · [文本](text/thermal-cond-md-2021.txt) | 高通量模拟与热导预测 |
| [Graph Convolutional Neural Networks for Polymers Property Prediction](https://arxiv.org/abs/1811.06231) | [原件](files/papers/graph-cnn-polymer-2018.pdf) · [文本](text/graph-cnn-polymer-2018.txt) | 图表示与性质预测 |
| [Polymer Informatics: Current Status and Critical Next Steps](https://arxiv.org/abs/2011.00508) | [原件](files/papers/polymer-informatics-next-arxiv-2020.pdf) · [文本](text/polymer-informatics-next-arxiv-2020.txt) | 数据、表示与可迁移性的关键问题（arXiv 版） |
| [Second-Order Transition Temperatures and Related Properties of Polystyrene](https://pubs.aip.org/aip/jap/article-abstract/21/6/581/158211) | 未获取（failed） | Fox–Flory 关系的原始工作（领域定位，订阅来源） |
| [The upper bound revisited](https://www.sciencedirect.com/science/article/abs/pii/S0376738808002544) | 未获取（failed） | Robeson 上界的更新（领域定位，订阅来源） |
| [The Temperature Dependence of Relaxation Mechanisms in Amorphous Polymers and Other Glass-forming Liquids](https://pubs.aip.org/aip/jcp/article/23/2/379/226027) | 未获取（failed） | WLF 方程的原始工作（领域定位，订阅来源） |

## 第 5 章 分子模拟与多尺度计算

| 资料 | 本地文件 | 用途 |
| --- | --- | --- |
| [E(3)-equivariant graph neural networks for data-efficient and accurate interatomic potentials](https://www.nature.com/articles/s41467-022-29939-5) | [原件](files/papers/nequip-2022.pdf) · [文本](text/nequip-2022.txt) | 等变力场 |
| [MACE: Higher Order Equivariant Message Passing Neural Networks](https://arxiv.org/abs/2206.07697) | [原件](files/papers/mace-2022.pdf) · [文本](text/mace-2022.txt) | 高阶等变力场 |
| [Atomic Simulation Environment (ASE)](https://wiki.fysik.dtu.dk/ase/) | [原件](files/documents/ase-tools.html) · [文本](text/ase-tools.txt) | 原子模拟与计算接口 |
| [PySCF: Python-based Simulations of Chemistry Framework](https://pyscf.org/) | [原件](files/documents/pyscf-tools.html) · [文本](text/pyscf-tools.txt) | 量子化学计算 |
| [LAMMPS Molecular Dynamics Simulator](https://www.lammps.org/) | [原件](files/documents/lammps-tools.html) · [文本](text/lammps-tools.txt) | 分子动力学 |
| [OpenMM](https://openmm.org/) | [原件](files/documents/openmm-tools.html) · [文本](text/openmm-tools.txt)（incomplete_text） | GPU 分子动力学 |
| [Inhomogeneous Electron Gas](https://link.aps.org/doi/10.1103/PhysRev.140.A1133) | [原件](files/papers/ks-dft-1965.html) · [文本](text/ks-dft-1965.txt) | 密度泛函理论基础 |
| [Phase Transition for a Hard Sphere System](https://pubs.aip.org/aip/jcp/article/27/5/1208/207705) | 未获取（failed） | 分子动力学方法起点 |
| [Development and Testing of the OPLS All-Atom Force Field on Conformational Energetics and Properties of Organic Liquids](https://pubs.acs.org/doi/10.1021/ja9621760) | 未获取（failed） | OPLS-AA 力场：有机液体与聚合物参数化起点（订阅来源） |
| [Development and testing of a general amber force field](https://onlinelibrary.wiley.com/doi/10.1002/jcc.20035) | 未获取（failed） | GAFF 力场：通用小分子与聚合物参数化（订阅来源） |
| [COMPASS: An ab Initio Force-Field Optimized for Condensed-Phase Applications](https://pubs.acs.org/doi/10.1021/jp9725439) | 未获取（failed） | COMPASS 力场：凝聚相与聚合物参数化（订阅来源） |
| [All-Atom Empirical Potential for Molecular Modeling and Dynamics Studies of Proteins](https://pubs.acs.org/doi/10.1021/jp973084f) | 未获取（failed） | CHARMM 全原子力场：成键与非键项形式（订阅来源） |
| [The MARTINI Force Field: Coarse Grained Model for Biomolecular Simulations](https://pubs.acs.org/doi/10.1021/jp071097f) | 未获取（failed） | MARTINI 粗粒化力场：映射与参数化（订阅来源） |
| [Deriving effective mesoscale potentials from atomistic simulations](https://onlinelibrary.wiley.com/doi/10.1002/jcc.10307) | 未获取（failed） | 迭代玻尔兹曼反演（IBI）：结构匹配式粗粒化（订阅来源） |
| [A multiscale coarse-graining method for biomolecular systems](https://pubs.acs.org/doi/10.1021/jp044629q) | 未获取（failed） | 力匹配式粗粒化：从全原子力反推有效势（订阅来源） |
| [The relative entropy is fundamental to multiscale and inverse thermodynamic problems](https://pubs.aip.org/aip/jcp/article/129/14/144108/187392) | 未获取（failed） | 相对熵最小化：粗粒化参数化的信息论判据（订阅来源） |
| [Escaping free-energy minima](https://www.pnas.org/doi/10.1073/pnas.202427399) | 未获取（failed） | 元动力学：累积高斯偏置与自由能重建 |
| [Nonphysical sampling distributions in Monte Carlo free-energy estimation: Umbrella sampling](https://www.sciencedirect.com/science/article/pii/0021999177901218) | 未获取（failed） | 伞形采样：沿反应坐标加偏置（订阅来源） |
| [The weighted histogram analysis method for free-energy calculations on biomolecules](https://onlinelibrary.wiley.com/doi/10.1002/jcc.540130812) | 未获取（failed） | WHAM：拼接偏置窗口的无偏自由能（订阅来源） |
| [Replica-exchange molecular dynamics method for protein folding](https://www.sciencedirect.com/science/article/abs/pii/S0009261499011419) | 未获取（failed） | 副本交换：多温度并行与构型交换（订阅来源） |
| [Generalized Neural-Network Representation of High-Dimensional Potential-Energy Surfaces](https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.98.146401) | [原件](files/papers/behler-parrinello-2007.html) · [文本](text/behler-parrinello-2007.txt) | 高维势能面的神经网络表示：局部环境求和（订阅来源） |
| [A foundation model for atomistic materials chemistry](https://arxiv.org/abs/2401.00096) | [原件](files/papers/mace-mp-0-2023.pdf) · [文本](text/mace-mp-0-2023.txt) | 通用基础势：MACE-MP-0 与跨材料迁移 |
| [CHGNet as a pretrained universal neural network potential for charge-informed atomistic modelling](https://arxiv.org/abs/2302.14231) | [原件](files/papers/chgnet-2023.pdf) · [文本](text/chgnet-2023.txt) | 通用势：电荷信息与磁矩 |
| [A universal graph deep learning interatomic potential for the periodic table](https://arxiv.org/abs/2202.02450) | [原件](files/papers/m3gnet-2022.pdf) · [文本](text/m3gnet-2022.txt) | 通用图势：周期表覆盖与材料筛选 |
| [Learning local equivariant representations for large-scale atomistic dynamics](https://arxiv.org/abs/2204.05249) | [原件](files/papers/allegro-2023.pdf) · [文本](text/allegro-2023.txt) | 局部等变势：大规模动力学与外推 |
| [On-the-fly active learning of interpretable Bayesian force fields](https://arxiv.org/abs/2003.01831) | [原件](files/papers/flare-2020.pdf) · [文本](text/flare-2020.txt) | 在线主动学习力场与不确定性驱动采样 |
| [Machine Learning Force Fields](https://arxiv.org/abs/2010.07067) | [原件](files/papers/mlff-review-2021.pdf) · [文本](text/mlff-review-2021.txt) | 机器学习势综述：描述符、模型与数据 |
| [LAMMPS - a flexible simulation tool for particle-based materials modeling at the atomic, meso, and continuum scales](https://arxiv.org/abs/2112.09251) | [原件](files/papers/lammps-2022.pdf) · [文本](text/lammps-2022.txt) | LAMMPS 2022 论文：原子到连续介质尺度 |
| [OpenMM 7: Rapid development of high performance algorithms for molecular dynamics](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1005659) | [原件](files/papers/openmm-2017.html) · [文本](text/openmm-2017.txt) | OpenMM 7：GPU 分子动力学与可扩展平台 |
| [Recent developments in the PySCF program package](https://arxiv.org/abs/2002.12531) | [原件](files/papers/pyscf-2020.pdf) · [文本](text/pyscf-2020.txt) | PySCF：Python 量子化学程序包 |
| [GROMACS: High performance molecular simulations through multi-level parallelism from laptops to supercomputers](https://www.sciencedirect.com/science/article/pii/S2352711015000059) | 未获取（failed） | GROMACS 5：多级并行的分子模拟 |
| [A consistent and accurate ab initio parametrization of density functional dispersion correction (DFT-D) for the 94 elements H-Pu](https://pubs.aip.org/aip/jcp/article/132/15/154104/187772) | 未获取（failed） | DFT-D3 色散校正：泛函之外的弱相互作用（订阅来源） |
| [Force field for computation of conformational energies, structures, and vibrational frequencies of aromatic polyesters](https://onlinelibrary.wiley.com/doi/10.1002/jcc.540150310) | 未获取（failed） | PCFF 力场：芳香聚酯与聚合物的凝聚相参数化（订阅来源） |
| [Gaussian Process Optimization in the Bandit Setting: No Regret and Experimental Design](https://arxiv.org/abs/0912.3995) | [原件](files/papers/gp-ucb-2010.pdf) · [文本](text/gp-ucb-2010.txt) | GP-UCB：置信上界采集与遗憾界（开放获取） |

## 第 6 章 性质预测模型

| 资料 | 本地文件 | 用途 |
| --- | --- | --- |
| [Polymer Informatics: Opportunities and Challenges](https://pubs.acs.org/doi/10.1021/acsmacrolett.6b00936) | 未获取（failed） | 高分子信息学奠基综述 |
| [Polymer Genome: A Data-Powered Polymer Informatics Platform for Property Predictions](https://pubs.acs.org/doi/10.1021/acs.jpcc.8b02913) | 未获取（failed） | 多性质预测平台与描述符体系 |
| [Machine learning discovery of high thermal conductivity polymers](https://www.nature.com/articles/s41524-019-0247-3) | [原件](files/papers/thermal-conductivity-ml-2019.pdf) · [文本](text/thermal-conductivity-ml-2019.txt) | 高通量筛选与热导率预测 |
| [Machine learning–enabled high-throughput screening of polymers for gas separation](https://www.science.org/doi/10.1126/sciadv.abc6216) | 未获取（failed） | 膜分离材料筛选 |
| [Benchmarking machine learning models for polymer informatics: glass transition temperature](https://pubs.acs.org/doi/10.1021/acs.jcim.0c01336) | 未获取（failed） | Tg 预测基准与数据划分 |
| [Prediction of Hansen solubility parameters using machine learning](https://pubs.acs.org/doi/10.1021/acs.jcim.9b00485) | 未获取（failed） | 溶解度参数与 QSPR |
| [PolyBERT: a chemical language model to enable fully machine-driven ultrafast polymer informatics](https://www.nature.com/articles/s41467-023-39868-6) | [原件](files/papers/polybert-2023.pdf) · [文本](text/polybert-2023.txt) | 聚合物语言模型与表示 |
| [Neural Message Passing for Quantum Chemistry](https://arxiv.org/abs/1704.01212) | [原件](files/papers/mpnn-2017.pdf) · [文本](text/mpnn-2017.txt) | 消息传递图神经网络 |
| [SchNet: A continuous-filter convolutional neural network for modeling quantum interactions](https://arxiv.org/abs/1706.08566) | [原件](files/papers/schnet-2017.pdf) · [文本](text/schnet-2017.txt) | 等变/连续滤波网络 |
| [Deep learning for polymer property prediction with limited data](https://arxiv.org/abs/2004.10122) | [原件](files/papers/deeppolymer-2020.pdf) · [文本](text/deeppolymer-2020.txt) | 小数据下的聚合物性质预测 |
| [RDKit: Open-source cheminformatics](https://www.rdkit.org/) | [原件](files/documents/rdkit-tools.html) · [文本](text/rdkit-tools.txt) | 指纹、描述符与分子处理 |
| [Gaussian Processes for Machine Learning](http://www.gaussianprocess.org/gpml/) | [原件](files/documents/gpml-2006.html) · [文本](text/gpml-2006.txt) | 高斯过程回归教材 |
| [MoleculeNet: A Benchmark for Molecular Machine Learning](https://pubs.rsc.org/en/content/articlelanding/2018/sc/c7sc02664a) | [原件](files/papers/moleculenet-2018.pdf) · [文本](text/moleculenet-2018.txt) | 小分子基准与划分策略 |
| [Weisfeiler-Lehman Graph Kernels](https://www.jmlr.org/papers/v12/shervashidze11a.html) | [原件](files/papers/wl-graph-kernel-2011.pdf) · [文本](text/wl-graph-kernel-2011.txt) | 迭代图核与消息传递的理论前身 |
| [A graph representation of molecular ensembles for polymer property prediction](https://arxiv.org/abs/2205.08619) | [原件](files/papers/polymer-ensemble-gnn-2022.pdf) · [文本](text/polymer-ensemble-gnn-2022.txt) | 聚合物集合图表示 |
| [Polymer informatics at-scale with multitask graph neural networks](https://arxiv.org/abs/2209.13557) | [原件](files/papers/polymer-multitask-gnn-2023.pdf) · [文本](text/polymer-multitask-gnn-2023.txt) | 多任务图网络与大规模筛选 |
| [Geometric Deep Learning: Grids, Groups, Graphs, Geodesics, and Gauges](https://arxiv.org/abs/2104.13478) | [原件](files/papers/geometric-deep-learning-2021.pdf) · [文本](text/geometric-deep-learning-2021.txt) | 几何深度学习的对称性与不变性框架 |
| [Benchmarking Materials Property Prediction Methods: The Matbench Test Set and Automatminer Reference Algorithm](https://arxiv.org/abs/2005.00707) | [原件](files/papers/matbench-2020.pdf) · [文本](text/matbench-2020.txt) | 材料基准的测试集与划分 |
| [Deep Learning Scaling is Predictable, Empirically](https://arxiv.org/abs/1712.00409) | [原件](files/papers/hestness-2017.pdf) · [文本](text/hestness-2017.txt) | 幂律学习曲线的经验形式 |
| [A Constructive Prediction of the Generalization Error Across Scales](https://arxiv.org/abs/1909.12673) | [原件](files/papers/rosenfeld-2020.pdf) · [文本](text/rosenfeld-2020.txt) | 跨尺度泛化误差预测 |
| [A survey of cross-validation procedures for model selection](https://arxiv.org/abs/0907.4728) | [原件](files/papers/arlot-celisse-2010.pdf) · [文本](text/arlot-celisse-2010.txt) | 交叉验证与模型选择 |
| [Semi-Supervised Classification with Graph Convolutional Networks](https://arxiv.org/abs/1609.02907) | [原件](files/papers/gcn-2017.pdf) · [文本](text/gcn-2017.txt) | 图卷积网络：谱域近似与半监督节点分类 |
| [Graph Attention Networks](https://arxiv.org/abs/1710.10903) | [原件](files/papers/gat-2018.pdf) · [文本](text/gat-2018.txt) | 图注意力网络：邻居加权聚合 |
| [Analyzing Learned Molecular Representations for Property Prediction](https://arxiv.org/abs/1904.01561) | [原件](files/papers/chemprop-2019.pdf) · [文本](text/chemprop-2019.txt) | Chemprop：有向消息传递与分子性质预测 |
| [E(n) Equivariant Graph Neural Networks](https://arxiv.org/abs/2102.09844) | [原件](files/papers/egnn-2021.pdf) · [文本](text/egnn-2021.txt) | E(n) 等变图网络：坐标更新与几何性质 |
| [Attention Is All You Need](https://arxiv.org/abs/1706.03762) | [原件](files/papers/transformer-2017.pdf) · [文本](text/transformer-2017.txt) | Transformer：自注意力架构 |
| [BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding](https://arxiv.org/abs/1810.04805) | [原件](files/papers/bert-2019.pdf) · [文本](text/bert-2019.txt) | 掩码语言建模预训练 |
| [ChemBERTa: Large-Scale Self-Supervised Pretraining for Molecular Property Prediction](https://arxiv.org/abs/2010.09885) | [原件](files/papers/chemberta-2020.pdf) · [文本](text/chemberta-2020.txt) | 小分子化学语言模型预训练 |
| [Random Forests](https://doi.org/10.1023/A:1010933404324) | [原件](files/papers/random-forest-2001.html) · [文本](text/random-forest-2001.txt) | 随机森林原始工作（订阅来源） |
| [Greedy Function Approximation: A Gradient Boosting Machine](https://doi.org/10.1214/aos/1013203451) | [原件](files/papers/gradient-boosting-2001.html) · [文本](text/gradient-boosting-2001.txt)（incomplete_text） | 梯度提升的统计框架（订阅来源） |
| [XGBoost: A Scalable Tree Boosting System](https://arxiv.org/abs/1603.02754) | [原件](files/papers/xgboost-2016.pdf) · [文本](text/xgboost-2016.txt) | XGBoost：可扩展的树提升系统 |
| [Support-Vector Networks](https://doi.org/10.1007/BF00994018) | [原件](files/papers/svr-1995.html) · [文本](text/svr-1995.txt) | 支持向量回归与 ε 不敏感损失（订阅来源） |
| [Inductive Confidence Machines for Regression](https://link.springer.com/chapter/10.1007/3-540-36755-1_29) | [原件](files/papers/conformal-2002.html) · [文本](text/conformal-2002.txt) | split conformal 回归预测区间（订阅来源） |
| [Quantile Regression Forests](https://www.jmlr.org/papers/v7/meinshausen06a.html) | [原件](files/papers/quantile-forest-2006.html) · [文本](text/quantile-forest-2006.txt) | 分位数回归森林：条件分位数 |
| [Simple and Scalable Predictive Uncertainty Estimation using Deep Ensembles](https://arxiv.org/abs/1612.01474) | [原件](files/papers/deep-ensembles-2017.pdf) · [文本](text/deep-ensembles-2017.txt) | 深度集成方差与预测不确定度 |
| [Scikit-learn: Machine Learning in Python](https://www.jmlr.org/papers/v12/pedregosa11a.html) | [原件](files/papers/scikit-learn-2011.html) · [文本](text/scikit-learn-2011.txt) | Python 机器学习工具与实现细节 |

## 第 7 章 多任务、迁移与物理信息学习

| 资料 | 本地文件 | 用途 |
| --- | --- | --- |
| [Polymer Genome: A Data-Powered Polymer Informatics Platform for Property Predictions](https://pubs.acs.org/doi/10.1021/acs.jpcc.8b02913) | 未获取（failed） | 多性质预测平台与描述符体系 |
| [Benchmarking machine learning models for polymer informatics: glass transition temperature](https://pubs.acs.org/doi/10.1021/acs.jcim.0c01336) | 未获取（failed） | Tg 预测基准与数据划分 |
| [PolyBERT: a chemical language model to enable fully machine-driven ultrafast polymer informatics](https://www.nature.com/articles/s41467-023-39868-6) | [原件](files/papers/polybert-2023.pdf) · [文本](text/polybert-2023.txt) | 聚合物语言模型与表示 |
| [Neural Message Passing for Quantum Chemistry](https://arxiv.org/abs/1704.01212) | [原件](files/papers/mpnn-2017.pdf) · [文本](text/mpnn-2017.txt) | 消息传递图神经网络 |
| [SchNet: A continuous-filter convolutional neural network for modeling quantum interactions](https://arxiv.org/abs/1706.08566) | [原件](files/papers/schnet-2017.pdf) · [文本](text/schnet-2017.txt) | 等变/连续滤波网络 |
| [E(3)-equivariant graph neural networks for data-efficient and accurate interatomic potentials](https://www.nature.com/articles/s41467-022-29939-5) | [原件](files/papers/nequip-2022.pdf) · [文本](text/nequip-2022.txt) | 等变力场 |
| [MACE: Higher Order Equivariant Message Passing Neural Networks](https://arxiv.org/abs/2206.07697) | [原件](files/papers/mace-2022.pdf) · [文本](text/mace-2022.txt) | 高阶等变力场 |
| [Physics-informed neural networks](https://www.sciencedirect.com/science/article/pii/S0021999118307125) | [原件](files/papers/pinn-2019.pdf) · [文本](text/pinn-2019.txt) | 物理信息神经网络 |
| [Deep learning for polymer property prediction with limited data](https://arxiv.org/abs/2004.10122) | [原件](files/papers/deeppolymer-2020.pdf) · [文本](text/deeppolymer-2020.txt) | 小数据下的聚合物性质预测 |
| [PI1M: A Benchmark Database for Polymer Informatics](https://pubs.acs.org/doi/10.1021/acs.jcim.0c00726) | 未获取（failed） | 百万级聚合物虚拟库 |
| [TransPolymer: a Transformer-based language model for polymer property predictions](https://www.nature.com/articles/s41524-023-01016-5) | [原件](files/papers/transpolymer-2023.pdf) · [文本](text/transpolymer-2023.txt) | 聚合物 Transformer 表示与预训练 |
| [Polymer informatics at-scale with multitask graph neural networks](https://arxiv.org/abs/2209.13557) | [原件](files/papers/polymer-multitask-gnn-2023.pdf) · [文本](text/polymer-multitask-gnn-2023.txt) | 多任务图网络与大规模筛选 |
| [E(n) Equivariant Graph Neural Networks](https://arxiv.org/abs/2102.09844) | [原件](files/papers/egnn-2021.pdf) · [文本](text/egnn-2021.txt) | E(n) 等变图网络：坐标更新与几何性质 |
| [ChemBERTa: Large-Scale Self-Supervised Pretraining for Molecular Property Prediction](https://arxiv.org/abs/2010.09885) | [原件](files/papers/chemberta-2020.pdf) · [文本](text/chemberta-2020.txt) | 小分子化学语言模型预训练 |
| [An Overview of Multi-Task Learning in Deep Neural Networks](https://arxiv.org/abs/1706.05098) | [原件](files/papers/multitask-overview-2017.pdf) · [文本](text/multitask-overview-2017.txt) | 多任务学习综述：硬共享、软共享与任务关系 |
| [Multi-Task Learning Using Uncertainty to Weigh Losses for Scene Geometry and Semantics](https://arxiv.org/abs/1705.07115) | [原件](files/papers/multitask-uncertainty-2018.pdf) · [文本](text/multitask-uncertainty-2018.txt) | 不确定性加权：可学习任务噪声 |
| [Gradient Surgery for Multi-Task Learning](https://arxiv.org/abs/2001.06782) | [原件](files/papers/gradient-surgery-2020.pdf) · [文本](text/gradient-surgery-2020.txt) | 梯度冲突与投影（PCGrad） |
| [A Survey on Multi-Task Learning](https://arxiv.org/abs/1707.08114) | [原件](files/papers/multitask-survey-2021.pdf) · [文本](text/multitask-survey-2021.txt) | 多任务学习的形式化与分类 |
| [Characterizing and Avoiding Negative Transfer](https://arxiv.org/abs/1811.09751) | [原件](files/papers/negative-transfer-2019.pdf) · [文本](text/negative-transfer-2019.txt) | 负迁移的刻画与规避 |
| [Model-Agnostic Meta-Learning for Fast Adaptation of Deep Networks](https://arxiv.org/abs/1703.03400) | [原件](files/papers/maml-2017.pdf) · [文本](text/maml-2017.txt) | 元学习与少样本适配 |
| [Parameter-Efficient Transfer Learning for NLP](https://arxiv.org/abs/1902.00751) | [原件](files/papers/adapter-2019.pdf) · [文本](text/adapter-2019.txt) | 适配器：参数高效迁移 |
| [LoRA: Low-Rank Adaptation of Large Language Models](https://arxiv.org/abs/2106.09685) | [原件](files/papers/lora-2021.pdf) · [文本](text/lora-2021.txt) | 低秩增量微调 |
| [Domain-Adversarial Training of Neural Networks](https://arxiv.org/abs/1505.07818) | [原件](files/papers/dann-2016.pdf) · [文本](text/dann-2016.txt) | 领域自适应：对抗对齐 |
| [A Comprehensive Survey on Transfer Learning](https://arxiv.org/abs/1911.02685) | [原件](files/papers/transfer-survey-2020.pdf) · [文本](text/transfer-survey-2020.txt) | 迁移学习综述：策略与失败模式 |
| [Strategies for Pre-training Graph Neural Networks](https://arxiv.org/abs/1905.12265) | [原件](files/papers/pretrain-gnn-2019.pdf) · [文本](text/pretrain-gnn-2019.txt) | 图网络预训练：属性掩码与上下文预测 |
| [Graph Contrastive Learning with Augmentations](https://arxiv.org/abs/2010.13902) | [原件](files/papers/graphcl-2020.pdf) · [文本](text/graphcl-2020.txt) | 图对比学习与数据增强 |
| [Molecular Contrastive Learning of Representations via Graph Neural Networks](https://arxiv.org/abs/2102.10056) | [原件](files/papers/molclr-2022.pdf) · [文本](text/molclr-2022.txt) | 分子图对比预训练 |
| [Informed Machine Learning: A Taxonomy and Survey of Integrating Knowledge into Learning Systems](https://arxiv.org/abs/1903.12394) | [原件](files/papers/informed-ml-2021.pdf) · [文本](text/informed-ml-2021.txt) | 知识注入的分类：特征、正则与结构 |
| [Integrating Scientific Knowledge with Machine Learning for Engineering and Environmental Systems](https://arxiv.org/abs/2003.04919) | [原件](files/papers/willard-2022.pdf) · [文本](text/willard-2022.txt) | 科学知识与机器学习的整合方式 |
| [Tensor Field Networks: Rotation- and Translation-Equivariant Neural Networks for 3D Point Clouds](https://arxiv.org/abs/1802.08219) | [原件](files/papers/tfn-2018.pdf) · [文本](text/tfn-2018.txt) | 张量场网络：等变特征构造 |

## 第 8 章 表征、成像与光谱的 AI 分析

| 资料 | 本地文件 | 用途 |
| --- | --- | --- |
| [Gaussian Processes for Machine Learning](http://www.gaussianprocess.org/gpml/) | [原件](files/documents/gpml-2006.html) · [文本](text/gpml-2006.txt) | 高斯过程回归教材 |
| [Autonomous experimentation systems for materials development](https://www.nature.com/articles/s41578-023-00587-5) | [原件](files/papers/self-driving-lab-review-2023.html) · [文本](text/self-driving-lab-review-2023.txt)（access_required） | 自主实验系统综述 |
| [In Search of Lost Domain Generalization](https://arxiv.org/abs/2007.01434) | [原件](files/papers/domainbed-2021.pdf) · [文本](text/domainbed-2021.txt) | 分布偏移下的评测协议 |
| [On-the-fly closed-loop materials discovery via Bayesian active learning](https://www.nature.com/articles/s41467-020-19597-w) | [原件](files/papers/kusne-2020.html) · [文本](text/kusne-2020.txt)（access_required） | 闭环主动学习与实验回流（开放获取） |
| [Attention Is All You Need](https://arxiv.org/abs/1706.03762) | [原件](files/papers/transformer-2017.pdf) · [文本](text/transformer-2017.txt) | Transformer：自注意力架构 |
| [Simple and Scalable Predictive Uncertainty Estimation using Deep Ensembles](https://arxiv.org/abs/1612.01474) | [原件](files/papers/deep-ensembles-2017.pdf) · [文本](text/deep-ensembles-2017.txt) | 深度集成方差与预测不确定度 |
| [U-Net: Convolutional Networks for Biomedical Image Segmentation](https://arxiv.org/abs/1505.04597) | [原件](files/papers/unet-2015.pdf) · [文本](text/unet-2015.txt) | 编码器–解码器与跳跃连接的分割基线 |
| [Mask R-CNN](https://arxiv.org/abs/1703.06870) | [原件](files/papers/mask-rcnn-2017.pdf) · [文本](text/mask-rcnn-2017.txt) | 实例分割与检测的联合框架 |
| [Encoder-Decoder with Atrous Separable Convolution for Semantic Image Segmentation](https://arxiv.org/abs/1802.02611) | [原件](files/papers/deeplab-v3plus-2018.pdf) · [文本](text/deeplab-v3plus-2018.txt) | 空洞卷积与多尺度上下文 |
| [nnU-Net: Self-adapting Framework for U-Net-Based Medical Image Segmentation](https://arxiv.org/abs/1809.10486) | [原件](files/papers/nnunet-2018.pdf) · [文本](text/nnunet-2018.txt) | 分割流程的自适应配置与预处理 |
| [Segment Anything](https://arxiv.org/abs/2304.02643) | [原件](files/papers/segment-anything-2023.pdf) · [文本](text/segment-anything-2023.txt) | 可提示的通用分割基础模型 |
| [Cost-efficient segmentation of electron microscopy images using active learning](https://arxiv.org/abs/1911.05548) | [原件](files/papers/em-active-learning-2019.pdf) · [文本](text/em-active-learning-2019.txt) | 电镜分割的主动标注 |
| [Machine Learning for Analyzing Atomic Force Microscopy (AFM) Images Generated from Polymer Blends](https://arxiv.org/abs/2409.11438) | [原件](files/papers/afm-polymer-blends-2024.pdf) · [文本](text/afm-polymer-blends-2024.txt) | 聚合物共混 AFM 图像的机器学习分析 |
| [Cryo-CARE: Content-Aware Image Restoration for Cryo-Transmission Electron Microscopy Data](https://arxiv.org/abs/1810.05420) | [原件](files/papers/care-cryoem-2018.pdf) · [文本](text/care-cryoem-2018.txt) | 内容感知图像恢复与去噪 |
| [High-throughput molecular imaging via deep learning enabled Raman spectroscopy](https://arxiv.org/abs/2009.13318) | [原件](files/papers/raman-imaging-2020.pdf) · [文本](text/raman-imaging-2020.txt) | 拉曼高光谱成像的深度学习方法 |
| [Benchmarking Deep Learning Models for Raman Spectroscopy Across Open-Source Datasets](https://arxiv.org/abs/2601.16107) | [原件](files/papers/raman-benchmark-2026.pdf) · [文本](text/raman-benchmark-2026.txt) | 拉曼深度学习模型的开放基准 |
| [Reversible Deep Learning for 13C NMR in Chemoinformatics: On Structures and Spectra](https://arxiv.org/abs/2602.03875) | [原件](files/papers/nmr-reversible-2026.pdf) · [文本](text/nmr-reversible-2026.txt) | 结构与核磁谱的双向映射 |
| [Neural Network-based Classification of Crystal Symmetries from X-Ray Diffraction Patterns](https://arxiv.org/abs/1812.05625) | [原件](files/papers/xrd-symmetry-cnn-2018.pdf) · [文本](text/xrd-symmetry-cnn-2018.txt) | XRD 图谱的晶系分类 |
| [Fast and interpretable classification of small X-ray diffraction datasets using data augmentation and deep neural networks](https://arxiv.org/abs/1811.08425) | [原件](files/papers/xrd-augment-2019.pdf) · [文本](text/xrd-augment-2019.txt) | 小样本 XRD 的数据增强与分类 |
| [Accelerating small-angle scattering experiments with simulation-based machine learning](https://arxiv.org/abs/1908.09102) | [原件](files/papers/saxs-ml-2019.pdf) · [文本](text/saxs-ml-2019.txt) | 模拟驱动的散射实验加速 |
| [Scattering-Based Structural Inversion of Soft Materials via Kolmogorov-Arnold Networks](https://arxiv.org/abs/2412.15474) | [原件](files/papers/scattering-inverse-kan-2024.pdf) · [文本](text/scattering-inverse-kan-2024.txt) | 散射曲线到结构的反演 |
| [Pair-Variational Autoencoders for Linking and Cross-Reconstruction of Characterization Data from Complementary Structural Characterization Techniques](https://arxiv.org/abs/2305.16467) | [原件](files/papers/pairvae-2023.pdf) · [文本](text/pairvae-2023.txt) | 互补表征数据的配对与互重建 |
| [Learning Transferable Visual Models From Natural Language Supervision](https://arxiv.org/abs/2103.00020) | [原件](files/papers/clip-2021.pdf) · [文本](text/clip-2021.txt) | 图文对比学习与共享嵌入 |
| [A Simple Framework for Contrastive Learning of Visual Representations](https://arxiv.org/abs/2002.05709) | [原件](files/papers/simclr-2020.pdf) · [文本](text/simclr-2020.txt) | 自监督对比表示 |
| [Masked Autoencoders Are Scalable Vision Learners](https://arxiv.org/abs/2111.06377) | [原件](files/papers/mae-2022.pdf) · [文本](text/mae-2022.txt) | 掩码自编码与可扩展预训练 |
| [An introduction to domain adaptation and transfer learning](https://arxiv.org/abs/1812.11806) | [原件](files/papers/domain-adaptation-2019.pdf) · [文本](text/domain-adaptation-2019.txt) | 域适应与迁移学习导论 |
| [Causal Interpretability for Machine Learning -- Problems, Methods and Evaluation](https://arxiv.org/abs/2003.03934) | [原件](files/papers/causal-interpretability-2020.pdf) · [文本](text/causal-interpretability-2020.txt) | 相关与因果的区分 |
| [Bayesian Active Learning for Scanning Probe Microscopy: from Gaussian Processes to Hypothesis Learning](https://arxiv.org/abs/2205.15458) | [原件](files/papers/spm-active-learning-2022.pdf) · [文本](text/spm-active-learning-2022.txt) | 扫描探针显微镜的贝叶斯主动测量 |

## 第 9 章 生成模型与高分子序列设计

| 资料 | 本地文件 | 用途 |
| --- | --- | --- |
| [BigSMILES: A Structurally-Based Line Notation for Describing Macromolecules](https://pubs.acs.org/doi/10.1021/acscentsci.9b00476) | 未获取（failed） | 随机结构高分子的字符串表示 |
| [PolyBERT: a chemical language model to enable fully machine-driven ultrafast polymer informatics](https://www.nature.com/articles/s41467-023-39868-6) | [原件](files/papers/polybert-2023.pdf) · [文本](text/polybert-2023.txt) | 聚合物语言模型与表示 |
| [PolyGAN: High-Order Polymer Property Prediction and Generation](https://pubs.acs.org/doi/10.1021/acs.jcim.0c01029) | 未获取（failed） | 生成对抗网络生成聚合物 |
| [PI1M: A Benchmark Database for Polymer Informatics](https://pubs.acs.org/doi/10.1021/acs.jcim.0c00726) | 未获取（failed） | 百万级聚合物虚拟库 |
| [Open Macromolecular Genome](https://github.com/TheJacksonLab/OpenMacromolecularGenome) | [原件](files/datasets/open-macromolecular-genome.html) · [文本](text/open-macromolecular-genome.txt) | 可合成聚合物的开放基因组 |
| [SMiPoly: Generation of a Synthesizable Polymer Virtual Library](https://pubs.acs.org/doi/10.1021/acs.jcim.3c00277) | 未获取（failed） | 可合成虚拟库生成 |
| [Self-Referencing Embedded Strings (SELFIES): A 100% robust molecular string representation](https://arxiv.org/abs/1905.13741) | [原件](files/papers/selfies-2020.pdf) · [文本](text/selfies-2020.txt) | 机器学习可用的鲁棒字符串表示 |
| [TransPolymer: a Transformer-based language model for polymer property predictions](https://www.nature.com/articles/s41524-023-01016-5) | [原件](files/papers/transpolymer-2023.pdf) · [文本](text/transpolymer-2023.txt) | 聚合物 Transformer 表示与预训练 |
| [Auto-Encoding Variational Bayes](https://arxiv.org/abs/1312.6114) | [原件](files/papers/vae-2013.pdf) · [文本](text/vae-2013.txt) | 变分自编码器、重参数化与证据下界 |
| [Generative Adversarial Networks](https://arxiv.org/abs/1406.2661) | [原件](files/papers/gan-2014.pdf) · [文本](text/gan-2014.txt) | 生成对抗网络与对抗训练 |
| [Denoising Diffusion Probabilistic Models](https://arxiv.org/abs/2006.11239) | [原件](files/papers/ddpm-2020.pdf) · [文本](text/ddpm-2020.txt) | 去噪扩散概率模型与噪声预测目标 |
| [Denoising Diffusion Implicit Models](https://arxiv.org/abs/2010.02502) | [原件](files/papers/ddim-2020.pdf) · [文本](text/ddim-2020.txt) | 确定性扩散采样与步数加速 |
| [Score-Based Generative Modeling through Stochastic Differential Equations](https://arxiv.org/abs/2011.13456) | [原件](files/papers/score-sde-2020.pdf) · [文本](text/score-sde-2020.txt) | 分数匹配与随机微分方程视角 |
| [Flow Matching for Generative Modeling](https://arxiv.org/abs/2210.02747) | [原件](files/papers/flow-matching-2022.pdf) · [文本](text/flow-matching-2022.txt) | 流匹配与连续归一化流 |
| [Neural Ordinary Differential Equations](https://arxiv.org/abs/1806.07366) | [原件](files/papers/neural-ode-2018.pdf) · [文本](text/neural-ode-2018.txt) | 连续归一化流与 ODE 求解采样 |
| [Variational Inference with Normalizing Flows](https://arxiv.org/abs/1505.05770) | [原件](files/papers/normalizing-flows-2015.pdf) · [文本](text/normalizing-flows-2015.txt) | 可逆变换与变量替换公式 |
| [MaskGIT: Masked Generative Image Transformer](https://arxiv.org/abs/2202.04200) | [原件](files/papers/maskgit-2022.pdf) · [文本](text/maskgit-2022.txt) | 掩码生成与并行迭代解码 |
| [Simple and Effective Masked Diffusion Language Models](https://arxiv.org/abs/2406.07524) | [原件](files/papers/mdlm-2024.pdf) · [文本](text/mdlm-2024.txt) | 掩码扩散语言模型与似然界 |
| [Structured Denoising Diffusion Models in Discrete State-Spaces](https://arxiv.org/abs/2107.03006) | [原件](files/papers/d3pm-2021.pdf) · [文本](text/d3pm-2021.txt) | 离散扩散与转移矩阵加噪 |
| [Classifier-Free Diffusion Guidance](https://arxiv.org/abs/2207.12598) | [原件](files/papers/cfg-2022.pdf) · [文本](text/cfg-2022.txt) | 无分类器引导与条件生成 |
| [Elucidating the Design Space of Diffusion-Based Generative Models](https://arxiv.org/abs/2206.00364) | [原件](files/papers/edm-2022.pdf) · [文本](text/edm-2022.txt) | 扩散训练与采样的设计空间 |
| [MolGAN: An implicit generative model for small molecular graphs](https://arxiv.org/abs/1805.11973) | [原件](files/papers/molgan-2018.pdf) · [文本](text/molgan-2018.txt) | 分子图对抗生成与强化学习奖励 |
| [Junction Tree Variational Autoencoder for Molecular Graph Generation](https://arxiv.org/abs/1802.04364) | [原件](files/papers/jtvae-2018.pdf) · [文本](text/jtvae-2018.txt) | 分子图 VAE 与语法约束解码 |
| [GraphAF: a Flow-based Autoregressive Model for Molecular Graph Generation](https://arxiv.org/abs/2001.09382) | [原件](files/papers/graphaf-2020.pdf) · [文本](text/graphaf-2020.txt) | 自回归流生成分子图 |
| [Equivariant Diffusion for Molecule Generation in 3D](https://arxiv.org/abs/2203.17003) | [原件](files/papers/geoldm-2022.pdf) · [文本](text/geoldm-2022.txt) | 三维分子等变扩散生成 |
| [Polymers for Extreme Conditions Designed Using Syntax-Directed Variational Autoencoders](https://arxiv.org/abs/2011.02551) | [原件](files/papers/polyvae-2020.pdf) · [文本](text/polyvae-2020.txt) | 语法指导 VAE 与聚合物候选设计 |
| [polyGen: A Learning Framework for Atomic-level Polymer Structure Generation](https://arxiv.org/abs/2504.17656) | [原件](files/papers/polygen-2025.pdf) · [文本](text/polygen-2025.txt) | 原子级聚合物结构生成 |
| [A Self-Improvable Polymer Discovery Framework Based on Conditional Generative Model](https://arxiv.org/abs/2312.04013) | [原件](files/papers/self-improvable-polymer-2023.pdf) · [文本](text/self-improvable-polymer-2023.txt) | 条件生成与自改进聚合物发现 |
| [polyBART: A Chemical Linguist for Polymer Property Prediction and Generative Design](https://arxiv.org/abs/2506.04233) | [原件](files/papers/polybart-2025.pdf) · [文本](text/polybart-2025.txt) | 聚合物序列生成与性质预测 |
| [GLAMOUR: Graph Learning over Macromolecule Representations](https://arxiv.org/abs/2103.02565) | [原件](files/papers/glamour-2021.pdf) · [文本](text/glamour-2021.txt) | 高分子图表征与表示学习 |
| [AI-guided inverse design and discovery of recyclable vitrimeric polymers](https://arxiv.org/abs/2312.03690) | [原件](files/papers/vitrimer-inverse-2023.pdf) · [文本](text/vitrimer-inverse-2023.txt) | 可回收聚合物的生成式逆向设计 |
| [Open-source Polymer Generative Pipeline](https://arxiv.org/abs/2412.08658) | [原件](files/papers/open-polymer-generative-pipeline-2024.pdf) · [文本](text/open-polymer-generative-pipeline-2024.txt) | 开源聚合物生成流程与评价协议 |
| [Estimation of synthetic accessibility score of drug-like molecules based on molecular complexity and fragment contributions](https://jcheminf.biomedcentral.com/articles/10.1186/1758-2946-1-8) | [原件](files/papers/sa-score-2009.html) · [文本](text/sa-score-2009.txt) | 可合成性评分的片段贡献法 |
| [Attention Is All You Need](https://arxiv.org/abs/1706.03762) | [原件](files/papers/transformer-2017.pdf) · [文本](text/transformer-2017.txt) | Transformer：自注意力架构 |

## 第 10 章 逆向设计与多目标材料设计

| 资料 | 本地文件 | 用途 |
| --- | --- | --- |
| [Polymer Genome: A Data-Powered Polymer Informatics Platform for Property Predictions](https://pubs.acs.org/doi/10.1021/acs.jpcc.8b02913) | 未获取（failed） | 多性质预测平台与描述符体系 |
| [Machine learning discovery of high thermal conductivity polymers](https://www.nature.com/articles/s41524-019-0247-3) | [原件](files/papers/thermal-conductivity-ml-2019.pdf) · [文本](text/thermal-conductivity-ml-2019.txt) | 高通量筛选与热导率预测 |
| [Machine learning–enabled high-throughput screening of polymers for gas separation](https://www.science.org/doi/10.1126/sciadv.abc6216) | 未获取（failed） | 膜分离材料筛选 |
| [PolyBERT: a chemical language model to enable fully machine-driven ultrafast polymer informatics](https://www.nature.com/articles/s41467-023-39868-6) | [原件](files/papers/polybert-2023.pdf) · [文本](text/polybert-2023.txt) | 聚合物语言模型与表示 |
| [Open Macromolecular Genome](https://github.com/TheJacksonLab/OpenMacromolecularGenome) | [原件](files/datasets/open-macromolecular-genome.html) · [文本](text/open-macromolecular-genome.txt) | 可合成聚合物的开放基因组 |
| [SMiPoly: Generation of a Synthesizable Polymer Virtual Library](https://pubs.acs.org/doi/10.1021/acs.jcim.3c00277) | 未获取（failed） | 可合成虚拟库生成 |
| [Gaussian Processes for Machine Learning](http://www.gaussianprocess.org/gpml/) | [原件](files/documents/gpml-2006.html) · [文本](text/gpml-2006.txt) | 高斯过程回归教材 |
| [A Tutorial on Bayesian Optimization](https://arxiv.org/abs/1807.02811) | [原件](files/papers/bo-review-2018.pdf) · [文本](text/bo-review-2018.txt) | 贝叶斯优化综述 |
| [Polymer informatics at-scale with multitask graph neural networks](https://arxiv.org/abs/2209.13557) | [原件](files/papers/polymer-multitask-gnn-2023.pdf) · [文本](text/polymer-multitask-gnn-2023.txt) | 多任务图网络与大规模筛选 |
| [MolGAN: An implicit generative model for small molecular graphs](https://arxiv.org/abs/1805.11973) | [原件](files/papers/molgan-2018.pdf) · [文本](text/molgan-2018.txt) | 分子图对抗生成与强化学习奖励 |
| [Junction Tree Variational Autoencoder for Molecular Graph Generation](https://arxiv.org/abs/1802.04364) | [原件](files/papers/jtvae-2018.pdf) · [文本](text/jtvae-2018.txt) | 分子图 VAE 与语法约束解码 |
| [AI-guided inverse design and discovery of recyclable vitrimeric polymers](https://arxiv.org/abs/2312.03690) | [原件](files/papers/vitrimer-inverse-2023.pdf) · [文本](text/vitrimer-inverse-2023.txt) | 可回收聚合物的生成式逆向设计 |
| [Estimation of synthetic accessibility score of drug-like molecules based on molecular complexity and fragment contributions](https://jcheminf.biomedcentral.com/articles/10.1186/1758-2946-1-8) | [原件](files/papers/sa-score-2009.html) · [文本](text/sa-score-2009.txt) | 可合成性评分的片段贡献法 |
| [Inverse molecular design using machine learning: Generative models for matter engineering](https://www.science.org/doi/10.1126/science.aat2663) | 未获取（failed） | 逆向分子设计的生成模型综述（订阅来源） |
| [Automatic Chemical Design Using a Data-Driven Continuous Representation of Molecules](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5842510/) | [原件](files/papers/gomez-bombarelli-2018.html) · [文本](text/gomez-bombarelli-2018.txt) | 潜空间连续表示与分子优化（开放获取） |
| [Graph Convolutional Policy Network for Goal-Directed Molecular Graph Generation](https://arxiv.org/abs/1806.02473) | [原件](files/papers/gcpn-2018.pdf) · [文本](text/gcpn-2018.txt) | 目标导向的图生成与强化学习 |
| [Molecular de-novo design through deep reinforcement learning](https://jcheminf.biomedcentral.com/articles/10.1186/s13321-017-0235-x) | [原件](files/papers/reinvent-2017.html) · [文本](text/reinvent-2017.txt) | 强化学习序列生成与先验策略（开放获取） |
| [GuacaMol: Benchmarking Models for de Novo Molecular Design](https://arxiv.org/abs/1811.09621) | [原件](files/papers/guacamol-2019.pdf) · [文本](text/guacamol-2019.txt) | 生成模型基准：有效性、多样性与新颖性 |
| [Molecular Sets (MOSES): A Benchmarking Platform for Molecular Generation Models](https://arxiv.org/abs/1811.12823) | [原件](files/papers/moses-2020.pdf) · [文本](text/moses-2020.txt) | 分子生成模型评测平台 |
| [A graph-based genetic algorithm and generative model/Monte Carlo tree search for the exploration of chemical space](https://pubs.rsc.org/en/content/articlelanding/2019/sc/c8sc05372c) | [原件](files/papers/jensen-2019.html) · [文本](text/jensen-2019.txt) | 图遗传算法与蒙特卡洛树搜索（开放获取） |
| [A fast and elitist multiobjective genetic algorithm: NSGA-II](https://doi.org/10.1109/4235.996017) | [原件](files/papers/nsga2-2002.html) · [文本](text/nsga2-2002.txt)（incomplete_text） | 非支配排序遗传算法（订阅来源） |
| [ParEGO: A hybrid algorithm with on-line landscape approximation for expensive multiobjective optimization problems](https://doi.org/10.1109/TEVC.2005.851274) | [原件](files/papers/parego-2006.html) · [文本](text/parego-2006.txt)（incomplete_text） | 多目标贝叶斯优化与标量化（订阅来源） |
| [Differentiable Expected Hypervolume Improvement for Parallel Multi-Objective Bayesian Optimization](https://arxiv.org/abs/2006.05078) | [原件](files/papers/ehvi-2020.pdf) · [文本](text/ehvi-2020.txt) | 超体积提升与多目标采集函数 |
| [Performance assessment of multiobjective optimizers: an analysis of the hypervolume measure](https://doi.org/10.1109/TEVC.2003.810758) | [原件](files/papers/hypervolume-2003.html) · [文本](text/hypervolume-2003.txt)（incomplete_text） | 超体积指标的定义与性质（订阅来源） |
| [A tutorial on multiobjective optimization: fundamentals and evolutionary methods](https://doi.org/10.1007/s11047-018-9685-y) | [原件](files/papers/multiobjective-tutorial-2018.html) · [文本](text/multiobjective-tutorial-2018.txt) | 多目标优化与前沿覆盖教程 |
| [Conditional Generative Adversarial Nets](https://arxiv.org/abs/1411.1784) | [原件](files/papers/conditional-gan-2014.pdf) · [文本](text/conditional-gan-2014.txt) | 条件生成对抗网络 |
| [Conditional Molecular Design with Deep Generative Models](https://arxiv.org/abs/1803.01096) | 未获取（failed） | 性质条件分子生成 |
| [Molecular generative model based on conditional variational autoencoder for de novo molecular design](https://jcheminf.biomedcentral.com/articles/10.1186/s13321-018-0286-7) | [原件](files/papers/cvae-mol-2018.html) · [文本](text/cvae-mol-2018.txt) | 条件变分自编码器生成（开放获取） |
| [A Survey of Uncertainty in Deep Neural Networks](https://arxiv.org/abs/2107.03342) | [原件](files/papers/uncertainty-dnn-2021.pdf) · [文本](text/uncertainty-dnn-2021.txt) | 预测不确定度的来源与估计方法 |
| [Inverse design in materials genomics: forward-to-inverse materials design](https://doi.org/10.1038/natrevmats.2018.5) | [原件](files/papers/zunger-2018.html) · [文本](text/zunger-2018.txt)（access_required） | 材料逆向设计的定位综述（订阅来源） |
| [On-the-fly closed-loop materials discovery via Bayesian active learning](https://www.nature.com/articles/s41467-020-19597-w) | [原件](files/papers/kusne-2020.html) · [文本](text/kusne-2020.txt)（access_required） | 闭环主动学习与实验回流（开放获取） |
| [Machine-learning-assisted materials discovery using failed experiments](https://doi.org/10.1038/nature17439) | [原件](files/papers/raccuglia-2016.html) · [文本](text/raccuglia-2016.txt)（access_required） | 负结果用于约束可行域（订阅来源） |
| [Active learning in materials science with emphasis on adaptive sampling using uncertainties for targeted design](https://www.nature.com/articles/s41524-019-0153-8) | [原件](files/papers/lookman-2019.html) · [文本](text/lookman-2019.txt)（access_required） | 不确定性驱动的主动采样（开放获取） |
| [Practical Bayesian Optimization of Machine Learning Algorithms](https://arxiv.org/abs/1206.2944) | [原件](files/papers/snoek-2012.pdf) · [文本](text/snoek-2012.txt) | 贝叶斯优化采集函数与实践 |
| [Batch Bayesian Optimization via Local Penalization](https://arxiv.org/abs/1505.08052) | [原件](files/papers/batch-bayesopt-2018.pdf) · [文本](text/batch-bayesopt-2018.txt) | 批量采集与并行评估 |
| [GraphINVENT: A graph-based generative model for molecular design](https://github.com/MolecularAI/GraphINVENT) | [原件](files/datasets/graphinvent-2021.html) · [文本](text/graphinvent-2021.txt) | 图生成模型的开源实现 |

## 第 11 章 主动学习、贝叶斯优化与强化学习

| 资料 | 本地文件 | 用途 |
| --- | --- | --- |
| [Deep learning for polymer property prediction with limited data](https://arxiv.org/abs/2004.10122) | [原件](files/papers/deeppolymer-2020.pdf) · [文本](text/deeppolymer-2020.txt) | 小数据下的聚合物性质预测 |
| [Gaussian Processes for Machine Learning](http://www.gaussianprocess.org/gpml/) | [原件](files/documents/gpml-2006.html) · [文本](text/gpml-2006.txt) | 高斯过程回归教材 |
| [A Tutorial on Bayesian Optimization](https://arxiv.org/abs/1807.02811) | [原件](files/papers/bo-review-2018.pdf) · [文本](text/bo-review-2018.txt) | 贝叶斯优化综述 |
| [A self-driving laboratory for accelerated discovery of thin-film materials](https://www.science.org/doi/10.1126/sciadv.aaz8867) | 未获取（failed） | 自驱动实验室案例 |
| [Tutorial: AI-assisted exploration and active design of polymers with high intrinsic thermal conductivity](https://arxiv.org/abs/2403.15887) | [原件](files/papers/thermal-cond-tutorial-2024.pdf) · [文本](text/thermal-cond-tutorial-2024.txt) | 热导设计的方法流程 |
| [On-the-fly active learning of interpretable Bayesian force fields](https://arxiv.org/abs/2003.01831) | [原件](files/papers/flare-2020.pdf) · [文本](text/flare-2020.txt) | 在线主动学习力场与不确定性驱动采样 |
| [Graph Convolutional Policy Network for Goal-Directed Molecular Graph Generation](https://arxiv.org/abs/1806.02473) | [原件](files/papers/gcpn-2018.pdf) · [文本](text/gcpn-2018.txt) | 目标导向的图生成与强化学习 |
| [Molecular de-novo design through deep reinforcement learning](https://jcheminf.biomedcentral.com/articles/10.1186/s13321-017-0235-x) | [原件](files/papers/reinvent-2017.html) · [文本](text/reinvent-2017.txt) | 强化学习序列生成与先验策略（开放获取） |
| [A fast and elitist multiobjective genetic algorithm: NSGA-II](https://doi.org/10.1109/4235.996017) | [原件](files/papers/nsga2-2002.html) · [文本](text/nsga2-2002.txt)（incomplete_text） | 非支配排序遗传算法（订阅来源） |
| [ParEGO: A hybrid algorithm with on-line landscape approximation for expensive multiobjective optimization problems](https://doi.org/10.1109/TEVC.2005.851274) | [原件](files/papers/parego-2006.html) · [文本](text/parego-2006.txt)（incomplete_text） | 多目标贝叶斯优化与标量化（订阅来源） |
| [Differentiable Expected Hypervolume Improvement for Parallel Multi-Objective Bayesian Optimization](https://arxiv.org/abs/2006.05078) | [原件](files/papers/ehvi-2020.pdf) · [文本](text/ehvi-2020.txt) | 超体积提升与多目标采集函数 |
| [Performance assessment of multiobjective optimizers: an analysis of the hypervolume measure](https://doi.org/10.1109/TEVC.2003.810758) | [原件](files/papers/hypervolume-2003.html) · [文本](text/hypervolume-2003.txt)（incomplete_text） | 超体积指标的定义与性质（订阅来源） |
| [A tutorial on multiobjective optimization: fundamentals and evolutionary methods](https://doi.org/10.1007/s11047-018-9685-y) | [原件](files/papers/multiobjective-tutorial-2018.html) · [文本](text/multiobjective-tutorial-2018.txt) | 多目标优化与前沿覆盖教程 |
| [A Survey of Uncertainty in Deep Neural Networks](https://arxiv.org/abs/2107.03342) | [原件](files/papers/uncertainty-dnn-2021.pdf) · [文本](text/uncertainty-dnn-2021.txt) | 预测不确定度的来源与估计方法 |
| [On-the-fly closed-loop materials discovery via Bayesian active learning](https://www.nature.com/articles/s41467-020-19597-w) | [原件](files/papers/kusne-2020.html) · [文本](text/kusne-2020.txt)（access_required） | 闭环主动学习与实验回流（开放获取） |
| [Machine-learning-assisted materials discovery using failed experiments](https://doi.org/10.1038/nature17439) | [原件](files/papers/raccuglia-2016.html) · [文本](text/raccuglia-2016.txt)（access_required） | 负结果用于约束可行域（订阅来源） |
| [Active learning in materials science with emphasis on adaptive sampling using uncertainties for targeted design](https://www.nature.com/articles/s41524-019-0153-8) | [原件](files/papers/lookman-2019.html) · [文本](text/lookman-2019.txt)（access_required） | 不确定性驱动的主动采样（开放获取） |
| [Practical Bayesian Optimization of Machine Learning Algorithms](https://arxiv.org/abs/1206.2944) | [原件](files/papers/snoek-2012.pdf) · [文本](text/snoek-2012.txt) | 贝叶斯优化采集函数与实践 |
| [Batch Bayesian Optimization via Local Penalization](https://arxiv.org/abs/1505.08052) | [原件](files/papers/batch-bayesopt-2018.pdf) · [文本](text/batch-bayesopt-2018.txt) | 批量采集与并行评估 |
| [Simple and Scalable Predictive Uncertainty Estimation using Deep Ensembles](https://arxiv.org/abs/1612.01474) | [原件](files/papers/deep-ensembles-2017.pdf) · [文本](text/deep-ensembles-2017.txt) | 深度集成方差与预测不确定度 |
| [Gaussian Process Optimization in the Bandit Setting: No Regret and Experimental Design](https://arxiv.org/abs/0912.3995) | [原件](files/papers/gp-ucb-2010.pdf) · [文本](text/gp-ucb-2010.txt) | GP-UCB：置信上界采集与遗憾界（开放获取） |
| [A Tutorial on Bayesian Optimization of Expensive Cost Functions, with Application to Active User Modeling and Hierarchical Reinforcement Learning](https://arxiv.org/abs/1012.2599) | [原件](files/papers/ei-tutorial-2010.pdf) · [文本](text/ei-tutorial-2010.txt) | EI、PI 与 UCB 三种采集函数的推导与比较（开放获取） |
| [Maximizing Acquisition Functions for Bayesian Optimization](https://arxiv.org/abs/1805.10196) | [原件](files/papers/batch-bo-2018.pdf) · [文本](text/batch-bo-2018.txt) | 批量采集：并行化采集函数最大化（开放获取） |
| [Bayesian Optimization with Unknown Constraints](https://arxiv.org/abs/1403.5607) | [原件](files/papers/constrained-bo-2014.pdf) · [文本](text/constrained-bo-2014.txt) | 未知约束的贝叶斯优化与可行性概率（开放获取） |
| [Constrained Bayesian Optimization with Noisy Experiments](https://arxiv.org/abs/1706.07094) | [原件](files/papers/constrained-bo-2017.pdf) · [文本](text/constrained-bo-2017.txt) | 噪声实验下的约束贝叶斯优化（开放获取） |
| [Multi-fidelity Bayesian Optimisation with Continuous Approximations](https://arxiv.org/abs/1703.06240) | [原件](files/papers/multifidelity-bo-2017.pdf) · [文本](text/multifidelity-bo-2017.txt) | 多保真贝叶斯优化与保真度连续近似（开放获取） |
| [A General Framework for Multi-fidelity Bayesian Optimization with Gaussian Processes](https://arxiv.org/abs/1811.02770) | [原件](files/papers/multifidelity-bo-2019.pdf) · [文本](text/multifidelity-bo-2019.txt) | 多保真高斯过程优化的统一框架（开放获取） |
| [Cost-aware Bayesian Optimization](https://arxiv.org/abs/2003.10870) | [原件](files/papers/cost-aware-bo-2020.pdf) · [文本](text/cost-aware-bo-2020.txt) | 成本感知采集与预算分配（开放获取） |
| [Determinantal Point Processes for Machine Learning](https://arxiv.org/abs/1207.6083) | [原件](files/papers/dpp-2012.pdf) · [文本](text/dpp-2012.txt) | 行列式点过程与批量多样性（开放获取） |
| [BatchBALD: Efficient and Diverse Batch Acquisition for Deep Bayesian Active Learning](https://arxiv.org/abs/1906.00910) | [原件](files/papers/batchbald-2019.pdf) · [文本](text/batchbald-2019.txt) | 批量主动学习中的信息量与去相关（开放获取） |
| [A Survey of Deep Active Learning](https://arxiv.org/abs/2009.00236) | [原件](files/papers/active-learning-review-2021.pdf) · [文本](text/active-learning-review-2021.txt) | 深度主动学习综述：不确定性、代表性与批量（开放获取） |
| [Playing Atari with Deep Reinforcement Learning](https://arxiv.org/abs/1312.5602) | [原件](files/papers/dqn-2013.pdf) · [文本](text/dqn-2013.txt) | 深度 Q 网络与值函数近似（开放获取） |
| [Proximal Policy Optimization Algorithms](https://arxiv.org/abs/1707.06347) | [原件](files/papers/ppo-2017.pdf) · [文本](text/ppo-2017.txt) | PPO 裁剪目标与策略优化（开放获取） |
| [Optimization of Molecules via Deep Reinforcement Learning](https://arxiv.org/abs/1810.08647) | [原件](files/papers/molrl-2019.pdf) · [文本](text/molrl-2019.txt) | 分子设计的深度强化学习与奖励设计（开放获取） |
| [Offline Reinforcement Learning: Tutorial, Review, and Perspectives on Open Problems](https://arxiv.org/abs/2005.01643) | [原件](files/papers/offline-rl-2020.pdf) · [文本](text/offline-rl-2020.txt) | 离线强化学习的问题设定与样本效率（开放获取） |
| [Conservative Q-Learning for Offline Reinforcement Learning](https://arxiv.org/abs/2006.04779) | [原件](files/papers/cql-2020.pdf) · [文本](text/cql-2020.txt) | 保守 Q 学习与分布外动作抑制（开放获取） |
| [Deep Reinforcement Learning in a Handful of Trials using Probabilistic Dynamics Models](https://arxiv.org/abs/1805.12114) | [原件](files/papers/mbrl-pets-2018.pdf) · [文本](text/mbrl-pets-2018.txt) | 基于概率动力学模型的高样本效率强化学习（开放获取） |
| [Benchmarking the performance of Bayesian optimization across multiple experimental materials science domains](https://www.nature.com/articles/s41524-021-00656-9) | [原件](files/papers/bo-materials-2021.pdf) · [文本](text/bo-materials-2021.txt) | 材料实验中的贝叶斯优化基准（开放获取） |

## 第 12 章 反应预测、聚合建模与可合成性

| 资料 | 本地文件 | 用途 |
| --- | --- | --- |
| [PoLyInfo polymer database](https://polymer.nims.go.jp/) | [原件](files/datasets/polyinfo-2021.html) · [文本](text/polyinfo-2021.txt) | 实验与计算聚合物性质数据库 |
| [PI1M: A Benchmark Database for Polymer Informatics](https://pubs.acs.org/doi/10.1021/acs.jcim.0c00726) | 未获取（failed） | 百万级聚合物虚拟库 |
| [Open Macromolecular Genome](https://github.com/TheJacksonLab/OpenMacromolecularGenome) | [原件](files/datasets/open-macromolecular-genome.html) · [文本](text/open-macromolecular-genome.txt) | 可合成聚合物的开放基因组 |
| [SMiPoly: Generation of a Synthesizable Polymer Virtual Library](https://pubs.acs.org/doi/10.1021/acs.jcim.3c00277) | 未获取（failed） | 可合成虚拟库生成 |
| [RDKit: Open-source cheminformatics](https://www.rdkit.org/) | [原件](files/documents/rdkit-tools.html) · [文本](text/rdkit-tools.txt) | 指纹、描述符与分子处理 |
| [Autonomous experimentation systems for materials development](https://www.nature.com/articles/s41578-023-00587-5) | [原件](files/papers/self-driving-lab-review-2023.html) · [文本](text/self-driving-lab-review-2023.txt)（access_required） | 自主实验系统综述 |
| [Autonomous chemical research with large language models](https://www.nature.com/articles/s41586-023-06792-0) | [原件](files/papers/coscientist-2023.html) · [文本](text/coscientist-2023.txt)（access_required） | LLM 驱动的自主化学研究 |
| [ChemCrow: Augmenting large-language models with chemistry tools](https://www.science.org/doi/10.1126/sciadv.adk1059) | 未获取（failed） | 化学工具调用智能体 |
| [Estimation of synthetic accessibility score of drug-like molecules based on molecular complexity and fragment contributions](https://jcheminf.biomedcentral.com/articles/10.1186/1758-2946-1-8) | [原件](files/papers/sa-score-2009.html) · [文本](text/sa-score-2009.txt) | 可合成性评分的片段贡献法 |
| [Analyzing Learned Molecular Representations for Property Prediction](https://arxiv.org/abs/1904.01561) | [原件](files/papers/chemprop-2019.pdf) · [文本](text/chemprop-2019.txt) | Chemprop：有向消息传递与分子性质预测 |
| [Copolymerization. I. A Basis for Comparing the Behavior of Monomers in Copolymerization](https://pubs.acs.org/doi/10.1021/ja01237a052) | 未获取（failed） | 竞聚率与共聚组成方程的原始工作（订阅来源） |
| [Molecular Size Distribution in Ethylene Oxide Polymers](https://pubs.acs.org/doi/10.1021/ja01863a066) | 未获取（failed） | 逐步聚合链长分布的原始工作（订阅来源） |
| [Atom Transfer Radical Polymerization](https://pubs.acs.org/doi/10.1021/cr940534g) | 未获取（failed） | ATRP 机理与动力学综述（订阅来源） |
| [Living Free-Radical Polymerization by Reversible Addition-Fragmentation Chain Transfer](https://pubs.acs.org/doi/10.1021/ma9804951) | 未获取（failed） | RAFT 可逆链转移的原始工作（订阅来源） |
| [Planning chemical syntheses with deep neural networks and symbolic AI](https://www.nature.com/articles/nature25978) | [原件](files/papers/retrosynthesis-segler-2018.html) · [文本](text/retrosynthesis-segler-2018.txt)（access_required） | 神经网络加蒙特卡洛树搜索的逆合成规划 |
| [Molecular Transformer: A Model for Uncertainty-Calibrated Chemical Reaction Prediction](https://arxiv.org/abs/1811.06038) | [原件](files/papers/molecular-transformer-2019.pdf) · [文本](text/molecular-transformer-2019.txt) | 序列到序列反应预测与不确定性校准 |
| [AiZynthFinder: a fast, robust and flexible open-source software for retrosynthetic planning](https://jcheminf.biomedcentral.com/articles/10.1186/s13321-020-00474-z) | [原件](files/papers/aizynthfinder-2020.html) · [文本](text/aizynthfinder-2020.txt) | 开源逆合成规划工具 |
| [Machine learning in chemical reaction space](https://www.nature.com/articles/s41467-020-19326-3) | [原件](files/papers/stuyver-coley-2020.html) · [文本](text/stuyver-coley-2020.txt)（access_required） | 反应空间建模与条件预测 |
| [Predicting reaction performance in C-N cross-coupling using machine learning](https://www.science.org/doi/10.1126/science.aar5169) | 未获取（failed） | 条件特征主导产率预测的实验证据（订阅来源） |
| [The Open Reaction Database](https://pubs.acs.org/doi/10.1021/jacs.1c09820) | 未获取（failed） | 开放反应数据平台（订阅来源） |
| [SCScore: Synthetic Complexity Learned from a Reaction Corpus](https://pubs.acs.org/doi/10.1021/acs.jcim.7b00622) | 未获取（failed） | 反应语料训练的合成复杂度分数（订阅来源） |

## 第 13 章 自驱动实验室与高通量自动化

| 资料 | 本地文件 | 用途 |
| --- | --- | --- |
| [Machine learning discovery of high thermal conductivity polymers](https://www.nature.com/articles/s41524-019-0247-3) | [原件](files/papers/thermal-conductivity-ml-2019.pdf) · [文本](text/thermal-conductivity-ml-2019.txt) | 高通量筛选与热导率预测 |
| [Deep learning for polymer property prediction with limited data](https://arxiv.org/abs/2004.10122) | [原件](files/papers/deeppolymer-2020.pdf) · [文本](text/deeppolymer-2020.txt) | 小数据下的聚合物性质预测 |
| [A Tutorial on Bayesian Optimization](https://arxiv.org/abs/1807.02811) | [原件](files/papers/bo-review-2018.pdf) · [文本](text/bo-review-2018.txt) | 贝叶斯优化综述 |
| [A self-driving laboratory for accelerated discovery of thin-film materials](https://www.science.org/doi/10.1126/sciadv.aaz8867) | 未获取（failed） | 自驱动实验室案例 |
| [Autonomous experimentation systems for materials development](https://www.nature.com/articles/s41578-023-00587-5) | [原件](files/papers/self-driving-lab-review-2023.html) · [文本](text/self-driving-lab-review-2023.txt)（access_required） | 自主实验系统综述 |
| [An autonomous laboratory for the accelerated synthesis of novel materials](https://www.nature.com/articles/s41586-023-06734-w) | [原件](files/papers/alab-2023.html) · [文本](text/alab-2023.txt)（access_required） | A-Lab 自主合成 |
| [Autonomous chemical research with large language models](https://www.nature.com/articles/s41586-023-06792-0) | [原件](files/papers/coscientist-2023.html) · [文本](text/coscientist-2023.txt)（access_required） | LLM 驱动的自主化学研究 |
| [Graph Convolutional Policy Network for Goal-Directed Molecular Graph Generation](https://arxiv.org/abs/1806.02473) | [原件](files/papers/gcpn-2018.pdf) · [文本](text/gcpn-2018.txt) | 目标导向的图生成与强化学习 |
| [Simple and Scalable Predictive Uncertainty Estimation using Deep Ensembles](https://arxiv.org/abs/1612.01474) | [原件](files/papers/deep-ensembles-2017.pdf) · [文本](text/deep-ensembles-2017.txt) | 深度集成方差与预测不确定度 |
| [AiZynthFinder: a fast, robust and flexible open-source software for retrosynthetic planning](https://jcheminf.biomedcentral.com/articles/10.1186/s13321-020-00474-z) | [原件](files/papers/aizynthfinder-2020.html) · [文本](text/aizynthfinder-2020.txt) | 开源逆合成规划工具 |
| [Maximizing Acquisition Functions for Bayesian Optimization](https://arxiv.org/abs/1805.10196) | [原件](files/papers/batch-bo-2018.pdf) · [文本](text/batch-bo-2018.txt) | 批量采集：并行化采集函数最大化（开放获取） |
| [A General Framework for Multi-fidelity Bayesian Optimization with Gaussian Processes](https://arxiv.org/abs/1811.02770) | [原件](files/papers/multifidelity-bo-2019.pdf) · [文本](text/multifidelity-bo-2019.txt) | 多保真高斯过程优化的统一框架（开放获取） |
| [Cost-aware Bayesian Optimization](https://arxiv.org/abs/2003.10870) | [原件](files/papers/cost-aware-bo-2020.pdf) · [文本](text/cost-aware-bo-2020.txt) | 成本感知采集与预算分配（开放获取） |
| [Determinantal Point Processes for Machine Learning](https://arxiv.org/abs/1207.6083) | [原件](files/papers/dpp-2012.pdf) · [文本](text/dpp-2012.txt) | 行列式点过程与批量多样性（开放获取） |
| [A Survey of Deep Active Learning](https://arxiv.org/abs/2009.00236) | [原件](files/papers/active-learning-review-2021.pdf) · [文本](text/active-learning-review-2021.txt) | 深度主动学习综述：不确定性、代表性与批量（开放获取） |
| [Benchmarking the performance of Bayesian optimization across multiple experimental materials science domains](https://www.nature.com/articles/s41524-021-00656-9) | [原件](files/papers/bo-materials-2021.pdf) · [文本](text/bo-materials-2021.txt) | 材料实验中的贝叶斯优化基准（开放获取） |
| [Bayesian Active Learning for Scanning Probe Microscopy: from Gaussian Processes to Hypothesis Learning](https://arxiv.org/abs/2205.15458) | [原件](files/papers/spm-active-learning-2022.pdf) · [文本](text/spm-active-learning-2022.txt) | 扫描探针显微镜的贝叶斯主动测量 |
| [ChemOS: An orchestration software to democratize autonomous discovery](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0229862) | [原件](files/papers/chemos-2020.html) · [文本](text/chemos-2020.txt) | 自主实验编排软件 |
| [AiiDA: Automated Interactive Infrastructure and Database for Computational Science](https://arxiv.org/abs/1504.01163) | [原件](files/papers/aiida-2016.pdf) · [文本](text/aiida-2016.txt) | 计算工作流管理与溯源 |
| [Optuna: A Next-generation Hyperparameter Optimization Framework](https://arxiv.org/abs/1907.10902) | [原件](files/papers/optuna-2019.pdf) · [文本](text/optuna-2019.txt) | 调度与超参搜索软件 |
| [BoTorch: A Framework for Efficient Monte-Carlo Bayesian Optimization](https://arxiv.org/abs/1910.06403) | [原件](files/papers/botorch-2019.pdf) · [文本](text/botorch-2019.txt) | 贝叶斯优化软件栈 |
| [The Evolution of Materials Acceleration Platforms -- Towards the Laboratory of the Future with AMANDA](https://arxiv.org/abs/2104.07455) | [原件](files/papers/amanda-2021.pdf) · [文本](text/amanda-2021.txt) | 材料加速平台的软硬件架构 |
| [Search Strategies for Self-driving Laboratories with Pending Experiments](https://arxiv.org/abs/2312.03466) | [原件](files/papers/pending-experiments-2023.pdf) · [文本](text/pending-experiments-2023.txt) | 有在途实验时的调度策略 |
| [Self-driving laboratory for accelerated discovery of thin-film materials](https://arxiv.org/abs/1906.05398) | [原件](files/papers/self-driving-lab-thinfilm-2019.pdf) · [文本](text/self-driving-lab-thinfilm-2019.txt) | 薄膜自驱动实验室预印本 |
| [PANDA: A self-driving lab for studying electrodeposited polymer films](https://arxiv.org/abs/2406.17725) | [原件](files/papers/panda-2024.pdf) · [文本](text/panda-2024.txt) | 聚合物薄膜自驱动实验室 |
| [Self-Driving Laboratory Optimizes the Lower Critical Solution Temperature of Thermoresponsive Polymers](https://arxiv.org/abs/2509.05351) | [原件](files/papers/sdl-lcst-2025.pdf) · [文本](text/sdl-lcst-2025.txt) | 温敏聚合物自驱动实验室 |
| [Beyond Ternary OPV: High-Throughput Experimentation and Self-Driving Laboratories Optimize Multi-Component Systems](https://arxiv.org/abs/1909.03511) | [原件](files/papers/opv-self-driving-2019.pdf) · [文本](text/opv-self-driving-2019.txt) | 高通量与自驱动实验室优化多元体系 |

## 第 14 章 高分子基础模型与智能体系统

| 资料 | 本地文件 | 用途 |
| --- | --- | --- |
| [SMILES, a chemical language and information system](https://pubs.acs.org/doi/10.1021/ci00057a005) | 未获取（failed） | 字符串表示的原始工作 |
| [BigSMILES: A Structurally-Based Line Notation for Describing Macromolecules](https://pubs.acs.org/doi/10.1021/acscentsci.9b00476) | 未获取（failed） | 随机结构高分子的字符串表示 |
| [PolyBERT: a chemical language model to enable fully machine-driven ultrafast polymer informatics](https://www.nature.com/articles/s41467-023-39868-6) | [原件](files/papers/polybert-2023.pdf) · [文本](text/polybert-2023.txt) | 聚合物语言模型与表示 |
| [Autonomous chemical research with large language models](https://www.nature.com/articles/s41586-023-06792-0) | [原件](files/papers/coscientist-2023.html) · [文本](text/coscientist-2023.txt)（access_required） | LLM 驱动的自主化学研究 |
| [ChemCrow: Augmenting large-language models with chemistry tools](https://www.science.org/doi/10.1126/sciadv.adk1059) | 未获取（failed） | 化学工具调用智能体 |
| [Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks](https://arxiv.org/abs/2005.11401) | [原件](files/papers/rag-2020.pdf) · [文本](text/rag-2020.txt) | 检索增强生成 |
| [ChemBERTa: Large-Scale Self-Supervised Pretraining for Molecular Property Prediction](https://arxiv.org/abs/2010.09885) | [原件](files/papers/chemberta-2022.pdf) · [文本](text/chemberta-2022.txt) | 字符串自监督预训练表示 |
| [TransPolymer: a Transformer-based language model for polymer property predictions](https://www.nature.com/articles/s41524-023-01016-5) | [原件](files/papers/transpolymer-2023.pdf) · [文本](text/transpolymer-2023.txt) | 聚合物 Transformer 表示与预训练 |
| [A universal graph deep learning interatomic potential for the periodic table](https://arxiv.org/abs/2202.02450) | [原件](files/papers/m3gnet-2022.pdf) · [文本](text/m3gnet-2022.txt) | 通用图势：周期表覆盖与材料筛选 |
| [GROMACS: High performance molecular simulations through multi-level parallelism from laptops to supercomputers](https://www.sciencedirect.com/science/article/pii/S2352711015000059) | 未获取（failed） | GROMACS 5：多级并行的分子模拟 |
| [Attention Is All You Need](https://arxiv.org/abs/1706.03762) | [原件](files/papers/transformer-2017.pdf) · [文本](text/transformer-2017.txt) | Transformer：自注意力架构 |
| [BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding](https://arxiv.org/abs/1810.04805) | [原件](files/papers/bert-2019.pdf) · [文本](text/bert-2019.txt) | 掩码语言建模预训练 |
| [Uni-Mol: A Universal 3D Molecular Representation Learning Framework](https://arxiv.org/abs/2110.01191) | [原件](files/papers/unimol-2023.pdf) · [文本](text/unimol-2023.txt) | 三维分子表示的去噪预训练 |
| [Large-Scale Chemical Language Representations Capture Molecular Structure and Properties](https://arxiv.org/abs/2106.09553) | [原件](files/papers/molformer-2022.pdf) · [文本](text/molformer-2022.txt) | 大规模化学语言表示 |
| [Multi-modal Molecule Structure-text Model for Text-based Retrieval and Editing](https://arxiv.org/abs/2212.10789) | [原件](files/papers/moleculestm-2023.pdf) · [文本](text/moleculestm-2023.txt) | 结构–文本多模态分子模型 |
| [Dense Passage Retrieval for Open-Domain Question Answering](https://arxiv.org/abs/2004.04906) | [原件](files/papers/dpr-2020.pdf) · [文本](text/dpr-2020.txt) | 稠密段落检索 |
| [REALM: Retrieval-Augmented Language Model Pre-Training](https://arxiv.org/abs/2002.08909) | [原件](files/papers/realm-2020.pdf) · [文本](text/realm-2020.txt) | 检索增强的语言模型预训练 |
| [Self-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection](https://arxiv.org/abs/2310.11511) | [原件](files/papers/self-rag-2024.pdf) · [文本](text/self-rag-2024.txt) | 自评检索与生成 |
| [Retrieval-Augmented Generation for Large Language Models: A Survey](https://arxiv.org/abs/2312.10997) | [原件](files/papers/rag-survey-2023.pdf) · [文本](text/rag-survey-2023.txt) | 检索增强生成综述 |
| [Lost in the Middle: How Language Models Use Long Contexts](https://arxiv.org/abs/2307.03172) | [原件](files/papers/lost-in-middle-2023.pdf) · [文本](text/lost-in-middle-2023.txt) | 长上下文的位置效应 |
| [Enabling Large Language Models to Generate Text with Citations](https://arxiv.org/abs/2305.14627) | [原件](files/papers/alce-2023.pdf) · [文本](text/alce-2023.txt) | 带引用的生成与评测 |
| [BEIR: A Heterogeneous Benchmark for Zero-shot Evaluation of Information Retrieval Models](https://arxiv.org/abs/2104.08663) | [原件](files/papers/beir-2021.pdf) · [文本](text/beir-2021.txt) | 检索模型零样本基准 |
| [ReAct: Synergizing Reasoning and Acting in Language Models](https://arxiv.org/abs/2210.03629) | [原件](files/papers/react-2023.pdf) · [文本](text/react-2023.txt) | 推理与行动交替的智能体 |
| [Toolformer: Language Models Can Teach Themselves to Use Tools](https://arxiv.org/abs/2302.04761) | [原件](files/papers/toolformer-2023.pdf) · [文本](text/toolformer-2023.txt) | 自监督学习工具调用 |
| [Reflexion: Language Agents with Verbal Reinforcement Learning](https://arxiv.org/abs/2303.11366) | [原件](files/papers/reflexion-2023.pdf) · [文本](text/reflexion-2023.txt) | 语言反馈改进智能体 |
| [Program-Aided Language Models](https://arxiv.org/abs/2211.10435) | [原件](files/papers/program-aided-2023.pdf) · [文本](text/program-aided-2023.txt) | 把推理外包给程序 |
| [ToolLLM: Facilitating Large Language Models to Master 16000+ Real-world APIs](https://arxiv.org/abs/2307.16789) | [原件](files/papers/toolllm-2023.pdf) · [文本](text/toolllm-2023.txt) | 大规模工具调用 |
| [AgentBench: Evaluating LLMs as Agents](https://arxiv.org/abs/2308.03688) | [原件](files/papers/agentbench-2023.pdf) · [文本](text/agentbench-2023.txt) | 智能体评测基准 |
| [AutoGen: Enabling Next-Gen LLM Applications via Multi-Agent Conversation](https://arxiv.org/abs/2308.08155) | [原件](files/papers/autogen-2023.pdf) · [文本](text/autogen-2023.txt) | 多智能体对话框架 |
| [A Survey on Large Language Model based Autonomous Agents](https://arxiv.org/abs/2308.11432) | [原件](files/papers/agents-survey-2024.pdf) · [文本](text/agents-survey-2024.txt) | 自主智能体综述 |
| [A Survey of Hallucination in Natural Language Generation](https://arxiv.org/abs/2202.03629) | [原件](files/papers/hallucination-survey-2023.pdf) · [文本](text/hallucination-survey-2023.txt) | 幻觉分类与评测 |
| [TruthfulQA: Measuring How Models Mimic Human Falsehoods](https://arxiv.org/abs/2109.07958) | [原件](files/papers/truthfulqa-2022.pdf) · [文本](text/truthfulqa-2022.txt) | 事实性问答基准 |

## 第 15 章 可持续高分子与环境应用

| 资料 | 本地文件 | 用途 |
| --- | --- | --- |
| [Polymer dielectrics for high-temperature capacitive energy storage](https://pubs.acs.org/doi/10.1021/acs.chemrev.1c00968) | 未获取（failed） | 介电储能综述，被引最高的领域文献 |
| [Machine learning for sustainable polymer design](https://www.nature.com/articles/s41578-024-00654-5) | [原件](files/papers/sustainable-polymers-ai-2024.html) · [文本](text/sustainable-polymers-ai-2024.txt)（access_required） | 可持续高分子与 AI 的结合 |
| [Machine learning discovery of high thermal conductivity polymers](https://www.nature.com/articles/s41524-019-0247-3) | [原件](files/papers/thermal-conductivity-ml-2019.pdf) · [文本](text/thermal-conductivity-ml-2019.txt) | 高通量筛选与热导率预测 |
| [Machine learning–enabled high-throughput screening of polymers for gas separation](https://www.science.org/doi/10.1126/sciadv.abc6216) | 未获取（failed） | 膜分离材料筛选 |
| [Open Polymer Challenge: Post-Competition Report](https://arxiv.org/abs/2512.08896) | [原件](files/papers/open-polymer-challenge-2025.pdf) · [文本](text/open-polymer-challenge-2025.txt) | 竞赛赛后报告与基准记录 |
| [AI-guided inverse design and discovery of recyclable vitrimeric polymers](https://arxiv.org/abs/2312.03690) | [原件](files/papers/vitrimer-inverse-2023.pdf) · [文本](text/vitrimer-inverse-2023.txt) | 可回收聚合物的生成式逆向设计 |
| [An Informatics Framework for the Design of Sustainable, Chemically Recyclable, Synthetically Accessible Polymers](https://arxiv.org/abs/2409.15354) | [原件](files/papers/informatics-recyclable-2024.pdf) · [文本](text/informatics-recyclable-2024.txt) | 化学可回收高分子的信息学筛选框架 |
| [AI-assisted design of chemically recyclable polymers for food packaging](https://arxiv.org/abs/2511.04704) | [原件](files/papers/ai-recyclable-food-packaging-2025.pdf) · [文本](text/ai-recyclable-food-packaging-2025.txt) | AI 设计化学可回收包装聚合物 |
| [From fragmented data to actionable design: Physics-calibrated learning for plastic upcycling](https://arxiv.org/abs/2608.02402) | [原件](files/papers/plastic-upcycling-ml-2026.pdf) · [文本](text/plastic-upcycling-ml-2026.txt) | 物理校准学习用于塑料升级回收 |
| [From Plastic Waste to Treasure: Selective Upcycling through Catalytic Technologies](https://arxiv.org/abs/2309.08354) | [原件](files/papers/upcycling-catalysis-2023.pdf) · [文本](text/upcycling-catalysis-2023.txt) | 催化选择性升级回收综述 |
| [Life cycle assessment for all organic chemicals](https://arxiv.org/abs/2603.15686) | [原件](files/papers/lca-organic-chemicals-2026.pdf) · [文本](text/lca-organic-chemicals-2026.txt) | 有机物全生命周期评价方法 |
| [Mapping the Landscape of Artificial Intelligence in Life Cycle Assessment Using Large Language Models](https://arxiv.org/abs/2602.22500) | [原件](files/papers/ai-lca-landscape-2026.pdf) · [文本](text/ai-lca-landscape-2026.txt) | AI 与 LCA 结合的文献图谱 |
| [Evaluation of ML Resource Utilization Requires Model Life Cycle Assessment](https://arxiv.org/abs/2606.07632) | [原件](files/papers/ml-model-lca-2026.pdf) · [文本](text/ml-model-lca-2026.txt) | 把 LCA 用于机器学习模型自身 |
| [Sustainable Materials Discovery in the Era of Artificial Intelligence](https://arxiv.org/abs/2601.21527) | [原件](files/papers/sustainable-materials-ai-2026.pdf) · [文本](text/sustainable-materials-ai-2026.txt) | AI 驱动可持续材料发现综述 |
| [Bioplastic Design using Multitask Deep Neural Networks](https://arxiv.org/abs/2203.12033) | [原件](files/papers/bioplastic-multitask-2022.pdf) · [文本](text/bioplastic-multitask-2022.txt) | 多任务网络设计生物基塑料 |
| [Toward Sustainable Polymer Design: A Molecular Dynamics-Informed Machine Learning Approach](https://arxiv.org/abs/2503.20956) | [原件](files/papers/sustainable-polymer-md-ml-2025.pdf) · [文本](text/sustainable-polymer-md-ml-2025.txt) | 分子动力学信息指导可持续高分子设计 |
| [Recyclable vitrimer-based printed circuit board for circular electronics](https://arxiv.org/abs/2308.12496) | [原件](files/papers/recyclable-vitrimer-pcb-2023.pdf) · [文本](text/recyclable-vitrimer-pcb-2023.txt) | 可回收 vitrimer 电子基板 |
| [Predicting Polymer Solubility in Solvents Using SMILES Strings](https://arxiv.org/abs/2512.09784) | [原件](files/papers/polymer-solubility-smiles-2025.pdf) · [文本](text/polymer-solubility-smiles-2025.txt) | 绿色溶剂筛选的溶解度预测 |
| [Polyethylene-based thermo-mechanically recyclable stretchable yarns for circular sustainability](https://arxiv.org/abs/2606.07652) | [原件](files/papers/thermo-mech-recyclable-pe-2026.pdf) · [文本](text/thermo-mech-recyclable-pe-2026.txt) | 热机械可回收聚乙烯纤维 |
| [Prediction of terephthalic acid (TPA) yield in aqueous hydrolysis of polyethylene terephthalate](https://arxiv.org/abs/2201.12657) | [原件](files/papers/tpa-yield-pet-hydrolysis-2022.pdf) · [文本](text/tpa-yield-pet-hydrolysis-2022.txt) | PET 水解解聚产率预测 |
| [100 years of plastic -- using the past to guide the future](https://arxiv.org/abs/2411.13618) | [原件](files/papers/plastic-waste-100years-2024.pdf) · [文本](text/plastic-waste-100years-2024.txt) | 塑料百年史与循环路径 |
| [Sustainable bioplastics from amyloid fibril-biodegradable polymer blends](https://arxiv.org/abs/2105.14287) | [原件](files/papers/bioplastic-amyloid-2021.pdf) · [文本](text/bioplastic-amyloid-2021.txt) | 生物基可降解共混材料 |
| [Recyclable flame-retardant epoxy composites based on disulfide bonds. Flammability and recyclability](https://arxiv.org/abs/2105.02141) | [原件](files/papers/recyclable-flame-retardant-epoxy-2021.pdf) · [文本](text/recyclable-flame-retardant-epoxy-2021.txt) | 二硫键可回收环氧复合材料 |
| [AI-Assisted Physics-Informed Predictions of Degradation Behavior of Polymeric Anion Exchange Membranes](https://arxiv.org/abs/2510.12655) | [原件](files/papers/aem-degradation-pinn-2025.pdf) · [文本](text/aem-degradation-pinn-2025.txt) | 物理信息网络预测膜退化 |

## 第 16 章 端到端案例与工程实践

| 资料 | 本地文件 | 用途 |
| --- | --- | --- |
| [Polymer Genome: A Data-Powered Polymer Informatics Platform for Property Predictions](https://pubs.acs.org/doi/10.1021/acs.jpcc.8b02913) | 未获取（failed） | 多性质预测平台与描述符体系 |
| [Machine learning for sustainable polymer design](https://www.nature.com/articles/s41578-024-00654-5) | [原件](files/papers/sustainable-polymers-ai-2024.html) · [文本](text/sustainable-polymers-ai-2024.txt)（access_required） | 可持续高分子与 AI 的结合 |
| [Machine learning–enabled high-throughput screening of polymers for gas separation](https://www.science.org/doi/10.1126/sciadv.abc6216) | 未获取（failed） | 膜分离材料筛选 |
| [Benchmarking machine learning models for polymer informatics: glass transition temperature](https://pubs.acs.org/doi/10.1021/acs.jcim.0c01336) | 未获取（failed） | Tg 预测基准与数据划分 |
| [PolyBERT: a chemical language model to enable fully machine-driven ultrafast polymer informatics](https://www.nature.com/articles/s41467-023-39868-6) | [原件](files/papers/polybert-2023.pdf) · [文本](text/polybert-2023.txt) | 聚合物语言模型与表示 |
| [PI1M: A Benchmark Database for Polymer Informatics](https://pubs.acs.org/doi/10.1021/acs.jcim.0c00726) | 未获取（failed） | 百万级聚合物虚拟库 |
| [Open Macromolecular Genome](https://github.com/TheJacksonLab/OpenMacromolecularGenome) | [原件](files/datasets/open-macromolecular-genome.html) · [文本](text/open-macromolecular-genome.txt) | 可合成聚合物的开放基因组 |
| [NeurIPS Open Polymer Prediction 2025](https://www.kaggle.com/competitions/neurips-open-polymer-prediction-2025) | [原件](files/datasets/kaggle-polymer-2025.html) · [文本](text/kaggle-polymer-2025.txt)（incomplete_text） | 多性质预测竞赛与盲测 |
| [Autonomous experimentation systems for materials development](https://www.nature.com/articles/s41578-023-00587-5) | [原件](files/papers/self-driving-lab-review-2023.html) · [文本](text/self-driving-lab-review-2023.txt)（access_required） | 自主实验系统综述 |
| [MoleculeNet: A Benchmark for Molecular Machine Learning](https://pubs.rsc.org/en/content/articlelanding/2018/sc/c7sc02664a) | [原件](files/papers/moleculenet-2018.pdf) · [文本](text/moleculenet-2018.txt) | 小分子基准与划分策略 |
| [Most Ligand-Based Classification Benchmarks Reward Memorization Rather than Generalization](https://pubs.acs.org/doi/10.1021/acs.jcim.8b00025) | [原件](files/papers/scaffold-memorization-2018.pdf) · [文本](text/scaffold-memorization-2018.txt) | 随机划分高估性能与去泄漏 |
| [Open Polymer Challenge: Post-Competition Report](https://arxiv.org/abs/2512.08896) | [原件](files/papers/open-polymer-challenge-2025.pdf) · [文本](text/open-polymer-challenge-2025.txt) | 竞赛赛后报告与基准记录 |
| [Leakage and the Reproducibility Crisis in ML-based Science](https://arxiv.org/abs/2207.07048) | [原件](files/papers/kapoor-narayanan-2023.pdf) · [文本](text/kapoor-narayanan-2023.txt) | 数据泄漏与复现危机 |
| [DOME: Recommendations for supervised machine learning validation in biology](https://arxiv.org/abs/2006.16189) | [原件](files/papers/dome-2021.pdf) · [文本](text/dome-2021.txt) | 监督学习报告规范 |
| [The FAIR Guiding Principles for scientific data management and stewardship](https://www.nature.com/articles/sdata201618) | [原件](files/documents/fair-principles-2016.html) · [文本](text/fair-principles-2016.txt)（access_required） | 数据可发现、可访问、可互操作、可复用原则 |
| [Superior Polymeric Gas Separation Membrane Designed by Explainable Graph Machine Learning](https://arxiv.org/abs/2404.10903) | [原件](files/papers/gas-separation-gnn-2024.pdf) · [文本](text/gas-separation-gnn-2024.txt) | 可解释图学习与气体分离膜 |
| [The upper bound revisited](https://www.sciencedirect.com/science/article/abs/pii/S0376738808002544) | 未获取（failed） | Robeson 上界的更新（领域定位，订阅来源） |
| [AI-guided inverse design and discovery of recyclable vitrimeric polymers](https://arxiv.org/abs/2312.03690) | [原件](files/papers/vitrimer-inverse-2023.pdf) · [文本](text/vitrimer-inverse-2023.txt) | 可回收聚合物的生成式逆向设计 |
| [On-the-fly closed-loop materials discovery via Bayesian active learning](https://www.nature.com/articles/s41467-020-19597-w) | [原件](files/papers/kusne-2020.html) · [文本](text/kusne-2020.txt)（access_required） | 闭环主动学习与实验回流（开放获取） |
| [Machine-learning-assisted materials discovery using failed experiments](https://doi.org/10.1038/nature17439) | [原件](files/papers/raccuglia-2016.html) · [文本](text/raccuglia-2016.txt)（access_required） | 负结果用于约束可行域（订阅来源） |
| [Random Forests](https://doi.org/10.1023/A:1010933404324) | [原件](files/papers/random-forest-2001.html) · [文本](text/random-forest-2001.txt) | 随机森林原始工作（订阅来源） |
| [Greedy Function Approximation: A Gradient Boosting Machine](https://doi.org/10.1214/aos/1013203451) | [原件](files/papers/gradient-boosting-2001.html) · [文本](text/gradient-boosting-2001.txt)（incomplete_text） | 梯度提升的统计框架（订阅来源） |
| [XGBoost: A Scalable Tree Boosting System](https://arxiv.org/abs/1603.02754) | [原件](files/papers/xgboost-2016.pdf) · [文本](text/xgboost-2016.txt) | XGBoost：可扩展的树提升系统 |
| [Support-Vector Networks](https://doi.org/10.1007/BF00994018) | [原件](files/papers/svr-1995.html) · [文本](text/svr-1995.txt) | 支持向量回归与 ε 不敏感损失（订阅来源） |
| [Inductive Confidence Machines for Regression](https://link.springer.com/chapter/10.1007/3-540-36755-1_29) | [原件](files/papers/conformal-2002.html) · [文本](text/conformal-2002.txt) | split conformal 回归预测区间（订阅来源） |
| [Simple and Scalable Predictive Uncertainty Estimation using Deep Ensembles](https://arxiv.org/abs/1612.01474) | [原件](files/papers/deep-ensembles-2017.pdf) · [文本](text/deep-ensembles-2017.txt) | 深度集成方差与预测不确定度 |
| [Machine learning enables interpretable discovery of innovative polymers for gas separation membranes](https://doi.org/10.1126/sciadv.abn9545) | [原件](files/papers/polymer-gas-membrane-ml-2022.md) · [文本](text/polymer-gas-membrane-ml-2022.txt) | 气体分离膜渗透率数据仓库与可解释机器学习 |

## 获取记录

以下条目不能作为已经取得的完整资料：

- **polymer-informatics-2017**：failed；HTTPError: HTTP Error 403: Forbidden。
- **polymer-genome-2018**：failed；HTTPError: HTTP Error 403: Forbidden。
- **polymer-informatics-next-2021**：incomplete_text；正文少于 600 字符，未取得完整内容。
- **polymer-dielectrics-review-2022**：failed；HTTPError: HTTP Error 403: Forbidden。
- **sustainable-polymers-ai-2024**：access_required；订阅来源，需机构访问或作者手动补充。
- **gas-separation-ml-2020**：failed；HTTPError: HTTP Error 403: Forbidden。
- **tg-benchmark-2021**：failed；HTTPError: HTTP Error 403: Forbidden。
- **solubility-hansen-2019**：failed；HTTPError: HTTP Error 403: Forbidden。
- **smiles-1988**：failed；HTTPError: HTTP Error 403: Forbidden。
- **bigsmiles-2019**：failed；HTTPError: HTTP Error 403: Forbidden。
- **ecfp-rogers-hahn-2010**：failed；HTTPError: HTTP Error 403: Forbidden。
- **polygan-2020**：failed；HTTPError: HTTP Error 403: Forbidden。
- **pi1m-2020**：failed；HTTPError: HTTP Error 403: Forbidden。
- **smipoly-2023**：failed；HTTPError: HTTP Error 403: Forbidden。
- **kaggle-polymer-2025**：incomplete_text；正文少于 600 字符，未取得完整内容。
- **openmm-tools**：incomplete_text；正文少于 600 字符，未取得完整内容。
- **md-1957**：failed；HTTPError: HTTP Error 403: Forbidden。
- **self-driving-lab-2020**：failed；HTTPError: HTTP Error 403: Forbidden。
- **self-driving-lab-review-2023**：access_required；订阅来源，需机构访问或作者手动补充。
- **alab-2023**：access_required；订阅来源，需机构访问或作者手动补充。
- **coscientist-2023**：access_required；订阅来源，需机构访问或作者手动补充。
- **chemcrow-2023**：failed；HTTPError: HTTP Error 403: Forbidden。
- **mol2vec-2018**：failed；HTTPError: HTTP Error 403: Forbidden。
- **morgan-1965**：failed；HTTPError: HTTP Error 403: Forbidden。
- **fair-principles-2016**：access_required；订阅来源，需机构访问或作者手动补充。
- **fox-flory-1950**：failed；HTTPError: HTTP Error 403: Forbidden。
- **robeson-2008**：failed；HTTPError: HTTP Error 403: Forbidden。
- **wlf-1955**：failed；HTTPError: HTTP Error 403: Forbidden。
- **opls-aa-1996**：failed；HTTPError: HTTP Error 403: Forbidden。
- **gaff-2004**：failed；HTTPError: HTTP Error 403: Forbidden。
- **compass-1998**：failed；HTTPError: HTTP Error 403: Forbidden。
- **charmm-1998**：failed；HTTPError: HTTP Error 403: Forbidden。
- **martini-2007**：failed；HTTPError: HTTP Error 403: Forbidden。
- **ibi-2003**：failed；HTTPError: HTTP Error 403: Forbidden。
- **force-matching-2005**：failed；HTTPError: HTTP Error 403: Forbidden。
- **relative-entropy-2008**：failed；HTTPError: HTTP Error 403: Forbidden。
- **metadynamics-2002**：failed；HTTPError: HTTP Error 403: Forbidden。
- **umbrella-1977**：failed；HTTPError: HTTP Error 403: Forbidden。
- **wham-1992**：failed；HTTPError: HTTP Error 403: Forbidden。
- **replica-exchange-1999**：failed；HTTPError: HTTP Error 403: Forbidden。
- **gromacs-2015**：failed；HTTPError: HTTP Error 403: Forbidden。
- **d3-2010**：failed；HTTPError: HTTP Error 403: Forbidden。
- **pcff-1994**：failed；HTTPError: HTTP Error 403: Forbidden。
- **inverse-design-review-2018**：failed；HTTPError: HTTP Error 403: Forbidden。
- **nsga2-2002**：incomplete_text；正文少于 600 字符，未取得完整内容。
- **parego-2006**：incomplete_text；正文少于 600 字符，未取得完整内容。
- **hypervolume-2003**：incomplete_text；正文少于 600 字符，未取得完整内容。
- **conditional-mol-2018**：failed；HTTPError: HTTP Error 406: Not Acceptable。
- **zunger-2018**：access_required；订阅来源，需机构访问或作者手动补充。
- **kusne-2020**：access_required；订阅来源，需机构访问或作者手动补充。
- **raccuglia-2016**：access_required；订阅来源，需机构访问或作者手动补充。
- **lookman-2019**：access_required；订阅来源，需机构访问或作者手动补充。
- **gradient-boosting-2001**：incomplete_text；正文少于 600 字符，未取得完整内容。
- **mayo-lewis-1944**：failed；HTTPError: HTTP Error 403: Forbidden。
- **flory-1940**：failed；HTTPError: HTTP Error 403: Forbidden。
- **matyjaszewski-2001**：failed；HTTPError: HTTP Error 403: Forbidden。
- **raft-chiefari-1998**：failed；HTTPError: HTTP Error 403: Forbidden。
- **retrosynthesis-segler-2018**：access_required；订阅来源，需机构访问或作者手动补充。
- **stuyver-coley-2020**：access_required；订阅来源，需机构访问或作者手动补充。
- **ahneman-2018**：failed；HTTPError: HTTP Error 403: Forbidden。
- **ord-2021**：failed；HTTPError: HTTP Error 403: Forbidden。
- **scscore-2018**：failed；HTTPError: HTTP Error 403: Forbidden。

维护命令：`python3 references/fetch.py --only 资料ID` 下载指定条目；`--reindex` 只更新索引。直接运行会补齐失败或未获取的项目，保留已下载的快照。PDF 文本优先用 PyMuPDF 提取，缺失时回退到 Poppler 的 `pdftotext`。
