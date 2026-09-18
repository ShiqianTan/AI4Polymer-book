"""Declared retrosynthesis-search and route-feasibility accounting.

Exhaustive versus beam search on a retrosynthesis tree, the product decay of a
multi-step route, and a four-stage feasibility funnel. Every number is a
declared model output, not a measurement.
"""
from math import log

from ..schema import result
from ..sources import provenance
from ..units import fraction, positive_int, positive_number


def _beam_nodes(branching, depth, beam):
    retained = 1
    generated = 0
    for _ in range(depth):
        children = retained * branching
        generated += children
        retained = min(beam, children)
    return generated


def _funnel(initial_candidates, stages):
    survivors = float(initial_candidates)
    rows = []
    for label, rate in stages:
        survivors *= rate
        rows.append(dict(stage=label, pass_rate=rate, survivors=survivors))
    return rows, survivors


def calculate(branching=50, depth=5, beam=10, step_yield=0.8, target_yield=0.3,
              initial_candidates=8910, feasibility=0.6, route_length_pass=0.6,
              yield_pass=0.5, cost_pass=0.4) -> dict:
    positive_int(branching, "branching")
    positive_int(depth, "depth")
    positive_int(beam, "beam")
    step_yield = fraction(step_yield, "step_yield")
    target_yield = fraction(target_yield, "target_yield")
    positive_int(initial_candidates, "initial_candidates")

    exhaustive = branching ** depth
    beam_nodes = _beam_nodes(branching, depth, beam)
    route_yield = step_yield ** depth
    max_steps = int(log(target_yield) / log(step_yield))
    yield_curve = [dict(steps=steps, total_yield=step_yield ** steps)
                   for steps in range(1, depth + 3)]
    stages = [("可行性", fraction(feasibility, "feasibility")),
              ("路线长度", fraction(route_length_pass, "route_length_pass")),
              ("产率", fraction(yield_pass, "yield_pass")),
              ("成本", fraction(cost_pass, "cost_pass"))]
    funnel, survivors = _funnel(initial_candidates, stages)

    return result(
        calculation="synthesis-route",
        model="declared-retrosynthesis-beam-and-yield-funnel",
        scenario=dict(branching=branching, depth=depth, beam=beam,
                      step_yield=step_yield, target_yield=target_yield,
                      initial_candidates=initial_candidates, feasibility=feasibility,
                      route_length_pass=route_length_pass, yield_pass=yield_pass,
                      cost_pass=cost_pass),
        sources=provenance(["retrosynthesis-segler-2018", "aizynthfinder-2020"]),
        summary=dict(
            exhaustive_nodes=exhaustive, beam_nodes=beam_nodes,
            pruning_ratio=exhaustive / beam_nodes,
            route_yield=route_yield, max_steps_at_target=max_steps,
            yield_curve=yield_curve, funnel=funnel,
            final_survivors=survivors,
            overall_pass=survivors / initial_candidates),
        assumptions=[
            "穷举搜索的节点数按 $b^{d}$ 计；束搜索每层只保留前 $k$ 个节点，展开数为各层保留节点数乘以分支因子之和。",
            "路线总产率按 $Y=\\bar y^{d}$ 计，各步产率独立同分布；达到目标总产率的最大步数为 $\\lfloor\\ln Y_\\text{target}/\\ln\\bar y\\rfloor$。",
            "漏斗四级通过率（可行性、路线长度、产率、成本）为声明输入，只用于说明量级，不代表实测通过率。",
            "全部数值为声明模型输出，参数为建模输入，不是实验测量。",
        ])
