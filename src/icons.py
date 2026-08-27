"""icons — single source of truth for the glyphs used across the UI.

Uses broadly-supported Unicode (text-presentation) symbols so gh-tui renders without a Nerd
Font installed. When we want the exact gh-dash look, swap these constants for Nerd Font
glyphs — nothing else needs to change.
"""

# top bar / search
SEARCH = "⌕"
SEP = "│"

# pr table
PR = "⇄"  # PR row icon
PR_HEADER = "⎇"  # first column header
REVIEWERS = "✦"  # reviewers column header
CHECKS = "◉"  # CI column header
DIFF = "±"  # diff column header
UPDATED = "◷"  # updated column header
CREATED = "✧"  # created column header
CI_PASS = "✓"
CI_FAIL = "✗"
CI_PENDING = "●"
APPROVED = "✓"

# detail pane
OVERVIEW = "▦"
CHECKS_TAB = "✔"
ACTIVITY = "◈"
SUMMARY = "≡"
CHANGES = "⊞"
FILES = "▤"
COMMITS = "⎇"
ARROW = "←"

# status bar
ISSUES = "◉"
GIFS = "▭"

# status set (design ref: Success / Error / Warning / Info)
SUCCESS = "✓"
ERROR = "✖"
WARNING = "▲"
INFO = "ⓘ"
