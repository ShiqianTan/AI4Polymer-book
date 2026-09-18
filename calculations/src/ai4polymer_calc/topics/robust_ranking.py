"""Rank declared candidates by mean and prediction interval on a specification window.

The candidate means, interval half-widths and the specification window are declared
modeling inputs, not measurements. The Gaussian tail probabilities, the lower bounds
and the rankings under a mean-only and a mean-plus-interval criterion are computed
exactly from those inputs.
"""
from math import erf, sqrt

from ..schema import result
from ..sources import provenance
from ..units import positive_number

SOURCE_IDS = ("uncertainty-survey",)


def _cdf(z: float) -> float:
    return 0.5 * (1.0 + erf(z / sqrt(2.0)))


def _probability_in_window(mean: float, sigma: float, low: float, high: float) -> float:
    return _cdf((high - mean) / sigma) - _cdf((low - mean) / sigma)


def calculate(means: tuple = (205.0, 205.0), half_widths: tuple = (20.0, 3.0),
              spec_low: float = 200.0, spec_high: float = 210.0) -> dict:
    if len(means) != len(half_widths) or not means:
        raise ValueError("means and half_widths must have the same nonzero length")
    if spec_high <= spec_low:
        raise ValueError("spec_high must exceed spec_low")
    for value in means:
        positive_number(value, "mean")
    for value in half_widths:
        positive_number(value, "half_width")

    candidates = []
    for index, (mean, half_width) in enumerate(zip(means, half_widths), start=1):
        candidates.append({
            "candidate": f"C{index}",
            "mean": float(mean),
            "half_width": float(half_width),
            "lower_bound": float(mean - half_width),
            "upper_bound": float(mean + half_width),
            "probability_in_window": _probability_in_window(mean, half_width, spec_low, spec_high),
        })

    mean_only = sorted(candidates, key=lambda row: -row["mean"])
    interval = sorted(candidates, key=lambda row: (-row["lower_bound"], row["half_width"]))

    return result(
        calculation="robust-ranking",
        model="declared-mean-interval-ranking",
        scenario=dict(means=list(means), half_widths=list(half_widths),
                      spec_low=spec_low, spec_high=spec_high),
        sources=provenance(SOURCE_IDS),
        summary=dict(
            candidate_count=len(candidates),
            spec_low=spec_low,
            spec_high=spec_high,
            candidates=candidates,
            mean_only_order=[row["candidate"] for row in mean_only],
            mean_only_tie=len({row["mean"] for row in candidates}) == 1,
            interval_order=[row["candidate"] for row in interval],
            best_by_interval=interval[0]["candidate"],
            best_by_probability=max(candidates, key=lambda row: row["probability_in_window"])["candidate"],
            ranking_flip=mean_only[0]["candidate"] != interval[0]["candidate"],
        ),
        assumptions=[
            "候选均值与区间半宽为声明输入：C1 为 205 ± 20，C2 为 205 ± 3，单位与目标性质一致（示例取 ℃）。",
            "区间半宽按一倍标准差处理，σ = half_width；在规范窗内的概率由正态分布尾部差 Φ((high−μ)/σ) − Φ((low−μ)/σ) 计算，Φ 用标准库的误差函数实现。",
            "均值加区间排序按下界 mean − half_width 降序，下界相同时取区间更窄者；均值排序只按 mean 降序。",
            "两个候选均值相同时均值排序并列，是否翻转由下界决定；该判据只说明不确定度如何改变排序，不代表真实实验重复性。",
        ])
