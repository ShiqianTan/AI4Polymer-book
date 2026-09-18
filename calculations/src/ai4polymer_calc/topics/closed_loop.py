"""Sample-efficiency comparison for closed-loop materials discovery.

Random search is the exact geometric expectation 1/p for the first hit; the
Bayesian-optimization count divides that expectation by a declared speedup,
which is a modeling input rather than a measured improvement.
"""
from ..schema import result
from ..sources import provenance
from ..units import fraction, positive_int, positive_number


def calculate(space_size: int = 1_000_000, top_fraction: float = 0.001,
              bo_speedup: float = 5.0, experiments_per_day: int = 50) -> dict:
    positive_int(space_size, "space_size")
    positive_int(experiments_per_day, "experiments_per_day")
    hit_fraction = fraction(top_fraction, "top_fraction")
    positive_number(bo_speedup, "bo_speedup")

    random_experiments = 1.0 / hit_fraction
    expected_failures = (1.0 - hit_fraction) / hit_fraction
    bo_experiments = random_experiments / bo_speedup
    random_calendar_days = random_experiments / experiments_per_day
    calendar_days = bo_experiments / experiments_per_day
    expected_hits_in_space = space_size * hit_fraction

    return result(
        calculation="closed-loop",
        model="closed-loop-sample-efficiency",
        scenario=dict(space_size=space_size, top_fraction=hit_fraction, bo_speedup=bo_speedup,
                      experiments_per_day=experiments_per_day,
                      bo_speedup_origin="declared input, not a measured improvement"),
        sources=provenance(["bayesian-optimization-snoek", "bayesian-optimization-shahriari"]),
        summary=dict(random_experiments_expected=random_experiments,
                     bo_experiments_expected=bo_experiments,
                     calendar_days=calendar_days, speedup_vs_random=bo_speedup,
                     expected_failures_before_success=expected_failures,
                     random_calendar_days=random_calendar_days,
                     expected_hits_in_space=expected_hits_in_space,
                     hit_fraction=hit_fraction,
                     experiments_per_day=experiments_per_day),
        assumptions=[
            "随机搜索命中概率 p = top_fraction，首次命中所需实验次数服从几何分布，期望 E[X] = 1/p；期望失败次数 = (1-p)/p。",
            "贝叶斯优化实验数 = 随机搜索期望 / bo_speedup；bo_speedup 是声明输入，不是实测加速比，也未规定采集函数或代理模型。",
            "calendar_days 指贝叶斯优化闭环：bo_experiments_expected / experiments_per_day；random_calendar_days 为随机搜索对照。",
            "speedup_vs_random 恒等于声明的 bo_speedup；它比较的是期望实验次数，不是每次实验的墙钟时间。",
            "expected_hits_in_space = space_size × top_fraction，仅表示整个空间中命中候选的期望数量，不改变几何期望。",
            "模型假设每次实验独立同分布且命中概率恒定；真实闭环中先验、批量和约束会改变该假设。",
        ])
