"""Inventory page: filterable item table."""

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

from personal_warehouse.config import CONDITIONS, PARTS, SEARCH_COLS, SECTIONS, SORT_SQL
from personal_warehouse.core.database import db
from personal_warehouse.core.formatting import item_name, make_location, money, parse_location, qty_fmt
from personal_warehouse.i18n import cond_t, from_label, tr, unit_t
from personal_warehouse.ui.theme import C, fnt
from personal_warehouse.ui.widgets import btn, card, lbl, make_tree


class InventoryPage:
    def _build_inventory(self):
        f = self.inventory_tab
        head = self._page_head(f, tr("inv_title"))
        actions = tk.Frame(head, bg=C["bg"])
        actions.pack(side=self.s2, anchor="e")
        btn(actions, tr("btn_export"), self.export_excel, "soft").pack(side=self.s2, padx=(6, 0))
        btn(actions, tr("btn_labels"), self.print_selected_labels, "soft").pack(side=self.s2, padx=(6, 0))
        btn(actions, tr("btn_add_item"), self.new_item, "primary").pack(side=self.s2, padx=(6, 0))

        # Filter toolbar, visually separated from the data grid.
        flt = card(f, padx=14, pady=12)
        flt.pack(fill="x", pady=(0, 12))
        search = tk.Frame(flt, bg=C["card"])
        search.pack(fill="x")
        lbl(search, tr("lbl_search"), 9, True, C["muted"], C["card"]).pack(side=self.s1, padx=(0, 8))
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(search, textvariable=self.search_var, width=22, justify=self.just)
        self.search_entry.pack(side=self.s1, padx=(0, 6), ipady=2)
        self.search_var.trace_add("write", lambda *a: self._debounce_search())
        btn(search, "✕", lambda: self.search_var.set(""), "ghost", padx=9, pady=6).pack(side=self.s1, padx=(0, 12))
        self.loc_filter = tk.StringVar(value=tr("all_locations"))
        loc_values = [tr("all_locations")] + [tr("section_n", s) for s in SECTIONS] + \
                     [make_location(s, p) for s in SECTIONS for p in PARTS]
        cb = ttk.Combobox(search, textvariable=self.loc_filter, state="readonly", width=13, values=loc_values,
                          justify=self.just)
        cb.pack(side=self.s1, padx=5)
        self.cond_filter = tk.StringVar(value=tr("all_conditions"))
        cc = ttk.Combobox(search, textvariable=self.cond_filter, state="readonly", width=13, justify=self.just,
                          values=[tr("all_conditions")] + [cond_t(c) for c in CONDITIONS])
        cc.pack(side=self.s1, padx=5)
        for w in (cb, cc):
            w.bind("<<ComboboxSelected>>", lambda e: self.refresh_inventory())
        self.low_only, self.show_archived = tk.BooleanVar(), tk.BooleanVar()
        flags = tk.Frame(flt, bg=C["card"])
        flags.pack(fill="x", pady=(10, 0))
        for text, var in [(tr("low_only"), self.low_only), (tr("show_archived"), self.show_archived)]:
            tk.Checkbutton(flags, text=text, variable=var, command=self.refresh_inventory, bg=C["card"], fg=C["ink"],
                           activebackground=C["card"], activeforeground=C["ink"], selectcolor=C["input"],
                           font=fnt(9), padx=4).pack(side=self.s1, padx=(0, 12))

        cols = ("code", "name", "category", "engine", "location", "condition", "qty", "buy", "sell")
        self.inv_heads = {"code": tr("h_code"), "name": tr("h_name"), "category": tr("h_category"),
                          "engine": tr("h_engine"), "location": tr("h_location"), "condition": tr("h_condition"),
                          "qty": tr("h_qty"), "buy": tr("h_buy"), "sell": tr("h_sell")}
        widths = {"code": 95, "name": 240, "category": 125, "engine": 160, "location": 80,
                  "condition": 105, "qty": 90, "buy": 95, "sell": 95}
        grid = card(f, padx=8, pady=8)
        grid.pack(fill="both", expand=True)
        wrap, self.inv_tree = make_tree(grid, cols, self.inv_heads, widths,
                                        {"name": "w", "category": "w", "engine": "w"}, self.rtl)
        wrap.pack(fill="both", expand=True)
        for col in cols:
            self.inv_tree.heading(col, command=lambda col=col: self.sort_by(col))
        self.inv_tree.bind("<Double-1>", lambda e: self.edit_selected())
        self.inv_tree.bind("<Return>", lambda e: self.edit_selected())
        self.inv_tree.bind("<Delete>", lambda e: self.archive_selected())

        bottom = tk.Frame(f, bg=C["bg"])
        bottom.pack(fill="x", pady=(10, 0))
        btn(bottom, tr("btn_edit"), self.edit_selected, "primary").pack(side=self.s1, padx=(0, 6))
        btn(bottom, tr("btn_move"), self.move_selected, "soft").pack(side=self.s1, padx=(0, 6))
        btn(bottom, tr("btn_archive"), self.archive_selected, "soft").pack(side=self.s1, padx=(0, 6))
        self.inv_summary = tk.StringVar()
        lbl(bottom, "", 9, False, C["muted"], textvariable=self.inv_summary).pack(side=self.s2)
        self._update_headings()

    def _debounce_search(self):
        if self._search_job:
            self.after_cancel(self._search_job)
        self._search_job = self.after(200, self.refresh_inventory)

    def sort_by(self, col):
        self.sort_desc = (not self.sort_desc) if col == self.sort_col else False
        self.sort_col = col
        self._update_headings()
        self.refresh_inventory()

    def _update_headings(self):
        for c, t in self.inv_heads.items():
            arrow = (" ▼" if self.sort_desc else " ▲") if c == self.sort_col else ""
            self.inv_tree.heading(c, text=t + arrow)

    def refresh_inventory(self):
        if not hasattr(self, "inv_tree"):
            return
        tree = self.inv_tree
        keep = set(tree.selection())
        existing = set(tree.get_children())
        wanted = set()
        sql, args = ["SELECT * FROM items WHERE 1=1"], []
        if not self.show_archived.get():
            sql.append("AND is_active=1")
        for tok in self.search_var.get().split():
            sql.append("AND (" + " OR ".join(f"{c} LIKE ?" for c in SEARCH_COLS) + ")")
            args += [f"%{tok}%"] * len(SEARCH_COLS)
        lf = self.loc_filter.get()
        if lf != tr("all_locations"):
            sec = next((s for s in SECTIONS if tr("section_n", s) == lf), None)
            if sec:
                sql.append("AND section=?")
                args.append(sec)
            elif lf and lf[0] in SECTIONS:
                s, p = parse_location(lf)
                sql.append("AND section=? AND part=?")
                args += [s, p]
        if self.cond_filter.get() != tr("all_conditions"):
            sql.append("AND condition=?")
            args.append(from_label(CONDITIONS, cond_t, self.cond_filter.get()))
        if self.low_only.get():
            sql.append("AND (quantity<=0 OR (min_stock>0 AND quantity<=min_stock))")
        sql.append(f"ORDER BY {SORT_SQL[self.sort_col]} {'DESC' if self.sort_desc else 'ASC'}, name COLLATE NOCASE")
        with db() as con:
            rows = con.execute(" ".join(sql), args).fetchall()
        units = value = 0.0
        for i, r in enumerate(rows):
            tag = ("odd",) if i % 2 else ()
            if not r["is_active"]:
                tag = ("gone",)
            elif r["quantity"] <= 0:
                tag = ("out",)
            elif r["min_stock"] > 0 and r["quantity"] <= r["min_stock"]:
                tag = ("low",)
            if r["is_active"]:
                units += r["quantity"]
                value += r["quantity"] * r["purchase_price"]
            iid = str(r["id"])
            wanted.add(iid)
            values = (r["item_code"], item_name(r), r["category"] or "", r["engine_application"] or "",
                      make_location(r["section"], r["part"]), cond_t(r["condition"]),
                      f'{qty_fmt(r["quantity"])} {unit_t(r["unit"])}',
                      money(r["purchase_price"]), money(r["selling_price"]))
            if iid in existing:
                tree.item(iid, values=values, tags=tag)
            else:
                tree.insert("", "end", iid=iid, tags=tag, values=values)
        stale = existing - wanted
        if stale:
            tree.delete(*stale)
        for iid in keep:
            if tree.exists(iid):
                tree.selection_add(iid)
        self.inv_summary.set(tr("inv_summary", len(rows), qty_fmt(units), money(value)))

    def sel_id(self):
        sel = self.inv_tree.selection()
        if not sel:
            messagebox.showinfo(tr("sel_title"), tr("sel_msg"))
            return None
        return int(sel[0])

    def edit_selected(self):
        iid = self.sel_id()
        if iid:
            self.edit_item(iid)

    def move_selected(self):
        iid = self.sel_id()
        if iid:
            self.go_movement(iid)

    def archive_selected(self):
        iid = self.sel_id()
        if not iid:
            return
        with db() as con:
            r = con.execute("SELECT name,is_active FROM items WHERE id=?", (iid,)).fetchone()
            if r["is_active"]:
                if not messagebox.askyesno(tr("archive_title"), tr("archive_confirm", r["name"])):
                    return
                con.execute("UPDATE items SET is_active=0,updated_at=CURRENT_TIMESTAMP WHERE id=?", (iid,))
                msg = tr("archived")
            else:
                con.execute("UPDATE items SET is_active=1,updated_at=CURRENT_TIMESTAMP WHERE id=?", (iid,))
                msg = tr("restored")
        self.refresh_all()
        self.status(f"{msg}: {r['name']}")
