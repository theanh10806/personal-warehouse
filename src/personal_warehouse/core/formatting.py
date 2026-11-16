"""Small formatting / parsing helpers shared by the whole app."""

import re

from personal_warehouse import config
from personal_warehouse.i18n import current_lang, tr


def make_location(section, part):
    """'A' + '1' -> 'A1'  (Section letter + Part number)."""
    return f"{section}{part}"


def parse_location(code):
    """'A1' -> ('A', '1')."""
    return code[0], code[1:]


def money(v):
    try:
        return f"${float(v):,.2f}"
    except (TypeError, ValueError):
        return "$0.00"


def qty_fmt(v):
    return f"{float(v or 0):,.3f}".rstrip("0").rstrip(".")


def num(text, field):
    s = (text or "").strip().replace(" ", "")
    if not s:
        return 0.0
    if re.fullmatch(r"\d{1,3}(,\d{3})+(\.\d+)?", s):
        s = s.replace(",", "")
    elif "," in s and "." not in s:
        s = s.replace(",", ".")
    try:
        v = float(s)
    except ValueError:
        raise ValueError(tr("num_must", field))
    if v < 0 or v != v or v == float("inf"):
        raise ValueError(tr("num_nonneg", field))
    return v


def photo_file(stored):
    return (config.PHOTO_DIR / stored) if stored else None


def item_name(r):
    """Name shown in lists: the Arabic name when the UI is Arabic and one exists."""
    try:
        if current_lang() == "ar" and r["name_ar"]:
            return r["name_ar"]
    except (IndexError, KeyError):
        pass
    return r["name"]
