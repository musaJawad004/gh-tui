# Local drafts and privacy

PR review comments and issue replies in the current preview are **local drafts only**.
Typing, selecting an `@mention`, and pressing `Ctrl+S` never call GitHub, an API, a
database, or any other server. There is intentionally no submit command yet.

## Controls

- Press `e` or click the editor to start editing.
- Press `Esc` to leave the editor and return keyboard control to the workspace.
- Press `Ctrl+S` to save immediately to the local cache.
- Press `Ctrl+M` to cycle through local `@mention` suggestions.
- Drafts are also saved automatically while typing and before changing items or tabs.

Each draft is keyed by repository, item type, and GitHub number (for example,
`pr:musa/my-app:#142`). This keeps drafts separate even if the list is reordered.

## Storage

The default cache file is:

```text
~/.cache/gh-tui/drafts.yml
```

When `XDG_CACHE_HOME` is set, the file lives at
`$XDG_CACHE_HOME/gh-tui/drafts.yml`. Set `GH_TUI_DRAFTS` to use an explicit path.
Remove that file to clear all local drafts.

The file contains plain-text YAML on your machine. It is written atomically and is never
uploaded by gh-tui. Treat it like any local note if a draft contains sensitive text.
