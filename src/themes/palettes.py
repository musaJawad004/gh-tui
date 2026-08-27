"""palettes — color values + Theme objects for gh-tui.

One source of truth: the *_COLORS dicts below drive both the Textual `Theme` (which powers
CSS tokens like $background, $primary, $text-muted) and the handful of semantic colors used
for inline Rich spans (repo names, diff +/-, CI dots). Switching theme restyles the
CSS-driven parts automatically; the semantic colors below are chosen to read well on both
light and dark backgrounds.

See README.md in this folder for the token model and how to add a theme.
"""

from textual.theme import Theme

# --- semantic colors (used for inline Rich spans; legible on light + dark) ---
ACCENT_BLUE = "#4C9EEB"  # PR icon, active accents, "Open" badge
REPO_PURPLE = "#8A91D6"  # repo names / usernames (link-ish)
GREEN = "#3FB950"  # additions, CI pass
RED = "#F85149"  # deletions, CI fail
YELLOW = "#D29922"  # pending / queued

GH_DARK_COLORS = {
    "bg": "#0B0E14",
    "surface": "#0F131A",
    "panel": "#0F131A",
    "fg": "#E6EDF3",
    "muted": "#8B949E",
    "primary": ACCENT_BLUE,
    "repo": REPO_PURPLE,
    "success": GREEN,
    "error": RED,
    "warning": YELLOW,
    "accent": "#A371F7",
    "border": "#1F2630",
    "row_selected": "#18233A",
    "tab_inactive": "#6E7681",
}

GH_LIGHT_COLORS = {
    "bg": "#FFFFFF",
    "surface": "#F6F8FA",
    "panel": "#F6F8FA",
    "fg": "#1F2328",
    "muted": "#59636E",
    "primary": "#0969DA",
    "repo": "#5A4FCF",
    "success": "#1A7F37",
    "error": "#CF222E",
    "warning": "#9A6700",
    "accent": "#8250DF",
    "border": "#D1D9E0",
    "row_selected": "#DBEAFE",
    "tab_inactive": "#818B98",
}


def _build(name: str, dark: bool, c: dict) -> Theme:
    return Theme(
        name=name,
        dark=dark,
        primary=c["primary"],
        secondary=c["repo"],
        accent=c["accent"],
        foreground=c["fg"],
        background=c["bg"],
        surface=c["surface"],
        panel=c["panel"],
        success=c["success"],
        warning=c["warning"],
        error=c["error"],
        variables={
            "diff-add": c["success"],
            "diff-remove": c["error"],
            "repo-name": c["repo"],
            "row-selected": c["row_selected"],
            "pr-open": c["primary"],
            "border-dim": c["border"],
            "tab-inactive": c["tab_inactive"],
        },
    )


GH_DARK = _build("gh-dark", True, GH_DARK_COLORS)
GH_LIGHT = _build("gh-light", False, GH_LIGHT_COLORS)

THEMES = [GH_DARK, GH_LIGHT]


def active_colors(app) -> dict:
    """Return the raw color dict matching the app's current theme name."""
    return GH_LIGHT_COLORS if getattr(app, "theme", "gh-dark") == "gh-light" else GH_DARK_COLORS
