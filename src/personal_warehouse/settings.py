"""User settings stored in settings.json (language, theme, update preferences)."""
import json

from personal_warehouse import config


def load_settings():
    try:
        return json.loads(config.SETTINGS_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}


def save_settings(**values):
    """Merge ``values`` into the saved settings; keys that are not mentioned are kept."""
    try:
        data = load_settings()
        data.update(values)
        config.SETTINGS_PATH.write_text(json.dumps(data), encoding="utf-8")
    except Exception:
        pass
