#!/usr/bin/env python3
"""Build chapter-thirteen teaching figures from fixed book evidence.

Usage: python manuscripts/ch13/build.py [--font /path/to/CJK-font.ttf]
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

SUMMARY = json.loads(
    (ROOT / 'calculations/results/closed-loop-bo.json').read_text())['summary']


def figure_loop(exp):
    fig, ax = canvas(height=4.2)
    items = [('决策', '30 min'), ('调度', '10 min'), ('执行', '8 h'),
             ('表征', '1 h'), ('数据回流', '10 min')]
    D.cycle(ax, items, center=(0.5, 0.5), rx=0.30, ry=0.28, w=0.24, h=0.12,
            color='blue', size=12)
    angle = math.radians(90 - 360 * 2 / 5)
    cx, cy = 0.5 + 0.30 * math.cos(angle), 0.5 + 0.28 * math.sin(angle)
    box(ax, cx - 0.12, cy - 0.06, 0.24, 0.12, '执行', color='orange', size=12)
    text(ax, 0.5, 0.93, '节点标注为典型节拍（示意）', size=11, ha='center')
    text(ax, 0.5, 0.06, '吞吐瓶颈：执行 8 h', size=11, ha='center')
    exp.save(fig, 'figure-13-1-loop', badge='SCHEMATIC')


def figure_throughput(exp):
    segments = [('调度', 10, 10, 'blue'), ('执行', 480, 240, 'orange'),
                ('表征', 60, 60, 'green'), ('回流', 10, 10, 'gray')]
    totals = [sum(s[1] for s in segments), sum(s[2] for s in segments)]
    fig, ax = plot(height=3.9, left=.12, bottom=.18)
    x = np.arange(2)
    bottoms = np.zeros(2)
    for name, current, shortened, color in segments:
        heights = np.array([current, shortened])
        ax.bar(x, heights, bottom=bottoms, width=.5, color=COL[color],
               edgecolor=COL['line'], linewidth=.9, label=name)
        bottoms += heights
    ax.set_xticks(x)
    ax.set_xticklabels(['当前周期', '缩短执行后'])
    ax.set_xlim(-0.6, 1.6)
    ax.set_ylim(0, 820)
    ax.set_ylabel('单周期时间（min）')
    for i, total in enumerate(totals):
        ax.text(i, total + 20, f'{total:.0f} min\n{1440 / total:.1f} 次/天',
                fontsize=11, ha='center', va='bottom')
    ax.text(0.5, 430, '缩短最大段：执行 8 h → 4 h', fontsize=11, ha='center')
    ax.legend(loc='center right', frameon=False)
    per_day = SUMMARY['experiments_per_day']
    bo_days = SUMMARY['calendar_days']
    rand_days = SUMMARY['random_calendar_days']
    ax.text(0.02, 0.97, f'闭环模型（closed-loop-bo.json）：{per_day:.0f} 次/天；\n'
            f'到目标 {bo_days:.0f} 天（随机 {rand_days:.0f} 天）',
            transform=ax.transAxes, fontsize=11, va='top')
    ax.text(0.02, 0.04, '分段耗时为示意', transform=ax.transAxes, fontsize=11)
    exp.save(fig, 'figure-13-2-throughput', badge='SCHEMATIC')


def figure_software_stack(exp):
    fig, ax = canvas(height=5.4)
    items = [
        ('重训', '更新模型', '偏置', 'purple'),
        ('数据库', '存储与溯源', '重复', 'gray'),
        ('LIMS/ELN', '挂元数据', '缺字段', 'green'),
        ('仪器', '测量样品', '误判', 'orange'),
        ('机器人', '执行物理动作', '漂移', 'orange'),
        ('工作流管理器', '展开指令与依赖', '半执行', 'blue'),
        ('调度器', '排程与优先级', '死锁', 'blue'),
        ('AI 模型', '选点与不确定度', '外推', 'green'),
    ]
    D.layers(ax, items, x=0.05, w=0.88, y0=0.055, step=0.108, h=0.085,
             name_x=0.14, desc_x=0.31, tag_x=0.92, arrow_x=0.50,
             name_size=12, size=11)
    text(ax, 0.5, 0.975, '自驱动实验室软件栈', size=12, ha='center', weight='bold')
    arrow(ax, (0.965, 0.10), (0.965, 0.87), kind='control')
    text(ax, 0.99, 0.485, '重训回流', size=11, ha='center', rotation=270)
    exp.save(fig, 'figure-13-3-software-stack', badge='SCHEMATIC')


def figure_hardware(exp):
    fig, ax = canvas(height=4.8)
    text(ax, 0.5, 0.955, '硬件模块：通量、精度、维护与适配代价', size=12,
         ha='center', weight='bold')
    headers = ['模块', '通量', '精度', '维护', '适配']
    rows = [
        ('液体处理', '96 通道', 'CV 1%–5%', '低', '低'),
        ('聚合反应器', '32 样/炉', '未报告', '中', '中'),
        ('孔板系统', '96 孔', '未报告', '低', '高'),
        ('GPC', '单柱', '±10%', '高', '高'),
        ('DSC', '单炉', '未报告', '中', '中'),
        ('FTIR', '单点', '未报告', '低', '中'),
        ('样品搬运', '1 臂', '10 μm', '中', '高'),
    ]
    D.table(ax, headers, rows, y_top=0.82, row_h=0.092,
            col_x=[0.12, 0.34, 0.56, 0.75, 0.92])
    text(ax, 0.04, 0.085, '通量与精度取自公开文献或为教学设定范围，维护与适配为定性代价。', size=11)
    text(ax, 0.04, 0.035, '"未报告"表示文献未给出该模块精度。', size=11)
    exp.save(fig, 'figure-13-4-hardware', badge='SCHEMATIC')


def figure_scheduler(exp):
    fig, ax = canvas(height=5.2)
    text(ax, 0.5, 0.965, '调度：作业流水线与同步/异步时序', size=12,
         ha='center', weight='bold')
    D.pipeline(ax, ['选点', '排程', '执行', '表征', '回填'], y=0.83, h=0.12,
               size=11, back=[(4, 0)])
    text(ax, 0.5, 0.70, '虚线：重训反馈；实线：数据流', size=11, ha='center')
    text(ax, 0.02, 0.90, '(a)', size=12, weight='bold')
    text(ax, 0.02, 0.655, '(b)', size=12, weight='bold')
    rows = [('同步 A', 0, 1), ('同步 B', 1, 1), ('同步 C', 2, 1),
            ('异步 A', 0, 1), ('异步 B', 0.33, 1), ('异步 C', 0.66, 1)]
    D.gantt(ax, rows, x0=0.24, x1=0.97, y_top=0.60, row_h=0.062, gap=0.012,
            total=3.0)
    text(ax, 0.04, 0.045, '异步在同样时间内完成更多实验，'
         '但决策用到在途结果（延迟反馈）。', size=11)
    exp.save(fig, 'figure-13-5-scheduler', badge='SCHEMATIC')


def figure_reliability(exp):
    fig, ax = canvas(height=4.6)
    text(ax, 0.5, 0.965, '可靠性与纠错：检测、分类、重试与上报', size=12,
         ha='center', weight='bold')
    w, h = 0.20, 0.11
    nodes = {
        'exec': (0.17, 0.74, '执行实验', 'blue'),
        'detect': (0.50, 0.74, '在线检测', 'blue'),
        'valid': (0.83, 0.74, '数据校验', 'blue'),
        'classify': (0.50, 0.44, '失败分类', 'orange'),
        'db': (0.83, 0.44, '入库', 'green'),
        'retry': (0.17, 0.44, '重试 ≤ k', 'orange'),
        'report': (0.50, 0.16, '人工上报', 'gray'),
    }
    for x, y, label, color in nodes.values():
        box(ax, x - w / 2, y - h / 2, w, h, label, color)
    edges = [((0.27, 0.74), (0.40, 0.74), 'data'),
             ((0.60, 0.74), (0.73, 0.74), 'data'),
             ((0.83, 0.685), (0.83, 0.495), 'data'),
             ((0.73, 0.71), (0.59, 0.49), 'control'),
             ((0.40, 0.44), (0.27, 0.44), 'data'),
             ((0.17, 0.495), (0.17, 0.685), 'control'),
             ((0.50, 0.385), (0.50, 0.215), 'control')]
    for start, end, kind in edges:
        arrow(ax, start, end, kind=kind)
    text(ax, 0.04, 0.055, '实线：数据流；虚线：控制或反馈。'
         '失败标记后仍入库，避免选择偏置。', size=11)
    exp.save(fig, 'figure-13-6-reliability', badge='SCHEMATIC')


def figure_cases(exp):
    fig, ax = canvas(height=5.4)
    text(ax, 0.5, 0.975, '四个自驱动实验室案例对照', size=12, ha='center',
         weight='bold')
    cards = [
        ('A-Lab', 'blue', [('硬件', '粉末站+4 炉+XRD'),
                           ('通量', '353 次/17 天'),
                           ('产出', '36/57 目标'),
                           ('局限', '多相 XRD 存疑')]),
        ('Coscientist', 'green', [('硬件', 'OT-2+板读器+云实验室'),
                                  ('通量', '未报告'),
                                  ('产出', '偶联产物经 GC-MS 确认'),
                                  ('局限', '半自动、需网络检索')]),
        ('Ada 薄膜', 'orange', [('硬件', '机械臂+旋涂+光谱'),
                                ('通量', '约 1 样/20 min'),
                                ('产出', '优化空穴迁移率'),
                                ('局限', '非器件迁移率')]),
        ('PANDA/LCST', 'purple', [('硬件', '龙门+96 孔+电化学'),
                                  ('通量', '未报告'),
                                  ('产出', '电致变色与 LCST'),
                                  ('局限', '通量未报告')]),
    ]
    positions = [(0.03, 0.52), (0.51, 0.52), (0.03, 0.06), (0.51, 0.06)]
    for (title, color, lines), (x, y) in zip(cards, positions):
        box(ax, x, y, 0.46, 0.40, '', color)
        text(ax, x + 0.035, y + 0.345, title, size=12, weight='bold')
        for i, (key, value) in enumerate(lines):
            text(ax, x + 0.035, y + 0.275 - i * 0.072, f'{key} {value}',
                 size=11)
    exp.save(fig, 'figure-13-7-cases', badge='LIT')


def figure_worked(exp):
    fig, (left, right) = plt.subplots(1, 2, figsize=(420 / 72, 4.0))
    fig.subplots_adjust(left=.13, right=.97, bottom=.24, top=.80, wspace=.45)
    for ax in (left, right):
        ax.spines[['top', 'right']].set_visible(False)
    rate = [SUMMARY['experiments_per_day'],
            SUMMARY['experiments_per_day'] * 0.72]
    labels = ['名义', '有效']
    bars = left.bar(labels, rate, color=[COL['blue'], COL['orange']],
                    edgecolor=COL['line'], linewidth=.9, width=.55)
    for rect, value in zip(bars, rate):
        left.text(rect.get_x() + rect.get_width() / 2, value + 1.2,
                  f'{value:.0f}', size=11, ha='center')
    left.set_ylim(0, 88)
    left.set_ylabel('速率（次/天）')
    left.set_title('(a) 闭环速率', size=11)
    left.text(0.5, 0.93, f'随机 {SUMMARY["random_calendar_days"]:.0f} → '
             f'{SUMMARY["random_experiments_expected"] / (SUMMARY["experiments_per_day"] * 0.72):.1f} 天',
             transform=left.transAxes, size=11, ha='center', va='top')
    left.text(0.5, 0.85, f'贝叶斯优化 {SUMMARY["calendar_days"]:.0f} → '
             f'{SUMMARY["bo_experiments_expected"] / (SUMMARY["experiments_per_day"] * 0.72):.1f} 天',
             transform=left.transAxes, size=11, ha='center', va='top')
    stages = ['移液', '表征']
    values = [4608, 48]
    right.bar(stages, values, color=[COL['green'], COL['purple']],
              edgecolor=COL['line'], linewidth=.9, width=.55)
    right.set_yscale('log')
    right.set_ylim(10, 20000)
    right.set_ylabel('能力（个/天，对数轴）')
    right.set_title('(b) 移液与表征能力', size=11)
    for i, value in enumerate(values):
        right.text(i, value * 1.25, f'{value}', size=11, ha='center')
    right.text(0.5, 0.30, '差距约 96 倍', transform=right.transAxes, size=11,
               ha='center')
    fig.text(0.5, 0.93, 'Worked example：名义与有效速率、瓶颈对比', size=12,
             ha='center', weight='bold')
    exp.save(fig, 'figure-13-8-worked', badge='CALC')


def figure_breakeven(exp):
    fig, ax = plot(height=3.8, left=.15, bottom=.20)
    fixed = 1e6 / (5 * 365) + 2000 + 1000
    n = np.linspace(5, 60, 300)
    ax.plot(n, fixed / n, color=COL['blue'], lw=2.2, label='自动化')
    ax.axhline(200, color=COL['orange'], lw=2.0, ls='--',
               label='人工（200 元/点）')
    ax.plot([fixed / 200], [200], 'o', color=COL['ink'], ms=6, zorder=5)
    ax.axvline(fixed / 200, color=COL['line'], lw=.8, ls=':')
    ax.set_xlim(5, 60)
    ax.set_ylim(0, 750)
    ax.set_xlabel('每日有效数据点数')
    ax.set_ylabel('单点成本（元）')
    ax.legend(loc='upper right', frameon=False)
    ax.text(fixed / 200 + 1.5, 235, f'盈亏平衡 {fixed / 200:.1f} 点/天',
            size=11)
    ax.text(36, fixed / 36 + 22, '98.6', size=11, ha='center')
    exp.save(fig, 'figure-13-9-breakeven', badge='CALC')


def main():
    exp = Exporter(HERE)
    figure_loop(exp)
    figure_throughput(exp)
    figure_software_stack(exp)
    figure_hardware(exp)
    figure_scheduler(exp)
    figure_reliability(exp)
    figure_cases(exp)
    figure_worked(exp)
    figure_breakeven(exp)
    exp.finish()
    index = [
        {'figure': '13-1', 'asset': 'ch13/figure-13-1-loop.svg'},
        {'figure': '13-2', 'asset': 'ch13/figure-13-2-throughput.svg'},
        {'figure': '13-3', 'asset': 'ch13/figure-13-3-software-stack.svg'},
        {'figure': '13-4', 'asset': 'ch13/figure-13-4-hardware.svg'},
        {'figure': '13-5', 'asset': 'ch13/figure-13-5-scheduler.svg'},
        {'figure': '13-6', 'asset': 'ch13/figure-13-6-reliability.svg'},
        {'figure': '13-7', 'asset': 'ch13/figure-13-7-cases.svg'},
        {'figure': '13-8', 'asset': 'ch13/figure-13-8-worked.svg'},
        {'figure': '13-9', 'asset': 'ch13/figure-13-9-breakeven.svg'},
    ]
    (HERE / 'figure-index.json').write_text(
        json.dumps(index, ensure_ascii=False, indent=2) + '\n')
    for record in exp.checks:
        print(f"{record['figure']}: min label {record['min_label_pt']:.0f} pt, "
              f"{len(record['text_extent_warnings'])} warnings")


if __name__ == '__main__':
    main()
