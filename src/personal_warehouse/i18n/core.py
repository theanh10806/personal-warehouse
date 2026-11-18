"""Translation table and the current language. Texts are registered by the modules in i18n/strings/."""

LANGS = {"vi": "Tiếng Việt", "en": "English", "ar": "العربية"}

TR = {}
_current = "vi"


def add(key, vi, en, ar):
    """Register one text in all three languages."""
    TR[key] = {"vi": vi, "en": en, "ar": ar}


def current():
    return _current


def set_language(code):
    global _current
    if code in LANGS:
        _current = code


def tr(key, *args):
    d = TR.get(key)
    s = (d.get(_current) or d.get("en") or key) if d else key
    return s.format(*args) if args else s
