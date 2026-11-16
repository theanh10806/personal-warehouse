"""Stock in / out / adjustment page and movement history."""

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

from personal_warehouse.config import MOVE_TYPES
from personal_warehouse.core.database import db
from personal_warehouse.core.formatting import item_name, make_location, money, num, qty_fmt
from personal_warehouse.core.stock import apply_movement
from personal_warehouse.i18n import from_label, mv_t, tr, unit_t
from personal_warehouse.ui.theme import C, fnt
from personal_warehouse.ui.widgets import btn, card, lbl, make_tree


class MovementsPage:
    def _build_movements(self):
        f = self.movement_tab
        self._page_head(f, tr("mv_title"), tr("mv_sub"))
        form = card(f, padx=16, pady=14)
        form.pack(fill="x")
        self.mov_item, self.mov_type = tk.StringVar(), tk.StringVar(value=mv_t("Stock In"))
        self.mov_qty, self.mov_price, self.mov_reason = tk.StringVar(), tk.StringVar(), tk.StringVar()
        self.mov_info = tk.StringVar(value=tr("mv_pick"))
        self.mov_qty_label = tk.StringVar(value=tr("mv_qty"))
        heads = [(tr("mv_item"), None), (tr("mv_type"), None), (None, self.mov_qty_label),
                 (tr("mv_price"), None), (tr("mv_reason"), None)]
        labels = []
        for text, var in heads:
            w = tk.Label(form, text=text or "", textvariable=var, bg=C["card"], fg=C["muted"],
                         font=fnt(10), anchor=self.a1)
            labels.append(w)
        self.mov_item_cb = ttk.Combobox(form, textvariable=self.mov_item, width=32, justify=self.just)
        self.mov_item_cb.bind("<KeyRelease>", self._filter_items)
        self.mov_item_cb.bind("<<ComboboxSelected>>", lambda e: self._on_item_picked())
        tcb = ttk.Combobox(form, textvariable=self.mov_type, values=[mv_t(m) for m in MOVE_TYPES],
                           state="readonly", width=12, justify=self.just)
        tcb.bind("<<ComboboxSelected>>", lambda e: self._on_item_picked())
        self.mov_qty_entry = ttk.Entry(form, textvariable=self.mov_qty, width=10, justify=self.just)
        self.mov_qty_entry.bind("<Return>", lambda e: self.save_movement())
        price_entry = ttk.Entry(form, textvariable=self.mov_price, width=11, justify=self.just)
        reason_entry = ttk.Entry(form, textvariable=self.mov_reason, width=20, justify=self.just)
        reason_entry.bind("<Return>", lambda ev: self.save_movement())
        save_btn = btn(form, tr("mv_save"), self.save_movement, "success")
        self._movement_form_widgets = [self.mov_item_cb, tcb, self.mov_qty_entry, price_entry, reason_entry, save_btn]
        self._movement_form_labels = labels
        self._movement_form = form
        self._movement_compact = None
        self.mov_info_label = tk.Label(form, textvariable=self.mov_info, bg=C["card"], fg=C["muted"],
                                        font=fnt(10), anchor=self.a1)
        form.bind("<Configure>", self._adapt_movement_form, add="+")
        self._adapt_movement_form()
        opts = tk.Frame(f, bg=C["bg"])
        opts.pack(fill="x", pady=(14, 8))
        lbl(opts, tr("mv_history"), 12, True, C["title"]).pack(side=self.s1)
        self.mov_only_item = tk.BooleanVar()
        tk.Checkbutton(opts, text=tr("mv_only"), variable=self.mov_only_item, command=self.refresh_movements,
                       bg=C["bg"], fg=C["ink"], activebackground=C["bg"], activeforeground=C["ink"],
                       selectcolor=C["input"], font=fnt(10)).pack(side=self.s1, padx=16)
        cols = ("date", "code", "name", "type", "qty", "change", "price", "reason")
        heads = {"date": tr("h_date"), "code": tr("h_code"), "name": tr("col_item"), "type": tr("h_move"),
                 "qty": tr("h_qty"), "change": tr("h_change"), "price": tr("h_price"), "reason": tr("h_reason")}
        widths = {"date": 140, "code": 90, "name": 210, "type": 100, "qty": 80,
                  "change": 150, "price": 90, "reason": 260}
        wrap, self.mov_tree = make_tree(f, cols, heads, widths, {"name": "w", "reason": "w"}, self.rtl)
        wrap.pack(fill="both", expand=True)

    def _adapt_movement_form(self, event=None):
        if not hasattr(self, "_movement_form"):
            return
        compact = self._movement_form.winfo_width() < 980
        if compact == self._movement_compact:
            return
        self._movement_compact = compact
        if compact:
            for i, (label, widget) in enumerate(zip(self._movement_form_labels, self._movement_form_widgets)):
                label.grid(row=i * 2, column=0, columnspan=2, sticky=self.a1, padx=6, pady=(5, 0))
                widget.grid(row=i * 2 + 1, column=0, columnspan=2, sticky="ew", padx=6, pady=(1, 4))
            self.mov_info_label.grid(row=10, column=0, columnspan=2, sticky=self.a1, padx=6, pady=(8, 0))
            self._movement_form.columnconfigure(0, weight=1)
            self._movement_form.columnconfigure(1, weight=0)
        else:
            for i, (label, widget) in enumerate(zip(self._movement_form_labels, self._movement_form_widgets)):
                label.grid(row=0, column=i, columnspan=1, sticky=self.a1, padx=6)
                widget.grid(row=1, column=i, columnspan=1, sticky="ew", padx=6, pady=4)
            self.mov_info_label.grid(row=2, column=0, columnspan=6, sticky=self.a1, padx=6, pady=(8, 0))
            for i, weight in enumerate((4, 1, 1, 1, 2, 0)):
                self._movement_form.columnconfigure(i, weight=weight)

    def _filter_items(self, ev):
        if ev.keysym in ("Up", "Down", "Left", "Right", "Tab", "Escape", "Shift_L", "Shift_R"):
            return
        toks = self.mov_item.get().lower().split()
        matches = [l for l in self._all_labels if all(t in l.lower() for t in toks)][:200]
        self.mov_item_cb["values"] = matches
        if ev.keysym == "Return" and matches and self.mov_item.get() not in self.item_choice_map:
            self.mov_item.set(matches[0])
        if self.mov_item.get() in self.item_choice_map:
            self._on_item_picked()

    def _mov_type_key(self):
        return from_label(MOVE_TYPES, mv_t, self.mov_type.get())

    def _on_item_picked(self):
        t = self._mov_type_key()
        self.mov_qty_label.set(tr("mv_counted") if t == "Adjustment" else tr("mv_qty"))
        iid = self.item_choice_map.get(self.mov_item.get())
        if not iid:
            self.mov_info.set(tr("mv_pick2"))
            return
        with db() as con:
            r = con.execute("SELECT * FROM items WHERE id=?", (iid,)).fetchone()
        low = tr("mv_low", qty_fmt(r["min_stock"])) if r["min_stock"] > 0 and r["quantity"] <= r["min_stock"] else ""
        self.mov_info.set(tr("mv_info", qty_fmt(r["quantity"]), unit_t(r["unit"]),
                             make_location(r["section"], r["part"]), money(r["purchase_price"]),
                             money(r["selling_price"]), low))
        self.mov_price.set(f"{r['purchase_price']:.2f}" if t == "Stock In"
                           else f"{r['selling_price']:.2f}" if t == "Stock Out" else "")
        if self.mov_only_item.get():
            self.refresh_movements()

    def go_movement(self, item_id):
        for label, iid in self.item_choice_map.items():
            if iid == item_id:
                self.mov_item.set(label)
                break
        self.mov_qty.set("")
        self._on_item_picked()
        self.pages.select(self.movement_tab)
        self.mov_qty_entry.focus_set()

    def save_movement(self):
        iid = self.item_choice_map.get(self.mov_item.get())
        if not iid:
            messagebox.showerror(tr("nav_move"), tr("err_pick_item"))
            return
        typ = self._mov_type_key()
        try:
            q = num(self.mov_qty.get(), tr("mv_qty"))
            price = round(num(self.mov_price.get(), tr("mv_price")), 2) if self.mov_price.get().strip() else None
        except ValueError as e:
            messagebox.showerror(tr("err_number_title"), str(e))
            return
        if typ != "Adjustment" and q <= 0:
            messagebox.showerror(tr("nav_move"), tr("err_qty"))
            return
        try:
            r, before, after = apply_movement(iid, typ, q, price, self.mov_reason.get().strip())
        except ValueError as e:
            messagebox.showinfo(tr("info_title"), str(e))
            return
        self.mov_qty.set("")
        self.mov_reason.set("")
        self.refresh_all()
        self._on_item_picked()
        warn = tr("mv_warn") if r["min_stock"] > 0 and after <= r["min_stock"] else ""
        self.status(tr("mv_done", mv_t(typ), item_name(r), qty_fmt(before), qty_fmt(after), unit_t(r["unit"]), warn))
        self.mov_qty_entry.focus_set()

    def refresh_movements(self):
        if not hasattr(self, "mov_tree"):
            return
        self.mov_tree.delete(*self.mov_tree.get_children())
        sql = "SELECT m.*,i.item_code,i.name,i.name_ar FROM movements m JOIN items i ON i.id=m.item_id"
        args = []
        iid = self.item_choice_map.get(self.mov_item.get())
        if self.mov_only_item.get() and iid:
            sql += " WHERE m.item_id=?"
            args.append(iid)
        with db() as con:
            rows = con.execute(sql + " ORDER BY m.id DESC LIMIT 500", args).fetchall()
        for i, r in enumerate(rows):
            arrow = "←" if self.rtl else "→"
            change = f"{qty_fmt(r['qty_before'])} {arrow} {qty_fmt(r['qty_after'])}" if r["qty_after"] is not None else ""
            self.mov_tree.insert("", "end", tags=("odd",) if i % 2 else (), values=(
                r["movement_date"], r["item_code"], item_name(r), mv_t(r["movement_type"]),
                qty_fmt(r["quantity"]), change,
                money(r["unit_price"]) if r["unit_price"] is not None else "",
                r["reason"] or ""))

    def refresh_movement_choices(self):
        if not hasattr(self, "mov_item_cb"):
            return
        with db() as con:
            rows = con.execute("SELECT id,item_code,name,name_ar,section,part FROM items WHERE is_active=1 "
                               "ORDER BY name COLLATE NOCASE").fetchall()
        self.item_choice_map = {
            f'{r["item_code"]} — {item_name(r)} [{make_location(r["section"], r["part"])}]': r["id"]
            for r in rows}
        self._all_labels = list(self.item_choice_map)
        self.mov_item_cb["values"] = self._all_labels[:200]
        if self.mov_item.get() not in self.item_choice_map:
            self.mov_item.set("")
            self.mov_info.set(tr("mv_pick"))
