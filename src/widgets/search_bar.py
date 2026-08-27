"""SearchBar — the rounded query box (e.g. `is:pr is:open author:@me owner:charmbracelet`).

Display-only for now; becomes an editable Input when we wire real search.
"""

from __future__ import annotations

from rich.text import Text
from textual.widgets import Static

import icons


class SearchBar(Static):
    def __init__(self, query: str):
        super().__init__()
        self._query = query

    def on_mount(self) -> None:
        t = Text()
        t.append(f"{icons.SEARCH}  ", style="dim")
        t.append(self._query)
        self.update(t)
