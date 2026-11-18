"""Update check against GitHub Releases. No GUI code here, so it is easy to test.

The app only *tells* the user a newer version exists and opens the download page;
it never downloads or runs anything by itself.
"""
import json
import re
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
    asset = ""
    for a in data.get("assets") or []:
        name = (a.get("name") or "").lower()
        if name.endswith(".exe") and "setup" in name:
            asset = _safe_url(a.get("browser_download_url"))
            break
    return {"version": tag.lstrip("vV"),
            "page": _safe_url(data.get("html_url")),
            "download": asset,
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
