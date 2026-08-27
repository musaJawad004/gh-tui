"""StatusBar — bottom bar: section switch (PRs / Issues), user, refresh + paging, and a
transient status message.
"""

from __future__ import annotations

from rich.text import Text
from textual.widgets import Static

import icons
from themes.palettes import GREEN


class StatusBar(Static):
    def on_mount(self) -> None:
        t = Text()
        t.append(f" {icons.PR} PRs ", style="bold")
        t.append(f"  {icons.ISSUES} Issues ", style="dim")
        t.append(f"  {icons.GIFS} gifs · @dlvhdr", style="dim")
        t.append("     ")
        t.append(f"{icons.UPDATED} Updated ~5s ago · PR 1/3 (fetched 3)", style="dim")
        t.append("     ")
        t.append(f"{icons.CI_PASS} ", style=GREEN)
        t.append('PRs for "Open Source" have loaded', style="dim")
        self.update(t)
