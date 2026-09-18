"""Parse Clarivate Web of Science tagged exports (.ciw) for the AI4Polymer survey.

The script reads every .ciw file in a directory, reconstructs records from the
Clarivate tagged plain-text format (records delimited by ``PT`` ... ``ER``,
two-character field codes, three-space continuation lines), and emits either a
machine-readable JSON summary or a Markdown rendering of the key tables. It
depends only on the Python 3.10+ standard library.

Usage
-----
    python3 parse_wos.py --wos DIR --output wos-summary.json
    python3 parse_wos.py --wos DIR --output wos-summary.md --format md

Options
-------
    --wos       directory containing the .ciw files (default: references/wos)
    --output    destination file (default: wos-summary.json)
    --format    json (default) or md
    --top       number of rows kept for the long-tail tables (default: full)
"""

from __future__ import annotations

import argparse
import collections
import glob
import json
import os
import re
import sys

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

ACCESS_DATE = "2026-04-21"
SOURCE_DIR_DEFAULT = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "references",
    "wos",
)
OUTPUT_DEFAULT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "wos-summary.json")

QUERY = (
    '(TI=(polymer* OR macromolecul* OR "polymeric material*" OR "high polymer" '
    'OR copolymer* OR biopolymer* OR elastomer*) AND PY=(2010-2027)) AND '
    '(AB=("machine learning" OR "deep learning" OR "neural network*" OR '
    '"reinforcement learning" OR "large language model" OR "AI Agent") AND PY=(2010-2027))'
)

FIELD_RE = re.compile(r"^([A-Z0-9]{2}) (.*)$")
CONT_RE = re.compile(r"^   (.*)$")
BRACKET_RE = re.compile(r"^\[[^\]]*\]\s*")
ADDRESS_SPLIT_RE = re.compile(r";\s*(?=\[)")
WS_RE = re.compile(r"\s+")

COUNTRY_ALIASES = {
    "Peoples R China": "China",
    "U Arab Emirates": "United Arab Emirates",
    "Turkiye": "Turkey",
    "England": "United Kingdom",
    "Scotland": "United Kingdom",
    "Wales": "United Kingdom",
    "North Ireland": "United Kingdom",
    "BELARUS": "Belarus",
    "Bosnia & Herceg": "Bosnia and Herzegovina",
}

THEMES = [
    ("machine learning", r"machine learn"),
    ("deep learning", r"deep learn"),
    ("neural network", r"neural net"),
    ("GNN/graph", r"graph neural|graph convolution|graph network|graph attention|"
                  r"message passing|molecular graph|\bgnn\b|graph representation"),
    ("transformer/LLM/foundation model", r"transformer|large language model|\bllm\b|"
                                         r"foundation model|language model|\bgpt\b|\bbert\b"),
    ("agent/agentic", r"\bagent\b|\bagents\b|\bagentic\b|multi-agent|autonomous agent"),
    ("generative/VAE/GAN/diffusion", r"generative|variational autoencoder|\bvae\b|"
                                     r"generative adversarial|\bgan\b|diffusion model|"
                                     r"denoising diffusion|autoregressive"),
    ("reinforcement learning/active learning/bayesian optimization",
     r"reinforcement learn|active learn|bayesian optimi"),
    ("inverse design/de novo", r"inverse design|de novo"),
    ("molecular dynamics/DFT/coarse-grained", r"molecular dynamics|density functional|"
                                              r"\bdft\b|coarse-grain|coarse grain|ab initio"),
    ("high-throughput screening", r"high-throughput|high throughput"),
    ("polymer informatics/materials informatics", r"polymer informatics|materials informatics|"
                                                  r"material informatics|cheminformatics|"
                                                  r"chemometrics|informatics"),
    ("physics-informed", r"physics-informed|physics informed|physics-based|"
                         r"physics-constrained|physically informed"),
    ("3D printing/additive manufacturing", r"3d print|three-dimensional print|"
                                           r"additive manufactur|fused deposition|"
                                           r"stereolithograph|inkjet print|direct ink writing|"
                                           r"extrusion print"),
    ("sustainability/recycling/biodegradation", r"sustainab|recycl|biodegrad|circular economy|"
                                                r"bio-based|biobased|life cycle assessment|"
                                                r"eco-friendly|environmentally friendly"),
    ("dielectric/energy storage/battery/electrolyte", r"dielectric|energy storage|batter|"
                                                      r"electrolyte|supercapacitor|capacitor"),
    ("membrane/separation", r"membrane|separation|permeation|pervaporation|filtration|"
                            r"desalination|gas separation|nanofiltration"),
    ("solubility/Flory-Huggins/glass transition", r"solubilit|flory|huggins|glass transition|"
                                                  r"miscibilit|chi parameter|interaction parameter"),
    ("representation/SMILES/descriptor/fingerprint", r"representation|smiles|descriptor|"
                                                     r"fingerprint|embedding|feature vector"),
    ("uncertainty/interpretability/SHAP", r"uncertaint|interpretab|explainab|\bshap\b|"
                                          r"black-box|trustworth"),
    ("transfer learning/few-shot/pretraining", r"transfer learn|few-shot|few shot|pretrain|"
                                               r"pre-train|fine-tun|fine tun|self-supervised"),
    ("self-driving lab/robotics/automation", r"self-driving lab|self driving lab|"
                                             r"autonomous lab|robotic|automat|closed-loop"),
    ("mechanical properties", r"mechanical propert|tensile|elastic modulus|young's modulus|"
                              r"stress-strain|fracture|toughness|elongation|flexural"),
    ("thermal conductivity", r"thermal conductiv|heat transfer|thermal transport|"
                             r"thermally conductive|thermal management"),
]

THEME_PATTERNS = [(label, re.compile(pattern, re.I)) for label, pattern in THEMES]

# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------


def find_sources(wos_dir):
    """Return the sorted list of .ciw files under ``wos_dir``."""
    return sorted(glob.glob(os.path.join(wos_dir, "*.ciw")))


def iter_records(paths):
    """Yield one dict per WoS record, joining continuation lines."""
    for path in paths:
        current = None
        last = None
        with open(path, encoding="utf-8", errors="replace") as handle:
            for raw in handle:
                line = raw.rstrip("\r\n")
                if line == "ER":
                    if current is not None:
                        yield current
                    current = None
                    last = None
                    continue
                if line.startswith("   "):
                    if current is not None and last is not None:
                        current[last] = f"{current[last]} {line.strip()}"
                    continue
                match = FIELD_RE.match(line)
                if not match:
                    continue
                code, value = match.groups()
                if code == "PT":
                    current = {"PT": value}
                    last = "PT"
                elif current is not None:
                    current[code] = value
                    last = code


def normalize(text):
    """Lower-case and collapse whitespace for stable aggregation."""
    return WS_RE.sub(" ", text.strip().lower())


def split_list(value):
    """Split a WoS semicolon-delimited field into trimmed items."""
    return [item.strip() for item in value.split(";") if item.strip()]


# ---------------------------------------------------------------------------
# Aggregation helpers
# ---------------------------------------------------------------------------


def count_field(records, code, dedupe=True):
    """Count values of a semicolon-delimited field, optionally once per record."""
    counter = collections.Counter()
    for record in records:
        value = record.get(code)
        if not value:
            continue
        items = split_list(value)
        if dedupe:
            items = dict.fromkeys(items)
        for item in items:
            counter[item] += 1
    return counter


def count_keywords(records, code):
    """Count keywords with case-normalized keys and a representative spelling."""
    counter = collections.Counter()
    variants = collections.defaultdict(collections.Counter)
    for record in records:
        value = record.get(code)
        if not value:
            continue
        for raw in split_list(value):
            key = normalize(raw)
            if not key:
                continue
            counter[key] += 1
            variants[key][raw.strip()] += 1
    display = {key: forms.most_common(1)[0][0] for key, forms in variants.items()}
    return counter, display, variants


def record_countries(record):
    """Extract normalized countries from the tail of every C1 address."""
    value = record.get("C1")
    if not value:
        return []
    countries = []
    for group in ADDRESS_SPLIT_RE.split(value):
        address = BRACKET_RE.sub("", group).strip().rstrip(".")
        if not address:
            continue
        tail = address.rsplit(",", 1)[-1].strip().rstrip(".")
        if tail.upper().endswith("USA"):
            country = "USA"
        else:
            country = COUNTRY_ALIASES.get(tail, tail)
        if country:
            countries.append(country)
    return list(dict.fromkeys(countries))


def top_items(counter, limit, label="name"):
    """Render a counter as a ranked list of dicts."""
    ranked = sorted(counter.items(), key=lambda pair: (-pair[1], pair[0]))
    return [{label: key, "count": count} for key, count in ranked[:limit]]


def build_summary(records, sources):
    """Compute every aggregate that the report cites."""
    total = len(records)

    years = collections.Counter()
    document_types = collections.Counter()
    journals = collections.Counter()
    wos_categories = collections.Counter()
    research_areas = collections.Counter()
    institutions = collections.Counter()
    countries = collections.Counter()
    themes = {
        label: {"regex": pattern.pattern, "total": 0,
                "by_year": collections.Counter()}
        for label, pattern in THEME_PATTERNS
    }

    for record in records:
        year = record.get("PY", "").strip()
        if year:
            years[year] += 1
        if record.get("DT"):
            document_types[record["DT"].strip()] += 1
        if record.get("SO"):
            journals[record["SO"].strip()] += 1
        for category in dict.fromkeys(split_list(record.get("WC", ""))):
            wos_categories[category] += 1
        for area in dict.fromkeys(split_list(record.get("SC", ""))):
            research_areas[area] += 1
        for institution in dict.fromkeys(split_list(record.get("C3", ""))):
            institutions[institution] += 1
        for country in record_countries(record):
            countries[country] += 1

        text = " ".join(
            record.get(code, "") for code in ("TI", "AB", "DE", "ID")
        )
        if text.strip():
            for label, pattern in THEME_PATTERNS:
                if pattern.search(text):
                    themes[label]["total"] += 1
                    if year:
                        themes[label]["by_year"][year] += 1

    author_keywords, author_display, author_variants = count_keywords(records, "DE")
    keywords_plus, plus_display, plus_variants = count_keywords(records, "ID")

    theme_output = {}
    for label, data in themes.items():
        by_year = {year: data["by_year"].get(year, 0) for year in sorted(years)}
        share = {
            year: round(data["by_year"].get(year, 0) / years[year] * 100, 2)
            for year in sorted(years)
            if years[year]
        }
        theme_output[label] = {
            "regex": data["regex"],
            "total": data["total"],
            "by_year": by_year,
            "share_pct": share,
        }

    top_keywords = [key for key, _ in author_keywords.most_common(30)]
    keyword_index = set(top_keywords)
    pair_counter = collections.Counter()
    for record in records:
        value = record.get("DE")
        if not value:
            continue
        present = sorted({
            normalize(raw) for raw in split_list(value)
            if normalize(raw) in keyword_index
        })
        for i, first in enumerate(present):
            for second in present[i + 1:]:
                pair_counter[(first, second)] += 1
    pairs = [
        {"keyword_1": first, "keyword_2": second, "count": count}
        for (first, second), count in sorted(
            pair_counter.items(), key=lambda pair: (-pair[1], pair[0])
        )
    ]

    cited = sorted(
        records,
        key=lambda record: (
            -int(record.get("TC", "0").strip() or 0),
            record.get("TI", ""),
        ),
    )[:50]
    most_cited = [
        {
            "rank": index,
            "times_cited": int(record.get("TC", "0").strip() or 0),
            "year": record.get("PY", "").strip(),
            "title": record.get("TI", "").strip(),
            "journal": record.get("SO", "").strip(),
            "doi": record.get("DI", "").strip(),
        }
        for index, record in enumerate(cited, start=1)
    ]

    missing = {
        code: sum(1 for record in records if not record.get(code))
        for code in ("DE", "ID", "AB", "C1", "WC", "SC", "DI", "TC", "PY")
    }
    variants_total = sum(
        1 for forms in author_variants.values() if len(forms) > 1
    )
    variant_examples = sorted(
        (
            {"keyword": key, "forms": [form for form, _ in forms.most_common()],
             "count": author_keywords[key]}
            for key, forms in author_variants.items() if len(forms) > 1
        ),
        key=lambda item: (-item["count"], item["keyword"]),
    )[:20]
    dates = collections.Counter(
        record.get("DA", "").strip() for record in records if record.get("DA")
    )

    year_sum = sum(years.values())
    return {
        "meta": {
            "generated_by": "research/2026-wos-survey/parse_wos.py",
            "query": QUERY,
            "access_date": ACCESS_DATE,
            "source_dir": os.path.abspath(os.path.dirname(sources[0])) if sources else "",
            "source_files": [os.path.basename(path) for path in sources],
            "total_records": total,
            "year_sum": year_sum,
            "year_sum_ok": year_sum == total,
            "year_min": min(years) if years else "",
            "year_max": max(years) if years else "",
            "records_with_de": total - missing["DE"],
            "records_with_id": total - missing["ID"],
        },
        "years": {year: years[year] for year in sorted(years)},
        "document_types": top_items(document_types, 20, "type"),
        "journals_top50": top_items(journals, 50, "journal"),
        "wos_categories": top_items(wos_categories, 60, "category"),
        "research_areas": top_items(research_areas, 30, "area"),
        "author_keywords_top150": [
            {"keyword": key, "display": author_display[key], "count": count}
            for key, count in author_keywords.most_common(150)
        ],
        "keywords_plus_top150": [
            {"keyword": key, "display": plus_display[key], "count": count}
            for key, count in keywords_plus.most_common(150)
        ],
        "institutions_top40": top_items(institutions, 40, "institution"),
        "countries_top40": top_items(countries, 40, "country"),
        "most_cited_top50": most_cited,
        "themes": theme_output,
        "keyword_cooccurrence": {
            "top_keywords": top_keywords,
            "pairs": pairs,
        },
        "data_quality": {
            "missing_fields": missing,
            "keyword_case_variants": variants_total,
            "keyword_case_variant_examples": variant_examples,
            "date_added_values": [
                {"date": date, "count": count}
                for date, count in dates.most_common()
            ],
            "notes": [
                "DE and ID keyword counts are case-normalized; the displayed "
                "spelling is the most frequent original form.",
                "Countries are parsed from the last comma-separated segment of "
                "each C1 address; England/Scotland/Wales/North Ireland are "
                "merged into United Kingdom.",
                "C3 institution counts are de-duplicated within a record.",
            ],
        },
    }


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------


def md_table(headers, rows):
    lines = [
        "| " + " | ".join(str(header) for header in headers) + " |",
        "|" + "|".join("---" for _ in headers) + "|",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(cell) for cell in row) + " |")
    return "\n".join(lines)


def render_markdown(summary):
    """Render the summary as a Markdown document of key tables."""
    meta = summary["meta"]
    years = summary["years"]
    parts = [
        "# AI4Polymer Web of Science 汇总（机器生成）",
        "",
        f"- 记录总数：**{meta['total_records']}**（逐年合计 {meta['year_sum']}，"
        f"一致：{'是' if meta['year_sum_ok'] else '否'}）",
        f"- 检索日期：{meta['access_date']}；年份范围：{meta['year_min']}–{meta['year_max']}",
        f"- 数据文件：{', '.join(meta['source_files'])}",
        "",
        "由 `research/2026-wos-survey/parse_wos.py --format md` 生成，"
        "原始数值见 [wos-summary.json](wos-summary.json)。",
        "",
        "## 逐年发文量",
        "",
        md_table(["年份", "记录数"], [[year, years[year]] for year in sorted(years)]),
        "",
        "## 文献类型",
        "",
        md_table(
            ["类型", "记录数"],
            [[item["type"], item["count"]] for item in summary["document_types"]],
        ),
        "",
        "## 期刊（前 50）",
        "",
        md_table(
            ["期刊", "记录数"],
            [[item["journal"], item["count"]] for item in summary["journals_top50"]],
        ),
        "",
        "## WoS 学科分类（前 60）",
        "",
        md_table(
            ["分类", "记录数"],
            [[item["category"], item["count"]] for item in summary["wos_categories"]],
        ),
        "",
        "## 研究领域（前 30）",
        "",
        md_table(
            ["领域", "记录数"],
            [[item["area"], item["count"]] for item in summary["research_areas"]],
        ),
        "",
        "## 作者关键词（前 150）",
        "",
        md_table(
            ["关键词（规范）", "原始拼写", "记录数"],
            [[item["keyword"], item["display"], item["count"]]
             for item in summary["author_keywords_top150"]],
        ),
        "",
        "## Keywords-Plus（前 150）",
        "",
        md_table(
            ["关键词（规范）", "原始拼写", "记录数"],
            [[item["keyword"], item["display"], item["count"]]
             for item in summary["keywords_plus_top150"]],
        ),
        "",
        "## 机构（前 40）",
        "",
        md_table(
            ["机构", "记录数"],
            [[item["institution"], item["count"]] for item in summary["institutions_top40"]],
        ),
        "",
        "## 国家/地区（前 40）",
        "",
        md_table(
            ["国家/地区", "记录数"],
            [[item["country"], item["count"]] for item in summary["countries_top40"]],
        ),
        "",
        "## 高被引论文（前 50）",
        "",
        md_table(
            ["排名", "被引", "年份", "标题", "期刊", "DOI"],
            [[item["rank"], item["times_cited"], item["year"], item["title"],
              item["journal"], item["doi"]] for item in summary["most_cited_top50"]],
        ),
        "",
        "## 主题逐年计数",
        "",
    ]
    year_keys = sorted(years)
    header = ["主题", "合计"] + year_keys
    rows = []
    for label, data in summary["themes"].items():
        rows.append([label, data["total"]] + [data["by_year"].get(year, 0) for year in year_keys])
    parts.append(md_table(header, rows))
    parts += [
        "",
        "## 主题逐年占比（%）",
        "",
    ]
    rows = []
    for label, data in summary["themes"].items():
        rows.append([label] + [data["share_pct"].get(year, 0) for year in year_keys])
    parts.append(md_table(["主题"] + year_keys, rows))
    parts += [
        "",
        "## 作者关键词共现（前 30 关键词的词对）",
        "",
        md_table(
            ["关键词 1", "关键词 2", "共现记录数"],
            [[pair["keyword_1"], pair["keyword_2"], pair["count"]]
             for pair in summary["keyword_cooccurrence"]["pairs"] if pair["count"] >= 2],
        ),
        "",
        "## 数据质量",
        "",
        f"- 缺失 DE 的记录：{summary['data_quality']['missing_fields']['DE']}",
        f"- 缺失 ID 的记录：{summary['data_quality']['missing_fields']['ID']}",
        f"- 存在大小写变体的关键词数：{summary['data_quality']['keyword_case_variants']}",
        "",
    ]
    return "\n".join(parts) + "\n"


def print_tables(summary):
    """Print a compact set of key tables to stdout."""
    meta = summary["meta"]
    print(f"total_records={meta['total_records']} year_sum={meta['year_sum']} "
          f"year_sum_ok={meta['year_sum_ok']}")
    print("\nYears:")
    for year, count in summary["years"].items():
        print(f"  {year}: {count}")
    print("\nTop 10 journals:")
    for item in summary["journals_top50"][:10]:
        print(f"  {item['count']:5d}  {item['journal']}")
    print("\nTop 15 author keywords:")
    for item in summary["author_keywords_top150"][:15]:
        print(f"  {item['count']:5d}  {item['keyword']}")
    print("\nTop 10 countries:")
    for item in summary["countries_top40"][:10]:
        print(f"  {item['count']:5d}  {item['country']}")
    print("\nTop 10 themes (total records matching):")
    ranked = sorted(summary["themes"].items(), key=lambda pair: -pair[1]["total"])
    for label, data in ranked[:10]:
        print(f"  {data['total']:5d}  {label}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def parse_args(argv):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--wos", default=SOURCE_DIR_DEFAULT,
                        help="directory containing .ciw files")
    parser.add_argument("--output", default=OUTPUT_DEFAULT,
                        help="destination JSON or Markdown file")
    parser.add_argument("--format", choices=("json", "md"), default="json",
                        help="output format")
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv if argv is not None else sys.argv[1:])
    sources = find_sources(args.wos)
    if not sources:
        raise SystemExit(f"no .ciw files found under {args.wos}")
    records = list(iter_records(sources))
    summary = build_summary(records, sources)

    output_dir = os.path.dirname(os.path.abspath(args.output))
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    if args.format == "md":
        with open(args.output, "w", encoding="utf-8") as handle:
            handle.write(render_markdown(summary))
    else:
        with open(args.output, "w", encoding="utf-8") as handle:
            json.dump(summary, handle, ensure_ascii=False, indent=2)
            handle.write("\n")

    print_tables(summary)
    print(f"\nwrote {args.output} ({args.format})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
