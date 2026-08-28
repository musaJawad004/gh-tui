"""Read-only GitHub data loading through the authenticated ``gh`` CLI.

Every operation in this module is a query. It never calls a mutating GitHub command and
never writes repository data to disk; the UI keeps the returned snapshot in memory.
"""

from __future__ import annotations

import json
import re
import subprocess
import time
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
        message = detail[-1] if detail else "gh query failed"
        full_error = " ".join(detail).lower()
        if "token" in full_error and ("invalid" in full_error or "expired" in full_error):
            message = "gh token is invalid or expired; run gh auth login -h github.com"
        if "rate limit" in message.lower() or "api rate" in message.lower():
            message = "GitHub API rate limit exceeded; authenticate with gh or wait for reset"
        raise GhCliError(message)
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


def _normalize_pull_request(item: dict[str, Any]) -> dict[str, Any]:
    """Normalize REST pull-request JSON to the fields used by the UI."""
    result = dict(item)
    result.setdefault("headRefName", (item.get("head") or {}).get("ref", "—"))
    result.setdefault("baseRefName", (item.get("base") or {}).get("ref", "—"))
    result.setdefault("author", {"login": (item.get("user") or {}).get("login", "unknown")})
    result.setdefault("updatedAt", item.get("updated_at"))
    result.setdefault("createdAt", item.get("created_at"))
    result.setdefault("changedFiles", item.get("changed_files", 0))
    result.setdefault("reviewDecision", "")
    result.setdefault("statusCheckRollup", [])
    return result


def _normalize_issue(item: dict[str, Any]) -> dict[str, Any]:
    result = dict(item)
    result.setdefault("updatedAt", item.get("updated_at"))
    result.setdefault("createdAt", item.get("created_at"))
    result.setdefault("author", {"login": (item.get("user") or {}).get("login", "unknown")})
    return result


def _normalize_workflow(item: dict[str, Any]) -> dict[str, Any]:
    result = dict(item)
    result.setdefault("workflowName", item.get("name", "workflow"))
    result.setdefault("headBranch", item.get("head_branch", "—"))
    result.setdefault("createdAt", item.get("created_at"))
    result.setdefault("updatedAt", item.get("updated_at"))
    return result


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
    events: list[dict[str, Any]] = field(default_factory=list)

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
        """Normalize GitHub events into a truthful, bounded recent-activity feed."""
        rows: list[tuple] = []
        cutoff = datetime.now(UTC).timestamp() - 48 * 3600
        for item in self.events:
            stamp = item.get("created_at") or item.get("createdAt")
            try:
                if stamp and datetime.fromisoformat(stamp).timestamp() < cutoff:
                    continue
            except ValueError:
                continue
            event_type = item.get("type", "")
            payload = item.get("payload") or {}
            repo = (item.get("repo") or {}).get("name", "")
            ref = repo.rsplit("/", 1)[-1] if repo else "—"
            if event_type == "PushEvent":
                count = len(payload.get("commits") or [])
                rows.append(("✓", "success", relative_time(stamp), f"{count or 1} commit{'s' if count != 1 else ''} pushed", ref, "commit"))
            elif event_type == "PullRequestEvent":
                pr = payload.get("pull_request") or {}
                action = payload.get("action", "updated")
                rows.append(("✓", "success", relative_time(stamp), f"pull request {action}: {pr.get('title', 'untitled')}", f"#{pr.get('number', '?')}", "pull request"))
            elif event_type == "IssuesEvent":
                issue = payload.get("issue") or {}
                action = payload.get("action", "updated")
                rows.append(("!", "warning", relative_time(stamp), f"issue {action}: {issue.get('title', 'untitled')}", f"#{issue.get('number', '?')}", "issue"))
            elif event_type in {"WorkflowRunEvent", "WorkflowDispatchEvent"}:
                action = payload.get("action", "updated")
                rows.append(("○", "warning", relative_time(stamp), f"workflow {action}", ref, "workflow"))
            elif event_type == "DeploymentEvent":
                rows.append(("→", "success", relative_time(stamp), "deployment created", ref, "deploy"))
        return rows


_snapshot_cache: dict[str, tuple[float, GitHubSnapshot]] = {}


def clear_snapshot_cache(repository: str | None = None) -> None:
    """Clear the process-local snapshot cache (no GitHub mutation)."""
    if repository is None:
        _snapshot_cache.clear()
    else:
        _snapshot_cache.pop(parse_repository_url(repository) or repository, None)


def load_pull_request_detail(repository: str, number: int, *, cwd: Path | None = None) -> dict[str, Any]:
    """Load one PR and its review surface lazily (all GET requests)."""
    repo = parse_repository_url(repository)
    if not repo:
        raise GhCliError("repository must be a GitHub URL or owner/name")
    detail = _run_json(["api", f"repos/{repo}/pulls/{number}"], cwd=cwd)
    detail["comments_data"] = _safe_query(["api", f"repos/{repo}/issues/{number}/comments?per_page=100"], cwd=cwd, default=[])
    detail["reviews_data"] = _safe_query(["api", f"repos/{repo}/pulls/{number}/reviews?per_page=100"], cwd=cwd, default=[])
    detail["files_data"] = _safe_query(["api", f"repos/{repo}/pulls/{number}/files?per_page=100"], cwd=cwd, default=[])
    return detail


def load_issue_detail(repository: str, number: int, *, cwd: Path | None = None) -> dict[str, Any]:
    """Load one issue and its conversation lazily (all GET requests)."""
    repo = parse_repository_url(repository)
    if not repo:
        raise GhCliError("repository must be a GitHub URL or owner/name")
    detail = _run_json(["api", f"repos/{repo}/issues/{number}"], cwd=cwd)
    detail["comments_data"] = _safe_query(["api", f"repos/{repo}/issues/{number}/comments?per_page=100"], cwd=cwd, default=[])
    return detail


def load_workflow_detail(repository: str, run_id: int, *, cwd: Path | None = None) -> dict[str, Any]:
    """Load one Actions run and its jobs lazily."""
    repo = parse_repository_url(repository)
    if not repo:
        raise GhCliError("repository must be a GitHub URL or owner/name")
    detail = _run_json(["api", f"repos/{repo}/actions/runs/{run_id}"], cwd=cwd)
    detail["jobs_data"] = _safe_query(["api", f"repos/{repo}/actions/runs/{run_id}/jobs?per_page=100"], cwd=cwd, default={"jobs": []}).get("jobs", [])
    return detail


def load_commit_detail(repository: str, sha: str, *, cwd: Path | None = None) -> dict[str, Any]:
    """Load one commit, including its complete changed-file list."""
    repo = parse_repository_url(repository)
    if not repo:
        raise GhCliError("repository must be a GitHub URL or owner/name")
    return _run_json(["api", f"repos/{repo}/commits/{sha}"], cwd=cwd)


def load_snapshot(repository: str, *, cwd: Path | None = None, limit: int = 30, force: bool = False, ttl: float = 1800) -> GitHubSnapshot:
    """Fetch all read-only dashboard resources for one repository."""
    repo = parse_repository_url(repository)
    if not repo:
        raise GhCliError("repository must be a GitHub URL or owner/name")
    cached = _snapshot_cache.get(repo)
    if cached and not force and time.monotonic() - cached[0] < ttl:
        return cached[1]
    repository_data = _run_json(["api", f"repos/{repo}"], cwd=cwd)
    repository_data = {
        **repository_data,
        "nameWithOwner": repository_data.get("full_name", repo),
        "url": repository_data.get("html_url"),
        "defaultBranchRef": {"name": repository_data.get("default_branch", "main")},
        "stargazerCount": repository_data.get("stargazers_count", 0),
    }
    snapshot = GitHubSnapshot(repository=repository_data or {})
    snapshot.pull_requests = [_normalize_pull_request(item) for item in _safe_query(["api", f"repos/{repo}/pulls?state=open&per_page={min(limit, 100)}"], cwd=cwd, default=[])]
    snapshot.issues = [_normalize_issue(item) for item in _safe_query(["api", f"repos/{repo}/issues?state=open&per_page={min(limit, 100)}"], cwd=cwd, default=[]) if "pull_request" not in item]
    workflow_data = _safe_query(["api", f"repos/{repo}/actions/runs?per_page={min(limit, 100)}"], cwd=cwd, default={"workflow_runs": []})
    snapshot.workflows = [_normalize_workflow(item) for item in workflow_data.get("workflow_runs", [])]
    snapshot.deployments = _safe_query(["api", f"repos/{repo}/deployments?per_page={min(limit, 30)}"], cwd=cwd, default=[])
    snapshot.branches = _safe_query(["api", f"repos/{repo}/branches?per_page={min(limit, 30)}"], cwd=cwd, default=[])
    snapshot.commits = _safe_query(["api", f"repos/{repo}/commits?per_page={min(limit, 30)}"], cwd=cwd, default=[])
    snapshot.releases = _safe_query(["api", f"repos/{repo}/releases?per_page={min(limit, 100)}"], cwd=cwd, default=[])
    snapshot.events = _safe_query(["api", f"repos/{repo}/events?per_page=100"], cwd=cwd, default=[])
    # Repo Manager is intentionally scoped to the configured repository; avoid an
    # unnecessary owner-wide listing (and its extra rate-limit cost).
    snapshot.repositories = []
    _snapshot_cache[repo] = (time.monotonic(), snapshot)
    return snapshot
