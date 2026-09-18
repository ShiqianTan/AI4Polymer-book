# bo-variants — closed-form-variant-accounting

输入：`{"batch_correlation": 0.5, "batch_size": 8, "budget": 1000, "expensive_cost_ratio": 20.0, "feasible_fraction": 0.3, "fidelity_cost_ratio": 0.05, "note": "declared toy model; not a measured speedup", "screening_pass_fraction": 0.2, "space_size": 1000000, "top_fraction": 0.001}`

| 来源 | 标题 | URL | 访问日期 |
| --- | --- | --- | --- |
| bayesian-optimization-gp-ucb | Srinivas et al., Gaussian Process Optimization in the Bandit Setting: No Regret and Experimental Design, ICML 2010 | https://arxiv.org/abs/0912.3995 | 2026-09-17 |
| batch-bayesopt-local-penalization | González et al., Batch Bayesian Optimization via Local Penalization, AISTATS 2016 | https://arxiv.org/abs/1505.08052 | 2026-09-17 |
| constrained-bayesopt-unknown | Gelbart, Snoek & Adams, Bayesian Optimization with Unknown Constraints, UAI 2014 | https://arxiv.org/abs/1403.5607 | 2026-09-17 |
| multifidelity-bayesopt-continuous | Kandasamy et al., Multi-fidelity Bayesian Optimisation with Continuous Approximations, ICML 2017 | https://arxiv.org/abs/1703.06240 | 2026-09-17 |
| cost-aware-bayesopt | Lee et al., Cost-aware Bayesian Optimization, 2020 | https://arxiv.org/abs/2003.10870 | 2026-09-17 |

## 结果

| 结果 | 值 |
| --- | ---: |
| batch_effective_size | 1.77778 |
| batch_information_retained | 0.222222 |
| expected_feasible_per_batch | 2.4 |
| probability_zero_feasible_batch | 0.057648 |
| expected_experiments_per_feasible | 3.33333 |
| infeasible_budget_fraction | 0.7 |
| fidelity_speedup | 4 |
| ladder_cost_high_fidelity_equivalent | 0.25 |
| cheap_evaluations_in_budget | 1,000 |
| expensive_evaluations_in_budget | 50 |
| cost_aware_information_threshold | 0.05 |
| expected_hits_in_budget | 1 |
| expected_experiments_per_hit | 1,000 |

## 假设与边界

- 批量有效样本量用组内相关设计效应：B_eff = B / (1 + (B-1)ρ)，ρ 为批内候选平均相关，是声明输入。
- 约束结果假设每个候选独立的可行概率 q：每批期望可行数 Bq，全批不可行概率 (1-q)^B。
- 多保真阶梯假设低保真成本为高保真的 r 倍、仅通过比例 p 的候选进入高保真，则一个高保真当量的成本为 r+p。
- 成本感知阈值假设一次廉价评估的信息量为一次昂贵评估的 c 倍时，若 c > 1/成本比则廉价评估的单位成本收益更高。
- 命中期望仍为几何分布的 1/p，预算内期望命中数 = 预算 × p；本模型不含先验、批量与约束对命中率的改变。
