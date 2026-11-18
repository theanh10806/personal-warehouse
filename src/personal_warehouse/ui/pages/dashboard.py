<<<<<<< HEAD
"""Dashboard page: KPI cards, stock in/out trend, smart insights, sections, alerts and recent activity.

Everything re-flows with the window (see widgets.Flow) and the page scrolls when it is too small."""

import tkinter as tk
from datetime import date, timedelta
=======
"""Dashboard page: metrics, section chart, alerts, recent activity."""

import tkinter as tk
>>>>>>> c8a133662267867832f0d0679ec8832dee7dfdbb

from personal_warehouse.config import SECTIONS
from personal_warehouse.core.database import db
from personal_warehouse.core.formatting import item_name, make_location, money, qty_fmt
from personal_warehouse.i18n import mv_t, tr
<<<<<<< HEAD
from personal_warehouse.ui.theme import C, TS, fnt, px
from personal_warehouse.ui.widgets import Flow, badge, btn, card, chip, debounce, lbl, make_tree, pulse
=======
from personal_warehouse.ui.theme import C, fnt
from personal_warehouse.ui.widgets import btn, card, lbl, make_tree
>>>>>>> c8a133662267867832f0d0679ec8832dee7dfdbb


class DashboardPage:
    def _build_dashboard(self):
        f = self.dashboard_tab
<<<<<<< HEAD
        head = self._page_head(f, tr("dash_title"), tr("dash_sub"))
        act = head.actions
        more = tk.Menu(self, tearoff=0)
        for key, cmd in (("qa_labels", self.print_selected_labels_from_dashboard), ("qa_export", self.export_excel),
                         ("qa_backup", self.backup_all)):
            more.add_command(label=tr(key), command=cmd)
        more_btn = btn(act, "⋯", lambda: more.tk_popup(more_btn.winfo_rootx(),
                                                       more_btn.winfo_rooty() + more_btn.winfo_height()),
                       "soft", padx=12, pady=6)
        more_btn.pack(side=self.s2, padx=self.pad(6, 0))
        btn(act, tr("qa_move"), lambda: self.pages.select(self.movement_tab), "soft", padx=12, pady=6).pack(
            side=self.s2, padx=self.pad(6, 0))
        btn(act, tr("qa_scan"), lambda: (self.pages.select(self.scan_tab), self.scan_entry.focus_set()),
            "soft", padx=12, pady=6).pack(side=self.s2, padx=self.pad(6, 0))

        # 1) KPI cards: 4 across -> 2 x 2 -> stacked
        self.metric_vars, self.sub_vars, self._badges = {}, {}, {}
        self._kpi_value_lbls, self._kpi_last = {}, {}
        kpis = Flow(f, self.rtl, [(px(1000), 4), (px(540), 2)], gap=12)
        kpis.frame.pack(fill="x")
        for key, glyph, tint, color, title in (
                ("items", "▤", C["teal_s"], C["teal"], "m_items"),
                ("units", "▦", C["yellow_s"], C["warn"], "m_units"),
                ("value", "$", C["violet_s"], C["violet"], "m_value"),
                ("alerts", "!", C["accent_s"], C["accent"], "m_alerts")):
            kpis.add(self._kpi_card(kpis.frame, key, glyph, tint, color, tr(title)))

        # 2) trend chart + smart insights
        mid = Flow(f, self.rtl, [(px(920), 2)], weights=(3, 2), gap=12)
        mid.frame.pack(fill="both", expand=True, pady=(px(4), 0))
        trend = self._panel(mid.frame, tr("card_trend"), legend=True)
        self.trend_canvas = tk.Canvas(trend, bg=C["card"], highlightthickness=0, width=px(120), height=px(230))
        self.trend_canvas.pack(fill="both", expand=True)
        self.trend_canvas.bind("<Configure>", debounce(self.trend_canvas, self._draw_trend))
        ins = self._panel(mid.frame, tr("card_insights"), sub=tr("ins_sub"))
        self.insight_box = tk.Frame(ins, bg=C["card"])
        self.insight_box.pack(fill="both", expand=True)
        self.insight_box.bind("<Configure>", self._wrap_insights, add="+")
        mid.add(trend)
        mid.add(ins)

        # 3) sections / alerts / recent activity: 3 across -> 2 -> 1
        low = Flow(f, self.rtl, [(px(1280), 3), (px(880), 2)], weights=(4, 5, 4), gap=12)
        low.frame.pack(fill="both", expand=True, pady=(px(4), 0))
        sections = self._panel(low.frame, tr("card_sections"))
        self.section_canvas = tk.Canvas(sections, bg=C["card"], highlightthickness=0, width=px(120),
                                        height=len(SECTIONS) * px(34) + px(12))
        self.section_canvas.pack(fill="both", expand=True)
        self.section_canvas.bind("<Configure>", debounce(self.section_canvas, self._draw_sections))

        alerts = self._panel(low.frame, tr("card_alerts"),
                             link=(tr("dash_view_all"), self._show_low_stock))
        w, self.alert_tree = make_tree(
            alerts, ("name", "loc", "qty", "min"),
            {"name": tr("col_item"), "loc": tr("col_loc"), "qty": tr("col_qty"), "min": tr("col_min")},
            {"name": 170, "loc": 60, "qty": 55, "min": 70}, {"name": "w"}, self.rtl, height=8)
        w.pack(fill="both", expand=True)
        self.alert_tree.bind("<Double-1>", lambda e: self._open_from_tree(self.alert_tree))

        recent = self._panel(low.frame, tr("card_recent"),
                             link=(tr("dash_view_all"), lambda: self.pages.select(self.movement_tab)))
        w, self.recent_tree = make_tree(
            recent, ("time", "name", "type", "qty"),
            {"time": tr("col_time"), "name": tr("col_item"), "type": tr("col_type"), "qty": tr("col_qty")},
            {"time": 105, "name": 140, "type": 90, "qty": 55}, {"name": "w"}, self.rtl, height=8)
        w.pack(fill="both", expand=True)
        self.recent_tree.tag_configure("min_in", foreground=C["ok"])
        self.recent_tree.tag_configure("min_out", foreground=C["danger"])
        for panel in (sections, alerts, recent):
            low.add(panel)
        self._trend_data, self._insights = [], []

    # ------------------------------------------------------------------ small builders
    def _panel(self, parent, title, sub="", link=None, legend=False, tint=False):
        bg = C["ai"] if tint else C["card"]
        c = card(parent, padx=px(16), pady=px(14))
        c.configure(bg=bg)
        head = tk.Frame(c, bg=bg)
        head.pack(fill="x", pady=(0, px(12)))
        if link:
            a = tk.Label(head, text=link[0] + (" ‹" if self.rtl else " ›"), bg=bg, fg=C["accent"], font=fnt(9, True),
                         cursor="hand2")
            a.pack(side=self.s2)
            a.bind("<Button-1>", lambda e, cmd=link[1]: cmd())
        if legend:
            for text, color in ((tr("legend_out"), C["accent_fill"]), (tr("legend_in"), C["teal_fill"])):
                tk.Label(head, text=text, bg=bg, fg=C["muted"], font=fnt(TS["label"])).pack(
                    side=self.s2, padx=self.pad(0, 4))
                tk.Frame(head, bg=color, width=px(10), height=px(10), highlightthickness=1,
                         highlightbackground=C["ink_line"]).pack(side=self.s2, padx=self.pad(6, 0))
        box = tk.Frame(head, bg=bg)
        box.pack(side=self.s1, fill="x", expand=True)
        lbl(box, title, TS["section"], True, C["title"], bg, anchor=self.a1, justify=self.just).pack(fill="x")
        if sub:
            sl = lbl(box, sub, TS["hint"], False, C["muted"], bg, anchor=self.a1, justify=self.just,
                     wraplength=px(210))
            sl.pack(fill="x")
            box.bind("<Configure>", lambda e: sl.configure(wraplength=max(px(100), box.winfo_width() - px(6)))
                     if isinstance(box.winfo_width(), (int, float)) and box.winfo_width() > 1 else None, add="+")
        return c

    def _kpi_card(self, parent, key, glyph, tint, color, title):
        c = card(parent)
        inner = tk.Frame(c, bg=C["card"], padx=px(17), pady=px(15))
        inner.pack(fill="both", expand=True)
        top = tk.Frame(inner, bg=C["card"])
        top.pack(fill="x")
        chip(top, glyph, tint, color).pack(side=self.s1)
        self._badges[key] = badge(top, "", C["ok_s"], C["ok"])
        self._badges[key].pack_forget()
        self._badges[key]._side = self.s2
        lbl(inner, title, TS["label"], False, C["muted"], C["card"], anchor=self.a1, justify=self.just,
            wraplength=px(220)).pack(fill="x", pady=(px(10), 0))
        self.metric_vars[key] = tk.StringVar(value="—")
        vl = tk.Label(inner, textvariable=self.metric_vars[key], bg=C["card"], fg=color,
                      font=fnt(TS["kpi"], True), anchor=self.a1)
        vl.pack(fill="x", pady=(px(4), 0))
        self._kpi_value_lbls[key] = vl
        self._kpi_color = getattr(self, "_kpi_color", {})
        self._kpi_color[key] = color
        self._kpi_last[key] = "—"
        self.sub_vars[key] = tk.StringVar(value="")
        tk.Label(inner, textvariable=self.sub_vars[key], bg=C["card"], fg=C["muted"], font=fnt(TS["label"]),
                 anchor=self.a1, justify=self.just, wraplength=px(220)).pack(fill="x", pady=(2, 0))
        return c

    def _set_badge(self, key, text, kind="ok"):
        b = self._badges[key]
        if not text:
            b.pack_forget()
            return
        tint, color = {"ok": (C["ok_s"], C["ok"]), "bad": (C["accent_s"], C["accent"]),
                       "flat": (C["head"], C["muted"])}[kind]
        b.configure(text=text, bg=tint, fg=color, highlightbackground=color)
        b.pack(side=b._side)

    def _set_metric(self, key, value):
        """Update a KPI number and, if it moved, briefly tint the label (accent for data, amber for
        alerts) so a refresh reads as a reaction.  First paint is silent."""
        self.metric_vars[key].set(value)
        last = self._kpi_last.get(key)
        if last is not None and last != value:
            pulse(self._kpi_value_lbls[key], C["yellow"], to=self._kpi_color.get(key, C["title"]), steps=10)
        self._kpi_last[key] = value

    def _show_low_stock(self):
        self.pages.select(self.inventory_tab)
        self.low_only.set(True)
        self.refresh_inventory()
=======
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
>>>>>>> c8a133662267867832f0d0679ec8832dee7dfdbb

    def print_selected_labels_from_dashboard(self):
        self.pages.select(self.inventory_tab)
        self.print_selected_labels()

    def _open_from_tree(self, tree):
        sel = tree.selection()
        if sel and sel[0].isdigit():
            self.edit_item(int(sel[0]))

<<<<<<< HEAD
    # ------------------------------------------------------------------ canvases
    def _draw_trend(self):
        cv = self.trend_canvas
        cv.delete("all")
        W, H = max(cv.winfo_width(), px(300)), max(cv.winfo_height(), px(160))
        days = [date.today() - timedelta(days=13 - i) for i in range(14)]
        data = {d: self._trend_data_map.get(d.isoformat(), (0, 0)) for d in days} if hasattr(
            self, "_trend_data_map") else {d: (0, 0) for d in days}
        top = max([max(v) for v in data.values()] + [1])
        step = 1
        while top / step > 5:                             # a tidy axis: 1, 2, 5, 10, 20, 50 ...
            step = step * 2 if str(step)[0] in "15" else step * 5 // 2
        top = step * (-(-top // step))
        ml, mr, mt, mb = px(46), px(12), px(14), px(28)

        def X(x):
            return W - x if self.rtl else x
        plot_w, plot_h = W - ml - mr, H - mt - mb
        for i in range(0, 5):
            v = top * i / 4
            y = mt + plot_h - plot_h * i / 4
            cv.create_line(X(ml), y, X(ml + plot_w), y, fill=C["line"])
            cv.create_text(X(ml - 6), y, text=qty_fmt(v), anchor="w" if self.rtl else "e", fill=C["muted"],
                           font=fnt(8))
        if not any(any(v) for v in data.values()):
            cv.create_text(W // 2, H // 2, text=tr("trend_empty"), fill=C["muted"], font=fnt(10))
            return
        gw = plot_w / 14
        bw = max(px(3), gw * 0.32)
        every = 1 if W >= px(560) else 2
        for i, d in enumerate(days):
            cx = ml + gw * i + gw / 2
            for k, (val, color) in enumerate(zip(data[d], (C["teal_fill"], C["accent_fill"]))):
                if val:
                    x0 = cx - bw - 1 if k == 0 else cx + 1
                    hh = plot_h * val / top
                    cv.create_rectangle(X(x0), mt + plot_h - hh, X(x0 + bw), mt + plot_h, fill=color, outline=C["ink_line"], width=1)
            if i % every == 0 or i == 13:
                cv.create_text(X(cx), H - mb + px(11), text=d.strftime("%d/%m"), fill=C["muted"], font=fnt(8))

    def _draw_sections(self):
        cv = self.section_canvas
        cv.delete("all")
        W = max(cv.winfo_width(), px(260))
        rowh = px(34)
        maxu = max([u for _, u in self._sect_data.values()] + [1])
        label_w = min(px(132), max(px(62), max((len(str(section)) for section in SECTIONS), default=4) * px(8) + px(14)))
        count_w = px(104)
        track = max(W - label_w - count_w - px(18), px(36))

        def X(x):
            return W - x if self.rtl else x
        for i, s in enumerate(SECTIONS):
            n, u = self._sect_data.get(s, (0, 0))
            y = px(6) + i * rowh
            cv.create_text(X(px(6)), y + rowh // 2 - 2, text=s, anchor=self.a1, fill=C["title"], font=fnt(10, True))
            cv.create_rectangle(X(label_w), y + px(8), X(label_w + track), y + px(20), fill=C["head"], outline="")
            bw = max(4, track * u / maxu) if u else 0
            if bw:
                cv.create_rectangle(X(label_w), y + px(8), X(label_w + bw), y + px(20), fill=C["teal_fill"], outline=C["ink_line"])
            cv.create_text(X(label_w + track + px(8)), y + rowh // 2 - 2, anchor=self.a1, fill=C["muted"],
                           font=fnt(9), text=f"{n} • {qty_fmt(u)}")

    # ------------------------------------------------------------------ data
    def refresh_dashboard(self):
        today = date.today()
        since14 = (today - timedelta(days=13)).isoformat()
        since7 = (today - timedelta(days=6)).isoformat()
        since30 = (today - timedelta(days=30)).isoformat()
        since60 = (today - timedelta(days=60)).isoformat()
=======
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
>>>>>>> c8a133662267867832f0d0679ec8832dee7dfdbb
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
<<<<<<< HEAD
            trend = con.execute("""SELECT substr(movement_date,1,10) d, movement_type t, SUM(quantity) q
                FROM movements WHERE movement_type IN ('Stock In','Stock Out') AND substr(movement_date,1,10)>=?
                GROUP BY d,t""", (since14,)).fetchall()
            top = con.execute("""SELECT i.name,i.name_ar,SUM(m.quantity) q FROM movements m
                JOIN items i ON i.id=m.item_id WHERE m.movement_type='Stock Out' AND substr(m.movement_date,1,10)>=?
                GROUP BY m.item_id ORDER BY q DESC LIMIT 1""", (since30,)).fetchone()
            idle = con.execute("""SELECT COUNT(*) FROM items i WHERE i.is_active=1 AND i.quantity>0 AND NOT EXISTS
                (SELECT 1 FROM movements m WHERE m.item_id=i.id AND substr(m.movement_date,1,10)>=?)""",
                               (since60,)).fetchone()[0]
        out_n = sum(1 for a in alerts if a["quantity"] <= 0)
        low_n = len(alerts) - out_n
        net7 = 0.0
        self._trend_data_map = {}
        for t in trend:
            ins, outs = self._trend_data_map.get(t["d"], (0, 0))
            self._trend_data_map[t["d"]] = (ins + t["q"], outs) if t["t"] == "Stock In" else (ins, outs + t["q"])
            if t["d"] >= since7:
                net7 += t["q"] if t["t"] == "Stock In" else -t["q"]

        self._set_metric("items", str(r["n"]))
        self.sub_vars["items"].set(tr("kpi_sections", sum(1 for s in SECTIONS if sect.get(s, (0, 0))[0]),
                                      len(SECTIONS)))
        self._set_metric("units", qty_fmt(r["units"]))
        self.sub_vars["units"].set(tr("kpi_units_sub"))
        self._set_badge("units", tr("kpi_net7", ("▲ " if net7 > 0 else "▼ " if net7 < 0 else "") + qty_fmt(abs(net7))),
                        "ok" if net7 > 0 else "bad" if net7 < 0 else "flat")
        self._set_metric("value", money(r["value"]))
        self.sub_vars["value"].set(tr("kpi_value_sub", money(r["profit"])))
        self._set_metric("alerts", str(len(alerts)))
        self.sub_vars["alerts"].set(tr("kpi_alert_sub", out_n, low_n))
        self._set_badge("alerts", tr("kpi_attention") if out_n else "", "bad")

        self._sect_data = sect
        self._draw_sections()
        self._draw_trend()
        self._fill_insights(alerts, out_n, low_n, top, idle)
=======
        self.metric_vars["items"].set(str(r["n"]))
        self.metric_vars["units"].set(qty_fmt(r["units"]))
        self.metric_vars["value"].set(money(r["value"]))
        self.metric_vars["profit"].set(money(r["profit"]))
        self.metric_vars["alerts"].set(str(len(alerts)))
        self._sect_data = sect
        self._draw_sections()
>>>>>>> c8a133662267867832f0d0679ec8832dee7dfdbb
        self.alert_tree.delete(*self.alert_tree.get_children())
        for a in alerts:
            self.alert_tree.insert(
                "", "end", iid=str(a["id"]),
                tags=("out",) if a["quantity"] <= 0 else ("low",),
                values=(item_name(a), make_location(a["section"], a["part"]),
                        qty_fmt(a["quantity"]), qty_fmt(a["min_stock"])))
        self.recent_tree.delete(*self.recent_tree.get_children())
        for i, m in enumerate(recent):
<<<<<<< HEAD
            tags = ["odd"] if i % 2 else []
            tags.append("min_in" if m["movement_type"] == "Stock In" else
                        "min_out" if m["movement_type"] == "Stock Out" else "")
            self.recent_tree.insert("", "end", tags=tuple(t for t in tags if t), values=(
                m["movement_date"][5:16], item_name(m), mv_t(m["movement_type"]), qty_fmt(m["quantity"])))

    def _fill_insights(self, alerts, out_n, low_n, top, idle):
        """Rule-based tips computed from the local database (no network, no AI service)."""
        rows = []
        names = lambda rs, n=3: ", ".join(item_name(a) for a in rs[:n]) + (" …" if len(rs) > n else "")
        outs = [a for a in alerts if a["quantity"] <= 0]
        lows = [a for a in alerts if a["quantity"] > 0]
        if outs:
            rows.append(("!", C["accent_s"], C["accent"], tr("ins_out", out_n, names(outs))))
        if lows:
            rows.append(("↻", C["yellow_s"], C["warn"], tr("ins_low", low_n, names(lows))))
        if top and top["q"]:
            rows.append(("↗", C["teal_s"], C["teal"], tr("ins_top", item_name(top), qty_fmt(top["q"]))))
        if idle:
            rows.append(("◷", C["violet_s"], C["violet"], tr("ins_idle", idle)))
        if not rows:
            rows.append(("✓", C["ok_s"], C["ok"], tr("ins_ok")))
        for w in self.insight_box.winfo_children():
            w.destroy()
        for glyph, tint, color, text in rows:
            row = tk.Frame(self.insight_box, bg=C["card"])
            row.pack(fill="x", pady=px(6))
            chip(row, glyph, tint, color, size=32, font_size=12, outline=C["ink_line"]).pack(side=self.s1, anchor="n")
            tk.Label(row, text=text, bg=C["card"], fg=C["ink"], font=fnt(10), anchor=self.a1, justify=self.just,
                     wraplength=px(210)).pack(side=self.s1, fill="x", expand=True, padx=self.pad(10, 0))
        self._wrap_insights()

    def _wrap_insights(self, event=None):
        w = self.insight_box.winfo_width()
        if not isinstance(w, (int, float)) or w <= 1:
            return
        for row in self.insight_box.winfo_children():
            for child in row.winfo_children():
                if child.winfo_class() == "Label" and child.cget("text") and len(child.cget("text")) > 2:
                    child.configure(wraplength=max(px(150), w - px(60)))
=======
            self.recent_tree.insert("", "end", tags=("odd",) if i % 2 else (), values=(
                m["movement_date"][5:16], item_name(m), mv_t(m["movement_type"]), qty_fmt(m["quantity"])))
>>>>>>> c8a133662267867832f0d0679ec8832dee7dfdbb
