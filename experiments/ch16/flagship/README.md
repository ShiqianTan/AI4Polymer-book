# 第 16 章 案例一：高 Tg 透明聚酰亚胺旗舰案例

本目录是第 16 章 16.2 节案例一的可运行实现。它用**真实公开测量数据**跑通一条完整链路：数据清洗 → 按结构分组划分 → 3 个基线 → 主模型 → 学习曲线 → 不确定度 → 枚举候选 → Top 20 → 可合成性过滤 → Top 5 → 与文献实测对照。没有湿实验，但每个数字都由本目录脚本真实产出，未编造。

## 快速开始

```bash
cd experiments/ch16/flagship
python3 run.py
```

运行时间约 2.3 分钟（随机森林设为单线程以保证逐位可复现），结果写入 `results/`。脚本只依赖以下第三方库，缺失时会打印安装提示并退出（不会抛栈崩溃）：

| 依赖 | 本机验证版本 |
| --- | --- |
| Python | 3.11.15 |
| numpy | 2.2.6 |
| RDKit | 2026.03.3 |
| scikit-learn | 1.9.0 |

```bash
pip install numpy rdkit scikit-learn
```

`results/manifest.json` 记录输入与全部输出的 SHA256；固定随机种子 `SEED=42`。

## 数据来源

| 项 | 值 |
| --- | --- |
| 名称 | Polymer Tg prediction dataset（`data/processed/dataset.csv`） |
| 发布方 | chem-data-extraction（课程数据集仓库，聚合自 LamaLab Zenodo 沉积） |
| 原始沉积 | Kunchapu & Jablonka, *Curated Glass Transition Temperature for Polymers*, Zenodo, DOI `10.5281/zenodo.15783761` |
| 下载 URL | `https://raw.githubusercontent.com/chem-data-extraction/polymer-Tg-prediction-dataset/main/data/processed/dataset.csv` |
| 许可 | CC BY 4.0 |
| 检索日期 | 2026-09-17 |
| 总条数 | 7372 |
| 聚酰亚胺子集 | 1765 |
| SHA256 | `c7de4f6e26a321319ada13ed682fd75ea615c72192a2be6a2eef9ccb2df704d0` |

数据为实验测量的玻璃化转变温度（$T_g$），每条含 PSMILES 重复单元、测量方法与来源。聚酰亚胺子集的 $T_g$ 范围 264.15–763.15 K，均值 513.80 K，标准差 79.05 K，中位数 520.15 K；其中 1337 条高于 473.15 K（200 °C）。

## 链路与真实产出

### 1. 数据清洗

- 从 7372 条记录中取出 `polymer_class == polyimide` 的 1765 条。
- $T_g$ 单位统一为 K；范围检查 [100, 900] K。
- PSMILES 用 RDKit 解析，把两个 `[*]` 连成闭环重复单元（与上游表示一致）。
- 结果：1765 条全部保留，0 条丢弃（`results/cleaning_drops.json`）。

### 2. 划分（按结构分组，避免泄漏）

用 Bemis-Murcko 骨架作为分组键做 `GroupShuffleSplit`。1304 个不同骨架，训练 1411 条、测试 354 条，训练/测试骨架重叠为 0。

### 3. 特征与模型

特征为 2048 位 Morgan 指纹（半径 2，RDKit 实算）。测试集结果（单位 K）：

| 模型 | MAE | $R^2$ |
| --- | --- | --- |
| 全局均值基线 | 64.70 | -0.02 |
| Ridge | 30.44 | 0.73 |
| 随机森林 | 30.59 | 0.75 |
| 主模型 HistGradientBoosting | 28.23 | 0.79 |

按骨架分组 5 折交叉验证：主模型 MAE 27.10 ± 1.34 K（均值基线 60.65 K，Ridge 28.70 K，随机森林 28.16 K）。

### 4. 学习曲线（真实拟合）

在训练集内取 20/50/100/200/400/700/1000/1400 条训练，测试集 MAE 从 64.78 K 降到 28.48 K。用幂律 $\mathrm{MAE}(n)=A n^{-\alpha}$ 拟合得 $A=130.2$、$\alpha=0.197$，拟合 $R^2=0.898$。三参数形式（含 $\mathrm{MAE}_\infty$）在本数据范围内退化到 $\mathrm{MAE}_\infty\approx 0$，即数据尚不能分辨渐近下限。据此外推，达到 MAE 30 K 需约 1750 条训练样本，超过现有 1765 条总量。

### 5. 不确定度

用 split conformal 在训练集内留出校准集，取绝对残差分位数：

| 名义覆盖 | 实测覆盖（测试集） | 平均区间宽度 |
| --- | --- | --- |
| 90% | 85.3% | 108.3 K |
| 80% | 70.1% | 72.9 K |

实测覆盖低于名义值，原因是按骨架分组使测试集与训练集不满足可交换性；这正是分组划分的代价，已在正文中标注。

### 6. 候选枚举与筛选

从 12 种二酐 × 26 种二胺（23 种常规 + 3 种含竞争反应基团）枚举 312 个聚酰亚胺重复单元，全部由 RDKit 实算构建成功。筛选漏斗：

| 阶段 | 存活数 |
| --- | --- |
| 枚举 | 312 |
| 构建成功 | 312 |
| 预测 $T_g \ge 473.15$ K | 305 |
| 透明性代理通过 | 105 |
| 可合成性通过 | 74 |
| Top 20 → Top 5 | 20 → 5 |

### 7. Top 5 候选

| 排名 | 二酐 | 二胺 | 预测 $T_g$ (K) | 预测 $T_g$ (°C) | 透明风险 | 训练集最大 Tanimoto | 是否新结构 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | PMDA | 6FpDA | 649.9 | 376.8 | -1 | 1.00 | 否 |
| 2 | 6FDA | DMB | 646.9 | 373.8 | 0 | 0.82 | 是 |
| 3 | 6FDA | TMB | 638.0 | 364.9 | 0 | 0.78 | 是 |
| 4 | PMDA | ABTFMB | 636.5 | 363.4 | +1 | 0.63 | 是 |
| 5 | PMDA | TFMB | 633.2 | 360.1 | -1 | 1.00 | 否 |

新结构短名单（训练集最大 Tanimoto < 0.99）：6FDA-DMB、6FDA-TMB、PMDA-ABTFMB、DSDA-6FpDA、CBDA-TMB。完整候选见 `results/candidates.csv`，Top 20 见 `results/top20.csv`。

### 8. 与文献实测对照

用 Ren et al. 2023（*Polymers* 15(17):3549, DOI `10.3390/polym15173549`）报告的 3 个 6FDA 基聚酰亚胺实测 $T_g$（DMA）做样本外验证：

| 结构 | 文献实测 (K) | 模型预测 (K) | 误差 (K) | 90% 区间是否覆盖 |
| --- | --- | --- | --- | --- |
| PI-ref1 (6FDA-FDAADA) | 674.5 | 609.6 | -64.8 | 否 |
| PI-ref2 (6FDA-ABTFMB) | 649.5 | 589.6 | -59.8 | 否 |
| PI-ref3 (6FDA-MABTFMB) | 654.6 | 570.7 | -83.8 | 否 |

模型对这三个含酰胺桥的二胺结构**系统性低估**约 60–84 K，且全部落在 conformal 区间之外。训练集最大 Tanimoto 仅 0.80–0.81，属分布外外推。这与第 16 章「外推失效」失败模式一致：在域内测试 MAE 28 K，但迁移到未见过的酰胺桥单体时误差翻倍且单向偏。**未做分子模拟验证**（无算力预算），该项在正文中如实标注为未进行。

## 哪些环节是真实计算，哪些无法进行

| 环节 | 状态 | 说明 |
| --- | --- | --- |
| $T_g$ 数据与模型 | 真实 | 公开实测数据 + RDKit/sklearn 实算 |
| 划分与泄漏检查 | 真实 | 骨架分组，重叠 0 |
| 学习曲线 | 真实拟合 | 幂律参数由本数据拟合 |
| 不确定度 | 真实 | split conformal |
| 候选枚举 | 真实 | 单体库 + RDKit 缩合构建 |
| 可合成性过滤 | 规则式 | 单体可得性、竞争基团、SA 分数 |
| **透明性** | **无标注数据** | 数据集中没有透过率标签，改用文献动机的结构代理 `ct_risk`（芳环数、稠合、CF3、脂环、砜），阈值 `ct_risk <= 1`；这是启发式，不是训练出来的透明性模型 |
| 湿实验 | 未做 | 本案例不含合成与表征 |
| 分子模拟 | 未做 | 未运行 MD/DFT |

### 失败记录（见 `results/failures.json`）

- **构建失败 0 个**：312 个候选全部构建成功。
- **$T_g$ 不达标 7 个**：含柔性脂环/醚链的候选预测 $T_g$ 低于 473.15 K。
- **透明性不达标 200 个**：PMDA/BPDA/ODPA/BTDA 与富电子二胺组合的 `ct_risk` 高，例如 PMDA-ODA（Kapton 型）+3、BPDA-PDA +3。
- **可合成性不达标 31 个**：含游离羧基、羟基、二硫键的二胺（竞争反应基团）被剔除；另有整类二酐因通用 SA 分数 > 4.5 被误杀，包括文献已商业化的脂环二酐 BCDA（SA 5.08）。这是规则式过滤器的已知假阳性，正文中作为「规则过滤误伤」记录。

## 目录结构

```
experiments/ch16/flagship/
├── run.py                     # 主入口
├── README.md                  # 本文件
├── data/
│   └── polymer-tg-dataset.csv # 真实数据（CC BY 4.0）
└── results/
    ├── summary.json           # 全部指标与 Top 列表
    ├── candidates.csv         # 312 个候选的打分
    ├── top20.csv / top5.csv   # 漏斗输出
    ├── failures.json          # 各阶段失败候选
    ├── cleaning_drops.json    # 清洗丢弃记录
    └── manifest.json          # 输入/输出 SHA256
```

## 复现

```bash
python3 run.py
```

固定种子 42；所有随机森林均为单线程，输出可逐字节复现（连续两次运行的 `results/manifest.json` 完全一致）。
