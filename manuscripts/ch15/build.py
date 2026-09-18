#!/usr/bin/env python3
"""Build chapter-fifteen teaching figures from fixed book evidence.

Usage: python manuscripts/ch15/build.py [--font /path/to/CJK-font.ttf]
"""
from pathlib import Path
import argparse
import hashlib
import json
import sys

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


def figure_15_1_circular(exp):
    fig, ax = canvas(height=3.8)
    D.cycle(ax, [
        ('原料', '单体'),
        ('聚合', '链增长'),
        ('制品', '使用'),
        ('回收', '分类清洗'),
        ('解聚回单体', '断键'),
    ], center=(0.46, 0.56), rx=0.29, ry=0.25, w=0.24, h=0.12)
    arrow(ax, (0.29, 0.21), (0.63, 0.21))
    text(ax, 0.46, 0.15, '机械回收：回收→再加工', size=11, ha='center')
    text(ax, 0.28, 0.50, '化学回收', size=11, ha='left')
    text(ax, 0.5, 0.95, '高分子的循环路径', size=13, ha='center', weight='bold')
    text(ax, 0.5, 0.05, '回流路径越短、越接近单体，循环价值越高',
         size=11, ha='center')
    exp.save(fig, 'figure-15-1-circular', badge='SCHEMATIC')


def figure_15_2_applications(exp):
    fig, ax = plot(height=3.6, left=.13, bottom=.18)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_xlabel('性能指标 →')
    ax.set_ylabel('可持续性指标 →')
    clusters = [
        ('回收', 'blue', 'o', [(0.22, 0.66), (0.30, 0.74), (0.18, 0.78)]),
        ('能源', 'orange', 's', [(0.62, 0.30), (0.70, 0.38), (0.56, 0.22)]),
        ('分离', 'green', '^', [(0.70, 0.64), (0.78, 0.72), (0.64, 0.56)]),
        ('储能', 'purple', 'D', [(0.40, 0.44), (0.48, 0.52), (0.34, 0.36)]),
    ]
    for name, color, marker, pts in clusters:
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        ax.scatter(xs, ys, s=80, marker=marker, facecolor=COL[color],
                   edgecolor=COL['line'], linewidth=.9, zorder=3)
        ax.text(sum(xs) / len(xs), sum(ys) / len(ys) + 0.10, name, size=12,
                ha='center', weight='bold')
    ax.axhline(0.5, color=COL['gray'], lw=.8, zorder=0)
    ax.axvline(0.5, color=COL['gray'], lw=.8, zorder=0)
    exp.save(fig, 'figure-15-2-applications', badge='SCHEMATIC')


def figure_15_3_tradeoff(exp):
    fig, ax = plot(height=3.6, left=.13, bottom=.18)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_xlabel('性能 →')
    ax.set_ylabel('可回收性 →')
    front = [(0.20, 0.86), (0.34, 0.78), (0.48, 0.68), (0.62, 0.56), (0.76, 0.42)]
    off = [(0.30, 0.50), (0.44, 0.30), (0.58, 0.22), (0.24, 0.38), (0.66, 0.30),
           (0.50, 0.12)]
    fx = [p[0] for p in front]
    fy = [p[1] for p in front]
    ox = [p[0] for p in off]
    oy = [p[1] for p in off]
    ax.plot(fx, fy, color=COL['line'], lw=1.8, zorder=2)
    ax.scatter(ox, oy, s=60, marker='s', facecolor=COL['gray'],
               edgecolor=COL['line'], linewidth=.9, zorder=3)
    ax.scatter(fx, fy, s=80, facecolor=COL['orange'], edgecolor=COL['line'],
               linewidth=.9, zorder=3)
    ax.text(0.58, 0.92, '圆点：前沿候选', size=11)
    ax.text(0.58, 0.84, '方点：被支配候选', size=11)
    ax.text(0.58, 0.76, '实线：Pareto 前沿', size=11)
    exp.save(fig, 'figure-15-3-tradeoff', badge='SCHEMATIC')


def figure_15_4_lifecycle(exp):
    fig, ax = canvas(height=3.9)
    text(ax, 0.5, 0.95, '生命周期五阶段与目标向量', size=13, ha='center', weight='bold')
    D.pipeline(ax, ['原料', '合成', '加工', '使用', '废弃'], y=0.75, h=0.13,
               color='blue')
    arrow(ax, (0.5, 0.665), (0.5, 0.525))
    box(ax, 0.05, 0.36, 0.90, 0.15,
        '目标向量：性能、成本、碳足迹、可回收率、毒性', color='green', size=11)
    text(ax, 0.5, 0.20,
         '原料与聚合决定合成段排放，使用段决定寿命摊薄，废弃段决定回收或降解路径',
         size=11, ha='center')
    exp.save(fig, 'figure-15-4-lifecycle', badge='SCHEMATIC')


def figure_15_5_feedstock(exp):
    fig, ax = plot(height=3.7, left=.15, bottom=.20)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_xlabel('可得性（产量与地理分布）→')
    ax.set_ylabel('单位产品碳强度 →')
    clusters = [
        ('化石基', 'blue', 'o', (0.80, 0.74), '石脑油、天然气'),
        ('CO₂ 基', 'orange', 's', (0.16, 0.60), 'CO₂ 与环氧化物'),
        ('生物基', 'green', '^', (0.50, 0.30), '淀粉、纤维素、油脂'),
    ]
    for name, color, marker, (x, y), note in clusters:
        ax.scatter([x], [y], s=110, marker=marker, facecolor=COL[color],
                   edgecolor=COL['line'], linewidth=.9, zorder=3)
        ax.text(x, y + 0.10, name, size=12, ha='center', weight='bold')
        ax.text(x, y - 0.11, note, size=11, ha='center')
    ax.text(0.5, 0.03, '位置为示意：碳强度按单位产品核算，边界不同结论会变',
            size=11, ha='center')
    exp.save(fig, 'figure-15-5-feedstock', badge='SCHEMATIC')


def figure_15_6_eol(exp):
    fig, ax = canvas(height=3.7)
    text(ax, 0.5, 0.95, '四条废弃路径的结构硬约束', size=13, ha='center', weight='bold')
    D.table(ax, ['路径', '结构硬约束', '关键量与失效模式'],
            [['机械回收', '可熔融、分子量余量', '再加工次数、逐轮降级'],
             ['化学回收', '可解聚键与催化剂', '产率、解聚能耗'],
             ['升级回收', '催化活性位点', '产物选择性、失活'],
             ['生物降解', '可水解键、低结晶度', '半衰期、环境匹配']],
            y_top=0.80, row_h=0.145, col_x=[0.15, 0.44, 0.79], size=11)
    text(ax, 0.5, 0.09,
         '路径不同，对同一张链的硬约束不同，可行域的交集决定可设计的材料',
         size=11, ha='center')
    exp.save(fig, 'figure-15-6-eol', badge='SCHEMATIC')


def figure_15_8_worked_pareto(exp):
    data = json.loads((ROOT / 'calculations/results/pareto-screen-block.json').read_text())
    summary = data['summary']
    front = summary['front']
    dominated = summary['dominated']
    fig, ax = plot(height=3.9, left=.15, bottom=.20)
    ax.set_xlim(0.28, 1.0)
    ax.set_ylim(0.20, 1.05)
    ax.set_xlabel('选择性代理 →')
    ax.set_ylabel('渗透率代理 →')
    fx = [p[0] for p in front]
    fy = [p[1] for p in front]
    dx = [p[0] for p in dominated]
    dy = [p[1] for p in dominated]
    ax.scatter(dx, dy, s=26, marker='s', facecolor=COL['gray'],
               edgecolor=COL['line'], linewidth=.5, zorder=2)
    ax.plot(fx, fy, color=COL['line'], lw=1.4, zorder=2)
    ax.scatter(fx, fy, s=18, facecolor=COL['orange'], edgecolor=COL['line'],
               linewidth=.4, zorder=3)
    kx, ky = summary['knee_selectivity'], summary['knee_permeability']
    ax.scatter([kx], [ky], s=120, marker='*', facecolor=COL['blue'],
               edgecolor=COL['line'], linewidth=.8, zorder=4)
    ax.annotate('膝点', (kx, ky), textcoords='offset points',
                xytext=(-58, -14), fontsize=11)
    ax.annotate('高选择性端', (fx[0], fy[0]), textcoords='offset points',
                xytext=(6, -18), fontsize=11)
    exp.save(fig, 'figure-15-8-worked-pareto', badge='CALC')


def figure_15_7_scenarios(exp):
    fig, ax = canvas(height=3.6)
    text(ax, 0.5, 0.95, '情景改变目标向量，最优材料随之移动', size=13,
         ha='center', weight='bold')
    D.tree(ax, '废弃情景', ['填埋', '焚烧', '机械回收', '化学回收'],
           root_xy=(0.5, 0.80), branch_y=0.50, w=0.19, h=0.12, size=12)
    notes = ['耐久、低成本', '低碳含量', '可熔融\n分子量余量', '可解聚键\n低温解聚']
    for i, note in enumerate(notes):
        x = 0.05 + 0.90 * (i + 0.5) / 4
        text(ax, x, 0.28, note, size=11, ha='center')
    text(ax, 0.5, 0.08,
         '情景不同，对耐久、碳含量与可回收性的要求不同',
         size=11, ha='center')
    exp.save(fig, 'figure-15-7-scenarios', badge='SCHEMATIC')


def main():
    exp = Exporter(HERE)
    figure_15_1_circular(exp)
    figure_15_2_applications(exp)
    figure_15_3_tradeoff(exp)
    figure_15_4_lifecycle(exp)
    figure_15_5_feedstock(exp)
    figure_15_6_eol(exp)
    figure_15_7_scenarios(exp)
    figure_15_8_worked_pareto(exp)
    exp.finish()
    index = [
        {'figure': '15-1', 'asset': 'ch15/figure-15-1-circular.svg'},
        {'figure': '15-2', 'asset': 'ch15/figure-15-2-applications.svg'},
        {'figure': '15-3', 'asset': 'ch15/figure-15-3-tradeoff.svg'},
        {'figure': '15-4', 'asset': 'ch15/figure-15-4-lifecycle.svg'},
        {'figure': '15-5', 'asset': 'ch15/figure-15-5-feedstock.svg'},
        {'figure': '15-6', 'asset': 'ch15/figure-15-6-eol.svg'},
        {'figure': '15-7', 'asset': 'ch15/figure-15-7-scenarios.svg'},
        {'figure': '15-8', 'asset': 'ch15/figure-15-8-worked-pareto.svg'},
    ]
    (HERE / 'figure-index.json').write_text(
        json.dumps(index, ensure_ascii=False, indent=2) + '\n')
    for record in exp.checks:
        print(f"{record['figure']}: min label {record['min_label_pt']:.0f} pt, "
              f"{len(record['text_extent_warnings'])} warnings")


if __name__ == '__main__':
    main()
