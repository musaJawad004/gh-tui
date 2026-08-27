"""Braille loaders — the dotted spinner + a dotted progress bar, matching the design refs.

BrailleSpinner cycles ⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏ on a timer. DottedProgress fills a track with braille
blocks. Both are plain Static widgets so they drop anywhere.
"""

from __future__ import annotations

from rich.text import Text
from textual.widgets import Static

SPINNER_FRAMES = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"


class BrailleSpinner(Static):
    def __init__(self, label: str = "loading", speed: float = 0.08, **kw) -> None:
        super().__init__(**kw)
        self._label = label
        self._speed = speed
        self._i = 0

    def on_mount(self) -> None:
        self._draw()
        self.set_interval(self._speed, self._tick)

    def _tick(self) -> None:
        self._i = (self._i + 1) % len(SPINNER_FRAMES)
        self._draw()

    def _draw(self) -> None:
        t = Text()
        t.append(SPINNER_FRAMES[self._i], style="bold")
        if self._label:
            t.append(f"  {self._label}", style="dim")
        self.update(t)


class DottedProgress(Static):
    """A dotted/braille progress track. Set `.progress` (0.0–1.0) to update the fill."""

    FILL = "⣿"
    EMPTY = "⢀"

    def __init__(self, width: int = 40, progress: float = 0.0, **kw) -> None:
        super().__init__(**kw)
        self._width = width
        self._progress = progress

    def on_mount(self) -> None:
        self._draw()

    @property
    def progress(self) -> float:
        return self._progress

    @progress.setter
    def progress(self, value: float) -> None:
        self._progress = max(0.0, min(1.0, value))
        self._draw()

    def _draw(self) -> None:
        filled = round(self._progress * self._width)
        t = Text()
        t.append("│", style="dim")
        t.append(self.FILL * filled, style="bold")
        t.append(self.EMPTY * (self._width - filled), style="dim")
        t.append("│", style="dim")
        self.update(t)
