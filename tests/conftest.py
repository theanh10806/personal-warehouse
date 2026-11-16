"""Test setup.

* Every test starts with its own throw-away data folder (``PW_DATA_DIR`` is read at import time).
* ``fake_tk`` replaces tkinter with a tiny stand-in so the whole UI can be built and driven in CI
  (no display, no Tk installed). It is strict about the window object: calling a method that does not
  exist on the app raises AttributeError, so typos and bad wiring between the page modules show up.
"""
import os
import sys
import tempfile
import types
from unittest import mock

import pytest

os.environ["PW_DATA_DIR"] = tempfile.mkdtemp(prefix="pw_test_")

from personal_warehouse import config  # noqa: E402


@pytest.fixture()
def data_dir(tmp_path, monkeypatch):
    """Point every data path at a fresh folder and create the schema."""
    for name, sub in (("DATA_DIR", ""), ("PHOTO_DIR", "Photos"), ("BACKUP_DIR", "Backup"), ("LABEL_DIR", "Labels")):
        p = tmp_path / sub if sub else tmp_path
        p.mkdir(exist_ok=True)
        monkeypatch.setattr(config, name, p)
    monkeypatch.setattr(config, "DB_PATH", tmp_path / "warehouse.db")
    monkeypatch.setattr(config, "SETTINGS_PATH", tmp_path / "settings.json")
    from personal_warehouse.core.database import init_db
    init_db()
    return tmp_path


class FakeVar:
    default = ""

    def __init__(self, master=None, value=None, **kw):
        self._v = self.default if value is None else value

    def get(self):
        return self._v

    def set(self, v):
        self._v = v

    def trace_add(self, *a, **k):
        pass


class FakeBool(FakeVar):
    default = False


class FakeEntry:
    """ttk.Entry / Combobox / Spinbox that really stores text."""

    def __init__(self, master=None, **kw):
        self._v = str(kw.get("textvariable").get()) if kw.get("textvariable") is not None else ""

    def get(self):
        return self._v

    def set(self, v):
        self._v = str(v)

    def insert(self, i, s):
        self._v = self._v + str(s)

    def delete(self, a, b=None):
        self._v = ""

    def __setitem__(self, k, v):
        pass

    def __getattr__(self, name):             # pack, grid, bind, configure, focus_set ...
        if name.startswith("__"):
            raise AttributeError(name)
        return mock.MagicMock(name=name)


class FakeToplevel:
    def __init__(self, *a, **k):
        pass

    def __getattr__(self, name):
        if name.startswith("__"):
            raise AttributeError(name)
        return mock.MagicMock(name=name)


class FakeCanvas:
    def __init__(self, *a, **k):
        pass

    def winfo_width(self):
        return 800

    def winfo_height(self):
        return 300

    def __getattr__(self, name):
        if name.startswith("__"):
            raise AttributeError(name)
        return mock.MagicMock(name=name)


class FakeTk:
    """Main window stand-in. Only real Tk methods exist; anything else is an AttributeError on purpose."""
    _ALLOWED = ("title geometry minsize configure cget protocol mainloop bell update update_idletasks "
                "wait_window bind option_add focus_set destroy after_cancel").split()

    def __init__(self, *a, **k):
        self.scheduled = []

    def after(self, ms, fn=None, *args):
        self.scheduled.append(fn)
        return f"job{len(self.scheduled)}"

    def winfo_children(self):
        return []

    def winfo_width(self):
        return 1000

    def __getattr__(self, name):
        if name in self._ALLOWED:
            return mock.MagicMock(name=name)
        raise AttributeError(name)


def _module(name, **attrs):
    m = types.ModuleType(name)
    m.__getattr__ = lambda attr: mock.MagicMock(name=f"{name}.{attr}")
    for k, v in attrs.items():
        setattr(m, k, v)
    return m


@pytest.fixture()
def fake_tk(monkeypatch):
    ttk = _module("tkinter.ttk", Entry=FakeEntry, Combobox=FakeEntry, Spinbox=FakeEntry)
    font = _module("tkinter.font", families=lambda: ["Arial"])
    filedialog = _module("tkinter.filedialog")
    messagebox = _module("tkinter.messagebox", askyesno=lambda *a, **k: True, showinfo=mock.MagicMock(),
                         showerror=mock.MagicMock())
    tk = _module("tkinter", Tk=FakeTk, Toplevel=FakeToplevel, StringVar=FakeVar, BooleanVar=FakeBool, Canvas=FakeCanvas,
                 TclError=type("TclError", (Exception,), {}), ttk=ttk, font=font, filedialog=filedialog,
                 messagebox=messagebox)
    for name, mod in (("tkinter", tk), ("tkinter.ttk", ttk), ("tkinter.font", font),
                      ("tkinter.filedialog", filedialog), ("tkinter.messagebox", messagebox)):
        monkeypatch.setitem(sys.modules, name, mod)
    stale = [m for m in sys.modules if m.startswith("personal_warehouse.ui")]
    for m in stale:
        monkeypatch.delitem(sys.modules, m)
    yield types.SimpleNamespace(tk=tk, filedialog=filedialog, messagebox=messagebox)
    for m in [m for m in sys.modules if m.startswith("personal_warehouse.ui")]:
        del sys.modules[m]
