# AI4Polymer 量化计算计划与验收清单

本项目把《AI4Polymer》全书散落的推导与算例收拢为可复现的 Python 项目。方法论为**从约束推导设计**：书中数字必须来自可复现、仅用标准库的计算工具。正式实验测量、合成收率、模型训练与质量评测保持独立；需要这些输入的计算只提供明确标记的情景扫描，不填造实测。

> **重要边界**：公式的单元测试与闭式验证**不能代替真实实验证据**。所有场景参数均为声明式建模输入；标注 `[ ]` 的工作包在取得真实测量、人工复核或正文落点前不得视为完成。

## 当前状态速览

六个专题计算、结果契约、复现与来源校验、结果索引均已交付并有独立测试。数据集的公开规模、设备峰值与文献常数属于**声明元数据**，引用前需人工复核；`Open Macromolecular Genome` 与 `PolyUniverse` 的规模保持 `null`。

## 基础（F）

- [x] **F01 项目骨架与结果契约** — 源码：`src/ai4polymer_calc/{cli,schema,report}.py`、`calc.py`；场景：`scenarios/book.json`；结果：`results/*.json`；验证：`tests/test_reproduce.py`；提纲落点：全书方法章。
- [x] **F02 单位与输入校验器** — 源码：`src/ai4polymer_calc/units.py`；场景：各专题输入；结果：拒绝非法/非有限输入；验证：`tests/test_units.py`；提纲落点：附录计量约定。
- [x] **F03 来源锁与引用校验** — 源码：`src/ai4polymer_calc/sources.py`；场景：`configs/sources.lock.json`；结果：`verify-sources`；验证：`tests/test_reproduce.py` 契约测试；提纲落点：参考文献与数据来源。
- [x] **F04 复现与结果验证** — 源码：`src/ai4polymer_calc/reproduce.py`；场景：`scenarios/book.json`；结果：`results/<slug>.{json,md}`、`results/README.md`、`results/manifest.json`；验证：`verify-results`；提纲落点：可复现性附录。
- [ ] **F05 逐章来源清单与正文同步** — 源码：`inventory/sources.json` 占位；场景：各章提纲；结果：待填；验证：待补；提纲落点：全书。缺口：章节未稳定，来源 id 尚未逐节绑定。

## 表示与数据（R）

- [x] **R01 描述符/指纹规格** — 源码：`configs/descriptors.json`；场景：`descriptor-budget`；结果：`results/descriptor-morgan-2048.json`；验证：`tests/test_descriptor_budget.py`；提纲落点：表示学习章。
- [x] **R02 公开数据集规模元数据** — 源码：`configs/datasets.json`；场景：`chemical-space`；结果：`results/chemical-space-random.json`；验证：`tests/test_chemical_space.py`；提纲落点：数据与数据库章。
- [x] **R03 示意单体库与 SMILES/PSMILES** — 源码：`configs/monomers.json`；场景：`chemical-space`；结果：序列空间规模；验证：暴力枚举；提纲落点：单体与聚合章。
- [x] **R04 表示维度、存储与碰撞预算** — 源码：`topics/descriptor_budget.py`；场景：四种表示；结果：`descriptor-*.json`；验证：生日问题闭式；提纲落点：表示学习章。
- [ ] **R05 真实指纹生成与去重核验（RDKit/ECFP）** — 源码：待接入外部工具；场景：真实分子库；结果：待生成；验证：与 RDKit 对照；提纲落点：表示学习章。缺口：stdlib-only 约束下不实现 RDKit 等价物。
- [ ] **R06 数据集规模人工复核（OMG/PolyUniverse）** — 源码：`configs/datasets.json`；场景：覆盖对比；结果：`size=null`；验证：待人工；提纲落点：数据章。缺口：公开规模与规范链接未核实。

## 模型（M）

- [x] **M01 消息传递 GNN 参数量与前向 FLOPs** — 源码：`topics/gnn_forward.py`；场景：`gnn-forward-4layer`；结果：`results/gnn-forward-4layer.json`；验证：FLOP 守恒；提纲落点：性质预测章。
- [x] **M02 Transformer 基线对照** — 源码：`topics/gnn_forward.py`；场景：同层数同宽度；结果：`transformer_forward_flops`；验证：逐项推导；提纲落点：语言模型章。
- [x] **M03 MD/MLFF/DFT 声明成本模型** — 源码：`topics/md_cost.py`；场景：`md-cost-mlff`、`md-cost-dft`；结果：`results/md-cost-*.json`；验证：标度关系；提纲落点：多尺度模拟章。
- [ ] **M04 真实模型训练/推理实测标定** — 源码：待接入；场景：真实数据集；结果：待生成；验证：实测吞吐/精度；提纲落点：各模型章。缺口：需 GPU 与真实数据。
- [ ] **M05 描述符→性能代理模型验证** — 源码：待接入；场景：真实标签；结果：待生成；验证：交叉验证；提纲落点：性质预测章。缺口：需实验/文献数据。

## 闭环（L）

- [x] **L01 随机搜索几何期望** — 源码：`topics/closed_loop.py`；场景：`closed-loop-bo`；结果：`results/closed-loop-bo.json`；验证：几何级数与 1/p；提纲落点：主动学习章。
- [x] **L02 贝叶斯优化加速比情景** — 源码：`topics/closed_loop.py`；场景：声明 `bo_speedup`；结果：日历时间对比；验证：闭式；提纲落点：闭环发现章。
- [x] **L03 幂律学习曲线反解** — 源码：`topics/learning_curve.py`；场景：`learning-curve-target`；结果：`results/learning-curve-target.json`；验证：反解回代；提纲落点：数据效率章。
- [ ] **L04 真实闭环实验标定** — 源码：待接入；场景：真实实验记录；结果：待生成；验证：实测命中率；提纲落点：自动化实验室章。缺口：需实验数据。
- [ ] **L05 多目标与带约束采集函数** — 源码：待实现；场景：多目标阈值；结果：待生成；验证：待定；提纲落点：多目标设计章。

## 章节（C01–C16）

每章条目给出证据链 `源码→场景→结果→验证→提纲落点`；未勾选表示该章的定量落点尚未交付或尚未逐原文验收。

- [ ] **C01 高分子与 AI 概览** — 源码：待定；场景：待定；结果：待生成；验证：待定；提纲落点：第 1 章。缺口：综述章以引用为主，暂无独立计算。
- [x] **C02 表示学习与描述符** — 源码：`topics/descriptor_budget.py`、`configs/descriptors.json`；场景：四种表示；结果：`results/descriptor-*.json`；验证：碰撞闭式；提纲落点：第 2 章。
- [x] **C03 高分子数据与数据库** — 源码：`topics/chemical_space.py`、`configs/datasets.json`；场景：`chemical-space-*`；结果：`results/chemical-space-*.json`；验证：大整数与覆盖对比；提纲落点：第 3 章。
- [x] **C04 生成模型与化学空间** — 源码：`topics/chemical_space.py`；场景：随机/嵌段/交替；结果：序列计数；验证：暴力枚举；提纲落点：第 4 章。
- [x] **C05 性质预测 GNN** — 源码：`topics/gnn_forward.py`；场景：`gnn-forward-4layer`；结果：`results/gnn-forward-4layer.json`；验证：FLOP 守恒；提纲落点：第 5 章。
- [x] **C06 高分子语言模型** — 源码：`topics/gnn_forward.py` 的 Transformer 基线；场景：同规模对照；结果：`transformer_forward_flops`；验证：逐项推导；提纲落点：第 6 章。
- [x] **C07 多尺度模拟（MD/DFT）** — 源码：`topics/md_cost.py`；场景：`md-cost-*`；结果：`results/md-cost-*.json`；验证：标度关系；提纲落点：第 7 章。
- [x] **C08 学习曲线与数据效率** — 源码：`topics/learning_curve.py`；场景：`learning-curve-target`；结果：`results/learning-curve-target.json`；验证：反解回代；提纲落点：第 8 章。
- [x] **C09 主动学习与贝叶斯优化** — 源码：`topics/closed_loop.py`；场景：`closed-loop-bo`；结果：`results/closed-loop-bo.json`；验证：几何期望；提纲落点：第 9 章。
- [ ] **C10 闭环实验室与自动化** — 源码：待定；场景：待定；结果：待生成；验证：待定；提纲落点：第 10 章。缺口：需真实实验流程。
- [ ] **C11 合成可行性与逆设计** — 源码：`chemical-space` 规则库为部分支撑；场景：待定；结果：待生成；验证：待定；提纲落点：第 11 章。缺口：需反应规则与收率数据。
- [ ] **C12 多目标与鲁棒性设计** — 源码：待实现；场景：待定；结果：待生成；验证：待定；提纲落点：第 12 章。
- [ ] **C13 可解释性与不确定性** — 源码：待实现；场景：待定；结果：待生成；验证：待定；提纲落点：第 13 章。
- [ ] **C14 工艺与放大** — 源码：待实现；场景：待定；结果：待生成；验证：待定；提纲落点：第 14 章。
- [ ] **C15 案例研究** — 源码：待定；场景：待定；结果：待生成；验证：待定；提纲落点：第 15 章。缺口：需真实案例数据。
- [ ] **C16 展望与伦理** — 源码：待定；场景：待定；结果：待生成；验证：待定；提纲落点：第 16 章。

## 执行顺序

1. 稳定各章提纲，逐节登记来源与计算落点（F05）。
2. 对声明元数据（数据集规模、设备峰值、文献常数）逐项人工复核（R06）。
3. 在取得真实数据后接入外部工具链，完成 R05、M04、M05、L04 的实测对照。
4. 每批交付同时更新本清单、`results/` 与正文落点；未完成项保持 `[ ]`，不得仅因有脚本而勾选。
