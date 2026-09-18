"""Enumerate a declared two-block design space and screen it on declared surrogates.

The candidate set is the exact combinatorial two-block space N(N-1)(L-1). The two
surrogate objectives, the reference point and the scalarization grids are declared
modeling inputs, not measured properties. The Pareto front, hypervolume and
scalarization coverage are computed exactly on those declared objectives.
"""
from math import inf, pi, sin

from ..schema import result
from ..sources import provenance
from ..units import positive_int

SOURCE_IDS = ("multiobjective-ehvi", "multiobjective-nsga2")


def _surrogates(first_fraction: float) -> tuple[float, float]:
    selectivity = 0.30 + 0.65 * first_fraction
    permeability = (0.95 - 0.65 * first_fraction
                    + 0.10 * sin(2.0 * pi * first_fraction)
                    + 0.04 * sin(6.0 * pi * first_fraction))
    return round(selectivity, 6), round(permeability, 6)


def _enumerate(monomers: int, chain_length: int) -> list[tuple[float, float, int, int, int]]:
    rows = []
    for first in range(monomers):
        for second in range(monomers):
            if first == second:
                continue
            for split in range(1, chain_length):
                selectivity, permeability = _surrogates(split / chain_length)
                rows.append((selectivity, permeability, first, second, split))
    return rows


def _unique_points(rows) -> list[tuple[float, float]]:
    seen = []
    for row in rows:
        point = (row[0], row[1])
        if point not in seen:
            seen.append(point)
    return seen


def _pareto(points) -> list[tuple[float, float]]:
    front = []
    for point in points:
        dominated = any(
            other[0] >= point[0] and other[1] >= point[1]
            and (other[0] > point[0] or other[1] > point[1])
            for other in points if other != point)
        if not dominated:
            front.append(point)
    return sorted(front)


def _hypervolume(front, reference) -> float:
    usable = sorted(((s, p) for s, p in front if s > reference[0] and p > reference[1]),
                    key=lambda point: point[0])
    volume = 0.0
    previous = reference[0]
    for selectivity, permeability in usable:
        volume += (permeability - reference[1]) * (selectivity - previous)
        previous = selectivity
    return volume


def _weighted_sum_points(front, steps: int) -> set:
    covered = set()
    for index in range(steps):
        weight = index / (steps - 1)
        best = max(front, key=lambda point: weight * point[0] + (1 - weight) * point[1])
        covered.add(best)
    return covered


def _epsilon_points(front, steps: int) -> set:
    lowest = min(point[1] for point in front)
    highest = max(point[1] for point in front)
    covered = set()
    for index in range(steps):
        epsilon = lowest + (highest - lowest) * index / (steps - 1)
        feasible = [point for point in front if point[1] >= epsilon]
        if feasible:
            covered.add(max(feasible, key=lambda point: point[0]))
    return covered


def _knee(front) -> tuple[float, float]:
    if len(front) < 3:
        return front[0]
    start, end = front[0], front[-1]
    span = ((end[0] - start[0]) ** 2 + (end[1] - start[1]) ** 2) ** 0.5
    best, distance = front[0], -inf
    for point in front[1:-1]:
        cross = abs((end[0] - start[0]) * (start[1] - point[1])
                    - (start[0] - point[0]) * (end[1] - start[1]))
        gap = cross / span if span else 0.0
        if gap > distance:
            best, distance = point, gap
    return best


def calculate(monomers: int = 10, chain_length: int = 100, reference: tuple = (0.0, 0.0),
              weight_steps: int = 11, epsilon_steps: int = 21) -> dict:
    positive_int(monomers, "monomers")
    positive_int(chain_length, "chain_length")
    positive_int(weight_steps, "weight_steps")
    positive_int(epsilon_steps, "epsilon_steps")
    if len(reference) != 2:
        raise ValueError("reference must list two numbers")

    rows = _enumerate(monomers, chain_length)
    points = _unique_points(rows)
    front = _pareto(points)
    dominated = [point for point in points if point not in front]
    weighted = _weighted_sum_points(front, weight_steps)
    epsilon = _epsilon_points(front, epsilon_steps)
    knee = _knee(front)

    return result(
        calculation="pareto-screen",
        model="declared-two-block-pareto-screen",
        scenario=dict(monomers=monomers, chain_length=chain_length,
                      reference=list(reference), weight_steps=weight_steps,
                      epsilon_steps=epsilon_steps),
        sources=provenance(SOURCE_IDS),
        summary=dict(
            enumerated_candidates=len(rows),
            distinct_objective_points=len(points),
            realizations_per_point=len(rows) // len(points),
            pareto_front_points=len(front),
            pareto_fraction=len(front) / len(points),
            hypervolume=_hypervolume(front, reference),
            weighted_sum_points=len(weighted),
            weighted_sum_coverage=len(weighted) / len(front),
            epsilon_constraint_points=len(epsilon),
            epsilon_constraint_coverage=len(epsilon) / len(front),
            knee_selectivity=knee[0],
            knee_permeability=knee[1],
            front_endpoints=[[front[0][0], front[0][1]], [front[-1][0], front[-1][1]]],
            front=[[s, p] for s, p in front],
            dominated=[[s, p] for s, p in sorted(dominated)],
            weighted_sum_optimal=[[s, p] for s, p in sorted(weighted)],
            epsilon_constraint_optimal=[[s, p] for s, p in sorted(epsilon)],
        ),
        assumptions=[
            "候选集为精确组合数 N(N-1)(L-1)：有序单体对与两嵌段分点，计数与 chemical-space 的嵌段模型一致。",
            "两个目标为声明代理模型：选择性代理 = 0.30 + 0.65·f，渗透率代理 = 0.95 − 0.65·f + 0.10·sin(2πf) + 0.04·sin(6πf)，f 为第一嵌段的链分数；它们不是实测性质，只用于演示筛选与排序流程。",
            "支配关系按两个目标同时最大化定义；超体积相对声明参考点计算，参考点取 (0,0)。",
            "加权和覆盖为权重 0 到 1 的等距网格上的最优前沿点集合；ε-约束覆盖为在渗透率代理下限网格上最大化选择性代理所得的前沿点集合。",
            "同一目标点对应 90 个结构不同的候选（不同有序单体对），因此前沿点数是结构多样性之外的独立概念。",
        ])
