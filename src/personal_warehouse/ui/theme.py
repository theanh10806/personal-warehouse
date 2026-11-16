"""Colour palettes, current theme and fonts."""

PALETTES = {
    "light": dict(bg="#F1F5F9", card="#FFFFFF", ink="#0F172A", muted="#64748B", title="#0F2747",
                  side="#0F2747", side_ink="#CBD5E1", side_act="#2563EB", side_hov="#1B3A66",
                  accent="#2563EB", accent_d="#1D4ED8", ok="#16A34A", ok_d="#15803D",
                  warn="#F59E0B", danger="#DC2626", danger_d="#B91C1C", teal="#0891B2", violet="#7C3AED",
                  head="#E2E8F0", line="#E2E8F0", soft_h="#CBD5E1", low="#FEF3C7", out="#FEE2E2",
                  gone="#94A3B8", stripe="#F8FAFC", sel="#DBEAFE", input="#FFFFFF",
                  occupied="#DBEAFE", empty="#F1F5F9"),
    "dark": dict(bg="#0B1220", card="#111B2E", ink="#E5E7EB", muted="#94A3B8", title="#F1F5F9",
                 side="#070D18", side_ink="#94A3B8", side_act="#2563EB", side_hov="#13213A",
                 accent="#3B82F6", accent_d="#2563EB", ok="#22C55E", ok_d="#16A34A",
                 warn="#FBBF24", danger="#EF4444", danger_d="#DC2626", teal="#22D3EE", violet="#A78BFA",
                 head="#1A2740", line="#243350", soft_h="#2A3B5C", low="#4A3A10", out="#4B1D22",
                 gone="#64748B", stripe="#0F1A2D", sel="#1E3A66", input="#16233A",
                 occupied="#1E3A66", empty="#16233A"),
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
    import tkinter.font as tkfont          # imported here so this module (and main.py) load without Tk
    fams = set(tkfont.families())
    FONT = next((f for f in ("Segoe UI", "SF Pro Text", "Helvetica Neue", "Noto Sans", "DejaVu Sans", "Arial")
                 if f in fams), "TkDefaultFont")


def fnt(size=10, bold=False):
    return (FONT, size, "bold" if bold else "normal")
