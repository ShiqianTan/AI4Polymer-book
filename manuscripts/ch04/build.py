#!/usr/bin/env python3
"""Build chapter-four polymer physics structure-property teaching figures.

Usage: python manuscripts/ch04/build.py [--font /path/to/CJK-font.ttf]
"""
from pathlib import Path
import argparse
import hashlib
import json
import math
import sys

import matplotlib.pyplot as plt
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


def figure_structure_property_map(exp):
    fig, ax = canvas(height=4.2)
    boxes = [
        ('化学组成', 'blue'),
        ('链结构', 'blue'),
        ('分子量分布\n与序列', 'purple'),
        ('形貌', 'purple'),
        ('加工\n与状态', 'green'),
        ('性能', 'green'),
    ]
    x0, w, gap, y, h = 0.035, 0.135, 0.02, 0.63, 0.15
    centers = []
    for i, (label, color) in enumerate(boxes):
        x = x0 + i * (w + gap)
        box(ax, x, y, w, h, label, color, size=11)
        centers.append(x + w / 2)
    access = ['可直接编码', '需模拟', '需模拟', '需实验测量', '需实验测量']
    reps = ['结构式', '重复单元', '$M_n, M_w$', '结晶度', '加工历史', '标签']
    for i in range(len(boxes) - 1):
        x = x0 + i * (w + gap)
        arrow(ax, (x + w, y + h / 2), (x + w + gap, y + h / 2))
        text(ax, x + w + gap / 2, y - 0.10, access[i], size=11, ha='center')
    for cx, rep in zip(centers, reps):
        text(ax, cx, y - 0.24, rep, size=11, ha='center')
    text(ax, 0.5, 0.95, '从化学到性能：结构–性能映射链',
         size=13, ha='center', weight='bold')
    text(ax, 0.035, 0.16,
         '箭头下方标注该环节的获取方式：可直接编码、需模拟或需实验测量。', size=11)
    text(ax, 0.035, 0.06, '方框下方是该环节在表示中对应的量。', size=11)
    exp.save(fig, 'figure-4-1-structure-property-map', badge='SCHEMATIC')


def figure_tg_chain_structure(exp):
    base_plateau, base_k = 400.0, 1.0e5
    stiff_plateau, stiff_k = 480.0, 1.4e5
    plateau_n = base_k / (0.01 * base_plateau)
    mn = [10 ** (3 + 3 * i / 200) for i in range(201)]
    base = [base_plateau - base_k / m for m in mn]
    stiff = [stiff_plateau - stiff_k / m for m in mn]
    fig, ax = plot(height=3.6, left=.16, bottom=.20)
    ax.set_xscale('log')
    ax.fill_between(mn, 280, stiff, color=COL['green'], zorder=1)
    ax.fill_between(mn, 280, base, color=COL['blue'], zorder=2)
    ax.plot(mn, stiff, color=COL['line'], lw=1.4, zorder=3)
    ax.plot(mn, base, color=COL['line'], lw=1.6, zorder=4)
    exp_mn = [1e3, 1e4, 1e5]
    ax.plot(exp_mn, [base_plateau - base_k / m for m in exp_mn],
            linestyle='none', marker='o', ms=5, mfc=COL['white'],
            mec=COL['line'], mew=1.2, zorder=5)
    ax.axhline(base_plateau, color=COL['gray'], lw=1, ls='--', zorder=1)
    ax.axvline(plateau_n, color=COL['gray'], lw=1, ls=':', zorder=1)
    ax.plot([plateau_n], [base_plateau - base_k / plateau_n], marker='o', ms=7,
            mfc=COL['orange'], mec=COL['line'], mew=1, zorder=6)
    ax.set_xlim(8e2, 1.2e6)
    ax.set_ylim(280, 510)
    ax.set_xticks([1e3, 1e4, 1e5, 1e6])
    ax.set_xticklabels(['10³', '10⁴', '10⁵', '10⁶'])
    ax.set_xlabel('数均分子量 $M_n$（g/mol）')
    ax.set_ylabel('玻璃化转变温度 $T_g$（K）')
    ax.text(1.3e3, 406, '平台 $T_{g,\\infty}$ = 400 K', size=11)
    ax.annotate(f'$M_n$≈{plateau_n / 1e4:.1f}×10⁴ g/mol\n后进入平台', xy=(plateau_n, 396),
                xytext=(1.6e5, 352), size=11,
                arrowprops=dict(arrowstyle='-', color=COL['line'], lw=.9))
    ax.text(1.2e5, 492, '较刚链（示意）', size=11)
    ax.text(1.25e3, 322, '基准链', size=11)
    ax.text(0.98, 0.05, '示意参数（非拟合）\n$T_{g,\\infty}$=400 K，$K$=10⁵ K·g/mol',
            transform=ax.transAxes, ha='right', va='bottom', size=11)
    exp.save(fig, 'figure-4-2-tg-chain-structure', badge='SCHEMATIC')


def figure_multiscale_structure(exp):
    fig, ax = canvas(height=4.0)
    tiers = [
        ('单体', '控制组成与极性 → $T_g$、介电'),
        ('链段', '控制链刚性 → $T_g$、黏弹性'),
        ('缠结网络', '控制缠结密度 → 模量、强度'),
        ('自由体积与形貌', '控制极化与输运 → 介电、分离'),
    ]
    D.pyramid(ax, tiers, cx=0.32, w_top=0.18, y_top=0.88, h=0.15, gap=0.02,
              widen=0.08, size=11)
    arrow(ax, (0.05, 0.88), (0.05, 0.24))
    text(ax, 0.022, 0.56, '尺度增大', size=11, rotation=90, ha='center')
    text(ax, 0.5, 0.96, '多尺度结构：从单体到自由体积与形貌',
         size=13, ha='center', weight='bold')
    text(ax, 0.04, 0.10, '各尺度结构分别控制不同的宏观性质。', size=11)
    exp.save(fig, 'figure-4-3-multiscale-structure', badge='SCHEMATIC')


def figure_multiscale_property_map(exp):
    fig, ax = canvas(height=4.7)
    items = [
        ('化学键', '~0.1 nm · 10⁻¹⁴ s', '本征刚度、极化率', 'purple'),
        ('重复单元', '0.5–2 nm · 10⁻¹² s', '链刚性、溶解性', 'orange'),
        ('链构象', '1–100 nm · 10⁻⁹ s', '$T_g$、橡胶弹性', 'green'),
        ('缠结', '5–20 nm · 10⁻³ s', '平台模量、黏度', 'blue'),
        ('形貌', '10 nm–100 μm · 10² s', '$T_m$、强度、渗透率', 'orange'),
        ('宏观性质', 'mm–m · 服役尺度', '断裂、击穿、寿命', 'gray'),
    ]
    D.layers(ax, items, x=0.04, w=0.92, y0=0.075, step=0.142, h=0.108,
             name_x=0.11, desc_x=0.20, tag_x=0.95,
             name_size=12, size=11)
    text(ax, 0.5, 0.965, '多尺度结构–性能图：从化学键到宏观性质',
         size=13, ha='center', weight='bold')
    text(ax, 0.04, 0.02, '六个尺度自下而上排列，标注特征长度、特征时间与控制变量。',
         size=11)
    exp.save(fig, 'figure-4-4-multiscale-property-map', badge='SCHEMATIC')


def figure_chain_flexibility(exp):
    fig, ax = canvas(height=4.0)
    items = ['全碳主链', '醚 / 硅氧', '芳环主链', '酰胺 / 棒状']
    D.spectrum(ax, items, y=0.64, h=0.15, color='blue',
               x0=0.04, x1=0.96, gap=0.02,
               left_label='旋转能垒：低', right_label='高')
    n = len(items)
    x0, x1, gap = 0.04, 0.96, 0.02
    w = (x1 - x0 - gap * (n - 1)) / n
    lps = ['约 0.4–1 nm', '约 0.4–0.7 nm', '约 2–5 nm', '可达数十 nm']
    props = ['柔顺、易结晶', '低温柔顺', '高 $T_g$、难结晶', '高刚性、高 $T_g$']
    for i in range(n):
        cx = x0 + i * (w + gap) + w / 2
        text(ax, cx, 0.42, lps[i], size=11, ha='center')
        text(ax, cx, 0.31, props[i], size=11, ha='center')
    text(ax, 0.5, 0.94, '链柔性谱系：从化学组成到持续长度', size=13, ha='center', weight='bold')
    text(ax, 0.04, 0.20, '持续长度 $\\ell_p$ 随主链旋转能垒增大；Kuhn 长度 $b=2\\ell_p$ 折算等效自由连接链。', size=11)
    text(ax, 0.04, 0.115, '立构规整度与支化不改变旋转能垒，但改变堆积：', size=11)
    text(ax, 0.04, 0.055, '全同/间同可结晶，无规不结晶。', size=11)
    exp.save(fig, 'figure-4-5-chain-flexibility', badge='SCHEMATIC')


def figure_mwd_entanglement_rheology(exp):
    fig, axes = plt.subplots(2, 1, figsize=(420 / 72, 4.8))
    fig.subplots_adjust(left=.17, right=.96, bottom=.11, top=.93, hspace=.55)

    ax = axes[0]
    mn = 100.0
    ms = [10 ** (math.log10(5) + i * (math.log10(500) - math.log10(5)) / 240)
          for i in range(241)]
    for dj, color, ls, label in [(1.1, COL['blue'], '-', '窄单峰 Đ≈1.1'),
                                 (2.0, COL['green'], '-', '宽单峰 Đ≈2'),
                                 (3.0, COL['orange'], '-', '带长尾 Đ≈3')]:
        s2 = math.log(dj)
        s = math.sqrt(s2)
        mu = math.log(mn) - s2 / 2
        w = [math.exp(-((math.log(m) - mu) ** 2) / (2 * s2)) / (m * s)
             for m in ms]
        peak = max(w)
        ax.plot(ms, [x / peak for x in w], color=color, lw=2.0, label=label)
    ax.axvline(mn, color=COL['line'], lw=1, ls='--')
    ax.set_xscale('log')
    ax.set_xlim(5, 500)
    ax.set_ylim(0, 1.2)
    ax.set_xticks([5, 10, 25, 50, 100, 200, 500])
    ax.set_xticklabels(['5', '10', '25', '50', '100', '200', '500'])
    ax.set_xlabel('分子量 M（kg/mol，示意）')
    ax.set_ylabel('重量分布 w(M)')
    ax.text(112, 1.05, '$M_n$', size=11)
    ax.legend(loc='upper right', frameon=False)
    ax.text(0.02, 0.90, '(a)', transform=ax.transAxes, size=12, weight='bold')

    ax = axes[1]
    t = np.logspace(-8, 6, 400)
    curves = [
        ([-8, -4, -2, 0, 2, 4, 6], [9, 9, 6.5, 4.5, 2.5, 0.5, -1], COL['orange'],
         '未缠结（无平台）'),
        ([-8, -4, -3, -2.5, -1, 1, 2, 4, 6],
         [9, 9, 6.2, 5.8, 5.8, 5.8, 4, 0.5, -1], COL['blue'], '缠结（平台可松弛）'),
        ([-8, -4, -3, -2.5, -1, 6], [9, 9, 6.2, 5.8, 5.8, 5.8], COL['green'],
         '交联（平台永久）'),
    ]
    for xp, yp, color, label in curves:
        xp = np.array(xp, dtype=float)
        yp = np.array(yp, dtype=float)
        xf = np.linspace(xp.min(), xp.max(), 300)
        yf = np.interp(xf, xp, yp)
        ax.plot(10 ** xf, 10 ** yf, color=color, lw=2.0, label=label)
    ax.axvspan(1e-3, 1e1, color=COL['gray'], alpha=.5, zorder=0)
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlim(1e-8, 1e6)
    ax.set_ylim(1e-1, 1e9)
    ax.set_xlabel('时间 t（s，示意）')
    ax.set_ylabel('松弛模量 G(t)')
    ax.text(3e-3, 3e6, '橡胶平台', size=11)
    ax.text(1e-7, 3e8, '玻璃态', size=11)
    ax.text(1e3, 3e-1, '末端流动', size=11)
    ax.legend(loc='lower left', frameon=False)
    ax.text(0.02, 0.90, '(b)', transform=ax.transAxes, size=12, weight='bold')
    exp.save(fig, 'figure-4-6-mwd-entanglement-rheology', badge='SCHEMATIC')


def figure_fox_flory_regimes(exp):
    fig, ax = canvas(height=4.0)
    xs = [0.07, 0.13, 0.19, 0.25, 0.31, 0.38, 0.45]
    ys = [0.22, 0.30, 0.43, 0.56, 0.65, 0.70, 0.71]
    ax.plot(xs, ys, color=COL['blue'], lw=2.4, solid_capstyle='round')
    ax.plot([0.07, 0.45], [0.71, 0.71], color=COL['gray'], lw=1, ls='--')
    ax.plot([0.30, 0.30], [0.20, 0.71], color=COL['gray'], lw=1, ls=':')
    text(ax, 0.085, 0.26, '低分子量端\n链端自由体积主导', size=11)
    text(ax, 0.20, 0.735, '平台：重复单元化学主导', size=11)
    text(ax, 0.26, 0.145, '数均分子量 $M_n$（对数，示意）', size=11, ha='center')
    text(ax, 0.045, 0.50, '$T_g$', size=11, rotation=90, ha='center')
    text(ax, 0.50, 0.955, 'Fox–Flory 关系的适用边界', size=13, ha='center', weight='bold')
    cards = [
        ('支化', '链端数增加', 'orange'),
        ('交联', '主导变量换成 $M_c$', 'green'),
        ('共聚物', '叠加组成效应', 'blue'),
        ('结晶体系', '由晶区主导', 'purple'),
    ]
    y = 0.80
    for name, note, color in cards:
        box(ax, 0.55, y - 0.115, 0.42, 0.10, '', color)
        text(ax, 0.575, y - 0.065, name, size=11, weight='bold')
        text(ax, 0.685, y - 0.065, note, size=11)
        y -= 0.155
    text(ax, 0.04, 0.045, '基准曲线分低分子量端与平台区，右侧为四类偏离。', size=11)
    exp.save(fig, 'figure-4-7-fox-flory-regimes', badge='SCHEMATIC')


def figure_mechanics_network_boundary(exp):
    fig, ax = plot(height=3.6, left=.15, bottom=.21)
    x = np.linspace(0.02, 1.0, 200)
    modulus = 1 - np.exp(-3.0 * x)
    elongation = 1 - x
    toughness = modulus * elongation
    toughness = toughness / toughness.max()
    ax.plot(x, modulus, color=COL['blue'], lw=2.2, label='模量（单调上升）')
    ax.plot(x, elongation, color=COL['orange'], lw=2.2, label='断裂伸长率（单调下降）')
    ax.plot(x, toughness, color=COL['green'], lw=2.4, label='韧性（中间峰值）')
    xp = x[np.argmax(toughness)]
    ax.plot([xp], [1.0], marker='o', ms=7, mfc=COL['white'], mec=COL['line'], mew=1.2)
    ax.annotate('韧性峰值\n（模量与延展性的乘积）', xy=(xp, 1.0), xytext=(0.60, 0.28),
                size=11, arrowprops=dict(arrowstyle='-', color=COL['line'], lw=.9))
    ax.axvline(0.18, color=COL['gray'], lw=1, ls=':')
    ax.text(0.20, 0.06, '未缠结/无平台区', size=11)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1.15)
    ax.set_xlabel('网络链段密度（$1/M_e$ 或 $1/M_c$，示意）')
    ax.set_ylabel('归一化性能')
    ax.legend(loc='upper center', frameon=False, ncol=1)
    exp.save(fig, 'figure-4-8-mechanics-network-boundary', badge='SCHEMATIC')


def figure_free_volume_transport(exp):
    fig, axes = plt.subplots(2, 1, figsize=(420 / 72, 4.8))
    fig.subplots_adjust(left=.16, right=.96, bottom=.17, top=.93, hspace=.5)

    top = axes[0]
    top.set(xlim=(0, 1), ylim=(0, 1))
    top.axis('off')
    D.pipeline(top, ['自由体积\n分数与空隙分布', '扩散系数 $D$\n溶解度系数 $S$',
                     '渗透系数\n$P=D\\cdot S$', '选择性\n$\\alpha=P_A/P_B$'],
               y=0.55, h=0.24, color='blue', size=11)
    text(top, 0.5, 0.93, '自由体积 → 扩散与溶解 → 渗透率与选择性',
         size=12, ha='center', weight='bold')
    text(top, 0.02, 0.93, '(a)', size=12, weight='bold')

    ax = axes[1]
    alpha = np.logspace(0, 3, 200)
    known = np.log10(50.0) - 0.9 * np.log10(alpha)
    modern = np.log10(140.0) - 0.9 * np.log10(alpha)
    ax.plot(alpha, known, color=COL['blue'], lw=2.4, label='数据集经验前沿')
    ax.plot(alpha, modern, color=COL['green'], lw=2.4, ls='--',
            label='新材料前沿（固有微孔/热重排）')
    rng = np.random.default_rng(4)
    ax.scatter(alpha, known - 0.25 - 0.35 * rng.random(alpha.size),
               s=8, color=COL['gray'], edgecolor=COL['line'], linewidth=.3, zorder=1)
    ax.set_xscale('log')
    ax.set_xlim(1, 1e3)
    ax.set_ylim(-1.5, 3.0)
    ax.set_xlabel('选择性 $\\alpha$（对数轴）')
    ax.set_ylabel('渗透系数 $\\log P$')
    ax.text(2, -1.1, '材料落在前沿之下', size=11)
    ax.legend(loc='upper right', frameon=False)
    ax.text(0.02, 0.90, '(b)', transform=ax.transAxes, size=12, weight='bold')
    exp.save(fig, 'figure-4-9-free-volume-transport', badge='SCHEMATIC')


def figure_ml_learnability_map(exp):
    fig, ax = plot(height=3.9, left=.14, bottom=.19)
    ax.axvspan(0.5, 1.0, ymin=0.0, ymax=0.5, color=COL['green'], alpha=.5, zorder=0)
    ax.axvspan(0.0, 0.5, ymin=0.5, ymax=1.0, color=COL['orange'], alpha=.5, zorder=0)
    props = [
        (0.88, 0.12, '$T_g$', 'blue'),
        (0.93, 0.22, '密度', 'blue'),
        (0.68, 0.34, '热导率', 'blue'),
        (0.55, 0.52, '介电常数', 'green'),
        (0.44, 0.50, '模量', 'green'),
        (0.22, 0.78, '气体渗透率', 'orange'),
        (0.16, 0.86, '离子电导率', 'orange'),
        (0.20, 0.92, '强度 / 韧性', 'orange'),
    ]
    for x, y, name, color in props:
        ax.scatter([x], [y], s=120, color=COL[color], edgecolor=COL['line'],
                   linewidth=.9, zorder=3)
        ax.text(x, y - 0.075, name, size=11, ha='center')
    ax.text(0.96, 0.42, '可直接监督拟合', size=11, ha='right')
    ax.text(0.04, 0.96, '必须引入机理约束', size=11, ha='left')
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_xlabel('数据密度与关系平滑度 →')
    ax.set_ylabel('物理约束需求 →')
    exp.save(fig, 'figure-4-10-ml-learnability-map', badge='SCHEMATIC')


def main():
    exp = Exporter(HERE)
    figure_structure_property_map(exp)
    figure_tg_chain_structure(exp)
    figure_multiscale_structure(exp)
    figure_multiscale_property_map(exp)
    figure_chain_flexibility(exp)
    figure_mwd_entanglement_rheology(exp)
    figure_fox_flory_regimes(exp)
    figure_mechanics_network_boundary(exp)
    figure_free_volume_transport(exp)
    figure_ml_learnability_map(exp)
    exp.finish()
    index = [
        {'figure': '4-1', 'asset': 'ch04/figure-4-1-structure-property-map.svg'},
        {'figure': '4-2', 'asset': 'ch04/figure-4-2-tg-chain-structure.svg'},
        {'figure': '4-3', 'asset': 'ch04/figure-4-3-multiscale-structure.svg'},
        {'figure': '4-4', 'asset': 'ch04/figure-4-4-multiscale-property-map.svg'},
        {'figure': '4-5', 'asset': 'ch04/figure-4-5-chain-flexibility.svg'},
        {'figure': '4-6', 'asset': 'ch04/figure-4-6-mwd-entanglement-rheology.svg'},
        {'figure': '4-7', 'asset': 'ch04/figure-4-7-fox-flory-regimes.svg'},
        {'figure': '4-8', 'asset': 'ch04/figure-4-8-mechanics-network-boundary.svg'},
        {'figure': '4-9', 'asset': 'ch04/figure-4-9-free-volume-transport.svg'},
        {'figure': '4-10', 'asset': 'ch04/figure-4-10-ml-learnability-map.svg'},
    ]
    (HERE / 'figure-index.json').write_text(
        json.dumps(index, ensure_ascii=False, indent=2) + '\n')
    for record in exp.checks:
        print(f"{record['figure']}: min label {record['min_label_pt']:.0f} pt, "
              f"{len(record['text_extent_warnings'])} warnings")


if __name__ == '__main__':
    main()
