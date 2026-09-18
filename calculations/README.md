# AI4Polymer 全书量化计算项目

本项目把《AI4Polymer：人工智能驱动的高分子材料设计》中出现的定量推导实现为可读、可复现的 Python 代码，遵循全书方法论：**从约束推导设计——书中的每一个数字都必须来自可复现、仅用标准库的计算工具**。

先看[全书计划与 checklist](PLAN.md)，再看[已生成结果](results/README.md)。本工具离线运行，只需要 Python 3.10+ 标准库，不需要 GPU、RDKit、NumPy 或 pandas。所有输入都是**声明式建模输入**，不是实测；公式单元测试不能代替真实实验证据。

## 直接复现

在书仓库根目录执行：

```bash
python3 calculations/calc.py models
python3 calculations/calc.py verify-sources
python3 calculations/calc.py reproduce
python3 -m unittest discover -s calculations/tests -v
```

也可以在 `calculations/` 下创建虚拟环境后执行 `python -m pip install -e .`，使用 `ai4polymer-calc` 命令。`[plot]` 可选依赖仅用于后续绘图，核心计算不依赖它。

## 结果契约

每个专题的 `calculate(...)` 返回且只返回这些顶层键：

```json
{
  "schema_version": 1,
  "calculation": "专题名",
  "model": "模型标识",
  "scenario": {"...": "输入"},
  "sources": [{"id": "...", "title": "...", "url": "...", "accessed": "..."}],
  "summary": {"...": "全部数值结果"},
  "assumptions": ["中文边界声明", "..."]
}
```

只有在确实选择硬件峰值时才附加 `selected_peak`。所有 JSON 都以 `allow_nan=False` 写出，整数（包括任意精度大整数）保持精确。

## 八个专题

### 1. `descriptor-budget` — 表示维度与碰撞预算

对给定表示计算特征维度、每分子字节数、两两比较成本，以及候选库在折叠指纹上的生日碰撞期望。

```bash
python3 calculations/calc.py descriptor-budget --representation morgan --n-bits 2048 --radius 2 --library-size 1000000 --format md
python3 calculations/calc.py descriptor-budget --representation mordred
python3 calculations/calc.py descriptor-budget --representation graph --atoms 100 --bonds 105
python3 calculations/calc.py descriptor-budget --representation psmiles --atoms 100 --bonds 105
```

要点：ECFP4 等价于 Morgan 半径 2、2048 位；期望碰撞对数 = C(M,2)/2^n_bits，碰撞概率 = 1−exp(−期望碰撞对数)。

### 2. `chemical-space` — 共聚物序列空间规模

用精确大整数计算序列数、规则式可合成比例，并与已知数据集比较。

```bash
python3 calculations/calc.py chemical-space --monomers 10 --chain-length 100 --copolymer random
python3 calculations/calc.py chemical-space --monomers 10 --chain-length 100 --copolymer block
python3 calculations/calc.py chemical-space --monomers 2 --chain-length 50 --copolymer alternating
python3 calculations/calc.py chemical-space --monomers 10 --chain-length 100 --copolymer random --stoichiometry 1,1
```

计数公式：均聚物 = N；无规 = N^L；交替 = N(N−1)；嵌段 = N(N−1)(L−1)。规则式可合成库把链上不同单体种类限制为至多 `max_distinct_monomers` 种。

### 3. `md-cost` — MD/DFT 成本模型

把声明的成本模型折算为 GPU 小时与能耗，设备峰值来自 `configs/devices.json`。

```bash
python3 calculations/calc.py md-cost --method md-ff --atoms 5000 --timesteps 1000000
python3 calculations/calc.py md-cost --method md-mlff --atoms 5000 --timesteps 1000000
python3 calculations/calc.py md-cost --method dft --atoms 500 --timesteps 1 --device a100-80gb-sxm
```

要点：FF 为近邻对线性模型、MLFF 为逐原子推理 FLOPs 模型、DFT 为 O(N³) SCF 模型；这些是声明模型，不是基准测量。

### 4. `gnn-forward` — GNN 参数量与前向 FLOPs

```bash
python3 calculations/calc.py gnn-forward --layers 4 --hidden 256 --atoms 100 --bonds 105 --edge-features 32 --heads 8 --readout attention
python3 calculations/calc.py gnn-forward --readout sum
python3 calculations/calc.py gnn-forward --layers 6 --hidden 512 --format md
```

要点：`total_flops = message_passing_flops + readout_flops + mlp_head_flops`，逐项推导保存在 `summary.terms`；同时给出同层数、同宽度的 Transformer 基线。

### 5. `learning-curve` — 数据需求反解

对幂律 `MAE(n) = MAE_inf + A·n^(−alpha)` 反解达到目标所需训练规模，并给出收紧目标时的边际数据。

```bash
python3 calculations/calc.py learning-curve --mae-inf 0.05 --a 1.0 --alpha 0.5 --target-mae 0.2 --n-max 100000 --strict-mae 0.1
python3 calculations/calc.py learning-curve --target-mae 0.08 --strict-mae 0.06 --format md
```

要点：曲线参数是声明输入，除非场景文件显式提供拟合值，否则不是拟合测量。

### 6. `closed-loop` — 闭环发现样本效率

```bash
python3 calculations/calc.py closed-loop --space-size 1000000 --top-fraction 0.001 --bo-speedup 5 --experiments-per-day 50
python3 calculations/calc.py closed-loop --top-fraction 0.01 --bo-speedup 10 --format md
```

要点：随机搜索首次命中服从几何分布，期望 = 1/p；贝叶斯优化实验数 = 随机期望 / 声明的 `bo_speedup`。

### 7. `pareto-screen` — 两嵌段设计空间的枚举与 Pareto 筛选

```bash
python3 calculations/calc.py pareto-screen --monomers 10 --chain-length 100 --format md
python3 calculations/calc.py pareto-screen --weight-steps 21 --epsilon-steps 41
```

要点：候选集为精确组合数 N(N-1)(L-1)；两个目标为声明代理模型，前沿、超体积与标量化覆盖在这些声明目标上精确计算。`--reference` 指定超体积参考点。

### 8. `robust-ranking` — 均值加区间的候选排序

```bash
python3 calculations/calc.py robust-ranking --means 205 205 --half-widths 20 3 --spec-low 200 --spec-high 210
```

要点：区间半宽按一倍标准差处理，规范窗内概率由正态分布尾部差计算；排序准则为下界（均值减半宽），均值并列时由下界决定翻转。

### 9. `polymerization` — 聚合动力学与共聚序列

```bash
python3 calculations/calc.py polymerization --step-conversions 0.9,0.99,0.999 --living-ratios 50,100,200
python3 calculations/calc.py polymerization --copolymer-pairs "0.1:0.1;1:1;10:0.1" --feed-fraction 0.5
python3 calculations/calc.py polymerization --flory-conversion 0.99 --poisson-mean-dp 100 --format md
```

要点：逐步聚合 $\bar X_n=1/(1-p)$、$\bar X_w=(1+p)/(1-p)$、分散度 $1+p$；活性聚合 Poisson 分布 $\bar X_n=\nu+1$、分散度趋近 1；Mayo-Lewis 瞬时组成与组成漂移按 $\mathrm df_1/\mathrm dp=(f_1-F_1)/(1-p)$ 积分。

### 10. `synthesis-route` — 逆合成搜索与路线可行性

```bash
python3 calculations/calc.py synthesis-route --branching 50 --depth 5 --beam 10
python3 calculations/calc.py synthesis-route --step-yield 0.8 --target-yield 0.3 --initial-candidates 8910
python3 calculations/calc.py synthesis-route --feasibility 0.6 --route-length-pass 0.6 --yield-pass 0.5 --cost-pass 0.4 --format md
```

要点：穷举节点 $b^d$，束搜索每层保留前 $k$ 个节点；路线总产率 $\bar y^d$，目标总产率反解最大步数；四级漏斗存活数为各通过率之积乘初始候选。

## 管理与复现命令

```bash
python3 calculations/calc.py models          # 列出八个专题及默认输入
python3 calculations/calc.py verify-sources  # 校验 configs 对 sources.lock.json 的引用
python3 calculations/calc.py reproduce       # 重新生成 results/<slug>.{json,md} 与 results/README.md
python3 calculations/calc.py verify-results  # 校验结果与输入哈希仍然一致
```

任意专题都支持 `--format {json,md}` 与 `--output PATH`；读取场景的专题还支持 `--inputs PATH`（JSON 对象，作为 `calculate()` 关键字参数）。

## 目录

- `src/ai4polymer_calc/`：CLI、公共模块与 `topics/` 专题计算。
- `configs/datasets.json`：公开高分子数据集规模元数据；`configs/descriptors.json`：表示规格；`configs/monomers.json`：示意单体库；`configs/devices.json`：设备峰值；`configs/sources.lock.json`：来源锁文件。
- `scenarios/book.json`：固定书稿输入；`results/`：确定性生成的结果。
- `inventory/sources.json`：逐章节来源清单占位；`tests/`：独立参照与契约检查。

## 测试

```bash
python3 -m unittest discover -s calculations/tests -v
```

包含：单位校验、chemical-space 小规模暴力枚举、descriptor-budget 碰撞闭式、closed-loop 几何期望、learning-curve 反解、gnn-forward FLOP 守恒、pareto-screen 小规模暴力前沿、robust-ranking 正态窗概率，以及所有专题的结果契约与 JSON 合法性检查。
