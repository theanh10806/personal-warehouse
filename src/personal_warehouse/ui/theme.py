"""Colour palettes, current theme, fonts and the app's design scales.

Theme "Shin": a warm cream page, off-white "paper" cards with a thicker soft outline, a dark warm-ink
sidebar and three bold accents taken from the dashboard mock-up - red (primary / active), yellow
(hover, selection, indicators) and teal (positive) - plus a lilac for tertiary data.  Red is reserved
for the primary call-to-action and the active navigation item; destructive actions use a deeper
brick red so the two never get confused.  Dark mode keeps the same hues on a warm charcoal base.
"""

PALETTES = {
    "light": dict(
        # Base surfaces and typography
        bg="#FFF3E0", card="#FFFDF7", ink="#26242B", muted="#706F79", title="#26242B",
        side="#26242B", side_ink="#D8D6DE", side_act="#E8493F", side_hov="#33313A",
        side_tile="#33313A", side_tile_act="#EE7A72", side_logo="#FFFDF7",
        # Accent foregrounds are distinct from filled command buttons for readable contrast
        accent="#C93329", accent_d="#A82920", accent_fill="#D93B32", accent_hover="#BF2F27",
        ok="#2E7D74", ok_d="#246860", ok_fill="#2E7D74", ok_hover="#246860",
        warn="#8F5F00", danger="#B3261E", danger_d="#8F1B13", danger_fill="#B3261E",
        danger_hover="#8F1B13", teal="#2E7D74", violet="#6E4FB8",
        yellow="#FFCE3E", yellow_s="#FFF3C9", teal_fill="#5BC0B6", violet_fill="#B49BE8",
        ink_line="#26242B",
        # Control and divider surfaces
        head="#FFF3E0", line="#E8E3F0", soft_h="#FFF3C9",
        low="#FFF3C9", out="#FBE3E1", gone="#8B8A93", stripe="#FFF9EC",
        sel="#FFE7A3", input="#FFFDF7", occupied="#FFE7A3", empty="#FFF3E0",
        # Semantic tints
        accent_s="#FBE3E1", ok_s="#DCF3F0", warn_s="#FFF3C9", danger_s="#FBE3E1",
        teal_s="#DCF3F0", violet_s="#EBE1FA", top="#FFFDF7", ai="#FFF8EA",
    ),
    "dark": dict(
        bg="#1F1D24", card="#2B2931", ink="#ECEAF1", muted="#B3B1BC", title="#FFFFFF",
        side="#17151B", side_ink="#CFCDD7", side_act="#E8493F", side_hov="#2B2931",
        side_tile="#2B2931", side_tile_act="#EE7A72", side_logo="#2B2931",
        accent="#FF8A80", accent_d="#FFB0A9", accent_fill="#D93B32", accent_hover="#BF2F27",
        ok="#6FD3C8", ok_d="#9BE3DB", ok_fill="#2E7D74", ok_hover="#246860",
        warn="#FFCE3E", danger="#FF9A93", danger_d="#FFB9B4", danger_fill="#B3261E",
        danger_hover="#8F1B13", teal="#6FD3C8", violet="#C9B3F2",
        yellow="#FFCE3E", yellow_s="#473D1F", teal_fill="#5BC0B6", violet_fill="#B49BE8",
        ink_line="#ECEAF1",
        head="#35323C", line="#403D48", soft_h="#3F3B2E",
        low="#473D1F", out="#4A2B2C", gone="#9C9AA6", stripe="#2F2D36",
        sel="#4A4128", input="#25232A", occupied="#4A4128", empty="#25232A",
        accent_s="#4A2B2C", ok_s="#1F3C39", warn_s="#473D1F", danger_s="#4A2B2C",
        teal_s="#1F3C39", violet_s="#3A3150", top="#2B2931", ai="#25232A",
    ),
}
C = dict(PALETTES["light"])

THEME = "light"
FONT = "Segoe UI Variable"
SCALE = 1.0                      # screen DPI / 96, set once by the main window (see set_scale)


def set_scale(factor):
    """Pixel sizes (sidebar width, row height ...) do not follow Tk's point-based font scaling; px() does."""
    global SCALE
    try:
        SCALE = max(1.0, min(3.0, float(factor)))
    except (TypeError, ValueError):
        SCALE = 1.0


def px(n):
    return int(round(n * SCALE))


def bw():
    """Outline thickness of cards / inputs (the mock-up uses a 1.5 px stroke)."""
    return max(2, px(1.5))


def current_theme():
    return THEME


def set_theme(name):
    global THEME
    THEME = name if name in PALETTES else "light"
    C.clear()
    C.update(PALETTES[THEME])


# Type scale: the only sizes the UI may use, so the visual hierarchy
# (page title > section > body > label > hint) stays consistent everywhere.
TS = {"page": 21, "kpi": 24, "section": 12, "body": 10, "label": 9, "hint": 8}

# Spacing scale (base pixels at 96 dpi).  Always go through sp() so the values
# follow the display's DPI scaling instead of staying fixed.
SP = {"xxs": 4, "xs": 8, "sm": 12, "md": 16, "lg": 20, "xl": 24}


def sp(name):
    """A spacing token, DPI-scaled: sp("sm") -> 12 px at 96 dpi."""
    return px(SP[name])


def mix(a, b, t):
    """Blend two #RRGGBB colours linearly (t in [0, 1]; 0 -> a, 1 -> b).

    Used by the micro-animations (page fade-in, value pulses); both inputs must
    be hex colours from the palette."""
    pa = tuple(int(a[i:i + 2], 16) for i in (1, 3, 5))
    pb = tuple(int(b[i:i + 2], 16) for i in (1, 3, 5))
    return "#%02X%02X%02X" % tuple(max(0, min(255, round(x + (y - x) * t))) for x, y in zip(pa, pb))


def pick_font():
    """Choose the first installed UI font. Needs a Tk root to exist."""
    global FONT
    import tkinter.font as tkfont
    fams = set(tkfont.families())
    FONT = next((f for f in ("Segoe UI Variable", "Segoe UI", "SF Pro Text", "Helvetica Neue", "Noto Sans", "DejaVu Sans", "Arial")
                 if f in fams), "TkDefaultFont")


def fnt(size=10, bold=False):
    return (FONT, size, "bold" if bold else "normal")
