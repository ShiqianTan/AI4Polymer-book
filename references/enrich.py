#!/usr/bin/env python3
"""Enrich the book's reference archive with standard citation metadata.

The script reads ``references/sources.tsv`` and, for every registered source,
resolves a DOI (or an arXiv identifier) and fetches authors, year and
container from Crossref or the arXiv API.  Results are written to
``references/metadata.json``.

Only the Python standard library is used.  The script is idempotent: a second
run reuses the values already present in ``metadata.json`` and only refreshes
them with ``--refresh``.  When the network fails the previous value is kept,
so a transient outage never erases good metadata.

Usage::

    python3 references/enrich.py            # fill missing values, reuse cache
    python3 references/enrich.py --refresh  # re-query every source
"""

from __future__ import annotations

import argparse
import csv
import difflib
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TSV_PATH = os.path.join(ROOT, "references", "sources.tsv")
OUT_PATH = os.path.join(ROOT, "references", "metadata.json")

USER_AGENT = (
    "AI4Polymer-Book-Reference-Archive/1.0 "
    "(+https://github.com/ShiqianTan/AI4Polymer-book)"
)
CROSSREF_WORKS = "https://api.crossref.org/works/"
CROSSREF_SEARCH = "https://api.crossref.org/works?query.title={query}&rows=8"
ARXIV_API = "https://export.arxiv.org/api/query?id_list={ids}&max_results=50"
DATACITE_DOI = "https://api.datacite.org/dois/10.48550/arXiv.{id}"

DOI_RE = re.compile(r"10\.\d{4,9}/[^\s\"'<>]+")
ARXIV_RE = re.compile(r"arxiv\.org/(?:abs|pdf)/(\d{4}\.\d{4,5})(?:v\d+)?", re.I)
INLINE_TAG_RE = re.compile(r"\s*<[^>]+>\s*")
YEAR_RE = re.compile(r"(?:19|20)\d{2}")
ARTICLE_WORDS = {"a", "an", "the"}
RATIO_ACCEPT = 0.90
PREFIX_INSERT_ACCEPT = 0.98
ARXIV_OVERLAP_ACCEPT = 0.4
NON_RETRYABLE = {400, 401, 403, 404, 410}

# A few source rows carry a DOI that resolves to a paper other than the one the
# registered title names.  When the archived copy and the chapter text agree on
# which paper is meant, the DOI is pinned here so the citation stays coherent.
PINNED_DOI = {
    # sources.tsv titles this row "Inhomogeneous Electron Gas" (Hohenberg-Kohn)
    # but the URL DOI and the archived snapshot are the Kohn-Sham paper, which
    # is what the repo key and chapter 5 refer to.
    "ks-dft-1965": "10.1103/PhysRev.140.A1133",
}

ATOM_NS = {"a": "http://www.w3.org/2005/Atom"}


# --------------------------------------------------------------------------- #
# HTTP helpers
# --------------------------------------------------------------------------- #
def http_bytes(url: str, tries: int = 3, accept: str = "application/json", timeout: int = 30) -> bytes:
    """GET *url* with retries and a descriptive user agent."""
    last: Exception | None = None
    for attempt in range(tries):
        request = urllib.request.Request(
            url, headers={"User-Agent": USER_AGENT, "Accept": accept}
        )
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                return response.read()
        except urllib.error.HTTPError as exc:
            last = exc
            if exc.code in NON_RETRYABLE:
                raise
        except Exception as exc:  # noqa: BLE001 - network errors are expected
            last = exc
        if attempt < tries - 1:
            time.sleep(3.0 * (attempt + 1))
    raise last if last else RuntimeError("request failed")


def http_json(url: str, tries: int = 3) -> dict:
    return json.loads(http_bytes(url, tries=tries).decode("utf-8"))


# --------------------------------------------------------------------------- #
# Text normalisation and title matching
# --------------------------------------------------------------------------- #
def strip_tags(value: str | None) -> str:
    return re.sub(r"\s+", " ", INLINE_TAG_RE.sub("", value or "")).strip()


def tokens(value: str | None) -> list[str]:
    words = re.sub(r"[^a-z0-9]+", " ", (value or "").lower()).split()
    return [w for w in words if w not in ARTICLE_WORDS]


def common_prefix(a: list[str], b: list[str]) -> int:
    n = 0
    while n < len(a) and n < len(b) and a[n] == b[n]:
        n += 1
    return n


def common_suffix(a: list[str], b: list[str]) -> int:
    n = 0
    while n < len(a) and n < len(b) and a[-1 - n] == b[-1 - n]:
        n += 1
    return n


def sequence_ratio(a: list[str], b: list[str]) -> float:
    if not a or not b:
        return 0.0
    return difflib.SequenceMatcher(None, " ".join(a), " ".join(b)).ratio()


def title_match(source: str, candidate: str) -> tuple[float, str] | None:
    """Return ``(score, kind)`` for two titles, or ``None`` when they disagree.

    The rules accept a registered title that is a prefix of the published
    title (subtitle case, ``prefix``), a title fully covered by matching ends
    (an inserted subtitle, ``coverage``), or a near-identical title
    (``ratio``).  A qualifier prepended before the registered title is rejected
    so that a different paper with a similar name is not mistaken for the
    source.
    """
    a, b = tokens(source), tokens(candidate)
    if not a or not b:
        return None
    if len(a) < 2:
        ratio = sequence_ratio(a, b)
        return (ratio, "ratio") if ratio >= RATIO_ACCEPT else None
    if b[: len(a)] == a:
        return (1.0, "prefix")
    prefix = common_prefix(a, b)
    suffix = common_suffix(a, b)
    if prefix == 0 and suffix == len(a) and len(b) > len(a):
        return None
    if prefix >= 1 and suffix >= 1 and prefix + suffix >= len(a):
        return (0.95, "coverage")
    ratio = sequence_ratio(a, b)
    if ratio >= RATIO_ACCEPT:
        return (ratio, "ratio")
    return None


def loose_overlap(source: str, candidate: str) -> float:
    """Fraction of the registered title's tokens present in *candidate*."""
    a, b = set(tokens(source)), set(tokens(candidate))
    if not a:
        return 0.0
    return len(a & b) / len(a)


def clean_doi(value: str) -> str:
    value = re.sub(r"\.pdf$", "", value.strip(), flags=re.I)
    value = value.rstrip(".,;:)]}>")
    return value.lower()


# --------------------------------------------------------------------------- #
# Crossref
# --------------------------------------------------------------------------- #
def year_from(message: dict) -> int | None:
    for key in ("issued", "published-print", "published-online", "published", "created"):
        parts = (message.get(key) or {}).get("date-parts")
        if parts and parts[0] and parts[0][0]:
            return int(parts[0][0])
    return None


def authors_from_crossref(message: dict) -> list[str] | None:
    authors: list[str] = []
    for author in message.get("author") or []:
        family, given = author.get("family"), author.get("given")
        if family:
            authors.append(f"{family}, {given}".strip().rstrip(",") if given else family)
        elif author.get("name"):
            authors.append(strip_tags(author["name"]))
    return authors or None


def container_from_crossref(message: dict) -> str | None:
    for key in ("container-title", "short-container-title"):
        values = message.get(key)
        if values and values[0]:
            return strip_tags(values[0])
    if message.get("publisher"):
        return strip_tags(message["publisher"])
    return None


def crossref_record(message: dict) -> dict:
    return {
        "doi": (message.get("DOI") or "").lower() or None,
        "title": strip_tags((message.get("title") or [""])[0]) or None,
        "authors": authors_from_crossref(message),
        "year": year_from(message),
        "container": container_from_crossref(message),
    }


def crossref_by_doi(doi: str) -> dict | None:
    """Return the Crossref record for *doi*, or ``None`` when it is unknown."""
    try:
        payload = http_json(CROSSREF_WORKS + urllib.parse.quote(doi, safe=""))
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return None
        raise
    return crossref_record(payload["message"])


def crossref_search(title: str, key_year: int | None) -> dict | None:
    """Return the best Crossref record matching *title*, or ``None``."""
    url = CROSSREF_SEARCH.format(query=urllib.parse.quote(title))
    try:
        items = http_json(url)["message"]["items"]
    except Exception:  # noqa: BLE001 - a failed search simply yields no match
        return None
    best: tuple[tuple, dict] | None = None
    for item in items:
        if not item.get("title"):
            continue
        doi = (item.get("DOI") or "").lower()
        if re.search(r"\.s\d+$", doi) or item.get("type") == "component":
            continue
        candidate = strip_tags(item["title"][0])
        matched = title_match(title, candidate)
        if matched is None:
            continue
        score, kind = matched
        year = year_from(item)
        if kind == "coverage" and key_year and year and abs(year - key_year) > 1:
            continue
        year_gap = abs(year - key_year) if (year and key_year) else 0
        rank = (score, -year_gap, 1 if container_from_crossref(item) else 0)
        if best is None or rank > best[0]:
            best = (rank, item)
    return crossref_record(best[1]) if best else None


# --------------------------------------------------------------------------- #
# arXiv
# --------------------------------------------------------------------------- #
def authors_from_arxiv(names: list[str]) -> list[str] | None:
    authors: list[str] = []
    for name in names:
        parts = name.split()
        if len(parts) >= 2:
            authors.append(f"{parts[-1]}, {' '.join(parts[:-1])}")
        elif parts:
            authors.append(parts[0])
    return authors or None


def arxiv_lookup(arxiv_ids: list[str]) -> dict[str, dict]:
    """Fetch arXiv metadata for *arxiv_ids* in a single request."""
    if not arxiv_ids:
        return {}
    url = ARXIV_API.format(ids=",".join(arxiv_ids))
    try:
        raw = http_bytes(url, tries=3, accept="application/atom+xml", timeout=12)
    except Exception:  # noqa: BLE001 - fall back to Crossref title search
        return {}
    records: dict[str, dict] = {}
    try:
        root = ET.fromstring(raw)
    except ET.ParseError:
        return {}
    for entry in root.findall("a:entry", ATOM_NS):
        entry_id = entry.findtext("a:id", default="", namespaces=ATOM_NS)
        match = re.search(r"(\d{4}\.\d{4,5})(?:v\d+)?$", entry_id)
        if not match:
            continue
        published = entry.findtext("a:published", default="", namespaces=ATOM_NS)
        records[match.group(1)] = {
            "doi": f"10.48550/arXiv.{match.group(1)}",
            "title": strip_tags(entry.findtext("a:title", default="", namespaces=ATOM_NS)),
            "authors": authors_from_arxiv(
                [a.findtext("a:name", default="", namespaces=ATOM_NS) for a in entry.findall("a:author", ATOM_NS)]
            ),
            "year": int(published[:4]) if published[:4].isdigit() else None,
            "container": "arXiv",
        }
    return records


def datacite_lookup(arxiv_ids: list[str], known: dict[str, dict]) -> dict[str, dict]:
    """Fallback for arXiv metadata through the DataCite DOI registry.

    The arXiv API occasionally returns HTTP 429; the registered arXiv DOI
    resolves through DataCite, which carries the same title, creators and year.
    """
    records = dict(known)
    for arxiv_id in arxiv_ids:
        if arxiv_id in records:
            continue
        try:
            attributes = http_json(DATACITE_DOI.format(id=arxiv_id))["data"]["attributes"]
        except Exception:  # noqa: BLE001 - a missing record stays unresolved
            continue
        creators = attributes.get("creators") or []
        authors = [c["name"] for c in creators if c.get("name")] or None
        records[arxiv_id] = {
            "doi": f"10.48550/arXiv.{arxiv_id}",
            "title": strip_tags((attributes.get("titles") or [{}])[0].get("title")),
            "authors": authors,
            "year": attributes.get("publicationYear"),
            "container": attributes.get("publisher") or "arXiv",
        }
    return records


# --------------------------------------------------------------------------- #
# Resolution
# --------------------------------------------------------------------------- #
def empty_item(row: dict) -> dict:
    return {
        "id": row["id"],
        "doi": None,
        "title": None,
        "authors": None,
        "year": None,
        "container": None,
        "matched_by": "none",
        "confidence": "none",
    }


def key_year(row_id: str) -> int | None:
    match = YEAR_RE.search(row_id)
    return int(match.group(0)) if match else None


def resolve(row: dict, arxiv_records: dict[str, dict]) -> tuple[dict, str]:
    """Resolve one source row to a metadata item.  Returns (item, log line)."""
    title = row.get("title", "")
    haystack = f"{row.get('url', '')} {row.get('source_page', '')}"

    arxiv_match = ARXIV_RE.search(haystack)
    if arxiv_match:
        record = arxiv_records.get(arxiv_match.group(1))
        if record:
            if title_match(title, record["title"]) is not None or loose_overlap(title, record["title"]) >= ARXIV_OVERLAP_ACCEPT:
                item = dict(record)
                item.update({"id": row["id"], "matched_by": "arxiv", "confidence": "doi"})
                return item, f"arxiv:{arxiv_match.group(1)}"

    doi_match = DOI_RE.search(haystack)
    if doi_match:
        doi = clean_doi(doi_match.group(0))
        record = crossref_by_doi(doi)
        if record and record["title"] and title_match(title, record["title"]) is not None:
            item = dict(record)
            item.update({"id": row["id"], "matched_by": "doi", "confidence": "doi"})
            return item, f"doi:{doi}"

    record = crossref_search(title, key_year(row["id"]))
    if record and record["title"] and title_match(title, record["title"]) is not None:
        item = dict(record)
        item.update({"id": row["id"], "matched_by": "title-search", "confidence": "title-match"})
        return item, f"title-match:{record['doi']}"

    return empty_item(row), "none"


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #
def read_sources() -> list[dict]:
    with open(TSV_PATH, encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def load_existing() -> dict:
    if not os.path.exists(OUT_PATH):
        return {}
    try:
        with open(OUT_PATH, encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, json.JSONDecodeError):
        return {}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--refresh", action="store_true", help="re-query every source")
    args = parser.parse_args(argv)

    rows = read_sources()
    existing = load_existing()
    cache = {item["id"]: item for item in existing.get("items", [])}

    def cached_ok(row: dict) -> bool:
        if args.refresh:
            return False
        item = cache.get(row["id"])
        return bool(item and "confidence" in item)

    pending = [row for row in rows if not cached_ok(row)]
    arxiv_ids = []
    for row in pending:
        match = ARXIV_RE.search(f"{row.get('url', '')} {row.get('source_page', '')}")
        if match:
            arxiv_ids.append(match.group(1))
    arxiv_records = arxiv_lookup(arxiv_ids)
    if len(arxiv_records) < len(arxiv_ids):
        arxiv_records = datacite_lookup(arxiv_ids, arxiv_records)
    print(f"arXiv records: {len(arxiv_records)}/{len(arxiv_ids)}", file=sys.stderr)

    items: list[dict] = []
    failures: list[str] = []
    for row in rows:
        if cached_ok(row):
            items.append(cache[row["id"]])
            continue
        try:
            item, note = resolve(row, arxiv_records)
        except Exception as exc:  # noqa: BLE001 - keep the previous value
            failures.append(f"{row['id']}: {exc}")
            item = cache.get(row["id"]) or empty_item(row)
            items.append(item)
            print(f"  {row['id']}: ERROR {exc}", file=sys.stderr)
            continue
        if row["id"] in PINNED_DOI:
            pinned = crossref_by_doi(PINNED_DOI[row["id"]])
            if pinned:
                item = dict(pinned)
                item.update({"id": row["id"], "matched_by": "doi", "confidence": "doi"})
                note = f"pinned:{PINNED_DOI[row['id']]}"
        if note == "none":
            failures.append(f"{row['id']}: no confident match")
        print(f"  {row['id']}: {note}", file=sys.stderr)
        items.append(item)

    items.sort(key=lambda item: item["id"])

    if existing.get("items") == items and existing.get("generated_at"):
        generated_at = existing["generated_at"]
    else:
        generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()

    payload = {
        "generated_at": generated_at,
        "source": "crossref",
        "providers": ["crossref", "arxiv"],
        "items": items,
    }
    with open(OUT_PATH, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
        handle.write("\n")

    counts: dict[str, int] = {}
    for item in items:
        counts[item["confidence"]] = counts.get(item["confidence"], 0) + 1
    print(f"wrote {OUT_PATH} ({len(items)} items)")
    print("confidence: " + ", ".join(f"{k}={v}" for k, v in sorted(counts.items())))
    if failures:
        print("unresolved:", file=sys.stderr)
        for line in failures:
            print(f"  {line}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
