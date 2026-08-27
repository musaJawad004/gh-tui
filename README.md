# gh-tui

> Your entire GitHub + Git + CI/CD workflow, in one terminal UI. Built in Python.

`gh-tui` is a keyboard-driven terminal UI that unifies **local Git**, **GitHub**, and
**CI/CD** into a single interface. Instead of jumping between `git`, the `gh` CLI, the
GitHub web app, and the Actions tab, you open one tool:

```bash
gh-tui
```

It's inspired by [`gh-dash`](https://github.com/dlvhdr/gh-dash) — but where gh-dash is a
PR/issue dashboard, gh-tui aims to cover the **whole workflow**: repositories, branches,
commits, stash, pull requests, reviews, issues, Actions/CI, deployments, releases,
secrets, and repo settings.

> **Status: early preview.** The keyboard-driven workspace, focused GitHub lists,
> settings, and theme system are runnable with mock data while API integration continues.

---

## Why gh-tui vs gh-dash?

`gh-dash` is excellent — we're deliberately building the parts it doesn't cover.

| Feature                        |       `gh-dash` | gh-tui |
| ------------------------------ | --------------: | -----: |
| Browse PRs                     |               ✅ |      ✅ |
| PR diffs                       |               ✅ |      ✅ |
| Comment/review PRs             |               ✅ |      ✅ |
| PR commits                     |               ✅ |      ✅ |
| Issues                         |               ✅ |      ✅ |
| Notifications                  |               ✅ |      ✅ |
| Checkout/update PR             |               ✅ |      ✅ |
| Create new repository UI       |               ❌ |      ✅ |
| Browse/manage all repositories |               ❌ |      ✅ |
| Full local branch manager      |               ❌ |      ✅ |
| Full local commit manager      |               ❌ |      ✅ |
| Stash management               |               ❌ |      ✅ |
| GitHub Actions dashboard       | ❌ separate tool |      ✅ |
| CI failure/log explorer        |               ❌ |      ✅ |
| Retry failed CI jobs           |      ❌ natively |      ✅ |
| Workflow management            |               ❌ |      ✅ |
| Deployment management          |               ❌ |      ✅ |
| Release management             |               ❌ |      ✅ |
| Secrets / variables            |               ❌ |      ✅ |
| Repo settings                  |               ❌ |      ✅ |
| Unified search                 |         Limited |      ✅ |
| PR + CI relationship           |         Limited |      ✅ |
| CI failure diagnosis           |               ❌ |      ✅ |
| Repo health                    |               ❌ |      ✅ |

## Stack (planned)

- **TUI:** [Textual](https://textual.textualize.io/) (+ Rich) — the Python equivalent of
  Bubble Tea / Lip Gloss / Bubbles.
- **GitHub:** shell out to the `gh` CLI for MVP (free auth), migrate hot paths to
  `gh api graphql` / `ghapi` later.
- **Local Git:** `pygit2` (libgit2) for fast reads; shell out to `git` for mutating ops.
- **No-LLM analysis:** pure heuristics for PR risk, CI failure diagnosis, repo health.

See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for the full rationale.

## Requirements (planned)

- Python 3.11+
- [`gh` CLI](https://cli.github.com/) authenticated (`gh auth login`)
- A **Nerd Font** in your terminal (for the branch/PR/clock glyphs)
- `git` on PATH

## Project structure

Flat `src/` layout — jump straight into the component folders (no nested package). Docs
live at the repo root.

```
gh-tui/
├── README.md · ARCHITECTURE.md · ROADMAP.md · FEATURES.md   # docs at root
├── CONTRIBUTING.md · CHANGELOG.md · LICENSE
├── pyproject.toml · requirements.txt · requirements-dev.txt
├── tests/            # structure + smoke tests
└── src/
    ├── __main__.py   # entry — `python src/`
    ├── app.py        # main Textual App
    ├── app.tcss      # app-wide styles (layout; colors via themes)
    ├── config.py     # YAML config
    ├── core/         # gh CLI + GraphQL + local git + cache
    ├── models/       # typed dataclasses
    ├── screens/      # one screen per major view
    ├── widgets/      # reusable widgets
    ├── analysis/     # no-LLM heuristics (risk, CI diagnosis, health)
    └── themes/       # light / dark / color-scheme themes (see themes/README.md)
```

## Terminal workspace

The default screen is intentionally list-first rather than a web-style dashboard: one
compact section switcher, one data table, one selected-item context line, and one command
line. Use `1`–`5` or `tab` to change sections, `j`/`k` to move, `enter` to inspect an item,
and `o` to open the optional overview.

PR and issue composers currently save **local-only drafts**; they do not submit anything
to GitHub or store data on a server. See [`LOCAL_DRAFTS.md`](LOCAL_DRAFTS.md) for cache
location, privacy behavior, `@mention` assistance, and keyboard controls.

## Themes

There are 25 built-in light, dark, minimal, and colorful schemes. Colors are semantic
tokens resolved by the active theme, including inline status/diff colors. Pick visually in
Settings, press `ctrl+t` to cycle, pass `--theme NAME`, or run `--list-themes`.
See [`src/themes/README.md`](src/themes/README.md).

## Getting started (dev)

Set up the development environment:

```bash
gh auth login                       # authenticate GitHub
cd gh-tui
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"             # install runtime + dev deps
pytest                              # structure tests should pass
```

```bash
python src/                         # launch (runs src/__main__.py)
# or, after the editable install:
gh-tui
gh-tui --list-themes                # print all 25 schemes
```

## License

MIT
