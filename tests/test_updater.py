import pytest

from personal_warehouse import updater


@pytest.mark.parametrize("latest,current,expected", [
    ("3.0.1", "3.0.0", True),
    ("v3.1.0", "3.0.9", True),
    ("3.0.0", "3.0.0", False),
    ("3.0", "3.0.0", False),
    ("2.9.9", "3.0.0", False),
    ("10.0.0", "9.9.9", True),          # numeric, not string, comparison
    ("3.1.0-beta", "3.1.0", False),     # pre-release is older than the final release
    ("3.1.0", "3.1.0-beta", True),
])
def test_is_newer(latest, current, expected):
    assert updater.is_newer(latest, current) is expected


def test_parse_version_garbage():
    assert updater.parse_version("") == (0,)
    assert updater.parse_version("abc") == (0,)
    assert updater.parse_version("3.0") == updater.parse_version("v3.0.0")


def test_is_configured():
    assert not updater.is_configured("your-username/personal-warehouse")
    assert not updater.is_configured("")
    assert not updater.is_configured("not a repo")
    assert updater.is_configured("someone/personal-warehouse")


def _payload(**kw):
    base = {"tag_name": "v3.1.0", "html_url": "https://github.com/o/r/releases/tag/v3.1.0", "body": " notes ",
            "assets": [{"name": "PersonalWarehouse-Setup-3.1.0.exe",
                        "browser_download_url": "https://github.com/o/r/releases/download/v3.1.0/x.exe"}]}
    base.update(kw)
    return base


def test_parse_release_ok():
    rel = updater.parse_release(_payload())
    assert rel["version"] == "3.1.0"
    assert rel["download"].endswith("x.exe")
    assert rel["notes"] == "notes"


def test_parse_release_skips_draft_and_prerelease():
    assert updater.parse_release(_payload(draft=True)) is None
    assert updater.parse_release(_payload(prerelease=True)) is None
    assert updater.parse_release({}) is None
    assert updater.parse_release(None) is None


def test_parse_release_rejects_foreign_urls():
    rel = updater.parse_release(_payload(html_url="https://evil.example/x", assets=[
        {"name": "A-Setup.exe", "browser_download_url": "https://evil.example/a.exe"}]))
    assert rel["page"] == "" and rel["download"] == ""


def test_check_disabled_without_repo():
    assert updater.check(repo="your-username/personal-warehouse")["status"] == "disabled"


def test_check_new_current_error(monkeypatch):
    rel = {"version": "3.1.0", "page": "", "download": "", "notes": ""}
    monkeypatch.setattr(updater, "fetch_latest", lambda repo, timeout: rel)
    assert updater.check("o/r", current="3.0.0")["status"] == "new"
    assert updater.check("o/r", current="3.1.0")["status"] == "current"

    def boom(repo, timeout):
        raise OSError("offline")
    monkeypatch.setattr(updater, "fetch_latest", boom)
    res = updater.check("o/r", current="3.0.0")
    assert res["status"] == "error" and "offline" in res["error"]
