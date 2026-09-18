# chemical-space — combinatorial-block-space

输入：`{"chain_length": 100, "copolymer": "block", "max_distinct_monomers": 2, "monomers": 10, "primary_dataset": "PI1M", "stoichiometry": "1,1"}`

| 来源 | 标题 | URL | 访问日期 |
| --- | --- | --- | --- |
| omg | Open Macromolecular Genome (search entry; canonical URL pending verification) | https://scholar.google.com/scholar?q=Open+Macromolecular+Genome | 2026-09-16 |
| pi1m | Ma et al., PI1M: A Benchmark Database for Polymer Informatics, J. Chem. Inf. Model. 2020 | https://pubs.acs.org/doi/10.1021/acs.jcim.0c00126 | 2026-09-16 |
| point2 | Kuenneth & Ramprasad, POINT2 polymer informatics benchmark, Digital Discovery 2023 | https://pubs.rsc.org/en/content/articlelanding/2023/dd/d2dd00115b | 2026-09-16 |
| polybert | Kuenneth & Ramprasad, polyBERT: a chemical language model to enable fully machine-driven ultrafast polymer informatics, Sci. Data 2023 | https://www.nature.com/articles/s41597-023-02305-0 | 2026-09-16 |
| polyinfo | NIMS PoLyInfo polymer database | https://polymer.nims.go.jp/en/ | 2026-09-16 |
| polyuniverse | PolyUniverse polymer dataset (search entry; canonical URL and scale pending verification) | https://scholar.google.com/scholar?q=PolyUniverse+polymer+dataset | 2026-09-16 |

## 结果

| 结果 | 值 |
| --- | ---: |
| sequence_count | 8,910 |
| log10_sequence_count | 3.94988 |
| synthesizable_count | 8,910 |
| synthesizable_fraction | 1 |
| composition_constrained_sequence_count | `null` |
| known_library | `"PI1M"` |
| known_library_size | 1,000,000 |
| coverage_of_known_library | 112.233 |
| log10_sequence_count_per_known_entry | -2.05012 |
| known_libraries_compared | 6 |

已知数据集对比

| dataset | size | coverage | log10_sequence_count_per_entry | verification |
| --- | --- | --- | --- | --- |
| `"PI1M"` | 1,000,000 | 112.233 | -2.05012 | `"reported"` |
| `"PoLyInfo"` | 12,000 | 1.3468 | -0.129304 | `"reported"` |
| `"POINT2"` | 238,219 | 26.7361 | -1.4271 | `"reported"` |
| `"polyBERT pretraining"` | 100,000,000 | 11223.3 | -4.05012 | `"reported"` |
| `"Open Macromolecular Genome"` | `null` | `null` | `null` | `"unverified"` |
| `"PolyUniverse"` | `null` | `null` | `null` | `"unverified"` |

## 假设与边界

- 序列计数使用精确大整数：均聚物 = N；无规共聚物 = N^L；交替共聚物 = N(N-1)（严格二元交替，L>=2）；嵌段共聚物 = N(N-1)(L-1)（两嵌段，有序单体对与嵌段长度）。
- 无规共聚物的组成约束计数为多项式系数 L!/(n_1!...n_k!)，其中 n_i 由声明配比按最大余数法取整到链长 L；配比本身是建模输入，不是实验测定。
- 规则式可合成库把链上不同单体种类限制为至多 max_distinct 种：无规序列的可达数 = sum_j C(N,j)·j!·S(L,j)（S 为第二类斯特林数）；均聚/交替/嵌段构型天然满足该规则，故可达比例记为 1。
- synthesizable_fraction = 可达序列数 / 全部序列数；它衡量规则库覆盖的理论比例，不代表实际合成收率或热力学可行性。
- coverage_of_known_library = 已知库条目数 / 理论序列数；对 size 为 null 的数据集返回 null。数据集规模为公开报告元数据，引用前需人工复核。
- log10_sequence_count 使用任意精度整数的位长计算，避免 double 溢出；序列数本身在 JSON 中以完整整数保存。
