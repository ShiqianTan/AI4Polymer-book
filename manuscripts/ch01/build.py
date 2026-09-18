#!/usr/bin/env python3
"""Build chapter-one teaching figures from fixed book evidence.

Usage: python manuscripts/ch01/build.py [--font /path/to/CJK-font.ttf]
"""
from pathlib import Path
import argparse
import hashlib
import json
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE.parent))

from matplotlib.patches import Circle, FancyArrowPatch, Rectangle

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

years = json.loads((ROOT / 'research/2026-wos-survey/wos-summary.json').read_text())['years']
case1 = json.loads((ROOT / 'experiments/ch16/flagship/results/summary.json').read_text())
case2 = json.loads((ROOT / 'experiments/ch16/case2/results/summary.json').read_text())
case3 = json.loads((ROOT / 'experiments/ch16/case3/results/summary.json').read_text())

LAYERS = [
    ('表示', '链结构与序列的机器可读表示', '第 2 章', 'blue'),
    ('数据', '实验、模拟与文献样本', '第 3–4 章', 'green'),
    ('模型', '性质预测与物理约束', '第 5–8 章', 'orange'),
    ('优化', '生成、逆向设计与序贯决策', '第 9–12 章', 'purple'),
    ('闭环', '自动化实验与数据回流', '第 13–16 章', 'gray'),
]

PARTS = [
    ('第一部分', ['表示、数据', '与物理基础'], 'blue', [
        ['1 初识'], ['2 表示与', '描述符'], ['3 数据与', '基准'], ['4 物理与', '结构性能']]),
    ('第二部分', ['计算与预测', ''], 'green', [
        ['5 分子模拟'], ['6 性质预测'], ['7 迁移与', '物理信息'], ['8 表征与', '光谱']]),
    ('第三部分', ['生成、优化', '与合成'], 'orange', [
        ['9 生成与', '序列设计'], ['10 逆向', '设计'], ['11 主动', '学习'], ['12 反应与', '可合成性']]),
    ('第四部分', ['闭环系统', '与落地'], 'purple', [
        ['13 自驱动', '实验室'], ['14 基础模型', '与智能体'], ['15 可持续', '高分子'], ['16 端到端', '案例']]),
]


def figure_panorama(exp):
    fig, ax = canvas(height=3.6)
    y0, step, h = 0.10, 0.155, 0.12
    for i, (name, desc, tag, color) in enumerate(LAYERS):
        y = y0 + i * step
        box(ax, 0.06, y, 0.80, h, '', color)
        text(ax, 0.125, y + h / 2, name, size=13, ha='center', weight='bold')
        text(ax, 0.21, y + h / 2, desc, size=11)
        text(ax, 0.83, y + h / 2, tag, size=11, ha='right')
        if i:
            arrow(ax, (0.46, y - (step - h)), (0.46, y))
    ax.plot([0.86, 0.895], [0.78, 0.78], color=COL['line'], lw=1)
    ax.plot([0.86, 0.895], [0.315, 0.315], color=COL['line'], lw=1)
    arrow(ax, (0.895, 0.78), (0.895, 0.315), kind='control')
    text(ax, 0.95, 0.548, '实验结果回流', size=11, rotation=90, ha='center')
    exp.save(fig, 'figure-1-1-panorama', badge='SCHEMATIC')


def figure_publications(exp):
    xs = list(range(2010, 2026))
    vals = [years[str(y)] for y in xs]
    v26 = years['2026']
    fig, ax = plot(height=3.0, left=.13, bottom=.21)
    ax.bar(xs, vals, width=.62, color=COL['blue'], edgecolor=COL['line'],
           linewidth=.7, zorder=2)
    ax.bar([2026], [v26], width=.62, facecolor='white', edgecolor=COL['blue'],
           linewidth=1.4, hatch='///', zorder=2)
    ax.plot(xs, vals, color=COL['line'], lw=1.4, marker='o', ms=3.5,
            mfc=COL['line'], mec=COL['line'], zorder=3)
    ax.set_xlim(2009.4, 2026.9)
    ax.set_ylim(0, 820)
    ax.set_xticks([2010, 2013, 2016, 2019, 2022, 2025])
    ax.set_xlabel('年份')
    ax.set_ylabel('年发文量（条）')
    ax.text(2010.0, 70, '2010 年 26 条', size=11)
    ax.annotate('2019 年后加速', xy=(2019.1, 95), xytext=(2012.6, 300), size=11,
                arrowprops=dict(arrowstyle='-', color=COL['line'], lw=.9))
    ax.annotate('2025 年 699 条', xy=(2025, 699), xytext=(2013.4, 560), size=11,
                arrowprops=dict(arrowstyle='-', color=COL['line'], lw=.9))
    ax.annotate('2026 截至 9 月', xy=(2026, v26), xytext=(2022.4, 170), size=11,
                ha='right', arrowprops=dict(arrowstyle='-', color=COL['line'], lw=.9))
    exp.save(fig, 'figure-1-2-publications', badge='LIT')


def figure_roadmap(exp):
    fig, ax = canvas(height=4.2)
    band_h, step = 0.19, 0.235
    base = 0.07
    for i, (label, name_lines, color, chapters) in enumerate(PARTS):
        y = base + (len(PARTS) - 1 - i) * step
        ax.add_patch(Rectangle((0.03, y), 0.955, band_h, facecolor=COL[color],
                               edgecolor=COL['line'], linewidth=.6))
        text(ax, 0.045, y + 0.148, label, size=13, weight='bold')
        for j, line in enumerate(name_lines):
            if line:
                text(ax, 0.045, y + 0.096 - j * 0.052, line, size=12)
        for k, lines in enumerate(chapters):
            x = 0.205 + k * 0.198
            box(ax, x, y + 0.0225, 0.188, 0.145, '\n'.join(lines),
                color='white', size=12, edge=COL[color])
        if i < len(PARTS) - 1:
            arrow(ax, (0.5, y), (0.5, y - (step - band_h)))
    top = base + 3 * step + band_h
    bottom = base
    ax.plot([0.03, 0.012], [top - band_h / 2, top - band_h / 2], color=COL['line'], lw=1)
    ax.plot([0.03, 0.012], [bottom + band_h / 2, bottom + band_h / 2], color=COL['line'], lw=1)
    arrow(ax, (0.012, bottom + band_h / 2), (0.012, top - band_h / 2), kind='control')
    text(ax, 0.5, 0.030, '闭环：实验结果回流到数据层', size=12, ha='center')
    exp.save(fig, 'figure-1-3-roadmap', badge='SCHEMATIC')


def figure_difference(exp):
    fig, ax = canvas(height=3.4)
    text(ax, 0.04, 0.905, '(a)', size=12, weight='bold')
    box(ax, 0.06, 0.70, 0.18, 0.13, '分子式', 'blue')
    arrow(ax, (0.24, 0.765), (0.44, 0.765))
    box(ax, 0.44, 0.70, 0.18, 0.13, '性质', 'green')
    text(ax, 0.66, 0.765, '一个结构对应一个标签', size=11)
    ax.plot([0.04, 0.96], [0.60, 0.60], color=COL['gray'], lw=.8)
    text(ax, 0.035, 0.585, '(b)', size=12, weight='bold')
    labels = ['重复单元', '架构', '序列', '分子量分布', '加工', '形貌']
    w, gap, x0 = 0.142, 0.012, 0.035
    for i, label in enumerate(labels):
        box(ax, x0 + i * (w + gap), 0.42, w, 0.13, label, 'orange', size=11)
    arrow(ax, (0.5, 0.42), (0.5, 0.35))
    box(ax, 0.34, 0.21, 0.32, 0.13, '结构状态 x（七元组）', 'purple', size=11)
    arrow(ax, (0.66, 0.275), (0.76, 0.275))
    box(ax, 0.76, 0.21, 0.18, 0.13, '性质', 'green')
    text(ax, 0.5, 0.08, '六个坐标共同影响一个标签；只记其中一个，误差下界由标签歧义锁死',
         size=11, ha='center')
    exp.save(fig, 'figure-1-4-difference', badge='SCHEMATIC')


def figure_timeline(exp):
    fig, ax = canvas(height=3.2)
    x0, x1 = 0.10, 0.96
    lo, hi = 2012.5, 2024.0
    y_mid, y_top, y_bot = 0.49, 0.68, 0.30

    def X(year):
        return x0 + (year - lo) / (hi - lo) * (x1 - x0)

    ax.add_patch(Circle((0.075, 0.945), 0.010, facecolor=COL['blue'],
                        edgecolor=COL['line'], lw=.9, zorder=3))
    text(ax, 0.095, 0.945, '通用 ML / Chemistry 里程碑', size=11)
    ax.add_patch(Circle((0.575, 0.945), 0.010, facecolor=COL['green'],
                        edgecolor=COL['line'], lw=.9, zorder=3))
    text(ax, 0.595, 0.945, '高分子领域采用', size=11)

    ax.plot([x0, x1], [y_mid, y_mid], color=COL['line'], lw=1.0)
    for year in range(2013, 2025, 2):
        ax.plot([X(year), X(year)], [y_mid - 0.018, y_mid + 0.018],
                color=COL['line'], lw=.9)
        text(ax, X(year), y_mid - 0.058, str(year), size=11, ha='center')

    top = [(2013, 'VAE'), (2017, 'GNN'), (2020, '扩散模型'), (2022, 'LLM')]
    bot = [(2018, 'Polymer Genome'), (2020, '生成设计'),
           (2022, '自主实验室'), (2023, 'polyBERT')]
    for i, (year, name) in enumerate(top):
        x = X(year)
        dy = 0.078 if i % 2 == 0 else 0.158
        ax.add_patch(Circle((x, y_top), 0.010, facecolor=COL['blue'],
                            edgecolor=COL['line'], lw=.9, zorder=3))
        ax.plot([x, x], [y_top, y_top + dy - 0.022], color=COL['line'], lw=.9)
        text(ax, x, y_top + dy, f'{year}  {name}', size=11,
             ha='left' if x < 0.5 else 'right')
    for i, (year, name) in enumerate(bot):
        x = X(year)
        dy = 0.078 if i % 2 == 0 else 0.158
        ax.add_patch(Circle((x, y_bot), 0.010, facecolor=COL['green'],
                            edgecolor=COL['line'], lw=.9, zorder=3))
        ax.plot([x, x], [y_bot, y_bot - dy + 0.022], color=COL['line'], lw=.9)
        text(ax, x, y_bot - dy, f'{year}  {name}', size=11,
             ha='left' if x < 0.5 else 'right')
    exp.save(fig, 'figure-1-5-timeline', badge='LIT')


def figure_tasks(exp):
    fig, ax = canvas(height=3.7)
    rows = [
        ['性质预测', '由结构预测性质', '结构 → 数值', '第 6–7 章'],
        ['逆向设计', '由性质反推结构', '目标 → 候选', '第 9–10 章'],
        ['配方优化', '多组分比例寻优', '配方 → 性能', '第 10–11 章'],
        ['合成与工艺优化', '让候选做得出', '路线/条件 → 产率', '第 12 章'],
        ['自主发现', '闭环搜索新体系', '需求 → 实测', '第 13–14 章'],
    ]
    D.table(ax, ['任务', '目标', '输入 → 输出', '对应章节'], rows,
            y_top=0.84, row_h=0.132, col_x=[0.14, 0.38, 0.66, 0.89])
    text(ax, 0.5, 0.035, '五类任务共享表示、数据与模型，但目标与搜索方式不同',
         size=11, ha='center')
    exp.save(fig, 'figure-1-6-tasks', badge='SCHEMATIC')


def figure_cases(exp):
    fig, ax = canvas(height=3.4)
    mae1 = case1['models']['main']['mae']
    mae2 = case2['splits']['epoxide_group']['gradient_boosting']['mae']
    time3 = case3['splits']['time_2000']['gradient_boosting']['mae']
    cases = [
        ('案例一\n高 Tg 透明聚酰亚胺', 'orange', [
            '目标  Tg > 200 °C',
            '约束  可溶液加工',
            '数据  1765 条公开',
            f'结果  MAE {mae1:.1f} K',
            '漏斗  312→74，3 新',
        ]),
        ('案例二\n可回收热固性材料', 'green', [
            '目标  模量约 3 GPa',
            '约束  解聚 < 150 °C',
            '数据  8424 条校准',
            f'结果  MAE {mae2:.1f} K',
            '漏斗  3599→71',
        ]),
        ('案例三\n气体分离膜', 'blue', [
            '目标  α>25，P>100',
            '约束  条件归一化',
            '数据  217 条双气体',
            f'结果  {time3:.3f} dex',
            '漏斗  1124→0',
        ]),
    ]
    for i, (title, color, lines) in enumerate(cases):
        x0 = 0.025 + i * 0.335
        box(ax, x0, 0.74, 0.30, 0.16, title, color, size=11)
        for j, line in enumerate(lines):
            text(ax, x0 + 0.015, 0.63 - j * 0.105, line, size=11)
    text(ax, 0.5, 0.05, '三个案例走同一条链路，卡点分别在透明性标签、解聚标签与高选择性样本',
         size=11, ha='center')
    exp.save(fig, 'figure-1-7-cases', badge='DATA')


def main():
    exp = Exporter(HERE)
    figure_panorama(exp)
    figure_publications(exp)
    figure_roadmap(exp)
    figure_difference(exp)
    figure_timeline(exp)
    figure_tasks(exp)
    figure_cases(exp)
    exp.finish()
    index = [
        {'figure': '1-1', 'asset': 'ch01/figure-1-1-panorama.svg'},
        {'figure': '1-2', 'asset': 'ch01/figure-1-2-publications.svg'},
        {'figure': '1-3', 'asset': 'ch01/figure-1-3-roadmap.svg'},
        {'figure': '1-4', 'asset': 'ch01/figure-1-4-difference.svg'},
        {'figure': '1-5', 'asset': 'ch01/figure-1-5-timeline.svg'},
        {'figure': '1-6', 'asset': 'ch01/figure-1-6-tasks.svg'},
        {'figure': '1-7', 'asset': 'ch01/figure-1-7-cases.svg'},
    ]
    (HERE / 'figure-index.json').write_text(
        json.dumps(index, ensure_ascii=False, indent=2) + '\n')
    for record in exp.checks:
        print(f"{record['figure']}: min label {record['min_label_pt']:.0f} pt, "
              f"{len(record['text_extent_warnings'])} warnings")


if __name__ == '__main__':
    main()
