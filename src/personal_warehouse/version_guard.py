"""One program per computer: the newest installed version wins, an older one refuses to start.

Microsoft Store (MSIX) and the GitHub installer (Inno Setup) are two separate packages, so Windows will happily keep
both. They share the same data folder and the same single-instance lock; this module adds the missing rule:

* every start records the highest version seen in ``~/.personal_warehouse/installed_version.txt``
  (line 1 = version, line 2 = channel: ``store`` / ``installer`` / ``source``);
* a build older than that version shows "you already have a newer version" and exits, so an old copy can never
  open (or migrate backwards) data that a newer copy has already used;
* the Inno Setup installer reads the same file and refuses to install an older version (see packaging/installer.iss).

The marker is a plain text file on purpose: the installer script has to read it too.
"""
import os
from pathlib import Path
import sys

from personal_warehouse import __version__

MARKER_NAME = "installed_version.txt"


def state_dir():
    """Same folder as the single-instance lock (``PW_STATE_DIR`` only exists so tests never touch the real one)."""
    override = os.environ.get("PW_STATE_DIR")
    return Path(override) if override else Path.home() / ".personal_warehouse"


def marker_path():
    return state_dir() / MARKER_NAME


def channel():
    from personal_warehouse import updater
    if updater.is_store_package():
        return "store"
    return "installer" if getattr(sys, "frozen", False) else "source"


def read_marker():
    """Return (version, channel) of the newest version recorded on this computer, or None."""
    try:
        lines = marker_path().read_text(encoding="utf-8").splitlines()
    except OSError:
        return None
    version = (lines[0] if lines else "").strip()
    from personal_warehouse.updater import parse_version
    if not version or parse_version(version) == (0,):         # empty / garbage marker: ignore it, never lock the user out
        return None
    return version, (lines[1].strip() if len(lines) > 1 else "")


def check(current=__version__):
    """{'status': 'ok'|'older', 'installed': newest recorded version or ''}."""
    if os.environ.get("PW_SKIP_VERSION_GUARD") == "1":
        return {"status": "ok", "installed": ""}
    from personal_warehouse.updater import parse_version
    found = read_marker()
    if found and parse_version(current) < parse_version(found[0]):
        return {"status": "older", "installed": found[0]}
    return {"status": "ok", "installed": found[0] if found else ""}


def record(current=__version__, source_channel=None):
    """Remember this version as the newest one - only ever upwards. Failure to write must never stop the app."""
    from personal_warehouse.updater import parse_version
    found = read_marker()
    if found and parse_version(found[0]) > parse_version(current):
        return False
    if found and found[0] == current and found[1] == (source_channel or channel()):
        return True                                           # nothing changed
    try:
        from personal_warehouse.settings import atomic_write
        state_dir().mkdir(parents=True, exist_ok=True)
        atomic_write(marker_path(), f"{current}\n{source_channel or channel()}\n".encode("utf-8"))
    except OSError:
        return False
    return True


def older_message(installed, current=__version__):
    from personal_warehouse.i18n import tr
    return tr("vg_older", installed, current, str(marker_path()))
