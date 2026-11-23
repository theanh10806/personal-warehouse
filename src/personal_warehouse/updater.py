"""Update check, download and install against GitHub Releases. No GUI code here, so it is easy to test.

Flow: ``check()`` tells the UI a newer version exists; only after the user agrees does ``download()`` fetch the
installer (checked against the size / SHA-256 GitHub publishes), and ``launch_installer()`` runs it silently while
the app closes. Nothing is downloaded or run without that explicit click.
"""
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.request

from personal_warehouse import GITHUB_REPO, __version__

API_URL = "https://api.github.com/repos/{repo}/releases/latest"
ALLOWED_PREFIX = "https://github.com/"


def is_configured(repo=GITHUB_REPO):
    return bool(re.fullmatch(r"[\w.-]+/[\w.-]+", repo or "")) and not repo.startswith("your-username/")


def parse_version(text):
    """'v3.1.0' -> (3, 1, 0); '3.1.0-beta' -> (3, 1, -1), so a pre-release sorts below the final release."""
    s = (text or "").strip().lstrip("vV")
    m = re.match(r"(\d+(?:\.\d+)*)(.*)$", s)
    if not m:
        return (0,)
    nums = tuple(int(x) for x in m.group(1).split("."))
    while len(nums) > 1 and nums[-1] == 0:          # 3.0 == 3.0.0
        nums = nums[:-1]
    pre = m.group(2).lstrip().startswith(("-", "a", "b", "rc"))
    return nums + ((-1,) if pre else (0,))          # final release (…,0) sorts above pre-release (…,-1)


def is_newer(latest, current=__version__):
    return parse_version(latest) > parse_version(current)


def _safe_url(url):
    return url if isinstance(url, str) and url.startswith(ALLOWED_PREFIX) else ""


def parse_release(data):
    """Reduce the GitHub API payload to what the UI needs. Returns None for drafts / pre-releases / bad data."""
    if not isinstance(data, dict) or data.get("draft") or data.get("prerelease"):
        return None
    tag = data.get("tag_name") or ""
    if not tag:
        return None
    asset, sha, size = "", "", 0
    for a in data.get("assets") or []:
        name = (a.get("name") or "").lower()
        if name.endswith(".exe") and "setup" in name:
            asset = _safe_url(a.get("browser_download_url"))
            digest = str(a.get("digest") or "").lower()               # GitHub: "sha256:<64 hex>"
            if digest.startswith("sha256:") and re.fullmatch(r"[0-9a-f]{64}", digest[7:]):
                sha = digest[7:]
            size = a.get("size") if isinstance(a.get("size"), int) and a.get("size") > 0 else 0
            break
    return {"version": tag.lstrip("vV"),
            "page": _safe_url(data.get("html_url")),
            "download": asset, "sha256": sha if asset else "", "size": size if asset else 0,
            "notes": (data.get("body") or "").strip()[:1500]}


def fetch_latest(repo=GITHUB_REPO, timeout=6):
    """Return the latest release dict, or None if nothing could be read. Raises OSError / ValueError on failure."""
    req = urllib.request.Request(API_URL.format(repo=repo), headers={
        "Accept": "application/vnd.github+json", "User-Agent": f"PersonalWarehouse/{__version__}"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return parse_release(json.loads(resp.read().decode("utf-8")))


def check(repo=GITHUB_REPO, current=__version__, timeout=6):
    """Return {'status': 'new'|'current'|'disabled'|'error', 'release': dict|None, 'error': str}."""
    if not is_configured(repo):
        return {"status": "disabled", "release": None, "error": ""}
    try:
        rel = fetch_latest(repo, timeout)
    except Exception as e:                           # offline, rate limited, 404 (no release yet) ...
        return {"status": "error", "release": None, "error": str(e)}
    if rel and is_newer(rel["version"], current):
        return {"status": "new", "release": rel, "error": ""}
    return {"status": "current", "release": rel, "error": ""}


# ---------------------------------------------------------------------------------------------- self-update
def is_store_package():
    """True when running from a Microsoft Store (MSIX) install: the Store updates those, never the app itself."""
    if sys.platform != "win32":
        return False
    exe = str(sys.executable or "").replace("/", "\\").lower()
    if "\\windowsapps\\" in exe:
        return True
    try:
        import ctypes
        from ctypes import wintypes
        function = ctypes.windll.kernel32.GetCurrentPackageFullName
        function.argtypes = [ctypes.POINTER(wintypes.UINT), wintypes.LPWSTR]
        function.restype = wintypes.LONG
        length = wintypes.UINT(0)
        result = function(ctypes.byref(length), None)
        if result == 122:
            return True
        if result == 15700:
            return False
    except (AttributeError, OSError):
        pass
    exe = str(sys.executable or "").replace("/", "\\").lower()
    return "\\windowsapps\\" in exe


def can_self_update():
    """In-app install only makes sense for the installed Windows app (not from source, not a Store package)."""
    return sys.platform == "win32" and bool(getattr(sys, "frozen", False)) and not is_store_package()


def update_dir():
    return Path(tempfile.gettempdir()) / "PersonalWarehouse-update"


def clean_update_dir():
    shutil.rmtree(update_dir(), ignore_errors=True)
    update_dir().mkdir(parents=True, exist_ok=True)


def download(url, dest, sha256="", size=0, progress=None, cancelled=None, timeout=30, _open=None):
    """Download ``url`` to ``dest`` and verify it. Raises InterruptedError when cancelled, ValueError / OSError otherwise.

    ``progress(done_bytes, total_bytes)`` is called while data arrives; ``cancelled()`` is polled between chunks.
    The file only appears at ``dest`` once it is complete and verified, so a half-finished download can never be run.
    """
    if not _safe_url(url):
        raise ValueError("Untrusted download address")
    opener = _open or urllib.request.urlopen
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    part = dest.with_name(dest.name + ".part")
    req = urllib.request.Request(url, headers={"User-Agent": f"PersonalWarehouse/{__version__}"})
    digest, done = hashlib.sha256(), 0
    try:
        with opener(req, timeout=timeout) as resp, open(part, "wb") as out:
            final = getattr(resp, "geturl", lambda: url)()
            if not str(final).startswith("https://"):
                raise ValueError("Download was redirected to an insecure address")
            total = int(resp.headers.get("Content-Length") or 0) or size
            while True:
                if cancelled and cancelled():
                    raise InterruptedError("cancelled")
                chunk = resp.read(65536)
                if not chunk:
                    break
                if done == 0 and not chunk.startswith(b"MZ"):
                    raise ValueError("Downloaded file is not a Windows program")
                out.write(chunk)
                digest.update(chunk)
                done += len(chunk)
                if progress:
                    progress(done, total)
        if done == 0:
            raise ValueError("Downloaded file is empty")
        if size and done != size:
            raise ValueError(f"Downloaded file has the wrong size ({done} instead of {size})")
        if sha256 and digest.hexdigest() != sha256.lower():
            raise ValueError("Downloaded file failed the SHA-256 check")
        os.replace(part, dest)
    except BaseException:
        try:
            part.unlink()
        except OSError:
            pass
        raise
    return dest


def installer_command(path):
    """Silent upgrade: close the running app, keep going without prompts, then start the new version."""
    return [str(path), "/SILENT", "/SUPPRESSMSGBOXES", "/NORESTART", "/CLOSEAPPLICATIONS", "/LOG", "/RELAUNCH=1"]   # /LOG: setup log in %TEMP%, evidence if a silent install fails


def launch_installer(path):
    """Start the downloaded installer detached from this process (so it survives the app closing)."""
    path = Path(path)
    if path.suffix.lower() != ".exe" or not path.is_file():
        raise ValueError("Installer file is missing")
    flags = 0
    if sys.platform == "win32":
        flags = subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
    subprocess.Popen(installer_command(path), close_fds=True, creationflags=flags)
