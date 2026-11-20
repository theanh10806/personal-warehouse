"""User settings stored in settings.json (language, theme, update preferences)."""
import json
import os
import tempfile
import threading

from personal_warehouse import config

_lock = threading.RLock()


def atomic_write(path, content):
    descriptor, temporary = tempfile.mkstemp(dir=path.parent, prefix=path.name + ".")
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        from pathlib import Path
        Path(temporary).unlink(missing_ok=True)


def load_settings():
    try:
        return json.loads(config.SETTINGS_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}


def save_settings(**values):
    """Merge ``values`` into the saved settings; keys that are not mentioned are kept."""
    with _lock:
        try:
            data = json.loads(config.SETTINGS_PATH.read_text(encoding="utf-8"))
        except FileNotFoundError:
            data = {}
        if not isinstance(data, dict):
            raise ValueError("Invalid settings file; refusing to overwrite it")
        data.update(values)
        atomic_write(config.SETTINGS_PATH, json.dumps(data).encode("utf-8"))
