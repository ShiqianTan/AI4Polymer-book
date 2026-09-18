"""Exact combinatorial size of a declared polymer sequence space.

All counts are arbitrary-precision integers; the synthesizable rule and the
comparison against known datasets are declared modeling inputs.
"""
from math import comb, factorial

from ..schema import parse_stoichiometry, result, sequence_count, sequences_at_most_k_types
from ..sources import config, provenance
from ..units import log10_big_int, positive_int

ARCHITECTURES = ("homopolymer", "random", "block", "alternating")


def _composition_counts(fractions: tuple[float, ...], chain_length: int) -> list[int]:
    exact = [value * chain_length for value in fractions]
    counts = [int(value) for value in exact]
    remainder = chain_length - sum(counts)
    order = sorted(range(len(counts)), key=lambda index: exact[index] - counts[index], reverse=True)
    for index in order[:remainder]:
        counts[index] += 1
    return counts


def _composition_sequences(fractions: tuple[float, ...], chain_length: int) -> int:
    counts = _composition_counts(fractions, chain_length)
    total = factorial(chain_length)
    for count in counts:
        total //= factorial(count)
    return total


def calculate(monomers: int = 10, chain_length: int = 100, copolymer: str = "random",
              stoichiometry: str = "1,1") -> dict:
    if copolymer not in ARCHITECTURES:
        raise ValueError("copolymer must be one of " + ", ".join(ARCHITECTURES))
    positive_int(monomers, "monomers")
    positive_int(chain_length, "chain_length")
    if copolymer != "homopolymer" and monomers < 2:
        raise ValueError("non-homopolymer architectures require at least two monomers")
    fractions = parse_stoichiometry(stoichiometry, monomers)

    total = sequence_count(monomers, chain_length, copolymer)
    rules = config("datasets.json")["synthesis_rules"]
    max_distinct = positive_int(rules["max_distinct_monomers"], "max_distinct_monomers")
    if copolymer == "random":
        synthesizable = sequences_at_most_k_types(monomers, chain_length, max_distinct)
    else:
        synthesizable = total
    synthesizable_fraction = synthesizable / total

    composition_count = _composition_sequences(fractions, chain_length) if copolymer == "random" else None

    datasets = config("datasets.json")["datasets"]
    comparison = []
    for row in datasets:
        size = row.get("size")
        comparison.append({
            "dataset": row["name"],
            "size": size,
            "coverage": (size / total) if size else None,
            "log10_sequence_count_per_entry": (log10_big_int(total) - log10_big_int(size)) if size else None,
            "verification": row.get("verification", "reported"),
        })
    primary_id = config("datasets.json").get("primary_dataset", datasets[0]["id"])
    primary = next(row for row in datasets if row["id"] == primary_id)

    source_ids = sorted({source_id for row in datasets for source_id in row.get("source_ids", [])})
    return result(
        calculation="chemical-space",
        model=f"combinatorial-{copolymer}-space",
        scenario=dict(monomers=monomers, chain_length=chain_length, copolymer=copolymer,
                      stoichiometry=stoichiometry, max_distinct_monomers=max_distinct,
                      primary_dataset=primary["name"]),
        sources=provenance(source_ids),
        summary=dict(sequence_count=total, log10_sequence_count=log10_big_int(total),
                     synthesizable_count=synthesizable, synthesizable_fraction=synthesizable_fraction,
                     composition_constrained_sequence_count=composition_count,
                     known_library=primary["name"], known_library_size=primary["size"],
                     coverage_of_known_library=(primary["size"] / total) if primary["size"] else None,
                     log10_sequence_count_per_known_entry=(log10_big_int(total) - log10_big_int(primary["size"]))
                     if primary["size"] else None,
                     known_libraries_compared=len(datasets),
                     dataset_comparison=comparison),
        assumptions=[
            "序列计数使用精确大整数：均聚物 = N；无规共聚物 = N^L；交替共聚物 = N(N-1)（严格二元交替，L>=2）；嵌段共聚物 = N(N-1)(L-1)（两嵌段，有序单体对与嵌段长度）。",
            "无规共聚物的组成约束计数为多项式系数 L!/(n_1!...n_k!)，其中 n_i 由声明配比按最大余数法取整到链长 L；配比本身是建模输入，不是实验测定。",
            "规则式可合成库把链上不同单体种类限制为至多 max_distinct 种：无规序列的可达数 = sum_j C(N,j)·j!·S(L,j)（S 为第二类斯特林数）；均聚/交替/嵌段构型天然满足该规则，故可达比例记为 1。",
            "synthesizable_fraction = 可达序列数 / 全部序列数；它衡量规则库覆盖的理论比例，不代表实际合成收率或热力学可行性。",
            "coverage_of_known_library = 已知库条目数 / 理论序列数；对 size 为 null 的数据集返回 null。数据集规模为公开报告元数据，引用前需人工复核。",
            "log10_sequence_count 使用任意精度整数的位长计算，避免 double 溢出；序列数本身在 JSON 中以完整整数保存。",
        ])
