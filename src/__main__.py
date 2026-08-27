"""Entry point so `python src/` launches gh-tui (via the CLI)."""

import sys

from cli import main

if __name__ == "__main__":
    sys.exit(main())
