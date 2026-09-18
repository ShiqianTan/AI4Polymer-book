#!/usr/bin/env python3
"""Build chapter-ten teaching figures from fixed book evidence.

Usage: python manuscripts/ch10/build.py [--font /path/to/CJK-font.ttf]
"""
from pathlib import Path
import argparse
import hashlib
import json
import math
import random
import sys

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE.parent))

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

RANDOM_SPACE = json.loads(
    (ROOT / 'calculations/results/chemical-space-random.json').read_text())
BLOCK_SPACE = json.loads(
    (ROOT / 'calculations/results/chemical-space-block.json').read_text())
PARETO = json.loads(
    (ROOT / 'calculations/results/pareto-screen-block.json').read_text())
ROBUST = json.loads(
    (ROOT / 'calculations/results/robust-ranking-tg.json').read_text())


def figure_inverse_design_loop(exp):
    fig, ax = canvas(height=4.4)
    items = [
        ('目标与约束', '定义可行域'),
        ('候选生成', ''),
        ('性质预测', ''),
        ('筛选', '逐级过滤'),
        ('合成验证', ''),
        ('数据回流', ''),
    ]
    D.cycle(ax, items, center=(0.46, 0.50), rx=0.30, ry=0.30,
            w=0.20, h=0.11, color='blue', size=11)
    box(ax, 0.62, 0.595, 0.20, 0.11, '候选生成', 'orange', size=11)
    box(ax, 0.78, 0.74, 0.18, 0.11, '生成式', 'green', size=11)
    box(ax, 0.78, 0.44, 0.18, 0.11, '优化式', 'green', size=11)
    arrow(ax, (0.78, 0.80), (0.80, 0.705))
    arrow(ax, (0.78, 0.50), (0.80, 0.595))
    exp.save(fig, 'figure-10-1-inverse-design-loop', badge='SCHEMATIC')


def figure_pareto_front(exp):
    rng = random.Random(20260916)
    front = []
    for i in range(12):
        x = 0.14 + 0.72 * i / 11
        front.append((x, 0.90 - 0.70 * (x / 0.86) ** 1.9))
    cloud = list(front)
    for _ in range(34):
        x = rng.uniform(0.12, 0.86)
        y = 0.90 - 0.70 * (x / 0.86) ** 1.9 - rng.uniform(0.05, 0.42)
        cloud.append((x, y))

    def dominates(a, b):
        return (a[0] >= b[0] and a[1] >= b[1]
                and (a[0] > b[0] or a[1] > b[1]))

    nondom = [p for p in cloud if not any(dominates(q, p)
                                          for q in cloud if q != p)]
    nondom.sort()
    dominated = [p for p in cloud if p not in nondom]

    fig, ax = plot(height=3.8, left=.17, bottom=.19)
    ax.scatter([p[0] for p in dominated], [p[1] for p in dominated],
               s=22, facecolor=COL['blue'], edgecolor=COL['line'],
               linewidth=.6, zorder=2, label='可行样本（被支配）')
    ax.plot([p[0] for p in nondom], [p[1] for p in nondom],
            color=COL['line'], lw=1.4, zorder=3)
    ax.scatter([p[0] for p in nondom], [p[1] for p in nondom],
               s=48, marker='s', facecolor=COL['orange'], edgecolor=COL['line'],
               linewidth=.8, zorder=4, label='Pareto 前沿')
    a, b = nondom[0], nondom[-1]
    distances = []
    for p in nondom:
        num = abs((b[1] - a[1]) * p[0] - (b[0] - a[0]) * p[1]
                  + b[0] * a[1] - b[1] * a[0])
        den = ((b[1] - a[1]) ** 2 + (b[0] - a[0]) ** 2) ** 0.5
        distances.append(num / den)
    knee = nondom[distances.index(max(distances))]
    ax.annotate('端点', xy=a, xytext=(a[0] - 0.02, a[1] + 0.07), size=11,
                ha='center', arrowprops=dict(arrowstyle='-', color=COL['line'],
                                             lw=.8))
    ax.annotate('端点', xy=b, xytext=(b[0] + 0.02, b[1] - 0.07), size=11,
                ha='center', arrowprops=dict(arrowstyle='-', color=COL['line'],
                                             lw=.8))
    ax.annotate('膝点', xy=knee, xytext=(knee[0] - 0.02, knee[1] + 0.16),
                size=11, ha='center',
                arrowprops=dict(arrowstyle='-', color=COL['line'], lw=.8))
    worst = min(dominated, key=lambda p: abs(p[0] - 0.45))
    ax.annotate('被支配点', xy=worst, xytext=(worst[0] - 0.16, worst[1] + 0.07),
                size=11, ha='center',
                arrowprops=dict(arrowstyle='-', color=COL['line'], lw=.8))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_xlabel('目标 1（越大越好）')
    ax.set_ylabel('目标 2（越大越好）')
    ax.legend(loc='upper right', frameon=False)
    ax.text(0.02, 0.04, '示意数据，非实测', size=11)
    exp.save(fig, 'figure-10-2-pareto-front', badge='SCHEMATIC')


def figure_screening_funnel(exp):
    fig, ax = canvas(height=4.2)
    stages = [
        ('有效性解析', ''),
        ('可合成性过滤', ''),
        ('性质预测与不确定度', ''),
        ('加工与稳定性', ''),
        ('成本估算', ''),
    ]
    D.funnel(ax, stages, cx=0.28, w_top=0.44, y_top=0.92, h=0.13,
             gap=0.02, shrink=0.15, size=11)
    text(ax, 0.28, 0.965, '初始候选', size=11, ha='center')
    text(ax, 0.28, 0.155, '进入合成验证', size=11, ha='center')
    rf = RANDOM_SPACE['summary']['synthesizable_fraction']
    bf = BLOCK_SPACE['summary']['synthesizable_fraction']
    mantissa, exponent = f'{rf:.1e}'.split('e')
    random_label = f'${mantissa}\\times10^{{{int(exponent)}}}$'
    notes = [
        [('通过率：0.90（示意）', 0.035), ('代价：低', -0.035)],
        [('通过率 block 1.00', 0.055), (f'random ≈ {random_label}', 0.005),
         ('代价：低', -0.055)],
        [('通过率：0.30（示意）', 0.035), ('代价：中', -0.035)],
        [('通过率：0.50（示意）', 0.035), ('代价：中', -0.035)],
        [('通过率：0.60（示意）', 0.035), ('代价：高', -0.035)],
    ]
    for i, rows in enumerate(notes):
        y = 0.92 - i * 0.15 - 0.065
        for label, dy in rows:
            text(ax, 0.52, y + dy, label, size=11)
    text(ax, 0.02, 0.055, '可行性通过率来自 chemical-space-block/random.json；',
         size=11)
    text(ax, 0.02, 0.005, '其余通过率与代价为示意值。', size=11)
    exp.save(fig, 'figure-10-3-screening-funnel', badge='SCHEMATIC')


def figure_search_strategies(exp):
    fig, ax = canvas(height=4.6)
    text(ax, 0.5, 0.965, '六类搜索策略：适用条件、代价与失效模式',
         size=12, ha='center', weight='bold')
    items = [
        ('枚举 enumeration', 'blue',
         '适用：小规模离散空间\n代价：线性于空间规模\n失效：空间不可枚举'),
        ('进化搜索 evolutionary', 'green',
         '适用：离散结构、梯度不可得\n代价：每代多次评估\n失效：早熟、多样性丧失'),
        ('潜空间搜索 latent space', 'green',
         '适用：已有连续编码器\n代价：解码加评估\n失效：解码误差、分布外'),
        ('条件生成 conditional', 'orange',
         '适用：有性质条件数据\n代价：采样加筛选\n失效：条件满足率低'),
        ('贝叶斯优化 BO', 'orange',
         '适用：评估昂贵、维度低\n代价：序贯、代理重训\n失效：高维、批量受限'),
        ('强化学习 RL', 'purple',
         '适用：序列决策、奖励可算\n代价：奖励设计、训练\n失效：奖励黑客、样本低效'),
    ]
    cols = [0.03, 0.51]
    rows = [0.78, 0.51, 0.24]
    for index, (label, color, note) in enumerate(items):
        x = cols[index % 2]
        y = rows[index // 2]
        box(ax, x, y, 0.46, 0.085, label, color, size=11)
        text(ax, x, y - 0.075, note, size=11)
    exp.save(fig, 'figure-10-4-search-strategies', badge='SCHEMATIC')


def figure_scalarization(exp):
    front = PARETO['summary']['front']
    dominated = PARETO['summary']['dominated']
    weighted = PARETO['summary']['weighted_sum_optimal']
    epsilon = PARETO['summary']['epsilon_constraint_optimal']
    fig, ax = plot(height=3.9, left=.16, bottom=.19)
    ax.scatter([p[0] for p in dominated], [p[1] for p in dominated], s=18,
               facecolor=COL['gray'], edgecolor=COL['line'], linewidth=.4,
               zorder=2, label='被支配点')
    ax.plot([p[0] for p in front], [p[1] for p in front],
            color=COL['line'], lw=1.2, zorder=3)
    ax.scatter([p[0] for p in front], [p[1] for p in front], s=16,
               facecolor=COL['blue'], edgecolor=COL['line'], linewidth=.4,
               zorder=4, label='Pareto 前沿')
    ax.scatter([p[0] for p in weighted], [p[1] for p in weighted], s=95,
               marker='s', facecolor=COL['orange'], edgecolor=COL['line'],
               linewidth=.9, zorder=5, label='加权和最优点（5 个）')
    ax.scatter([p[0] for p in epsilon], [p[1] for p in epsilon], s=70,
               marker='^', facecolor=COL['green'], edgecolor=COL['line'],
               linewidth=.9, zorder=6, label='ε-约束最优点（20 个）')
    ax.set_xlabel('选择性代理（越大越好）')
    ax.set_ylabel('渗透率代理（越大越好）')
    ax.set_xlim(0.28, 1.0)
    ax.set_ylim(0.2, 1.05)
    ax.legend(loc='lower left', frameon=False)
    ax.set_title('标量化方法对非凸前沿的覆盖')
    exp.save(fig, 'figure-10-5-scalarization', badge='CALC')


def figure_robust_design(exp):
    rows = ROBUST['summary']['candidates']
    colors = {'C1': 'orange', 'C2': 'blue'}
    fig, ax = plot(height=3.8, left=.14, bottom=.19)
    x = np.linspace(150, 260, 400)
    for row in rows:
        sigma = row['half_width']
        density = np.exp(-0.5 * ((x - row['mean']) / sigma) ** 2) / (sigma * np.sqrt(2 * np.pi))
        style = '-' if row['candidate'] == 'C1' else '--'
        ax.plot(x, density, color=COL[colors[row['candidate']]], lw=1.8,
                linestyle=style, zorder=3,
                label=f"{row['candidate']}：205 ± {row['half_width']:.0f} ℃"
                      f"（窗内 {row['probability_in_window'] * 100:.0f}%）")
        ax.axvline(row['lower_bound'], color=COL[colors[row['candidate']]],
                   lw=1, ls=':', zorder=2)
    ax.axvspan(200, 210, color=COL['gray'], zorder=0)
    ax.set_xlabel('玻璃化转变温度（℃）')
    ax.set_ylabel('概率密度（示意）')
    ax.set_xlim(150, 260)
    ax.set_title('均值相同、区间不同的设计价值')
    ax.legend(loc='upper left', frameon=False)
    ax.text(205, 0.006, '规范窗 200–210 ℃', size=11, ha='center')
    exp.save(fig, 'figure-10-6-robust-design', badge='CALC')


def figure_evaluation_metrics(exp):
    fig, ax = canvas(height=3.9)
    text(ax, 0.5, 0.94, '设计流程的五个评估指标', size=13, ha='center', weight='bold')
    headers = ['指标', '定义', '计算']
    rows = [
        ('命中率', '满足目标区间的比例', 'hits / N'),
        ('多样性', '候选间的结构差异', '平均距离'),
        ('新颖性', '不在训练集的比例', 'novel / N'),
        ('可达性', '落在可行域的比例', 'feasible / N'),
        ('超体积提升', '前沿覆盖的增量', 'HV(S∪新) − HV(S)'),
    ]
    D.table(ax, headers, rows, y_top=0.82, row_h=0.115,
            col_x=[0.16, 0.50, 0.82])
    text(ax, 0.04, 0.06, '五个指标一起报告；只看命中率会奖励同质候选。', size=11)
    exp.save(fig, 'figure-10-7-evaluation-metrics', badge='SCHEMATIC')


def figure_worked_space(exp):
    labels = ['无规空间（全部）', '无规空间（1:1 组成）', '无规空间（规则式可合成）',
              '嵌段空间（全部）', '嵌段空间（可合成）']
    values = [RANDOM_SPACE['summary']['sequence_count'],
              RANDOM_SPACE['summary']['composition_constrained_sequence_count'],
              RANDOM_SPACE['summary']['synthesizable_count'],
              BLOCK_SPACE['summary']['sequence_count'],
              BLOCK_SPACE['summary']['synthesizable_count']]
    shown = ['$10^{100}$', '$1.0\\times10^{29}$', '$5.7\\times10^{31}$',
             '8910', '8910']
    colors = [COL['purple'], COL['orange'], COL['blue'], COL['green'], COL['green']]
    logs = [math.log10(value) for value in values]
    fig, ax = plot(height=3.9, left=.34, bottom=.20)
    ypos = list(range(len(labels)))[::-1]
    ax.barh(ypos, logs, color=colors, edgecolor=COL['line'], linewidth=.9, zorder=2)
    ax.set_yticks(ypos)
    ax.set_yticklabels(labels)
    ax.set_xlim(0, 112)
    ax.set_xlabel('候选数的常用对数 $\\log_{10}N$')
    for y, log_value, label in zip(ypos, logs, shown):
        if log_value > 20:
            ax.text(log_value - 1.5, y, label, size=11, ha='right', va='center')
        else:
            ax.text(log_value + 1.5, y, label, size=11, ha='left', va='center')
    exp.save(fig, 'figure-10-8-worked-space', badge='CALC')


def figure_worked_pareto(exp):
    front = PARETO['summary']['front']
    dominated = PARETO['summary']['dominated']
    knee = (PARETO['summary']['knee_selectivity'], PARETO['summary']['knee_permeability'])
    hv = PARETO['summary']['hypervolume']
    fig, ax = plot(height=3.9, left=.16, bottom=.19)
    xs = [0.0] + [p[0] for p in front]
    ys = [front[0][1]] + [p[1] for p in front]
    ax.fill_between(xs, 0.0, ys, step='post', color=COL['blue'], alpha=.35, zorder=1)
    ax.scatter([p[0] for p in dominated], [p[1] for p in dominated], s=16,
               facecolor=COL['gray'], edgecolor=COL['line'], linewidth=.4,
               zorder=2, label='被支配目标点')
    ax.plot([p[0] for p in front], [p[1] for p in front],
            color=COL['line'], lw=1.2, zorder=3)
    ax.scatter([p[0] for p in front], [p[1] for p in front], s=18,
               facecolor=COL['green'], edgecolor=COL['line'], linewidth=.4,
               zorder=4, label='Pareto 前沿（80 点）')
    ax.scatter([knee[0]], [knee[1]], s=95, marker='s', facecolor=COL['orange'],
               edgecolor=COL['line'], linewidth=.9, zorder=5, label='膝点')
    ax.annotate('超体积 0.700（阴影面积）', xy=(0.50, 0.30), xytext=(0.50, 0.30),
                size=11, ha='center')
    ax.set_xlabel('选择性代理（越大越好）')
    ax.set_ylabel('渗透率代理（越大越好）')
    ax.set_xlim(0.28, 1.0)
    ax.set_ylim(0.2, 1.05)
    ax.legend(loc='lower left', frameon=False)
    ax.set_title(f'8910 个候选的筛选结果：{hv:.3f} 超体积')
    exp.save(fig, 'figure-10-9-worked-pareto', badge='CALC')


def main():
    exp = Exporter(HERE)
    figure_inverse_design_loop(exp)
    figure_pareto_front(exp)
    figure_screening_funnel(exp)
    figure_search_strategies(exp)
    figure_scalarization(exp)
    figure_robust_design(exp)
    figure_evaluation_metrics(exp)
    figure_worked_space(exp)
    figure_worked_pareto(exp)
    exp.finish()
    index = [
        {'figure': '10-1', 'asset': 'ch10/figure-10-1-inverse-design-loop.svg'},
        {'figure': '10-2', 'asset': 'ch10/figure-10-2-pareto-front.svg'},
        {'figure': '10-3', 'asset': 'ch10/figure-10-3-screening-funnel.svg'},
        {'figure': '10-4', 'asset': 'ch10/figure-10-4-search-strategies.svg'},
        {'figure': '10-5', 'asset': 'ch10/figure-10-5-scalarization.svg'},
        {'figure': '10-6', 'asset': 'ch10/figure-10-6-robust-design.svg'},
        {'figure': '10-7', 'asset': 'ch10/figure-10-7-evaluation-metrics.svg'},
        {'figure': '10-8', 'asset': 'ch10/figure-10-8-worked-space.svg'},
        {'figure': '10-9', 'asset': 'ch10/figure-10-9-worked-pareto.svg'},
    ]
    (HERE / 'figure-index.json').write_text(
        json.dumps(index, ensure_ascii=False, indent=2) + '\n')
    for record in exp.checks:
        print(f"{record['figure']}: min label {record['min_label_pt']:.0f} pt, "
              f"{len(record['text_extent_warnings'])} warnings")


if __name__ == '__main__':
    main()
