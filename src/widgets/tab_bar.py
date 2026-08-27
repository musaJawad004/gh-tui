"""TabBar — top header: search glyph, the named tabs with counts, and the version.

Colors come from CSS (theme tokens); the active tab is bold + inherited foreground, inactive
tabs are dimmed, so it stays correct across themes.
"""

from __future__ import annotations

from rich.text import Text
from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widgets import Static

import icons


class TabBar(Horizontal):
    def __init__(self, tabs: list[tuple[str, int]], active: int = 0, version: str = "v4.16.1"):
        super().__init__()
        self._tabs = tabs
        self._active = active
        self._version = version

    def compose(self) -> ComposeResult:
        yield Static(self._render_tabs(), id="tabs")
        yield Static(self._version, id="version")

    def _render_tabs(self) -> Text:
        t = Text()
        t.append(f"{icons.SEARCH}  ", style="dim")
        for i, (label, count) in enumerate(self._tabs):
            if i > 0:
                t.append(f"  {icons.SEP}  ", style="dim")
            segment = f"{label} ({count})"
            t.append(segment, style="bold" if i == self._active else "dim")
        return t
