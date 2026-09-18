# learning-curve — power-law-learning-curve

输入：`{"a": 1.0, "alpha": 0.5, "mae_inf": 0.05, "n_max": 100000, "parameter_origin": "declared input, not a fitted measurement", "strict_mae": 0.1, "target_mae": 0.2}`

| 来源 | 标题 | URL | 访问日期 |
| --- | --- | --- | --- |
| learning-curve-hestness | Hestness et al., Deep Learning Scaling is Predictable, Empirically, 2017 | https://arxiv.org/abs/1712.00409 | 2026-09-16 |
| learning-curve-rosenfeld | Rosenfeld et al., A Constructive Prediction of the Generalization Error Across Scales, ICLR 2020 | https://arxiv.org/abs/1909.12673 | 2026-09-16 |

## 结果

| 结果 | 值 |
| --- | ---: |
| required_n | 44.4444 |
| required_n_experiments | 45 |
| mae_at_n_max | 0.0531623 |
| target_achievable_within_n_max | `true` |
| strict_target_required_n | 400 |
| strict_target_required_n_experiments | 400 |
| marginal_experiments_to_strict_target | 355 |
| target_reduction | 0.1 |

学习曲线采样

| n | mae |
| --- | --- |
| 1 | 1.05 |
| 10 | 0.366228 |
| 100 | 0.15 |
| 1,000 | 0.0816228 |
| 10,000 | 0.06 |
| 100,000 | 0.0531623 |

## 假设与边界

- 学习曲线形式为 MAE(n) = MAE_inf + A·n^(-alpha)；A、alpha 与 MAE_inf 都是声明输入，除非场景文件显式提供拟合值，否则不是拟合测量结果。
- 所需样本数由反解得到：n = (A / (target - MAE_inf))^(1/alpha)；要求 target > MAE_inf，否则返回 null（不可达）。
- required_n_experiments = ceil(required_n)，即至少需要的整数训练样本数；连续值与整数解分别保存。
- target_achievable_within_n_max 表示在 n_max 处 MAE 是否已不高于目标；它只比较曲线外推，不代表真实数据可获得。
- 边际数据 = 更严目标所需样本数 − 原目标所需样本数；两个目标都必须严格高于 MAE_inf 才能给出数值。
- 曲线采样点仅用于展示幂律形状；外推到 n_max 以外不受支持。
