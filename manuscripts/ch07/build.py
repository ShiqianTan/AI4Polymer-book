#!/usr/bin/env python3
"""Build chapter-seven teaching figures from fixed book evidence.

Usage: python manuscripts/ch07/build.py [--font /path/to/CJK-font.ttf]
"""
from pathlib import Path
import argparse
import hashlib
import json
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE.parent))

import numpy as np
from matplotlib.patches import Circle, Polygon, Rectangle

from figure_style import COL, Exporter, arrow, box, canvas, plot, text
from figure_style import diagrams as D

parser = argparse.ArgumentParser()
parser.add_argument('--font')
args = parser.parse_args()

if args.font:
    from matplotlib import font_manager
    import matplotlib.pyplot as plt
    resolved = Path(args.font).expanduser().resolve()
    font_manager.fontManager.addfont(str(resolved))
    family = font_manager.FontProperties(fname=str(resolved)).get_name()
    plt.rcParams['font.sans-serif'] = [family, 'DejaVu Sans']

lock = json.loads((HERE / 'sources.json').read_text())
for row in lock['sources']:
    path = ROOT / row['path']
    actual = hashlib.sha256(path.read_bytes()).hexdigest()
    if actual != row['sha256']:
        raise SystemExit(f'Source changed: {row["path"]}; review before rebuilding.')

curve = json.loads((ROOT / 'calculations/results/learning-curve-target.json').read_text())
gnn = json.loads((ROOT / 'calculations/results/gnn-forward-4layer.json').read_text())


def figure_multitask_architecture(exp):
    fig, ax = canvas(height=3.9)
    heads = ['Tg', '模量', '介电', '溶解度']
    D.tree(ax, '共享编码器', heads, root_xy=(0.5, 0.84), branch_y=0.40,
           w=0.20, h=0.13, root_color='purple', color='blue', size=11)
    for i in range(len(heads)):
        x = 0.05 + 0.90 * (i + 0.5) / len(heads)
        arrow(ax, (x + 0.02, 0.465), (0.52, 0.775), kind='control')
    text(ax, 0.04, 0.68, '实线：数据流', size=11)
    text(ax, 0.04, 0.60, '虚线：梯度回流', size=11)
    exp.save(fig, 'figure-7-1-multitask-architecture', badge='SCHEMATIC')


def figure_transfer_curve(exp):
    rows = curve['summary']['curve']
    ns = np.array([row['n'] for row in rows], dtype=float)
    mae = np.array([row['mae'] for row in rows])
    n = np.logspace(0, 5, 240)
    scratch = 0.05 + 1.0 * n ** -0.5
    frozen = 0.07 + 0.30 * n ** -0.5
    full = 0.05 + 0.50 * n ** -0.5
    cross_n = ((0.50 - 0.30) / (0.07 - 0.05)) ** 2
    cross_mae = 0.07 + 0.30 * cross_n ** -0.5
    fig, ax = plot(height=3.9, left=.15, bottom=.19)
    ax.set_xscale('log')
    ax.plot(n, scratch, color=COL['line'], lw=1.5, ls='-', label='从头训练')
    ax.plot(n, frozen, color=COL['line'], lw=1.5, ls='--', label='冻结编码器')
    ax.plot(n, full, color=COL['line'], lw=1.5, ls='-.', label='全量微调')
    ax.plot(ns, mae, 'o', ms=5, mfc=COL['orange'], mec=COL['line'], zorder=4)
    ax.plot(ns, 0.07 + 0.30 * ns ** -0.5, 'o', ms=5, mfc=COL['blue'],
            mec=COL['line'], zorder=4)
    ax.plot(ns, 0.05 + 0.50 * ns ** -0.5, 'o', ms=5, mfc=COL['green'],
            mec=COL['line'], zorder=4)
    ax.plot([cross_n], [cross_mae], '*', ms=15, mfc=COL['purple'],
            mec=COL['line'], zorder=5)
    ax.annotate(f'交叉点 n≈{cross_n:.0f}', xy=(cross_n, cross_mae),
                xytext=(1500, 0.30), size=11,
                arrowprops=dict(arrowstyle='-', color=COL['line'], lw=.9))
    ax.set_xlim(1, 1e5)
    ax.set_ylim(0, 1.15)
    ax.set_xlabel('下游标注样本量（条，对数）')
    ax.set_ylabel('外推集误差（MAE）')
    ax.legend(loc='upper right')
    exp.save(fig, 'figure-7-2-transfer-curve', badge='CALC')


def figure_constraint(exp):
    fig, ax = plot(height=3.9, left=.15, bottom=.18)
    verts = [(0.20, 0.10), (0.85, 0.12), (1.02, 0.45),
             (0.80, 0.82), (0.35, 0.88), (0.10, 0.50)]
    ax.add_patch(Polygon(verts, closed=True, facecolor=COL['green'],
                         edgecolor=COL['line'], linewidth=1.2, zorder=0))
    text(ax, 0.52, 0.47, '可行域', size=12, ha='center', weight='bold')
    start = (0.10, 0.16)
    paths = [
        ((0.60, 1.02), (1.08, 0.95), '--', 'gray', '无约束拟合'),
        ((0.45, 0.55), (0.93, 0.68), '-.', 'orange', '软约束'),
        ((0.40, 0.45), (0.70, 0.60), '-', 'blue', '硬约束'),
    ]
    for ctrl, end, ls, mfc, label in paths:
        t = np.linspace(0, 1, 120)
        x = (1 - t) ** 2 * start[0] + 2 * (1 - t) * t * ctrl[0] + t ** 2 * end[0]
        y = (1 - t) ** 2 * start[1] + 2 * (1 - t) * t * ctrl[1] + t ** 2 * end[1]
        ax.plot(x, y, color=COL['line'], lw=1.4, ls=ls, zorder=2)
        ax.plot([end[0]], [end[1]], 'o', ms=8, mfc=COL[mfc],
                mec=COL['line'], zorder=3)
    ax.plot([start[0]], [start[1]], 'o', ms=7, mfc=COL['white'],
            mec=COL['line'], zorder=3)
    text(ax, 1.05, 1.00, '无约束拟合', size=11, ha='right')
    text(ax, 1.00, 0.62, '软约束', size=11)
    text(ax, 0.72, 0.53, '硬约束', size=11)
    text(ax, 0.06, 0.12, '起点', size=11)
    text(ax, 0.90, 0.75, '约束边界', size=11, ha='center')
    ax.annotate('软约束略越界', xy=(0.93, 0.68), xytext=(0.62, 0.94), size=11,
                arrowprops=dict(arrowstyle='-', color=COL['line'], lw=.9))
    ax.set_xlim(0, 1.15)
    ax.set_ylim(0, 1.05)
    ax.set_xlabel('输出 y₁')
    ax.set_ylabel('输出 y₂')
    exp.save(fig, 'figure-7-3-constraint', badge='SCHEMATIC')


def figure_property_correlation(exp):
    fig, ax = canvas(height=4.1)
    text(ax, 0.5, 0.945, '性质对与共享结构变量', size=13, ha='center',
         weight='bold')
    text(ax, 0.05, 0.86, '性质对', size=11, weight='bold')
    text(ax, 0.37, 0.86, '共享结构变量', size=11, weight='bold')
    text(ax, 0.66, 0.86, '相关强度（示意）', size=11, weight='bold')
    rows = [
        ('$T_g$ ↔ 模量', '链刚性', 0.65),
        ('模量 ↔ 缠结', '缠结密度', 0.55),
        ('渗透率 ↔ 介电', '自由体积', 0.45),
        ('介电 ↔ 溶解度', '极性', 0.70),
    ]
    for i, (pair, var, rho) in enumerate(rows):
        y = 0.72 - i * 0.155
        box(ax, 0.04, y - 0.055, 0.30, 0.11, pair, 'blue', size=11)
        box(ax, 0.36, y - 0.055, 0.24, 0.11, var, 'green', size=11)
        ax.add_patch(Rectangle((0.65, y - 0.035), 0.28 * rho, 0.07,
                               facecolor=COL['orange'], edgecolor=COL['line'],
                               linewidth=.9))
        text(ax, 0.65 + 0.28 * rho + 0.012, y, f'{rho:.2f}', size=11)
    text(ax, 0.5, 0.05,
         '相关性越高，共享收益越大；负相关或表示要求冲突时转为负迁移。',
         size=11, ha='center')
    exp.save(fig, 'figure-7-4-property-correlation', badge='SCHEMATIC')


def figure_sharing_tradeoff(exp):
    fig, ax = canvas(height=3.9)
    text(ax, 0.5, 0.94, '共享结构的三种取舍', size=13, ha='center',
         weight='bold')
    for name, x in [('硬共享', 0.03), ('软共享', 0.36), ('门控共享', 0.69)]:
        box(ax, x, 0.78, 0.28, 0.08, name, 'purple', size=12)
    box(ax, 0.07, 0.42, 0.20, 0.12, '共享编码器', 'blue', size=11)
    for j, head in enumerate(['头 1', '头 2', '头 3']):
        cx = 0.045 + j * 0.085
        box(ax, cx, 0.17, 0.075, 0.09, head, 'green', size=11)
        arrow(ax, (0.17, 0.42), (cx + 0.0375, 0.26))
    for j in range(3):
        cx = 0.375 + j * 0.088
        box(ax, cx, 0.42, 0.078, 0.12, f'编码 {j + 1}', 'blue', size=11)
        box(ax, cx, 0.17, 0.078, 0.09, f'头 {j + 1}', 'green', size=11)
        arrow(ax, (cx + 0.039, 0.42), (cx + 0.039, 0.26))
    arrow(ax, (0.455, 0.50), (0.535, 0.50), kind='control')
    for j in range(3):
        cx = 0.70 + j * 0.088
        box(ax, cx, 0.42, 0.078, 0.12, f'专家 {j + 1}', 'blue', size=11)
    box(ax, 0.75, 0.64, 0.16, 0.09, '门控', 'orange', size=11)
    for j in range(3):
        arrow(ax, (0.83, 0.64), (0.739 + j * 0.088, 0.54), kind='control')
    text(ax, 0.5, 0.05,
         '硬共享样本效率最高但易冲突；软共享保留差异；门控按任务选专家。',
         size=11, ha='center')
    exp.save(fig, 'figure-7-5-sharing-tradeoff', badge='SCHEMATIC')


def figure_transfer_budget(exp):
    hidden = gnn['scenario']['hidden']
    encoder = gnn['summary']['parameters'] - (hidden * hidden + hidden)
    head = (hidden * hidden + hidden) / encoder * 100
    lora = 2 * 8 / hidden * 100
    adapter = 2 * 64 / hidden * 100
    values = [head, lora, adapter, 100.0]
    names = ['冻结编码器\n（只训头）', 'LoRA\n（r=8）', '适配器\n（b=64）',
             '全量微调']
    colors = ['blue', 'green', 'orange', 'purple']
    fig, ax = plot(height=3.9, left=.30, bottom=.20)
    ypos = list(range(len(names)))[::-1]
    ax.barh(ypos, values, color=[COL[c] for c in colors],
            edgecolor=COL['line'], linewidth=.9)
    ax.set_yticks(ypos)
    ax.set_yticklabels(names)
    ax.set_xlim(0, 118)
    ax.set_xlabel('可训练参数占编码器的比例（%）')
    for yi, value in zip(ypos, values):
        ax.text(value + 2.5, yi, f'{value:.1f}%', size=11, va='center')
    ax.text(0.98, 0.05, '隐藏宽度 256', transform=ax.transAxes, size=11,
            ha='right')
    exp.save(fig, 'figure-7-6-transfer-budget', badge='CALC')


def figure_self_supervised(exp):
    fig, ax = canvas(height=3.3)
    text(ax, 0.5, 0.925, '自监督预训练的三类目标', size=13, ha='center',
         weight='bold')
    for name, x in [('掩码重建', 0.03), ('对比学习', 0.36), ('图增强', 0.69)]:
        box(ax, x, 0.74, 0.28, 0.09, name, 'purple', size=12)
    for j, lab in enumerate(['C', 'C', 'M', 'C', 'O']):
        box(ax, 0.045 + j * 0.053, 0.51, 0.046, 0.09, lab,
            'orange' if lab == 'M' else 'blue', size=11)
    text(ax, 0.16, 0.38, '掩码原子 / 令牌', size=11, ha='center')
    text(ax, 0.16, 0.28, '目标：重建被遮挡部分', size=11, ha='center')
    box(ax, 0.375, 0.51, 0.11, 0.09, '视图 A', 'blue', size=11)
    box(ax, 0.51, 0.51, 0.11, 0.09, '视图 B', 'green', size=11)
    arrow(ax, (0.485, 0.555), (0.51, 0.555))
    text(ax, 0.50, 0.38, '正对拉近 · 负对推远', size=11, ha='center')
    text(ax, 0.50, 0.28, '目标：表示对增强不变', size=11, ha='center')
    ax.add_patch(Circle((0.78, 0.555), 0.028, facecolor=COL['blue'],
                        edgecolor=COL['line'], linewidth=.9))
    ax.add_patch(Circle((0.86, 0.555), 0.028, facecolor=COL['blue'],
                        edgecolor=COL['line'], linewidth=.9))
    ax.add_patch(Circle((0.82, 0.47), 0.028, facecolor=COL['white'],
                        edgecolor=COL['line'], linewidth=.9, linestyle='--'))
    ax.plot([0.78, 0.86], [0.555, 0.555], color=COL['line'], lw=.9)
    ax.plot([0.78, 0.82], [0.555, 0.47], color=COL['line'], lw=.9, ls='--')
    ax.plot([0.86, 0.82], [0.555, 0.47], color=COL['line'], lw=.9, ls='--')
    text(ax, 0.82, 0.38, '删节点 / 扰动边 / 采子图', size=11, ha='center')
    text(ax, 0.82, 0.28, '目标：对结构扰动鲁棒', size=11, ha='center')
    exp.save(fig, 'figure-7-7-self-supervised', badge='SCHEMATIC')


def figure_physics_forms(exp):
    fig, ax = canvas(height=4.0)
    text(ax, 0.5, 0.945, '物理信息的三类实现', size=13, ha='center',
         weight='bold')
    for name, x in [('物理特征（输入）', 0.03), ('物理正则（损失）', 0.36),
                    ('等变结构（网络）', 0.69)]:
        box(ax, x, 0.79, 0.28, 0.08, name, 'purple', size=11)
    box(ax, 0.045, 0.62, 0.26, 0.09, '链刚性 / 自由体积', 'blue', size=11)
    arrow(ax, (0.175, 0.62), (0.175, 0.53))
    box(ax, 0.045, 0.44, 0.26, 0.09, '网络', 'green', size=11)
    text(ax, 0.175, 0.31, '适用：物理量已知且可算', size=11, ha='center')
    text(ax, 0.175, 0.23, '失效：量估不准会引入偏差', size=11, ha='center')
    box(ax, 0.375, 0.62, 0.26, 0.09, '数据损失', 'green', size=11)
    box(ax, 0.375, 0.47, 0.26, 0.09, '方程残差 × λ', 'orange', size=11)
    arrow(ax, (0.505, 0.47), (0.505, 0.40))
    text(ax, 0.505, 0.31, '适用：控制方程已知', size=11, ha='center')
    text(ax, 0.505, 0.23, '失效：λ 过大压过数据', size=11, ha='center')
    box(ax, 0.705, 0.62, 0.26, 0.09, '坐标 / 向量', 'blue', size=11)
    arrow(ax, (0.835, 0.62), (0.835, 0.55))
    box(ax, 0.705, 0.46, 0.26, 0.09, '等变层', 'green', size=11)
    text(ax, 0.835, 0.39, '输出随旋转同步变换', size=11, ha='center')
    text(ax, 0.835, 0.31, '适用：性质有对称群', size=11, ha='center')
    text(ax, 0.835, 0.23, '失效：任务本无对称性', size=11, ha='center')
    text(ax, 0.5, 0.08, '三者可叠加，但应分别声明、分别检验，不都归入 PINN。',
         size=11, ha='center')
    exp.save(fig, 'figure-7-8-physics-forms', badge='SCHEMATIC')


def figure_transfer_failures(exp):
    fig, ax = canvas(height=4.3)
    text(ax, 0.5, 0.955, '借力路径的四类失败模式', size=13, ha='center',
         weight='bold')
    cells = [
        ('负迁移', '共享后目标误差升高', '留出目标，比较单任务', 'orange'),
        ('分布不匹配', '预训练与下游结构不同源', '领域内继续预训练', 'orange'),
        ('约束过强', '训练与验证误差同时升高', '降 λ，改硬约束', 'blue'),
        ('等变浪费', '无对称性任务精度不升', '换普通图网络', 'blue'),
    ]
    x0, y0, w, h, gap = 0.05, 0.10, 0.43, 0.34, 0.04
    for i, (name, signal, fix, color) in enumerate(cells):
        cx = x0 + (i % 2) * (w + gap)
        cy = y0 + (1 - i // 2) * (h + gap)
        ax.add_patch(Rectangle((cx, cy), w, h, facecolor=COL[color],
                               edgecolor=COL['line'], linewidth=.9))
        text(ax, cx + w / 2, cy + h - 0.055, name, size=12, ha='center',
             weight='bold')
        text(ax, cx + w / 2, cy + h / 2, '诊断：' + signal, size=11,
             ha='center')
        text(ax, cx + w / 2, cy + 0.055, '修法：' + fix, size=11, ha='center')
    exp.save(fig, 'figure-7-9-transfer-failures', badge='SCHEMATIC')


def main():
    exp = Exporter(HERE)
    figure_multitask_architecture(exp)
    figure_transfer_curve(exp)
    figure_constraint(exp)
    figure_property_correlation(exp)
    figure_sharing_tradeoff(exp)
    figure_transfer_budget(exp)
    figure_self_supervised(exp)
    figure_physics_forms(exp)
    figure_transfer_failures(exp)
    exp.finish()
    index = [
        {'figure': '7-1', 'asset': 'ch07/figure-7-1-multitask-architecture.svg'},
        {'figure': '7-2', 'asset': 'ch07/figure-7-2-transfer-curve.svg'},
        {'figure': '7-3', 'asset': 'ch07/figure-7-3-constraint.svg'},
        {'figure': '7-4', 'asset': 'ch07/figure-7-4-property-correlation.svg'},
        {'figure': '7-5', 'asset': 'ch07/figure-7-5-sharing-tradeoff.svg'},
        {'figure': '7-6', 'asset': 'ch07/figure-7-6-transfer-budget.svg'},
        {'figure': '7-7', 'asset': 'ch07/figure-7-7-self-supervised.svg'},
        {'figure': '7-8', 'asset': 'ch07/figure-7-8-physics-forms.svg'},
        {'figure': '7-9', 'asset': 'ch07/figure-7-9-transfer-failures.svg'},
    ]
    (HERE / 'figure-index.json').write_text(
        json.dumps(index, ensure_ascii=False, indent=2) + '\n')
    for record in exp.checks:
        print(f"{record['figure']}: min label {record['min_label_pt']:.0f} pt, "
              f"{len(record['text_extent_warnings'])} warnings")


if __name__ == '__main__':
    main()
