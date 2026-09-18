# descriptor-budget — morgan-representation-budget

输入：`{"atoms": 100, "bonds": 105, "collision_key_space": "folded n_bits fingerprint", "element_bytes": 1, "library_size": 1000000, "n_bits": 2048, "radius": 2, "representation": "morgan"}`

| 来源 | 标题 | URL | 访问日期 |
| --- | --- | --- | --- |
| rdkit-morgan | RDKit documentation: Morgan fingerprints / circular fingerprints | https://www.rdkit.org/docs/GettingStartedInPython.html | 2026-09-16 |
| ecfp-rogers-hahn | Rogers & Hahn, Extended-Connectivity Fingerprints, J. Chem. Inf. Model. 2010 | https://pubs.acs.org/doi/10.1021/ci100050t | 2026-09-16 |

## 结果

| 结果 | 值 |
| --- | ---: |
| representation | `"morgan"` |
| feature_dim | 2,048 |
| bits_per_molecule | 2,048 |
| bytes_per_molecule | 256 |
| library_size | 1,000,000 |
| fingerprint_space_bits | 2,048 |
| expected_unique_fingerprints | 1,000,000 |
| expected_collisions | 0 |
| collision_probability | 0 |
| pairwise_comparison_count | 499,999,500,000 |
| xor_popcount_word_operations | 15,999,984,000,000 |

## 假设与边界

- 特征维度按声明表示规格计算：Morgan/ECFP 为 n_bits 位、Mordred 为声明描述符条数、graph 为原子与键特征拼接维度、PSMILES 为字符串长度估计；不是实测内存或运行时占用。
- ECFP4 等价于 Morgan 半径 2、2048 位；若改变半径必须改用对应 ECFP 阶数，本工具拒绝把其他半径当作 ECFP4。
- 去重、检索或聚类时所有表示都被折叠为同一 n_bits 指纹键空间，因此碰撞按生日问题在 2^n_bits 上估计；稠密描述符之间的精确浮点碰撞不在此模型内。
- 期望碰撞对数 = C(M,2)/2^n_bits，至少一次碰撞的概率 = 1-exp(-期望碰撞对数)；两者都是均匀随机指纹的期望，不是对真实高分子分布或相关性的预测。
- bytes_per_molecule 采用按位打包（位指纹向上取整到字节）或声明元素宽度；未计入索引、标签、图结构或对齐填充。
- pairwise_comparison_count 是全库两两精确比较次数；xor_popcount_word_operations 假设每个 64 位字一次异或加一次 popcount，不是实测指令数。
