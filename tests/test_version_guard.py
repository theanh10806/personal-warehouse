"""One program per computer: an older build must not run once a newer one has been seen (Store and GitHub share a marker)."""
from pathlib import Path

import pytest

from personal_warehouse import main as app_main, version_guard


@pytest.fixture()
def state(tmp_path, monkeypatch):
    monkeypatch.setenv("PW_STATE_DIR", str(tmp_path / "state"))
    monkeypatch.delenv("PW_SKIP_VERSION_GUARD", raising=False)
    return tmp_path / "state" / "installed_version.txt"


def test_no_marker_allows_and_records(state):
    assert version_guard.check("3.8.0")["status"] == "ok"
    assert version_guard.record("3.8.0", "store")
    assert state.read_text(encoding="utf-8").splitlines() == ["3.8.0", "store"]


def test_older_build_is_refused(state):
    version_guard.record("3.8.0", "store")
    res = version_guard.check("3.1.0")
    assert res == {"status": "older", "installed": "3.8.0"}          # Store 3.1.0 after GitHub/Store 3.8.0


def test_same_and_newer_allowed_and_marker_only_goes_up(state):
    version_guard.record("3.8.0", "store")
    assert version_guard.check("3.8.0")["status"] == "ok"            # same version from the other channel is fine
    assert version_guard.check("3.9.0")["status"] == "ok"
    assert version_guard.record("3.1.0", "installer") is False       # never lowered
    assert state.read_text(encoding="utf-8").startswith("3.8.0")
    assert version_guard.record("3.9.0", "installer")
    assert version_guard.read_marker() == ("3.9.0", "installer")


@pytest.mark.parametrize("junk", ["", "\n", "hello\nstore\n", "\x00\x01"])
def test_garbage_marker_never_locks_the_user_out(state, junk):
    state.parent.mkdir(parents=True)
    state.write_text(junk, encoding="utf-8")
    assert version_guard.check("3.1.0")["status"] == "ok"


def test_skip_env_for_developers(state, monkeypatch):
    version_guard.record("9.0.0", "store")
    monkeypatch.setenv("PW_SKIP_VERSION_GUARD", "1")
    assert version_guard.check("3.1.0")["status"] == "ok"


def test_message_names_both_versions_in_every_language(state):
    from personal_warehouse.i18n import set_language
    try:
        for lang in ("vi", "en", "ar"):
            set_language(lang)
            text = version_guard.older_message("3.8.0", "3.1.0")
            assert "3.8.0" in text and "3.1.0" in text and str(version_guard.marker_path()) in text
    finally:
        set_language("vi")


def test_main_stops_older_build_and_shows_message(state, monkeypatch, capsys):
    version_guard.record("99.0.0", "store")
    ran = []
    monkeypatch.setattr(app_main, "_run", lambda argv=None: ran.append(1))
    monkeypatch.setattr(app_main.sys, "platform", "linux")
    app_main.main([])
    assert not ran and "99.0.0" in capsys.readouterr().out


def test_main_starts_and_records_when_current(state, monkeypatch):
    ran = []
    monkeypatch.setattr(app_main, "_run", lambda argv=None: ran.append(1))
    app_main.main([])
    assert ran and version_guard.read_marker()[0] == version_guard.__version__


def test_installer_reads_the_same_marker_file():
    iss = (Path(__file__).resolve().parents[1] / "packaging" / "installer.iss").read_text(encoding="utf-8")
    assert version_guard.MARKER_NAME in iss and ".personal_warehouse" in iss
    assert "InitializeSetup" in iss and "ComparePackedVersion" in iss
