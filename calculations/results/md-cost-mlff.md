# md-cost — md-mlff-declared-cost-model

输入：`{"atoms": 5000, "device": "a100-80gb-sxm", "device_name": "NVIDIA A100 80GB SXM", "efficiency": 0.3, "gpus": 1, "method": "md-mlff", "precision": "BF16", "timestep_fs": 1.0, "timesteps": 1000000}`

| 来源 | 标题 | URL | 访问日期 |
| --- | --- | --- | --- |
| device-a100 | NVIDIA A100 Tensor Core GPU datasheet | https://www.nvidia.com/en-us/data-center/a100/ | 2026-09-16 |

## 结果

| 结果 | 值 |
| --- | ---: |
| total_steps | 1,000,000 |
| atom_steps | 5,000,000,000 |
| force_evaluations | 1,000,000 |
| flops_or_force_evals | 10,000,400,000,000,000 |
| neighbor_list_rebuilds | 100,000 |
| neighbor_flops | 400,000,000,000 |
| gpu_seconds | 106.842 |
| gpu_hours | 0.0296783 |
| wall_clock_hours | 0.0296783 |
| energy_kwh | 0.0118713 |
| simulated_time_ns | 1,000,000 |

分项

| term | value |
| --- | --- |
| `"cost_model"` | `"MLFF: 2000000 FLOPs/原子/步 × 5000 原子 × 1000000 步，加近邻表重建"` |
| `"simulated_time_ns"` | 1,000,000 |

## 假设与边界

- 本专题使用声明的成本模型，不是实测基准：FF 为近邻对线性模型，MLFF 为逐原子推理 FLOPs 模型，DFT 为 O(N^3) SCF 模型。
- FF 模型取每原子 40 近邻对、每对 40 FLOPs、每 10 步重建近邻表；这些常数是建模输入。
- MLFF 模型取每原子每步 2,000,000 FLOPs；它随原子数线性增长，不含训练与模型加载。
- DFT 模型取 50 次 SCF、每次 10,000 FLOPs/原子^3；立方标度在中等体系即会主导。
- 设备峰值取自公开数据表（BF16 张量核心稠密峰值，DFT 用 FP32 向量峰值），未做精度、稀疏或实测标定；效率是声明的理想利用率，不是 MFU 测量。
- gpu_hours = 总 FLOPs / (峰值 × 效率) / 3600；wall_clock_hours = gpu_hours / gpus，假设理想并行与无通信开销。
- energy_kwh 用设备 TDP × gpu_hours 估算，不含冷却、供电损耗与空闲；TDP 不是实测功耗。
- timestep_fs 与 simulated_time_ns 仅用于说明物理时长，不参与 FLOPs 折算。
