"""Dashboard page: metrics, section chart, alerts, recent activity."""

import tkinter as tk

from personal_warehouse.config import SECTIONS
from personal_warehouse.core.database import db
from personal_warehouse.core.formatting import item_name, make_location, money, qty_fmt
from personal_warehouse.i18n import mv_t, tr
from personal_warehouse.ui.theme import C, fnt
from personal_warehouse.ui.widgets import btn, card, lbl, make_tree


class DashboardPage:
    def _build_dashboard(self):
        f = self.dashboard_tab
        self._page_head(f, tr("dash_title"), tr("dash_sub"))
        cards = tk.Frame(f, bg=C["bg"])
        cards.pack(fill="x")
        self.metric_vars = {}
        for key, title, color in [("items", "m_items", C["accent"]), ("units", "m_units", C["teal"]),
                                  ("value", "m_value", C["ok"]), ("profit", "m_profit", C["violet"]),
                                  ("alerts", "m_alerts", C["warn"])]:
            c = card(cards)
            c.pack(side=self.s1, fill="x", expand=True, padx=5)
            tk.Frame(c, bg=color, width=5).pack(side=self.s1, fill="y")
            inner = tk.Frame(c, bg=C["card"], padx=16, pady=14)
            inner.pack(side=self.s1, fill="both", expand=True)
            lbl(inner, tr(title), 10, False, C["muted"], C["card"], anchor=self.a1).pack(fill="x")
            self.metric_vars[key] = tk.StringVar(value="—")
            tk.Label(inner, textvariable=self.metric_vars[key], bg=C["card"], fg=C["title"],
                     font=fnt(20, True), anchor=self.a1).pack(fill="x", pady=(6, 0))
        qa = tk.Frame(f, bg=C["bg"])
        qa.pack(fill="x", pady=(14, 0))
        for text, cmd, kind in [(tr("qa_add"), self.new_item, "primary"),
                                (tr("qa_inv"), lambda: self.pages.select(self.inventory_tab), "soft"),
                                (tr("qa_move"), lambda: self.pages.select(self.movement_tab), "soft"),
                                (tr("qa_scan"), lambda: (self.pages.select(self.scan_tab), self.scan_entry.focus_set()), "soft"),
                                (tr("qa_labels"), self.print_selected_labels_from_dashboard, "soft"),
                                (tr("qa_export"), self.export_excel, "soft"),
                                (tr("qa_backup"), self.backup_all, "soft")]:
            btn(qa, text, cmd, kind).pack(side=self.s1, padx=4)
        lower = tk.Frame(f, bg=C["bg"])
        lower.pack(fill="both", expand=True, pady=(14, 0))
        for i in range(3):
            lower.columnconfigure(i, weight=1, uniform="dash")
        lower.rowconfigure(0, weight=1)

        def panel(col, title):
            c = card(lower, padx=14, pady=12)
            c.grid(row=0, column=col, sticky="nsew", padx=5)
            lbl(c, title, 10, True, C["title"], C["card"], anchor=self.a1).pack(fill="x", pady=(0, 8))
            return c

        left = panel(0, tr("card_sections"))
        self.section_canvas = tk.Canvas(left, bg=C["card"], highlightthickness=0, height=260)
        self.section_canvas.pack(fill="both", expand=True)
        self.section_canvas.bind("<Configure>", lambda e: self._draw_sections())
        mid = panel(1, tr("card_alerts"))
        w, self.alert_tree = make_tree(
            mid, ("name", "loc", "qty", "min"),
            {"name": tr("col_item"), "loc": tr("col_loc"), "qty": tr("col_qty"), "min": tr("col_min")},
            {"name": 170, "loc": 60, "qty": 55, "min": 60}, {"name": "w"}, self.rtl, height=9)
        w.pack(fill="both", expand=True)
        self.alert_tree.bind("<Double-1>", lambda e: self._open_from_tree(self.alert_tree))
        right = panel(2, tr("card_recent"))
        w, self.recent_tree = make_tree(
            right, ("time", "name", "type", "qty"),
            {"time": tr("col_time"), "name": tr("col_item"), "type": tr("col_type"), "qty": tr("col_qty")},
            {"time": 105, "name": 140, "type": 80, "qty": 55}, {"name": "w"}, self.rtl, height=9)
        w.pack(fill="both", expand=True)

    def print_selected_labels_from_dashboard(self):
        self.pages.select(self.inventory_tab)
        self.print_selected_labels()

    def _open_from_tree(self, tree):
        sel = tree.selection()
        if sel and sel[0].isdigit():
            self.edit_item(int(sel[0]))

    def _draw_sections(self):
        cv = self.section_canvas
        cv.delete("all")
        W = max(cv.winfo_width(), 320)
        rowh = 31
        maxu = max([u for _, u in self._sect_data.values()] + [1])
        track = W - 36 - 110

        def px(x):
            return W - x if self.rtl else x
        for i, s in enumerate(SECTIONS):
            n, u = self._sect_data.get(s, (0, 0))
            y = 6 + i * rowh
            cv.create_text(px(8), y + 13, text=s, anchor=self.a1, fill=C["title"], font=fnt(12, True))
            cv.create_rectangle(px(36), y + 4, px(36 + track), y + 22, fill=C["head"], outline="")
            bw = max(4, track * u / maxu) if u else 0
            if bw:
                cv.create_rectangle(px(36), y + 4, px(36 + bw), y + 22, fill=C["accent"], outline="")
            cv.create_text(px(36 + track + 8), y + 13, anchor=self.a1, fill=C["muted"], font=fnt(9),
                           text=f"{n} • {qty_fmt(u)}")

    def refresh_dashboard(self):
        with db() as con:
            r = con.execute("""SELECT COUNT(*) n, COALESCE(SUM(quantity),0) units,
                COALESCE(SUM(quantity*purchase_price),0) value,
                COALESCE(SUM(quantity*(selling_price-purchase_price)),0) profit
                FROM items WHERE is_active=1""").fetchone()
            alerts = con.execute("""SELECT id,name,name_ar,section,part,quantity,min_stock
                FROM items WHERE is_active=1
                AND (quantity<=0 OR (min_stock>0 AND quantity<=min_stock))
                ORDER BY quantity,name LIMIT 100""").fetchall()
            sect = {x["section"]: (x["n"], x["u"]) for x in con.execute(
                "SELECT section,COUNT(*) n,COALESCE(SUM(quantity),0) u "
                "FROM items WHERE is_active=1 GROUP BY section")}
            recent = con.execute("""SELECT m.movement_date,m.movement_type,m.quantity,i.name,i.name_ar
                FROM movements m JOIN items i ON i.id=m.item_id ORDER BY m.id DESC LIMIT 30""").fetchall()
        self.metric_vars["items"].set(str(r["n"]))
        self.metric_vars["units"].set(qty_fmt(r["units"]))
        self.metric_vars["value"].set(money(r["value"]))
        self.metric_vars["profit"].set(money(r["profit"]))
        self.metric_vars["alerts"].set(str(len(alerts)))
        self._sect_data = sect
        self._draw_sections()
        self.alert_tree.delete(*self.alert_tree.get_children())
        for a in alerts:
            self.alert_tree.insert(
                "", "end", iid=str(a["id"]),
                tags=("out",) if a["quantity"] <= 0 else ("low",),
                values=(item_name(a), make_location(a["section"], a["part"]),
                        qty_fmt(a["quantity"]), qty_fmt(a["min_stock"])))
        self.recent_tree.delete(*self.recent_tree.get_children())
        for i, m in enumerate(recent):
            self.recent_tree.insert("", "end", tags=("odd",) if i % 2 else (), values=(
                m["movement_date"][5:16], item_name(m), mv_t(m["movement_type"]), qty_fmt(m["quantity"])))
