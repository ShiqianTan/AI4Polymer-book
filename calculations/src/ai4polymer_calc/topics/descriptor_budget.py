"""Feature dimension, storage and birthday-collision budget for one representation.

Fingerprint collisions are estimated for a folded n_bits key space; the raw
feature dimension is reported separately so bit fingerprints and dense
descriptor vectors are never conflated.
"""
from math import ceil, exp, ldexp

from ..schema import Graph, result
from ..sources import config, provenance
from ..units import positive_int

REPRESENTATIONS = ("morgan", "mordred", "graph", "psmiles")


def _representation_dimension(spec: dict, name: str, n_bits: int, atoms: int, bonds: int) -> tuple[int, int, int]:
    kind = spec["kind"]
    if name == "morgan":
        positive_int(n_bits, "n_bits")
        return n_bits, ceil(n_bits / 8), 1
    if name == "mordred":
        dimension = positive_int(spec["descriptor_count"], "mordred descriptor_count")
        element_bytes = positive_int(spec.get("element_bytes", 4), "element_bytes")
        return dimension, dimension * element_bytes, element_bytes
    if name == "graph":
        graph = Graph(atoms=atoms, bonds=bonds,
                      atom_feature_dim=positive_int(spec["atom_feature_dim"], "atom_feature_dim"),
                      bond_feature_dim=positive_int(spec["bond_feature_dim"], "bond_feature_dim"),
                      element_bytes=positive_int(spec.get("element_bytes", 1), "element_bytes"))
        return graph.feature_dim, graph.bytes_per_molecule, graph.element_bytes
    if name == "psmiles":
        chars = (atoms * positive_int(spec["avg_atom_symbol_chars"], "avg_atom_symbol_chars")
                 + bonds * positive_int(spec["chars_per_bond"], "chars_per_bond")
                 + positive_int(spec["star_endpoint_chars"], "star_endpoint_chars"))
        element_bytes = positive_int(spec.get("element_bytes", 1), "element_bytes")
        return chars, chars * element_bytes, element_bytes
    raise ValueError("representation must be one of " + ", ".join(REPRESENTATIONS))


def calculate(representation: str = "morgan", n_bits: int = 2048, radius: int = 2,
              atoms: int = 100, bonds: int = 105, library_size: int = 1_000_000) -> dict:
    if representation not in REPRESENTATIONS:
        raise ValueError("representation must be one of " + ", ".join(REPRESENTATIONS))
    positive_int(n_bits, "n_bits")
    positive_int(radius, "radius", allow_zero=True)
    positive_int(atoms, "atoms")
    positive_int(bonds, "bonds", allow_zero=True)
    positive_int(library_size, "library_size")
    if representation == "morgan" and radius != 2:
        raise ValueError("ECFP4 equivalence is stated for Morgan radius 2; other radii require their own assumption")

    spec = config("descriptors.json")["representations"][representation]
    feature_dim, bytes_per_molecule, element_bytes = _representation_dimension(spec, representation, n_bits, atoms, bonds)
    pairs = library_size * (library_size - 1) // 2
    expected_collisions = ldexp(float(pairs), -n_bits) if pairs.bit_length() <= 1000 else 0.0
    collision_probability = -exp(-expected_collisions) + 1.0
    expected_unique = max(0.0, library_size - expected_collisions)
    word_operations = pairs * ceil(n_bits / 64)

    return result(
        calculation="descriptor-budget",
        model=f"{representation}-representation-budget",
        scenario=dict(representation=representation, n_bits=n_bits, radius=radius, atoms=atoms,
                      bonds=bonds, library_size=library_size, element_bytes=element_bytes,
                      collision_key_space="folded n_bits fingerprint"),
        sources=provenance(spec.get("source_ids", [])),
        summary=dict(representation=representation, feature_dim=feature_dim,
                     bits_per_molecule=bytes_per_molecule * 8, bytes_per_molecule=bytes_per_molecule,
                     library_size=library_size, fingerprint_space_bits=n_bits,
                     expected_unique_fingerprints=expected_unique,
                     expected_collisions=expected_collisions,
                     collision_probability=collision_probability,
                     pairwise_comparison_count=library_size * (library_size - 1) // 2,
                     xor_popcount_word_operations=word_operations),
        assumptions=[
            "特征维度按声明表示规格计算：Morgan/ECFP 为 n_bits 位、Mordred 为声明描述符条数、graph 为原子与键特征拼接维度、PSMILES 为字符串长度估计；不是实测内存或运行时占用。",
            f"ECFP4 等价于 Morgan 半径 2、{n_bits} 位；若改变半径必须改用对应 ECFP 阶数，本工具拒绝把其他半径当作 ECFP4。",
            "去重、检索或聚类时所有表示都被折叠为同一 n_bits 指纹键空间，因此碰撞按生日问题在 2^n_bits 上估计；稠密描述符之间的精确浮点碰撞不在此模型内。",
            "期望碰撞对数 = C(M,2)/2^n_bits，至少一次碰撞的概率 = 1-exp(-期望碰撞对数)；两者都是均匀随机指纹的期望，不是对真实高分子分布或相关性的预测。",
            "bytes_per_molecule 采用按位打包（位指纹向上取整到字节）或声明元素宽度；未计入索引、标签、图结构或对齐填充。",
            "pairwise_comparison_count 是全库两两精确比较次数；xor_popcount_word_operations 假设每个 64 位字一次异或加一次 popcount，不是实测指令数。",
        ])
