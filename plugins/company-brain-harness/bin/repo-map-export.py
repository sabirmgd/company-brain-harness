#!/usr/bin/env python3
"""Export local git repository maps as normalized Company Brain records."""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


SKIP_DIRS = {
    ".git",
    ".cache",
    ".npm",
    "node_modules",
    "dist",
    "build",
    "coverage",
    ".next",
    ".pnpm-store",
    ".terraform",
    ".turbo",
    ".venv",
    ".yarn",
    "__pycache__",
    "vendor",
}


IMPORTANT_FILES = (
    "README.md",
    "CLAUDE.md",
    "AGENTS.md",
    "package.json",
    "pnpm-workspace.yaml",
    "turbo.json",
    "tsconfig.json",
    "nest-cli.json",
    "next.config.js",
    "next.config.ts",
    "vite.config.ts",
    "Dockerfile",
    "docker-compose.yml",
    ".github/workflows",
    ".gitlab-ci.yml",
)


def slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-") or "repo"


def run_git(repo: Path, args: list[str]) -> str:
    result = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, check=False)
    if result.returncode != 0:
        return ""
    return result.stdout.strip()


def read_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def detect_stack(repo: Path) -> list[str]:
    markers: list[str] = []
    package = read_json(repo / "package.json")
    deps = {}
    for key in ("dependencies", "devDependencies"):
        value = package.get(key)
        if isinstance(value, dict):
            deps.update(value)
    if package:
        markers.append("node")
    if "@nestjs/core" in deps:
        markers.append("nestjs")
    if "next" in deps:
        markers.append("nextjs")
    if "react" in deps:
        markers.append("react")
    if "vite" in deps:
        markers.append("vite")
    if (repo / "Dockerfile").exists() or (repo / "docker-compose.yml").exists():
        markers.append("docker")
    if (repo / ".gitlab-ci.yml").exists():
        markers.append("gitlab-ci")
    if (repo / ".github" / "workflows").exists():
        markers.append("github-actions")
    if (repo / "pyproject.toml").exists():
        markers.append("python")
    if (repo / "go.mod").exists():
        markers.append("go")
    return sorted(set(markers))


def important_paths(repo: Path, limit: int) -> list[str]:
    found: list[str] = []
    for rel in IMPORTANT_FILES:
        path = repo / rel
        if path.exists():
            found.append(rel)
    for subdir in ("docs", "infra", "scripts", "src", "apps", "packages"):
        path = repo / subdir
        if path.is_dir():
            found.append(subdir + "/")
    return found[:limit]


def doc_paths(repo: Path, limit: int) -> list[str]:
    docs: list[str] = []
    for path in repo.rglob("*"):
        if len(docs) >= limit:
            break
        if any(part in SKIP_DIRS for part in path.relative_to(repo).parts):
            continue
        if path.is_file() and path.suffix.lower() in {".md", ".mdx"}:
            docs.append(str(path.relative_to(repo)))
    return docs


def repo_summary(repo: Path, *, docs_limit: int, paths_limit: int, commits_limit: int) -> str:
    branch = run_git(repo, ["branch", "--show-current"]) or "(detached/unknown)"
    head = run_git(repo, ["rev-parse", "--short", "HEAD"]) or "unknown"
    remote = run_git(repo, ["remote", "get-url", "origin"]) or "none"
    status = run_git(repo, ["status", "--short"])
    commits = run_git(repo, ["log", f"--max-count={commits_limit}", "--pretty=%h %ad %s", "--date=short"])
    stack = detect_stack(repo)
    important = important_paths(repo, paths_limit)
    docs = doc_paths(repo, docs_limit)

    parts = [
        f"# {repo.name}",
        "",
        "## Repository",
        "",
        f"- Path: `{repo}`",
        f"- Remote: `{remote}`",
        f"- Branch: `{branch}`",
        f"- HEAD: `{head}`",
        f"- Working tree: {'dirty' if status else 'clean'}",
        "",
    ]
    if stack:
        parts.extend(["## Stack Markers", "", *[f"- {item}" for item in stack], ""])
    if important:
        parts.extend(["## Important Paths", "", *[f"- `{item}`" for item in important], ""])
    if docs:
        parts.extend(["## Local Docs", "", *[f"- `{item}`" for item in docs], ""])
    if commits:
        parts.extend(["## Recent Commits", "", *[f"- {line}" for line in commits.splitlines()], ""])
    if status:
        parts.extend(["## Dirty Working Tree Snapshot", "", "```text", status[:4000], "```", ""])
    return "\n".join(parts).strip() + "\n"


def normalize_repo(repo: Path, args: argparse.Namespace) -> dict[str, Any]:
    repo = repo.expanduser().resolve()
    if not (repo / ".git").exists():
        raise ValueError(f"{repo}: not a git repository")
    remote = run_git(repo, ["remote", "get-url", "origin"]) or ""
    head = run_git(repo, ["rev-parse", "--short", "HEAD"]) or "unknown"
    branch = run_git(repo, ["branch", "--show-current"]) or "unknown"
    return {
        "external_id": args.id_prefix + repo.name,
        "title": f"{repo.name} repo map",
        "summary": repo_summary(repo, docs_limit=args.docs_limit, paths_limit=args.paths_limit, commits_limit=args.commits_limit),
        "target_path": f"{args.target_prefix.strip('/')}/{slugify(repo.name)}.md",
        "tags": ["repo", "code", "source", *detect_stack(repo)[:4]],
        "artifact_type": args.artifact_type,
        "visibility": args.visibility,
        "author": "repo-map-export.py",
        "occurred_at": None,
        "url": remote or None,
        "cursor": f"{branch}:{head}",
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
    parser = argparse.ArgumentParser(description="Export local git repo maps to normalized Company Brain JSONL.")
    parser.add_argument("--repo", action="append", required=True, help="local git repo path; repeatable")
    parser.add_argument("--id-prefix", default="")
    parser.add_argument("--target-prefix", default="brain/engineering/repos")
    parser.add_argument("--artifact-type", default="repo_map")
    parser.add_argument("--visibility", default="team")
    parser.add_argument("--docs-limit", type=int, default=30)
    parser.add_argument("--paths-limit", type=int, default=30)
    parser.add_argument("--commits-limit", type=int, default=10)
    parser.add_argument("--output-jsonl", type=Path, default=None)
    args = parser.parse_args(argv)

    try:
        records = [normalize_repo(Path(repo), args) for repo in args.repo]
        write_jsonl(records, args.output_jsonl)
    except ValueError as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        return 1

    if args.output_jsonl:
        print(json.dumps({
            "action": "exported",
            "connector": "local_git",
            "count": len(records),
            "output_jsonl": str(args.output_jsonl),
        }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
