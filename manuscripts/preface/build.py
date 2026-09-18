#!/usr/bin/env python3
"""Build preface teaching figures from fixed book evidence.

Usage: python manuscripts/preface/build.py [--font /path/to/CJK-font.ttf]
"""
from pathlib import Path
import argparse
import hashlib
import json
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE.parent))

from matplotlib.patches import Circle, Rectangle

from figure_style import COL, Exporter, arrow, box, canvas, text

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

LANES = [
    ('材料背景读者', 'blue', ['第 1–4 章', '第 15 章\n（可持续）', '按需\n第 5–6 章']),
    ('计算与机器学习\n背景读者', 'green', ['第 1–3 章', '第 5–12 章', '第 16 章']),
    ('落地工程读者', 'orange', ['第 1、3 章', '第 10、11、\n13 章', '第 16 章']),
]


def figure_reading_paths(exp):
    fig, ax = canvas(height=4.0)
    text(ax, 0.04, 0.95, '三条读者路径', size=14, weight='bold')
    centers = [0.78, 0.50, 0.22]
    box_w, box_h = 0.18, 0.12
    xs = [0.40, 0.62, 0.84]
    for (label, color, chapters), cy in zip(LANES, centers):
        ax.add_patch(Rectangle((0.03, cy - 0.08), 0.94, 0.16,
                               facecolor=COL[color], edgecolor=COL['line'],
                               linewidth=.6))
        text(ax, 0.04, cy, label, size=12, weight='bold')
        ax.add_patch(Circle((0.275, cy), 0.011, facecolor=COL[color],
                            edgecolor=COL['line'], lw=.9, zorder=3))
        arrow(ax, (0.288, cy), (0.31, cy))
        for i, chapter in enumerate(chapters):
            box(ax, xs[i] - box_w / 2, cy - box_h / 2, box_w, box_h,
                chapter, 'white', size=11, edge=COL[color])
            if i < len(chapters) - 1:
                arrow(ax, (xs[i] + box_w / 2, cy),
                      (xs[i + 1] - box_w / 2, cy))
        arrow(ax, (xs[-1] + box_w / 2, cy), (0.962, cy))
    text(ax, 0.5, 0.045, '圆点为起点，箭头指向阅读顺序', size=11, ha='center')
    exp.save(fig, 'figure-0-1-reading-paths', badge='SCHEMATIC')


def main():
    exp = Exporter(HERE)
    figure_reading_paths(exp)
    exp.finish()
    index = [
        {'figure': '0-1', 'asset': 'preface/figure-0-1-reading-paths.svg'},
    ]
    (HERE / 'figure-index.json').write_text(
        json.dumps(index, ensure_ascii=False, indent=2) + '\n')
    for record in exp.checks:
        print(f"{record['figure']}: min label {record['min_label_pt']:.0f} pt, "
              f"{len(record['text_extent_warnings'])} warnings")


if __name__ == '__main__':
    main()
