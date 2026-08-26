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

> ⚠️ **Status: pre-code scaffold.** This repo currently contains only the project
> structure, planning docs, and empty module stubs. No functionality is implemented yet.
> See [`docs/ROADMAP.md`](docs/ROADMAP.md).

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

## Themes

Multiple built-in themes (light + dark + schemes like dracula/nord). Colors are semantic
tokens resolved by the active theme, so `app.theme = "dracula"` restyles the whole UI
instantly. Users pick one in `config.yml`. See [`src/themes/README.md`](src/themes/README.md).

## Getting started (dev)

Not runnable yet — this is a scaffold. Setup that works today:

```bash
gh auth login                       # authenticate GitHub
cd gh-tui
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"             # install runtime + dev deps
pytest                              # structure tests should pass
```

Once implementation begins:

```bash
python src/                         # launch (runs src/__main__.py)
# or, after the editable install:
gh-tui
```

## License

MIT
