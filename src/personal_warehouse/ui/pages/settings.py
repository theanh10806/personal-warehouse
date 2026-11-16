"""Settings page: language, theme, bulk translation, data tools, updates."""

import threading
import time

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

from personal_warehouse import __version__, config
from personal_warehouse.config import KEEP_AUTO_BACKUPS
from personal_warehouse.core.database import db
from personal_warehouse.core.translator import translate_online
from personal_warehouse.i18n import LANGS, current_lang, tr
from personal_warehouse.settings import load_settings, save_settings
from personal_warehouse.ui.theme import C, current_theme, fnt
from personal_warehouse.ui.widgets import btn, card, lbl


class SettingsPage:
    def _build_settings(self):
        f = self.settings_tab
        self._page_head(f, tr("set_title"), tr("set_sub"))
        c1 = card(f, padx=20, pady=16)
        c1.pack(fill="x")
        for row, (label, values, current, cb) in enumerate([
                (tr("set_lang"), list(LANGS.values()), LANGS[current_lang()],
                 lambda v: self.set_language(next(k for k, n in LANGS.items() if n == v))),
                (tr("set_theme"), [tr("theme_light"), tr("theme_dark")],
                 tr("theme_dark") if current_theme() == "dark" else tr("theme_light"),
                 lambda v: self.change_theme("dark" if v == tr("theme_dark") else "light"))]):
            lbl(c1, label, 11, True, C["title"], C["card"], anchor=self.a1).grid(row=row, column=0, sticky=self.a1, pady=8, padx=(0, 20))
            cmb = ttk.Combobox(c1, values=values, state="readonly", width=22, justify=self.just)
            cmb.set(current)
            cmb.grid(row=row, column=1, sticky=self.a1)
            cmb.bind("<<ComboboxSelected>>", lambda e, cmb=cmb, cb=cb: cb(cmb.get()))
        lbl(c1, tr("set_rtl"), 9, False, C["muted"], C["card"], anchor=self.a1).grid(
            row=2, column=0, columnspan=2, sticky=self.a1, pady=(4, 0))

        c2 = card(f, padx=20, pady=16)
        c2.pack(fill="x", pady=(14, 0))
        lbl(c2, tr("set_translate"), 11, True, C["title"], C["card"], anchor=self.a1).pack(fill="x")
        lbl(c2, tr("set_translate_hint"), 9, False, C["muted"], C["card"], anchor=self.a1, justify=self.just,
            wraplength=820).pack(fill="x", pady=(4, 10))
        btn(c2, tr("btn_translate"), self.bulk_translate, "primary").pack(anchor=self.a1)

        c3 = card(f, padx=20, pady=16)
        c3.pack(fill="x", pady=(14, 0))
        lbl(c3, tr("data_info", config.DATA_DIR, config.BACKUP_DIR.name, KEEP_AUTO_BACKUPS), 10, False, C["muted"], C["card"],
            anchor=self.a1, justify=self.just).pack(fill="x", pady=(0, 10))
        row = tk.Frame(c3, bg=C["card"])
        row.pack(fill="x")
        btn(row, tr("qa_export"), self.export_excel, "soft").pack(side=self.s1, padx=(0, 8))
        btn(row, tr("qa_backup"), self.backup_all, "soft").pack(side=self.s1)

        c4 = card(f, padx=20, pady=16)
        c4.pack(fill="x", pady=(14, 0))
        lbl(c4, tr("upd_title"), 11, True, C["title"], C["card"], anchor=self.a1).pack(fill="x")
        lbl(c4, tr("upd_version", __version__), 10, False, C["muted"], C["card"], anchor=self.a1,
            justify=self.just).pack(fill="x", pady=(4, 10))
        self.upd_auto = tk.BooleanVar(value=load_settings().get("auto_update", True))
        tk.Checkbutton(c4, text=tr("upd_auto"), variable=self.upd_auto, bg=C["card"], fg=C["ink"],
                       activebackground=C["card"], activeforeground=C["ink"], selectcolor=C["input"],
                       font=fnt(10), command=lambda: save_settings(auto_update=self.upd_auto.get()),
                       anchor=self.a1).pack(fill="x", pady=(0, 8))
        btn(c4, tr("upd_check"), lambda: self.check_updates(manual=True), "soft").pack(anchor=self.a1)

    def bulk_translate(self):
        if self._bt and not self._bt.get("finished"):
            return
        with db() as con:
            rows = con.execute("SELECT id,name FROM items WHERE is_active=1 AND (name_ar IS NULL OR name_ar='')").fetchall()
        if not rows:
            messagebox.showinfo(tr("tr_title"), tr("bt_nothing"))
            return
        if not messagebox.askyesno(tr("tr_title"), tr("bt_confirm", len(rows))):
            return
        self._bt = {"rows": [(r["id"], r["name"]) for r in rows], "out": [], "fail": 0, "streak": 0,
                    "done": 0, "finished": False}
        threading.Thread(target=self._bt_worker, args=(self._bt,), daemon=True).start()
        self.after(300, self._bt_poll)

    @staticmethod
    def _bt_worker(st):
        for iid, name in st["rows"]:
            try:
                st["out"].append((iid, translate_online(name, "ar")))
                st["streak"] = 0
            except Exception:
                st["fail"] += 1
                st["streak"] += 1
                if st["streak"] >= 3:                     # probably offline
                    break
            st["done"] += 1
            time.sleep(0.15)
        st["finished"] = True

    def _bt_poll(self):
        st = self._bt
        if not st:
            return
        self.status(tr("bt_progress", st["done"], len(st["rows"])), 3000)
        if not st["finished"]:
            self.after(400, self._bt_poll)
            return
        if st["out"]:
            with db() as con:
                con.executemany("UPDATE items SET name_ar=?,updated_at=CURRENT_TIMESTAMP WHERE id=?",
                                [(t, i) for i, t in st["out"] if t])
            self.refresh_all()
        if st["streak"] >= 3 and not st["out"]:
            messagebox.showerror(tr("tr_title"), tr("bt_offline"))
        else:
            messagebox.showinfo(tr("tr_title"), tr("bt_done", len(st["out"]), st["fail"]))
