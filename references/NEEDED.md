# 参考文献获取状态与待补清单

> 更新：2026-09-17 · 共 289 条来源 · 由 `references/fetch.py` 自动获取

## 状态总览

| 状态 | 数量 | 含义 |
| --- | ---: | --- |
| `downloaded` | 226 | 已下载全文与可检索文本 |
| `user_provided` | 1 | 仓库内已有（WoS 导出） |
| `incomplete_text` | 7 | 拿到页面但正文过短，需人工补 |
| `access_required` | 11 | 订阅来源，需机构访问 |
| `failed` | 44 | 出版社反爬（HTTP 403），需浏览器手动下载 |

自动获取命令：`python3 references/fetch.py`（`--only <id>…` 只取指定条目，`--reindex` 只重建索引）。
索引见 `references/README.md` 与 `references/index.md`。

---

## 一、需手动补充：出版社反爬（44 条）

这些条目下载返回 `403 Forbidden`，浏览器打开可以正常访问。

| id | 章节 | 标题 | 链接 |
| --- | --- | --- | --- |
| `bigsmiles-2019` | 2,9 | BigSMILES: A Structurally-Based Line Notation for Describing Macromolecules | https://pubs.acs.org/doi/10.1021/acscentsci.9b00476 |
| `charmm-1998` | 5 | All-Atom Empirical Potential for Molecular Modeling and Dynamics Studies of Proteins | https://pubs.acs.org/doi/10.1021/jp973084f |
| `chemcrow-2023` | 14 | ChemCrow: Augmenting large-language models with chemistry tools | https://www.science.org/doi/10.1126/sciadv.adk1059 |
| `compass-1998` | 5 | COMPASS: An ab Initio Force-Field Optimized for Condensed-Phase Applications | https://pubs.acs.org/doi/10.1021/jp9725439 |
| `conditional-mol-2018` | 10 | Conditional Molecular Design with Deep Generative Models | https://arxiv.org/abs/1803.01096 |
| `d3-2010` | 5 | A consistent and accurate ab initio parametrization of density functional dispersion correction (DFT-D) for the 94 elements H-Pu | https://pubs.aip.org/aip/jcp/article/132/15/154104/187772 |
| `ecfp-rogers-hahn-2010` | 2 | Extended-Connectivity Fingerprints | https://pubs.acs.org/doi/10.1021/ci100050t |
| `force-matching-2005` | 5 | A multiscale coarse-graining method for biomolecular systems | https://pubs.acs.org/doi/10.1021/jp044629q |
| `fox-flory-1950` | 4 | Second-Order Transition Temperatures and Related Properties of Polystyrene | https://pubs.aip.org/aip/jap/article-abstract/21/6/581/158211 |
| `gaff-2004` | 5 | Development and testing of a general amber force field | https://onlinelibrary.wiley.com/doi/10.1002/jcc.20035 |
| `gas-separation-ml-2020` | 6,10,15 | Machine learning–enabled high-throughput screening of polymers for gas separation | https://www.science.org/doi/10.1126/sciadv.abc6216 |
| `gromacs-2015` | 5,14 | GROMACS: High performance molecular simulations through multi-level parallelism from laptops to supercomputers | https://www.sciencedirect.com/science/article/pii/S2352711015000059 |
| `ibi-2003` | 5 | Deriving effective mesoscale potentials from atomistic simulations | https://onlinelibrary.wiley.com/doi/10.1002/jcc.10307 |
| `inverse-design-review-2018` | 10 | Inverse molecular design using machine learning: Generative models for matter engineering | https://www.science.org/doi/10.1126/science.aat2663 |
| `martini-2007` | 5 | The MARTINI Force Field: Coarse Grained Model for Biomolecular Simulations | https://pubs.acs.org/doi/10.1021/jp071097f |
| `md-1957` | 5 | Phase Transition for a Hard Sphere System | https://pubs.aip.org/aip/jcp/article/27/5/1208/207705 |
| `metadynamics-2002` | 5 | Escaping free-energy minima | https://www.pnas.org/doi/10.1073/pnas.202427399 |
| `mol2vec-2018` | 2 | Mol2vec: Unsupervised Machine Learning Approach with Chemical Intuition | https://pubs.acs.org/doi/10.1021/acs.jcim.7b00616 |
| `morgan-1965` | 2 | The Generation of a Unique Machine Description for Chemical Structures | https://pubs.acs.org/doi/10.1021/c160017a018 |
| `opls-aa-1996` | 5 | Development and Testing of the OPLS All-Atom Force Field on Conformational Energetics and Properties of Organic Liquids | https://pubs.acs.org/doi/10.1021/ja9621760 |
| `pcff-1994` | 5 | Force field for computation of conformational energies, structures, and vibrational frequencies of aromatic polyesters | https://onlinelibrary.wiley.com/doi/10.1002/jcc.540150310 |
| `pi1m-2020` | 2,3,9 | PI1M: A Benchmark Database for Polymer Informatics | https://pubs.acs.org/doi/10.1021/acs.jcim.0c00726 |
| `polygan-2020` | 9 | PolyGAN: High-Order Polymer Property Prediction and Generation | https://pubs.acs.org/doi/10.1021/acs.jcim.0c01029 |
| `polymer-dielectrics-review-2022` | 4,15 | Polymer dielectrics for high-temperature capacitive energy storage | https://pubs.acs.org/doi/10.1021/acs.chemrev.1c00968 |
| `polymer-genome-2018` | 2,6,7,10 | Polymer Genome: A Data-Powered Polymer Informatics Platform for Property Predictions | https://pubs.acs.org/doi/10.1021/acs.jpcc.8b02913 |
| `polymer-informatics-2017` | 1,6 | Polymer Informatics: Opportunities and Challenges | https://pubs.acs.org/doi/10.1021/acsmacrolett.6b00936 |
| `relative-entropy-2008` | 5 | The relative entropy is fundamental to multiscale and inverse thermodynamic problems | https://pubs.aip.org/aip/jcp/article/129/14/144108/187392 |
| `replica-exchange-1999` | 5 | Replica-exchange molecular dynamics method for protein folding | https://www.sciencedirect.com/science/article/abs/pii/S0009261499011419 |
| `robeson-2008` | 4 | The upper bound revisited | https://www.sciencedirect.com/science/article/abs/pii/S0376738808002544 |
| `self-driving-lab-2020` | 13 | A self-driving laboratory for accelerated discovery of thin-film materials | https://www.science.org/doi/10.1126/sciadv.aaz8867 |
| `smiles-1988` | 2 | SMILES, a chemical language and information system | https://pubs.acs.org/doi/10.1021/ci00057a005 |
| `smipoly-2023` | 3,9,10,12 | SMiPoly: Generation of a Synthesizable Polymer Virtual Library | https://pubs.acs.org/doi/10.1021/acs.jcim.3c00277 |
| `solubility-hansen-2019` | 4,6 | Prediction of Hansen solubility parameters using machine learning | https://pubs.acs.org/doi/10.1021/acs.jcim.9b00485 |
| `tg-benchmark-2021` | 3,4,6 | Benchmarking machine learning models for polymer informatics: glass transition temperature | https://pubs.acs.org/doi/10.1021/acs.jcim.0c01336 |
| `umbrella-1977` | 5 | Nonphysical sampling distributions in Monte Carlo free-energy estimation: Umbrella sampling | https://www.sciencedirect.com/science/article/pii/0021999177901218 |
| `wham-1992` | 5 | The weighted histogram analysis method for free-energy calculations on biomolecules | https://onlinelibrary.wiley.com/doi/10.1002/jcc.540130812 |
| `wlf-1955` | 4 | The Temperature Dependence of Relaxation Mechanisms in Amorphous Polymers and Other Glass-forming Liquids | https://pubs.aip.org/aip/jcp/article/23/2/379/226027 |
| `mayo-lewis-1944` | 12 | Copolymerization. I. A Basis for Comparing the Behavior of Monomers in Copolymerization | https://pubs.acs.org/doi/10.1021/ja01237a052 |
| `flory-1940` | 12 | Molecular Size Distribution in Ethylene Oxide Polymers | https://pubs.acs.org/doi/10.1021/ja01863a066 |
| `matyjaszewski-2001` | 12 | Atom Transfer Radical Polymerization | https://pubs.acs.org/doi/10.1021/cr940534g |
| `raft-chiefari-1998` | 12 | Living Free-Radical Polymerization by Reversible Addition-Fragmentation Chain Transfer | https://pubs.acs.org/doi/10.1021/ma9804951 |
| `ahneman-2018` | 12 | Predicting reaction performance in C-N cross-coupling using machine learning | https://www.science.org/doi/10.1126/science.aar5169 |
| `ord-2021` | 12 | The Open Reaction Database | https://pubs.acs.org/doi/10.1021/jacs.1c09820 |
| `scscore-2018` | 12 | SCScore: Synthetic Complexity Learned from a Reaction Corpus | https://pubs.acs.org/doi/10.1021/acs.jcim.7b00622 |

## 二、需手动补充：订阅来源（11 条）

已抓到落地页，正文需机构访问。

| id | 章节 | 标题 | 链接 |
| --- | --- | --- | --- |
| `alab-2023` | 13 | An autonomous laboratory for the accelerated synthesis of novel materials | https://www.nature.com/articles/s41586-023-06734-w |
| `coscientist-2023` | 14 | Autonomous chemical research with large language models | https://www.nature.com/articles/s41586-023-06792-0 |
| `fair-principles-2016` | 3 | The FAIR Guiding Principles for scientific data management and stewardship | https://www.nature.com/articles/sdata201618 |
| `kusne-2020` | 10 | On-the-fly closed-loop materials discovery via Bayesian active learning | https://www.nature.com/articles/s41467-020-19597-w |
| `lookman-2019` | 10 | Active learning in materials science with emphasis on adaptive sampling using uncertainties for targeted design | https://www.nature.com/articles/s41524-019-0153-8 |
| `raccuglia-2016` | 10 | Machine-learning-assisted materials discovery using failed experiments | https://doi.org/10.1038/nature17439 |
| `self-driving-lab-review-2023` | 13 | Autonomous experimentation systems for materials development | https://www.nature.com/articles/s41578-023-00587-5 |
| `sustainable-polymers-ai-2024` | 15 | Machine learning for sustainable polymer design | https://www.nature.com/articles/s41578-024-00654-5 |
| `zunger-2018` | 10 | Inverse design in materials genomics: forward-to-inverse materials design | https://doi.org/10.1038/natrevmats.2018.5 |
| `retrosynthesis-segler-2018` | 12 | Planning chemical syntheses with deep neural networks and symbolic AI | https://www.nature.com/articles/nature25978 |
| `stuyver-coley-2020` | 12 | Machine learning in chemical reaction space | https://www.nature.com/articles/s41467-020-19326-3 |

## 三、正文过短，需补全（7 条）

| id | 章节 | 情况 | 建议 |
| --- | --- | --- | --- |
| `gradient-boosting-2001` | 6 | 抓到页面但正文少于阈值 | 补全文或改引摘要 |
| `hypervolume-2003` | 10 | 抓到页面但正文少于阈值 | 补全文或改引摘要 |
| `kaggle-polymer-2025` | 3,16 | 抓到页面但正文少于阈值 | 补全文或改引摘要 |
| `nsga2-2002` | 10 | 抓到页面但正文少于阈值 | 补全文或改引摘要 |
| `openmm-tools` | 5 | 抓到页面但正文少于阈值 | 补全文或改引摘要 |
| `parego-2006` | 10 | 抓到页面但正文少于阈值 | 补全文或改引摘要 |
| `polymer-informatics-next-2021` | 1,3 | 抓到页面但正文少于阈值 | 补全文或改引摘要 |

---

## 四、待核实的数据

这些数字目前在 `calculations/` 中是建模假设或缺失值，正文引用前需要一条可核对的来源。

| 项目 | 现状 | 需要 |
| --- | --- | --- |
| Open Macromolecular Genome 规模 | `null`（未核实） | 库规模（结构数） |
| PolyUniverse 规模 | `null`（未核实） | 库规模（结构数） |
| DFT 单点 FLOPs/原子³ 常数 `10⁴` | 建模假设 | 可引用出处或改用实测 |
| MLFF FLOPs/原子/步 常数 `2×10⁶` | 建模假设 | 可引用出处或改用实测 |
| 一次湿实验耗时 3–7 天 | 经验估计 | 来源或标注为量级假设 |

## 五、已就位

- WoS 检索导出（3178 条）：`references/wos/`，调研报告 `research/2026-wos-survey/`。
- 领域资源清单：`https://github.com/ShiqianTan/AI4Polymer`（外部，无需下载）。
- 全部复算结果：`calculations/results/`（11 个主题，各含 `.json` 与 `.md`）。
- 已下载 66 条全文：`references/files/<category>/`，可检索文本 `references/text/<id>.txt`。
- 第 5 章新增开放来源（16 条已下载）：通用与基础机器学习势（`mace-mp-0-2023`、`chgnet-2023`、`m3gnet-2022`、`allegro-2023`、`flare-2020`、`mlff-review-2021`、`behler-parrinello-2007`）、工具与框架（`lammps-2022`、`openmm-2017`、`pyscf-2020`）。
- 第 6 章新增来源（15 条）：图网络与序列模型（`gcn-2017`、`gat-2018`、`chemprop-2019`、`egnn-2021`、`transformer-2017`、`bert-2019`、`chemberta-2020`）、基线与不确定度（`random-forest-2001`、`gradient-boosting-2001`、`xgboost-2016`、`svr-1995`、`conformal-2002`、`quantile-forest-2006`、`deep-ensembles-2017`）与工具（`scikit-learn-2011`）。
- 第 9 章新增开放来源（25 条已下载，arXiv 与开放期刊）：生成方法（`vae-2013`、`gan-2014`、`ddpm-2020`、`ddim-2020`、`score-sde-2020`、`flow-matching-2022`、`neural-ode-2018`、`normalizing-flows-2015`、`maskgit-2022`、`mdlm-2024`、`d3pm-2021`、`cfg-2022`、`edm-2022`）、分子生成（`molgan-2018`、`jtvae-2018`、`graphaf-2020`、`geoldm-2022`）、聚合物生成（`polyvae-2020`、`polygen-2025`、`self-improvable-polymer-2023`、`polybart-2025`、`glamour-2021`、`vitrimer-inverse-2023`、`open-polymer-generative-pipeline-2024`）与可合成性评分（`sa-score-2009`）。其中 `polyvae-2020` 与 `polybart-2025` 的 arXiv 主站下载被截断，改用 `export.arxiv.org` 取得全文。
- 第 12 章新增开放来源（2 条已下载）：`molecular-transformer-2019`（arXiv 主站 PDF 被截断，改用 `export.arxiv.org` 取得全文）与 `aizynthfinder-2020`（开放期刊 HTML）；`retrosynthesis-segler-2018` 与 `stuyver-coley-2020` 抓到 Nature 落地页，正文需机构访问。
- 第 7 章新增开放来源（16 条已下载，均为 arXiv）：多任务学习（`multitask-overview-2017`、`multitask-uncertainty-2018`、`gradient-surgery-2020`、`multitask-survey-2021`、`negative-transfer-2019`）、迁移与参数高效微调（`maml-2017`、`adapter-2019`、`lora-2021`、`dann-2016`、`transfer-survey-2020`）、自监督预训练（`pretrain-gnn-2019`、`graphcl-2020`、`molclr-2022`）与物理信息（`informed-ml-2021`、`willard-2022`、`tfn-2018`）。同时把 `polybert-2023`、`tg-benchmark-2021`、`chemberta-2020`、`polymer-multitask-gnn-2023`、`transpolymer-2023`、`pi1m-2020` 的章节登记扩展到第 7 章。
- 第 8 章新增开放来源（22 条已下载，均为 arXiv 或开放镜像）：图像分割与检测（`unet-2015`、`mask-rcnn-2017`、`deeplab-v3plus-2018`、`nnunet-2018`、`segment-anything-2023`、`em-active-learning-2019`、`afm-polymer-blends-2024`、`care-cryoem-2018`）、振动与核磁谱（`raman-imaging-2020`、`raman-benchmark-2026`、`nmr-reversible-2026`）、散射与衍射（`xrd-symmetry-cnn-2018`、`xrd-augment-2019`、`saxs-ml-2019`、`scattering-inverse-kan-2024`、`pairvae-2023`）、多模态与表示（`clip-2021`、`simclr-2020`、`mae-2022`）、域漂移与因果（`domain-adaptation-2019`、`causal-interpretability-2020`）与主动测量（`spm-active-learning-2022`）。其中 `pairvae-2023` 的 arXiv 主站返回 HTTP 406，改用 `export.arxiv.org` 取得全文。同时把 `gpml-2006`、`transformer-2017`、`domainbed-2021`、`deep-ensembles-2017`、`self-driving-lab-review-2023`、`kusne-2020` 的章节登记扩展到第 8 章。
- 第 15 章新增开放来源（18 条已下载，均为 arXiv）：可持续材料与 AI（`sustainable-materials-ai-2026`）、化学可回收设计（`informatics-recyclable-2024`、`ai-recyclable-food-packaging-2025`、`recyclable-vitrimer-pcb-2023`、`recyclable-flame-retardant-epoxy-2021`）、升级回收（`upcycling-catalysis-2023`、`plastic-upcycling-ml-2026`）、LCA（`lca-organic-chemicals-2026`、`ai-lca-landscape-2026`、`ml-model-lca-2026`）、生物基与生物降解（`bioplastic-multitask-2022`、`bioplastic-amyloid-2021`、`sustainable-polymer-md-ml-2025`）、机械与热机械回收（`thermo-mech-recyclable-pe-2026`、`tpa-yield-pet-hydrolysis-2022`）、溶剂与寿命（`polymer-solubility-smiles-2025`、`aem-degradation-pinn-2025`）与循环经济史（`plastic-waste-100years-2024`）。其中 `upcycling-catalysis-2023`、`sustainable-polymer-md-ml-2025`、`bioplastic-amyloid-2021` 的 arXiv 主站返回 HTTP 406，`thermo-mech-recyclable-pe-2026` 主站下载截断，四条均改用 `export.arxiv.org` 取得全文。同时把 `vitrimer-inverse-2023`、`open-polymer-challenge-2025` 的章节登记扩展到第 15 章。
- 第 11 章新增开放来源（18 条已下载，均为 arXiv 或开放期刊）：采集函数（`gp-ucb-2010`、`ei-tutorial-2010`）、批量与约束（`batch-bo-2018`、`constrained-bo-2014`、`constrained-bo-2017`）、多保真与成本感知（`multifidelity-bo-2017`、`multifidelity-bo-2019`、`cost-aware-bo-2020`）、主动学习与多样性（`dpp-2012`、`batchbald-2019`、`active-learning-review-2021`）、强化学习（`dqn-2013`、`ppo-2017`、`molrl-2019`、`offline-rl-2020`、`cql-2020`、`mbrl-pets-2018`）与材料应用（`bo-materials-2021`）。其中 `batch-bo-2018` 的 arXiv 主站 PDF 多次截断，改用浏览器式 `curl` 取回后按 `fetch.py` 的字段手工登记。同时把 `gpml-2006`、`bo-review-2018`、`deep-ensembles-2017`、`snoek-2012`、`batch-bayesopt-2018`、`ehvi-2020`、`parego-2006`、`hypervolume-2003`、`nsga2-2002`、`multiobjective-tutorial-2018`、`raccuglia-2016`、`deeppolymer-2020`、`uncertainty-dnn-2021`、`thermal-cond-tutorial-2024`、`reinvent-2017`、`gcpn-2018`、`self-driving-lab-2020`、`kusne-2020`、`lookman-2019`、`flare-2020` 的章节登记扩展到第 11 章。新增复算主题 `bo-variants`（批量、约束、多保真、成本感知的闭式核算），结果见 `calculations/results/bo-variants.{json,md}`。
- 第 13 章新增开放来源（10 条已下载）：编排与工作流软件（`chemos-2020`、`aiida-2016`、`optuna-2019`、`botorch-2019`）、材料加速平台（`amanda-2021`）、调度与在途实验（`pending-experiments-2023`）与自驱动实验室案例（`self-driving-lab-thinfilm-2019`、`panda-2024`、`sdl-lcst-2025`、`opv-self-driving-2019`）。其中 `amanda-2021` 的 arXiv 主站返回 HTTP 406，改用 `export.arxiv.org` 取得全文；`self-driving-lab-thinfilm-2019` 是 `self-driving-lab-2020` 的 arXiv 预印本，用于补足后者未归档的全文。同时把 `bo-materials-2021`、`batch-bo-2018`、`multifidelity-bo-2019`、`cost-aware-bo-2020`、`active-learning-review-2021`、`dpp-2012`、`spm-active-learning-2022`、`deep-ensembles-2017`、`aizynthfinder-2020`、`gcpn-2018`、`deeppolymer-2020`、`thermal-conductivity-ml-2019` 的章节登记扩展到第 13 章。
- 第 14 章新增开放来源（20 条已下载，均为 arXiv）：分子基础模型（`unimol-2023`、`molformer-2022`、`moleculestm-2023`）、检索增强生成与检索评测（`dpr-2020`、`realm-2020`、`self-rag-2024`、`rag-survey-2023`、`lost-in-middle-2023`、`alce-2023`、`beir-2021`）、智能体与工具调用（`react-2023`、`toolformer-2023`、`reflexion-2023`、`program-aided-2023`、`toolllm-2023`、`agentbench-2023`、`autogen-2023`、`agents-survey-2024`）与幻觉评测（`hallucination-survey-2023`、`truthfulqa-2022`）。其中 `moleculestm-2023` 首次下载被截断，重试后取得全文。同时把 `m3gnet-2022`、`transformer-2017`、`smiles-1988`、`bigsmiles-2019`、`gromacs-2015` 的章节登记扩展到第 14 章。

## 六、补入后的登记方式

1. 把文件放到 `references/files/<category>/<id>.<ext>`（category 见 `sources.tsv`）。
2. 重新登记：`python3 references/fetch.py --reindex`，或对单条运行 `--only <id>`。
3. 若来源是本地文件，把 `sources.tsv` 的 `url` 写成 `local:<相对 references/ 的路径>`，状态会记为 `user_provided`。
