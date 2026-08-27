"""Reusable animated loaders for gh-flow.

The application deliberately uses explicit task feedback instead of skeleton screens:
spinners for short unknown waits, indeterminate bars for refreshes, progress bars for
known work, step loaders for boot sequences, and compact inline command loaders.
"""

from __future__ import annotations

from collections.abc import Sequence

from rich.text import Text
from textual.widgets import Static

SPINNER_SETS: dict[str, tuple[str, ...]] = {
    "dots": tuple("⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"),
    "line": ("│", "/", "─", "\\"),
    "pipe": ("╵", "╱", "╴", "╲", "╷", "╱", "╶", "╲"),
    "circle": ("◐", "◓", "◑", "◒"),
    "arrow": ("→", "↘", "↓", "↙", "←", "↖", "↑", "↗"),
    "bounce": ("● · ·", "· ● ·", "· · ●", "· ● ·"),
    "moon": ("◐", "◓", "◑", "◒"),
}

# Backwards-compatible default used by older screens and third-party imports.
SPINNER_FRAMES = "".join(SPINNER_SETS["dots"])

TASK_SPINNERS = {
    "connect": "pipe",
    "fetch": "circle",
    "sync": "dots",
    "deploy": "arrow",
    "build": "line",
    "refresh": "dots",
}


def spinner_frame(kind: str, frame: int) -> str:
    """Return an animation frame for a spinner name or task category."""
    name = TASK_SPINNERS.get(kind, kind)
    frames = SPINNER_SETS.get(name, SPINNER_SETS["dots"])
    return frames[frame % len(frames)]


def inline_loader(
    label: str,
    frame: int,
    *,
    kind: str = "dots",
    color: str = "#16D9F5",
    command: str | None = None,
) -> Text:
    """Render a compact command/task loader suitable for a single status line."""
    result = Text()
    if command:
        result.append("$ ", style="dim")
        result.append(command, style="#26F05A")
        result.append("  ")
    result.append(spinner_frame(kind, frame), style=f"bold {color}")
    result.append(f"  {label}…", style="dim")
    return result


def indeterminate_bar(frame: int, *, width: int = 34, color: str = "#16D9F5") -> Text:
    """Render a moving dotted highlight for work with no known completion value."""
    width = max(8, width)
    head = frame % (width + 8) - 4
    result = Text("[", style="dim")
    for index in range(width):
        distance = abs(index - head)
        if distance == 0:
            result.append("█", style=f"bold {color}")
        elif distance <= 2:
            result.append("▪", style=color)
        elif distance <= 4:
            result.append("·", style=color)
        else:
            result.append("·", style="dim")
    result.append("]", style="dim")
    return result


def progress_bar(
    progress: float,
    *,
    width: int = 28,
    color: str = "#16D9F5",
    show_value: bool = True,
) -> Text:
    """Render a deterministic Unicode progress bar."""
    progress = max(0.0, min(1.0, progress))
    filled = round(progress * width)
    result = Text("[", style="dim")
    result.append("█" * filled, style=color)
    result.append("░" * (width - filled), style="dim")
    result.append("]", style="dim")
    if show_value:
        result.append(f" {progress:>4.0%}", style="dim")
    return result


def step_loader(
    steps: Sequence[str],
    active: int,
    frame: int,
    *,
    color: str = "#16D9F5",
    success: str = "#26F05A",
) -> Text:
    """Render completed, active, and pending steps without skeleton placeholders."""
    result = Text()
    for index, label in enumerate(steps):
        if index < active:
            result.append("  ✓ ", style=success)
            result.append(label, style="dim")
        elif index == active:
            result.append(f"  {spinner_frame('dots', frame)} ", style=f"bold {color}")
            result.append(label)
        else:
            result.append("  ○ ", style="dim")
            result.append(label, style="dim")
        if index < len(steps) - 1:
            result.append("\n")
    return result


class TaskSpinner(Static):
    """Animated spinner with a task-aware animation style."""

    def __init__(
        self,
        label: str = "loading",
        *,
        kind: str = "dots",
        command: str | None = None,
        speed: float = 0.08,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self._label = label
        self._kind = kind
        self._command = command
        self._speed = speed
        self._frame = 0

    def on_mount(self) -> None:
        self._draw()
        self.set_interval(self._speed, self._tick)

    def _tick(self) -> None:
        self._frame += 1
        self._draw()

    def _draw(self) -> None:
        self.update(
            inline_loader(
                self._label,
                self._frame,
                kind=self._kind,
                command=self._command,
            )
        )


class BrailleSpinner(TaskSpinner):
    """Compatibility alias for the original dotted spinner."""

    def __init__(self, label: str = "loading", speed: float = 0.08, **kwargs) -> None:
        super().__init__(label, kind="dots", speed=speed, **kwargs)


class IndeterminateBar(Static):
    def __init__(self, width: int = 34, speed: float = 0.08, **kwargs) -> None:
        super().__init__(**kwargs)
        self._width = width
        self._speed = speed
        self._frame = 0

    def on_mount(self) -> None:
        self._draw()
        self.set_interval(self._speed, self._tick)

    def _tick(self) -> None:
        self._frame += 1
        self._draw()

    def _draw(self) -> None:
        self.update(indeterminate_bar(self._frame, width=self._width))


class DottedProgress(Static):
    """Deterministic progress widget retained under its original public name."""

    def __init__(self, width: int = 40, progress: float = 0.0, **kwargs) -> None:
        super().__init__(**kwargs)
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
        self.update(progress_bar(self._progress, width=self._width))
