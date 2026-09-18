# synthesis-route — declared-retrosynthesis-beam-and-yield-funnel

输入：`{"beam": 10, "branching": 50, "cost_pass": 0.4, "depth": 5, "feasibility": 0.6, "initial_candidates": 8910, "route_length_pass": 0.6, "step_yield": 0.8, "target_yield": 0.3, "yield_pass": 0.5}`

| 来源 | 标题 | URL | 访问日期 |
| --- | --- | --- | --- |
| retrosynthesis-segler-2018 | Segler, Preuss & Waller, Planning chemical syntheses with deep neural networks and symbolic AI, Nature 2018 | https://www.nature.com/articles/nature25978 | 2026-09-17 |
| aizynthfinder-2020 | Saigiridharan et al., AiZynthFinder: a fast, robust and flexible open-source software for retrosynthetic planning, J. Cheminform. 2020 | https://jcheminf.biomedcentral.com/articles/10.1186/s13321-020-00474-z | 2026-09-17 |

## 结果

| 结果 | 值 |
| --- | ---: |
| exhaustive_nodes | 312,500,000 |
| beam_nodes | 2,050 |
| pruning_ratio | 152439 |
| route_yield | 0.32768 |
| max_steps_at_target | 5 |
| final_survivors | 641.52 |
| overall_pass | 0.072 |

## 假设与边界

- 穷举搜索的节点数按 $b^{d}$ 计；束搜索每层只保留前 $k$ 个节点，展开数为各层保留节点数乘以分支因子之和。
- 路线总产率按 $Y=\bar y^{d}$ 计，各步产率独立同分布；达到目标总产率的最大步数为 $\lfloor\ln Y_\text{target}/\ln\bar y\rfloor$。
- 漏斗四级通过率（可行性、路线长度、产率、成本）为声明输入，只用于说明量级，不代表实测通过率。
- 全部数值为声明模型输出，参数为建模输入，不是实验测量。
