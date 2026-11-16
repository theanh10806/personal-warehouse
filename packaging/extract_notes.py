"""Print the CHANGELOG.md section for one version (used as the GitHub release notes).

usage: python packaging/extract_notes.py 3.0.0 > notes.md
"""
import re
import sys
from pathlib import Path


def extract(changelog, version):
    m = re.search(rf"^## \[{re.escape(version)}\][^\n]*\n(.*?)(?=^## \[|\Z)", changelog, re.S | re.M)
    return m.group(1).strip() if m else ""


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    text = Path(__file__).resolve().parents[1].joinpath("CHANGELOG.md").read_text(encoding="utf-8")
    notes = extract(text, sys.argv[1].lstrip("v"))
    print(notes or f"Release {sys.argv[1]}")
