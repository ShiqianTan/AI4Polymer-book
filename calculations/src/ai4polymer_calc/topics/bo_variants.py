"""Batch, constrained, multi-fidelity and cost-aware extensions of Bayesian optimization.

Every quantity is a closed form on a declared toy model: the batch design effect
is the intraclass-correlation formula, the constrained and multi-fidelity results
are declared cost and information models, and none of them is a measurement.
"""
from ..schema import result
from ..sources import provenance
from ..units import fraction, positive_int, positive_number


def calculate(space_size: int = 1_000_000, top_fraction: float = 0.001,
              batch_size: int = 8, batch_correlation: float = 0.5,
              feasible_fraction: float = 0.3, fidelity_cost_ratio: float = 0.05,
              screening_pass_fraction: float = 0.2,
              expensive_cost_ratio: float = 20.0, budget: int = 1000) -> dict:
    positive_int(space_size, "space_size")
    positive_int(batch_size, "batch_size")
    positive_int(budget, "budget")
    hit_fraction = fraction(top_fraction, "top_fraction")
    correlation = fraction(batch_correlation, "batch_correlation")
    feasible = fraction(feasible_fraction, "feasible_fraction")
    fidelity = fraction(fidelity_cost_ratio, "fidelity_cost_ratio")
    screening = fraction(screening_pass_fraction, "screening_pass_fraction")
    positive_number(expensive_cost_ratio, "expensive_cost_ratio")

    batch_effective = batch_size / (1.0 + (batch_size - 1) * correlation)
    batch_retained = batch_effective / batch_size
    feasible_per_batch = batch_size * feasible
    zero_feasible = (1.0 - feasible) ** batch_size
    experiments_per_feasible = 1.0 / feasible
    ladder_cost = fidelity + screening
    fidelity_speedup = 1.0 / ladder_cost
    cheap_evaluations = float(budget)
    expensive_evaluations = budget / expensive_cost_ratio
    information_threshold = 1.0 / expensive_cost_ratio
    expected_hits = budget * hit_fraction
    experiments_per_hit = 1.0 / hit_fraction

    return result(
        calculation="bo-variants",
        model="closed-form-variant-accounting",
        scenario=dict(space_size=space_size, top_fraction=hit_fraction,
                      batch_size=batch_size, batch_correlation=correlation,
                      feasible_fraction=feasible, fidelity_cost_ratio=fidelity,
                      screening_pass_fraction=screening,
                      expensive_cost_ratio=expensive_cost_ratio, budget=budget,
                      note="declared toy model; not a measured speedup"),
        sources=provenance(["bayesian-optimization-gp-ucb", "batch-bayesopt-local-penalization",
                            "constrained-bayesopt-unknown", "multifidelity-bayesopt-continuous",
                            "cost-aware-bayesopt"]),
        summary=dict(batch_effective_size=batch_effective,
                     batch_information_retained=batch_retained,
                     expected_feasible_per_batch=feasible_per_batch,
                     probability_zero_feasible_batch=zero_feasible,
                     expected_experiments_per_feasible=experiments_per_feasible,
                     infeasible_budget_fraction=1.0 - feasible,
                     fidelity_speedup=fidelity_speedup,
                     ladder_cost_high_fidelity_equivalent=ladder_cost,
                     cheap_evaluations_in_budget=cheap_evaluations,
                     expensive_evaluations_in_budget=expensive_evaluations,
                     cost_aware_information_threshold=information_threshold,
                     expected_hits_in_budget=expected_hits,
                     expected_experiments_per_hit=experiments_per_hit),
        assumptions=[
            "批量有效样本量用组内相关设计效应：B_eff = B / (1 + (B-1)ρ)，ρ 为批内候选平均相关，是声明输入。",
            "约束结果假设每个候选独立的可行概率 q：每批期望可行数 Bq，全批不可行概率 (1-q)^B。",
            "多保真阶梯假设低保真成本为高保真的 r 倍、仅通过比例 p 的候选进入高保真，则一个高保真当量的成本为 r+p。",
            "成本感知阈值假设一次廉价评估的信息量为一次昂贵评估的 c 倍时，若 c > 1/成本比则廉价评估的单位成本收益更高。",
            "命中期望仍为几何分布的 1/p，预算内期望命中数 = 预算 × p；本模型不含先验、批量与约束对命中率的改变。",
        ])
