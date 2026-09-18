# closed-loop — closed-loop-sample-efficiency

输入：`{"bo_speedup": 5.0, "bo_speedup_origin": "declared input, not a measured improvement", "experiments_per_day": 50, "space_size": 1000000, "top_fraction": 0.001}`

| 来源 | 标题 | URL | 访问日期 |
| --- | --- | --- | --- |
| bayesian-optimization-snoek | Snoek et al., Practical Bayesian Optimization of Machine Learning Algorithms, NeurIPS 2012 | https://arxiv.org/abs/1206.2944 | 2026-09-16 |
| bayesian-optimization-shahriari | Shahriari et al., Taking the Human Out of the Loop: A Review of Bayesian Optimization, Proc. IEEE 2016 | https://ieeexplore.ieee.org/document/7352306 | 2026-09-16 |

## 结果

| 结果 | 值 |
| --- | ---: |
| random_experiments_expected | 1,000 |
| bo_experiments_expected | 200 |
| calendar_days | 4 |
| speedup_vs_random | 5 |
| expected_failures_before_success | 999 |
| random_calendar_days | 20 |
| expected_hits_in_space | 1,000 |
| hit_fraction | 0.001 |
| experiments_per_day | 50 |

## 假设与边界

- 随机搜索命中概率 p = top_fraction，首次命中所需实验次数服从几何分布，期望 E[X] = 1/p；期望失败次数 = (1-p)/p。
- 贝叶斯优化实验数 = 随机搜索期望 / bo_speedup；bo_speedup 是声明输入，不是实测加速比，也未规定采集函数或代理模型。
- calendar_days 指贝叶斯优化闭环：bo_experiments_expected / experiments_per_day；random_calendar_days 为随机搜索对照。
- speedup_vs_random 恒等于声明的 bo_speedup；它比较的是期望实验次数，不是每次实验的墙钟时间。
- expected_hits_in_space = space_size × top_fraction，仅表示整个空间中命中候选的期望数量，不改变几何期望。
- 模型假设每次实验独立同分布且命中概率恒定；真实闭环中先验、批量和约束会改变该假设。
