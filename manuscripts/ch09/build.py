#!/usr/bin/env python3
"""Build chapter-nine teaching figures from fixed book evidence.

Usage: python manuscripts/ch09/build.py [--font /path/to/CJK-font.ttf]
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


def figure_generative_lineage(exp):
    fig, ax = canvas(height=3.9)
    models = ['VAE', 'GAN', '扩散与流', '自回归\n语言模型']
    x0, x1, gap, n = 0.14, 0.98, 0.014, len(models)
    w = (x1 - x0 - gap * (n - 1)) / n
    D.spectrum(ax, models, y=0.80, h=0.14, color='blue', size=11,
               x0=x0, x1=x1, gap=gap)
    box(ax, x0 + 2 * (w + gap), 0.73, w, 0.14, '扩散与流', 'orange', size=11)
    text(ax, 0.5, 0.95, '生成模型谱系：按采样代价与可控性定位', size=12,
         ha='center', weight='bold')
    rows = [
        ('数据需求', ['中', '中', '高', '高']),
        ('采样步数', ['1 步', '1 步', 'T 步', 'L 步']),
        ('可控性', ['中', '低', '高', '高']),
        ('多样性', ['中', '低', '高', '高']),
    ]
    ys = [0.52, 0.42, 0.32, 0.22]
    for (name, vals), y in zip(rows, ys):
        text(ax, 0.02, y, name, size=11)
        for i, v in enumerate(vals):
            text(ax, x0 + i * (w + gap) + w / 2, y, v, size=11, ha='center')
    text(ax, 0.5, 0.08, 'T 为去噪步数，L 为序列长度；低/中/高为定性比较',
         size=11, ha='center')
    exp.save(fig, 'figure-9-1-generative-lineage', badge='SCHEMATIC')


def figure_diffusion(exp):
    fig, ax = canvas(height=4.2)
    ax.plot([0.08, 0.94], [0.50, 0.50], color=COL['line'], lw=1)
    arrow(ax, (0.08, 0.50), (0.95, 0.50))
    text(ax, 0.93, 0.44, '时间 t', size=11, ha='right')
    nodes = [(0.10, 'x_0'), (0.45, 'x_t'), (0.80, 'x_T')]
    for x, label in nodes:
        box(ax, x, 0.755, 0.14, 0.11, f'${label}$', 'blue', size=12)
    arrow(ax, (0.24, 0.81), (0.45, 0.81))
    arrow(ax, (0.59, 0.81), (0.80, 0.81))
    text(ax, 0.10, 0.92, '前向加噪（固定 $\\beta_t$）', size=11)
    for x, label in nodes:
        box(ax, x, 0.235, 0.14, 0.11, f'${label}$', 'green', size=12)
    arrow(ax, (0.80, 0.29), (0.59, 0.29))
    arrow(ax, (0.45, 0.29), (0.24, 0.29))
    text(ax, 0.10, 0.40, '反向去噪（学习 $p_\\theta$）', size=11)
    box(ax, 0.26, 0.05, 0.32, 0.12, '噪声预测网络 $\\epsilon_\\theta$', 'orange',
        size=11)
    arrow(ax, (0.44, 0.17), (0.45, 0.18))
    text(ax, 0.62, 0.10, '采样步数 $T$ 决定代价', size=11)
    exp.save(fig, 'figure-9-2-diffusion', badge='SCHEMATIC')


def figure_conditional_generation(exp):
    fig, ax = canvas(height=3.8)
    box(ax, 0.03, 0.66, 0.20, 0.13, '条件 $c$', 'green', size=12)
    box(ax, 0.31, 0.65, 0.24, 0.14, '生成器 $G(z\\,|\\,c)$', 'orange', size=12)
    box(ax, 0.63, 0.66, 0.24, 0.13, '候选结构', 'blue', size=12)
    box(ax, 0.63, 0.40, 0.24, 0.12, '性质预测器', 'blue', size=11)
    box(ax, 0.63, 0.16, 0.24, 0.12, '可合成性过滤', 'blue', size=11)
    arrow(ax, (0.23, 0.725), (0.31, 0.72))
    arrow(ax, (0.55, 0.72), (0.63, 0.725))
    arrow(ax, (0.75, 0.66), (0.75, 0.52))
    arrow(ax, (0.75, 0.40), (0.75, 0.28))
    arrow(ax, (0.63, 0.46), (0.55, 0.70), kind='control')
    text(ax, 0.44, 0.60, '验证回流', size=11, ha='center')
    text(ax, 0.75, 0.05, '输出可合成候选', size=11, ha='center')
    text(ax, 0.13, 0.83, '条件注入', size=11, ha='center')
    exp.save(fig, 'figure-9-3-conditional-generation', badge='SCHEMATIC')


def figure_generative_template(exp):
    fig, ax = canvas(height=4.3)
    text(ax, 0.5, 0.965, '生成模型族的统一模板', size=13, ha='center',
         weight='bold')
    D.pipeline(ax, ['基本思想', '目标', '采样', '优势', '弱点', '示例', '代码'],
               y=0.82, h=0.11, color='blue', size=11)
    text(ax, 0.5, 0.70, '逐项对齐：采样列决定代价，弱点列决定检查动作',
         size=11, ha='center')
    headers = ['模型族', '采样', '优势', '弱点']
    rows = [
        ('VAE', '1 步', '潜空间可插值', '后验坍塌'),
        ('GAN', '1 步', '样本清晰', '模式坍塌'),
        ('自回归', 'L 步', '精确似然', '暴露偏差'),
        ('扩散', 'T 步', '质量与可控性', '步数多'),
        ('流匹配', '50 步', '路径直、步数少', '需连续化'),
        ('掩码生成', 'R 轮', '支持补全', '轮数敏感'),
    ]
    D.table(ax, headers, rows, y_top=0.58, row_h=0.070,
            col_x=[0.15, 0.37, 0.63, 0.86])
    text(ax, 0.04, 0.055, '聚合物示例与代码示例见 9.7 至 9.12。', size=11)
    exp.save(fig, 'figure-9-4-generative-template', badge='SCHEMATIC')


def figure_vae_latent(exp):
    fig, ax = canvas(height=4.1)
    text(ax, 0.5, 0.965, 'VAE：ELBO 与潜空间', size=13, ha='center',
         weight='bold')
    text(ax, 0.02, 0.905, '(a)', size=12, weight='bold')
    text(ax, 0.02, 0.40, '(b)', size=12, weight='bold')
    box(ax, 0.04, 0.74, 0.18, 0.11, '编码器 $q_\\phi$', 'blue', size=11)
    box(ax, 0.28, 0.74, 0.18, 0.11, '重参数化', 'green', size=11)
    box(ax, 0.52, 0.74, 0.18, 0.11, '解码器 $p_\\theta$', 'blue', size=11)
    box(ax, 0.76, 0.74, 0.18, 0.11, '重建结构', 'orange', size=11)
    arrow(ax, (0.22, 0.795), (0.28, 0.795))
    arrow(ax, (0.46, 0.795), (0.52, 0.795))
    arrow(ax, (0.70, 0.795), (0.76, 0.795))
    box(ax, 0.04, 0.52, 0.42, 0.12, '重建项 $\\log p_\\theta(x\\mid z)$',
        'blue', size=11)
    box(ax, 0.54, 0.52, 0.42, 0.12, 'KL 项 $\\mathrm{KL}(q_\\phi\\,\\|\\,p)$',
        'green', size=11)
    ax.plot([0.10, 0.90], [0.30, 0.30], color=COL['line'], lw=1)
    for x, lab in [(0.10, '$z_1$'), (0.50, '$z$'), (0.90, '$z_2$')]:
        ax.scatter([x], [0.30], s=90, facecolor=COL['orange'],
                   edgecolor=COL['line'], zorder=4)
        text(ax, x, 0.22, lab, size=11, ha='center')
    text(ax, 0.5, 0.10, '潜空间插值：解码中间点扫描性质', size=11, ha='center')
    exp.save(fig, 'figure-9-5-vae-latent', badge='SCHEMATIC')


def figure_gan_game(exp):
    fig, ax = canvas(height=4.0)
    text(ax, 0.5, 0.965, 'GAN：博弈与模式坍塌', size=13, ha='center',
         weight='bold')
    text(ax, 0.02, 0.905, '(a)', size=12, weight='bold')
    text(ax, 0.02, 0.60, '(b)', size=12, weight='bold')
    box(ax, 0.05, 0.72, 0.20, 0.12, '生成器 $G$', 'blue', size=11)
    box(ax, 0.40, 0.72, 0.20, 0.12, '判别器 $D$', 'orange', size=11)
    box(ax, 0.73, 0.72, 0.22, 0.12, '真假分数', 'green', size=11)
    arrow(ax, (0.25, 0.78), (0.40, 0.78))
    arrow(ax, (0.60, 0.78), (0.73, 0.78))
    arrow(ax, (0.40, 0.72), (0.15, 0.72), kind='control')
    text(ax, 0.28, 0.64, '梯度回传', size=11, ha='center')
    ax.plot([0.06, 0.44], [0.34, 0.34], color=COL['line'], lw=1)
    text(ax, 0.06, 0.52, '数据分布', size=11)
    for cx, h in [(0.12, 0.14), (0.21, 0.10), (0.33, 0.13)]:
        box(ax, cx, 0.34, 0.055, h, '', 'blue')
    text(ax, 0.25, 0.22, '覆盖全部模式', size=11, ha='center')
    ax.plot([0.56, 0.94], [0.34, 0.34], color=COL['line'], lw=1)
    text(ax, 0.56, 0.52, '生成分布', size=11)
    for cx, h in [(0.62, 0.15), (0.67, 0.12)]:
        box(ax, cx, 0.34, 0.055, h, '', 'orange')
    text(ax, 0.75, 0.22, '只覆盖少数模式', size=11, ha='center')
    text(ax, 0.5, 0.09, '训练早期分布不重叠：JSD 梯度接近零，训练停滞',
         size=11, ha='center')
    exp.save(fig, 'figure-9-6-gan-game', badge='SCHEMATIC')


def figure_diffusion_flow(exp):
    fig, ax = plot(height=3.9, left=.16, bottom=.20)
    t = np.linspace(0, 1, 200)
    ax.plot(t, 1 - t, color=COL['green'], lw=2.2, label='流匹配（直线路径）')
    ax.plot(t, (1 - t) ** 0.55, color=COL['orange'], lw=2.2, ls='--',
            label='扩散（噪声路径）')
    ax.scatter([0, 1], [1, 0], s=60, facecolor=COL['blue'],
               edgecolor=COL['line'], zorder=4)
    ax.text(0.03, 0.93, '先验（噪声）', size=11)
    ax.text(0.74, 0.08, '数据', size=11)
    ax.text(0.50, 0.68, '扩散 T=1000 步', size=11, color=COL['orange'])
    ax.text(0.05, 0.42, '流匹配 50 步', size=11, color=COL['green'])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_xlabel('采样进程（先验 → 数据）')
    ax.set_ylabel('噪声水平')
    ax.legend(loc='upper right')
    exp.save(fig, 'figure-9-7-diffusion-flow', badge='SCHEMATIC')


def figure_masked_decoding(exp):
    fig, ax = canvas(height=3.8)
    text(ax, 0.5, 0.955, '掩码生成：迭代解码', size=13, ha='center',
         weight='bold')
    n = 6
    rows = [('第 0 轮', 0), ('第 1 轮', 2), ('第 2 轮', 4), ('第 3 轮', 6)]
    x0, cw, gap = 0.20, 0.10, 0.012
    for r, (label, filled) in enumerate(rows):
        y = 0.76 - r * 0.17
        text(ax, 0.17, y, label, size=11, ha='right')
        for i in range(n):
            color = 'gray' if i >= filled else 'blue'
            mark = 'M' if i >= filled else 'T'
            box(ax, x0 + i * (cw + gap), y - 0.055, cw, 0.11, mark, color,
                size=11)
        text(ax, 0.88, y, f'{filled}/{n}', size=11)
    text(ax, 0.5, 0.06, '每轮按置信度确定一部分 token，其余重新加掩',
         size=11, ha='center')
    exp.save(fig, 'figure-9-8-masked-decoding', badge='SCHEMATIC')


def figure_polymer_challenges(exp):
    fig, ax = canvas(height=4.4)
    text(ax, 0.5, 0.955, '高分子特有的生成挑战', size=13, ha='center',
         weight='bold')
    headers = ['挑战', '怎么检查', '失败后果']
    rows = [
        ('重复单元有效性', '价态 + 环闭合', '化学无效'),
        ('聚合连接性', '连接点成对', '无法成链'),
        ('组成', '摩尔分数对照', '性质偏移'),
        ('序列', '序列熵 / 嵌段', '分辨率错配'),
        ('架构', '支化 / 交联点', '流变偏离'),
        ('分子量', '长度分布距离', '性质系统偏移'),
        ('可合成性', '规则库 / SA 分', '预算浪费'),
    ]
    D.table(ax, headers, rows, y_top=0.84, row_h=0.088,
            col_x=[0.18, 0.52, 0.84])
    text(ax, 0.04, 0.045, '七项逐项检查；任一项失败，候选进不了筛选。', size=11)
    exp.save(fig, 'figure-9-9-polymer-challenges', badge='SCHEMATIC')


def figure_metric_pitfalls(exp):
    fig, ax = canvas(height=3.9)
    text(ax, 0.5, 0.955, '生成评价：指标与陷阱', size=13, ha='center',
         weight='bold')
    headers = ['指标', '陷阱', '检查动作']
    rows = [
        ('validity', '只查语法', '加价态检查'),
        ('uniqueness', '分母可选', '写清分母'),
        ('novelty', '依赖参照集', '写明参照集'),
        ('CSR', '生成器自报', '独立预测器'),
        ('可合成性', '代理指标', '写明代理类型'),
    ]
    D.table(ax, headers, rows, y_top=0.80, row_h=0.115,
            col_x=[0.20, 0.50, 0.80])
    text(ax, 0.04, 0.06, '五项一起报告，并给出采样参数与随机种子。', size=11)
    exp.save(fig, 'figure-9-10-metric-pitfalls', badge='SCHEMATIC')


def figure_conditional_failures(exp):
    fig, ax = canvas(height=4.2)
    text(ax, 0.5, 0.955, '条件生成：实现与失败模式', size=13, ha='center',
         weight='bold')
    text(ax, 0.16, 0.86, '条件注入', size=11, ha='center')
    box(ax, 0.03, 0.66, 0.28, 0.13, '性质条件\n拼接 / 注意力 / 引导',
        'blue', size=11)
    box(ax, 0.03, 0.48, 0.28, 0.13, '组成条件\ntoken / BigSMILES',
        'green', size=11)
    box(ax, 0.03, 0.30, 0.28, 0.13, '序列条件\n块边界 / 掩码 / 前缀',
        'orange', size=11)
    text(ax, 0.64, 0.86, '失败模式', size=11, ha='center')
    fails = [
        ('条件与预测器不匹配', '用同一模型定义与验证'),
        ('引导过度', '按可用候选数扫 w'),
        ('条件冲突', '分层：先硬过滤'),
        ('分布外条件', '检查是否在训练分布内'),
    ]
    for i, (name, check) in enumerate(fails):
        y = 0.72 - i * 0.155
        box(ax, 0.36, y - 0.055, 0.28, 0.11, name, 'gray', size=11)
        text(ax, 0.66, y, check, size=11)
    text(ax, 0.5, 0.06, '先确认条件的定义与验证用同一个独立模型',
         size=11, ha='center')
    exp.save(fig, 'figure-9-11-conditional-failures', badge='SCHEMATIC')


def main():
    exp = Exporter(HERE)
    figure_generative_lineage(exp)
    figure_diffusion(exp)
    figure_conditional_generation(exp)
    figure_generative_template(exp)
    figure_vae_latent(exp)
    figure_gan_game(exp)
    figure_diffusion_flow(exp)
    figure_masked_decoding(exp)
    figure_polymer_challenges(exp)
    figure_metric_pitfalls(exp)
    figure_conditional_failures(exp)
    exp.finish()
    index = [
        {'figure': '9-1', 'asset': 'ch09/figure-9-1-generative-lineage.svg'},
        {'figure': '9-2', 'asset': 'ch09/figure-9-2-diffusion.svg'},
        {'figure': '9-3', 'asset': 'ch09/figure-9-3-conditional-generation.svg'},
        {'figure': '9-4', 'asset': 'ch09/figure-9-4-generative-template.svg'},
        {'figure': '9-5', 'asset': 'ch09/figure-9-5-vae-latent.svg'},
        {'figure': '9-6', 'asset': 'ch09/figure-9-6-gan-game.svg'},
        {'figure': '9-7', 'asset': 'ch09/figure-9-7-diffusion-flow.svg'},
        {'figure': '9-8', 'asset': 'ch09/figure-9-8-masked-decoding.svg'},
        {'figure': '9-9', 'asset': 'ch09/figure-9-9-polymer-challenges.svg'},
        {'figure': '9-10', 'asset': 'ch09/figure-9-10-metric-pitfalls.svg'},
        {'figure': '9-11', 'asset': 'ch09/figure-9-11-conditional-failures.svg'},
    ]
    (HERE / 'figure-index.json').write_text(
        json.dumps(index, ensure_ascii=False, indent=2) + '\n')
    for record in exp.checks:
        print(f"{record['figure']}: min label {record['min_label_pt']:.0f} pt, "
              f"{len(record['text_extent_warnings'])} warnings")


if __name__ == '__main__':
    main()
