# gnn-forward — message-passing-gnn-4layer-256hidden

输入：`{"atoms": 100, "bonds": 105, "device": "a100-80gb-sxm", "edge_features": 32, "efficiency": 0.3, "ffn_multiplier": 4, "heads": 8, "hidden": 256, "layers": 4, "num_atom_types": 32, "num_bond_types": 8, "readout": "attention"}`

| 来源 | 标题 | URL | 访问日期 |
| --- | --- | --- | --- |
| mpnn-gilmer | Gilmer et al., Neural Message Passing for Quantum Chemistry, ICML 2017 | https://arxiv.org/abs/1704.01212 | 2026-09-16 |
| transformer-vaswani | Vaswani et al., Attention Is All You Need, NeurIPS 2017 | https://arxiv.org/abs/1706.03762 | 2026-09-16 |
| device-a100 | NVIDIA A100 Tensor Core GPU datasheet | https://www.nvidia.com/en-us/data-center/a100/ | 2026-09-16 |

## 结果

| 结果 | 值 |
| --- | ---: |
| message_passing_flops | 327,127,040 |
| readout_flops | 102,400 |
| mlp_head_flops | 131,584 |
| total_flops | 327,361,024 |
| parameters | 1,948,674 |
| aggregation_scalar_adds | 26,880 |
| readout_scalar_adds | 25,600 |
| flops_per_parameter | 167.992 |
| transformer_parameters | 3,233,280 |
| transformer_forward_flops | 670,237,184 |
| inference_seconds | 3.49745e-06 |
| inference_energy_estimate | 0.00139898 |

逐项推导

| term | flops | derivation |
| --- | --- | --- |
| `"qkv_projection"` | 157,286,400 | `"3 × 2 × N × H² × L"` |
| `"edge_message_mlp"` | 116,981,760 | `"2 × B × (2H + E) × H × L"` |
| `"attention_score"` | 215,040 | `"2 × B × H × L"` |
| `"attention_weighted_sum"` | 215,040 | `"2 × B × H × L"` |
| `"node_update_mlp"` | 52,428,800 | `"2 × N × H² × L"` |
| `"readout"` | 102,400 | `"attention readout"` |
| `"mlp_head"` | 131,584 | `"2 × H² + 2 × H"` |

## 假设与边界

- 消息传递层工作逐项推导：QKV 投影 3×2NH²、逐边消息 MLP 2B(2H+E)H、注意力打分 2BH、加权求和 2BH、节点更新 MLP 2NH²，每项乘层数 L。
- 注意力头数 H_heads 只改变参数分组与并行布局；在声明宽度下总 FLOPs 与头数无关，本模型不引入每头额外开销。
- 聚合为逐边标量加法 B×H，单独记为 scalar adds，不计入矩阵 FLOPs；readout 的 sum/mean 同样只有标量加法。
- 参数由原子/键嵌入、逐层 QKV/消息/更新/输出投影、readout 与两层预测头组成；未计归一化层、dropout、位置编码或量化缩放参数。
- Transformer 基线使用相同层数、隐藏宽度与 token 数（token = 原子数），逐层 24·T·H² + 4·T²·H，FFN 倍率 4；它是尺度对照，不是等参数对照。
- inference_energy_estimate = 总 FLOPs / (设备峰值 × 声明效率) × TDP，单位为焦耳；未含数据搬运、通信与冷却，不是实测能耗。
- 输入原子/键数来自声明图统计；图批处理、稀疏索引与内核填充未计入，实际吞吐需按后端测量。
