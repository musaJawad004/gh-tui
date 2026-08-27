"""themes — the gh-tui theme registry.

Themes are Textual `Theme` objects (a named color set + `dark` flag). The app's single
stylesheet references semantic tokens ($primary, $surface, $success, ...); setting
`app.theme = "<name>"` re-resolves them and restyles the whole UI instantly.

Public API:
    THEMES              # all built-in themes
    DEFAULT_THEME       # applied on first launch
    register_themes(app)

See README.md for the token table and how to add a theme.
"""

from .palettes import GH_DARK, GH_FLOW, GH_LIGHT, THEME_NAMES, THEMES

DEFAULT_THEME = "gh-flow"

__all__ = [
    "DEFAULT_THEME",
    "GH_DARK",
    "GH_FLOW",
    "GH_LIGHT",
    "THEMES",
    "THEME_NAMES",
    "register_themes",
]


def register_themes(app) -> None:
    """Register every built-in theme on the Textual app."""
    for theme in THEMES:
        app.register_theme(theme)
