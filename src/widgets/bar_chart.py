"""BarChart — a compact activity histogram using block glyphs (contribution-graph style).

Renders `values` as vertical bars across `height` rows using ▁▂▃▄▅▆▇█, with one column
highlighted (accent color + value label above) and left/right axis labels below.
"""

from __future__ import annotations

from rich.text import Text
from textual.widgets import Static

# index 0..8 -> fill level (space + eighth blocks)
_EIGHTHS = " ▁▂▃▄▅▆▇█"


class BarChart(Static):
    def __init__(
        self,
        values: list[int],
        *,
        height: int = 6,
        highlight: int | None = None,
        left_label: str = "",
        right_label: str = "",
        accent: str = "#F0C08A",
        bar_style: str = "#3B4250",
        **kw,
    ) -> None:
        super().__init__(**kw)
        self._values = values
        self._height = height
        self._highlight = highlight
        self._left = left_label
        self._right = right_label
        self._accent = accent
        self._bar = bar_style

    def on_mount(self) -> None:
        self.update(self._render_chart())

    def _render_chart(self) -> Text:
        values = self._values
        n = len(values)
        peak = max(values) if values else 1
        rows = self._height
        # total eighths of fill per column
        eighths = [round(v / peak * rows * 8) for v in values]

        out = Text()

        # value label above the highlighted column
        if self._highlight is not None and 0 <= self._highlight < n:
            label = str(values[self._highlight])
            start = max(0, self._highlight - len(label) // 2)
            out.append(" " * start)
            out.append(label, style="bold")
            out.append("\n")

        # bars, top row first
        for row in range(rows, 0, -1):
            line = Text()
            for i in range(n):
                fill = eighths[i] - (row - 1) * 8
                ch = "█" if fill >= 8 else (_EIGHTHS[fill] if fill > 0 else " ")
                style = self._accent if i == self._highlight else self._bar
                line.append(ch, style=style)
            out.append(line)
            out.append("\n")

        # axis labels
        if self._left or self._right:
            gap = max(1, n - len(self._left) - len(self._right))
            axis = Text()
            axis.append(self._left, style="dim")
            axis.append(" " * gap)
            axis.append(self._right, style="dim")
            out.append(axis)

        return out
