"""Read-only GitHub data loading through the authenticated ``gh`` CLI.

Every operation in this module is a query. It never calls a mutating GitHub command and
never writes repository data to disk; the UI keeps the returned snapshot in memory.
"""

from __future__ import annotations

import json
import re
import subprocess
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


class GhCliError(RuntimeError):
    """A read-only ``gh`` query failed."""


def parse_repository_url(value: str) -> str | None:
    """Normalize common GitHub URLs or ``owner/name`` values to ``owner/name``."""
    value = value.strip().rstrip("/")
    value = re.sub(r"^git@github\.com:", "https://github.com/", value)
    match = re.search(r"github\.com[/:]([^/]+)/([^/#]+?)(?:\.git)?$", value)
    if match:
        return f"{match.group(1)}/{match.group(2)}"
    if re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", value):
        return value
    return None


def detect_local_repository(cwd: Path | None = None) -> str | None:
    """Read the local origin URL without contacting GitHub."""
    try:
        result = subprocess.run(
            ["git", "config", "--get", "remote.origin.url"],
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=3,
            check=False,
        )
    except OSError:
        return None
    return parse_repository_url(result.stdout) if result.returncode == 0 else None


def _run_json(args: list[str], *, cwd: Path | None = None) -> Any:
    try:
        result = subprocess.run(
            ["gh", *args],
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=20,
            check=False,
        )
    except OSError as exc:
        raise GhCliError(f"gh CLI is unavailable: {exc}") from exc
    if result.returncode:
        detail = (result.stderr or result.stdout).strip().splitlines()
        raise GhCliError(detail[-1] if detail else "gh query failed")
    try:
        return json.loads(result.stdout or "null")
    except json.JSONDecodeError as exc:
        raise GhCliError("gh returned invalid JSON") from exc


def _safe_query(args: list[str], *, cwd: Path | None = None, default: Any) -> Any:
    try:
        return _run_json(args, cwd=cwd)
    except GhCliError:
        return default


def relative_time(value: str | None) -> str:
    if not value:
        return "—"
    try:
        parsed = datetime.fromisoformat(value)
        delta = datetime.now(UTC) - parsed.astimezone(UTC)
    except ValueError:
        return "—"
    seconds = max(0, int(delta.total_seconds()))
    if seconds < 60:
        return "now"
    if seconds < 3600:
        return f"{seconds // 60}m"
    if seconds < 86400:
        return f"{seconds // 3600}h"
    return f"{seconds // 86400}d"


def _author(item: dict) -> str:
    author = item.get("author") or {}
    return author.get("login") or author.get("name") or "unknown"


@dataclass
class GitHubSnapshot:
    repository: dict[str, Any] = field(default_factory=dict)
    pull_requests: list[dict[str, Any]] = field(default_factory=list)
    issues: list[dict[str, Any]] = field(default_factory=list)
    workflows: list[dict[str, Any]] = field(default_factory=list)
    deployments: list[dict[str, Any]] = field(default_factory=list)
    branches: list[dict[str, Any]] = field(default_factory=list)
    commits: list[dict[str, Any]] = field(default_factory=list)
    releases: list[dict[str, Any]] = field(default_factory=list)
    repositories: list[dict[str, Any]] = field(default_factory=list)

    @property
    def name(self) -> str:
        return self.repository.get("nameWithOwner") or self.repository.get("name") or "unknown/repository"

    def pr_rows(self) -> list[tuple]:
        rows = []
        for item in self.pull_requests:
            checks = item.get("statusCheckRollup") or []
            failed = any((check.get("conclusion") or "").lower() == "failure" for check in checks)
            ci = "×" if failed else "✓"
            decision = item.get("reviewDecision") or ""
            approved = "✓" if decision == "APPROVED" else "·"
            changes = f"+{item.get('additions', 0)}  -{item.get('deletions', 0)}"
            rows.append((
                f"#{item.get('number', '?')}", item.get("title", "Untitled"),
                item.get("headRefName", "—"), ci, f"{approved} {len(checks)}", changes,
                relative_time(item.get("updatedAt")),
            ))
        return rows

    def issue_rows(self) -> list[tuple]:
        return [(
            f"#{item.get('number', '?')}", item.get("title", "Untitled"),
            " · ".join(label.get("name", "") for label in item.get("labels", [])) or "unlabeled",
            str(item.get("comments") or 0), relative_time(item.get("updatedAt")),
        ) for item in self.issues]

    def workflow_rows(self) -> list[tuple]:
        rows = []
        for item in self.workflows:
            conclusion = (item.get("conclusion") or item.get("status") or "queued").lower()
            state = "passed" if conclusion == "success" else "failed" if conclusion in {"failure", "cancelled"} else "running"
            icon = "✓" if state == "passed" else "×" if state == "failed" else "○"
            rows.append((icon, item.get("name") or item.get("workflowName") or "workflow", item.get("headBranch", "—"), state, "—", relative_time(item.get("updatedAt") or item.get("createdAt"))))
        return rows

    def deployment_rows(self) -> list[tuple]:
        return [(
            "●" if index == 0 else "○", "success", item.get("environment") or "preview",
            item.get("ref") or "—", relative_time(item.get("created_at")), "—",
        ) for index, item in enumerate(self.deployments)]

    def repo_rows(self) -> list[tuple]:
        return [(
            item.get("nameWithOwner") or item.get("name", "repository"),
            item.get("primaryLanguage", {}).get("name") if isinstance(item.get("primaryLanguage"), dict) else item.get("language", "—"),
            "private" if item.get("isPrivate") else "public", str(item.get("stargazerCount", 0)), relative_time(item.get("updatedAt")),
        ) for item in self.repositories]

    def commit_rows(self) -> list[dict[str, Any]]:
        return self.commits

    def activity_rows(self) -> list[tuple]:
        """Normalize fetched resources into the overview activity table shape."""
        rows: list[tuple] = []
        for item in self.workflows[:2]:
            conclusion = (item.get("conclusion") or item.get("status") or "queued").lower()
            rows.append((
                "✓" if conclusion == "success" else "×" if conclusion in {"failure", "cancelled"} else "○",
                "success" if conclusion == "success" else "error" if conclusion in {"failure", "cancelled"} else "warning",
                relative_time(item.get("updatedAt") or item.get("createdAt")),
                f"{item.get('name') or item.get('workflowName') or 'workflow'} workflow {conclusion}",
                str(item.get("databaseId", "run")), "workflow",
            ))
        for item in self.pull_requests[:3]:
            number = item.get("number", "?")
            rows.append(("✓", "success", relative_time(item.get("updatedAt")), item.get("title", "pull request"), f"#{number}", "pull request"))
        for item in self.issues[:2]:
            rows.append(("!", "warning", relative_time(item.get("updatedAt")), item.get("title", "issue"), f"#{item.get('number', '?')}", "issue"))
        return rows


def load_snapshot(repository: str, *, cwd: Path | None = None, limit: int = 30) -> GitHubSnapshot:
    """Fetch all read-only dashboard resources for one repository."""
    repo = parse_repository_url(repository)
    if not repo:
        raise GhCliError("repository must be a GitHub URL or owner/name")
    repository_data = _run_json(["repo", "view", repo, "--json", "nameWithOwner,url,defaultBranchRef,visibility,description,stargazerCount"], cwd=cwd)
    snapshot = GitHubSnapshot(repository=repository_data or {})
    snapshot.pull_requests = _safe_query(["pr", "list", "--repo", repo, "--state", "open", "--limit", str(limit), "--json", "number,title,headRefName,baseRefName,author,updatedAt,createdAt,additions,deletions,changedFiles,commits,reviewDecision,statusCheckRollup"], cwd=cwd, default=[])
    snapshot.issues = _safe_query(["issue", "list", "--repo", repo, "--state", "open", "--limit", str(limit), "--json", "number,title,labels,comments,updatedAt,author"], cwd=cwd, default=[])
    snapshot.workflows = _safe_query(["run", "list", "--repo", repo, "--limit", str(limit), "--json", "databaseId,name,workflowName,headBranch,status,conclusion,createdAt,updatedAt"], cwd=cwd, default=[])
    snapshot.deployments = _safe_query(["api", f"repos/{repo}/deployments?per_page={min(limit, 30)}"], cwd=cwd, default=[])
    snapshot.branches = _safe_query(["api", f"repos/{repo}/branches?per_page={min(limit, 30)}"], cwd=cwd, default=[])
    snapshot.commits = _safe_query(["api", f"repos/{repo}/commits?per_page={min(limit, 30)}"], cwd=cwd, default=[])
    snapshot.releases = _safe_query(["release", "list", "--repo", repo, "--limit", str(limit), "--json", "tagName,name,isLatest,publishedAt"], cwd=cwd, default=[])
    owner = repo.split("/", 1)[0]
    snapshot.repositories = _safe_query(["repo", "list", owner, "--limit", str(limit), "--json", "nameWithOwner,name,isPrivate,primaryLanguage,stargazerCount,updatedAt"], cwd=cwd, default=[])
    return snapshot
