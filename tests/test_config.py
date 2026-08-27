"""Persistent settings behavior."""

from app import GhTuiApp
from config import DEFAULT_SETTINGS, load_settings, save_settings


def test_settings_round_trip(tmp_path):
    path = tmp_path / "gh-tui" / "config.yml"
    values = {**DEFAULT_SETTINGS, "theme": "dracula", "nerd_fonts": True, "per_page": 50}

    save_settings(values, path)

    loaded = load_settings(path)
    assert loaded["theme"] == "dracula"
    assert loaded["nerd_fonts"] is True
    assert loaded["per_page"] == 50


def test_app_restores_saved_theme_and_settings(tmp_path):
    path = tmp_path / "config.yml"
    save_settings({**DEFAULT_SETTINGS, "theme": "nord", "auto_refresh": "60s"}, path)

    app = GhTuiApp(config_path=path, start_screen="workspace")

    assert app.theme == "nord"
    assert app.settings["auto_refresh"] == "60s"


def test_invalid_config_falls_back_to_defaults(tmp_path):
    path = tmp_path / "config.yml"
    path.write_text("[not: valid: yaml", encoding="utf-8")

    assert load_settings(path) == DEFAULT_SETTINGS
