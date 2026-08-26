"""Structure tests.

These are executable documentation of the project layout: they pass today (pre-code) and
guard the architecture as the codebase grows. When a folder/module is intentionally moved,
update this file in the same commit.
"""

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"

EXPECTED_PACKAGES = ["core", "models", "screens", "widgets", "analysis", "themes"]
EXPECTED_MODULES = ["app.py", "config.py", "__main__.py", "app.tcss"]
EXPECTED_DOCS = ["README.md", "ARCHITECTURE.md", "ROADMAP.md", "FEATURES.md", "LICENSE"]


@pytest.mark.parametrize("pkg", EXPECTED_PACKAGES)
def test_package_folder_exists(pkg):
    folder = SRC / pkg
    assert folder.is_dir(), f"missing src/{pkg}/"
    assert (folder / "__init__.py").is_file(), f"missing src/{pkg}/__init__.py"


@pytest.mark.parametrize("module", EXPECTED_MODULES)
def test_top_level_module_exists(module):
    assert (SRC / module).is_file(), f"missing src/{module}"


@pytest.mark.parametrize("doc", EXPECTED_DOCS)
def test_root_doc_exists(doc):
    assert (ROOT / doc).is_file(), f"missing {doc} at repo root"


def test_themes_are_set_up():
    themes = SRC / "themes"
    assert (themes / "palettes.py").is_file()
    assert (themes / "README.md").is_file()
