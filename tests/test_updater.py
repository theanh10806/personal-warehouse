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


# ---------------------------------------------------------------------------------------------- self-update
import hashlib  # noqa: E402

GOOD = b"MZ" + b"x" * 200_000


class FakeResp:
    def __init__(self, data, url="https://objects.githubusercontent.com/x.exe", length=True):
        self._data, self._pos, self._url = data, 0, url
        self.headers = {"Content-Length": str(len(data))} if length else {}

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def geturl(self):
        return self._url

    def read(self, n):
        chunk = self._data[self._pos:self._pos + n]
        self._pos += len(chunk)
        return chunk


def _opener(data, **kw):
    return lambda req, timeout=None: FakeResp(data, **kw)


GH = "https://github.com/o/r/releases/download/v3.1.0/PersonalWarehouse-Setup-3.1.0.exe"


def test_parse_release_carries_checksum_and_size():
    sha = hashlib.sha256(GOOD).hexdigest()
    rel = updater.parse_release(_payload(assets=[{"name": "PersonalWarehouse-Setup-3.1.0.exe", "size": len(GOOD),
                                                  "digest": "sha256:" + sha, "browser_download_url": GH}]))
    assert rel["sha256"] == sha and rel["size"] == len(GOOD)
    bad = updater.parse_release(_payload(assets=[{"name": "A-Setup.exe", "digest": "md5:abc", "browser_download_url": GH}]))
    assert bad["sha256"] == "" and bad["size"] == 0


def test_download_ok_reports_progress(tmp_path):
    seen = []
    dest = updater.download(GH, tmp_path / "s.exe", hashlib.sha256(GOOD).hexdigest(), len(GOOD),
                            progress=lambda d, t: seen.append((d, t)), _open=_opener(GOOD))
    assert dest.read_bytes() == GOOD and not (tmp_path / "s.exe.part").exists()
    assert seen[-1] == (len(GOOD), len(GOOD))


@pytest.mark.parametrize("data,kw,msg", [
    pytest.param(GOOD, {"sha256": "0" * 64}, "SHA-256", id="wrong-sha256"),
    pytest.param(GOOD, {"size": 5}, "size", id="wrong-size"),
    pytest.param(b"<html>not an exe</html>", {}, "not a Windows program", id="not-an-exe"),
    pytest.param(b"", {}, "empty", id="empty-file"),
])
def test_download_rejects_bad_files_and_leaves_nothing(tmp_path, data, kw, msg):
    with pytest.raises(ValueError, match=msg):
        updater.download(GH, tmp_path / "s.exe", _open=_opener(data), **kw)
    assert list(tmp_path.iterdir()) == []


def test_download_refuses_foreign_or_insecure_urls(tmp_path):
    with pytest.raises(ValueError):
        updater.download("https://evil.example/a.exe", tmp_path / "s.exe", _open=_opener(GOOD))
    with pytest.raises(ValueError, match="insecure"):
        updater.download(GH, tmp_path / "s.exe", _open=_opener(GOOD, url="http://plain.example/a.exe"))
    assert list(tmp_path.iterdir()) == []


def test_download_can_be_cancelled(tmp_path):
    with pytest.raises(InterruptedError):
        updater.download(GH, tmp_path / "s.exe", cancelled=lambda: True, _open=_opener(GOOD))
    assert list(tmp_path.iterdir()) == []


def test_installer_command_is_silent_and_relaunches():
    cmd = updater.installer_command("C:/t/Setup.exe")
    assert cmd[0] == "C:/t/Setup.exe" and "/SILENT" in cmd and "/RELAUNCH=1" in cmd and "/CLOSEAPPLICATIONS" in cmd


def test_launch_installer_needs_a_real_exe(tmp_path):
    with pytest.raises(ValueError):
        updater.launch_installer(tmp_path / "missing.exe")
    txt = tmp_path / "a.txt"
    txt.write_text("x")
    with pytest.raises(ValueError):
        updater.launch_installer(txt)


def test_store_package_detection(monkeypatch):
    monkeypatch.setattr(updater.sys, "platform", "win32")
    monkeypatch.setattr(updater.sys, "executable", r"C:\Program Files\WindowsApps\PW_3.1.0.0_x64__abc\PersonalWarehouse.exe")
    assert updater.is_store_package() and not updater.can_self_update()
    monkeypatch.setattr(updater.sys, "executable", r"C:\Users\me\AppData\Local\Programs\Personal Warehouse\PersonalWarehouse.exe")
    monkeypatch.setattr(updater.sys, "frozen", True, raising=False)
    assert not updater.is_store_package() and updater.can_self_update()
