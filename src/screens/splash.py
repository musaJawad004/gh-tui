"""SplashScreen — CLI-style boot screen.

Shows the big ASCII wordmark, then ticks through a boot sequence with the braille loader
before handing off to the terminal workspace. Any key (or the sequence finishing) continues.
"""

from __future__ import annotations

from rich.text import Text
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import Static

from themes.palettes import GREEN
from version import __version__
from widgets.logo import render_logo
from widgets.spinner import SPINNER_FRAMES

STEPS = [
    "Connecting to GitHub",
    "Loading repositories",
    "Fetching pull requests",
    "Reading CI / Actions status",
    "Scanning local git",
    "Opening workspace",
]


class SplashScreen(Screen):
    DEFAULT_CSS = """
    SplashScreen { align: center middle; background: $background; }
    SplashScreen #box { width: auto; height: auto; }
    SplashScreen #logo { color: $primary; width: auto; }
    SplashScreen #tagline { width: 100%; content-align: center middle; margin-top: 1; color: $text-muted; }
    SplashScreen #steps { width: 100%; margin-top: 2; }
    SplashScreen #hint { width: 100%; content-align: center middle; margin-top: 1; color: $text-muted; }
    """

    BINDINGS = [
        ("escape", "skip", "Skip"),
        ("enter", "skip", "Skip"),
        ("space", "skip", "Skip"),
    ]

    def compose(self) -> ComposeResult:
        with Vertical(id="box"):
            yield Static(id="logo")
            yield Static(id="tagline")
            yield Static(id="steps")
            yield Static(Text("press any key to skip", style="dim"), id="hint")

    def on_mount(self) -> None:
        self.query_one("#logo", Static).update(Text(render_logo(), no_wrap=True))
        self.query_one("#tagline", Static).update(
            Text(f"Your entire GitHub workflow, without leaving the terminal.   v{__version__}")
        )
        self._step = 0
        self._frame = 0
        self._done = False
        self._render_steps()
        self._timer = self.set_interval(0.08, self._tick)

    def _tick(self) -> None:
        self._frame += 1
        if self._frame % 4 == 0:
            self._step += 1
        if self._step >= len(STEPS):
            self._finish()
            return
        self._render_steps()

    def _render_steps(self) -> None:
        frame = SPINNER_FRAMES[self._frame % len(SPINNER_FRAMES)]
        t = Text()
        for i, label in enumerate(STEPS):
            if i < self._step:
                t.append("  ✓ ", style=GREEN)
                t.append(f"{label}\n", style="dim")
            elif i == self._step:
                t.append(f"  {frame} ", style="bold")
                t.append(f"{label}…\n")
            else:
                t.append(f"    {label}\n", style="dim")
        self.query_one("#steps", Static).update(t)

    def _finish(self) -> None:
        if self._done:
            return
        self._done = True
        self._timer.stop()
        from screens.main import MainScreen

        self.app.switch_screen(MainScreen())

    def action_skip(self) -> None:
        self._finish()
