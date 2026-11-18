"""Inventory page: filterable item table."""

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

from personal_warehouse.config import CONDITIONS, PARTS, SEARCH_COLS, SECTIONS, SORT_SQL
from personal_warehouse.core.database import db
from personal_warehouse.core.formatting import item_name, make_location, money, parse_location, qty_fmt
from personal_warehouse.i18n import cond_t, from_label, tr, unit_t
<<<<<<< HEAD
from personal_warehouse.ui.theme import C, fnt, px
from personal_warehouse.ui.widgets import Flow, btn, card, lbl, make_tree
=======
from personal_warehouse.ui.theme import C, fnt
from personal_warehouse.ui.widgets import btn, card, lbl, make_tree
>>>>>>> c8a133662267867832f0d0679ec8832dee7dfdbb


class InventoryPage:
    def _build_inventory(self):
        f = self.inventory_tab
<<<<<<< HEAD
        head = self._page_head(f, tr("inv_title"))
        actions = head.actions
        btn(actions, tr("btn_add_item"), self.new_item, "primary").pack(side=self.s2, padx=self.pad(6, 0))
        btn(actions, tr("btn_labels"), self.print_selected_labels, "soft").pack(side=self.s2, padx=self.pad(6, 0))
        btn(actions, tr("btn_export"), self.export_excel, "soft").pack(side=self.s2, padx=self.pad(6, 0))

        # Filter toolbar, visually separated from the data grid.
        flt = card(f, padx=14, pady=12)
        flt.pack(fill="x", pady=(0, 12))
        # three filter cells that re-flow (one row -> two -> stacked) as the window narrows
        row = Flow(flt, self.rtl, [(px(820), 3), (px(520), 2)], weights=(3, 1, 1), gap=6, bg=C["card"])
        row.frame.pack(fill="x")
        search = tk.Frame(row.frame, bg=C["card"])
        lbl(search, tr("lbl_search"), 9, True, C["muted"], C["card"]).pack(side=self.s1, padx=self.pad(0, 8))
        self.search_var = tk.StringVar()
        btn(search, "✕", lambda: self.search_var.set(""), "ghost", padx=9, pady=6).pack(side=self.s2)
        self.search_entry = ttk.Entry(search, textvariable=self.search_var, width=8, justify=self.just)
        self.search_entry.pack(side=self.s1, fill="x", expand=True, ipady=2)
        self.search_var.trace_add("write", lambda *a: self._debounce_search())
        self.loc_filter = tk.StringVar(value=tr("all_locations"))
        loc_values = [tr("all_locations")] + [tr("section_n", s) for s in SECTIONS] + \
                     [make_location(s, p) for s in SECTIONS for p in PARTS]
        cb = ttk.Combobox(row.frame, textvariable=self.loc_filter, state="readonly", width=8, values=loc_values,
                          justify=self.just)
        self.cond_filter = tk.StringVar(value=tr("all_conditions"))
        cc = ttk.Combobox(row.frame, textvariable=self.cond_filter, state="readonly", width=8, justify=self.just,
                          values=[tr("all_conditions")] + [cond_t(c) for c in CONDITIONS])
        for cell in (search, cb, cc):
            row.add(cell)
        for w in (cb, cc):
            w.bind("<<ComboboxSelected>>", lambda e: self.refresh_inventory())
        self.low_only, self.show_archived = tk.BooleanVar(), tk.BooleanVar()
        flags = tk.Frame(flt, bg=C["card"])
        flags.pack(fill="x", pady=(10, 0))
        for text, var in [(tr("low_only"), self.low_only), (tr("show_archived"), self.show_archived)]:
            tk.Checkbutton(flags, text=text, variable=var, command=self.refresh_inventory, bg=C["card"], fg=C["ink"],
                           activebackground=C["card"], activeforeground=C["ink"], selectcolor=C["input"],
                           font=fnt(9), padx=4).pack(side=self.s1, padx=(0, 12))
=======
        top = tk.Frame(f, bg=C["bg"])
        top.pack(fill="x", pady=(0, 12))
        lbl(top, tr("inv_title"), 22, True, C["title"]).pack(side=self.s1)
        btn(top, tr("btn_export"), self.export_excel, "soft").pack(side=self.s2, padx=4)
        btn(top, tr("btn_labels"), self.print_selected_labels, "soft").pack(side=self.s2, padx=4)
        btn(top, tr("btn_add_item"), self.new_item, "primary").pack(side=self.s2, padx=4)

        flt = card(f, padx=12, pady=10)
        flt.pack(fill="x", pady=(0, 10))
        lbl(flt, tr("lbl_search"), 10, False, C["muted"], C["card"]).pack(side=self.s1)
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(flt, textvariable=self.search_var, width=32, justify=self.just)
        self.search_entry.pack(side=self.s1, padx=6)
        self.search_var.trace_add("write", lambda *a: self._debounce_search())
        btn(flt, "✕", lambda: self.search_var.set(""), "soft", padx=8, pady=4).pack(side=self.s1)
        self.loc_filter = tk.StringVar(value=tr("all_locations"))
        loc_values = [tr("all_locations")] + [tr("section_n", s) for s in SECTIONS] + \
                     [make_location(s, p) for s in SECTIONS for p in PARTS]
        cb = ttk.Combobox(flt, textvariable=self.loc_filter, state="readonly", width=16, values=loc_values,
                          justify=self.just)
        cb.pack(side=self.s1, padx=8)
        self.cond_filter = tk.StringVar(value=tr("all_conditions"))
        cc = ttk.Combobox(flt, textvariable=self.cond_filter, state="readonly", width=18, justify=self.just,
                          values=[tr("all_conditions")] + [cond_t(c) for c in CONDITIONS])
        cc.pack(side=self.s1)
        for w in (cb, cc):
            w.bind("<<ComboboxSelected>>", lambda e: self.refresh_inventory())
        self.low_only, self.show_archived = tk.BooleanVar(), tk.BooleanVar()
        for text, var in [(tr("low_only"), self.low_only), (tr("show_archived"), self.show_archived)]:
            tk.Checkbutton(flt, text=text, variable=var, command=self.refresh_inventory, bg=C["card"], fg=C["ink"],
                           activebackground=C["card"], activeforeground=C["ink"], selectcolor=C["input"],
                           font=fnt(10)).pack(side=self.s1, padx=8)
>>>>>>> c8a133662267867832f0d0679ec8832dee7dfdbb

        cols = ("code", "name", "category", "engine", "location", "condition", "qty", "buy", "sell")
        self.inv_heads = {"code": tr("h_code"), "name": tr("h_name"), "category": tr("h_category"),
                          "engine": tr("h_engine"), "location": tr("h_location"), "condition": tr("h_condition"),
                          "qty": tr("h_qty"), "buy": tr("h_buy"), "sell": tr("h_sell")}
        widths = {"code": 95, "name": 240, "category": 125, "engine": 160, "location": 80,
                  "condition": 105, "qty": 90, "buy": 95, "sell": 95}
<<<<<<< HEAD
        grid = card(f, padx=8, pady=8)
        grid.pack(fill="both", expand=True)
        wrap, self.inv_tree = make_tree(grid, cols, self.inv_heads, widths,
                                        {"name": "w", "category": "w", "engine": "w"}, self.rtl, height=12)
        wrap.pack(fill="both", expand=True)
        for col in cols:
            self.inv_tree.heading(col, command=lambda col=col: self.sort_by(col))
=======
        wrap, self.inv_tree = make_tree(f, cols, self.inv_heads, widths,
                                        {"name": "w", "category": "w", "engine": "w"}, self.rtl)
        wrap.pack(fill="both", expand=True)
        for c in cols:
            self.inv_tree.heading(c, command=lambda c=c: self.sort_by(c))
>>>>>>> c8a133662267867832f0d0679ec8832dee7dfdbb
        self.inv_tree.bind("<Double-1>", lambda e: self.edit_selected())
        self.inv_tree.bind("<Return>", lambda e: self.edit_selected())
        self.inv_tree.bind("<Delete>", lambda e: self.archive_selected())

        bottom = tk.Frame(f, bg=C["bg"])
        bottom.pack(fill="x", pady=(10, 0))
<<<<<<< HEAD
        self.inv_summary = tk.StringVar()
        summary = lbl(bottom, "", 9, False, C["muted"], textvariable=self.inv_summary, anchor=self.a1,
                      justify=self.just)
        summary.pack(fill="x", pady=(0, 6))
        bottom.bind("<Configure>", lambda e: summary.configure(wraplength=max(px(160), bottom.winfo_width() - px(8)))
                    if isinstance(bottom.winfo_width(), (int, float)) and bottom.winfo_width() > 1 else None, add="+")
        buttons = tk.Frame(bottom, bg=C["bg"])
        buttons.pack(fill="x")
        btn(buttons, tr("btn_edit"), self.edit_selected, "primary").pack(side=self.s1, padx=self.pad(0, 6))
        btn(buttons, tr("btn_move"), self.move_selected, "soft").pack(side=self.s1, padx=self.pad(0, 6))
        btn(buttons, tr("btn_archive"), self.archive_selected, "soft").pack(side=self.s1, padx=self.pad(0, 6))
=======
        btn(bottom, tr("btn_edit"), self.edit_selected, "primary").pack(side=self.s1, padx=(0, 6))
        btn(bottom, tr("btn_move"), self.move_selected, "soft").pack(side=self.s1, padx=(0, 6))
        btn(bottom, tr("btn_archive"), self.archive_selected, "soft").pack(side=self.s1, padx=(0, 6))
        self.inv_summary = tk.StringVar()
        lbl(bottom, "", 10, False, C["muted"], textvariable=self.inv_summary).pack(side=self.s2)
>>>>>>> c8a133662267867832f0d0679ec8832dee7dfdbb
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
<<<<<<< HEAD
        existing = set(tree.get_children())
        wanted = set()
=======
        tree.delete(*tree.get_children())
>>>>>>> c8a133662267867832f0d0679ec8832dee7dfdbb
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
<<<<<<< HEAD
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
=======
            tree.insert("", "end", iid=str(r["id"]), tags=tag, values=(
                r["item_code"], item_name(r), r["category"] or "", r["engine_application"] or "",
                make_location(r["section"], r["part"]), cond_t(r["condition"]),
                f'{qty_fmt(r["quantity"])} {unit_t(r["unit"])}',
                money(r["purchase_price"]), money(r["selling_price"])))
            if r["is_active"]:
                units += r["quantity"]
                value += r["quantity"] * r["purchase_price"]
>>>>>>> c8a133662267867832f0d0679ec8832dee7dfdbb
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
