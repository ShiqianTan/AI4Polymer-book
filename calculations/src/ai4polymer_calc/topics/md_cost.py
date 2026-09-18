"""Declared cost models for polymer MD/DFT simulation, converted to GPU hours.

Each method has its own explicit cost model; these are declared models, not
benchmarks, and the device peak is a datasheet value without calibration.
"""
from math import ceil

from ..schema import result
from ..sources import device, provenance
from ..units import ceil_div, positive_int, positive_number

METHODS = ("md-ff", "md-mlff", "dft")

COST_MODELS = {
    "md-ff": {
        "neighbor_pairs_per_atom": 40,
        "flops_per_pair": 40,
        "neighbor_rebuild_interval": 10,
        "neighbor_flops_per_pair": 20,
    },
    "md-mlff": {
        "mlff_flops_per_atom": 2_000_000,
        "neighbor_rebuild_interval": 10,
        "neighbor_pairs_per_atom": 40,
        "neighbor_flops_per_pair": 20,
    },
    "dft": {
        "scf_iterations": 50,
        "flops_per_atom_cubed": 10_000,
    },
}


def calculate(atoms: int = 5000, timesteps: int = 1_000_000, timestep_fs: float = 1.0,
              method: str = "md-ff", device_id: str = "a100-80gb-sxm",
              efficiency: float = 0.3, gpus: int = 1) -> dict:
    if method not in METHODS:
        raise ValueError("method must be one of " + ", ".join(METHODS))
    positive_int(atoms, "atoms")
    positive_int(timesteps, "timesteps")
    positive_number(timestep_fs, "timestep_fs")
    positive_int(gpus, "gpus")
    if not 0 < efficiency <= 1:
        raise ValueError("efficiency must lie in (0, 1]")
    hardware = device(device_id)
    model = COST_MODELS[method]
    atom_steps = atoms * timesteps

    if method == "md-ff":
        flops = timesteps * atoms * model["neighbor_pairs_per_atom"] * model["flops_per_pair"]
        rebuilds = ceil_div(timesteps, model["neighbor_rebuild_interval"])
        neighbor_flops = rebuilds * atoms * model["neighbor_pairs_per_atom"] * model["neighbor_flops_per_pair"]
        total_flops = flops + neighbor_flops
        force_evaluations = timesteps
        cost_model = (f"FF: {atoms} 原子 × {model['neighbor_pairs_per_atom']} 近邻对/原子 × "
                      f"{model['flops_per_pair']} FLOPs/对 × {timesteps} 步，加每 "
                      f"{model['neighbor_rebuild_interval']} 步重建近邻表")
    elif method == "md-mlff":
        flops = timesteps * atoms * model["mlff_flops_per_atom"]
        rebuilds = ceil_div(timesteps, model["neighbor_rebuild_interval"])
        neighbor_flops = rebuilds * atoms * model["neighbor_pairs_per_atom"] * model["neighbor_flops_per_pair"]
        total_flops = flops + neighbor_flops
        force_evaluations = timesteps
        cost_model = (f"MLFF: {model['mlff_flops_per_atom']} FLOPs/原子/步 × {atoms} 原子 × "
                      f"{timesteps} 步，加近邻表重建")
    else:
        flops = model["scf_iterations"] * model["flops_per_atom_cubed"] * atoms ** 3
        neighbor_flops = 0
        total_flops = flops
        force_evaluations = model["scf_iterations"]
        cost_model = (f"DFT: {model['flops_per_atom_cubed']} FLOPs/原子^3 × {atoms}^3 × "
                      f"{model['scf_iterations']} 次 SCF")

    peak = hardware["bf16_tensor_flops_per_second"] if method != "dft" else hardware["fp32_flops_per_second"]
    gpu_seconds = total_flops / (peak * efficiency)
    gpu_hours = gpu_seconds / 3600
    wall_clock_hours = gpu_hours / gpus
    energy_kwh = gpu_hours * hardware["tdp_watts"] / 1000

    return result(
        calculation="md-cost",
        model=f"{method}-declared-cost-model",
        scenario=dict(atoms=atoms, timesteps=timesteps, timestep_fs=timestep_fs, method=method,
                      device=device_id, efficiency=efficiency, gpus=gpus, device_name=hardware["name"],
                      precision=("FP32" if method == "dft" else "BF16")),
        sources=provenance(hardware.get("source_ids", [])),
        selected_peak=dict(device=device_id, precision=("FP32" if method == "dft" else "BF16"),
                           flops_per_second=peak, basis=hardware["note"]),
        summary=dict(total_steps=timesteps, atom_steps=atom_steps,
                     force_evaluations=force_evaluations,
                     flops_or_force_evals=total_flops,
                     neighbor_list_rebuilds=ceil_div(timesteps, model["neighbor_rebuild_interval"]) if method != "dft" else 0,
                     neighbor_flops=neighbor_flops,
                     gpu_seconds=gpu_seconds, gpu_hours=gpu_hours,
                     wall_clock_hours=wall_clock_hours, energy_kwh=energy_kwh,
                     simulated_time_ns=timesteps * timestep_fs,
                     breakdown=[{"term": "cost_model", "value": cost_model},
                                {"term": "simulated_time_ns", "value": timesteps * timestep_fs}]),
        assumptions=[
            "本专题使用声明的成本模型，不是实测基准：FF 为近邻对线性模型，MLFF 为逐原子推理 FLOPs 模型，DFT 为 O(N^3) SCF 模型。",
            f"FF 模型取每原子 {COST_MODELS['md-ff']['neighbor_pairs_per_atom']} 近邻对、每对 {COST_MODELS['md-ff']['flops_per_pair']} FLOPs、每 {COST_MODELS['md-ff']['neighbor_rebuild_interval']} 步重建近邻表；这些常数是建模输入。",
            f"MLFF 模型取每原子每步 {COST_MODELS['md-mlff']['mlff_flops_per_atom']:,} FLOPs；它随原子数线性增长，不含训练与模型加载。",
            f"DFT 模型取 {COST_MODELS['dft']['scf_iterations']} 次 SCF、每次 {COST_MODELS['dft']['flops_per_atom_cubed']:,} FLOPs/原子^3；立方标度在中等体系即会主导。",
            "设备峰值取自公开数据表（BF16 张量核心稠密峰值，DFT 用 FP32 向量峰值），未做精度、稀疏或实测标定；效率是声明的理想利用率，不是 MFU 测量。",
            "gpu_hours = 总 FLOPs / (峰值 × 效率) / 3600；wall_clock_hours = gpu_hours / gpus，假设理想并行与无通信开销。",
            "energy_kwh 用设备 TDP × gpu_hours 估算，不含冷却、供电损耗与空闲；TDP 不是实测功耗。",
            "timestep_fs 与 simulated_time_ns 仅用于说明物理时长，不参与 FLOPs 折算。",
        ])
