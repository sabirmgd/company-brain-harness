"""Shared helpers for source-governed capture scripts."""
from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from harness_common import conventions_dir, staging_dir
from source_registry import Source


PRIVATE_VISIBILITIES = {"private", "personal", "personal_private", "dm", "user_space"}
RESTRICTED_VISIBILITIES = {"restricted", "confidential"}
SECRET_MARKERS = ("sk-", "Bearer ", "BEGIN ", "PRIVATE KEY", "password=", "token=")
SYNC_STATE_FILE = "source-sync-state.json"
RAW_KEYS = ("raw_body", "raw_text", "raw_content", "raw_payload", "raw")


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-") or "item"


def evidence_dir(root: Path) -> Path:
    return staging_dir(root) / "evidence"


def evidence_path(root: Path, source_id: str) -> Path:
    return evidence_dir(root) / f"{slugify(source_id)}.jsonl"


def raw_evidence_dir(root: Path) -> Path:
    return staging_dir(root) / "raw"


def raw_evidence_path(root: Path, source_id: str, external_id: str, extension: str) -> Path:
    safe_extension = re.sub(r"[^a-z0-9]+", "", extension.lower()).strip(".") or "txt"
    return raw_evidence_dir(root) / slugify(source_id) / f"{slugify(external_id)}.{safe_extension}"


def state_path(root: Path) -> Path:
    return conventions_dir(root) / SYNC_STATE_FILE


def load_state(root: Path) -> dict[str, Any]:
    path = state_path(root)
    if not path.is_file():
        return {"schema_version": "1.0", "sources": {}}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"schema_version": "1.0", "sources": {}}
    if not isinstance(data, dict):
        return {"schema_version": "1.0", "sources": {}}
    data.setdefault("schema_version", "1.0")
    data.setdefault("sources", {})
    return data


def save_state(root: Path, state: dict[str, Any]) -> None:
    path = state_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def source_state(state: dict[str, Any], source_id: str) -> dict[str, Any]:
    sources = state.setdefault("sources", {})
    current = sources.setdefault(source_id, {})
    current.setdefault("items", {})
    return current


def content_hash(record: dict[str, Any]) -> str:
    ignored = {"pulled_at", "last_seen_at", "cursor"}
    stable = {key: value for key, value in record.items() if key not in ignored}
    payload = json.dumps(stable, sort_keys=True, ensure_ascii=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def looks_like_secret(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    return any(marker in value for marker in SECRET_MARKERS)


def record_has_secret(record: dict[str, Any]) -> bool:
    for key in ("title", "summary", "body", "text", "url", *RAW_KEYS):
        if looks_like_secret(record.get(key)):
            return True
    return False


def normalize_tags(value: Any, fallback: list[str]) -> list[str]:
    tags: list[str] = []
    if isinstance(value, str):
        tags.extend(part.strip() for part in value.split(",") if part.strip())
    elif isinstance(value, list):
        tags.extend(str(part).strip() for part in value if str(part).strip())
    tags.extend(fallback)
    out: list[str] = []
    seen: set[str] = set()
    for tag in tags:
        key = tag.lower()
        if key not in seen:
            seen.add(key)
            out.append(tag)
    return out[:8]


def allowed_artifacts(source: Source) -> list[str]:
    values = source.artifact_policy.get("allowed") or source.brain_artifacts.get("allowed")
    if isinstance(values, list):
        return [str(value) for value in values]
    return []


def blocked_artifacts(source: Source) -> list[str]:
    values = source.artifact_policy.get("not_allowed") or source.brain_artifacts.get("not_allowed")
    if isinstance(values, list):
        return [str(value) for value in values]
    return []


def raw_store_policy(source: Source) -> str:
    value = source.raw_policy.get("store_raw", "private_only")
    if value is False:
        return "false"
    return str(value)


def raw_storage_allowed(source: Source) -> bool:
    return raw_store_policy(source) in {"private_only", "temporary"}


def raw_content(record: dict[str, Any]) -> tuple[str | None, str]:
    for key in RAW_KEYS:
        if key not in record:
            continue
        value = record.get(key)
        if value is None or value == "":
            continue
        if isinstance(value, (dict, list)):
            return json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n", "json"
        text = str(value)
        raw_format = str(record.get("raw_format") or record.get("raw_type") or "").lower()
        if raw_format in {"html", "md", "markdown", "json", "txt", "text"}:
            extension = "md" if raw_format == "markdown" else raw_format
            extension = "txt" if extension == "text" else extension
            return text, extension
        if text.lstrip().startswith(("{", "[")):
            return text, "json"
        if "<html" in text[:200].lower() or "<p" in text[:200].lower():
            return text, "html"
        return text, "txt"
    return None, "txt"


def visibility(record: dict[str, Any]) -> str:
    return str(record.get("visibility") or record.get("source_visibility") or "company").strip().lower()


def allowed_to_store_evidence(record: dict[str, Any], *, allow_restricted: bool) -> tuple[bool, str | None]:
    current = visibility(record)
    if current in PRIVATE_VISIBILITIES:
        return False, f"visibility {current!r} is private/personal"
    if current in RESTRICTED_VISIBILITIES and not allow_restricted:
        return False, f"visibility {current!r} requires restricted workflow"
    if record_has_secret(record):
        return False, "record appears to contain a secret"
    return True, None


def evidence_record(source: Source, record: dict[str, Any], *, pulled_at: str) -> dict[str, Any]:
    external_id = str(record.get("external_id") or record.get("id") or "").strip()
    title = str(record.get("title") or external_id or "Untitled source item").strip()
    summary = str(record.get("summary") or record.get("body") or record.get("text") or "").strip()
    policy = raw_store_policy(source)
    if policy in {"false", "False", "0"}:
        summary = str(record.get("summary") or record.get("snippet") or title).strip()
    return {
        "schema_version": "1.0",
        "source_id": source.id,
        "connector": source.connector,
        "external_id": external_id,
        "source_ref": f"{source.id}/{external_id}",
        "title": title,
        "summary": summary,
        "url": record.get("url"),
        "author": record.get("author") or source.display_name or source.id,
        "occurred_at": record.get("occurred_at") or record.get("created_at"),
        "pulled_at": pulled_at,
        "visibility": visibility(record),
        "sensitivity": record.get("sensitivity") or "internal",
        "artifact_type": record.get("artifact_type") or "curated_summary",
        "target_path": record.get("target_path"),
        "tags": record.get("tags") or [],
        "cursor": record.get("cursor"),
        "hash": content_hash(record),
    }


def iter_jsonl(path: Path):
    with path.open(encoding="utf-8") as handle:
        for line_number, raw in enumerate(handle, start=1):
            line = raw.strip()
            if not line:
                continue
            try:
                value = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_number}: invalid JSON: {exc}") from exc
            if not isinstance(value, dict):
                raise ValueError(f"{path}:{line_number}: expected JSON object")
            yield value
