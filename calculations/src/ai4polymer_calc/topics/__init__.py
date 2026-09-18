"""Polymer representation, model and closed-loop topics reuse shared records."""
from . import (bo_variants, chemical_space, closed_loop, descriptor_budget,
               gnn_forward, learning_curve, md_cost, pareto_screen,
               polymerization, robust_ranking, synthesis_route)

TOPICS = (
    ("descriptor-budget", descriptor_budget,
     "表示维度、每分子存储与折叠指纹的生日碰撞预算"),
    ("chemical-space", chemical_space,
     "共聚物序列空间规模、规则式可合成比例与已知库覆盖"),
    ("md-cost", md_cost,
     "MD/MLFF/DFT 声明成本模型到 GPU 小时与能耗"),
    ("gnn-forward", gnn_forward,
     "消息传递 GNN 参数量与逐项前向 FLOPs，含 Transformer 基线"),
    ("learning-curve", learning_curve,
     "幂律学习曲线反解所需训练规模与边际数据"),
    ("closed-loop", closed_loop,
     "随机搜索与贝叶斯优化的样本效率与日历时间对比"),
    ("pareto-screen", pareto_screen,
     "两嵌段设计空间的精确枚举、Pareto 前沿、超体积与标量化覆盖"),
    ("robust-ranking", robust_ranking,
     "均值加区间的候选排序、规范窗概率与排序翻转"),
    ("polymerization", polymerization,
     "逐步与活性聚合的动力学、Flory/Poisson 分子量分布与 Mayo-Lewis 共聚"),
    ("synthesis-route", synthesis_route,
     "逆合成穷举与束搜索代价、路线产率衰减与四级可行性漏斗"),
    ("bo-variants", bo_variants,
     "批量、约束、多保真与成本感知贝叶斯优化的闭式核算"),
)

TOPIC_MODULES = {name: module for name, module, _ in TOPICS}
TOPIC_DESCRIPTIONS = {name: description for name, _, description in TOPICS}
