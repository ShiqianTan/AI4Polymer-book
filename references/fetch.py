#!/usr/bin/env python3
"""Download the explicitly listed primary sources and build an offline index.

Run from a checkout: python3 references/fetch.py
PDF text is extracted with PyMuPDF when available, falling back to Poppler.
"""
import argparse
import concurrent.futures
import csv
import hashlib
import html
import json
import re
import subprocess
import urllib.request
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import quote, urlsplit

ROOT = Path(__file__).resolve().parent
CHAPTERS = [c["title"] for c in
            json.loads((ROOT.parent / "archive/outlines/chapters.json").read_text())]
USER_AGENT = "AI4Polymer-Book-Reference-Archive/1.0"
ARXIV_ABS = re.compile(r"^https?://arxiv\.org/abs/(.+?)(?:v\d+)?$")
SUBSCRIPTION = ("pubs.acs.org", "www.nature.com", "www.science.org", "link.aps.org",
                "pubs.aip.org", "www.sciencedirect.com", "onlinelibrary.wiley.com", "doi.org")
MIN_TEXT = 600


class ReadableText(HTMLParser):
    def __init__(self):
        super().__init__()
        self.skip = 0
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "noscript"):
            self.skip += 1
        if tag in ("p", "div", "li", "tr", "br", "h1", "h2", "h3", "h4"):
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag in ("script", "style", "noscript") and self.skip:
            self.skip -= 1
        if tag in ("p", "div", "li", "tr", "h1", "h2", "h3", "h4"):
            self.parts.append("\n")

    def handle_data(self, data):
        if not self.skip:
            self.parts.append(data)

    def result(self):
        return "\n".join(line for line in
                         (re.sub(r"\s+", " ", x).strip() for x in "".join(self.parts).splitlines())
                         if line)


def pdf_text(path):
    """Return (text, pages). Prefer PyMuPDF; fall back to Poppler."""
    try:
        import fitz
    except ImportError:
        fitz = None
    if fitz is not None:
        with fitz.open(path) as document:
            return "\n".join(page.get_text() for page in document), document.page_count
    text = subprocess.run(["pdftotext", "-layout", str(path), "-"],
                          check=True, capture_output=True, text=True).stdout
    info = subprocess.run(["pdfinfo", str(path)], check=True, capture_output=True, text=True).stdout
    pages = re.search(r"^Pages:\s+(\d+)", info, re.M)
    return text, (int(pages.group(1)) if pages else None)


def normalize(url):
    """Prefer the PDF over the abstract page for arXiv entries."""
    match = ARXIV_ABS.match(url)
    return f"https://arxiv.org/pdf/{match.group(1)}" if match else url


def fetch(row):
    item = dict(row)
    item["chapters"] = [int(c) for c in row["chapters"].split(",")]
    item["retrieved_at"] = datetime.now(timezone.utc).isoformat()
    for attempt in range(2):
        try:
            supplied = row["url"].startswith("local:")
            if supplied:
                source = (ROOT / row["url"][6:]).resolve()
                source.relative_to(ROOT)
                data = source.read_bytes()
                item["acquisition"] = "user_provided"
                item["content_type"] = "application/pdf" if data.startswith(b"%PDF-") else "text/plain"
            else:
                request = urllib.request.Request(normalize(row["url"]),
                                                 headers={"User-Agent": USER_AGENT})
                with urllib.request.urlopen(request, timeout=45) as response:
                    data = response.read()
                    item["resolved_url"] = response.url
                    item["content_type"] = response.headers.get("Content-Type", "")
            if data.startswith(b"%PDF-"):
                suffix = ".pdf"
            elif "pdf" in item["content_type"].lower() or row["url"].endswith(".pdf"):
                raise ValueError("Expected a PDF; response has no PDF signature")
            elif "html" in item["content_type"].lower() or b"<html" in data[:5000].lower():
                suffix = ".html"
            elif row["url"].endswith(".json"):
                json.loads(data)
                suffix = ".json"
            elif row["url"].endswith(".md"):
                suffix = ".md"
            else:
                suffix = ".txt"
            dest = source if supplied else ROOT / "files" / row["category"] / (row["id"] + suffix)
            dest.parent.mkdir(parents=True, exist_ok=True)
            if not supplied:
                dest.write_bytes(data)
            plain = ROOT / "text" / (row["id"] + ".txt")
            plain.parent.mkdir(exist_ok=True)
            pages = None
            if suffix == ".pdf":
                body, pages = pdf_text(dest)
                plain.write_text(body)
                version = re.search(r"(?:arXiv|ChinaXiv):\s*([0-9.]+v\d+)", body[:12000])
                item["version_in_text"] = version.group(1) if version else None
                item["first_page_excerpt"] = body.split("\f")[0][:1800]
            else:
                body = data.decode("utf-8", errors="replace")
                if suffix == ".html":
                    parser = ReadableText()
                    parser.feed(body)
                    body = parser.result()
                plain.write_text(body)
            item.update(file=str(dest.relative_to(ROOT)), text=str(plain.relative_to(ROOT)),
                        sha256=hashlib.sha256(data).hexdigest(), bytes=len(data),
                        text_chars=len(body), pages=pages,
                        status="user_provided" if supplied else "downloaded")
            item.pop("error", None)
            host = urlsplit(item.get("resolved_url", row["url"])).netloc
            if not supplied and suffix != ".pdf" and host in SUBSCRIPTION:
                item["status"] = "access_required"
                item["error"] = "订阅来源，需机构访问或作者手动补充"
            elif len(body.strip()) < MIN_TEXT:
                item["status"] = "incomplete_text"
                item["error"] = f"正文少于 {MIN_TEXT} 字符，未取得完整内容"
            return item
        except Exception as exc:
            item["error"] = f"{type(exc).__name__}: {exc}"
    item["status"] = "failed"
    return item


def index(items):
    ok = [r for r in items if r["status"] in ("downloaded", "local_snapshot", "user_provided")]
    pdfs = [r for r in ok if r.get("file", "").endswith(".pdf")]
    lines = [
        "# 本地参考资料库", "",
        "本书正文引用的原始论文、综述、数据集与官方文档按章登记于此。每条来源先在 `sources.tsv` 登记，再由 `fetch.py` 下载、生成可搜索文本并写入 `manifest.json`。",
        "",
        f"当前清单 {len(items)} 项：已取得正文 {len(ok)} 项，其中 PDF {len(pdfs)} 份。其余项目的获取状态见文末。",
        "",
        "[来源清单](sources.tsv) · [下载与校验记录](manifest.json) · [待补充清单](NEEDED.md) · [本地索引](index.md)",
        "",
        "PDF 原件位于 `files/`，可搜索文本位于 `text/`。网页同时保存原始 HTML 与离线文本。不得把网页入口记作规范全文。",
        "",
        "`manifest.json` 记录获取时间、来源地址、校验值、字节数、PDF 页数及可从正文识别出的 arXiv 版本。网页按本地文件的 SHA-256 固定快照；下载完成不代表已经逐页审阅。",
        "",
        "`user_provided` 表示作者提供的原件，保留原文件名并记录校验值。清单中的 `local:` 地址只用于读取本资料库内的文件，不发起网络请求。",
        "",
        "`landing_only` 是索引入口，`incomplete_text` 表示未取得完整正文，`access_required` 表示来源要求机构访问，`failed` 表示请求失败。",
        "",
    ]
    for number, title in enumerate(CHAPTERS, 1):
        rows = [r for r in items if number in r["chapters"]]
        if not rows:
            continue
        lines += [f"## 第 {number} 章 {title}", "", "| 资料 | 本地文件 | 用途 |", "| --- | --- | --- |"]
        for r in rows:
            local = (f"[原件]({quote(r['file'])}) · [文本]({quote(r['text'])})" if r.get("file") else "未获取")
            if r["status"] != "downloaded":
                local += f"（{r['status']}）"
            lines.append(f"| [{r['title']}]({r['source_page']}) | {local} | {r['note']} |")
        lines.append("")
    lines += ["## 获取记录", "", "以下条目不能作为已经取得的完整资料：", ""]
    gaps = [r for r in items if r["status"] not in ("downloaded", "local_snapshot", "user_provided")]
    for r in gaps:
        lines.append(f"- **{r['id']}**：{r['status']}；{r.get('error', r['note'])}。")
    if not gaps:
        lines.append("当前清单中的资料均已取得正文。")
    lines += ["", "维护命令：`python3 references/fetch.py --only 资料ID` 下载指定条目；`--reindex` 只更新索引。"
                  "直接运行会补齐失败或未获取的项目，保留已下载的快照。"
                  "PDF 文本优先用 PyMuPDF 提取，缺失时回退到 Poppler 的 `pdftotext`。", ""]
    (ROOT / "README.md").write_text("\n".join(lines))

    table = ["# 参考资料索引", "",
             "按章号、类型或状态筛选；原件与文本均指向本资料库内的文件。", "",
             "| 章节 | 类型 | 资料 | 本地文件 | 状态 |", "| --- | --- | --- | --- | --- |"]
    for r in items:
        local = (f"[原件]({quote(r['file'])}) · [文本]({quote(r['text'])})" if r.get("file") else "未获取")
        table.append(f"| {','.join(map(str, r['chapters']))} | {r['category']} | "
                     f"[{r['title']}]({r['source_page']}) | {local} | {r['status']} |")
    table.append("")
    (ROOT / "index.md").write_text("\n".join(table))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--only", nargs="*", help="Only fetch these source ids")
    parser.add_argument("--reindex", action="store_true", help="Rebuild the index without downloading")
    args = parser.parse_args()
    with (ROOT / "sources.tsv").open() as stream:
        sources = list(csv.DictReader(stream, delimiter="\t"))
    manifest = ROOT / "manifest.json"
    known = {r["id"]: r for r in json.loads(manifest.read_text())} if manifest.exists() else {}
    for row in sources:
        if row["id"] in known:
            known[row["id"]]["title"] = row["title"]
            known[row["id"]]["note"] = row["note"]
            known[row["id"]]["chapters"] = [int(c) for c in row["chapters"].split(",")]
    pending = [r for r in sources if not args.reindex and
               (r["id"] in args.only if args.only else
                r["id"] not in known or known[r["id"]]["status"] == "failed")]
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        jobs = {pool.submit(fetch, row): row["id"] for row in pending}
        for job in concurrent.futures.as_completed(jobs):
            result = job.result()
            known[result["id"]] = result
            print(result["id"], result["status"], result.get("bytes", 0), flush=True)
            manifest.write_text(json.dumps(list(known.values()), ensure_ascii=False, indent=2) + "\n")
    items = [known[r["id"]] for r in sources if r["id"] in known]
    manifest.write_text(json.dumps(items, ensure_ascii=False, indent=2) + "\n")
    index(items)
    print("Indexed", len(items), "items", flush=True)


if __name__ == "__main__":
    main()
