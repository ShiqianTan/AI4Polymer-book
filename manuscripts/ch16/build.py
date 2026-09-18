#!/usr/bin/env python3
"""Build chapter-sixteen teaching figures from fixed book evidence.

Usage: python manuscripts/ch16/build.py [--font /path/to/CJK-font.ttf]
"""
from pathlib import Path
import argparse
import csv
import hashlib
import json
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE.parent))

import matplotlib.pyplot as plt
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

block = json.loads(
    (ROOT / 'calculations/results/chemical-space-block.json').read_text())['summary']
descriptor = json.loads(
    (ROOT / 'calculations/results/descriptor-morgan-2048.json').read_text())['summary']
flagship = json.loads(
    (ROOT / 'experiments/ch16/flagship/results/summary.json').read_text())
benchmark = json.loads(
    (ROOT / 'experiments/ch06/benchmark/results/summary.json').read_text())
case2 = json.loads(
    (ROOT / 'experiments/ch16/case2/results/summary.json').read_text())
case3 = json.loads(
    (ROOT / 'experiments/ch16/case3/results/summary.json').read_text())

CANDIDATES = block['sequence_count']
SYNTH_FRACTION = block['synthesizable_fraction']
FINGERPRINT_BITS = descriptor['feature_dim']
BYTES_PER_MOLECULE = descriptor['bytes_per_molecule']
LIBRARY_SIZE = descriptor['library_size']
EXPECTED_COLLISIONS = descriptor['expected_collisions']


def two_panel(height=3.9, wspace=0.34, left=0.09, right=0.97):
    fig, axes = plt.subplots(1, 2, figsize=(420 / 72, height))
    fig.subplots_adjust(left=left, right=right, bottom=0.17, top=0.92, wspace=wspace)
    return fig, axes


def bar_panel(ax, labels, values, color, ylabel, ylim=None, fmt='{:.2f}'):
    ax.bar(range(len(labels)), values, color=COL[color], edgecolor=COL['line'],
           linewidth=.8, width=.62)
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, fontsize=11)
    ax.set_ylabel(ylabel, fontsize=11)
    ax.tick_params(labelsize=11)
    if ylim:
        ax.set_ylim(*ylim)
    span = (ylim[1] - ylim[0]) if ylim else max(values)
    for i, value in enumerate(values):
        ax.text(i, value + span * 0.02, fmt.format(value), ha='center', va='bottom',
                fontsize=11)
    ax.spines[['top', 'right']].set_visible(False)


def unit_panel(ax):
    ax.set(xlim=(0, 1), ylim=(0, 1))
    ax.axis('off')


def figure_16_1_pipeline(exp):
    fig, ax = canvas(height=3.4)
    steps = ['需求', '表示', '数据', '模型', '生成', '筛选', '合成', '验证']
    D.pipeline(ax, steps, y=0.64, h=0.14, back=[(2, 1), (4, 3), (6, 5), (7, 6)])
    text(ax, 0.5, 0.90, '端到端设计流程', size=13, ha='center', weight='bold')
    text(ax, 0.5, 0.12, '每步输出可验证的中间结果；虚线：某步不达标时回退一步调整',
         size=11, ha='center')
    exp.save(fig, 'figure-16-1-pipeline', badge='SCHEMATIC')


def figure_16_2_cases(exp):
    fig, ax = canvas(height=3.6)
    rows = [
        ['高 Tg\n透明聚酰亚胺', 'Tg > 200 °C\n可见光透明', '可溶液加工\n单体可购买',
         '样本\n约 10³', '透明与\n耐热难兼顾'],
        ['可回收\n热固性材料', '模量接近环氧\n温和解聚', '解聚温度\n< 150 °C',
         '候选空间\n8910 条', '性能与解聚\n温度权衡'],
        ['气体\n分离膜', '选择性 > 25\n渗透率 > 100 Barrer', '测量条件\n归一化',
         '样本\n约 10³', '突破 Robeson\n上限稀少'],
    ]
    D.table(ax, ['案例', '目标性质', '硬约束', '数据规模', '关键风险'], rows,
            y_top=0.82, row_h=0.17, col_x=[0.13, 0.35, 0.56, 0.75, 0.90])
    text(ax, 0.04, 0.19,
         f'候选空间：10 单体、链长 100 嵌段组合 {CANDIDATES} 条；\n'
         f'规则可合成比例 {SYNTH_FRACTION:.1f}（规则判据，不等于实验可合成）；\n'
         f'Morgan {FINGERPRINT_BITS} 位指纹每条 {BYTES_PER_MOLECULE} B，'
         f'{LIBRARY_SIZE:,} 库期望碰撞 {EXPECTED_COLLISIONS:.0f}。',
         size=11)
    exp.save(fig, 'figure-16-2-cases', badge='CALC')


def figure_16_3_decisions(exp):
    fig, ax = canvas(height=3.8)
    D.tree(ax, '检查失败类型', ['数据不足', '模型不达标', '候选不可合成'],
           root_xy=(0.5, 0.86), branch_y=0.62, w=0.26, h=0.12)
    actions = ['补充采样\n或换表示', '重训模型\n或加约束', '可达性过滤\n或改键型']
    for i, action in enumerate(actions):
        x = 0.05 + 0.90 * (i + 0.5) / 3
        box(ax, x - 0.14, 0.28, 0.28, 0.16, action, 'green', size=11)
        arrow(ax, (x, 0.56), (x, 0.44))
    text(ax, 0.5, 0.10, '沿分支定位当前状态，先回退再继续优化',
         size=11, ha='center')
    exp.save(fig, 'figure-16-3-decisions', badge='SCHEMATIC')


def figure_16_4_case1_funnel(exp):
    fig, ax = canvas(height=3.5)
    funnel = flagship['funnel']
    stages = [
        ('枚举', str(funnel['enumerated'])),
        ('构建', str(funnel['built'])),
        ('Tg 达标', str(funnel['tg_pass'])),
        ('透明代理', str(funnel['transparent_pass'])),
        ('可合成', str(funnel['synthesizable_pass'])),
    ]
    D.funnel(ax, [(label, value) for label, value in stages],
             cx=0.36, w_top=0.50, y_top=0.90, h=0.14, gap=0.012, shrink=0.15)
    text(ax, 0.72, 0.74, '案例一\n312 → 74', size=12, weight='bold')
    text(ax, 0.72, 0.52,
         '透明性只有结构代理，\n无透过率标签；\n'
         '74 个进入合成评审，\nTop 5 中 3 个为新结构。',
         size=11)
    text(ax, 0.36, 0.055, '每一级为上一级的子集；数值由旗舰脚本实算', size=11, ha='center')
    exp.save(fig, 'figure-16-4-case1-funnel', badge='DATA')


def figure_16_5_case1_learning(exp):
    fig, axes = two_panel(height=3.6, left=0.11, right=0.97, wspace=0.36)
    curve = flagship['learning_curve']['curve']
    fit = flagship['learning_curve']['fit']
    sizes = [point['n'] for point in curve]
    errors = [point['mae'] for point in curve]
    axes[0].plot(sizes, errors, marker='o', color=COL['line'], linewidth=1.2,
                 markersize=4, markerfacecolor=COL['blue'])
    grid = [20 + i * (1400 - 20) / 100 for i in range(101)]
    fitline = [fit['a'] * n ** (-fit['alpha']) for n in grid]
    axes[0].plot(grid, fitline, color='#c0392b', linewidth=1.0, linestyle='--')
    axes[0].set_xlabel('训练样本数 n', fontsize=11)
    axes[0].set_ylabel('测试 MAE (K)', fontsize=11)
    axes[0].tick_params(labelsize=11)
    axes[0].spines[['top', 'right']].set_visible(False)
    axes[0].text(0.04, 0.12,
                 f"MAE = {fit['a']:.1f} n^-{fit['alpha']:.3f}\n拟合 R² = {fit['fit_r2']:.3f}",
                 transform=axes[0].transAxes, fontsize=11)

    levels = flagship['uncertainty']['levels']
    nominal = [level['nominal_coverage'] * 100 for level in levels]
    achieved = [level['coverage'] * 100 for level in levels]
    positions = range(len(levels))
    axes[1].bar([p - 0.18 for p in positions], nominal, width=0.34, color=COL['gray'],
                edgecolor=COL['line'], linewidth=.8, label='名义覆盖')
    axes[1].bar([p + 0.18 for p in positions], achieved, width=0.34, color=COL['green'],
                edgecolor=COL['line'], linewidth=.8, label='实测覆盖')
    axes[1].set_xticks(list(positions))
    axes[1].set_xticklabels([f"{int(n)}%" for n in nominal], fontsize=11)
    axes[1].set_ylabel('覆盖 (%)', fontsize=11)
    axes[1].set_ylim(0, 108)
    axes[1].tick_params(labelsize=11)
    axes[1].legend(fontsize=11, loc='lower right')
    axes[1].spines[['top', 'right']].set_visible(False)
    axes[0].set_title('(a)', fontsize=12)
    axes[1].set_title('(b)', fontsize=12)
    exp.save(fig, 'figure-16-5-case1-learning', badge='DATA')


def figure_16_6_case1_benchmark(exp):
    fig, ax = plot(height=3.5, left=0.13, bottom=0.20)
    labels = ['均值基线', 'Ridge', '随机森林', '梯度提升']
    flagship_models = flagship['models']
    flagship_values = [
        flagship_models['baselines']['mean']['mae'],
        flagship_models['baselines']['ridge']['mae'],
        flagship_models['baselines']['random_forest']['mae'],
        flagship_models['main']['mae'],
    ]
    aggregate = benchmark['primary_models']['aggregate']
    benchmark_values = [
        aggregate['mean']['mae']['mean'],
        aggregate['ridge_lambda_10.0']['mae']['mean'],
        aggregate['random_forest']['mae']['mean'],
        aggregate['gradient_boosting']['mae']['mean'],
    ]
    positions = range(len(labels))
    ax.bar([p - 0.18 for p in positions], flagship_values, width=0.34, color=COL['blue'],
           edgecolor=COL['line'], linewidth=.8, label='案例一（RDKit 指纹 + 树）')
    ax.bar([p + 0.18 for p in positions], benchmark_values, width=0.34, color=COL['orange'],
           edgecolor=COL['line'], linewidth=.8, label='第 6 章基准（纯标准库）')
    ax.set_xticks(list(positions))
    ax.set_xticklabels(labels, fontsize=11)
    ax.set_ylabel('测试 MAE (K)', fontsize=11)
    ax.set_ylim(0, 76)
    ax.tick_params(labelsize=11)
    ax.legend(fontsize=11, loc='upper right')
    ax.spines[['top', 'right']].set_visible(False)
    exp.save(fig, 'figure-16-6-case1-benchmark', badge='DATA')


def figure_16_7_case2_funnel(exp):
    fig, axes = two_panel(height=3.9, left=0.09, right=0.97, wspace=0.40)
    unit_panel(axes[0])
    funnel = case2['funnel']
    stages = [
        ('枚举', str(funnel['enumerated'])),
        ('构建', str(funnel['built'])),
        ('动态键', str(funnel['dynamic_bond_pass'])),
        ('网络', str(funnel['network_pass'])),
        ('Tg 窗口', str(funnel['tg_window_pass'])),
        ('密度', str(funnel['density_pass'])),
    ]
    D.funnel(axes[0], stages, cx=0.34, w_top=0.52, y_top=0.90, h=0.125, gap=0.008,
             shrink=0.13)
    axes[0].set_title('(a)', fontsize=12)
    axes[0].text(0.66, 0.16, '真实数据\n8424 条训练', fontsize=11)

    splits = case2['splits']['epoxide_group']
    labels = ['均值', 'Ridge', '随机森林', '梯度提升']
    values = [
        splits['baseline_mean']['mae'],
        splits['ridge']['mae'],
        splits['random_forest']['mae'],
        splits['gradient_boosting']['mae'],
    ]
    bar_panel(axes[1], labels, values, 'green', 'MAE (K)', ylim=(0, 32))
    axes[1].set_title('(b)', fontsize=12)
    exp.save(fig, 'figure-16-7-case2-funnel', badge='DATA')


def figure_16_8_case2_calibration(exp):
    fig, ax = plot(height=3.6, left=0.14, bottom=0.18)
    rows = list(csv.DictReader(open(ROOT / 'experiments/ch16/case2/data/tg_calibration.csv')))
    experimental = [float(row['tg_exp']) for row in rows]
    simulated = [float(row['tg_md']) for row in rows]
    ax.scatter(experimental, simulated, s=12, color=COL['purple'], edgecolor=COL['line'],
               linewidth=.4, alpha=.8)
    limits = [150, 520]
    ax.plot(limits, limits, color=COL['line'], linewidth=1.0, linestyle='--')
    ax.set_xlim(*limits)
    ax.set_ylim(*limits)
    ax.set_xlabel('实验 Tg (K)', fontsize=11)
    ax.set_ylabel('MD Tg (K)', fontsize=11)
    ax.tick_params(labelsize=11)
    ax.spines[['top', 'right']].set_visible(False)
    calibration = case2['external_calibration']
    ax.text(0.05, 0.90,
            f"MAE = {calibration['mae_md_vs_exp']:.1f} K\n"
            f"系统偏差 = {calibration['bias_md_vs_exp']:+.1f} K",
            transform=ax.transAxes, fontsize=11, va='top')
    exp.save(fig, 'figure-16-8-case2-calibration', badge='DATA')


def figure_16_9_case3_robeson(exp):
    fig, ax = plot(height=3.7, left=0.13, bottom=0.18)
    rows = list(csv.DictReader(open(ROOT / 'experiments/ch16/case3/data/datasetA_imputed_all.csv')))
    xs, ys = [], []
    for row in rows:
        try:
            co2 = float(row['CO2'])
            ch4 = float(row['CH4'])
        except (TypeError, ValueError):
            continue
        if co2 > 0 and ch4 > 0:
            xs.append(round(__import__('math').log10(co2 / ch4), 4))
            ys.append(__import__('math').log10(co2))
    ax.scatter(xs, ys, s=12, color=COL['blue'], edgecolor=COL['line'], linewidth=.4,
               alpha=.8, label='实测（217 条）')
    slope = case3['robeson']['slope']
    intercept = case3['robeson']['intercept']
    line_x = [-0.8, 2.0]
    ax.plot(line_x, [intercept + slope * x for x in line_x], color='#c0392b',
            linewidth=1.2, linestyle='--', label='本书拟合参照线')
    top = case3['top5']
    ax.scatter([__import__('math').log10(row['alpha']) for row in top],
               [__import__('math').log10(row['p_co2']) for row in top],
               s=28, marker='^', color=COL['orange'], edgecolor=COL['line'],
               linewidth=.5, label='预测短名单 Top 5')
    ax.set_xlabel('log₁₀ α(CO₂/CH₄)', fontsize=11)
    ax.set_ylabel('log₁₀ P(CO₂) [Barrer]', fontsize=11)
    ax.set_xlim(-0.9, 2.1)
    ax.set_ylim(-1.0, 5.2)
    ax.tick_params(labelsize=11)
    ax.legend(fontsize=11, loc='lower left')
    ax.spines[['top', 'right']].set_visible(False)
    exp.save(fig, 'figure-16-9-case3-robeson', badge='DATA')


def figure_16_10_case3_splits(exp):
    fig, axes = two_panel(height=3.7, left=0.10, right=0.97, wspace=0.40)
    splits = case3['splits']
    labels = ['随机', '单体家族', '时间']
    values = [
        splits['random']['gradient_boosting']['mae'],
        splits['monomer_group']['gradient_boosting']['mae'],
        splits['time_2000']['gradient_boosting']['mae'],
    ]
    bar_panel(axes[0], labels, values, 'orange', 'MAE (dex)', ylim=(0, 1.8), fmt='{:.3f}')
    axes[0].set_title('(a)', fontsize=12)
    unit_panel(axes[1])
    funnel = case3['screening']
    D.funnel(axes[1], [
        ('候选库', str(funnel['structures'])),
        ('P > 100', str(funnel['p_co2_pass'])),
        ('α > 25', str(funnel['alpha_pass'])),
        ('上限之上', str(funnel['above_bound'])),
    ], cx=0.36, w_top=0.54, y_top=0.86, h=0.15, gap=0.012, shrink=0.16)
    axes[1].set_title('(b)', fontsize=12)
    axes[1].text(0.30, 0.12, f"最大 α {funnel['max_predicted_alpha']:.1f}\n"
                             f"α > 20 共 {funnel['alpha_above_20']}",
                 fontsize=11, ha='center')
    exp.save(fig, 'figure-16-10-case3-splits', badge='DATA')


def main():
    exp = Exporter(HERE)
    figure_16_1_pipeline(exp)
    figure_16_2_cases(exp)
    figure_16_3_decisions(exp)
    figure_16_4_case1_funnel(exp)
    figure_16_5_case1_learning(exp)
    figure_16_6_case1_benchmark(exp)
    figure_16_7_case2_funnel(exp)
    figure_16_8_case2_calibration(exp)
    figure_16_9_case3_robeson(exp)
    figure_16_10_case3_splits(exp)
    exp.finish()
    index = [
        {'figure': '16-1', 'asset': 'ch16/figure-16-1-pipeline.svg'},
        {'figure': '16-2', 'asset': 'ch16/figure-16-2-cases.svg'},
        {'figure': '16-3', 'asset': 'ch16/figure-16-3-decisions.svg'},
        {'figure': '16-4', 'asset': 'ch16/figure-16-4-case1-funnel.svg'},
        {'figure': '16-5', 'asset': 'ch16/figure-16-5-case1-learning.svg'},
        {'figure': '16-6', 'asset': 'ch16/figure-16-6-case1-benchmark.svg'},
        {'figure': '16-7', 'asset': 'ch16/figure-16-7-case2-funnel.svg'},
        {'figure': '16-8', 'asset': 'ch16/figure-16-8-case2-calibration.svg'},
        {'figure': '16-9', 'asset': 'ch16/figure-16-9-case3-robeson.svg'},
        {'figure': '16-10', 'asset': 'ch16/figure-16-10-case3-splits.svg'},
    ]
    (HERE / 'figure-index.json').write_text(
        json.dumps(index, ensure_ascii=False, indent=2) + '\n')
    for record in exp.checks:
        print(f"{record['figure']}: min label {record['min_label_pt']:.0f} pt, "
              f"{len(record['text_extent_warnings'])} warnings")


if __name__ == '__main__':
    main()
