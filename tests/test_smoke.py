"""Smoke test — placeholder until the app exists.

Once `src/app.py` defines the Textual `App`, un-skip this and assert it builds/pilots.
"""

import pytest


@pytest.mark.skip(reason="app not implemented yet — un-skip in v0.1")
def test_app_boots():
    # from app import GhTuiApp
    # app = GhTuiApp()
    # async with app.run_test() as pilot:
    #     assert app.is_running
    ...
