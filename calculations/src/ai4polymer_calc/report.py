"""Human-readable Markdown derived from the same result contract as the JSON."""
import json


def _format(value) -> str:
    if isinstance(value, bool):
        return f"`{json.dumps(value)}`"
    if isinstance(value, int):
        return f"{value:,}"
    if isinstance(value, float):
        if value == int(value) and abs(value) < 1e15:
            return f"{int(value):,}"
        return f"{value:.6g}"
    if value is None:
        return "`null`"
    return f"`{json.dumps(value, ensure_ascii=False)}`"


def summary_table(result: dict) -> str:
    lines = ["| 结果 | 值 |", "| --- | ---: |"]
    for key, value in result["summary"].items():
        if isinstance(value, (list, dict)):
            continue
        lines.append(f"| {key} | {_format(value)} |")
    return "\n".join(lines)


def _record_table(title: str, rows: list) -> list[str]:
    if not rows:
        return []
    columns = list(rows[0])
    lines = ["", title, "", "| " + " | ".join(columns) + " |",
             "| " + " | ".join("---" for _ in columns) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(_format(row.get(column)) for column in columns) + " |")
    return lines


def markdown(result: dict) -> str:
    scenario = result["scenario"]
    lines = [f"# {result['calculation']} — {result['model']}", "",
             "输入：`" + json.dumps(scenario, ensure_ascii=False, sort_keys=True) + "`", "",
             "| 来源 | 标题 | URL | 访问日期 |", "| --- | --- | --- | --- |"]
    for row in result["sources"]:
        lines.append(f"| {row.get('id', '')} | {row.get('title', '')} | {row.get('url', '')} | {row.get('accessed', '')} |")
    lines.extend(["", "## 结果", "", summary_table(result)])
    summary = result["summary"]
    for key, title in (("terms", "逐项推导"), ("dataset_comparison", "已知数据集对比"),
                       ("breakdown", "分项"), ("curve", "学习曲线采样")):
        lines.extend(_record_table(title, summary.get(key, [])))
    lines.extend(["", "## 假设与边界", ""])
    lines.extend("- " + statement for statement in result["assumptions"])
    lines.append("")
    return "\n".join(lines)
