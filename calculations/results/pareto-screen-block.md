# pareto-screen — declared-two-block-pareto-screen

输入：`{"chain_length": 100, "epsilon_steps": 21, "monomers": 10, "reference": [0.0, 0.0], "weight_steps": 11}`

| 来源 | 标题 | URL | 访问日期 |
| --- | --- | --- | --- |
| multiobjective-ehvi | Daulton et al., Differentiable Expected Hypervolume Improvement for Parallel Multi-Objective Bayesian Optimization, NeurIPS 2020 | https://arxiv.org/abs/2006.05078 | 2026-09-17 |
| multiobjective-nsga2 | Deb et al., A fast and elitist multiobjective genetic algorithm: NSGA-II, IEEE Trans. Evol. Comput. 2002 | https://doi.org/10.1109/4235.996017 | 2026-09-17 |

## 结果

| 结果 | 值 |
| --- | ---: |
| enumerated_candidates | 8,910 |
| distinct_objective_points | 99 |
| realizations_per_point | 90 |
| pareto_front_points | 80 |
| pareto_fraction | 0.808081 |
| hypervolume | 0.700117 |
| weighted_sum_points | 5 |
| weighted_sum_coverage | 0.0625 |
| epsilon_constraint_points | 20 |
| epsilon_constraint_coverage | 0.25 |
| knee_selectivity | 0.6965 |
| knee_permeability | 0.454705 |

## 假设与边界

- 候选集为精确组合数 N(N-1)(L-1)：有序单体对与两嵌段分点，计数与 chemical-space 的嵌段模型一致。
- 两个目标为声明代理模型：选择性代理 = 0.30 + 0.65·f，渗透率代理 = 0.95 − 0.65·f + 0.10·sin(2πf) + 0.04·sin(6πf)，f 为第一嵌段的链分数；它们不是实测性质，只用于演示筛选与排序流程。
- 支配关系按两个目标同时最大化定义；超体积相对声明参考点计算，参考点取 (0,0)。
- 加权和覆盖为权重 0 到 1 的等距网格上的最优前沿点集合；ε-约束覆盖为在渗透率代理下限网格上最大化选择性代理所得的前沿点集合。
- 同一目标点对应 90 个结构不同的候选（不同有序单体对），因此前沿点数是结构多样性之外的独立概念。
