"""palettes — semantic colors + the built-in Theme objects for gh-tui.

Each theme drives Textual's CSS tokens ($background, $primary, $text-muted, $border-dim,
$row-selected, ...). Switching theme restyles the whole UI instantly. THEME_SPECS below is
a compact table; THEMES/THEME_NAMES are built from it.
"""

from textual.theme import Theme

# --- fallback colors for renderables created before an App is mounted -----------------
ACCENT_BLUE = "#5B7FFF"
REPO_PURPLE = "#A78BFA"
GREEN = "#35D07F"
RED = "#FF5C5C"
YELLOW = "#F5A623"
CYAN = "#22D3EE"


def _spec(
    name: str,
    background: str,
    surface: str,
    border: str,
    foreground: str,
    muted: str,
    primary: str,
    secondary: str,
    success: str,
    warning: str,
    error: str,
) -> tuple:
    """Build the internal spec while keeping the user-facing palette table readable."""
    # All supplied palettes are terminal dark themes. Secondary is also used for repo
    # names and chart accents; surface is a subtle, readable selected-row background.
    return (
        name,
        True,
        background,
        surface,
        foreground,
        muted,
        primary,
        secondary,
        success,
        warning,
        error,
        secondary,
        border,
        surface,
    )


# name, background, surface, border, text, muted, primary, secondary, success, warning, error
THEME_SPECS = [
    _spec(
        "gh-flow",
        "#050706",
        "#090C0A",
        "#36413B",
        "#D5DBD7",
        "#7E8882",
        "#3DDC84",
        "#2FC7E8",
        "#43E06F",
        "#F5D547",
        "#FF4D4D",
    ),
    _spec(
        "linear",
        "#0F1015",
        "#17181F",
        "#2A2C36",
        "#F2F2F3",
        "#8A8C98",
        "#5E6AD2",
        "#8A92FF",
        "#4CB782",
        "#D9A441",
        "#E5484D",
    ),
    _spec(
        "codex",
        "#0A0A0A",
        "#111111",
        "#2A2A2A",
        "#F3F3F3",
        "#858585",
        "#10A37F",
        "#66D9C5",
        "#38C793",
        "#F2C94C",
        "#EF5B5B",
    ),
    _spec(
        "claude",
        "#14120F",
        "#1C1915",
        "#3B352E",
        "#F2EDE5",
        "#9A9186",
        "#D97757",
        "#E3A07C",
        "#8FB573",
        "#D9AE5F",
        "#D85C5C",
    ),
    _spec(
        "notion",
        "#191919",
        "#202020",
        "#373737",
        "#F1F1EF",
        "#9B9B99",
        "#FFFFFF",
        "#B4B4B0",
        "#4DAB9A",
        "#C89B3C",
        "#E16259",
    ),
    _spec(
        "apple",
        "#000000",
        "#1C1C1E",
        "#38383A",
        "#F5F5F7",
        "#8E8E93",
        "#0A84FF",
        "#64D2FF",
        "#30D158",
        "#FFD60A",
        "#FF453A",
    ),
    _spec(
        "github-dark",
        "#0D1117",
        "#161B22",
        "#30363D",
        "#C9D1D9",
        "#8B949E",
        "#58A6FF",
        "#A371F7",
        "#3FB950",
        "#D29922",
        "#F85149",
    ),
    _spec(
        "tokyo-night",
        "#1A1B26",
        "#24283B",
        "#414868",
        "#C0CAF5",
        "#565F89",
        "#7AA2F7",
        "#BB9AF7",
        "#9ECE6A",
        "#E0AF68",
        "#F7768E",
    ),
    _spec(
        "catppuccin-mocha",
        "#1E1E2E",
        "#181825",
        "#45475A",
        "#CDD6F4",
        "#7F849C",
        "#89B4FA",
        "#CBA6F7",
        "#A6E3A1",
        "#F9E2AF",
        "#F38BA8",
    ),
    _spec(
        "gruvbox-dark",
        "#282828",
        "#1D2021",
        "#504945",
        "#EBDBB2",
        "#928374",
        "#83A598",
        "#D3869B",
        "#B8BB26",
        "#FABD2F",
        "#FB4934",
    ),
    _spec(
        "dracula",
        "#282A36",
        "#21222C",
        "#44475A",
        "#F8F8F2",
        "#6272A4",
        "#8BE9FD",
        "#BD93F9",
        "#50FA7B",
        "#F1FA8C",
        "#FF5555",
    ),
    _spec(
        "nord",
        "#2E3440",
        "#3B4252",
        "#4C566A",
        "#ECEFF4",
        "#7B88A1",
        "#88C0D0",
        "#B48EAD",
        "#A3BE8C",
        "#EBCB8B",
        "#BF616A",
    ),
    _spec(
        "one-dark",
        "#282C34",
        "#21252B",
        "#3E4451",
        "#ABB2BF",
        "#5C6370",
        "#61AFEF",
        "#C678DD",
        "#98C379",
        "#E5C07B",
        "#E06C75",
    ),
    _spec(
        "solarized-dark",
        "#002B36",
        "#073642",
        "#586E75",
        "#839496",
        "#657B83",
        "#268BD2",
        "#6C71C4",
        "#859900",
        "#B58900",
        "#DC322F",
    ),
    _spec(
        "monokai",
        "#272822",
        "#1E1F1C",
        "#49483E",
        "#F8F8F2",
        "#75715E",
        "#66D9EF",
        "#AE81FF",
        "#A6E22E",
        "#E6DB74",
        "#F92672",
    ),
    _spec(
        "ayu-dark",
        "#0A0E14",
        "#0F1419",
        "#263238",
        "#B3B1AD",
        "#626A73",
        "#59C2FF",
        "#D2A6FF",
        "#AAD94C",
        "#FFB454",
        "#F07178",
    ),
    _spec(
        "rose-pine",
        "#191724",
        "#1F1D2E",
        "#403D52",
        "#E0DEF4",
        "#6E6A86",
        "#31748F",
        "#C4A7E7",
        "#9CCFD8",
        "#F6C177",
        "#EB6F92",
    ),
    _spec(
        "kanagawa",
        "#1F1F28",
        "#16161D",
        "#54546D",
        "#DCD7BA",
        "#727169",
        "#7E9CD8",
        "#957FB8",
        "#98BB6C",
        "#E6C384",
        "#E46876",
    ),
    _spec(
        "matrix",
        "#010603",
        "#06100A",
        "#173B24",
        "#B5F5C8",
        "#4D7B59",
        "#00FF66",
        "#67FF9A",
        "#00FF66",
        "#D7FF00",
        "#FF4242",
    ),
    _spec(
        "mono",
        "#070707",
        "#111111",
        "#343434",
        "#E6E6E6",
        "#777777",
        "#FFFFFF",
        "#BEBEBE",
        "#D9D9D9",
        "#AFAFAF",
        "#FFFFFF",
    ),
]


def _build(spec) -> Theme:
    (
        name,
        dark,
        bg,
        surface,
        fg,
        muted,
        primary,
        repo,
        success,
        warning,
        error,
        accent,
        border,
        sel,
    ) = spec
    return Theme(
        name=name,
        dark=dark,
        primary=primary,
        secondary=repo,
        accent=accent,
        foreground=fg,
        background=bg,
        surface=surface,
        panel=surface,
        success=success,
        warning=warning,
        error=error,
        variables={
            "text-muted": muted,
            "diff-add": success,
            "diff-remove": error,
            "repo-name": repo,
            "row-selected": sel,
            "pr-open": primary,
            "border-dim": border,
            "tab-inactive": muted,
        },
    )


THEMES = [_build(s) for s in THEME_SPECS]
THEME_NAMES = [s[0] for s in THEME_SPECS]
_BY_NAME = {t.name: t for t in THEMES}
GH_FLOW = _BY_NAME["gh-flow"]
GH_DARK = _BY_NAME["github-dark"]
GH_LIGHT = _BY_NAME["notion"]


def palette_colors(name: str) -> dict[str, str]:
    """Return one theme's semantic colors for Rich ``Text`` spans."""
    theme = _BY_NAME.get(name, GH_FLOW)
    return {
        "background": theme.background,
        "foreground": theme.foreground,
        "muted": theme.variables["text-muted"],
        "primary": theme.primary,
        "secondary": theme.secondary,
        "success": theme.success,
        "warning": theme.warning,
        "error": theme.error,
        "accent": theme.accent,
        "border": theme.variables["border-dim"],
        "row_selected": theme.variables["row-selected"],
    }


def theme_is_dark(name: str) -> bool:
    """Return whether ``name`` is a dark theme."""
    return _BY_NAME.get(name, GH_FLOW).dark


def active_colors(app) -> dict[str, str]:
    """Return the active theme's semantic colors for Rich ``Text`` spans.

    Textual resolves ``$primary``-style tokens in CSS, but Rich renderables need actual
    color values. Keeping this adapter here prevents light themes from inheriting the
    default dark palette's inline colors.
    """
    return palette_colors(getattr(app, "theme", ""))
