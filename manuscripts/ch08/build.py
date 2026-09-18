#!/usr/bin/env python3
"""Build chapter-eight teaching figures from fixed book evidence.

Usage: python manuscripts/ch08/build.py [--font /path/to/CJK-font.ttf]
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

from figure_style import COL, Exporter, arrow, box, canvas, plot, text
from figure_style import diagrams as D

import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse

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


def figure_characterization_loop(exp):
    fig, ax = canvas(height=4.3)
    items = [
        ('采集', '按参数测量'),
        ('分析', '分割·反演·融合'),
        ('结构/性质估计', '给出后验不确定度'),
        ('选择下一次测量', '消费后验不确定度'),
    ]
    D.cycle(ax, items, center=(0.36, 0.50), rx=0.24, ry=0.30,
            w=0.20, h=0.11, color='blue', size=11)
    box(ax, 0.50, 0.445, 0.20, 0.11, '分析', 'orange', size=11)
    inputs = [
        (0.78, '图像', '像素场'),
        (0.50, '光谱', '一维信号'),
        (0.22, '散射', '倒空间强度'),
    ]
    for y, name, kind in inputs:
        box(ax, 0.76, y - 0.06, 0.20, 0.12, f'{name}\n{kind}', 'green', size=11)
    arrow(ax, (0.76, 0.78), (0.70, 0.56))
    arrow(ax, (0.76, 0.50), (0.70, 0.50))
    arrow(ax, (0.76, 0.22), (0.70, 0.44))
    text(ax, 0.86, 0.94, '三类表征数据', size=11, ha='center', weight='bold')
    exp.save(fig, 'figure-8-1-characterization-loop', badge='SCHEMATIC')


def figure_spectrum_structure(exp):
    fig, ax = canvas(height=3.8)
    box(ax, 0.03, 0.28, 0.30, 0.62, '', 'blue')
    text(ax, 0.18, 0.845, '结构空间', size=12, ha='center', weight='bold')
    for i, label in enumerate(['结构 A', '结构 B', '结构 C']):
        box(ax, 0.06, 0.68 - i * 0.17, 0.24, 0.11, label, 'white', size=11)
    box(ax, 0.67, 0.36, 0.30, 0.36, '', 'orange')
    text(ax, 0.82, 0.665, '谱空间', size=12, ha='center', weight='bold')
    xs = [0.69 + i * 0.02 for i in range(15)]
    peaks = [(0.73, 0.10), (0.79, 0.16), (0.86, 0.08), (0.92, 0.12)]
    ys = []
    for x in xs:
        v = 0.44
        for c, a in peaks:
            v += a * math.exp(-((x - c) / 0.018) ** 2)
        ys.append(min(v, 0.63))
    ax.plot(xs, ys, color=COL['line'], lw=1.4)
    ax.plot([0.69, 0.955], [0.44, 0.44], color=COL['line'], lw=.8)
    text(ax, 0.82, 0.40, '波数 / 化学位移', size=11, ha='center')
    for i in range(3):
        y = 0.735 - i * 0.17
        arrow(ax, (0.30, y), (0.67, 0.50))
    text(ax, 0.48, 0.74, '模拟/DFT 正演', size=11, ha='center', weight='bold')
    arrow(ax, (0.67, 0.36), (0.30, 0.28), kind='control')
    text(ax, 0.56, 0.205, '病态反问题：同一谱对应多个结构', size=11, ha='center')
    exp.save(fig, 'figure-8-2-spectrum-structure', badge='SCHEMATIC')


def figure_segmentation_pipeline(exp):
    fig, ax = canvas(height=3.2)
    steps = ['原始图像', '预处理', '编码器\n解码器', '后处理', '统计量']
    D.pipeline(ax, steps, y=0.74, h=0.14, color='blue', size=11)
    box(ax, 0.798, 0.67, 0.172, 0.14, '统计量', 'orange', size=11)
    text(ax, 0.5, 0.93, '分割流程：从像素到形貌统计量', size=12, ha='center',
         weight='bold')
    notes = [
        '输入：像素场\n输出：像素场\n参数：分辨率',
        '输入：像素场\n输出：归一化\n参数：基线窗',
        '输入：特征图\n输出：概率图\n参数：网络权重',
        '输入：概率图\n输出：类别图\n参数：阈值',
        '输入：类别图\n输出：统计量\n参数：分箱',
    ]
    for i, note in enumerate(notes):
        x = 0.03 + i * 0.192 + 0.086
        text(ax, x, 0.42, note, size=11, ha='center')
    exp.save(fig, 'figure-8-3-segmentation-pipeline', badge='SCHEMATIC')


def two_panel(height=3.7, wspace=0.34, left=0.10, right=0.97):
    fig, axes = plt.subplots(1, 2, figsize=(420 / 72, height))
    fig.subplots_adjust(left=left, right=right, bottom=0.18, top=0.92, wspace=wspace)
    return fig, axes


def gauss(x, mu, sigma, amp):
    return amp * math.exp(-((x - mu) / sigma) ** 2)


def sphere_form(qr):
    if qr < 1e-6:
        return 1.0
    return (3 * (math.sin(qr) - qr * math.cos(qr)) / qr ** 3) ** 2


def figure_three_pipelines(exp):
    fig, ax = canvas(height=4.3)
    stages = ['输入', '预处理', '表示', '模型', '输出', '性质']
    rows = [('图像', 0.80), ('光谱', 0.51), ('散射', 0.22)]
    for label, y in rows:
        D.pipeline(ax, stages, y=y, h=0.13, color='blue', size=11,
                   x0=0.16, x1=0.97, gap=0.016)
        text(ax, 0.08, y, label, size=12, ha='center', weight='bold')
    text(ax, 0.5, 0.95, '三条表征流水线', size=12, ha='center', weight='bold')
    notes = ['瓶颈：标注与域漂移', '瓶颈：预处理与峰归属', '瓶颈：反演不适定']
    for (_, y), note in zip(rows, notes):
        text(ax, 0.565, y - 0.115, note, size=11, ha='center')
    exp.save(fig, 'figure-8-4-three-pipelines', badge='SCHEMATIC')


def figure_spectral_preprocessing(exp):
    fig, axes = two_panel(height=3.7, wspace=0.36)
    xs = [400 + i * (4000 - 400) / 400 for i in range(401)]
    peaks = [(1720, 40, 0.55), (1250, 60, 0.34), (2900, 80, 0.26)]
    baseline = [0.28 + 8e-5 * (x - 400) for x in xs]
    raw = [baseline[i] + sum(gauss(xs[i], m, s, a) for m, s, a in peaks)
           for i in range(len(xs))]
    corrected = [sum(gauss(xs[i], m, s, a) for m, s, a in peaks)
                 for i in range(len(xs))]
    peak_max = max(corrected)
    corrected = [v / peak_max for v in corrected]

    axes[0].text(0.02, 1.02, '(a)', transform=axes[0].transAxes, fontsize=12,
                 va='bottom', weight='bold')
    axes[1].text(0.02, 1.02, '(b)', transform=axes[1].transAxes, fontsize=12,
                 va='bottom', weight='bold')
    axes[0].plot(xs, raw, color=COL['line'], linewidth=1.0)
    axes[0].plot(xs, baseline, color='#c0392b', linewidth=1.0, linestyle='--')
    axes[0].text(0.05, 0.90, '原始谱 + 基线漂移', transform=axes[0].transAxes,
                 fontsize=11, va='top')
    axes[0].text(0.05, 0.78, '虚线：拟合基线', transform=axes[0].transAxes,
                 fontsize=11, va='top')
    axes[0].set_xlabel('波数 (cm⁻¹)', fontsize=11)
    axes[0].set_ylabel('强度 (a.u.)', fontsize=11)
    axes[0].invert_xaxis()
    axes[0].tick_params(labelsize=11)
    axes[0].spines[['top', 'right']].set_visible(False)

    axes[1].plot(xs, corrected, color=COL['blue'], linewidth=1.2)
    axes[1].fill_between(xs, 0, corrected, color=COL['blue'], alpha=.5)
    for m, s, a in peaks:
        axes[1].text(m, a / peak_max * 0.45, f'{m}', fontsize=11, ha='center')
    axes[1].text(0.05, 0.90, '扣基线 · 归一化后', transform=axes[1].transAxes,
                 fontsize=11, va='top')
    axes[1].set_xlabel('波数 (cm⁻¹)', fontsize=11)
    axes[1].set_ylabel('归一化强度', fontsize=11)
    axes[1].invert_xaxis()
    axes[1].tick_params(labelsize=11)
    axes[1].spines[['top', 'right']].set_visible(False)
    exp.save(fig, 'figure-8-5-spectral-preprocessing', badge='SCHEMATIC')


def figure_scattering_inverse(exp):
    fig, axes = two_panel(height=3.7, wspace=0.36)
    rs = [1.0 + i * 14.0 / 300 for i in range(301)]
    smooth = [gauss(r, 6.0, 1.5, 1.0) for r in rs]
    ripple = [max(0.0, gauss(r, 6.0, 1.5, 1.0)
                  * (1 + 0.4 * math.sin(2 * math.pi * r / 0.8))) for r in rs]
    axes[0].text(0.02, 1.02, '(a)', transform=axes[0].transAxes, fontsize=12,
                 va='bottom', weight='bold')
    axes[1].text(0.02, 1.02, '(b)', transform=axes[1].transAxes, fontsize=12,
                 va='bottom', weight='bold')
    axes[0].plot(rs, smooth, color=COL['blue'], linewidth=1.2, label='分布 A')
    axes[0].plot(rs, ripple, color=COL['orange'], linewidth=1.2, linestyle='--',
                 label='分布 B（含细结构）')
    axes[0].set_xlabel('半径 r (nm)', fontsize=11)
    axes[0].set_ylabel('分布 f(r)', fontsize=11)
    axes[0].tick_params(labelsize=11)
    axes[0].legend(fontsize=11, loc='upper right')
    axes[0].spines[['top', 'right']].set_visible(False)

    qs = [0.05 + i * 1.45 / 300 for i in range(301)]
    curves = []
    for dist in (smooth, ripple):
        curves.append([sum(dist[i] * sphere_form(q * rs[i]) * rs[i] ** 2
                           for i in range(len(rs))) for q in qs])
    axes[1].semilogy(qs, [v / curves[0][0] for v in curves[0]], color=COL['blue'],
                     linewidth=1.4, label='分布 A')
    axes[1].semilogy(qs, [v / curves[1][0] for v in curves[1]], color=COL['orange'],
                     linewidth=1.2, linestyle='--', label='分布 B')
    axes[1].text(0.05, 0.88, '两曲线最大相对差 < 2×10⁻⁶', transform=axes[1].transAxes,
                 fontsize=11, va='top')
    axes[1].set_xlabel('散射矢量 q (nm⁻¹)', fontsize=11)
    axes[1].set_ylabel('归一化强度 I(q)', fontsize=11)
    axes[1].tick_params(labelsize=11)
    axes[1].legend(fontsize=11, loc='lower left')
    axes[1].spines[['top', 'right']].set_visible(False)
    exp.save(fig, 'figure-8-6-scattering-inverse', badge='CALC')


def figure_fusion_positions(exp):
    fig, ax = canvas(height=4.2)
    rows = [
        ('早期', 0.80, ['三模态输入', '拼接 768 维', '共享模型'],
         '实现最简单；缺模态时维度不完整；需先标准化'),
        ('中期', 0.52, ['三模态输入', '交叉注意力', '共享模型'],
         '表达力强；输出维度不随模态数增长；配准要求最严'),
        ('晚期', 0.24, ['三模态输入', '加权集成', '各模态模型'],
         '对缺失最鲁棒；可并行；推理为各模型之和'),
    ]
    for label, y, steps, note in rows:
        D.pipeline(ax, steps, y=y, h=0.13, color='green', size=11,
                   x0=0.16, x1=0.97, gap=0.02)
        text(ax, 0.075, y, label, size=12, ha='center', weight='bold')
        text(ax, 0.565, y - 0.115, note, size=11, ha='center')
    text(ax, 0.5, 0.95, '多模态融合的三个位置', size=12, ha='center', weight='bold')
    exp.save(fig, 'figure-8-7-fusion-positions', badge='SCHEMATIC')


def figure_prior_constraint(exp):
    fig, ax = canvas(height=3.9)
    ax.add_patch(Ellipse((0.33, 0.50), 0.54, 0.80, facecolor=COL['blue'],
                         edgecolor=COL['line'], linewidth=.9))
    ax.add_patch(Ellipse((0.33, 0.50), 0.38, 0.56, facecolor=COL['green'],
                         edgecolor=COL['line'], linewidth=.9))
    ax.add_patch(Ellipse((0.33, 0.50), 0.22, 0.34, facecolor=COL['orange'],
                         edgecolor=COL['line'], linewidth=.9))
    text(ax, 0.33, 0.83, '观测解集', size=12, ha='center', weight='bold')
    text(ax, 0.33, 0.66, '物理先验', size=11, ha='center')
    text(ax, 0.33, 0.50, '后验', size=11, ha='center')
    notes = [
        (0.83, '观测约束 y = A(x) + ε', 'blue'),
        (0.60, '物理先验：非负·平滑·上限', 'green'),
        (0.37, '数据先验：结构流形', 'orange'),
        (0.17, '多模态：零空间交集', 'gray'),
    ]
    for y, label, color in notes:
        box(ax, 0.60, y - 0.055, 0.37, 0.11, label, color, size=11)
        arrow(ax, (0.58, y), (0.53, 0.50 + (y - 0.50) * 0.30), kind='control')
    text(ax, 0.5, 0.955, '先验约束把可行解集缩小', size=12, ha='center', weight='bold')
    exp.save(fig, 'figure-8-8-prior-constraint', badge='SCHEMATIC')


def figure_worked_cost(exp):
    fig, ax = plot(height=3.4, left=0.16, bottom=0.22)
    labels = ['人工标注', '模型纯计算']
    values = [500 * 3600, 1.2337]
    positions = [1, 0]
    ax.barh(positions, values, height=0.5, color=[COL['orange'], COL['blue']],
            edgecolor=COL['line'], linewidth=.8)
    ax.set_xscale('log')
    ax.set_yticks(positions)
    ax.set_yticklabels(labels, fontsize=11)
    ax.set_xlabel('时间（秒，对数轴）', fontsize=11)
    ax.tick_params(labelsize=11)
    ax.spines[['top', 'right']].set_visible(False)
    ax.text(0.97, 1, f'{500} 小时', transform=ax.get_yaxis_transform(),
            fontsize=11, ha='right', va='center')
    ax.text(0.97, 0, f'{1.2:.1f} 秒', transform=ax.get_yaxis_transform(),
            fontsize=11, ha='right', va='center')
    ax.text(0.03, 0.90, '理论估算，非实测墙钟时间', transform=ax.transAxes,
            fontsize=11, va='top')
    exp.save(fig, 'figure-8-9-worked-cost', badge='CALC')


def main():
    exp = Exporter(HERE)
    figure_characterization_loop(exp)
    figure_spectrum_structure(exp)
    figure_segmentation_pipeline(exp)
    figure_three_pipelines(exp)
    figure_spectral_preprocessing(exp)
    figure_scattering_inverse(exp)
    figure_fusion_positions(exp)
    figure_prior_constraint(exp)
    figure_worked_cost(exp)
    exp.finish()
    index = [
        {'figure': '8-1', 'asset': 'ch08/figure-8-1-characterization-loop.svg'},
        {'figure': '8-2', 'asset': 'ch08/figure-8-2-spectrum-structure.svg'},
        {'figure': '8-3', 'asset': 'ch08/figure-8-3-segmentation-pipeline.svg'},
        {'figure': '8-4', 'asset': 'ch08/figure-8-4-three-pipelines.svg'},
        {'figure': '8-5', 'asset': 'ch08/figure-8-5-spectral-preprocessing.svg'},
        {'figure': '8-6', 'asset': 'ch08/figure-8-6-scattering-inverse.svg'},
        {'figure': '8-7', 'asset': 'ch08/figure-8-7-fusion-positions.svg'},
        {'figure': '8-8', 'asset': 'ch08/figure-8-8-prior-constraint.svg'},
        {'figure': '8-9', 'asset': 'ch08/figure-8-9-worked-cost.svg'},
    ]
    (HERE / 'figure-index.json').write_text(
        json.dumps(index, ensure_ascii=False, indent=2) + '\n')
    for record in exp.checks:
        print(f"{record['figure']}: min label {record['min_label_pt']:.0f} pt, "
              f"{len(record['text_extent_warnings'])} warnings")


if __name__ == '__main__':
    main()
