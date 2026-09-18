"""Parameter count and forward FLOPs for a message-passing GNN property predictor.

Every term is derived from declared widths; a Transformer baseline is computed
with the same depth, hidden width and token count for comparison.
"""
from ..schema import result
from ..sources import device, provenance
from ..units import positive_int

READOUTS = ("sum", "mean", "attention")
NUM_ATOM_TYPES = 32
NUM_BOND_TYPES = 8
FFN_MULTIPLIER = 4


def calculate(layers: int = 4, hidden: int = 256, atoms: int = 100, bonds: int = 105,
              edge_features: int = 32, heads: int = 8, readout: str = "attention",
              device_id: str = "a100-80gb-sxm", efficiency: float = 0.3) -> dict:
    if readout not in READOUTS:
        raise ValueError("readout must be one of " + ", ".join(READOUTS))
    positive_int(layers, "layers")
    positive_int(hidden, "hidden")
    positive_int(atoms, "atoms")
    positive_int(bonds, "bonds", allow_zero=True)
    positive_int(edge_features, "edge_features")
    positive_int(heads, "heads")
    if hidden % heads:
        raise ValueError("hidden must be divisible by heads")
    if not 0 < efficiency <= 1:
        raise ValueError("efficiency must lie in (0, 1]")

    qkv_flops = 6 * atoms * hidden * hidden
    message_flops = 2 * bonds * (2 * hidden + edge_features) * hidden
    score_flops = 2 * bonds * hidden
    weighted_sum_flops = 2 * bonds * hidden
    update_flops = 2 * atoms * hidden * hidden
    aggregation_adds = bonds * hidden
    per_layer_flops = qkv_flops + message_flops + score_flops + weighted_sum_flops + update_flops
    message_passing_flops = layers * per_layer_flops

    readout_flops = 4 * atoms * hidden if readout == "attention" else 0
    readout_adds = atoms * hidden

    mlp_head_flops = 2 * hidden * hidden + 2 * hidden

    total_flops = message_passing_flops + readout_flops + mlp_head_flops

    per_layer_params = (3 * (hidden * hidden + hidden) + (2 * hidden + edge_features) * hidden + hidden
                        + (hidden * hidden + hidden) + (hidden * hidden + hidden))
    readout_params = (hidden + 1) if readout == "attention" else 0
    head_params = hidden * hidden + hidden + hidden + 1
    embedding_params = NUM_ATOM_TYPES * hidden + NUM_BOND_TYPES * edge_features
    parameters = embedding_params + layers * per_layer_params + readout_params + head_params

    ffn = FFN_MULTIPLIER * hidden
    transformer_per_layer_flops = 24 * atoms * hidden * hidden + 4 * atoms * atoms * hidden
    transformer_parameters = (embedding_params + layers * (12 * hidden * hidden + 13 * hidden)
                              + hidden * hidden + hidden)
    transformer_forward_flops = layers * transformer_per_layer_flops + mlp_head_flops

    hardware = device(device_id)
    peak = hardware["bf16_tensor_flops_per_second"]
    inference_seconds = total_flops / (peak * efficiency)
    inference_energy_joules = inference_seconds * hardware["tdp_watts"]

    terms = [
        {"term": "qkv_projection", "flops": layers * qkv_flops, "derivation": "3 × 2 × N × H² × L"},
        {"term": "edge_message_mlp", "flops": layers * message_flops,
         "derivation": "2 × B × (2H + E) × H × L"},
        {"term": "attention_score", "flops": layers * score_flops, "derivation": "2 × B × H × L"},
        {"term": "attention_weighted_sum", "flops": layers * weighted_sum_flops, "derivation": "2 × B × H × L"},
        {"term": "node_update_mlp", "flops": layers * update_flops, "derivation": "2 × N × H² × L"},
        {"term": "readout", "flops": readout_flops, "derivation": f"{readout} readout"},
        {"term": "mlp_head", "flops": mlp_head_flops, "derivation": "2 × H² + 2 × H"},
    ]
    return result(
        calculation="gnn-forward",
        model=f"message-passing-gnn-{layers}layer-{hidden}hidden",
        scenario=dict(layers=layers, hidden=hidden, atoms=atoms, bonds=bonds,
                      edge_features=edge_features, heads=heads, readout=readout,
                      device=device_id, efficiency=efficiency, num_atom_types=NUM_ATOM_TYPES,
                      num_bond_types=NUM_BOND_TYPES, ffn_multiplier=FFN_MULTIPLIER),
        sources=provenance(["mpnn-gilmer", "transformer-vaswani", *hardware.get("source_ids", [])]),
        summary=dict(message_passing_flops=message_passing_flops, readout_flops=readout_flops,
                     mlp_head_flops=mlp_head_flops, total_flops=total_flops, parameters=parameters,
                     aggregation_scalar_adds=aggregation_adds,
                     readout_scalar_adds=readout_adds,
                     flops_per_parameter=total_flops / parameters,
                     transformer_parameters=transformer_parameters,
                     transformer_forward_flops=transformer_forward_flops,
                     inference_seconds=inference_seconds,
                     inference_energy_estimate=inference_energy_joules,
                     terms=terms),
        assumptions=[
            "消息传递层工作逐项推导：QKV 投影 3×2NH²、逐边消息 MLP 2B(2H+E)H、注意力打分 2BH、加权求和 2BH、节点更新 MLP 2NH²，每项乘层数 L。",
            "注意力头数 H_heads 只改变参数分组与并行布局；在声明宽度下总 FLOPs 与头数无关，本模型不引入每头额外开销。",
            "聚合为逐边标量加法 B×H，单独记为 scalar adds，不计入矩阵 FLOPs；readout 的 sum/mean 同样只有标量加法。",
            "参数由原子/键嵌入、逐层 QKV/消息/更新/输出投影、readout 与两层预测头组成；未计归一化层、dropout、位置编码或量化缩放参数。",
            "Transformer 基线使用相同层数、隐藏宽度与 token 数（token = 原子数），逐层 24·T·H² + 4·T²·H，FFN 倍率 4；它是尺度对照，不是等参数对照。",
            "inference_energy_estimate = 总 FLOPs / (设备峰值 × 声明效率) × TDP，单位为焦耳；未含数据搬运、通信与冷却，不是实测能耗。",
            "输入原子/键数来自声明图统计；图批处理、稀疏索引与内核填充未计入，实际吞吐需按后端测量。",
        ])
