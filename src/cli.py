"""Command-line entry point for gh-tui.

Handles the base CLI options (`--help`, `--version`, `--check-updates`, `--theme`,
`--screen`) and otherwise launches the TUI.
"""

from __future__ import annotations

import argparse
import sys

from version import __version__

REPO = "musaJawad004/gh-tui"
SCREENS = ["workspace", "overview", "pull-requests", "settings"]


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="gh-tui",
        description="Your entire GitHub + Git + CI/CD workflow, in one terminal UI.",
        epilog="Run with no arguments to open the terminal workspace.",
    )
    p.add_argument("-v", "--version", action="version", version=f"gh-tui {__version__}")
    p.add_argument(
        "--check-updates",
        action="store_true",
        help="check GitHub for a newer release and exit",
    )
    p.add_argument(
        "--theme",
        metavar="NAME",
        choices=None,
        help="start with a specific built-in theme (see --list-themes)",
    )
    p.add_argument(
        "--list-themes", action="store_true", help="list built-in color schemes and exit"
    )
    p.add_argument(
        "--screen",
        metavar="NAME",
        choices=SCREENS,
        help=f"open directly to a section ({', '.join(SCREENS)})",
    )
    return p


def latest_message() -> str:
    """Return a human-readable update-check result. Never raises (safe for the TUI)."""
    import json
    import urllib.error
    import urllib.request

    url = f"https://api.github.com/repos/{REPO}/releases/latest"
    req = urllib.request.Request(
        url, headers={"Accept": "application/vnd.github+json", "User-Agent": "gh-tui"}
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.load(resp)
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return f"gh-tui {__version__}: no releases published yet."
        return f"gh-tui: update check failed (HTTP {e.code})."
    except Exception as e:  # noqa: BLE001 — network/parse issues should not crash
        return f"gh-tui: could not check for updates ({e})."

    latest = str(data.get("tag_name", "")).lstrip("v")
    if not latest:
        return f"gh-tui {__version__}: no releases found."
    if latest == __version__:
        return f"gh-tui {__version__} is up to date."
    return f"Update available: {latest} (you have {__version__}). → github.com/{REPO}/releases"


def check_updates() -> int:
    print(latest_message())
    return 0


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.check_updates:
        return check_updates()

    if args.list_themes:
        from themes import THEME_NAMES

        print("\n".join(THEME_NAMES))
        return 0

    if args.theme:
        from themes import THEME_NAMES

        if args.theme not in THEME_NAMES:
            build_parser().error(f"unknown theme {args.theme!r}; use --list-themes")

    # Imported lazily so `--help`/`--version` don't pay the TUI import cost.
    from app import GhTuiApp

    GhTuiApp(theme=args.theme, start_screen=args.screen).run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
