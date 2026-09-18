# polymerization — declared-step-growth-flory-mayo-lewis

输入：`{"copolymer_pairs": "0.1:0.1;1:1;10:0.1;0.1:10", "curve_points": 80, "drift_steps": 100, "feed_fraction": 0.5, "flory_conversion": 0.99, "living_conversion": 0.99, "living_ratios": "50,100,200", "max_conversion": 0.99, "poisson_mean_dp": 100, "step_conversions": "0.9,0.99,0.999"}`

| 来源 | 标题 | URL | 访问日期 |
| --- | --- | --- | --- |
| flory-1940 | Flory, Molecular Size Distribution in Ethylene Oxide Polymers, J. Am. Chem. Soc. 1940 | https://pubs.acs.org/doi/10.1021/ja01863a066 | 2026-09-17 |
| mayo-lewis-1944 | Mayo & Lewis, Copolymerization. I. A Basis for Comparing the Behavior of Monomers in Copolymerization, J. Am. Chem. Soc. 1944 | https://pubs.acs.org/doi/10.1021/ja01237a052 | 2026-09-17 |
| matyjaszewski-2001 | Matyjaszewski & Xia, Atom Transfer Radical Polymerization, Chem. Rev. 2001 | https://pubs.acs.org/doi/10.1021/cr940534g | 2026-09-17 |

## 结果

| 结果 | 值 |
| --- | ---: |

## 假设与边界

- 逐步聚合采用 Carothers 关系 $\bar X_n=1/(1-p)$ 与最可几 Flory 分布；$\bar X_w=(1+p)/(1-p)$，故分散度 $\bar X_w/\bar X_n=1+p$，$p\to1$ 时趋近 2。
- 活性/可控聚合采用 Poisson 链长分布：$\nu$ 为单体与引发剂投料比乘转化率，$\bar X_n=\nu+1$，分散度 $=(\nu^2+3\nu+1)/(\nu+1)^2$，$\nu\to\infty$ 时趋近 1。
- 共聚采用 Mayo-Lewis 瞬时组成方程；组成漂移由 $\mathrm d f_1/\mathrm d p=(f_1-F_1)/(1-p)$ 以固定步长 RK4 积分，初值为投料组成。
- 序列长度按 Bernoulli（末端模型）近似：单体 1 的平均连续单元数 $L_1=(r_1f_1+f_2)/f_2$，单体 2 对称。
- 所有数值为声明模型的解析或数值输出，参数为建模输入，不代表任何实测体系的速率常数或分布。
