#!/usr/bin/env python3
"""connections-check - forgiving Company Brain connector health check.

Read-only. Prints whether the configured brain root and optional data sources are
available. Missing optional connectors are setup nudges, not failures.

Usage:
    bin/connections-check.py
    bin/connections-check.py --json
    bin/connections-check.py --root /path/to/brain-root
    bin/connections-check.py --live   # run lightweight API smoke tests where safe

Exit codes:
    0 = core brain access is available
    2 = core brain access is missing or unusable
    3 = bad local configuration / invalid arguments
"""
from __future__ import annotations

import argparse
import json
import os
import urllib.error
import urllib.request
import shutil
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from datetime import date
from pathlib import Path
from typing import Optional

from harness_common import conventions_dir, resolve_root, restricted_prefixes, routing_file, staging_dir


DEFAULT_ROOT = (
    os.environ.get("BRAIN_ROOT")
    or os.environ.get("COMPANY_BRAIN_ROOT")
    or os.environ.get("COMPANY_OS_ROOT")
    or os.getcwd()
)

DEFAULT_ORG = (
    os.environ.get("COMPANY_BRAIN_GITHUB_ORG")
    or os.environ.get("COMPANY_OS_GITHUB_ORG")
    or ""
)
GOOGLE_DRIVE_APP = Path("/Applications/Google Drive.app")


@dataclass
class Check:
    key: str
    label: str
    status: str
    required: bool
    detail: str
    next_step: Optional[str] = None
    unlocks: Optional[str] = None


@dataclass
class Report:
    generated: str
    root: str
    overall: str
    checks: list[Check] = field(default_factory=list)

    def add(self, check: Check) -> None:
        self.checks.append(check)

    def core_ok(self) -> bool:
        return all(c.status == "ok" for c in self.checks if c.required)


def run(cmd: list[str], *, timeout: int = 12) -> tuple[int, str, str]:
    try:
        p = subprocess.run(
            cmd,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
            check=False,
        )
        return p.returncode, p.stdout.strip(), p.stderr.strip()
    except FileNotFoundError as e:
        return 127, "", str(e)
    except subprocess.TimeoutExpired as e:
        return 124, e.stdout or "", e.stderr or "command timed out"


def check_drive(report: Report, root: Path) -> None:
    if not root.is_dir():
        report.add(Check(
            key="drive_root",
            label="Company Brain root",
            status="fail",
            required=True,
            detail=f"Brain root not found: {root}",
            next_step="Mount or clone the brain root and set BRAIN_ROOT if the path differs.",
            unlocks="Required for every Company Brain session.",
        ))
        return

    report.add(Check(
        key="drive_root",
        label="Company Brain root",
        status="ok",
        required=True,
        detail=f"Found {root}",
        unlocks="Shared source of truth for agent sessions.",
    ))

    try:
        route = routing_file(root)
        conventions = conventions_dir(root)
        staging = staging_dir(root)
    except ValueError as exc:
        report.add(Check(
            key="brain_config",
            label="Brain config",
            status="fail",
            required=True,
            detail=str(exc),
            next_step="Fix the relative paths in company-brain.yml / company-os.yml.",
            unlocks="Portable harness configuration.",
        ))
        return

    missing = [str(p.relative_to(root)) for p in (route, conventions / "README.md") if not p.exists()]
    report.add(Check(
        key="brain_routing",
        label="Brain routing files",
        status="ok" if not missing else "fail",
        required=True,
        detail="Routing file and conventions README found." if not missing else "Missing: " + ", ".join(missing),
        next_step=None if not missing else "Restore routing and conventions files before onboarding teammates.",
        unlocks="Lets Claude route work to the correct folder.",
    ))

    policy = conventions / "CAPTURE_POLICY.md"
    connections = conventions / "CONNECTIONS.md"
    flows = conventions / "HARNESS_FLOWS.md"
    status = conventions / "HARNESS_STATUS.md"
    missing_docs = [str(p.relative_to(root)) for p in (policy, connections, flows, status) if not p.exists()]
    report.add(Check(
        key="harness_docs",
        label="Harness docs",
        status="ok" if not missing_docs else "warn",
        required=False,
        detail="Connection, capture policy, harness flows, and status docs found." if not missing_docs else "Missing: " + ", ".join(missing_docs),
        next_step=None if not missing_docs else "Add the missing harness docs before broader rollout.",
        unlocks="Makes setup repeatable for the brain owner and teammates.",
    ))

    report.add(Check(
        key="staging_dir",
        label="Private staging area",
        status="ok" if staging.exists() else "missing",
        required=False,
        detail=f"Staging dir found: {staging.relative_to(root)}" if staging.exists() else f"Staging dir not found yet: {staging.relative_to(root)}",
        next_step=None if staging.exists() else "Run a staging workflow once or create the staging dir before team intake.",
        unlocks="Preview-first propose -> approve -> promote workflow.",
    ))

    for prefix in restricted_prefixes(root):
        restricted = root / prefix
        if not restricted.exists():
            continue
        readable = os.access(restricted, os.R_OK)
        report.add(Check(
            key=f"restricted_permissions:{prefix}",
            label=f"Restricted permissions: {prefix}",
            status="warn" if readable else "ok",
            required=False,
            detail=(
                "Restricted path exists and appears readable from this machine. Contents were not inspected."
                if readable else
                "Restricted path exists but is not readable from this machine."
            ),
            next_step=(
                "Confirm restricted-folder permissions before inviting the broader team."
                if readable else None
            ),
            unlocks="Protects sensitive material from broad team indexing.",
        ))


def check_google_drive_app(report: Report) -> None:
    report.add(Check(
        key="google_drive_desktop",
        label="Google Drive for Desktop",
        status="ok" if GOOGLE_DRIVE_APP.exists() else "missing",
        required=False,
        detail="Installed at /Applications/Google Drive.app" if GOOGLE_DRIVE_APP.exists() else "Not found in /Applications.",
        next_step=None if GOOGLE_DRIVE_APP.exists() else "Install Google Drive for Desktop and sign in.",
        unlocks="Local folder access when the brain backend is Google Drive.",
    ))


def check_gws(report: Report, live: bool) -> None:
    path = shutil.which("gws")
    if not path:
        report.add(Check(
            key="gws",
            label="Google Workspace CLI",
            status="missing",
            required=False,
            detail="gws is not on PATH.",
            next_step="Install googleworkspace-cli, then run: gws auth setup; gws auth login -s drive,gmail,calendar,docs,sheets",
            unlocks="Shared Google Drive/Gmail/Calendar/Docs automation for the engine.",
        ))
        return

    code, out, err = run(["gws", "auth", "status"])
    if code != 0:
        report.add(Check(
            key="gws",
            label="Google Workspace CLI",
            status="warn",
            required=False,
            detail=f"Installed at {path}, but auth status failed: {err or out}",
            next_step="Run: gws auth setup; gws auth login -s drive,gmail,calendar,docs,sheets",
            unlocks="Shared Google Drive/Gmail/Calendar/Docs automation for the engine.",
        ))
        return

    try:
        status = json.loads(out)
    except json.JSONDecodeError:
        status = {}

    auth_method = status.get("auth_method") or status.get("credential_source") or "unknown"
    ok = auth_method not in {"none", "unknown"}
    detail = f"Installed at {path}; auth_method={auth_method}."

    if ok and live:
        live_code, _, live_err = run(
            ["gws", "drive", "files", "list", "--params", '{"pageSize":1}'],
            timeout=20,
        )
        if live_code != 0:
            report.add(Check(
                key="gws",
                label="Google Workspace CLI",
                status="warn",
                required=False,
                detail=detail + f" Live Drive smoke test failed: {live_err}",
                next_step="Refresh auth with gws auth login or check Workspace admin approval.",
                unlocks="Shared Google Drive/Gmail/Calendar/Docs automation for the engine.",
            ))
            return
        detail += " Live Drive smoke test passed."

    report.add(Check(
        key="gws",
        label="Google Workspace CLI",
        status="ok" if ok else "missing",
        required=False,
        detail=detail,
        next_step=None if ok else "Run: gws auth setup; gws auth login -s drive,gmail,calendar,docs,sheets",
        unlocks="Shared Google Drive/Gmail/Calendar/Docs automation for the engine.",
    ))


def check_fireflies(report: Report, live: bool) -> None:
    key = os.environ.get("FIREFLIES_API_KEY")
    source = (
        os.environ.get("COMPANY_BRAIN_FIREFLIES_SOURCE")
        or os.environ.get("COMPANY_OS_FIREFLIES_SOURCE")
        or ""
    ).strip().lower()
    approved = (
        os.environ.get("COMPANY_BRAIN_CAPTURE_POLICY_APPROVED")
        or os.environ.get("COMPANY_OS_CAPTURE_POLICY_APPROVED")
        or ""
    ).strip().lower() in {
        "1", "true", "yes", "approved"
    }
    if not key:
        report.add(Check(
            key="fireflies",
            label="Fireflies company source",
            status="missing",
            required=False,
            detail="FIREFLIES_API_KEY is not set in the environment.",
            next_step="After CAPTURE_POLICY.md is approved, set a company Fireflies key and COMPANY_BRAIN_FIREFLIES_SOURCE=company.",
            unlocks="Company meeting capture into private staging.",
        ))
        return

    if source != "company" or not approved:
        detail_parts = ["FIREFLIES_API_KEY is set, but it is not marked as a company-approved capture source."]
        if source:
            detail_parts.append(f"COMPANY_BRAIN_FIREFLIES_SOURCE={source}.")
        else:
            detail_parts.append("COMPANY_BRAIN_FIREFLIES_SOURCE is unset.")
        detail_parts.append(
            "COMPANY_BRAIN_CAPTURE_POLICY_APPROVED is approved."
            if approved else
            "COMPANY_BRAIN_CAPTURE_POLICY_APPROVED is not approved."
        )
        report.add(Check(
            key="fireflies",
            label="Fireflies company source",
            status="warn",
            required=False,
            detail=" ".join(detail_parts),
            next_step="Do not use personal Fireflies for the harness. Use a company workspace/key only after policy approval.",
            unlocks="Company meeting capture into private staging.",
        ))
        return

    detail = "Company-approved Fireflies source is configured. Key value was not printed."
    if live:
        body = json.dumps({"query": "{ user { email } }"}).encode("utf-8")
        req = urllib.request.Request(
            "https://api.fireflies.ai/graphql",
            data=body,
            headers={
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=20) as response:
                payload = response.read(2048).decode("utf-8", errors="replace")
        except urllib.error.HTTPError as exc:
            payload = exc.read(2048).decode("utf-8", errors="replace")
            report.add(Check(
                key="fireflies",
                label="Fireflies company source",
                status="warn",
                required=False,
                detail=f"Key is set, but Fireflies smoke test failed with HTTP {exc.code}: {payload}",
                next_step="Verify the company FIREFLIES_API_KEY has API access.",
                unlocks="Company meeting capture into private staging.",
            ))
            return
        except (urllib.error.URLError, TimeoutError) as exc:
            report.add(Check(
                key="fireflies",
                label="Fireflies company source",
                status="warn",
                required=False,
                detail=f"Key is set, but Fireflies smoke test failed: {exc}",
                next_step="Verify network access and retry later.",
                unlocks="Company meeting capture into private staging.",
            ))
            return
        if "errors" in payload and "user" not in payload:
            report.add(Check(
                key="fireflies",
                label="Fireflies company source",
                status="warn",
                required=False,
                detail=f"Key is set, but Fireflies returned GraphQL errors: {payload}",
                next_step="Verify the company FIREFLIES_API_KEY has workspace API access.",
                unlocks="Company meeting capture into private staging.",
            ))
            return
        detail += " API smoke test passed."

    report.add(Check(
        key="fireflies",
        label="Fireflies company source",
        status="ok",
        required=False,
        detail=detail,
        unlocks="Company meeting capture into private staging.",
    ))


def check_github(report: Report, org: str, live: bool) -> None:
    path = shutil.which("gh")
    if not path:
        report.add(Check(
            key="github",
            label="GitHub CLI",
            status="missing",
            required=False,
            detail="gh is not on PATH.",
            next_step="Install gh and authenticate to the company GitHub org.",
            unlocks="Repo-aware POCs and stack guardrails.",
        ))
        return

    code, out, err = run(["gh", "auth", "status", "-h", "github.com"], timeout=15)
    if code != 0:
        report.add(Check(
            key="github",
            label="GitHub CLI",
            status="warn",
            required=False,
            detail=f"gh found at {path}, but auth failed: {err or out}",
            next_step="Run: gh auth login",
            unlocks="Repo-aware POCs and stack guardrails.",
        ))
        return

    if not org:
        report.add(Check(
            key="github",
            label="GitHub org access",
            status="missing",
            required=False,
            detail="gh is authenticated, but no company org is configured.",
            next_step="Set COMPANY_BRAIN_GITHUB_ORG to enable repo-awareness checks.",
            unlocks="Repo-aware POCs and stack guardrails.",
        ))
        return

    detail = f"gh authenticated; org={org}."
    if live:
        repo_code, repo_out, repo_err = run(
            ["gh", "repo", "list", org, "--limit", "1", "--json", "name"],
            timeout=20,
        )
        if repo_code != 0:
            report.add(Check(
                key="github",
                label="GitHub org access",
                status="warn",
                required=False,
                detail=detail + f" Repo list failed: {repo_err or repo_out}",
                next_step=f"Confirm GitHub access to the {org} organization.",
                unlocks="Repo-aware POCs and stack guardrails.",
            ))
            return
        detail += " Repo list smoke test passed."

    report.add(Check(
        key="github",
        label="GitHub org access",
        status="ok",
        required=False,
        detail=detail,
        unlocks="Repo-aware POCs and stack guardrails.",
    ))


def check_brain_health(report: Report) -> None:
    script = Path(__file__).resolve().parent / "brain-health.py"
    report.add(Check(
        key="brain_health",
        label="Brain health scorer",
        status="ok" if script.exists() else "missing",
        required=False,
        detail=f"Found {script}" if script.exists() else "bin/brain-health.py not found.",
        next_step=None if script.exists() else "Restore bin/brain-health.py.",
        unlocks="Read-only score and empty-folder punch list.",
    ))


def check_promotion_cli(report: Report) -> None:
    script = Path(__file__).resolve().parent / "promote-to-brain.py"
    report.add(Check(
        key="promotion_cli",
        label="Generic promotion CLI",
        status="ok" if script.exists() else "missing",
        required=False,
        detail=f"Found {script}" if script.exists() else "bin/promote-to-brain.py not found.",
        next_step=None if script.exists() else "Build the generic approved-note promotion path.",
        unlocks="Approved notes can be promoted into any filesystem-backed brain root.",
    ))


def check_staging_clis(report: Report) -> None:
    base = Path(__file__).resolve().parent
    missing = [
        p.name for p in (
            base / "stage-brain-note.py",
            base / "approve-staged-note.py",
        )
        if not p.exists()
    ]
    report.add(Check(
        key="staging_approval_clis",
        label="Staging and approval CLIs",
        status="ok" if not missing else "missing",
        required=False,
        detail="stage-brain-note.py and approve-staged-note.py found." if not missing else "Missing: " + ", ".join(missing),
        next_step=None if not missing else "Restore the staging/approval CLIs before team content intake.",
        unlocks="Team-safe propose -> approve/reject/revise workflow.",
    ))


def render(report: Report) -> str:
    labels = {
        "ok": "ok",
        "missing": "not set up",
        "warn": "needs attention",
        "fail": "blocked",
    }
    order = {"fail": 0, "warn": 1, "missing": 2, "ok": 3}
    checks = sorted(report.checks, key=lambda c: (not c.required, order.get(c.status, 9), c.key))

    lines = []
    lines.append("")
    lines.append(f"COMPANY BRAIN CONNECTION CHECK [{report.overall}]")
    lines.append(f"root: {report.root}")
    lines.append("")
    for c in checks:
        required = "required" if c.required else "optional"
        lines.append(f"- {c.label}: {labels.get(c.status, c.status)} ({required})")
        lines.append(f"  {c.detail}")
        if c.unlocks:
            lines.append(f"  Unlocks: {c.unlocks}")
        if c.next_step:
            lines.append(f"  Next: {c.next_step}")
    lines.append("")
    if report.core_ok():
        lines.append("Core brain access is ready. Optional missing connectors can be added over time.")
    else:
        lines.append("Core brain access is blocked. Fix required checks before onboarding teammates.")
    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description="Forgiving Company Brain connector health check.")
    ap.add_argument("--root", default=DEFAULT_ROOT, help="Company Brain root path")
    ap.add_argument("--github-org", default=DEFAULT_ORG, help="GitHub organization to check")
    ap.add_argument("--live", action="store_true", help="run lightweight API smoke tests")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    args = ap.parse_args()

    root = resolve_root(args.root)
    report = Report(
        generated=date.today().isoformat(),
        root=str(root),
        overall="pending",
    )

    check_drive(report, root)
    check_google_drive_app(report)
    check_gws(report, args.live)
    check_fireflies(report, args.live)
    check_github(report, args.github_org, args.live)
    check_brain_health(report)
    check_promotion_cli(report)
    check_staging_clis(report)

    report.overall = "ready" if report.core_ok() else "blocked"

    if args.json:
        print(json.dumps({
            "generated": report.generated,
            "root": report.root,
            "overall": report.overall,
            "checks": [asdict(c) for c in report.checks],
        }, indent=2))
    else:
        print(render(report))

    return 0 if report.core_ok() else 2


if __name__ == "__main__":
    sys.exit(main())
