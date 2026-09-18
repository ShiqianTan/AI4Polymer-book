"""Regenerate the fixed book scenarios and verify that results are current."""
import hashlib
import json
from pathlib import Path

from .paths import PROJECT
from .report import markdown
from .schema import to_json, validate_result
from .sources import verify_sources
from .topics import TOPIC_MODULES


def is_source_input(path: Path) -> bool:
    return "__pycache__" not in path.parts and path.suffix not in {".pyc", ".pyo"}


def _relative(paths) -> list[str]:
    return sorted(str(path.relative_to(PROJECT)) for path in paths if path.is_file() and is_source_input(path))


def input_paths() -> list[Path]:
    paths = [PROJECT / "calc.py", PROJECT / "pyproject.toml", PROJECT / "scenarios" / "book.json"]
    paths.extend((PROJECT / "configs").glob("*.json"))
    paths.extend((PROJECT / "src" / "ai4polymer_calc").rglob("*.py"))
    return [path for path in paths if path.is_file()]


def input_hashes() -> list[dict]:
    return [{"file": str(path.relative_to(PROJECT)),
             "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
            for path in sorted(input_paths())]


def scenarios() -> list[dict]:
    payload = json.loads((PROJECT / "scenarios" / "book.json").read_text(encoding="utf-8"),
                         parse_constant=_reject_constant)
    rows = payload.get("scenarios")
    if not isinstance(rows, list) or not rows:
        raise ValueError("scenarios/book.json must contain a nonempty scenarios list")
    return rows


def _reject_constant(token: str):
    raise ValueError(f"JSON constant {token} is not permitted")


def _save(output: Path, slug: str, payload: dict, artifacts: list) -> None:
    for extension, text in (("json", to_json(payload)), ("md", markdown(payload))):
        path = output / f"{slug}.{extension}"
        path.write_text(text, encoding="utf-8")
        artifacts.append({"file": str(path.relative_to(PROJECT)),
                          "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})


def _index(entries: list[dict]) -> str:
    lines = ["# 结果索引", "",
             "由 `python3 calculations/calc.py reproduce` 生成；每个场景同时输出 `.json` 与 `.md`。", "",
             "| 场景 | 专题 | 模型 | 结果 |", "| --- | --- | --- | --- |"]
    for entry in entries:
        lines.append(f"| `{entry['slug']}` | {entry['topic']} | {entry['model']} | "
                     f"[json]({entry['slug']}.json) · [md]({entry['slug']}.md) |")
    lines.append("")
    return "\n".join(lines)


def run() -> dict:
    verify_sources()
    output = PROJECT / "results"
    output.mkdir(exist_ok=True)
    artifacts = []
    entries = []
    for row in scenarios():
        topic = row["topic"]
        if topic not in TOPIC_MODULES:
            raise ValueError(f"scenario {row['id']!r} names unknown topic {topic!r}")
        payload = TOPIC_MODULES[topic].calculate(**row.get("inputs", {}))
        validate_result(payload)
        _save(output, row["id"], payload, artifacts)
        entries.append({"slug": row["id"], "topic": topic, "model": payload["model"]})
    readme = output / "README.md"
    readme.write_text(_index(entries), encoding="utf-8")
    artifacts.append({"file": str(readme.relative_to(PROJECT)),
                      "sha256": hashlib.sha256(readme.read_bytes()).hexdigest()})
    manifest = {"inputs": input_hashes(), "artifacts": artifacts,
                "scope": "fixed book scenarios regenerated from declared configs; formula tests do not substitute for experimental evidence"}
    (output / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {"generated": [entry["slug"] for entry in entries], "artifacts": len(artifacts),
            "results_index": str(readme.relative_to(PROJECT)), "scope": manifest["scope"]}


def verify_results() -> dict:
    verify_sources()
    manifest_path = PROJECT / "results" / "manifest.json"
    if not manifest_path.exists():
        raise ValueError("results/manifest.json is missing; run reproduce")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("inputs") != input_hashes():
        raise ValueError("Calculator, configs or scenarios changed; run reproduce")
    artifacts = manifest.get("artifacts")
    if not isinstance(artifacts, list) or not artifacts:
        raise ValueError("Result manifest must contain a nonempty artifact list")
    for artifact in artifacts:
        path = PROJECT / artifact["file"]
        if not path.exists():
            raise ValueError(f"Missing result artifact: {artifact['file']}")
        if hashlib.sha256(path.read_bytes()).hexdigest() != artifact["sha256"]:
            raise ValueError(f"Generated result changed: {artifact['file']}; run reproduce")
    return {"verified_artifacts": len(artifacts), "results_index": "results/README.md",
            "scope": manifest["scope"]}
