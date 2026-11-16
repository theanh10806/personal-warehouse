"""Colour palettes, current theme and fonts."""

PALETTES = {
    "light": dict(bg="#F3F5F9", card="#FFFFFF", ink="#182230", muted="#778196", title="#111827",
                  side="#FFFFFF", side_ink="#4B5565", side_act="#E8EDFF", side_hov="#F1F4FA",
                  accent="#536DFE", accent_d="#4058E8", ok="#218B68", ok_d="#187653",
                  warn="#E6A23C", danger="#D94B55", danger_d="#BE3540", teal="#47BBD5", violet="#9870D5",
                  head="#EEF1F6", line="#E5E9F0", soft_h="#DDE3EF", low="#FFF3D8", out="#FCE8E8",
                  gone="#9AA3B2", stripe="#FAFBFD", sel="#E7EDFF", input="#FFFFFF",
                  occupied="#E7EDFF", empty="#F3F5F9"),
    "dark": dict(bg="#111827", card="#1B2535", ink="#E7ECF5", muted="#A0AEC0", title="#F5F7FB",
                 side="#151E2D", side_ink="#B7C1D1", side_act="#293A66", side_hov="#202E45",
                 accent="#7188FF", accent_d="#536DFE", ok="#38B987", ok_d="#218B68",
                 warn="#F3BD58", danger="#F16B74", danger_d="#D94B55", teal="#5BC9E2", violet="#B18CEB",
                 head="#253247", line="#2B3A50", soft_h="#34445C", low="#4A3A20", out="#4A252D",
                 gone="#728096", stripe="#1E293B", sel="#293A66", input="#202C3E",
                 occupied="#293A66", empty="#202C3E"),
}
C = dict(PALETTES["light"])

THEME = "light"
FONT = "Segoe UI"


def current_theme():
    return THEME


def set_theme(name):
    global THEME
    THEME = name if name in PALETTES else "light"
    C.clear()
    C.update(PALETTES[THEME])


def pick_font():
    """Choose the first installed UI font. Needs a Tk root to exist."""
    global FONT
    import tkinter.font as tkfont
    fams = set(tkfont.families())
    FONT = next((f for f in ("Segoe UI", "SF Pro Text", "Helvetica Neue", "Noto Sans", "DejaVu Sans", "Arial")
                 if f in fams), "TkDefaultFont")


def fnt(size=10, bold=False):
    return (FONT, size, "bold" if bold else "normal")
