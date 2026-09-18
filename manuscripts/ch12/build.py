#!/usr/bin/env python3
"""Build chapter-twelve teaching figures from fixed book evidence.

Usage: python manuscripts/ch12/build.py [--font /path/to/CJK-font.ttf]
"""
from pathlib import Path
import argparse
import hashlib
import json
import math
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE.parent))

import matplotlib.pyplot as plt
import numpy as np

from figure_style import COL, Exporter, arrow, box, canvas, plot, text
from figure_style import diagrams as D

parser = argparse.ArgumentParser()
parser.add_argument('--font')
args = parser.parse_args()

if args.font:
    from matplotlib import font_manager
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

SPACE = json.loads(
    (ROOT / 'calculations/results/chemical-space-random.json').read_text())['summary']
BLOCK_SPACE = json.loads(
    (ROOT / 'calculations/results/chemical-space-block.json').read_text())['summary']
POLY = json.loads(
    (ROOT / 'calculations/results/polymerization-kinetics.json').read_text())
ROUTE = json.loads(
    (ROOT / 'calculations/results/synthesis-route-block.json').read_text())


def panels(height=3.8, left=.11, right=.95, bottom=.17, top=.93, hspace=0.42):
    fig, axes = plt.subplots(1, 2, figsize=(420 / 72, height))
    fig.subplots_adjust(left=left, right=right, bottom=bottom, top=top,
                        wspace=0.30)
    for ax in axes:
        ax.spines[['top', 'right']].set_visible(False)
    return fig, axes


def figure_reaction_network(exp):
    fig, ax = canvas(height=4.2)
    nodes = {
        'm1': (0.11, 0.28, '单体 A', 'green'),
        'm2': (0.11, 0.80, '单体 B', 'green'),
        'i1': (0.40, 0.54, '中间体 1', 'gray'),
        'i2': (0.65, 0.54, '中间体 2', 'gray'),
        'p': (0.88, 0.54, '目标聚合物', 'orange'),
    }
    edges = [('m1', 'i1'), ('m2', 'i1'), ('i1', 'i2'), ('i2', 'p')]
    D.graph(ax, nodes, edges, w=0.20, h=0.12, size=12)
    text(ax, 0.24, 0.42, '偶联', size=11, ha='center')
    text(ax, 0.28, 0.71, '缩聚', size=11, ha='center')
    text(ax, 0.525, 0.63, '偶联', size=11, ha='center')
    text(ax, 0.765, 0.63, '开环聚合', size=11, ha='center')
    ax.plot([0.88, 0.88], [0.48, 0.10], color=COL['line'], lw=1, ls='--')
    ax.plot([0.11, 0.88], [0.10, 0.10], color=COL['line'], lw=1, ls='--')
    arrow(ax, (0.11, 0.10), (0.11, 0.22), kind='control')
    text(ax, 0.52, 0.15, '逆向路径：3 步（合成步数）→ 可用单体', size=11, ha='center')
    exp.save(fig, 'figure-12-1-reaction-network', badge='SCHEMATIC')


def figure_polymerization(exp):
    fig, (left, right) = panels()
    p = np.linspace(0.01, 0.99, 300)
    left.plot(p, 1 / (1 - p), color=COL['orange'], lw=2.2,
              label='逐步聚合 $\\bar X_n = 1/(1-p)$')
    left.axhline(500, color=COL['green'], lw=2.0, ls='--')
    left.text(0.60, 620, '链式聚合（示意）', size=11, ha='center')
    left.set_yscale('log')
    left.set_xlim(0, 1)
    left.set_ylim(1, 1500)
    left.set_xlabel('转化率 $p$')
    left.set_ylabel('数均聚合度 $\\bar X_n$')
    left.annotate('$p=0.99$，$\\bar X_n=100$', xy=(0.99, 100), xytext=(0.42, 160),
                  size=11, arrowprops=dict(arrowstyle='-', color=COL['line'], lw=.9))
    left.legend(loc='lower right', frameon=False)
    left.text(0.02, 0.92, '(a)', transform=left.transAxes, size=12, weight='bold')

    n = np.arange(1, 11)
    series = [(0.1, COL['green'], '-', '交替倾向 $r=0.1$'),
              (1.0, COL['blue'], '--', '无规 $r=1$'),
              (10.0, COL['orange'], '-.', '嵌段倾向 $r=10$')]
    for r, color, ls, label in series:
        prob = r / (r + 1)
        right.plot(n, prob ** (n - 1) * (1 - prob), color=color, lw=2.0, ls=ls,
                   marker='o', ms=4, label=label)
    right.set_xticks(n)
    right.set_xlim(0.5, 10.5)
    right.set_ylim(0, 1.0)
    right.set_xlabel('序列长度 $n$（单体 1 连续单元数）')
    right.set_ylabel('概率 $P(n)$')
    right.legend(loc='upper right', frameon=False)
    right.text(0.02, 0.92, '(b)', transform=right.transAxes, size=12, weight='bold')
    exp.save(fig, 'figure-12-2-polymerization', badge='SCHEMATIC')


def figure_synthesizability(exp):
    fig, ax = canvas(height=4.3)
    frac = SPACE['synthesizable_fraction']
    stages = [
        ('生成候选', f'理论空间 $10^{{{SPACE["log10_sequence_count"]:.0f}}}$'),
        ('可行性', f'可达比例 {frac:.1e}'),
        ('路线长度', '60%（示意）'),
        ('产率', '50%（示意）'),
        ('成本', '40%（示意）'),
    ]
    D.funnel(ax, stages, cx=0.32, w_top=0.56, y_top=0.85, h=0.135, gap=0.012,
             shrink=0.16)
    text(ax, 0.32, 0.94, '可合成性筛选漏斗', size=13, ha='center', weight='bold')
    text(ax, 0.03, 0.055,
         '可行性级为规则式可达比例（chemical-space-random.json）；\n'
         '路线长度、产率、成本为示意通过率，梯形宽度不代表比例。', size=11)
    exp.save(fig, 'figure-12-3-synthesizability', badge='SCHEMATIC')


def figure_kinetics_regimes(exp):
    fig, ax = canvas(height=4.0)
    text(ax, 0.5, 0.955, '三类聚合机理：链长、分散度与可调变量', size=13,
         ha='center', weight='bold')
    headers = ['机理', '链长与转化率', '分散度', 'AI 可介入变量']
    rows = [
        ('逐步聚合', '$\\bar X_n=1/(1-p)$', '趋近 2', '投料比、除水'),
        ('自由基', '$\\bar X_n\\propto 1/\\sqrt{[I]}$', '1.5–2.5', '引发剂、温度'),
        ('活性/可控', '$\\bar X_n=\\nu+1$', '趋近 1', '催化剂、配体'),
    ]
    D.table(ax, headers, rows, y_top=0.78, row_h=0.155,
            col_x=[0.13, 0.39, 0.62, 0.83], size=11)
    text(ax, 0.04, 0.055,
         '链长关系为声明模型；分散度为文献典型区间。', size=11)
    exp.save(fig, 'figure-12-4-polymerization-regimes', badge='SCHEMATIC')


def _mayo_lewis(f1, r1, r2):
    f2 = 1.0 - f1
    return (r1 * f1 * f1 + f1 * f2) / (r1 * f1 * f1 + 2.0 * f1 * f2 + r2 * f2 * f2)


def figure_copolymerization(exp):
    fig, (left, right) = panels(height=3.8)
    f1 = np.linspace(0.002, 0.998, 300)
    curves = [(0.1, 0.1, COL['green'], '-', '$r_1=r_2=0.1$（交替）'),
              (1.0, 1.0, COL['blue'], '--', '$r_1=r_2=1$（无规）'),
              (10.0, 0.1, COL['orange'], '-.', '$r_1=10,\\ r_2=0.1$（梯度）')]
    left.plot([0, 1], [0, 1], color=COL['line'], lw=1, ls=':', zorder=1)
    for r1, r2, color, ls, label in curves:
        left.plot(f1, _mayo_lewis(f1, r1, r2), color=color, lw=2.0, ls=ls,
                  label=label)
    left.set_xlim(0, 1)
    left.set_ylim(0, 1)
    left.set_xlabel('投料组成 $f_1$')
    left.set_ylabel('瞬时共聚组成 $F_1$')
    left.legend(loc='upper left', frameon=False)
    left.text(0.02, 0.05, '(a)', transform=left.transAxes, size=12, weight='bold')

    for row, color, ls in [(next(r for r in POLY['summary']['copolymer']
                                 if r['r1'] == 10.0), COL['orange'], '-.'),
                           (next(r for r in POLY['summary']['copolymer']
                                 if r['r1'] == 1.0), COL['blue'], '--'),
                           (next(r for r in POLY['summary']['copolymer']
                                 if r['r1'] == 0.1), COL['green'], '-')]:
        drift = row['drift']
        right.plot([p['conversion'] for p in drift],
                   [p['feed_f1'] for p in drift], color=color, lw=2.0, ls=ls,
                   label=f"$r_1={row['r1']:g},\\ r_2={row['r2']:g}$")
    right.set_xlim(0, 1)
    right.set_ylim(0, 1)
    right.set_xlabel('转化率 $p$')
    right.set_ylabel('剩余投料中单体 1 的比例 $f_1$')
    right.legend(loc='center left', frameon=False)
    right.text(0.02, 0.92, '(b)', transform=right.transAxes, size=12, weight='bold')
    exp.save(fig, 'figure-12-5-copolymerization', badge='CALC')


def figure_molecular_weight_distribution(exp):
    flory = POLY['summary']['flory']
    poisson = POLY['summary']['poisson']
    fig, ax = plot(height=3.9, left=.16, bottom=.20)
    ax.semilogy(flory['n'], flory['weight_fraction'], color=COL['orange'],
                lw=2.0, label=f"逐步聚合 Flory（Đ={flory['dispersity']:.2f}）")
    ax.semilogy(poisson['n'], poisson['weight_fraction'], color=COL['blue'],
                lw=2.0, label=f"活性聚合 Poisson（Đ={poisson['dispersity']:.2f}）")
    ax.set_xlim(0, 300)
    ax.set_ylim(1e-5, 0.2)
    ax.set_xlabel('聚合度 $n$')
    ax.set_ylabel('重量分数（对数轴）')
    ax.set_title('分子量分布的形状：Flory 宽、Poisson 窄', loc='left')
    ax.legend(loc='upper right', frameon=False)
    exp.save(fig, 'figure-12-6-mwd', badge='CALC')


def figure_condition_prediction(exp):
    fig, ax = canvas(height=4.0)
    text(ax, 0.5, 0.955, '反应条件预测：输入、数据来源与输出', size=13,
         ha='center', weight='bold')
    inputs = ['单体', '引发剂', '催化剂', '溶剂', '温度', '时间']
    for i, label in enumerate(inputs):
        box(ax, 0.02 + i * 0.163, 0.72, 0.145, 0.10, label, 'blue', size=11)
    box(ax, 0.30, 0.47, 0.40, 0.11, '条件→结果模型', 'orange', size=12)
    for i in range(len(inputs)):
        arrow(ax, (0.0925 + i * 0.163, 0.72), (0.40 + 0.20 * i / 5.0, 0.58))
    outputs = ['conversion', 'Mn / Mw', 'Đ', 'sequence']
    for i, label in enumerate(outputs):
        box(ax, 0.06 + i * 0.235, 0.22, 0.20, 0.10, label, 'green', size=11)
        arrow(ax, (0.16 + 0.20 * i / 3.0, 0.47), (0.16 + i * 0.235, 0.32))
    text(ax, 0.5, 0.075,
         '数据来源：文献挖掘、ELN、高通量实验；标签噪声与量纲需先治理。',
         size=11, ha='center')
    exp.save(fig, 'figure-12-7-condition-prediction', badge='SCHEMATIC')


def figure_retrosynthesis_search(exp):
    summary = ROUTE['summary']
    values = [summary['exhaustive_nodes'], summary['beam_nodes']]
    logs = [math.log10(value) for value in values]
    fig, ax = plot(height=3.7, left=.30, bottom=.20)
    ax.barh([1, 0], logs, color=[COL['purple'], COL['green']],
            edgecolor=COL['line'], linewidth=.9, height=.5, zorder=2)
    ax.set_yticks([1, 0])
    ax.set_yticklabels(['穷举 $b^{d}$', '束搜索（前 $k$）'])
    ax.set_xlim(0, 11)
    ax.set_xlabel('搜索节点数（常用对数 $\\log_{10}N$）')
    ax.text(logs[0] - 0.2, 1, f"$3.1\\times10^{{8}}$", size=11, ha='right',
            va='center')
    ax.text(logs[1] + 0.2, 0, f"$2.1\\times10^{{3}}$", size=11, ha='left',
            va='center')
    ax.set_title(f"剪枝比约 $1.5\\times10^{{5}}$（$b=50$、$d=5$、$k=10$）", loc='left')
    exp.save(fig, 'figure-12-8-retrosynthesis-search', badge='CALC')


def figure_synthesizability_scores(exp):
    fig, (left, right) = panels(height=3.6)
    x = np.linspace(0, 1, 300)
    left.plot(x, np.exp(-0.5 * ((x - 0.42) / 0.15) ** 2), color=COL['purple'],
              lw=2.0)
    left.axvline(0.5, color=COL['line'], lw=1.2, ls='--')
    left.plot([0.26], [0.28], marker='o', ms=8, color=COL['orange'],
              markeredgecolor=COL['line'])
    left.annotate('已知商业化单体被误杀', xy=(0.26, 0.28), xytext=(0.30, 0.72),
                  size=11, arrowprops=dict(arrowstyle='-', color=COL['line'], lw=.9))
    left.set_xlim(0, 1)
    left.set_ylim(0, 1.05)
    left.set_xlabel('规则式评分（片段贡献）')
    left.set_ylabel('候选密度（示意）')
    left.set_title('规则法：假阳性', loc='left')
    left.text(0.02, 0.90, '(a)', transform=left.transAxes, size=12, weight='bold')
    right.plot(x, np.exp(-0.5 * ((x - 0.60) / 0.15) ** 2), color=COL['green'],
               lw=2.0)
    right.axvline(0.5, color=COL['line'], lw=1.2, ls='--')
    right.plot([0.58], [0.55], marker='o', ms=8, color=COL['orange'],
               markeredgecolor=COL['line'])
    right.annotate('同一单体评分靠前', xy=(0.58, 0.55), xytext=(0.30, 0.80),
                   size=11, arrowprops=dict(arrowstyle='-', color=COL['line'], lw=.9))
    right.set_xlim(0, 1)
    right.set_ylim(0, 1.05)
    right.set_xlabel('学习式评分（反应数据）')
    right.set_title('学习法：标签校准', loc='left')
    right.text(0.02, 0.90, '(b)', transform=right.transAxes, size=12, weight='bold')
    exp.save(fig, 'figure-12-9-synthesizability-scores', badge='SCHEMATIC')


def figure_worked_route(exp):
    summary = ROUTE['summary']
    fig, (left, right) = panels(height=3.8)
    steps = [row['steps'] for row in summary['yield_curve']]
    yields = [row['total_yield'] for row in summary['yield_curve']]
    left.plot(steps, yields, marker='o', ms=5, color=COL['orange'], lw=2.0,
              label='路线总产率 $0.8^{d}$')
    left.axhline(0.3, color=COL['green'], lw=1.6, ls='--')
    left.text(1.1, 0.34, '目标总产率 0.3', size=11)
    left.annotate('最多 5 步', xy=(5, 0.328), xytext=(4.1, 0.62), size=11,
                  arrowprops=dict(arrowstyle='-', color=COL['line'], lw=.9))
    left.set_xlim(0.5, 7.5)
    left.set_ylim(0, 0.9)
    left.set_xlabel('路线步数 $d$')
    left.set_ylabel('总产率 $Y=\\bar y^{d}$')
    left.legend(loc='upper right', frameon=False)
    left.text(0.02, 0.92, '(a)', transform=left.transAxes, size=12, weight='bold')

    stages = [(row['stage'], f"{row['survivors']:.0f}") for row in summary['funnel']]
    stages = [('初始候选', f"{ROUTE['scenario']['initial_candidates']:.0f}")] + stages
    D.funnel(ax=right, stages=stages, cx=0.30, w_top=0.50, y_top=0.92,
             h=0.15, gap=0.02, shrink=0.14, size=11)
    right.text(0.30, 0.94, '可合成性漏斗（8910 候选）', size=12, ha='center',
               weight='bold')
    right.text(0.02, 0.03, '通过率为示意值；\n存活数由 JSON 复算。', size=11)
    right.text(0.01, 0.85, '(b)', size=12, weight='bold')
    right.axis('off')
    exp.save(fig, 'figure-12-10-worked-route', badge='CALC')


def main():
    exp = Exporter(HERE)
    figure_reaction_network(exp)
    figure_polymerization(exp)
    figure_synthesizability(exp)
    figure_kinetics_regimes(exp)
    figure_copolymerization(exp)
    figure_molecular_weight_distribution(exp)
    figure_condition_prediction(exp)
    figure_retrosynthesis_search(exp)
    figure_synthesizability_scores(exp)
    figure_worked_route(exp)
    exp.finish()
    index = [
        {'figure': '12-1', 'asset': 'ch12/figure-12-1-reaction-network.svg'},
        {'figure': '12-2', 'asset': 'ch12/figure-12-2-polymerization.svg'},
        {'figure': '12-3', 'asset': 'ch12/figure-12-3-synthesizability.svg'},
        {'figure': '12-4', 'asset': 'ch12/figure-12-4-polymerization-regimes.svg'},
        {'figure': '12-5', 'asset': 'ch12/figure-12-5-copolymerization.svg'},
        {'figure': '12-6', 'asset': 'ch12/figure-12-6-mwd.svg'},
        {'figure': '12-7', 'asset': 'ch12/figure-12-7-condition-prediction.svg'},
        {'figure': '12-8', 'asset': 'ch12/figure-12-8-retrosynthesis-search.svg'},
        {'figure': '12-9', 'asset': 'ch12/figure-12-9-synthesizability-scores.svg'},
        {'figure': '12-10', 'asset': 'ch12/figure-12-10-worked-route.svg'},
    ]
    (HERE / 'figure-index.json').write_text(
        json.dumps(index, ensure_ascii=False, indent=2) + '\n')
    for record in exp.checks:
        print(f"{record['figure']}: min label {record['min_label_pt']:.0f} pt, "
              f"{len(record['text_extent_warnings'])} warnings")


if __name__ == '__main__':
    main()
