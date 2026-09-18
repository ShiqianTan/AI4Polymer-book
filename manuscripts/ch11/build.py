#!/usr/bin/env python3
"""Build chapter-eleven teaching figures from fixed book evidence.

Usage: python manuscripts/ch11/build.py [--font /path/to/CJK-font.ttf]
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
VARIANTS = json.loads(
    (ROOT / 'calculations/results/bo-variants.json').read_text())['summary']


def panels(height=4.5, left=.13, right=.95, bottom=.11, top=.94, hspace=0.55):
    fig, axes = plt.subplots(2, 1, figsize=(420 / 72, height))
    fig.subplots_adjust(left=left, right=right, bottom=bottom, top=top,
                        hspace=hspace)
    for ax in axes:
        ax.spines[['top', 'right']].set_visible(False)
    return fig, axes


def figure_closed_loop(exp):
    fig, ax = canvas(height=4.0)
    items = [('数据', '实验/模拟样本'), ('代理模型', '预测 + 不确定度'),
             ('采集函数', 'EI / UCB'), ('评估', '真实评估')]
    D.cycle(ax, items, center=(0.5, 0.55), rx=0.30, ry=0.25, w=0.24, h=0.12,
            color='blue', size=12)
    arrow(ax, (0.34, 0.55), (0.66, 0.55), kind='control')
    text(ax, 0.5, 0.47, '模型更新（重训代理）', size=11, ha='center')
    arrow(ax, (0.08, 0.055), (0.92, 0.055))
    text(ax, 0.5, 0.115, '预算消耗：每次评估消耗一次实验预算', size=11, ha='center')
    exp.save(fig, 'figure-11-1-closed-loop-optimization', badge='SCHEMATIC')


def figure_acquisition(exp):
    xt = np.array([0.10, 0.30, 0.55, 0.80, 0.93])
    yt = np.array([0.10, 0.85, 0.25, 1.00, 0.60])
    xs = np.linspace(0.0, 1.0, 400)

    def kernel(a, b, length=0.14):
        return np.exp(-0.5 * ((a[:, None] - b[None, :]) / length) ** 2)

    K = kernel(xt, xt) + 0.02 * np.eye(len(xt))
    Ks = kernel(xs, xt)
    with np.errstate(divide='ignore', over='ignore', invalid='ignore'):
        mu = Ks @ np.linalg.solve(K, yt)
        cov = kernel(xs, xs) - Ks @ np.linalg.solve(K, Ks.T)
    sd = np.sqrt(np.clip(np.diag(cov), 1e-9, None))

    fig, (top, bot) = panels()
    top.fill_between(xs, mu - 2 * sd, mu + 2 * sd, color=COL['blue'], zorder=1)
    top.plot(xs, mu, color=COL['line'], lw=1.7, zorder=3)
    top.plot(xt, yt, 'o', color=COL['ink'], ms=5, zorder=4)
    top.set_xlim(0, 1)
    top.set_ylim(-0.5, 1.85)
    top.set_ylabel('目标值 $f(x)$')
    top.tick_params(labelbottom=False)
    top.text(0.03, 1.45, '后验均值与 95% 置信带', size=11)
    top.text(0.03, 1.20, '● 已观测数据点', size=11)
    top.text(0.02, 0.97, '(a)', transform=top.transAxes, size=12, weight='bold')

    fbest = yt.max()
    z = (mu - fbest) / sd
    phi = np.exp(-0.5 * z ** 2) / np.sqrt(2 * np.pi)
    cdf = 0.5 * (1 + np.vectorize(math.erf)(z / np.sqrt(2)))
    ei = (mu - fbest) * cdf + sd * phi
    ucb_small = mu + 0.5 * sd
    ucb_large = mu + 2.0 * sd

    def unit(v):
        return (v - v.min()) / (v.max() - v.min())

    ei_u, us_u, ul_u = unit(ei), unit(ucb_small), unit(ucb_large)
    bot.plot(xs, ei_u, color=COL['green'], lw=2.0, ls='-', label='EI（期望改进）')
    bot.plot(xs, us_u, color=COL['blue'], lw=2.0, ls='--', label='UCB, κ = 0.5')
    bot.plot(xs, ul_u, color=COL['orange'], lw=2.0, ls='-', label='UCB, κ = 2')
    i_ei, i_ucb = int(ei_u.argmax()), int(ul_u.argmax())
    bot.plot(xs[[i_ei, i_ucb]], [ei_u[i_ei], ul_u[i_ucb]], 'o',
             color=COL['ink'], ms=6, zorder=5)
    bot.axvline(xs[i_ei], color=COL['line'], lw=.8, ls=':')
    bot.axvline(xs[i_ucb], color=COL['line'], lw=.8, ls=':')
    bot.set_xlim(0, 1)
    bot.set_ylim(-0.62, 1.52)
    bot.set_xlabel('设计变量 $x$')
    bot.set_ylabel('归一化采集值')
    bot.legend(loc='lower center', frameon=False, ncol=3, handlelength=1.4,
               columnspacing=1.1)
    bot.text(0.02, 1.10, 'κ 越大越偏探索，选点移向高不确定区；\nκ 越小越偏利用，选点靠近后验峰值。',
             fontsize=11, ha='left', va='top')
    bot.text(0.02, 0.97, '(b)', transform=bot.transAxes, size=12, weight='bold')
    exp.save(fig, 'figure-11-2-acquisition', badge='SCHEMATIC')


def figure_convergence(exp):
    r_hit = SUMMARY['random_experiments_expected']
    b_hit = SUMMARY['bo_experiments_expected']
    speedup = SUMMARY['speedup_vs_random']
    per_day = SUMMARY['experiments_per_day']
    target = 1.0
    x = np.linspace(0, r_hit, 700)

    def curve(hit, exponent, start=0.10):
        return target - (target - start) * np.clip(1 - x / hit, 0, None) ** exponent

    y_random = curve(r_hit, 1.4)
    y_bo = curve(b_hit, 2.2)
    y_cost = curve(b_hit, 0.6)

    fig, ax = plot(height=3.5, left=.15, bottom=.19)
    ax.plot(x, y_random, color=COL['blue'], lw=2.0, ls='--', label='随机采样')
    ax.plot(x, y_cost, color=COL['green'], lw=2.0, ls='-.', label='成本感知')
    ax.plot(x, y_bo, color=COL['orange'], lw=2.4, ls='-', label='贝叶斯优化')
    ax.axhline(target, color=COL['line'], lw=.8, ls=':')
    ax.plot([r_hit, b_hit], [target, target], 'o', color=COL['ink'], ms=5)
    ax.set_xlim(0, r_hit * 1.02)
    ax.set_ylim(0, 1.18)
    ax.set_xlabel('累计成本（实验当量）')
    ax.set_ylabel('当前最优值（归一化）')
    ax.legend(loc='center right', frameon=False)
    ax.annotate('', xy=(r_hit, 0.28), xytext=(b_hit, 0.28),
                arrowprops=dict(arrowstyle='<->', color=COL['line'], lw=.9))
    ax.text((r_hit + b_hit) / 2, 0.34, f'加速 {speedup:.0f}×', size=11, ha='center')
    ax.text(r_hit - 15, target + 0.06, f'随机 {r_hit:.0f} 次', size=11, ha='right')
    ax.text(b_hit + 15, target + 0.06, f'贝叶斯优化 {b_hit:.0f} 次', size=11)
    ax.text(0.03, 0.06, f'闭环模型：{per_day:.0f} 次/天', size=11,
            ha='left', transform=ax.transAxes)
    exp.save(fig, 'figure-11-3-convergence', badge='CALC')


def _gp_posterior():
    xt = np.array([0.10, 0.30, 0.55, 0.80, 0.93])
    yt = np.array([0.10, 0.85, 0.25, 1.00, 0.60])
    xs = np.linspace(0.0, 1.0, 400)

    def kernel(a, b, length=0.14):
        return np.exp(-0.5 * ((a[:, None] - b[None, :]) / length) ** 2)

    K = kernel(xt, xt) + 0.02 * np.eye(len(xt))
    Ks = kernel(xs, xt)
    with np.errstate(divide='ignore', over='ignore', invalid='ignore'):
        mu = Ks @ np.linalg.solve(K, yt)
        cov = kernel(xs, xs) - Ks @ np.linalg.solve(K, Ks.T)
    sd = np.sqrt(np.clip(np.diag(cov), 1e-9, None))
    return xt, yt, xs, mu, sd


def figure_method_goals(exp):
    fig, ax = canvas(height=4.2)
    text(ax, 0.5, 0.955, '三类序贯方法：目标、反馈与决策结构', size=12, ha='center',
         weight='bold')
    headers = ['', '主动学习', '贝叶斯优化', '强化学习']
    rows = [
        ('目标', '降低模型误差', '找到最优解', '最大化累积回报'),
        ('决策对象', '选样本标注', '选点评估', '每一步动作'),
        ('反馈', '标签', '目标值', '奖励'),
        ('决策结构', '单步', '单步', '序列'),
    ]
    D.table(ax, headers, rows, y_top=0.78, row_h=0.145,
            col_x=[0.13, 0.39, 0.64, 0.87])
    text(ax, 0.04, 0.075, '三者的目标、反馈与决策结构并列对照。', size=11)
    exp.save(fig, 'figure-11-4-method-goals', badge='SCHEMATIC')


def figure_acquisition_tradeoffs(exp):
    xt, yt, xs, mu, sd = _gp_posterior()
    fig, (top, bot) = panels()
    top.fill_between(xs, mu - 2 * sd, mu + 2 * sd, color=COL['blue'], zorder=1)
    top.plot(xs, mu, color=COL['line'], lw=1.7, zorder=3)
    top.plot(xt, yt, 'o', color=COL['ink'], ms=5, zorder=4)
    top.set_xlim(0, 1)
    top.set_ylim(-0.5, 1.85)
    top.set_ylabel('目标值 $f(x)$')
    top.tick_params(labelbottom=False)
    top.text(0.03, 1.48, '后验均值与 95% 置信带', size=11)
    top.text(0.02, 0.97, '(a)', transform=top.transAxes, size=12, weight='bold')

    fbest = yt.max()
    z = (mu - fbest) / sd
    phi = np.exp(-0.5 * z ** 2) / np.sqrt(2 * np.pi)
    cdf = 0.5 * (1 + np.vectorize(math.erf)(z / np.sqrt(2)))
    ei = (mu - fbest) * cdf + sd * phi
    pi = cdf
    ucb = mu + 1.0 * sd

    def unit(v):
        return (v - v.min()) / (v.max() - v.min())

    ei_u, pi_u, ucb_u = unit(ei), unit(pi), unit(ucb)
    bot.plot(xs, ei_u, color=COL['green'], lw=2.0, ls='-', label='EI（期望改进）')
    bot.plot(xs, pi_u, color=COL['purple'], lw=2.0, ls=':', label='PI（改进概率）')
    bot.plot(xs, ucb_u, color=COL['blue'], lw=2.0, ls='--', label='UCB, κ = 1')
    i_ei, i_pi, i_ucb = (int(ei_u.argmax()), int(pi_u.argmax()),
                         int(ucb_u.argmax()))
    for idx, color in ((i_ei, COL['green']), (i_pi, COL['purple']),
                       (i_ucb, COL['blue'])):
        bot.plot(xs[idx], [ei_u[idx], pi_u[idx], ucb_u[idx]][
            (i_ei, i_pi, i_ucb).index(idx)], 'o', color=COL['ink'], ms=6,
            zorder=5)
        bot.axvline(xs[idx], color=color, lw=.8, ls=':')
    bot.set_xlim(0, 1)
    bot.set_ylim(-0.62, 1.52)
    bot.set_xlabel('设计变量 $x$')
    bot.set_ylabel('归一化采集值')
    bot.legend(loc='lower center', frameon=False, ncol=3, handlelength=1.4,
               columnspacing=1.1)
    bot.text(0.02, 1.28, 'EI 兼顾均值与方差；PI 偏好高方差区、忽略改进幅度；\n'
                         'UCB 的选点随 κ 在两区之间移动。',
             fontsize=11, ha='left', va='top')
    bot.text(0.02, 0.97, '(b)', transform=bot.transAxes, size=12, weight='bold')
    exp.save(fig, 'figure-11-5-acquisition-tradeoffs', badge='SCHEMATIC')


def figure_bo_extensions(exp):
    fig, ax = canvas(height=4.8)
    text(ax, 0.5, 0.955, '五类贝叶斯优化扩展：适用条件与失效模式', size=12,
         ha='center', weight='bold')
    headers = ['扩展', '适用条件', '主要失效模式']
    retained = VARIANTS['batch_information_retained']
    feasible = VARIANTS['expected_feasible_per_batch'] / 8.0
    speed = VARIANTS['fidelity_speedup']
    rows = [
        ('批量', '平台一轮跑一批', f'批内相关，保留 {retained:.0%}'),
        ('约束', '不可行代价高', f'可行域为空，浪费 {1 - feasible:.0%}'),
        ('多目标', '目标相互冲突', '只看超体积、忽略分布'),
        ('多保真', '低保真便宜', f'排序不一致，加速 {speed:.0f}'),
        ('成本感知', '成本差数量级', '成本模型失准'),
    ]
    D.table(ax, headers, rows, y_top=0.82, row_h=0.135,
            col_x=[0.17, 0.50, 0.82])
    text(ax, 0.04, 0.10, f'数值来自 bo-variants：批量保留 {retained:.0%}、',
         size=11)
    text(ax, 0.04, 0.05, f'可行率 {feasible:.0%}、多保真加速 {speed:.0f}。',
         size=11)
    exp.save(fig, 'figure-11-6-bo-extensions', badge='CALC')


def figure_worked_efficiency(exp):
    p = SUMMARY['hit_fraction']
    r_hit = SUMMARY['random_experiments_expected']
    b_hit = SUMMARY['bo_experiments_expected']
    n = np.linspace(0, 1300, 600)
    fig, (left, right) = plt.subplots(1, 2, figsize=(420 / 72, 3.7))
    fig.subplots_adjust(left=.11, right=.97, bottom=.28, top=.90, wspace=.42)
    for ax in (left, right):
        ax.spines[['top', 'right']].set_visible(False)

    left.plot(n, 1 - (1 - p) ** n, color=COL['blue'], lw=2.0, ls='--',
              label='随机采样')
    left.plot(n, 1 - (1 - 5 * p) ** n, color=COL['orange'], lw=2.2, ls='-',
              label='贝叶斯优化')
    left.axhline(1.0, color=COL['line'], lw=.8, ls=':')
    left.axvline(r_hit, color=COL['line'], lw=.8, ls=':')
    left.axvline(b_hit, color=COL['line'], lw=.8, ls=':')
    left.set_xlabel('实验次数')
    left.set_ylabel('至少命中一次的概率')
    left.set_ylim(0, 1.08)
    left.legend(loc='lower right', frameon=False)
    left.text(r_hit - 20, 0.42, f'{r_hit:.0f}', size=11, ha='right')
    left.text(b_hit + 20, 0.20, f'{b_hit:.0f}', size=11)
    left.set_title('闭环命中概率', size=11)
    left.text(0.02, 0.92, '(a)', transform=left.transAxes, size=12, weight='bold')

    labels = ['批量', '约束', '多保真', '成本感知']
    values = [VARIANTS['batch_information_retained'],
              VARIANTS['expected_feasible_per_batch'] / 8.0,
              VARIANTS['ladder_cost_high_fidelity_equivalent'],
              VARIANTS['cost_aware_information_threshold']]
    colors = [COL['green'], COL['blue'], COL['orange'], COL['purple']]
    right.bar(range(len(values)), values, color=colors, edgecolor=COL['line'],
              linewidth=.9, width=.6, zorder=2)
    right.set_xticks(range(len(labels)))
    right.set_xticklabels(labels, fontsize=11)
    fig.text(0.5, 0.05, '依次为：信息保留、可行比例、成本当量、信息阈值',
             ha='center', size=11)
    right.set_ylim(0, 0.42)
    right.set_ylabel('比例')
    right.set_title('扩展核算', size=11)
    right.text(0.02, 0.92, '(b)', transform=right.transAxes, size=12, weight='bold')
    for i, v in enumerate(values):
        right.text(i, v + 0.012, f'{v:.2f}', size=11, ha='center')
    exp.save(fig, 'figure-11-8-worked-efficiency', badge='CALC')


def figure_rl_boundary(exp):
    fig, ax = canvas(height=4.9)
    text(ax, 0.5, 0.965, '强化学习的适用边界与三类算法', size=12, ha='center',
         weight='bold')
    box(ax, 0.36, 0.83, 0.28, 0.09, '决策结构', 'gray', size=11)
    box(ax, 0.06, 0.68, 0.26, 0.09, '单步：BO / 条件生成', 'blue', size=11)
    box(ax, 0.62, 0.68, 0.32, 0.09, '序列：强化学习或树搜索', 'orange', size=11)
    arrow(ax, (0.44, 0.83), (0.19, 0.77))
    arrow(ax, (0.56, 0.83), (0.78, 0.77))
    box(ax, 0.62, 0.585, 0.14, 0.08, '能在线交互', 'green', size=11)
    box(ax, 0.80, 0.585, 0.17, 0.08, '只能离线', 'purple', size=11)
    arrow(ax, (0.70, 0.68), (0.69, 0.625))
    arrow(ax, (0.82, 0.68), (0.88, 0.625))

    headers = ['算法', '数据来源', '样本效率', '主要风险']
    rows = [
        ('策略梯度 PPO', '在线交互', '低', '方差大'),
        ('Q 学习 DQN', '在线加回放', '中', '高估、稀疏奖励'),
        ('离线强化学习 CQL', '固定数据集', '高', '分布偏移'),
    ]
    D.table(ax, headers, rows, y_top=0.52, row_h=0.105,
            col_x=[0.20, 0.47, 0.70, 0.88])
    text(ax, 0.03, 0.90, '(a)', size=12, weight='bold')
    text(ax, 0.03, 0.555, '(b)', size=12, weight='bold')
    text(ax, 0.04, 0.075, '序列问题才考虑强化学习或树搜索。', size=11)
    exp.save(fig, 'figure-11-7-rl-boundary', badge='SCHEMATIC')


def figure_failure_modes(exp):
    fig, ax = canvas(height=4.2)
    text(ax, 0.5, 0.945, '四类失败模式与诊断信号', size=12, ha='center',
         weight='bold')
    headers = ['失败模式', '识别信号', '修法']
    rows = [
        ('代理外推失效', '选点距离大且采集值高', '分布外过滤、集成分歧'),
        ('采集退化', '方差项主导、选点聚集', '显式噪声、去相关'),
        ('约束无解', '可行比例低于阈值', '放宽约束、重参数化'),
        ('批次相关', '批内相似度高', '局部惩罚、行列式点过程'),
    ]
    D.table(ax, headers, rows, y_top=0.80, row_h=0.135,
            col_x=[0.19, 0.50, 0.81])
    text(ax, 0.04, 0.075, '四类失败的共同点是假设不成立，不是优化器不够强。',
         size=11)
    exp.save(fig, 'figure-11-9-failure-modes', badge='SCHEMATIC')


def main():
    exp = Exporter(HERE)
    figure_closed_loop(exp)
    figure_acquisition(exp)
    figure_convergence(exp)
    figure_method_goals(exp)
    figure_acquisition_tradeoffs(exp)
    figure_bo_extensions(exp)
    figure_worked_efficiency(exp)
    figure_rl_boundary(exp)
    figure_failure_modes(exp)
    exp.finish()
    index = [
        {'figure': '11-1', 'asset': 'ch11/figure-11-1-closed-loop-optimization.svg'},
        {'figure': '11-2', 'asset': 'ch11/figure-11-2-acquisition.svg'},
        {'figure': '11-3', 'asset': 'ch11/figure-11-3-convergence.svg'},
        {'figure': '11-4', 'asset': 'ch11/figure-11-4-method-goals.svg'},
        {'figure': '11-5', 'asset': 'ch11/figure-11-5-acquisition-tradeoffs.svg'},
        {'figure': '11-6', 'asset': 'ch11/figure-11-6-bo-extensions.svg'},
        {'figure': '11-7', 'asset': 'ch11/figure-11-7-rl-boundary.svg'},
        {'figure': '11-8', 'asset': 'ch11/figure-11-8-worked-efficiency.svg'},
        {'figure': '11-9', 'asset': 'ch11/figure-11-9-failure-modes.svg'},
    ]
    (HERE / 'figure-index.json').write_text(
        json.dumps(index, ensure_ascii=False, indent=2) + '\n')
    for record in exp.checks:
        print(f"{record['figure']}: min label {record['min_label_pt']:.0f} pt, "
              f"{len(record['text_extent_warnings'])} warnings")


if __name__ == '__main__':
    main()
