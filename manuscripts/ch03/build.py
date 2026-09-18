#!/usr/bin/env python3
"""Build chapter-three data, benchmark and reproducibility teaching figures.

Usage: python manuscripts/ch03/build.py [--font /path/to/CJK-font.ttf]
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

from matplotlib.patches import Circle

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

SUPER = str.maketrans('0123456789', '⁰¹²³⁴⁵⁶⁷⁸⁹')


def _size_label(value):
    exponent = int(math.floor(math.log10(value)))
    mantissa = value / 10 ** exponent
    return f'{mantissa:.1f}×10{str(exponent).translate(SUPER)}'


def figure_data_sources(exp):
    wos = json.loads((ROOT / 'research/2026-wos-survey/wos-summary.json').read_text())
    cfg = json.loads((ROOT / 'calculations/configs/datasets.json').read_text())
    sizes = {d['id']: d['size'] for d in cfg['datasets']}
    rows = [
        ('文献检索 WoS', wos['meta']['total_records'], 'gray'),
        ('PoLyInfo', sizes['polyinfo'], 'blue'),
        ('POINT2', sizes['point2'], 'green'),
        ('PI1M', sizes['pi1m'], 'orange'),
        ('polyBERT 预训练', sizes['polybert'], 'purple'),
    ]
    fig, ax = plot(height=3.6, left=.28, bottom=.17)
    ys = list(range(len(rows)))
    ax.barh(ys, [r[1] for r in rows], color=[COL[r[2]] for r in rows],
            edgecolor=COL['line'], linewidth=.8, height=.6)
    ax.set_yticks(ys)
    ax.set_yticklabels([r[0] for r in rows])
    ax.set_xscale('log')
    ax.set_xlim(1e3, 3e9)
    ax.set_xticks([1e3, 1e4, 1e5, 1e6, 1e7, 1e8])
    ax.set_xticklabels(['10³', '10⁴', '10⁵', '10⁶', '10⁷', '10⁸'])
    ax.set_xlabel('样本量（条，对数轴）')
    for y, row in zip(ys, rows):
        ax.text(row[1] * 1.3, y, _size_label(row[1]), size=11, va='center')
    ax.text(0.97, 0.05, '预训练语料比实验\n数据库高约 4 个数量级',
            transform=ax.transAxes, ha='right', va='bottom', size=11)
    exp.save(fig, 'figure-3-1-data-sources', badge='LIT')


def figure_learning_curve(exp):
    data = json.loads((ROOT / 'calculations/results/learning-curve-target.json').read_text())
    scenario = data['scenario']
    summary = data['summary']
    mae_inf = scenario['mae_inf']
    a = scenario['a']
    alpha = scenario['alpha']
    target = scenario['target_mae']
    crossing = summary['required_n_experiments']
    curve = summary['curve']
    xs = [10 ** (i / 40) for i in range(0, 201)]
    ys = [mae_inf + a * n ** (-alpha) for n in xs]
    y_cross = mae_inf + a * crossing ** (-alpha)
    fig, ax = plot(height=3.6, left=.17, bottom=.20)
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.plot(xs, ys, color=COL['line'], lw=1.6, zorder=2)
    ax.plot([c['n'] for c in curve], [c['mae'] for c in curve],
            linestyle='none', marker='o', ms=5, mfc=COL['blue'],
            mec=COL['line'], mew=1, zorder=3)
    ax.axhline(mae_inf, color=COL['gray'], lw=1.1, zorder=1)
    ax.axhline(target, color=COL['gray'], lw=1, ls=':', zorder=1)
    ax.axvline(crossing, color=COL['line'], lw=1, ls='--', zorder=1)
    ax.plot([crossing], [y_cross], marker='o', ms=7, mfc=COL['orange'],
            mec=COL['line'], mew=1, zorder=4)
    ax.set_xlim(1, 1.3e5)
    ax.set_ylim(0.04, 1.5)
    ax.set_xticks([1, 10, 100, 1000, 10000, 100000])
    ax.set_yticks([0.05, 0.1, 0.2, 0.5, 1.0])
    ax.set_yticklabels(['0.05', '0.1', '0.2', '0.5', '1.0'])
    ax.set_xlabel('训练样本数 n')
    ax.set_ylabel('MAE')
    mask = dict(facecolor=COL['white'], edgecolor='none', pad=1.5)
    ax.text(1.15, mae_inf * 1.25, '不可约误差 MAE∞ = 0.05', size=11, bbox=mask)
    ax.text(1.15, target * 1.18, '目标 MAE = 0.2', size=11, bbox=mask)
    ax.annotate(f'{crossing} 个样本达标', xy=(crossing, y_cross),
                xytext=(260, 0.11), size=11,
                arrowprops=dict(arrowstyle='-', color=COL['line'], lw=.9))
    exp.save(fig, 'figure-3-2-learning-curve', badge='CALC')


def _disc(ax, cx, cy, r, color):
    ax.add_patch(Circle((cx, cy), r, facecolor=COL[color], edgecolor=COL['line'],
                        linewidth=.9, alpha=.85))


MATRIX_STATE = {'full': 'blue', 'part': 'orange', 'none': 'gray'}


def _cell(ax, x, y, w, h, state):
    box(ax, x, y, w, h, '', color=MATRIX_STATE[state], edge=COL['line'])


def figure_source_matrix(exp):
    rows = [
        ('PoLyInfo', ['part', 'full', 'full', 'part']),
        ('Polymer Genome', ['part', 'full', 'full', 'part']),
        ('PI1M', ['full', 'none', 'full', 'part']),
        ('开放基因组', ['none', 'full', 'full', 'full']),
        ('POINT2', ['full', 'full', 'full', 'full']),
        ('SMiPoly', ['part', 'none', 'full', 'part']),
        ('文献挖掘', ['part', 'part', 'part', 'part']),
        ('模拟数据', ['full', 'full', 'full', 'full']),
        ('专利', ['full', 'part', 'part', 'part']),
        ('实验 ELN', ['part', 'full', 'full', 'none']),
    ]
    cols = ['规模', '性质', '表示', '可获取']
    fig, ax = canvas(height=4.9)
    x0, cw, gap = 0.30, 0.135, 0.010
    for j, name in enumerate(cols):
        text(ax, x0 + j * cw + cw / 2, 0.935, name, size=11, ha='center')
    top, bottom = 0.885, 0.12
    rh = (top - bottom) / len(rows)
    for i, (name, states) in enumerate(rows):
        y = top - (i + 1) * rh
        text(ax, 0.02, y + rh / 2, name, size=11, ha='left')
        for j, state in enumerate(states):
            _cell(ax, x0 + j * cw + gap / 2, y + 0.006, cw - gap, rh - 0.012, state)
    legend = [('full', '完整'), ('part', '部分'), ('none', '不适用')]
    lx = 0.03
    for state, label in legend:
        box(ax, lx, 0.035, 0.03, 0.035, '', color=MATRIX_STATE[state])
        text(ax, lx + 0.038, 0.052, label, size=11, ha='left')
        lx += 0.115
    text(ax, 0.42, 0.052, '按性质与可获取性筛行。', size=11, ha='left')
    exp.save(fig, 'figure-3-4-source-matrix', badge='DATA')


RED = '#F3C9C4'

RISK_PANELS = [
    ('Direct leakage', '直接泄漏', '禁止', 'target 派生特征\n测试标签参与处理', RED, '-'),
    ('Duplicate contamination', '重复污染', '通常禁止', '同一材料 / 同一测量\n跨 train–test', RED, '-'),
    ('Chemical overlap', '化学重叠', '取决于任务', '相同 scaffold /\nmonomer family', COL['orange'], '--'),
    ('Distribution shift', '分布偏移', '泛化任务', '新单体 / 新年份 /\n新实验室', COL['gray'], ':'),
]


def figure_leakage_types(exp):
    fig, ax = canvas(height=4.6)
    w, h = 0.45, 0.38
    for i, (en, zh, verdict, example, color, ls) in enumerate(RISK_PANELS):
        x = 0.035 + (i % 2) * 0.48
        y = 0.535 - (i // 2) * 0.46
        patch = box(ax, x, y, w, h, '', color='white', edge=COL['line'])
        patch.set_facecolor(color)
        patch.set_linestyle(ls)
        patch.set_linewidth(1.8)
        text(ax, x + 0.025, y + h - 0.055, en, size=12, ha='left', weight='bold')
        text(ax, x + 0.025, y + h - 0.115, zh, size=11, ha='left')
        text(ax, x + 0.025, y + 0.075, example, size=11, ha='left')
        text(ax, x + w - 0.025, y + 0.075, verdict, size=11, ha='right', weight='bold')
    exp.save(fig, 'figure-3-5-leakage-types', badge='SCHEMATIC')


def figure_safe_order(exp):
    fig, ax = canvas(height=3.5)
    text(ax, 0.04, 0.86, '划分前：确定性变换，不估计参数', size=11, ha='left', weight='bold')
    steps = ['结构规范化', '单位换算', '确定性解析']
    for i, label in enumerate(steps):
        box(ax, 0.04 + i * 0.32, 0.62, 0.29, 0.16, label, 'green')
    ax.plot([0.04, 0.96], [0.50, 0.50], color=COL['line'], lw=1.2, ls='--')
    text(ax, 0.5, 0.50, 'split  划分', size=11, ha='center',
         bbox=dict(facecolor=COL['white'], edgecolor='none', pad=1.5))
    text(ax, 0.04, 0.34, '划分后：仅在训练集上拟合', size=11, ha='left', weight='bold')
    fit = ['插补器', '缩放 / PCA', '特征选择', '超参搜索']
    for i, label in enumerate(fit):
        box(ax, 0.04 + i * 0.24, 0.10, 0.21, 0.16, label, 'orange')
    text(ax, 0.96, 0.06, '测试集只 transform，不 fit', size=11, ha='right')
    exp.save(fig, 'figure-3-9-safe-order', badge='SCHEMATIC')


def _dot_panel(ax, cx, cy, w, h, title, clusters, note):
    box(ax, cx - w / 2, cy - h / 2, w, h, '', color='white', edge=COL['line'])
    text(ax, cx, cy + h / 2 + 0.045, title, size=11, ha='center', weight='bold')
    for (dx, dy), color in clusters:
        ax.plot([cx + dx * w], [cy + dy * h], marker='o', ms=5,
                color=COL[color], markeredgecolor=COL['line'], mew=.7,
                linestyle='none', zorder=3)
    text(ax, cx, cy - h / 2 - 0.045, note, size=11, ha='center')


def _cluster(ax, cx, cy, w, h, groups):
    clusters = []
    for gx, gy, color in groups:
        for dx, dy in [(-0.05, -0.04), (0.05, -0.03), (-0.02, 0.05),
                       (0.06, 0.05), (0.0, 0.0)]:
            clusters.append(((gx + dx, gy + dy), color))
    return clusters


def figure_split_strategies(exp):
    fig, ax = canvas(height=3.5)
    xs = [0.10, 0.30, 0.50, 0.70, 0.90]
    random_c = []
    for i in range(20):
        gx = -0.42 + (i % 5) * 0.21
        gy = -0.30 + (i // 5) * 0.20
        random_c.append(((gx, gy), 'blue' if i % 2 else 'orange'))
    scaffold = _cluster(ax, 0, 0, 1, 1, [
        (-0.42, -0.28, 'blue'), (0.0, 0.18, 'blue'), (0.42, -0.12, 'orange')])
    monomer = _cluster(ax, 0, 0, 1, 1, [
        (-0.42, 0.12, 'blue'), (0.42, 0.12, 'orange'), (0.0, -0.30, 'blue')])
    chemistry = _cluster(ax, 0, 0, 1, 1, [
        (-0.30, 0.20, 'blue'), (0.30, 0.20, 'orange'),
        (-0.30, -0.25, 'blue'), (0.30, -0.25, 'blue')])
    time_c = []
    for i in range(18):
        gy = -0.30 + (i % 6) * 0.12
        gx = -0.42 + (i // 6) * 0.42
        time_c.append(((gx, gy), 'orange' if i // 6 == 2 else 'blue'))
    panels = [
        ('随机', random_c, '同分布内插'),
        ('骨架', scaffold, '新骨架外推'),
        ('单体', monomer, '新家族外推'),
        ('化学类', chemistry, '跨类外推'),
        ('时间', time_c, '跨年份外推'),
    ]
    for x, (title, clusters, note) in zip(xs, panels):
        _dot_panel(ax, x, 0.45, 0.17, 0.52, title, clusters, note)
    exp.save(fig, 'figure-3-6-split-strategies', badge='SCHEMATIC')


def figure_leakage_diagnosis(exp):
    data = json.loads((ROOT / 'calculations/results/learning-curve-target.json').read_text())
    mae_inf = data['scenario']['mae_inf']
    a = data['scenario']['a']
    alpha = data['scenario']['alpha']
    xs = [10 ** (i / 40) for i in range(0, 201)]
    ys = [mae_inf + a * n ** (-alpha) for n in xs]
    e_in, e_out = 0.15, 0.20
    n_in, n_out = 100, 45
    fig, ax = plot(height=3.7, left=.17, bottom=.20)
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.plot(xs, ys, color=COL['line'], lw=1.6, zorder=2)
    ax.axhline(e_in, color=COL['gray'], lw=1, ls=':', zorder=1)
    ax.axhline(e_out, color=COL['gray'], lw=1, ls=':', zorder=1)
    ax.plot([n_in], [e_in], marker='o', ms=7, mfc=COL['blue'],
            mec=COL['line'], mew=1, zorder=4)
    ax.plot([n_out], [e_out], marker='o', ms=7, mfc=COL['orange'],
            mec=COL['line'], mew=1, zorder=4)
    ax.annotate('', xy=(n_in, e_in), xytext=(n_out, e_in),
                arrowprops=dict(arrowstyle='<->', color=COL['line'], lw=1))
    ax.set_xlim(1, 1.3e4)
    ax.set_ylim(0.04, 1.5)
    ax.set_xticks([1, 10, 100, 1000, 10000])
    ax.set_yticks([0.05, 0.1, 0.2, 0.5, 1.0])
    ax.set_yticklabels(['0.05', '0.1', '0.2', '0.5', '1.0'])
    ax.set_xlabel('训练样本数 n')
    ax.set_ylabel('MAE')
    mask = dict(facecolor=COL['white'], edgecolor='none', pad=1.5)
    ax.text(1.15, e_in * 1.16, '随机划分 0.15 → n=100', size=11, bbox=mask)
    ax.text(1.15, e_out * 1.16, '分组划分 0.20 → n=45', size=11, bbox=mask)
    ax.text(8, 0.42, '膨胀因子 f = 2.25', size=11, bbox=mask)
    exp.save(fig, 'figure-3-7-leakage-diagnosis', badge='CALC')


def figure_archival_levels(exp):
    fig, ax = canvas(height=3.7)
    levels = [
        ('已归档', '原件 + 哈希 + 文本', '可引具体数字', 'green'),
        ('已核实但不可归档', '记录日期与定位', '只作领域定位', 'orange'),
        ('待核实', '规模与规范未核实', '不引具体数字', 'gray'),
    ]
    for i, (title, mid, note, color) in enumerate(levels):
        y = 0.78 - i * 0.23
        box(ax, 0.04, y - 0.10, 0.44, 0.20, '', color=color)
        text(ax, 0.06, y + 0.055, title, size=11, ha='left', weight='bold')
        text(ax, 0.06, y - 0.005, mid, size=11, ha='left')
        text(ax, 0.06, y - 0.065, note, size=11, ha='left')
        arrow(ax, (0.49, y), (0.60, y))
    box(ax, 0.60, 0.30, 0.36, 0.52, '', color='white', edge=COL['line'])
    text(ax, 0.78, 0.72, '结果绑定', size=11, ha='center', weight='bold')
    text(ax, 0.78, 0.62, r'(D, C, E, s)', size=11, ha='center')
    text(ax, 0.78, 0.52, '数据版本 D', size=11, ha='center')
    text(ax, 0.78, 0.44, '代码版本 C', size=11, ha='center')
    text(ax, 0.78, 0.36, '环境 E 与种子 s', size=11, ha='center')
    exp.save(fig, 'figure-3-8-archival-levels', badge='SCHEMATIC')


def figure_data_leakage(exp):
    fig, ax = canvas(height=3.6)
    text(ax, 0.27, 0.92, '随机划分', size=13, ha='center', weight='bold')
    text(ax, 0.73, 0.92, '分组划分', size=13, ha='center', weight='bold')
    _disc(ax, 0.19, 0.55, 0.13, 'blue')
    _disc(ax, 0.37, 0.55, 0.13, 'orange')
    text(ax, 0.19, 0.74, '训练集', size=11, ha='center')
    text(ax, 0.37, 0.74, '测试集', size=11, ha='center')
    text(ax, 0.28, 0.55, '同系物\n重叠', size=11, ha='center')
    text(ax, 0.28, 0.33, '同系物同时落入两侧', size=11, ha='center')
    _disc(ax, 0.60, 0.55, 0.13, 'blue')
    _disc(ax, 0.86, 0.55, 0.13, 'orange')
    text(ax, 0.60, 0.74, '训练集', size=11, ha='center')
    text(ax, 0.86, 0.74, '测试集', size=11, ha='center')
    text(ax, 0.73, 0.55, '重叠 0', size=11, ha='center', weight='bold')
    text(ax, 0.73, 0.33, '同一单体家族整体归到一侧', size=11, ha='center')
    text(ax, 0.5, 0.12, '随机划分低估测试误差；分组划分使重叠为零。',
         size=11, ha='center')
    exp.save(fig, 'figure-3-3-data-leakage', badge='SCHEMATIC')


def main():
    exp = Exporter(HERE)
    figure_data_sources(exp)
    figure_learning_curve(exp)
    figure_data_leakage(exp)
    figure_source_matrix(exp)
    figure_leakage_types(exp)
    figure_split_strategies(exp)
    figure_leakage_diagnosis(exp)
    figure_archival_levels(exp)
    figure_safe_order(exp)
    exp.finish()
    index = [
        {'figure': '3-1', 'asset': 'ch03/figure-3-1-data-sources.svg'},
        {'figure': '3-2', 'asset': 'ch03/figure-3-2-learning-curve.svg'},
        {'figure': '3-3', 'asset': 'ch03/figure-3-3-data-leakage.svg'},
        {'figure': '3-4', 'asset': 'ch03/figure-3-4-source-matrix.svg'},
        {'figure': '3-9', 'asset': 'ch03/figure-3-9-safe-order.svg'},
        {'figure': '3-5', 'asset': 'ch03/figure-3-5-leakage-types.svg'},
        {'figure': '3-6', 'asset': 'ch03/figure-3-6-split-strategies.svg'},
        {'figure': '3-7', 'asset': 'ch03/figure-3-7-leakage-diagnosis.svg'},
        {'figure': '3-8', 'asset': 'ch03/figure-3-8-archival-levels.svg'},
    ]
    (HERE / 'figure-index.json').write_text(
        json.dumps(index, ensure_ascii=False, indent=2) + '\n')
    for record in exp.checks:
        print(f"{record['figure']}: min label {record['min_label_pt']:.0f} pt, "
              f"{len(record['text_extent_warnings'])} warnings")


if __name__ == '__main__':
    main()
