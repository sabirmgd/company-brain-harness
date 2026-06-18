#!/usr/bin/env python3
"""Export Confluence pages as normalized Company Brain source records."""
from __future__ import annotations

import argparse
import base64
import html
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from pathlib import Path
from typing import Any


DEFAULT_BASE_URL = os.environ.get("CONFLUENCE_BASE_URL") or os.environ.get("ATLASSIAN_BASE_URL")
DEFAULT_EMAIL = os.environ.get("ATLASSIAN_EMAIL")
DEFAULT_TOKEN = os.environ.get("ATLASSIAN_API_TOKEN") or os.environ.get("CONFLUENCE_API_TOKEN")


class TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []
        self.skip_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"script", "style"}:
            self.skip_depth += 1
        if tag in {"p", "div", "br", "li", "tr", "h1", "h2", "h3"}:
            self.parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style"} and self.skip_depth:
            self.skip_depth -= 1
        if tag in {"p", "div", "li", "tr", "h1", "h2", "h3"}:
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        if not self.skip_depth:
            self.parts.append(data)

    def text(self) -> str:
        value = html.unescape(" ".join(self.parts))
        value = re.sub(r"[ \t\r\f\v]+", " ", value)
        value = re.sub(r"\n\s+", "\n", value)
        value = re.sub(r"\n{3,}", "\n\n", value)
        return value.strip()


def slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-") or "page"


def html_to_text(value: str) -> str:
    parser = TextExtractor()
    parser.feed(value or "")
    return parser.text()


def clip(value: str, limit: int) -> str:
    value = value.strip()
    if len(value) <= limit:
        return value
    return value[: max(0, limit - 20)].rstrip() + "\n\n[summary clipped]"


def auth_header(email: str, token: str) -> str:
    raw = f"{email}:{token}".encode("utf-8")
    return "Basic " + base64.b64encode(raw).decode("ascii")


def request_json(url: str, *, email: str, token: str) -> dict[str, Any]:
    req = urllib.request.Request(
        url,
        headers={
            "Authorization": auth_header(email, token),
            "Accept": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read(2048).decode("utf-8", errors="replace")
        raise RuntimeError(f"Confluence API returned HTTP {exc.code}: {body}") from exc


def confluence_url(base_url: str, link: str) -> str:
    if link.startswith(("http://", "https://")):
        return link
    parsed = urllib.parse.urlparse(base_url)
    origin = f"{parsed.scheme}://{parsed.netloc}"
    if link.startswith("/wiki/") or link == "/wiki":
        return origin + link
    if link.startswith("/"):
        return base_url.rstrip("/") + link
    return base_url.rstrip("/") + "/" + link


def build_cql(args: argparse.Namespace) -> str:
    if args.cql:
        return args.cql
    clauses = ["type = page"]
    if args.space_key:
        clauses.insert(0, f'space = "{args.space_key}"')
    if args.modified_since:
        clauses.append(f'lastmodified >= "{args.modified_since}"')
    return " and ".join(clauses) + " order by lastmodified desc"


def confluence_search(args: argparse.Namespace) -> list[dict[str, Any]]:
    if not args.base_url:
        raise RuntimeError("missing --base-url or CONFLUENCE_BASE_URL/ATLASSIAN_BASE_URL")
    if not args.email or not args.api_token:
        raise RuntimeError("missing ATLASSIAN_EMAIL or ATLASSIAN_API_TOKEN")
    if not args.space_key and not args.cql:
        raise RuntimeError("refusing broad Confluence export; pass --space-key or --cql")

    base_url = args.base_url.rstrip("/")
    cql = build_cql(args)
    start = 0
    pages: list[dict[str, Any]] = []
    seen_page_ids: set[str] = set()
    next_url: str | None = None
    seen_urls: set[str] = set()

    while len(pages) < args.limit:
        page_size = min(args.page_size, args.limit - len(pages))
        if next_url:
            url = confluence_url(base_url, next_url)
        else:
            params = urllib.parse.urlencode({
                "cql": cql,
                "limit": page_size,
                "start": start,
                "expand": "body.storage,space,version,_links",
            })
            url = f"{base_url}/rest/api/content/search?{params}"
        if url in seen_urls:
            break
        seen_urls.add(url)

        data = request_json(url, email=args.email, token=args.api_token)
        results = data.get("results") or []
        if not isinstance(results, list) or not results:
            break
        new_count = 0
        for item in results:
            if not isinstance(item, dict):
                continue
            page_id = str(item.get("id") or "")
            if page_id in seen_page_ids:
                continue
            seen_page_ids.add(page_id)
            pages.append(item)
            new_count += 1
            if len(pages) >= args.limit:
                break
        links = data.get("_links") if isinstance(data.get("_links"), dict) else {}
        next_link = links.get("next")
        if next_link:
            next_url = str(next_link)
            continue
        size = int(data.get("size") or len(results))
        if size <= 0 or len(results) < page_size or new_count == 0:
            break
        start += size

    return pages


def load_input_json(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict):
        results = data.get("results")
        if isinstance(results, list):
            return [item for item in results if isinstance(item, dict)]
        if data.get("id"):
            return [data]
    if isinstance(data, list):
        return [item for item in data if isinstance(item, dict)]
    raise ValueError(f"{path}: expected Confluence search JSON or list of page objects")


def page_url(base_url: str | None, page: dict[str, Any]) -> str | None:
    links = page.get("_links") if isinstance(page.get("_links"), dict) else {}
    webui = links.get("webui")
    base = links.get("base") or base_url
    if webui and base:
        return str(base).rstrip("/") + str(webui)
    tiny = links.get("tinyui")
    if tiny and base:
        return str(base).rstrip("/") + str(tiny)
    return None


def normalize_page(page: dict[str, Any], args: argparse.Namespace) -> dict[str, Any]:
    page_id = str(page.get("id") or "").strip()
    title = str(page.get("title") or page_id or "Untitled Confluence Page").strip()
    space = page.get("space") if isinstance(page.get("space"), dict) else {}
    space_key = str(space.get("key") or args.space_key or "confluence").strip()
    version = page.get("version") if isinstance(page.get("version"), dict) else {}
    by = version.get("by") if isinstance(version.get("by"), dict) else {}
    body = page.get("body") if isinstance(page.get("body"), dict) else {}
    storage = body.get("storage") if isinstance(body.get("storage"), dict) else {}
    text = html_to_text(str(storage.get("value") or ""))
    target_prefix = args.target_prefix.strip("/")
    return {
        "external_id": page_id,
        "title": title,
        "summary": clip(text or title, args.summary_chars),
        "target_path": f"{target_prefix}/{slugify(space_key)}/{slugify(title)}.md",
        "tags": ["confluence", space_key.lower(), "source"],
        "artifact_type": args.artifact_type,
        "visibility": args.visibility,
        "author": by.get("displayName") or space.get("name") or "Confluence",
        "occurred_at": version.get("when"),
        "url": page_url(args.base_url, page),
        "cursor": version.get("when") or page_id,
    }


def write_jsonl(records: list[dict[str, Any]], path: Path | None) -> None:
    if path is None:
        for record in records:
            print(json.dumps(record, sort_keys=True))
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, sort_keys=True) + "\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Export Confluence pages to normalized Company Brain JSONL.")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help="Confluence base URL, usually https://site.atlassian.net/wiki")
    parser.add_argument("--email", default=DEFAULT_EMAIL, help="Atlassian email; defaults to ATLASSIAN_EMAIL")
    parser.add_argument("--api-token", default=DEFAULT_TOKEN, help="Atlassian API token; defaults to ATLASSIAN_API_TOKEN")
    parser.add_argument("--space-key", default=None, help="Confluence space key to export")
    parser.add_argument("--cql", default=None, help="explicit CQL query; overrides --space-key/--modified-since")
    parser.add_argument("--modified-since", default=None, help="CQL date, for example 2026-06-01")
    parser.add_argument("--limit", type=int, default=50)
    parser.add_argument("--page-size", type=int, default=25)
    parser.add_argument("--target-prefix", default="Resources/confluence")
    parser.add_argument("--artifact-type", default="curated_note")
    parser.add_argument("--visibility", default="team")
    parser.add_argument("--summary-chars", type=int, default=1800)
    parser.add_argument("--input-json", type=Path, default=None, help="offline Confluence API JSON fixture")
    parser.add_argument("--output-jsonl", type=Path, default=None)
    args = parser.parse_args(argv)

    try:
        pages = load_input_json(args.input_json) if args.input_json else confluence_search(args)
        records = [normalize_page(page, args) for page in pages if page.get("id")]
        write_jsonl(records, args.output_jsonl)
    except (RuntimeError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        return 1

    if args.output_jsonl:
        print(json.dumps({
            "action": "exported",
            "connector": "confluence",
            "count": len(records),
            "output_jsonl": str(args.output_jsonl),
            "note": "credentials were read from arguments/environment and were not written",
        }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
