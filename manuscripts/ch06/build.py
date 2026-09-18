#!/usr/bin/env python3
"""Build chapter-six teaching figures from fixed book evidence.

Usage: python manuscripts/ch06/build.py [--font /path/to/CJK-font.ttf]
"""
from pathlib import Path
import argparse
import hashlib
import json
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE.parent))

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle

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

gnn = json.loads((ROOT / 'calculations/results/gnn-forward-4layer.json').read_text())
curve = json.loads((ROOT / 'calculations/results/learning-curve-target.json').read_text())
bench = json.loads((ROOT / 'experiments/ch06/benchmark/results/summary.json').read_text())


def figure_model_spectrum(exp):
    fig, ax = canvas(height=4.0)
    items = ['线性', '核方法', '树集成', '高斯过程', '图网络', 'Trans\nformer']
    x0, x1, gap, n = 0.18, 0.98, 0.012, len(items)
    D.spectrum(ax, items, y=0.80, h=0.13, size=11, x0=x0, x1=x1, gap=gap,
               left_label='简单 · 可解释', right_label='复杂 · 大数据')
    w = (x1 - x0 - gap * (n - 1)) / n
    centers = [x0 + i * (w + gap) + w / 2 for i in range(n)]
    box(ax, centers[3] - w / 2, 0.735, w, 0.13, '高斯过程', 'orange', size=11)
    rows = [
        ('数据需求', ['低', '中', '中', '中', '高', '高']),
        ('可解释性', ['高', '中', '中', '中', '低', '低']),
        ('不确定度', ['无', '无', '集成', '原生', '额外', '额外']),
    ]
    for r, (label, cells) in enumerate(rows):
        y = 0.50 - r * 0.13
        text(ax, 0.03, y, label, size=11)
        for cx, cell in zip(centers, cells):
            text(ax, cx, y, cell, size=11, ha='center')
    text(ax, 0.5, 0.09, '六个模型族按数据需求、可解释性与不确定度能力排列。',
         size=11, ha='center')
    exp.save(fig, 'figure-6-1-model-spectrum', badge='SCHEMATIC')


def figure_message_passing(exp):
    flops = gnn['summary']['total_flops']
    params = gnn['summary']['parameters']
    fig, ax = canvas(height=4.0)
    ratio = (4.0 * 0.93) / ((420 / 72) * 0.93)
    cx, cy = 0.28, 0.55
    shells = [
        (0.085, [90, 210, 330], 'blue', 11),
        (0.150, [30, 90, 150, 210, 270, 330], 'green', 9),
        (0.215, [0, 45, 90, 135, 180, 225, 270, 315], 'orange', 7),
    ]
    positions = []
    for r, angles, color, ms in shells:
        positions.append([(cx + r * np.cos(np.radians(a)) * ratio,
                           cy + r * np.sin(np.radians(a))) for a in angles])
    for p in positions[0]:
        ax.plot([cx, p[0]], [cy, p[1]], color=COL['line'], lw=.6, zorder=1)
    for i in (0, 1):
        for p in positions[i]:
            near = min(positions[i + 1],
                       key=lambda q: (q[0] - p[0]) ** 2 + (q[1] - p[1]) ** 2)
            ax.plot([p[0], near[0]], [p[1], near[1]],
                    color=COL['line'], lw=.6, zorder=1)
    for pts, (r, angles, color, ms) in zip(positions, shells):
        for p in pts:
            ax.plot([p[0]], [p[1]], 'o', ms=ms, mfc=COL[color],
                    mec=COL['line'], mew=.8, zorder=2)
    ax.plot([cx], [cy], 'o', ms=16, mfc=COL['purple'], mec=COL['line'],
            mew=1, zorder=3)
    text(ax, cx, cy - 0.105, '中心原子', size=11, ha='center')
    text(ax, cx, 0.12, '感受野随层数扩大', size=11, ha='center')
    arrow(ax, (cx, 0.19), (cx, 0.30))
    text(ax, 0.54, 0.90, '消息传递：感受野逐层扩大', size=12, weight='bold')
    for i, label in enumerate(['消息生成', '聚合', '节点更新']):
        box(ax, 0.58, 0.685 - i * 0.15, 0.34, 0.11, label, 'blue', size=11)
    arrow(ax, (0.75, 0.685), (0.75, 0.645))
    arrow(ax, (0.75, 0.535), (0.75, 0.495))
    for x, color, label in [(0.56, 'blue', '1 跳'), (0.69, 'green', '2 跳'),
                            (0.82, 'orange', '3 跳')]:
        ax.plot([x], [0.26], 'o', ms=9, mfc=COL[color], mec=COL['line'],
                mew=.8, zorder=2)
        text(ax, x + 0.022, 0.26, label, size=11)
    text(ax, 0.75, 0.10,
         f'4 层消息传递\n{flops / 1e8:.2f} 亿 FLOPs · {params / 1e4:.0f} 万参数',
         size=11, ha='center')
    exp.save(fig, 'figure-6-2-message-passing', badge='SCHEMATIC')


def figure_predicted_vs_measured(exp):
    mae = curve['summary']['mae_at_n_max']
    rng = np.random.default_rng(11)
    actual = rng.uniform(0.05, 0.98, 140)
    noise = rng.standard_normal(actual.size)
    noise -= noise.mean()
    noise *= mae / np.abs(noise).mean()
    predicted = actual + noise
    fig, ax = plot(height=3.9, left=.16, bottom=.19)
    xs = np.array([0.0, 1.05])
    ax.fill_between(xs, xs - mae, xs + mae, color=COL['blue'], zorder=0)
    ax.plot(xs, xs, color=COL['line'], lw=1.2, ls='--', zorder=1)
    ax.scatter(actual, predicted, s=24, facecolor=COL['orange'],
               edgecolor=COL['line'], linewidth=.5, zorder=3)
    ax.annotate('±MAE 带', xy=(0.30, 0.30), xytext=(0.06, 0.86), size=11,
                arrowprops=dict(arrowstyle='-', color=COL['line'], lw=.9))
    ax.text(0.92, 0.86, 'y = x', size=11, ha='right')
    ax.text(0.72, 0.05, f'MAE = {mae:.3f}', size=11)
    ax.set_xlim(0, 1.05)
    ax.set_ylim(0, 1.05)
    ax.set_xlabel('参考值（归一化）')
    ax.set_ylabel('预测值（归一化）')
    exp.save(fig, 'figure-6-3-predicted-vs-measured', badge='SCHEMATIC')


def figure_benchmark_pipeline(exp):
    fig, ax = canvas(height=4.3)
    text(ax, 0.5, 0.965, '第 6 章基准流水线：同一份数据、同一批种子', size=13,
         ha='center', weight='bold')
    items = [
        ('数据清洗', '7372 → 1765 条', 'SHA256 固定', 'blue'),
        ('图解析', 'SMILES → 原子键图', '1765 条全解析', 'blue'),
        ('表示', '21 描述符 + 256 指纹', '277 维', 'green'),
        ('划分', '骨架 / 单体 / 化学', '骨架重叠 0', 'green'),
        ('模型', '均值 线性 岭 SVR', 'RF / 梯度提升', 'orange'),
        ('评测', 'MAE · R² · Spearman', 'conformal 区间', 'orange'),
    ]
    D.layers(ax, items, x=0.05, w=0.90, y0=0.075, step=0.145, h=0.10,
             name_x=0.11, desc_x=0.30, tag_x=0.90, arrow_x=0.46,
             name_size=12, size=11)
    exp.save(fig, 'figure-6-4-benchmark-pipeline', badge='SCHEMATIC')


def figure_model_comparison(exp):
    agg = bench['primary_models']['aggregate']
    names = ['均值基线', '线性回归', '岭回归', 'SVR', '随机森林', '梯度提升']
    keys = ['mean', 'linear', 'ridge_lambda_10.0', 'svr', 'random_forest',
            'gradient_boosting']
    colors = ['gray', 'blue', 'blue', 'green', 'orange', 'purple']
    values = [agg[k]['mae']['mean'] for k in keys]
    errors = [agg[k]['mae']['std'] for k in keys]
    fig, ax = plot(height=4.0, left=.34, bottom=.20)
    ypos = list(range(len(names)))[::-1]
    ax.barh(ypos, values, xerr=errors, color=[COL[c] for c in colors],
            edgecolor=COL['line'], linewidth=.9,
            error_kw=dict(ecolor=COL['line'], lw=.9, capsize=3))
    ax.set_yticks(ypos)
    ax.set_yticklabels(names)
    ax.set_xlim(0, 72)
    ax.set_xlabel('测试 MAE（K）')
    for y, value, error in zip(ypos, values, errors):
        ax.text(value + error + 1.5, y, f'{value:.1f}', size=11, va='center')
    ax.text(0.98, 0.04, '骨架划分 · 5 个种子', transform=ax.transAxes,
            size=11, ha='right')
    exp.save(fig, 'figure-6-5-model-comparison', badge='DATA')


def figure_split_comparison(exp):
    splits = ['随机', '单体', '骨架', '化学']
    keys = ['random', 'monomer', 'scaffold', 'chemistry']
    ridge = [bench['split_comparison']['ridge_mae'][k]['mean'] for k in keys]
    ridge_std = [bench['split_comparison']['ridge_mae'][k]['std'] for k in keys]
    gb = [bench['split_comparison']['gradient_boosting_mae'][k]['mean'] for k in keys]
    gb_std = [bench['split_comparison']['gradient_boosting_mae'][k]['std'] for k in keys]
    x = np.arange(len(splits))
    width = 0.38
    fig, ax = plot(height=3.9, left=.16, bottom=.20)
    ax.bar(x - width / 2, ridge, width, yerr=ridge_std, label='岭回归',
           color=COL['blue'], edgecolor=COL['line'], linewidth=.9,
           error_kw=dict(ecolor=COL['line'], lw=.9, capsize=3))
    ax.bar(x + width / 2, gb, width, yerr=gb_std, label='梯度提升',
           color=COL['orange'], edgecolor=COL['line'], linewidth=.9,
           error_kw=dict(ecolor=COL['line'], lw=.9, capsize=3))
    for xi, (a, b) in enumerate(zip(ridge, gb)):
        ax.text(xi - width / 2, a + ridge_std[xi] + 0.8, f'{a:.1f}', size=11,
                ha='center')
        ax.text(xi + width / 2, b + gb_std[xi] + 0.8, f'{b:.1f}', size=11,
                ha='center')
    ax.set_xticks(x)
    ax.set_xticklabels(splits)
    ax.set_ylim(0, 46)
    ax.set_ylabel('测试 MAE（K）')
    ax.set_xlabel('划分（按分组粒度排列）')
    ax.legend(loc='upper left')
    exp.save(fig, 'figure-6-6-split-comparison', badge='DATA')


def figure_learning_curve(exp):
    points = bench['learning_curve']['points']
    sizes = np.array([p['n'] for p in points], dtype=float)
    errors = np.array([p['mae'] for p in points], dtype=float)
    a = bench['learning_curve']['power_law_A']
    alpha = bench['learning_curve']['power_law_exponent']
    grid = np.linspace(sizes.min(), sizes.max(), 120)
    fig, ax = plot(height=3.9, left=.17, bottom=.20)
    ax.plot(grid, a * grid ** (-alpha), color=COL['line'], lw=1.3, zorder=1)
    ax.scatter(sizes, errors, s=90, facecolor=COL['orange'],
               edgecolor=COL['line'], linewidth=.9, zorder=3)
    for n, e in zip(sizes, errors):
        ax.text(n * 1.06, e + 0.5, f'{e:.1f}', size=11)
    ax.set_xscale('log')
    ax.set_xlim(40, 1800)
    ax.set_ylim(27.5, 45)
    ax.set_xlabel('训练量（条，对数轴）')
    ax.set_ylabel('测试 MAE（K）')
    ax.text(0.98, 0.92, f'MAE = {a:.1f} · n$^{{-{alpha:.3f}}}$\n拟合 R² = '
            f'{bench["learning_curve"]["fit_r2"]:.3f}', transform=ax.transAxes,
            size=11, ha='right', va='top')
    exp.save(fig, 'figure-6-7-learning-curve', badge='DATA')


def figure_uncertainty(exp):
    conformal = bench['uncertainty']['conformal']
    quantile = bench['uncertainty']['quantile_regression']
    ensemble = bench['uncertainty']['ensemble_variance']
    fig, axes = plt.subplots(1, 2, figsize=(420 / 72, 4.0))
    fig.subplots_adjust(left=.16, right=.96, bottom=.20, top=.88, wspace=.55)
    ax = axes[0]
    nominal = [c['nominal_coverage'] for c in conformal]
    achieved = [c['coverage'] for c in conformal]
    y = np.arange(len(conformal))[::-1]
    ax.barh(y + 0.18, nominal, 0.34, color=COL['gray'], edgecolor=COL['line'],
            linewidth=.9, label='名义覆盖')
    ax.barh(y - 0.18, achieved, 0.34, color=COL['green'], edgecolor=COL['line'],
            linewidth=.9, label='实际覆盖')
    ax.set_yticks(y)
    ax.set_yticklabels([f'{c["nominal_coverage"] * 100:.0f}%' for c in conformal])
    ax.set_xlim(0.6, 1.0)
    ax.set_xlabel('覆盖')
    ax.legend(loc='lower right')
    ax = axes[1]
    labels = ['集成方差', 'Conformal 90%', '分位数回归 90%']
    widths = [ensemble['random_forest_std_mean_k'],
              conformal[1]['mean_width_k'], quantile['mean_width_k']]
    ax.barh([2, 1, 0], widths, color=[COL['purple'], COL['blue'], COL['orange']],
            edgecolor=COL['line'], linewidth=.9)
    for yi, value in zip([2, 1, 0], widths):
        ax.text(value + 6, yi, f'{value:.1f}', size=11, va='center')
    ax.set_yticks([2, 1, 0])
    ax.set_yticklabels(labels)
    ax.set_xlim(0, 330)
    ax.set_xlabel('区间宽度（K）')
    for i, ax in enumerate(axes):
        ax.spines[['top', 'right']].set_visible(False)
        ax.text(0.02, 0.90, f'({chr(97 + i)})', transform=ax.transAxes,
                size=12, weight='bold')
    exp.save(fig, 'figure-6-8-uncertainty', badge='DATA')


def figure_failure_modes(exp):
    fig, ax = canvas(height=4.4)
    text(ax, 0.5, 0.955, '性质预测的四类失败模式', size=13, ha='center',
         weight='bold')
    cells = [
        ('外推', '最近邻相似度低', '声明域外，不自动筛选', 'orange'),
        ('组成漂移', '描述符均值偏移', '监测组成，重校准', 'orange'),
        ('同系物泄漏', '跨集合分组重叠', '按结构分组划分', 'blue'),
        ('测量差异', '残差按方法聚集', '按方法分层校准', 'blue'),
    ]
    x0, y0, w, h, gap = 0.05, 0.10, 0.43, 0.34, 0.04
    for i, (name, signal, fix, color) in enumerate(cells):
        cx = x0 + (i % 2) * (w + gap)
        cy = y0 + (1 - i // 2) * (h + gap)
        ax.add_patch(Rectangle((cx, cy), w, h, facecolor=COL[color],
                               edgecolor=COL['line'], linewidth=.9))
        text(ax, cx + w / 2, cy + h - 0.055, name, size=12, ha='center',
             weight='bold')
        text(ax, cx + w / 2, cy + h / 2, '诊断：' + signal, size=11, ha='center')
        text(ax, cx + w / 2, cy + 0.055, '修法：' + fix, size=11, ha='center')
    exp.save(fig, 'figure-6-9-failure-modes', badge='SCHEMATIC')


def figure_selection_guide(exp):
    fig, ax = canvas(height=4.4)
    text(ax, 0.5, 0.965, '模型选型决策路径', size=13, ha='center', weight='bold')
    steps = ['数据规模与部署场景', '三层基线', '学习曲线检查',
             '表示字段检查', '不确定度校准', '复现清单']
    x, w, h, step = 0.05, 0.42, 0.085, 0.135
    y0 = 0.86
    for i, label in enumerate(steps):
        y = y0 - i * step
        box(ax, x, y - h, w, h, label, 'blue' if i < 3 else 'green', size=11)
        if i:
            arrow(ax, (x + 0.07, y + step - h), (x + 0.07, y))
    box(ax, 0.56, 0.33, 0.40, 0.42, '', 'orange')
    text(ax, 0.76, 0.70, '三个停止信号', size=11, ha='center', weight='bold')
    for j, note in enumerate(['改进小于种子波动', '学习曲线走平', '分组误差偏高']):
        text(ax, 0.58, 0.61 - j * 0.085, note, size=11)
    arrow(ax, (0.56, 0.54), (0.47, 0.47), kind='control')
    text(ax, 0.05, 0.03, '先跑基线与学习曲线，再决定是否上复杂模型。', size=11)
    exp.save(fig, 'figure-6-10-selection-guide', badge='SCHEMATIC')


def main():
    exp = Exporter(HERE)
    figure_model_spectrum(exp)
    figure_message_passing(exp)
    figure_predicted_vs_measured(exp)
    figure_benchmark_pipeline(exp)
    figure_model_comparison(exp)
    figure_split_comparison(exp)
    figure_learning_curve(exp)
    figure_uncertainty(exp)
    figure_failure_modes(exp)
    figure_selection_guide(exp)
    exp.finish()
    index = [
        {'figure': '6-1', 'asset': 'ch06/figure-6-1-model-spectrum.svg'},
        {'figure': '6-2', 'asset': 'ch06/figure-6-2-message-passing.svg'},
        {'figure': '6-3', 'asset': 'ch06/figure-6-3-predicted-vs-measured.svg'},
        {'figure': '6-4', 'asset': 'ch06/figure-6-4-benchmark-pipeline.svg'},
        {'figure': '6-5', 'asset': 'ch06/figure-6-5-model-comparison.svg'},
        {'figure': '6-6', 'asset': 'ch06/figure-6-6-split-comparison.svg'},
        {'figure': '6-7', 'asset': 'ch06/figure-6-7-learning-curve.svg'},
        {'figure': '6-8', 'asset': 'ch06/figure-6-8-uncertainty.svg'},
        {'figure': '6-9', 'asset': 'ch06/figure-6-9-failure-modes.svg'},
        {'figure': '6-10', 'asset': 'ch06/figure-6-10-selection-guide.svg'},
    ]
    (HERE / 'figure-index.json').write_text(
        json.dumps(index, ensure_ascii=False, indent=2) + '\n')
    for record in exp.checks:
        print(f"{record['figure']}: min label {record['min_label_pt']:.0f} pt, "
              f"{len(record['text_extent_warnings'])} warnings")


if __name__ == '__main__':
    main()
