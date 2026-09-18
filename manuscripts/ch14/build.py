#!/usr/bin/env python3
"""Build chapter-fourteen teaching figures from fixed book evidence.

Usage: python manuscripts/ch14/build.py [--font /path/to/CJK-font.ttf]
"""
from pathlib import Path
import argparse
import hashlib
import json
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE.parent))

import matplotlib.pyplot as plt
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

GNN = json.loads((ROOT / 'calculations/results/gnn-forward-4layer.json').read_text())['summary']
GNN_FLOPS = GNN['total_flops']
GNN_PARAMS = GNN['parameters']
BIG_P = 1.1e8
SMALL_P = 1e7
WEIGHT_MB = BIG_P * 2 / 1e6


def two_panel(height=3.6, wspace=0.34, left=0.11, right=0.97):
    fig, axes = plt.subplots(1, 2, figsize=(420 / 72, height))
    fig.subplots_adjust(left=left, right=right, bottom=0.20, top=0.92, wspace=wspace)
    return fig, axes


def unit_panel(ax):
    ax.set(xlim=(0, 1), ylim=(0, 1))
    ax.axis('off')


def figure_14_1_stack(exp):
    fig, ax = canvas(height=3.5)
    D.layers(ax, [
        ('基础模型', 'PSMILES → 结构表示', '', 'blue'),
        ('检索', '查询 → 文献片段', '', 'green'),
        ('工具', '参数 → 性质/路线', '', 'orange'),
        ('编排', '任务描述 → 调用序列', '', 'purple'),
    ], y0=0.22, step=0.16, h=0.12, name_size=12)
    text(ax, 0.5, 0.94, '基础模型与智能体栈', size=13, ha='center', weight='bold')
    text(ax, 0.5, 0.09, '自下而上为能力来源，自上而下为一次任务的调用链',
         size=11, ha='center')
    arrow(ax, (0.90, 0.80), (0.90, 0.20), kind='control')
    text(ax, 0.945, 0.50, '调用链', size=11, rotation=90, ha='center')
    exp.save(fig, 'figure-14-1-stack', badge='SCHEMATIC')


def figure_14_2_agent_loop(exp):
    fig, ax = canvas(height=3.6)
    D.cycle(ax, [
        ('理解', '解析任务'),
        ('规划', '拆解步骤'),
        ('调用', '执行工具'),
        ('观察', '校验结果'),
        ('终止', '交付答案'),
    ], center=(0.36, 0.54), rx=0.23, ry=0.25, w=0.21, h=0.12)
    text(ax, 0.70, 0.86, '可用工具', size=12, weight='bold')
    for i, tool in enumerate(['性质预测', '逆合成', '数据库查询', '文献检索']):
        box(ax, 0.70, 0.70 - i * 0.14, 0.27, 0.10, tool, 'gray', size=11)
    text(ax, 0.5, 0.06, '失败时先检查工具选择错误还是参数错误',
         size=11, ha='center')
    exp.save(fig, 'figure-14-2-agent-loop', badge='SCHEMATIC')


def figure_14_3_rag(exp):
    fig, ax = canvas(height=3.4)
    D.pipeline(ax, ['文献切块', '向量化', '检索', '拼接', '生成'],
               y=0.60, h=0.14, back=[(4, 2)])
    text(ax, 0.5, 0.92, '检索增强生成流程', size=13, ha='center', weight='bold')
    text(ax, 0.5, 0.28, '仅依据检索证据时，命中质量限制答案事实性', size=11, ha='center')
    exp.save(fig, 'figure-14-3-rag', badge='SCHEMATIC')


def figure_14_4_model_taxonomy(exp):
    fig, ax = canvas(height=3.4)
    rows = [
        ['字符串', 'PSMILES → 掩码', '性质、表示', '$10^{8}$'],
        ['图', '原子-键图 → 掩码', '拓扑性质', '$10^{7}$'],
        ['三维', '构象 → 去噪', '几何、构象', '$10^{6}$'],
        ['多模态', '结构 + 文本 → 对比', '跨模态检索', '$10^{6}$'],
    ]
    D.table(ax, ['模型族', '输入 → 预训练目标', '能做什么', '数据规模'],
            rows, y_top=0.80, row_h=0.155, col_x=[0.10, 0.37, 0.66, 0.89])
    text(ax, 0.5, 0.93, '基础模型的谱系与能力边界', size=13, ha='center', weight='bold')
    text(ax, 0.5, 0.07,
         '按任务需要的结构信息选模型；数据规模为量级示意',
         size=11, ha='center')
    exp.save(fig, 'figure-14-4-model-taxonomy', badge='SCHEMATIC')


def figure_14_5_rag_pipeline(exp):
    fig, ax = canvas(height=3.0)
    steps = ['解析', '切块', '向量化', '检索', '重排', '生成', '引用']
    D.pipeline(ax, steps, y=0.62, h=0.14)
    text(ax, 0.5, 0.93, '科学检索增强生成的分步管线', size=13, ha='center', weight='bold')
    x0, x1, gap, n = 0.03, 0.97, 0.02, len(steps)
    w = (x1 - x0 - gap * (n - 1)) / n
    notes = {1: '切断证据', 3: '漏召', 5: '混入参数知识'}
    for index, note in notes.items():
        cx = x0 + index * (w + gap) + w / 2
        text(ax, cx, 0.38, note, size=11, ha='center')
        arrow(ax, (cx, 0.46), (cx, 0.55), kind='control')
    text(ax, 0.5, 0.16,
         '答案错误时从右向左定位：先看引用，再看检索，最后看切块',
         size=11, ha='center')
    exp.save(fig, 'figure-14-5-rag-pipeline', badge='SCHEMATIC')


def figure_14_6_retrieval_eval(exp):
    fig, axes = two_panel(height=3.4, left=0.12, right=0.97, wspace=0.38)
    alpha, relevant = 0.5, 2.0
    ks = list(range(1, 21))
    recall = [(1 - alpha ** k) for k in ks]
    precision = [min(relevant, 2 * (1 - alpha ** k)) / k for k in ks]
    axes[0].plot(ks, recall, marker='o', markersize=3.5, linewidth=1.2,
                 color=COL['line'], markerfacecolor=COL['blue'], label='召回率')
    axes[0].plot(ks, precision, marker='s', markersize=3.5, linewidth=1.2,
                 color='#c0392b', markerfacecolor=COL['orange'], label='精度')
    axes[0].set_xlabel('top-k', fontsize=11)
    axes[0].set_ylabel('指标值', fontsize=11)
    axes[0].set_ylim(0, 1.05)
    axes[0].tick_params(labelsize=11)
    axes[0].legend(fontsize=11, loc='center right')
    axes[0].spines[['top', 'right']].set_visible(False)
    axes[0].set_title('(a)', fontsize=12)
    axes[0].text(0.03, 0.86, 'alpha=0.5', transform=axes[0].transAxes,
                 fontsize=11)
    r = [i / 50 for i in range(51)]
    axes[1].plot(r, r, color=COL['line'], linewidth=1.4)
    axes[1].fill_between(r, 0, r, color=COL['green'], alpha=0.5)
    axes[1].set_xlabel('检索命中率 r', fontsize=11)
    axes[1].set_ylabel('事实性上界 F', fontsize=11)
    axes[1].set_xlim(0, 1)
    axes[1].set_ylim(0, 1.05)
    axes[1].tick_params(labelsize=11)
    axes[1].spines[['top', 'right']].set_visible(False)
    axes[1].set_title('(b)', fontsize=12)
    axes[1].text(0.42, 0.20, '可行区 F ≤ r', fontsize=11)
    axes[1].text(0.05, 0.88, '设定：仅依据检索证据回答', fontsize=11)
    exp.save(fig, 'figure-14-6-retrieval-eval', badge='CALC')


def figure_14_7_workflow(exp):
    fig, ax = canvas(height=4.5)
    steps = [
        ('1 任务解析', '语言模型', '目标歧义'),
        ('2 结构构建', '单体识别 + PSMILES', '单体认错、连接点写错'),
        ('3 拓扑生成', '链构建器', '立构规整度缺失'),
        ('4 装盒', '装盒工具', '密度单位错、链重叠'),
        ('5 模拟', 'GROMACS', '力场缺参数、温控/压控错'),
        ('6 分析', '密度分析', '平衡未达、区间选错'),
        ('7 拟合', '分段线性拟合', '拟合区间主观、降温速率偏差'),
        ('8 报告', '模板', '把模拟值当成实验值'),
    ]
    y0, step, h = 0.075, 0.104, 0.088
    for i, (name, tool, fail) in enumerate(steps):
        y = y0 + (len(steps) - 1 - i) * step
        box(ax, 0.03, y, 0.30, h, name, 'blue', size=11)
        text(ax, 0.37, y + h / 2 + 0.020, '工具：' + tool, size=11)
        text(ax, 0.37, y + h / 2 - 0.020, '失败点：' + fail, size=11)
        if i < len(steps) - 1:
            arrow(ax, (0.18, y), (0.18, y - step + h))
    text(ax, 0.03, 0.965, '智能体工作流的分步解剖（以模拟 PMMA 的 Tg 为例）',
         size=12, weight='bold')
    exp.save(fig, 'figure-14-7-workflow', badge='SCHEMATIC')


def figure_14_8_multiagent(exp):
    fig, axes = two_panel(height=3.6, left=0.10, right=0.97, wspace=0.40)
    unit_panel(axes[0])
    w, h = 0.13, 0.11
    square = [(0.15, 0.70), (0.37, 0.70), (0.15, 0.44), (0.37, 0.44)]
    for i, (xi, yi) in enumerate(square):
        for xj, yj in square[i + 1:]:
            axes[0].plot([xi, xj], [yi, yj], color=COL['line'], lw=.8, zorder=0)
    for xi, yi in square:
        box(axes[0], xi - w / 2, yi - h / 2, w, h, '', 'blue')
    axes[0].text(0.26, 0.88, 'all-to-all：6 条边', size=11, ha='center')
    axes[0].set_title('(a)', fontsize=12)
    cx, cy = 0.76, 0.57
    leaves = [(0.62, 0.80), (0.90, 0.80), (0.62, 0.34), (0.90, 0.34)]
    for lx, ly in leaves:
        axes[0].plot([cx, lx], [cy, ly], color=COL['line'], lw=.8, zorder=0)
    box(axes[0], cx - 0.09, cy - h / 2, 0.18, h, '调度', 'orange', size=11)
    for lx, ly in leaves:
        box(axes[0], lx - w / 2, ly - h / 2, w, h, '', 'green')
    axes[0].text(0.76, 0.10, '中心调度：4 条边', size=11, ha='center')
    ks = list(range(2, 33))
    all2all = [k * (k - 1) / 2 for k in ks]
    central = [k - 1 for k in ks]
    axes[1].plot(ks, all2all, color=COL['line'], linewidth=1.4, linestyle='-',
                 marker='o', markersize=3, label='all-to-all')
    axes[1].plot(ks, central, color='#c0392b', linewidth=1.4, linestyle='--',
                 marker='s', markersize=3, label='中心调度')
    axes[1].set_title('(b)', fontsize=12)
    axes[1].set_xlabel('角色数 k', fontsize=11)
    axes[1].set_ylabel('通信边数', fontsize=11)
    axes[1].tick_params(labelsize=11)
    axes[1].legend(fontsize=11, loc='upper left')
    axes[1].spines[['top', 'right']].set_visible(False)
    axes[1].text(0.22, 0.62, 'all-to-all ~ k(k-1)/2', transform=axes[1].transAxes,
                 fontsize=11)
    axes[1].text(0.22, 0.50, '中心调度 ~ k-1', transform=axes[1].transAxes,
                 fontsize=11)
    exp.save(fig, 'figure-14-8-multiagent', badge='CALC')


def figure_14_9_eval_metrics(exp):
    fig, ax = canvas(height=3.4)
    rows = [
        ['任务成功率', '规划与分解', '端到端日志'],
        ['科学正确性', '工具与解释', '专家复核'],
        ['工具执行准确率', '参数', '调用日志'],
        ['可复现性', '随机性', '重复执行'],
        ['幻觉率', '生成', '抽样复核'],
    ]
    D.table(ax, ['指标', '覆盖的失败', '采集方式'], rows,
            y_top=0.78, row_h=0.135, col_x=[0.18, 0.48, 0.80])
    text(ax, 0.5, 0.93, '评测指标与失败模式', size=13, ha='center', weight='bold')
    text(ax, 0.5, 0.06,
         '报告得分必须同时报告评测设定（工具集、提示模板、最大步数、重试次数）',
         size=11, ha='center')
    exp.save(fig, 'figure-14-9-eval-metrics', badge='SCHEMATIC')


def figure_14_10_cost_success(exp):
    fig, axes = two_panel(height=3.6, left=0.12, right=0.97, wspace=0.36)
    ns = [64, 128, 256, 512, 1024, 2048]
    axes[0].loglog(ns, [2 * n * BIG_P for n in ns], marker='o', markersize=4,
                   linewidth=1.2, color=COL['line'], markerfacecolor=COL['blue'],
                   label='P = 1.1e8')
    axes[0].loglog(ns, [2 * n * SMALL_P for n in ns], marker='s', markersize=4,
                   linewidth=1.2, color='#c0392b', markerfacecolor=COL['orange'],
                   label='P = 1e7')
    axes[0].axhline(GNN_FLOPS, color=COL['gray'], linewidth=1.4, linestyle='--')
    axes[0].set_xlabel('token 数 N', fontsize=11)
    axes[0].set_ylabel('前向 FLOPs', fontsize=11)
    axes[0].set_ylim(1e8, 1e12)
    axes[0].tick_params(labelsize=11)
    axes[0].legend(fontsize=11, loc='upper left')
    axes[0].spines[['top', 'right']].set_visible(False)
    axes[0].text(0.03, 0.16, '虚线：GNN 前向 3.3e8', transform=axes[0].transAxes,
                 fontsize=11)
    axes[0].set_title('(a)', fontsize=12)
    ls = list(range(1, 21))
    for p, color, style in [(0.95, COL['line'], '-'), (0.99, '#c0392b', '--'),
                            (0.999, '#2e7d32', ':')]:
        axes[1].plot(ls, [p ** L for L in ls], linewidth=1.3, color=color,
                     linestyle=style, label='p = ' + str(p))
    axes[1].axvline(10, color=COL['gray'], linewidth=1.0, linestyle=':')
    axes[1].set_xlabel('调用链长度 L', fontsize=11)
    axes[1].set_ylabel('端到端成功率', fontsize=11)
    axes[1].set_ylim(0, 1.02)
    axes[1].tick_params(labelsize=11)
    axes[1].legend(fontsize=11, loc='lower left')
    axes[1].spines[['top', 'right']].set_visible(False)
    axes[1].text(0.05, 0.55, 'p=0.95\nL=10 → 0.60', transform=axes[1].transAxes,
                 fontsize=11)
    axes[1].set_title('(b)', fontsize=12)
    exp.save(fig, 'figure-14-10-cost-success', badge='CALC')


def main():
    exp = Exporter(HERE)
    figure_14_1_stack(exp)
    figure_14_2_agent_loop(exp)
    figure_14_3_rag(exp)
    figure_14_4_model_taxonomy(exp)
    figure_14_5_rag_pipeline(exp)
    figure_14_6_retrieval_eval(exp)
    figure_14_7_workflow(exp)
    figure_14_8_multiagent(exp)
    figure_14_9_eval_metrics(exp)
    figure_14_10_cost_success(exp)
    exp.finish()
    index = [
        {'figure': '14-1', 'asset': 'ch14/figure-14-1-stack.svg'},
        {'figure': '14-2', 'asset': 'ch14/figure-14-2-agent-loop.svg'},
        {'figure': '14-3', 'asset': 'ch14/figure-14-3-rag.svg'},
        {'figure': '14-4', 'asset': 'ch14/figure-14-4-model-taxonomy.svg'},
        {'figure': '14-5', 'asset': 'ch14/figure-14-5-rag-pipeline.svg'},
        {'figure': '14-6', 'asset': 'ch14/figure-14-6-retrieval-eval.svg'},
        {'figure': '14-7', 'asset': 'ch14/figure-14-7-workflow.svg'},
        {'figure': '14-8', 'asset': 'ch14/figure-14-8-multiagent.svg'},
        {'figure': '14-9', 'asset': 'ch14/figure-14-9-eval-metrics.svg'},
        {'figure': '14-10', 'asset': 'ch14/figure-14-10-cost-success.svg'},
    ]
    (HERE / 'figure-index.json').write_text(
        json.dumps(index, ensure_ascii=False, indent=2) + '\n')
    for record in exp.checks:
        print(f"{record['figure']}: min label {record['min_label_pt']:.0f} pt, "
              f"{len(record['text_extent_warnings'])} warnings")


if __name__ == '__main__':
    main()
