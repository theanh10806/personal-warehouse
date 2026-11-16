"""Storage map page (8 sections x 3 parts)."""

import tkinter as tk

from personal_warehouse.config import PARTS, SECTIONS
from personal_warehouse.core.database import db
from personal_warehouse.core.formatting import make_location, parse_location, qty_fmt
from personal_warehouse.i18n import tr
from personal_warehouse.ui.theme import C, fnt
from personal_warehouse.ui.widgets import card, lbl


class LocationsPage:
    def _build_locations(self):
        f = self.locations_tab
        self._page_head(f, tr("map_title"), tr("map_sub"))
        grid = tk.Frame(f, bg=C["bg"])
        grid.pack(fill="both", expand=True)
        self.location_buttons = {}
        for i, s in enumerate(SECTIONS):
            c = card(grid, padx=14, pady=12)
            c.grid(row=i // 2, column=i % 2, sticky="nsew", padx=6, pady=6)
            lbl(c, tr("section_big", s), 12, True, C["title"], C["card"], anchor=self.a1).pack(fill="x", pady=(0, 8))
            row = tk.Frame(c, bg=C["card"])
            row.pack(fill="x")
            for p in PARTS:
                code = make_location(s, p)
                b = tk.Button(row, text=code, relief="flat", bd=0, cursor="hand2", font=fnt(10), pady=10,
                              fg=C["ink"], command=lambda c=code: self.open_location(c))
                b.pack(side=self.s1, fill="x", expand=True, padx=3)
                self.location_buttons[code] = b
        for i in range(4):
            grid.rowconfigure(i, weight=1)
        for i in range(2):
            grid.columnconfigure(i, weight=1)

    def open_location(self, code):
        self.loc_filter.set(code)
        self.search_var.set("")
        self.cond_filter.set(tr("all_conditions"))
        self.low_only.set(False)
        self.refresh_inventory()
        self.pages.select(self.inventory_tab)

    def refresh_locations(self):
        if not hasattr(self, "location_buttons"):
            return
        with db() as con:
            stats = {(r["section"], r["part"]): r for r in con.execute(
                "SELECT section,part,COUNT(*) n,SUM(quantity) u FROM items "
                "WHERE is_active=1 GROUP BY section,part")}
        for code, b in self.location_buttons.items():
            s, p = parse_location(code)
            r = stats.get((s, p))
            n, u = (r["n"], r["u"] or 0) if r else (0, 0)
            b.configure(text=tr("loc_cell", code, n, qty_fmt(u)),
                        bg=C["occupied"] if n else C["empty"], activebackground=C["sel"])
