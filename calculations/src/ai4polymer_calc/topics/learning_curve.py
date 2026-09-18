"""Invert a declared power-law learning curve MAE(n) = MAE_inf + A·n^(-alpha).

The curve parameters are declared inputs, not fitted measurements, unless a
scenario supplies fitted values; the module never invents a fit.
"""
from math import ceil, isfinite

from ..schema import result
from ..sources import provenance
from ..units import positive_int, positive_number


def _invert(mae_inf: float, a: float, alpha: float, target: float):
    gap = target - mae_inf
    if gap <= 0:
        return None
    return (a / gap) ** (1.0 / alpha)


def _mae(mae_inf: float, a: float, alpha: float, n: float) -> float:
    return mae_inf + a * n ** (-alpha)


def calculate(mae_inf: float = 0.05, a: float = 1.0, alpha: float = 0.5,
              target_mae: float = 0.2, n_max: int = 100_000,
              strict_mae: float = 0.1) -> dict:
    positive_number(a, "a")
    positive_number(alpha, "alpha")
    positive_int(n_max, "n_max")
    if not isfinite(mae_inf) or mae_inf < 0:
        raise ValueError("mae_inf must be a finite nonnegative number")
    positive_number(target_mae, "target_mae")
    positive_number(strict_mae, "strict_mae")
    if strict_mae >= target_mae:
        raise ValueError("strict_mae must be smaller (stricter) than target_mae")

    required_n = _invert(mae_inf, a, alpha, target_mae)
    required_experiments = ceil(required_n) if required_n is not None else None
    mae_at_n_max = _mae(mae_inf, a, alpha, n_max)
    achievable = mae_at_n_max <= target_mae
    strict_required_n = _invert(mae_inf, a, alpha, strict_mae)
    strict_experiments = ceil(strict_required_n) if strict_required_n is not None else None
    marginal = (strict_experiments - required_experiments
                if required_experiments is not None and strict_experiments is not None else None)

    curve = []
    n = 1
    while n <= n_max:
        curve.append({"n": n, "mae": _mae(mae_inf, a, alpha, n)})
        n *= 10
    if curve and curve[-1]["n"] != n_max:
        curve.append({"n": n_max, "mae": mae_at_n_max})

    return result(
        calculation="learning-curve",
        model="power-law-learning-curve",
        scenario=dict(mae_inf=mae_inf, a=a, alpha=alpha, target_mae=target_mae,
                      n_max=n_max, strict_mae=strict_mae,
                      parameter_origin="declared input, not a fitted measurement"),
        sources=provenance(["learning-curve-hestness", "learning-curve-rosenfeld"]),
        summary=dict(required_n=required_n, required_n_experiments=required_experiments,
                     mae_at_n_max=mae_at_n_max, target_achievable_within_n_max=achievable,
                     strict_target_required_n=strict_required_n,
                     strict_target_required_n_experiments=strict_experiments,
                     marginal_experiments_to_strict_target=marginal,
                     target_reduction=target_mae - strict_mae,
                     curve=curve),
        assumptions=[
            "学习曲线形式为 MAE(n) = MAE_inf + A·n^(-alpha)；A、alpha 与 MAE_inf 都是声明输入，除非场景文件显式提供拟合值，否则不是拟合测量结果。",
            "所需样本数由反解得到：n = (A / (target - MAE_inf))^(1/alpha)；要求 target > MAE_inf，否则返回 null（不可达）。",
            "required_n_experiments = ceil(required_n)，即至少需要的整数训练样本数；连续值与整数解分别保存。",
            "target_achievable_within_n_max 表示在 n_max 处 MAE 是否已不高于目标；它只比较曲线外推，不代表真实数据可获得。",
            "边际数据 = 更严目标所需样本数 − 原目标所需样本数；两个目标都必须严格高于 MAE_inf 才能给出数值。",
            "曲线采样点仅用于展示幂律形状；外推到 n_max 以外不受支持。",
        ])
