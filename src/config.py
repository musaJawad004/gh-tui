"""Persistent gh-tui user settings.

Settings are stored as YAML in the platform config directory and merged with safe
defaults on every launch. A custom path can be injected for tests or portable installs.
"""

from __future__ import annotations

import os
from pathlib import Path

import yaml

DEFAULT_SETTINGS: dict = {
    "theme": "gh-flow",
    "nerd_fonts": False,
    "default_screen": "overview",
    "confirm_destructive": True,
    "auto_refresh": "30s",
    "per_page": 30,
    "default_owner": "musaJawad004",
    "base_branch": "main",
    "repository": "",
}


def settings_path() -> Path:
    """Return the configured settings file path."""
    override = os.environ.get("GH_TUI_CONFIG")
    if override:
        return Path(override).expanduser()
    base = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    return base / "gh-tui" / "config.yml"


def load_settings(path: Path | None = None) -> dict:
    """Load known settings, falling back safely for missing or invalid YAML."""
    target = path or settings_path()
    try:
        loaded = yaml.safe_load(target.read_text(encoding="utf-8")) or {}
    except (OSError, yaml.YAMLError):
        loaded = {}
    if not isinstance(loaded, dict):
        loaded = {}
    known = {key: loaded[key] for key in DEFAULT_SETTINGS if key in loaded}
    return {**DEFAULT_SETTINGS, **known}


def save_settings(settings: dict, path: Path | None = None) -> Path:
    """Atomically persist known settings and return the destination path."""
    target = path or settings_path()
    target.parent.mkdir(parents=True, exist_ok=True)
    values = {key: settings.get(key, default) for key, default in DEFAULT_SETTINGS.items()}
    temporary = target.with_suffix(".tmp")
    temporary.write_text(yaml.safe_dump(values, sort_keys=False), encoding="utf-8")
    temporary.replace(target)
    return target
