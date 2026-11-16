"""Reusable Tk widgets / factories (card, label, button, tree) and the page switcher."""

import tkinter as tk
from tkinter import ttk

from personal_warehouse.core.barcode import code128_bars
from personal_warehouse.i18n import tr
from personal_warehouse.ui.theme import C, fnt


def card(parent, **kw):
    return tk.Frame(parent, bg=C["card"], highlightbackground=C["line"], highlightthickness=1, **kw)


def lbl(parent, text="", size=10, bold=False, fg=None, bg=None, **kw):
    return tk.Label(parent, text=text, font=fnt(size, bold), fg=fg or C["ink"], bg=bg or C["bg"], **kw)


def btn(parent, text, cmd, kind="soft", **kw):
    pal = {"primary": (C["accent"], "#FFFFFF", C["accent_d"]), "success": (C["ok"], "#FFFFFF", C["ok_d"]),
           "danger": (C["danger"], "#FFFFFF", C["danger_d"]), "soft": (C["head"], C["ink"], C["soft_h"]),
           "ghost": (C["card"], C["accent"], C["head"])}
    bg, fg, hov = pal[kind]
    opts = dict(padx=14, pady=8, cursor="hand2", font=fnt(10, True))
    opts.update(kw)                                   # callers may override padx / pady / font ...
    b = tk.Button(parent, text=text, command=cmd, bg=bg, fg=fg, activebackground=hov, activeforeground=fg,
                  disabledforeground=C["muted"], relief="flat", bd=0, **opts)
    b.bind("<Enter>", lambda e: b.configure(bg=hov) if str(b["state"]) != "disabled" else None)
    b.bind("<Leave>", lambda e: b.configure(bg=bg))
    return b


def make_tree(parent, cols, heads, widths, anchors=None, rtl=False, **kw):
    wrap = tk.Frame(parent, bg=C["card"], highlightbackground=C["line"], highlightthickness=1)
    tree = ttk.Treeview(wrap, columns=cols, show="headings", **kw)
    sb = ttk.Scrollbar(wrap, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=sb.set)
    flip = {"w": "e", "e": "w"}
    for c in cols:
        tree.heading(c, text=heads[c])
        a = (anchors or {}).get(c, "center")
        tree.column(c, width=widths[c], minwidth=50, anchor=flip.get(a, a) if rtl else a)
    if rtl:
        tree.configure(displaycolumns=list(reversed(cols)))
    tree.pack(side="right" if rtl else "left", fill="both", expand=True)
    sb.pack(side="left" if rtl else "right", fill="y")
    tree.tag_configure("odd", background=C["stripe"])
    tree.tag_configure("low", background=C["low"])
    tree.tag_configure("out", background=C["out"])
    tree.tag_configure("gone", foreground=C["gone"])
    return wrap, tree


def draw_barcode(canvas, text, width=250, height=74):
    canvas.delete("all")
    if not text:
        canvas.create_text(width // 2, height // 2, text=tr("bc_none"), fill="#64748B", font=fnt(9))
        return
    bars, total = code128_bars(text)
    quiet = 10
    scale = max(1, width // (total + 2 * quiet))
    x0 = (width - scale * (total + 2 * quiet)) // 2 + quiet * scale
    for x, w in bars:
        canvas.create_rectangle(x0 + x * scale, 4, x0 + (x + w) * scale, height - 20, fill="black", outline="")
    canvas.create_text(width // 2, height - 9, text=text, fill="black", font=("Courier New", 10, "bold"))



class Pages:
    """Tiny page switcher (sidebar navigation instead of notebook tabs)."""

    def __init__(self, on_select=None):
        self.current = None
        self.on_select = on_select

    def select(self, frame=None):
        if frame is None:
            return str(self.current) if self.current else ""
        if self.current is frame:
            return None
        if self.current is not None:
            self.current.pack_forget()
        frame.pack(fill="both", expand=True)
        self.current = frame
        if self.on_select:
            self.on_select(frame)
        return None
