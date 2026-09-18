# md-cost — dft-declared-cost-model

输入：`{"atoms": 500, "device": "a100-80gb-sxm", "device_name": "NVIDIA A100 80GB SXM", "efficiency": 0.3, "gpus": 1, "method": "dft", "precision": "FP32", "timestep_fs": 1.0, "timesteps": 1}`

| 来源 | 标题 | URL | 访问日期 |
| --- | --- | --- | --- |
| device-a100 | NVIDIA A100 Tensor Core GPU datasheet | https://www.nvidia.com/en-us/data-center/a100/ | 2026-09-16 |

## 结果

| 结果 | 值 |
| --- | ---: |
| total_steps | 1 |
| atom_steps | 500 |
| force_evaluations | 50 |
| flops_or_force_evals | 62,500,000,000,000 |
| neighbor_list_rebuilds | 0 |
| neighbor_flops | 0 |
| gpu_seconds | 10.6838 |
| gpu_hours | 0.00296771 |
| wall_clock_hours | 0.00296771 |
| energy_kwh | 0.00118708 |
| simulated_time_ns | 1 |

分项

| term | value |
| --- | --- |
| `"cost_model"` | `"DFT: 10000 FLOPs/原子^3 × 500^3 × 50 次 SCF"` |
| `"simulated_time_ns"` | 1 |

## 假设与边界

- 本专题使用声明的成本模型，不是实测基准：FF 为近邻对线性模型，MLFF 为逐原子推理 FLOPs 模型，DFT 为 O(N^3) SCF 模型。
- FF 模型取每原子 40 近邻对、每对 40 FLOPs、每 10 步重建近邻表；这些常数是建模输入。
- MLFF 模型取每原子每步 2,000,000 FLOPs；它随原子数线性增长，不含训练与模型加载。
- DFT 模型取 50 次 SCF、每次 10,000 FLOPs/原子^3；立方标度在中等体系即会主导。
- 设备峰值取自公开数据表（BF16 张量核心稠密峰值，DFT 用 FP32 向量峰值），未做精度、稀疏或实测标定；效率是声明的理想利用率，不是 MFU 测量。
- gpu_hours = 总 FLOPs / (峰值 × 效率) / 3600；wall_clock_hours = gpu_hours / gpus，假设理想并行与无通信开销。
- energy_kwh 用设备 TDP × gpu_hours 估算，不含冷却、供电损耗与空闲；TDP 不是实测功耗。
- timestep_fs 与 simulated_time_ns 仅用于说明物理时长，不参与 FLOPs 折算。
