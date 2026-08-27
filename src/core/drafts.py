"""Local-only comment draft persistence.

Drafts intentionally live in the user's cache directory.  This module has no network
client and never submits a comment to GitHub; it only reads and atomically writes YAML.
"""

from __future__ import annotations

import os
from pathlib import Path

import yaml


def drafts_path() -> Path:
    """Return the local draft-cache path, honoring portable/test overrides."""
    override = os.environ.get("GH_TUI_DRAFTS")
    if override:
        return Path(override).expanduser()
    base = Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache"))
    return base / "gh-tui" / "drafts.yml"


def load_drafts(path: Path | None = None) -> dict[str, str]:
    """Load string drafts and safely ignore missing, malformed, or unknown values."""
    target = path or drafts_path()
    try:
        loaded = yaml.safe_load(target.read_text(encoding="utf-8")) or {}
    except (OSError, yaml.YAMLError):
        return {}
    if not isinstance(loaded, dict):
        return {}
    return {
        str(key): value
        for key, value in loaded.items()
        if isinstance(key, str) and isinstance(value, str)
    }


def save_drafts(drafts: dict[str, str], path: Path | None = None) -> Path:
    """Atomically save non-empty drafts to the local cache and return its path."""
    target = path or drafts_path()
    target.parent.mkdir(parents=True, exist_ok=True)
    values = {key: value for key, value in sorted(drafts.items()) if value}
    temporary = target.with_suffix(".tmp")
    temporary.write_text(yaml.safe_dump(values, sort_keys=False), encoding="utf-8")
    temporary.replace(target)
    return target
