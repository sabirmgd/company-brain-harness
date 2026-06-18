"""Source registry parsing and policy checks for Company Brain CLIs.

The harness avoids runtime dependencies, so this module parses the small YAML
shape used by source-registry.yml instead of requiring PyYAML.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from harness_common import conventions_dir, safe_relative_path


ALLOWED_CONNECTORS = {
    "filesystem",
    "manual",
    "fireflies",
    "google_workspace",
    "github",
    "slack",
    "hubspot",
    "apollo",
    "notion",
    "crm",
    "calendar",
    "email",
    "confluence",
}
ALLOWED_CONTROL_TIERS = {
    "company_owned",
    "customer_owned",
    "delegated_personal",
    "personal_private",
    "unknown",
}
ALLOWED_STATUSES = {
    "excluded",
    "proposed",
    "approved_staging_only",
    "active",
    "suspended",
    "retired",
    "future",
}
CAPTURE_ELIGIBLE_STATUSES = {"active", "approved_staging_only"}
PERSONAL_CONTROL_TIERS = {"personal_private", "unknown"}
SECRET_MARKERS = ("sk-", "Bearer ", "BEGIN ", "PRIVATE KEY", "password=", "token=")
POLICY_SECTIONS = {
    "capture",
    "routing",
    "audit",
    "scope",
    "raw_policy",
    "artifact_policy",
    "brain_artifacts",
    "sync",
    "dedupe",
}


@dataclass
class Source:
    id: str
    connector: str | None = None
    display_name: str | None = None
    control_tier: str | None = None
    status: str | None = None
    credential_ref: str | None = None
    owner: str | None = None
    review_owner: str | None = None
    capture: dict[str, Any] = field(default_factory=dict)
    scope: dict[str, Any] = field(default_factory=dict)
    routing: dict[str, Any] = field(default_factory=dict)
    raw_policy: dict[str, Any] = field(default_factory=dict)
    artifact_policy: dict[str, Any] = field(default_factory=dict)
    brain_artifacts: dict[str, Any] = field(default_factory=dict)
    sync: dict[str, Any] = field(default_factory=dict)
    dedupe: dict[str, Any] = field(default_factory=dict)
    audit: dict[str, Any] = field(default_factory=dict)

    @property
    def capture_allowed(self) -> bool:
        return bool(self.capture.get("allowed"))

    @property
    def approval_required(self) -> bool:
        return bool(self.capture.get("approval_required"))

    @property
    def approved_by(self) -> str | None:
        value = self.audit.get("approved_by")
        return str(value) if value not in {None, "", "null"} else None


@dataclass
class RegistryReport:
    path: str | None
    sources: list[Source]
    errors: list[str]
    warnings: list[str]

    @property
    def ok(self) -> bool:
        return not self.errors

    def to_json(self) -> dict[str, Any]:
        return {
            "path": self.path,
            "ok": self.ok,
            "errors": self.errors,
            "warnings": self.warnings,
            "sources": [
                {
                    "id": source.id,
                    "connector": source.connector,
                    "control_tier": source.control_tier,
                    "status": source.status,
                    "capture_allowed": source.capture_allowed,
                    "approval_required": source.approval_required,
                    "approved_by": source.approved_by,
                    "eligible_for_capture": is_capture_eligible(source),
                    "scope": source.scope,
                    "raw_policy": source.raw_policy,
                    "artifact_policy": source.artifact_policy,
                    "brain_artifacts": source.brain_artifacts,
                    "sync": source.sync,
                    "routing": source.routing,
                }
                for source in self.sources
            ],
        }


def registry_path(root: Path, override: str | None = None) -> Path:
    if override:
        return root / safe_relative_path(override, name="source registry")
    return conventions_dir(root) / "source-registry.yml"


def _strip_comment(raw: str) -> str:
    in_quote: str | None = None
    out = []
    for ch in raw:
        if ch in {"'", '"'}:
            in_quote = None if in_quote == ch else ch
        if ch == "#" and in_quote is None:
            break
        out.append(ch)
    return "".join(out).rstrip()


def _parse_scalar(value: str) -> Any:
    value = value.strip()
    if value in {"", "null", "None", "~"}:
        return None
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    lowered = value.lower()
    if lowered in {"true", "yes"}:
        return True
    if lowered in {"false", "no"}:
        return False
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        if not inner:
            return []
        return [_parse_scalar(part.strip()) for part in inner.split(",")]
    return value


def _split_key_value(line: str) -> tuple[str, Any] | None:
    if ":" not in line:
        return None
    key, value = line.split(":", 1)
    key = key.strip()
    if not key:
        return None
    return key, _parse_scalar(value.strip())


def parse_sources(text: str) -> list[Source]:
    sources: list[Source] = []
    current: Source | None = None
    section: str | None = None
    list_section: str | None = None
    list_key: str | None = None
    in_sources = False

    for raw in text.splitlines():
        line = _strip_comment(raw)
        if not line.strip():
            continue
        if not line.startswith(" ") and line.endswith(":"):
            in_sources = line.strip() == "sources:"
            section = None
            continue
        if not in_sources:
            continue

        if line.startswith("  - "):
            payload = line[4:].strip()
            parsed = _split_key_value(payload)
            if not parsed or parsed[0] != "id" or not parsed[1]:
                continue
            current = Source(id=str(parsed[1]))
            sources.append(current)
            section = None
            list_section = None
            list_key = None
            continue

        if current is None:
            continue
        indent = len(line) - len(line.lstrip(" "))
        stripped = line.strip()
        if indent == 4 and stripped.endswith(":"):
            section = stripped[:-1]
            list_section = None
            list_key = None
            continue
        if (
            indent == 8
            and section in POLICY_SECTIONS
            and list_section == section
            and list_key
            and stripped.startswith("- ")
        ):
            value = _parse_scalar(stripped[2:].strip())
            bucket = getattr(current, section).setdefault(list_key, [])
            if isinstance(bucket, list):
                bucket.append(value)
            continue
        parsed = _split_key_value(stripped)
        if not parsed:
            continue
        key, value = parsed
        raw_value = stripped.split(":", 1)[1].strip()
        starts_list = value is None and raw_value == ""
        if indent == 4:
            section = None
            list_section = None
            list_key = None
            if hasattr(current, key):
                setattr(current, key, None if value is None else str(value))
        elif indent == 6 and section in POLICY_SECTIONS:
            getattr(current, section)[key] = [] if starts_list else value
            list_section = section if starts_list else None
            list_key = key if starts_list else None

    return sources


def _looks_like_secret(value: str) -> bool:
    if any(marker in value for marker in SECRET_MARKERS):
        return True
    if "=" in value and not value.startswith(("env:", "secret-manager:", "gws:", "gh:", "manual:")):
        return True
    return False


def validate_sources(sources: list[Source]) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    seen: set[str] = set()

    for source in sources:
        prefix = f"{source.id}: "
        if source.id in seen:
            errors.append(prefix + "duplicate source id")
        seen.add(source.id)

        for attr in ("connector", "control_tier", "status", "credential_ref", "owner", "review_owner"):
            if not getattr(source, attr):
                errors.append(prefix + f"missing {attr}")

        if source.connector and source.connector not in ALLOWED_CONNECTORS:
            warnings.append(prefix + f"unknown connector {source.connector!r}; keep if this is intentional")
        if source.control_tier and source.control_tier not in ALLOWED_CONTROL_TIERS:
            errors.append(prefix + f"invalid control_tier {source.control_tier!r}")
        if source.status and source.status not in ALLOWED_STATUSES:
            errors.append(prefix + f"invalid status {source.status!r}")

        if source.credential_ref and _looks_like_secret(source.credential_ref):
            errors.append(prefix + "credential_ref appears to contain a credential value")

        if "allowed" not in source.capture:
            errors.append(prefix + "missing capture.allowed")
        if "approval_required" not in source.capture:
            errors.append(prefix + "missing capture.approval_required")
        if not source.routing.get("staging_destination"):
            warnings.append(prefix + "missing routing.staging_destination")
        if source.status in CAPTURE_ELIGIBLE_STATUSES:
            if not source.scope.get("include"):
                warnings.append(prefix + "eligible source should declare scope.include")
            if not source.scope.get("exclude"):
                warnings.append(prefix + "eligible source should declare scope.exclude")
            allowed_artifacts = source.artifact_policy.get("allowed") or source.brain_artifacts.get("allowed")
            if not allowed_artifacts and not source.raw_policy.get("store_raw"):
                warnings.append(prefix + "eligible source should declare artifact_policy.allowed or raw_policy.store_raw")
            if source.raw_policy.get("store_raw") not in {None, False, "false", "private_only", "temporary"}:
                errors.append(prefix + "raw_policy.store_raw must be false, private_only, or temporary")
            if source.sync.get("enabled") not in {None, True, False}:
                errors.append(prefix + "sync.enabled must be true or false")

        if source.control_tier in PERSONAL_CONTROL_TIERS:
            if source.capture_allowed:
                errors.append(prefix + "personal/unknown source cannot have capture.allowed=true")
            if source.status not in {"excluded", "suspended", "retired"}:
                errors.append(prefix + "personal/unknown source should be excluded, suspended, or retired")
            if source.raw_policy.get("store_raw") not in {None, False, "false"}:
                errors.append(prefix + "personal/unknown source cannot store raw material")

        if source.status in {"proposed", "future", "excluded", "suspended", "retired"} and source.capture_allowed:
            errors.append(prefix + f"status {source.status!r} cannot capture while capture.allowed=true")

        if source.status in CAPTURE_ELIGIBLE_STATUSES:
            if not source.capture_allowed:
                errors.append(prefix + "eligible status requires capture.allowed=true")
            if not source.approval_required and source.connector not in {"filesystem", "github", "manual"}:
                warnings.append(prefix + "capture should normally require approval")
            if not source.approved_by:
                warnings.append(prefix + "eligible source has no audit.approved_by")

    return errors, warnings


def load_registry(root: Path, override: str | None = None) -> RegistryReport:
    path = registry_path(root, override)
    if not path.is_file():
        return RegistryReport(
            path=str(path),
            sources=[],
            errors=[],
            warnings=[f"source registry not found: {path.relative_to(root)}"],
        )
    sources = parse_sources(path.read_text(encoding="utf-8", errors="ignore"))
    errors, warnings = validate_sources(sources)
    if not sources:
        errors.append("source registry has no sources")
    return RegistryReport(path=str(path), sources=sources, errors=errors, warnings=warnings)


def is_capture_eligible(source: Source) -> bool:
    if source.status not in CAPTURE_ELIGIBLE_STATUSES:
        return False
    if not source.capture_allowed:
        return False
    if source.control_tier in PERSONAL_CONTROL_TIERS:
        return False
    return True


def errors_for_source(report: RegistryReport, source_id: str) -> list[str]:
    prefix = f"{source_id}: "
    return [error for error in report.errors if error.startswith(prefix)]


def find_source(
    report: RegistryReport,
    *,
    source_id: str | None = None,
    connector: str | None = None,
) -> Source | None:
    candidates = report.sources
    if source_id:
        candidates = [source for source in candidates if source.id == source_id]
    if connector:
        candidates = [source for source in candidates if source.connector == connector]
    if len(candidates) == 1:
        return candidates[0]
    eligible = [source for source in candidates if is_capture_eligible(source)]
    return eligible[0] if len(eligible) == 1 else None
