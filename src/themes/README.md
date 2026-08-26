# Theming

gh-tui ships **multiple themes** — light, dark, and extra color schemes — and lets users
pick one in `config.yml`. This folder defines them.

## How it works (Textual model)

A theme is **not** a separate CSS file. It's a `Theme` object: a named set of colors plus a
`dark: bool`. The whole app uses **one** stylesheet (`src/app.tcss`) written against
*semantic tokens* (`$primary`, `$surface`, `$success`, …). Switching theme re-resolves
those tokens and every widget restyles instantly:

```python
app.theme = "dracula"   # done — no CSS reload, no per-widget code
```

So: **colors live here, layout/structure lives in `src/app.tcss`.** Never hardcode a hex
value in a widget — always reference a token.

## Files

| File | Role |
|------|------|
| `__init__.py` | theme registry + `register_themes(app)` + `DEFAULT_THEME` |
| `palettes.py` | one `Theme(...)` per built-in theme (the actual colors) |
| `README.md` | this file |

## Semantic tokens

Every theme (light and dark) must define all of these so the UI stays legible in both:

| Token | Used for |
|-------|----------|
| `$background` | app background |
| `$surface` | panels / cards |
| `$panel` | secondary panels, detail pane |
| `$foreground` | primary text |
| `$text-muted` | secondary text, timestamps |
| `$primary` | accent, active tab, links (repo names) |
| `$secondary` | secondary accent |
| `$success` | CI ✓ dot, healthy status |
| `$warning` | pending / queued status |
| `$error` | CI ✗ dot, failures |
| `$row-selected` | highlighted table row |
| `$diff-add` | `+` additions |
| `$diff-remove` | `-` deletions |
| `$pr-open` / `$pr-merged` / `$pr-closed` / `$pr-draft` | PR state colors |

## Built-in themes (planned)

- **gh-dark** (default) — dark navy, GitHub-like
- **gh-light** — light variant
- **dracula**, **nord**, **gruvbox-dark**, **solarized-light** — popular schemes

## Add a theme

1. Add a `Theme(...)` in `palettes.py` defining every token above.
2. Append it to `THEMES` in `__init__.py`.
3. Users select it with `theme: <name>` in `config.yml`.

That's it — no CSS changes needed.
