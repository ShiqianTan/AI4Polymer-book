"""Read pinned source metadata and verify that every config reference resolves."""
import json
from pathlib import Path

from .paths import PROJECT

LOCK = PROJECT / "configs" / "sources.lock.json"
REFERENCING_CONFIGS = ("datasets.json", "descriptors.json", "monomers.json", "devices.json")


def records() -> list[dict]:
    payload = json.loads(LOCK.read_text(encoding="utf-8"), parse_constant=_reject_constant)
    rows = payload.get("sources")
    if not isinstance(rows, list) or not rows:
        raise ValueError("configs/sources.lock.json must contain a nonempty sources list")
    return rows


def _reject_constant(token: str):
    raise ValueError(f"JSON constant {token} is not permitted")


def source_record(source_id: str) -> dict:
    matches = [row for row in records() if row.get("id") == source_id]
    if len(matches) != 1:
        raise ValueError(f"Source lock has {len(matches)} records for {source_id!r}; expected exactly one")
    return matches[0]


def provenance(source_ids) -> list[dict]:
    """Reader-facing provenance for the exact source ids a topic declares."""
    rows = []
    for source_id in source_ids:
        row = source_record(source_id)
        rows.append({"id": row["id"], "title": row.get("title", ""),
                     "url": row.get("url", ""), "accessed": row.get("accessed", "")})
    return rows


def device(device_id: str) -> dict:
    rows = config("devices.json")["devices"]
    matches = [row for row in rows if row.get("id") == device_id]
    if len(matches) != 1:
        raise ValueError(f"Unknown device {device_id!r}; choose from " + ", ".join(row["id"] for row in rows))
    return matches[0]


def config(name: str) -> dict:
    path = PROJECT / "configs" / name
    payload = json.loads(path.read_text(encoding="utf-8"), parse_constant=_reject_constant)
    if not isinstance(payload, dict):
        raise ValueError(f"configs/{name} must be a JSON object")
    return payload


def config_source_ids(payload) -> set[str]:
    found = set()
    if isinstance(payload, dict):
        for key, value in payload.items():
            if key == "source_ids" and isinstance(value, list):
                found.update(str(item) for item in value)
            elif key == "source_id" and isinstance(value, str):
                found.add(value)
            else:
                found.update(config_source_ids(value))
    elif isinstance(payload, list):
        for item in payload:
            found.update(config_source_ids(item))
    return found


def verify_sources() -> dict:
    """Every config reference must resolve to one locked record with a URL and access date."""
    locked = {row.get("id"): row for row in records()}
    problems = []
    referenced = set()
    for row in records():
        if not row.get("id"):
            problems.append({"source": None, "error": "locked record lacks an id"})
            continue
        for field in ("title", "url", "accessed"):
            if not row.get(field):
                problems.append({"source": row["id"], "error": f"locked record lacks {field}"})
    for name in REFERENCING_CONFIGS:
        path = PROJECT / "configs" / name
        if not path.exists():
            problems.append({"source": name, "error": "referencing config is missing"})
            continue
        try:
            payload = json.loads(path.read_text(encoding="utf-8"), parse_constant=_reject_constant)
        except ValueError as error:
            problems.append({"source": name, "error": str(error)})
            continue
        for source_id in sorted(config_source_ids(payload)):
            referenced.add(source_id)
            if source_id not in locked:
                problems.append({"source": source_id, "error": f"referenced by configs/{name} but not locked"})
    return {"verified": len(locked), "referenced": len(referenced),
            "unresolved": problems, "scope": "config references resolve to locked metadata; URLs are not fetched offline"}
