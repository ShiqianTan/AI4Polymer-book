# robust-ranking — declared-mean-interval-ranking

输入：`{"half_widths": [20.0, 3.0], "means": [205.0, 205.0], "spec_high": 210.0, "spec_low": 200.0}`

| 来源 | 标题 | URL | 访问日期 |
| --- | --- | --- | --- |
| uncertainty-survey | Gawlikowski et al., A Survey of Uncertainty in Deep Neural Networks, 2021 | https://arxiv.org/abs/2107.03342 | 2026-09-17 |

## 结果

| 结果 | 值 |
| --- | ---: |
| candidate_count | 2 |
| spec_low | 200 |
| spec_high | 210 |
| mean_only_tie | `true` |
| best_by_interval | `"C2"` |
| best_by_probability | `"C2"` |
| ranking_flip | `true` |

## 假设与边界

- 候选均值与区间半宽为声明输入：C1 为 205 ± 20，C2 为 205 ± 3，单位与目标性质一致（示例取 ℃）。
- 区间半宽按一倍标准差处理，σ = half_width；在规范窗内的概率由正态分布尾部差 Φ((high−μ)/σ) − Φ((low−μ)/σ) 计算，Φ 用标准库的误差函数实现。
- 均值加区间排序按下界 mean − half_width 降序，下界相同时取区间更窄者；均值排序只按 mean 降序。
- 两个候选均值相同时均值排序并列，是否翻转由下界决定；该判据只说明不确定度如何改变排序，不代表真实实验重复性。
