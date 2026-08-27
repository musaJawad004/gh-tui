"""PullRequest model + a couple of formatting helpers.

Minimal shape the UI needs. Real data (from `gh`) will populate these same fields later.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class PullRequest:
    repo: str  # "charmbracelet/bubbletea"
    number: int  # 1190
    title: str  # "feat(examples): tree"
    author: str  # "dlvhdr"
    base: str  # "v2-exp"
    head: str  # "dlvhdr/tree-example"
    state: str  # "open"
    reviewers_ok: bool  # a review approved
    ci: str  # "pass" | "fail" | "pending"
    additions: int
    deletions: int
    updated: str  # relative, e.g. "1h"
    created: str  # relative, e.g. "1y"
    files_changed: int
    commits: int
    summary: str | None = None


def humanize_count(n: int) -> str:
    """1200 -> '1.2k', 1000 -> '1k', 391 -> '391'."""
    if n >= 1000:
        return f"{n / 1000:.1f}k".replace(".0k", "k")
    return str(n)
