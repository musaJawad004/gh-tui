"""ASCII-art wordmark for the splash screen (rendered with pyfiglet)."""

from __future__ import annotations

from functools import lru_cache

from pyfiglet import Figlet


@lru_cache(maxsize=8)
def render_logo(text: str = "gh-flow", font: str = "larry3d") -> str:
    """Return the multi-line ASCII banner for `text`."""
    return Figlet(font=font).renderText(text).rstrip("\n")
