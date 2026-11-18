"""Modal dialogs."""

import tkinter as tk
from tkinter import ttk

from personal_warehouse.config import LABEL_KINDS, LABEL_SIZES, LAYOUTS
from personal_warehouse.i18n import tr
from personal_warehouse.ui.theme import C, fnt
from personal_warehouse.ui.widgets import btn, lbl


class LabelDialog(tk.Toplevel):
    def __init__(self, master, count, rtl):
        super().__init__(master)
        self.title(tr("lbl_title_msg"))
        self.configure(bg=C["card"])
        self.resizable(False, False)
        self.transient(master)
        self.result = None
        a1 = "e" if rtl else "w"
        just = "right" if rtl else "left"
        self.layout_v = tk.StringVar(value=tr("layout_a4"))
        self.size_v = tk.StringVar(value="Medium 70×40 mm")
        self.kind_v = tk.StringVar(value=tr("kind_qr"))
        self.copies_v = tk.StringVar(value="1")
        self.full_v = tk.BooleanVar(value=False)
        self.prices_v = tk.BooleanVar(value=False)
        f = tk.Frame(self, bg=C["card"], padx=22, pady=18)
        f.pack()
        lbl(f, tr("lbl_dialog", count), 13, True, C["title"], C["card"]).grid(
            row=0, column=0, columnspan=2, sticky=a1, pady=(0, 12))
        rows = [
            (tr("lbl_layout"), ttk.Combobox(f, textvariable=self.layout_v, state="readonly", width=34, justify=just,
                                            values=[tr("layout_" + k) for k in LAYOUTS])),
            (tr("lbl_size"), ttk.Combobox(f, textvariable=self.size_v, state="readonly", width=34, justify=just,
                                          values=list(LABEL_SIZES))),
            (tr("lbl_kind"), ttk.Combobox(f, textvariable=self.kind_v, state="readonly", width=34, justify=just,
                                          values=[tr("kind_" + k) for k in LABEL_KINDS])),
            (tr("lbl_copies"), ttk.Spinbox(f, from_=1, to=50, textvariable=self.copies_v, width=8, justify=just))]
<<<<<<< HEAD
        lc, wc = (1, 0) if rtl else (0, 1)                      # label at the start side
        for i, (text, widget) in enumerate(rows, 1):
            lbl(f, text, 10, False, C["ink"], C["card"]).grid(row=i, column=lc, sticky=a1, pady=6)
            widget.grid(row=i, column=wc, sticky=a1, padx=12)
=======
        for i, (text, widget) in enumerate(rows, 1):
            lbl(f, text, 10, False, C["ink"], C["card"]).grid(row=i, column=0, sticky=a1, pady=6)
            widget.grid(row=i, column=1, sticky=a1, padx=12)
>>>>>>> c8a133662267867832f0d0679ec8832dee7dfdbb
        for i, (text, var) in enumerate([(tr("lbl_full"), self.full_v), (tr("lbl_prices"), self.prices_v)], 5):
            tk.Checkbutton(f, text=text, variable=var, bg=C["card"], fg=C["ink"], activebackground=C["card"],
                           activeforeground=C["ink"], selectcolor=C["input"], font=fnt(10),
                           anchor=a1).grid(row=i, column=0, columnspan=2, sticky=a1, pady=2)
        lbl(f, tr("lbl_hint"), 9, False, C["muted"], C["card"], wraplength=430, justify=just).grid(
            row=7, column=0, columnspan=2, sticky=a1, pady=(8, 14))
        b = tk.Frame(f, bg=C["card"])
        b.grid(row=8, column=0, columnspan=2, sticky="w" if rtl else "e")
        btn(b, tr("lbl_open"), self._ok, "primary").pack(side="left" if rtl else "right")
        btn(b, tr("btn_cancel"), self.destroy, "soft").pack(side="left" if rtl else "right", padx=8)
        self.grab_set()

    def _ok(self):
        try:
            copies = max(1, min(50, int(self.copies_v.get())))
        except ValueError:
            copies = 1
        layout = next((k for k in LAYOUTS if tr("layout_" + k) == self.layout_v.get()), "a4")
        kind = next((k for k in LABEL_KINDS if tr("kind_" + k) == self.kind_v.get()), "qr")
        self.result = {"layout": layout, "size": self.size_v.get(), "kind": kind, "copies": copies,
                       "full": self.full_v.get(), "prices": self.prices_v.get()}
        self.destroy()
