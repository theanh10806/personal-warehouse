"""Internationalisation: Tiếng Việt / English / العربية.

To add or change a text, edit the module for that feature in ``i18n/strings/``.
To add a language, add it to ``LANGS`` in ``core.py`` and give every ``_t(...)`` a fourth value.
"""
from personal_warehouse.config import CONDITIONS, MOVE_KEYS, UNITS
from personal_warehouse.i18n.core import LANGS, TR, add, current as current_lang, set_language, tr
from personal_warehouse.i18n.strings import (  # noqa: F401  (importing registers the texts)
<<<<<<< HEAD
    common, dashboard, export, inventory, item_form, labels, locations, movements, scan, settings, webui)
=======
    common, dashboard, export, inventory, item_form, labels, locations, movements, scan, settings)
>>>>>>> c8a133662267867832f0d0679ec8832dee7dfdbb

__all__ = ["LANGS", "TR", "add", "tr", "current_lang", "set_language", "cond_t", "unit_t", "mv_t", "from_label"]


def cond_t(v):
    return tr("cond_" + v) if v in CONDITIONS else (v or "")


def unit_t(v):
    return tr("unit_" + v) if v in UNITS else (v or "")


def mv_t(v):
    return tr(MOVE_KEYS[v]) if v in MOVE_KEYS else (v or "")


def from_label(values, fn, label):
    """Reverse of cond_t / unit_t / mv_t: translated label -> internal value."""
    for v in values:
        if fn(v) == label:
            return v
    return label
