#!/usr/bin/env python3
"""Build chapter-five teaching figures from fixed book evidence.

Usage: python manuscripts/ch05/build.py [--font /path/to/CJK-font.ttf]
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

dft = json.loads((ROOT / 'calculations/results/md-cost-dft.json').read_text())
mlff = json.loads((ROOT / 'calculations/results/md-cost-mlff.json').read_text())


def figure_multiscale_pyramid(exp):
    fig, ax = canvas(height=4.0)
    text(ax, 0.5, 0.96, '多尺度方法：空间/时间尺度与典型方法',
         size=12, ha='center', weight='bold')
    tiers = [
        ('电子结构', 'Å · fs · DFT'),
        ('全原子', 'nm · ns · 经典力场'),
        ('粗粒化', '10 nm · µs · 珠簧模型'),
        ('连续介质', 'µm · ms · 有限元'),
    ]
    D.pyramid(ax, tiers, cx=0.40, w_top=0.18, y_top=0.87, h=0.16, gap=0.02,
              widen=0.10, size=11, colors=['purple', 'orange', 'green', 'blue'])
    text(ax, 0.03, 0.08, '向上：尺度减小 · 精度提高\n向下：尺度增大 · 代价降低', size=11)
    exp.save(fig, 'figure-5-1-multiscale-pyramid', badge='SCHEMATIC')


def figure_accuracy_cost(exp):
    dft_cost = dft['summary']['gpu_seconds'] / dft['summary']['atom_steps']
    mlff_cost = mlff['summary']['gpu_seconds'] / mlff['summary']['atom_steps']
    fig, ax = plot(height=3.9, left=.20, bottom=.20)
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.grid(True, which='major', color=COL['gray'], lw=.7, zorder=0)
    ax.grid(True, which='minor', color=COL['gray'], lw=.4, zorder=0)
    ax.axhline(10.0, color=COL['line'], lw=1, ls='--', zorder=1)
    ax.axvline(mlff_cost, color=COL['line'], lw=1, ls='--', zorder=1)
    ax.scatter([mlff_cost], [10.0], s=140, facecolor=COL['blue'],
               edgecolor=COL['line'], linewidth=1, zorder=4)
    ax.scatter([dft_cost], [1.0], s=70, facecolor=COL['purple'],
               edgecolor=COL['line'], linewidth=.9, zorder=4)
    ax.scatter([2e-11], [50.0], s=70, facecolor=COL['green'],
               edgecolor=COL['line'], linewidth=.9, zorder=4)
    ax.scatter([2e-12], [500.0], s=70, facecolor=COL['gray'],
               edgecolor=COL['line'], linewidth=.9, zorder=4)
    ax.text(7e-3, 1.0, 'DFT · 电子结构', size=11, ha='right')
    ax.text(4e-8, 24, '机器学习势', size=11, weight='bold')
    ax.text(5e-11, 110, '全原子力场', size=11)
    ax.text(4e-13, 900, '粗粒化', size=11)
    ax.text(2.5e-2, 11.5, '等精度线', size=11, ha='right')
    ax.text(mlff_cost * 1.35, 1.7e3, '等代价线', size=11)
    ax.set_xlim(1e-13, 3e-1)
    ax.set_ylim(0.4, 3e3)
    ax.set_xlabel('每原子每步代价（GPU·s）')
    ax.set_ylabel('能量误差（meV/atom）')
    exp.save(fig, 'figure-5-2-accuracy-cost', badge='CALC')


def figure_trajectory(exp):
    rng = np.random.default_rng(7)
    t = np.linspace(0, 10, 1400)
    temp = 300 + 220 * np.exp(-t / 1.0) + 9 * rng.standard_normal(t.size)
    energy = -850 + 190 * np.exp(-t / 0.9) + 12 * rng.standard_normal(t.size)
    coord = 4.1 + 1.5 * np.exp(-t / 1.3) + 0.22 * np.sin(3.1 * t) \
        + 0.12 * rng.standard_normal(t.size)
    fig, ax1 = plot(height=4.3, left=.15, bottom=.13)
    fig.subplots_adjust(right=.86)
    ax1.set_position([.15, .57, .71, .36])
    ax2 = fig.add_axes([.15, .13, .71, .30], sharex=ax1)
    ax2.spines[['top', 'right']].set_visible(False)
    axr = ax1.twinx()
    axr.set_position(ax1.get_position())
    for axis in (ax1, ax2):
        axis.axvspan(0, 3, color=COL['gray'], zorder=0)
        axis.axvspan(3, 10, color=COL['blue'], zorder=0)
    for frame in range(3, 11):
        ax2.axvline(frame, color=COL['line'], lw=.6, ls=':', zorder=1)
    line_t, = ax1.plot(t, temp, color=COL['line'], lw=1.1, label='温度')
    line_e, = axr.plot(t, energy, color=COL['orange'], lw=1.6, label='势能')
    ax2.plot(t, coord, color=COL['line'], lw=1.1, zorder=2)
    ax1.text(1.5, 540, '平衡段', size=11, ha='center')
    ax1.text(6.5, 540, '采样段', size=11, ha='center')
    ax2.text(6.5, 5.95, '保存帧（每 1 ns）', size=11, ha='center', va='top')
    ax1.legend(handles=[line_t, line_e], loc='upper right')
    ax1.set_ylim(280, 570)
    axr.set_ylim(-930, -590)
    ax2.set_ylim(3.0, 6.3)
    ax2.set_xlim(0, 10)
    ax2.set_xticks([0, 2, 4, 6, 8, 10])
    ax2.set_xlabel('时间（ns）')
    ax1.set_ylabel('温度（K）')
    axr.set_ylabel('势能（kJ/mol）')
    ax2.set_ylabel('链段坐标（Å）')
    ax1.text(0.015, 0.90, '(a)', transform=ax1.transAxes, size=12, weight='bold')
    ax2.text(0.015, 0.86, '(b)', transform=ax2.transAxes, size=12, weight='bold')
    exp.save(fig, 'figure-5-3-trajectory', badge='SCHEMATIC')


def figure_md_workflow(exp):
    fig, ax = canvas(height=4.6)
    text(ax, 0.5, 0.965, '经典 MD：从单体到玻璃化转变温度',
         size=13, ha='center', weight='bold')
    steps = [
        ('单体构建', 'PSMILES → 三维结构', 'blue'),
        ('聚合建模', '链长 · 序列 · 立构规整度', 'blue'),
        ('无定形盒子构建', '周期胞 · 低初始密度', 'blue'),
        ('能量最小化', '消除原子重叠', 'green'),
        ('NVT 平衡', '500–600 K · 固定体积', 'green'),
        ('NPT 平衡', '密度收敛到平台', 'green'),
        ('高温退火', '消除制备历史', 'orange'),
        ('降温采样', '固定速率 · 记录比容', 'orange'),
        ('Tg 提取', '比容–温度双线性拟合', 'orange'),
    ]
    x, w, h, step = 0.06, 0.32, 0.064, 0.092
    y0 = 0.885
    for i, (name, note, color) in enumerate(steps):
        y = y0 - i * step
        box(ax, x, y - h, w, h, '', color)
        text(ax, x + 0.015, y - h / 2, name, size=11)
        text(ax, x + w + 0.03, y - h / 2, note, size=11)
        if i:
            arrow(ax, (x + 0.05, y + step - h), (x + 0.05, y))
    arrow(ax, (0.028, y0 - 5 * step - h / 2), (0.028, y0 - 4 * step - h / 2),
          kind='control')
    text(ax, 0.06, 0.02, '顺序不可颠倒；虚线为检查不通过时回到上一步。', size=11)
    exp.save(fig, 'figure-5-4-md-workflow', badge='SCHEMATIC')


def figure_force_fields(exp):
    fig, ax = canvas(height=3.8)
    headers = ['力场', '适用对象', '参数来源']
    rows = [
        ('OPLS-AA', '烃 · 醚 · 酯', '液相热力学'),
        ('GAFF', '通用有机物', 'HF / RESP'),
        ('COMPASS', '聚合物 · 无机', '从头算 + 交叉项'),
        ('PCFF', '交联 · 界面', '从头算 + 交叉项'),
        ('CHARMM', '极性 · 离子', '生物大分子'),
    ]
    D.table(ax, headers, rows, y_top=0.78, row_h=0.115,
            col_x=[0.14, 0.45, 0.76])
    text(ax, 0.5, 0.93, '经典力场家族与适用对象', size=13, ha='center', weight='bold')
    text(ax, 0.06, 0.06, '五个家族按参数来源与覆盖的化学空间排列。',
         size=11)
    exp.save(fig, 'figure-5-5-force-fields', badge='LIT')


def figure_coarse_graining(exp):
    fig, ax = canvas(height=3.9)
    text(ax, 0.5, 0.95, '粗粒化：映射与四条参数化路线',
         size=13, ha='center', weight='bold')
    box(ax, 0.06, 0.74, 0.20, 0.10, '原子 · m 个', 'blue', size=11)
    arrow(ax, (0.26, 0.79), (0.36, 0.79))
    box(ax, 0.36, 0.74, 0.20, 0.10, '珠子 · 1 个', 'green', size=11)
    text(ax, 0.06, 0.62, '映射比 m 越大，可达尺度越大、有效势可迁移性越差。', size=11)
    routes = ['MARTINI', 'IBI', '力匹配', '相对熵']
    notes = ['预设珠子类型', '匹配 g(r)', '匹配全原子力', '匹配分布']
    D.spectrum(ax, routes, y=0.40, h=0.14, color='orange', gap=0.02)
    n = len(routes)
    x0, x1, gap = 0.04, 0.96, 0.02
    w = (x1 - x0 - gap * (n - 1)) / n
    for i, note in enumerate(notes):
        cx = x0 + i * (w + gap) + w / 2
        text(ax, cx, 0.14, note, size=11, ha='center')
    text(ax, 0.04, 0.04, '四条路线按匹配对象区分：结构、力、分布与预设参数。', size=11)
    exp.save(fig, 'figure-5-6-coarse-graining', badge='LIT')


def figure_mlip_lineage(exp):
    fig, ax = plot(height=4.0, left=.28, bottom=.22)
    ax.set_xscale('log')
    ax.grid(True, which='major', color=COL['gray'], lw=.7, zorder=0)
    groups = [
        ('局部势', 1e3, 1.0, 'blue'),
        ('等变势', 1e4, 1.7, 'green'),
        ('通用势', 1e5, 2.6, 'orange'),
        ('基础势', 1e6, 3.3, 'purple'),
    ]
    for label, x, y, color in groups:
        ax.scatter([x], [y], s=160, facecolor=COL[color],
                   edgecolor=COL['line'], linewidth=1, zorder=4)
        ax.text(x, y + 0.36, label, size=11, ha='center', weight='bold', zorder=5)
    ax.set_xlim(1e2, 1e8)
    ax.set_ylim(0.4, 3.8)
    ax.set_yticks([1, 2, 3])
    ax.set_yticklabels(['单一体系', '单一化学家族', '跨材料'])
    ax.set_xlabel('训练数据规模（构象数，对数轴）')
    ax.set_ylabel('泛化范围')
    exp.save(fig, 'figure-5-7-mlip-lineage', badge='LIT')


def figure_mlff_boundary(exp):
    fig, ax = canvas(height=4.0)
    text(ax, 0.5, 0.95, '机器学习势的适用边界', size=13, ha='center', weight='bold')
    x0, y0, w, h = 0.24, 0.16, 0.34, 0.30
    cells = [
        (0, 0, 'gray', '不可用', '化学与构象均不足'),
        (1, 0, 'orange', '补化学数据', '构象覆盖、化学不足'),
        (0, 1, 'orange', '补构象数据', '化学覆盖、构象不足'),
        (1, 1, 'green', '适合直接用', '化学与构象均覆盖'),
    ]
    for cx, cy, color, label, note in cells:
        x = x0 + cx * w
        y = y0 + cy * h
        ax.add_patch(Rectangle((x, y), w, h, facecolor=COL[color],
                               edgecolor=COL['line'], linewidth=.9))
        text(ax, x + w / 2, y + h / 2 + 0.035, label, size=12, ha='center',
             weight='bold')
        text(ax, x + w / 2, y + h / 2 - 0.045, note, size=11, ha='center')
    ax.annotate('', xy=(x0 + 2 * w + 0.06, y0 - 0.03), xytext=(x0, y0 - 0.03),
                arrowprops=dict(arrowstyle='-|>', color=COL['line'], lw=1))
    text(ax, x0 + w, y0 - 0.07, '构象覆盖：低 → 高', size=11, ha='center')
    ax.annotate('', xy=(x0 - 0.04, y0 + 2 * h + 0.04), xytext=(x0 - 0.04, y0),
                arrowprops=dict(arrowstyle='-|>', color=COL['line'], lw=1))
    text(ax, x0 - 0.06, y0 + h, '化学覆盖：低 → 高', size=11, ha='center',
         rotation=90)
    exp.save(fig, 'figure-5-8-mlff-boundary', badge='SCHEMATIC')


def figure_enhanced_sampling(exp):
    fig, ax = canvas(height=3.9)
    text(ax, 0.5, 0.95, '增强采样：三种方法', size=13, ha='center', weight='bold')
    centers = [0.19, 0.50, 0.81]
    for cx, panel, title in zip(centers, ['(a)', '(b)', '(c)'],
                                ['伞形采样', '元动力学', '副本交换']):
        text(ax, cx, 0.93, panel, size=12, ha='center', weight='bold')
        text(ax, cx, 0.86, title, size=12, ha='center', weight='bold')
    for c in [0.10, 0.19, 0.28]:
        xs = np.linspace(c - 0.05, c + 0.05, 60)
        ax.plot(xs, 0.45 + 6.0 * (xs - c) ** 2, color=COL['line'], lw=1.1, zorder=2)
    ax.plot([0.05, 0.33], [0.45, 0.45], color=COL['gray'], lw=1, zorder=1)
    text(ax, 0.19, 0.72, '窗口拼接 → PMF', size=11, ha='center')
    xs = np.linspace(0.39, 0.61, 120)
    for c, amp in [(0.44, 0.10), (0.50, 0.15), (0.56, 0.10)]:
        ax.plot(xs, 0.45 + amp * np.exp(-((xs - c) / 0.035) ** 2),
                color=COL['line'], lw=1.1, zorder=2)
    ax.plot([0.39, 0.61], [0.45, 0.45], color=COL['gray'], lw=1, zorder=1)
    text(ax, 0.50, 0.72, '累积偏置 → F(s)', size=11, ha='center')
    for y, lab in [(0.42, 'T1'), (0.54, 'T2'), (0.66, 'T3')]:
        ax.plot([0.70, 0.92], [y, y], color=COL['line'], lw=1.2)
        text(ax, 0.935, y, lab, size=11)
    arrow(ax, (0.80, 0.43), (0.80, 0.53), kind='control')
    arrow(ax, (0.86, 0.55), (0.86, 0.65), kind='control')
    text(ax, 0.81, 0.76, '构型交换', size=11, ha='center')
    for cx, note in zip(centers, ['一维反应坐标', '多盆地探索', '温度驱动转变']):
        text(ax, cx, 0.12, note, size=11, ha='center')
    exp.save(fig, 'figure-5-9-enhanced-sampling', badge='SCHEMATIC')


def figure_worked_cost(exp):
    ff_seconds = 55 * 0.090
    dft_seconds = 100 * dft['summary']['gpu_seconds']
    mlff_seconds = 55 * mlff['summary']['gpu_seconds']
    labels = ['经典力场 MD', 'DFT 参数化', '机器学习势 MD']
    values = [ff_seconds, dft_seconds, mlff_seconds]
    colors = [COL['green'], COL['orange'], COL['purple']]
    fig, ax = plot(height=3.6, left=.30, bottom=.22)
    ypos = [2, 1, 0]
    ax.barh(ypos, values, color=colors, edgecolor=COL['line'], linewidth=.9)
    ax.set_yticks(ypos)
    ax.set_yticklabels(labels)
    ax.set_xscale('log')
    ax.set_xlim(1, 3e5)
    ax.set_xlabel('理论估算（GPU·秒，对数轴）')
    for y, value in zip(ypos, values):
        ax.text(value * 1.4, y, f'{value:.3g}', size=11, va='center')
    exp.save(fig, 'figure-5-10-worked-cost', badge='CALC')


def figure_selection_guide(exp):
    fig, ax = canvas(height=4.4)
    text(ax, 0.5, 0.96, '模拟方法选型决策路径', size=13, ha='center', weight='bold')
    steps = ['目标尺度与精度需求', '映射表筛选方法', '代价模型核算',
             '数据与参数检查', '平衡与收敛检查', '复现清单']
    x, w, h, step = 0.06, 0.42, 0.085, 0.135
    y0 = 0.86
    for i, label in enumerate(steps):
        y = y0 - i * step
        box(ax, x, y - h, w, h, label, 'blue' if i < 3 else 'green', size=11)
        if i:
            arrow(ax, (x + 0.07, y + step - h), (x + 0.07, y))
    box(ax, 0.58, 0.34, 0.38, 0.40, '', 'orange')
    text(ax, 0.77, 0.69, '三种换方法信号', size=11, ha='center', weight='bold')
    for j, note in enumerate(['漂移：采样不足', '波动：参数未覆盖', '预算失效：重新标定']):
        text(ax, 0.60, 0.60 - j * 0.08, note, size=11)
    arrow(ax, (0.58, 0.54), (0.48, 0.47), kind='control')
    text(ax, 0.06, 0.04, '决策路径依次经过六个步骤；右侧三个信号触发回到相应步骤。', size=11)
    exp.save(fig, 'figure-5-11-selection-guide', badge='SCHEMATIC')


def main():
    exp = Exporter(HERE)
    figure_multiscale_pyramid(exp)
    figure_accuracy_cost(exp)
    figure_trajectory(exp)
    figure_md_workflow(exp)
    figure_force_fields(exp)
    figure_coarse_graining(exp)
    figure_mlip_lineage(exp)
    figure_mlff_boundary(exp)
    figure_enhanced_sampling(exp)
    figure_worked_cost(exp)
    figure_selection_guide(exp)
    exp.finish()
    index = [
        {'figure': '5-1', 'asset': 'ch05/figure-5-1-multiscale-pyramid.svg'},
        {'figure': '5-2', 'asset': 'ch05/figure-5-2-accuracy-cost.svg'},
        {'figure': '5-3', 'asset': 'ch05/figure-5-3-trajectory.svg'},
        {'figure': '5-4', 'asset': 'ch05/figure-5-4-md-workflow.svg'},
        {'figure': '5-5', 'asset': 'ch05/figure-5-5-force-fields.svg'},
        {'figure': '5-6', 'asset': 'ch05/figure-5-6-coarse-graining.svg'},
        {'figure': '5-7', 'asset': 'ch05/figure-5-7-mlip-lineage.svg'},
        {'figure': '5-8', 'asset': 'ch05/figure-5-8-mlff-boundary.svg'},
        {'figure': '5-9', 'asset': 'ch05/figure-5-9-enhanced-sampling.svg'},
        {'figure': '5-10', 'asset': 'ch05/figure-5-10-worked-cost.svg'},
        {'figure': '5-11', 'asset': 'ch05/figure-5-11-selection-guide.svg'},
    ]
    (HERE / 'figure-index.json').write_text(
        json.dumps(index, ensure_ascii=False, indent=2) + '\n')
    for record in exp.checks:
        print(f"{record['figure']}: min label {record['min_label_pt']:.0f} pt, "
              f"{len(record['text_extent_warnings'])} warnings")


if __name__ == '__main__':
    main()
