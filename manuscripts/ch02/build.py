#!/usr/bin/env python3
"""Build chapter-two representation and descriptor teaching figures.

Usage: python manuscripts/ch02/build.py [--font /path/to/CJK-font.ttf]
"""
from pathlib import Path
import argparse
import hashlib
import json
import math
import sys

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

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


def figure_representation_tradeoff(exp):
    fig, ax = canvas(height=4.3)
    cols = ['局部化学', '拓扑', '序列', '系综 / 分布', '形貌']
    reps = ['指纹 · 描述符', '分子图', '字符串 · 序列', '构象系综', '形貌场']
    rows = ['无损性', '可解释性', '计算代价', '定长', '三维感知']
    vals = [
        [1, 3, 3, 3, 2],
        [3, 2, 1, 1, 2],
        [1, 2, 1, 3, 3],
        [3, 1, 1, 1, 1],
        [1, 1, 1, 3, 3],
    ]
    level = {3: '高', 2: '中', 1: '低'}
    shade = {3: 'blue', 2: 'green', 1: 'gray'}
    x0, x1 = 0.30, 0.985
    y_top, y_bot = 0.78, 0.15
    cw = (x1 - x0) / len(cols)
    ch = (y_top - y_bot) / len(rows)
    for c, name in enumerate(cols):
        text(ax, x0 + (c + 0.5) * cw, 0.87, name, size=12, ha='center', weight='bold')
    for c, name in enumerate(reps):
        text(ax, x0 + (c + 0.5) * cw, 0.815, name, size=11, ha='center')
    for r, name in enumerate(rows):
        y = y_top - (r + 1) * ch
        text(ax, x0 - 0.015, y + ch / 2, name, size=11, ha='right')
        for c in range(len(cols)):
            v = vals[r][c]
            ax.add_patch(Rectangle((x0 + c * cw + 0.004, y + 0.004),
                                   cw - 0.008, ch - 0.008,
                                   facecolor=COL[shade[v]],
                                   edgecolor=COL['line'], linewidth=.6))
            text(ax, x0 + (c + 0.5) * cw, y + ch / 2, level[v], size=11, ha='center')
    text(ax, 0.5, 0.965, '表示对象与表示特点的取舍面', size=13, ha='center', weight='bold')
    text(ax, 0.5, 0.075,
         '横轴是表示对象，纵轴是表示特点；「计算代价」行中高 = 更贵。\n'
         '各列各有短板，没有占优列：这是 Pareto 取舍面，不是排行榜。',
         size=11, ha='center')
    exp.save(fig, 'figure-2-1-representation-spectrum', badge='SCHEMATIC')


def figure_fingerprint_information_loss(exp):
    fig, ax = canvas(height=4.0)
    box(ax, 0.04, 0.60, 0.43, 0.22, '', 'green')
    text(ax, 0.075, 0.755, 'ECFP 编码', size=12, weight='bold')
    text(ax, 0.075, 0.695, '半径 r 内的局部子结构：', size=11)
    text(ax, 0.075, 0.645, '原子环境 · 官能团邻域', size=11)
    box(ax, 0.53, 0.60, 0.43, 0.22, '', 'orange')
    text(ax, 0.565, 0.755, 'ECFP 未显式编码（主因）', size=12, weight='bold')
    text(ax, 0.565, 0.695, '序列长程排列 · 分子量分布', size=11)
    text(ax, 0.565, 0.645, '链拓扑 · 加工历史', size=11)
    text(ax, 0.5, 0.94, 'ECFP 的信息损失来源', size=13, ha='center', weight='bold')
    text(ax, 0.5, 0.885, '主因是表示所编码的语义，其次才是散列折叠的位碰撞', size=11, ha='center')
    nb = 18
    bx0, bx1 = 0.08, 0.92
    bw = (bx1 - bx0) / nb
    setbits = {2, 6, 9, 13, 16}
    for i in range(nb):
        ax.add_patch(Rectangle((bx0 + i * bw, 0.40), bw * 0.88, 0.06,
                               facecolor=COL['blue'] if i in setbits else COL['white'],
                               edgecolor=COL['line'], linewidth=.6))
    text(ax, bx0, 0.49, '折叠到 n 位：置位稀疏、分布有偏', size=11)
    arrow(ax, (0.20, 0.30), (bx0 + 9.44 * bw, 0.40))
    text(ax, 0.20, 0.26, '子结构 A', size=11, ha='center')
    arrow(ax, (0.42, 0.30), (bx0 + 9.44 * bw, 0.40))
    text(ax, 0.42, 0.26, '子结构 B', size=11, ha='center')
    text(ax, 0.60, 0.30, '→ 同一位：折叠位碰撞（次因）', size=11)
    text(ax, 0.08, 0.13,
         '经验诊断量：置位 bit 数分布、稀疏子结构碰撞、重复单元层面的近重复率。\n'
         '这些是经验量，不由均匀独立的生日模型预测。', size=11)
    exp.save(fig, 'figure-2-2-fingerprint-collision', badge='SCHEMATIC')


def figure_representation_interface(exp):
    fig, ax = canvas(height=3.6)
    stages = ['结构\nPSMILES', '规范化\n唯一字符串', '表示\n定长向量', '特征编码', '模型输入']
    notes = [('维度 变长', '无不变性'), ('维度 变长', '书写顺序不变'),
             ('维度 定长', '原子编号不变'), ('维度 d 维', '尺度对齐'),
             ('维度 固定', '由模型决定')]
    D.pipeline(ax, stages, y=0.64, h=0.16, color='blue')
    n = len(stages)
    w = (0.97 - 0.03 - 0.02 * (n - 1)) / n
    for i, (dim, inv) in enumerate(notes):
        cx = 0.03 + i * (w + 0.02) + w / 2
        text(ax, cx, 0.45, dim, size=11, ha='center')
        text(ax, cx, 0.37, inv, size=11, ha='center')
    text(ax, 0.5, 0.91, '表示到模型的接口', size=13, ha='center', weight='bold')
    text(ax, 0.5, 0.14, '接口处的维度与不变性决定可选模型与代价。', size=11, ha='center')
    exp.save(fig, 'figure-2-3-representation-interface', badge='SCHEMATIC')


def figure_four_layer_objects(exp):
    fig, ax = canvas(height=3.7)
    items = [
        ('化学层', '重复单元 · 端基 · 立构规整度', 'PSMILES', 'blue'),
        ('序列层', '均聚 / 无规 / 交替 / 嵌段 / 梯度', 'BigSMILES', 'green'),
        ('分子量层', 'Mn · Mw · D · 分布 P(M)', 'MWD 参数', 'orange'),
        ('架构层', '线性 / 支化 / 星形 / 超支化 / 网络', '拓扑', 'purple'),
    ]
    D.layers(ax, items, x=0.05, w=0.82, y0=0.15, step=0.165, h=0.125,
             name_x=0.115, desc_x=0.20, tag_x=0.84, arrow_x=0.47,
             name_size=12, size=11)
    text(ax, 0.5, 0.94, '高分子的四层表示对象', size=13, ha='center', weight='bold')
    text(ax, 0.05, 0.05, '四层共同决定可预测性；只记其中一层，标签歧义就锁住误差下界。', size=11)
    exp.save(fig, 'figure-2-4-four-layer-objects', badge='SCHEMATIC')


def figure_sequence_types(exp):
    fig, ax = canvas(height=3.6)
    items = ['均聚物', '交替', '两嵌段', '梯度', '接枝', '无规']
    D.spectrum(ax, items, y=0.62, h=0.15, color='blue',
               x0=0.04, x1=0.96, gap=0.014,
               left_label='序列信息量：低', right_label='高')
    n = len(items)
    x0, x1, gap = 0.04, 0.96, 0.014
    w = (x1 - x0 - gap * (n - 1)) / n
    counts = ['10', '90', '8910', '组合', '组合', '10^100']
    for i, count in enumerate(counts):
        cx = x0 + i * (w + gap) + w / 2
        text(ax, cx, 0.30, count, size=11, ha='center')
    text(ax, 0.5, 0.93, '序列类型与序列数', size=13, ha='center', weight='bold')
    text(ax, 0.5, 0.19, '序列数按 N=10、L=100 复算；梯度与接枝由组成与支链长度组合描述。', size=11, ha='center')
    text(ax, 0.5, 0.11, '证据：复算（均聚/交替/嵌段/无规）。', size=11, ha='center')
    exp.save(fig, 'figure-2-5-sequence-types', badge='CALC')


def figure_mwd(exp):
    fig, ax = plot(height=3.6, left=.16, bottom=.21)
    mn = 100.0
    ms = [10 ** (math.log10(5) + i * (math.log10(500) - math.log10(5)) / 240)
          for i in range(241)]
    for dj, color, ls in [(1.5, COL['blue'], '-'), (2.0, COL['green'], '-'),
                          (4.0, COL['orange'], '-')]:
        s2 = math.log(dj)
        s = math.sqrt(s2)
        mu = math.log(mn) - s2 / 2
        w = [math.exp(-((math.log(m) - mu) ** 2) / (2 * s2)) / (m * s)
             for m in ms]
        peak = max(w)
        ax.plot(ms, [x / peak for x in w], color=color, lw=2.2,
                label=f'D = {dj}')
    ax.axvline(mn, color=COL['line'], lw=1, ls='--')
    ax.set_xscale('log')
    ax.set_xlim(5, 500)
    ax.set_ylim(0, 1.15)
    ax.set_xticks([5, 10, 25, 50, 100, 200, 500])
    ax.set_xticklabels(['5', '10', '25', '50', '100', '200', '500'])
    ax.set_xlabel('分子量 M（kg/mol）')
    ax.set_ylabel('重量分布 w(M)（归一化）')
    ax.text(108, 1.02, 'M_n = 100 kg/mol', size=11)
    ax.legend(loc='upper left', frameon=False)
    exp.save(fig, 'figure-2-6-mwd-curve', badge='SCHEMATIC')


def figure_architecture(exp):
    fig, ax = canvas(height=3.4)
    items = ['线性', '支化', '星形', '超支化', '网络']
    notes = ['单链', '长 / 短支链', 'f 条臂', '树枝状', '交联']
    D.spectrum(ax, items, y=0.60, h=0.16, color='purple',
               x0=0.04, x1=0.96, gap=0.02)
    n = len(items)
    x0, x1, gap = 0.04, 0.96, 0.02
    w = (x1 - x0 - gap * (n - 1)) / n
    for i, note in enumerate(notes):
        cx = x0 + i * (w + gap) + w / 2
        text(ax, cx, 0.30, note, size=11, ha='center')
    text(ax, 0.5, 0.93, '链拓扑：从线性到网络', size=13, ha='center', weight='bold')
    text(ax, 0.5, 0.16, '架构决定链段活动性与缠结，与分子量层共同控制流变和力学。', size=11, ha='center')
    exp.save(fig, 'figure-2-7-architecture', badge='SCHEMATIC')


def figure_representation_matrix(exp):
    fig, ax = canvas(height=4.5)
    rows = ['SMILES', 'PSMILES', 'BigSMILES', 'SELFIES', '分子图', '指纹',
            '描述符', '序列表示', '3D 结构', '形貌表示']
    cols = ['化学', '序列', 'MWD', '架构', '3D', '加工']
    full, part, none = 2, 1, 0
    vals = [
        [full, none, none, none, none, none],
        [full, part, none, part, none, none],
        [full, full, part, full, none, none],
        [full, none, none, none, none, none],
        [full, part, none, full, none, none],
        [part, none, none, none, none, none],
        [part, part, part, part, part, part],
        [part, full, none, none, none, none],
        [full, part, none, part, full, part],
        [part, part, part, full, part, full],
    ]
    fills = {full: COL['blue'], part: COL['orange'], none: COL['gray']}
    marks = {full: '全', part: '部', none: '无'}
    x0, x1 = 0.30, 0.985
    y_top, y_bot = 0.855, 0.115
    cw = (x1 - x0) / len(cols)
    ch = (y_top - y_bot) / len(rows)
    for c, name in enumerate(cols):
        text(ax, x0 + (c + 0.5) * cw, 0.885, name, size=11, ha='center', weight='bold')
    for r, name in enumerate(rows):
        y = y_top - (r + 1) * ch
        text(ax, x0 - 0.012, y + ch / 2, name, size=11, ha='right')
        for c in range(len(cols)):
            ax.add_patch(Rectangle((x0 + c * cw + 0.004, y + 0.004),
                                   cw - 0.008, ch - 0.008,
                                   facecolor=fills[vals[r][c]],
                                   edgecolor=COL['line'], linewidth=.6))
            text(ax, x0 + (c + 0.5) * cw, y + ch / 2, marks[vals[r][c]],
                 size=11, ha='center')
    text(ax, 0.5, 0.965, '表示 × 信息维度', size=13, ha='center', weight='bold')
    legend = [('完整保留', full), ('部分保留', part), ('不保留', none)]
    for i, (label, kind) in enumerate(legend):
        lx = 0.30 + i * 0.24
        ax.add_patch(Rectangle((lx, 0.035), 0.03, 0.03,
                               facecolor=fills[kind], edgecolor=COL['line'], linewidth=.6))
        text(ax, lx + 0.04, 0.05, label, size=11)
    exp.save(fig, 'figure-2-8-representation-matrix', badge='SCHEMATIC')


def figure_worked_cost(exp):
    morgan = json.loads((ROOT / 'calculations/results/descriptor-morgan-2048.json').read_text())
    mordred = json.loads((ROOT / 'calculations/results/descriptor-mordred-1826.json').read_text())
    gnn = json.loads((ROOT / 'calculations/results/gnn-forward-4layer.json').read_text())
    ms = morgan['summary']
    md = mordred['summary']
    gs = gnn['summary']
    fig, axes = plt.subplots(1, 2, figsize=(420 / 72, 4.1))
    fig.subplots_adjust(left=.20, right=.97, bottom=.28, top=.86, wspace=.95)
    labels = ['PSMILES', 'Morgan', 'Mordred', '原子图']
    storage = [311, ms['bytes_per_molecule'], md['bytes_per_molecule'], 8080]
    ypos = list(range(len(labels)))[::-1]
    axes[0].barh(ypos, storage, color=[COL['green'], COL['blue'], COL['orange'], COL['purple']],
                 edgecolor=COL['line'], linewidth=.9)
    axes[0].set_yticks(ypos)
    axes[0].set_yticklabels(labels)
    axes[0].set_xscale('log')
    axes[0].set_xlim(80, 1e5)
    axes[0].set_xlabel('每分子存储（B，对数轴）')
    for y, value in zip(ypos, storage):
        axes[0].text(value * 1.2, y, f'{value:g}', size=11, va='center')
    ops = [ms['xor_popcount_word_operations'],
           ms['pairwise_comparison_count'] * md['feature_dim'],
           gs['total_flops'] * ms['library_size'],
           gs['transformer_forward_flops'] * ms['library_size']]
    names = ['指纹比较\n(字操作)', '描述符比较\n(维操作)', 'GNN 前向\n(FLOPs)',
             'Transformer\n(FLOPs)']
    ypos2 = list(range(len(names)))[::-1]
    axes[1].barh(ypos2, ops, color=[COL['blue'], COL['orange'], COL['purple'], COL['green']],
                 edgecolor=COL['line'], linewidth=.9)
    axes[1].set_yticks(ypos2)
    axes[1].set_yticklabels(names)
    axes[1].set_xscale('log')
    axes[1].set_xlim(1e12, 1e17)
    axes[1].set_xlabel('理想操作计数（对数轴）')
    for y, value in zip(ypos2, ops):
        axes[1].text(value * 1.05, y, f'{value:.2e}', size=11, va='center')
    fig.text(0.5, 0.045,
             '三种操作量纲不同，本图只做记账，不用于推算时间比。',
             size=11, ha='center')
    exp.save(fig, 'figure-2-9-worked-cost', badge='CALC')


def main():
    exp = Exporter(HERE)
    figure_representation_tradeoff(exp)
    figure_fingerprint_information_loss(exp)
    figure_representation_interface(exp)
    figure_four_layer_objects(exp)
    figure_sequence_types(exp)
    figure_mwd(exp)
    figure_architecture(exp)
    figure_representation_matrix(exp)
    figure_worked_cost(exp)
    exp.finish()
    index = [
        {'figure': '2-1', 'asset': 'ch02/figure-2-1-representation-spectrum.svg'},
        {'figure': '2-2', 'asset': 'ch02/figure-2-2-fingerprint-collision.svg'},
        {'figure': '2-3', 'asset': 'ch02/figure-2-3-representation-interface.svg'},
        {'figure': '2-4', 'asset': 'ch02/figure-2-4-four-layer-objects.svg'},
        {'figure': '2-5', 'asset': 'ch02/figure-2-5-sequence-types.svg'},
        {'figure': '2-6', 'asset': 'ch02/figure-2-6-mwd-curve.svg'},
        {'figure': '2-7', 'asset': 'ch02/figure-2-7-architecture.svg'},
        {'figure': '2-8', 'asset': 'ch02/figure-2-8-representation-matrix.svg'},
        {'figure': '2-9', 'asset': 'ch02/figure-2-9-worked-cost.svg'},
    ]
    (HERE / 'figure-index.json').write_text(
        json.dumps(index, ensure_ascii=False, indent=2) + '\n')
    for record in exp.checks:
        print(f"{record['figure']}: min label {record['min_label_pt']:.0f} pt, "
              f"{len(record['text_extent_warnings'])} warnings")


if __name__ == '__main__':
    main()
