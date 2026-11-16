"""Add / edit item page."""

from pathlib import Path
from datetime import datetime
import re
import shutil

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox

from personal_warehouse import config
from personal_warehouse.config import CONDITIONS, PARTS, SECTIONS, UNITS
from personal_warehouse.core.database import db, record_movement
from personal_warehouse.core.formatting import make_location, num, photo_file, qty_fmt
from personal_warehouse.core.translator import translate_online
from personal_warehouse.i18n import cond_t, current_lang, from_label, tr, unit_t
from personal_warehouse.ui.imaging import Image, ImageTk
from personal_warehouse.ui.theme import C
from personal_warehouse.ui.widgets import btn, card, draw_barcode, lbl


class ItemFormPage:
    def _build_item_form(self):
        f = self.item_tab
        self.form_title = tk.StringVar(value=tr("form_new"))
        box = tk.Frame(f, bg=C["bg"])
        box.pack(fill="x", pady=(0, 12))
        lbl(box, "", 22, True, C["title"], anchor=self.a1, textvariable=self.form_title).pack(fill="x")
        self.loc_preview = tk.StringVar()
        lbl(box, "", 10, False, C["muted"], anchor=self.a1, textvariable=self.loc_preview).pack(fill="x", pady=(2, 0))
        body = tk.Frame(f, bg=C["bg"])
        body.pack(fill="both", expand=True)
        formcard = card(body, padx=18, pady=12)
        formcard.pack(side=self.s1, fill="both", expand=True)
        form = tk.Frame(formcard, bg=C["card"])
        form.pack(fill="both", expand=True)
        self.fields = {}
        specs = [("name", "f_name", "entry"), ("name_ar", "f_name_ar", "entry_tr"),
                 ("category", "f_category", "entry"), ("description", "f_description", "entry"),
                 ("engine_application", "f_engine", "entry"), ("barcode", "f_barcode", "entry"),
                 ("section", "f_section", "section"), ("part", "f_part", "part"),
                 ("condition", "f_condition", "condition"), ("unit", "f_unit", "unit"),
                 ("quantity", "f_qty", "entry"), ("min_stock", "f_min", "entry"),
                 ("purchase_price", "f_buy", "entry"), ("selling_price", "f_sell", "entry"),
                 ("supplier", "f_supplier", "entry"), ("notes", "f_notes", "entry")]
        for idx, (key, label, kind) in enumerate(specs):
            r, c = divmod(idx, 2)
            cell = tk.Frame(form, bg=C["card"], padx=8, pady=5)
            cell.grid(row=r, column=c, sticky="ew")
            self._field_label(cell, tr(label), C["card"]).pack(fill="x")
            if kind in ("entry", "entry_tr"):
                row = tk.Frame(cell, bg=C["card"])
                row.pack(fill="x", pady=(3, 0))
                w = ttk.Entry(row, width=36, justify="right" if (self.rtl or key == "name_ar" and current_lang() == "ar") else "left")
                if kind == "entry_tr":
                    btn(row, tr("btn_translate"), self.translate_name_field, "soft", padx=8, pady=4).pack(
                        side=self.s2, padx=(6, 0))
                w.pack(side=self.s1, fill="x", expand=True)
            else:
                vals = {"section": SECTIONS, "part": PARTS, "condition": [cond_t(c) for c in CONDITIONS],
                        "unit": [unit_t(u) for u in UNITS]}[kind]
                w = ttk.Combobox(cell, values=vals, state="readonly", width=34, justify=self.just)
                w.bind("<<ComboboxSelected>>", lambda e: self._update_loc_preview())
                w.pack(fill="x", pady=(3, 0))
            self.fields[key] = w
        form.columnconfigure(0, weight=1, uniform="item_fields")
        form.columnconfigure(1, weight=1, uniform="item_fields")

        side = card(body, padx=16, pady=14)
        side.pack(side=self.s2, fill="y", padx=(0, 12) if self.rtl else (12, 0))
        self._item_form_body = body
        self._item_form_grid = form
        self._item_form_side = side
        self._item_form_compact = None
        body.bind("<Configure>", self._adapt_item_form, add="+")
        lbl(side, tr("photo_title"), 10, True, C["title"], C["card"], anchor=self.a1).pack(fill="x")
        self.photo_label = tk.Label(side, text=tr("no_photo"), bg=C["empty"], fg=C["muted"], width=28, height=11)
        self.photo_label.pack(pady=10)
        btn(side, tr("choose_photo"), self.choose_photo, "soft").pack(fill="x", pady=2)
        btn(side, tr("remove_photo"), self.remove_photo, "soft").pack(fill="x", pady=2)
        if Image is None:
            lbl(side, tr("pillow_tip"), 9, False, C["muted"], C["card"], justify=self.just, anchor=self.a1).pack(fill="x", pady=6)
        lbl(side, tr("bc_preview"), 10, True, C["title"], C["card"], anchor=self.a1).pack(fill="x", pady=(14, 6))
        self.bc_canvas = tk.Canvas(side, width=250, height=74, bg="white", highlightthickness=1,
                                   highlightbackground=C["line"])
        self.bc_canvas.pack()

        actions = tk.Frame(f, bg=C["bg"])
        actions.pack(fill="x", pady=12)
        btn(actions, tr("btn_save"), self.save_item, "success").pack(side=self.s1)
        btn(actions, tr("btn_clear"), self.clear_form, "soft").pack(side=self.s1, padx=8)
        btn(actions, tr("btn_print_one"), self.print_current_label, "soft").pack(side=self.s1)
        btn(actions, tr("btn_back"), lambda: self.pages.select(self.inventory_tab), "ghost").pack(side=self.s2)
        self.clear_form()

    def _adapt_item_form(self, event=None):
        if not hasattr(self, "_item_form_body"):
            return
        compact = self._item_form_body.winfo_width() < 1160
        if compact == self._item_form_compact:
            return
        self._item_form_compact = compact
        if compact:
            self._item_form_side.pack_forget()
            self._item_form_side.pack(side="bottom", fill="x", pady=(10, 0))
            for idx, cell in enumerate(self._item_form_grid.winfo_children()):
                cell.grid_configure(row=idx, column=0, columnspan=2, sticky="ew")
            self._item_form_grid.columnconfigure(0, weight=1, uniform="")
            self._item_form_grid.columnconfigure(1, weight=0, uniform="")
        else:
            self._item_form_side.pack_forget()
            self._item_form_side.pack(side=self.s2, fill="y", padx=(0, 12) if self.rtl else (12, 0))
            for idx, cell in enumerate(self._item_form_grid.winfo_children()):
                cell.grid_configure(row=idx // 2, column=idx % 2, columnspan=1, sticky="ew")
            self._item_form_grid.columnconfigure(0, weight=1, uniform="item_fields")
            self._item_form_grid.columnconfigure(1, weight=1, uniform="item_fields")

    def _get(self, k):
        w = self.fields[k]
        v = w.get().strip()
        if k == "condition":
            return from_label(CONDITIONS, cond_t, v)
        if k == "unit":
            return from_label(UNITS, unit_t, v)
        return v

    def _set(self, k, val):
        w = self.fields[k]
        val = "" if val is None else str(val)
        if k == "condition":
            val = cond_t(val)
        elif k == "unit":
            val = unit_t(val)
        if isinstance(w, ttk.Combobox):
            w.set(val)
        else:
            w.configure(state="normal")
            w.delete(0, "end")
            w.insert(0, val)

    def _update_loc_preview(self):
        self.loc_preview.set(tr("loc_preview", make_location(self._get("section"), self._get("part"))))

    def clear_form(self):
        self.selected_id = None
        self.photo_new = self.photo_current = None
        self.photo_remove = False
        self.form_title.set(tr("form_new"))
        defaults = {"section": "A", "part": "1", "condition": "New", "unit": "pcs",
                    "quantity": "0", "min_stock": "0"}
        for k in self.fields:
            self._set(k, defaults.get(k, ""))
        self._update_loc_preview()
        self.show_photo(None)
        draw_barcode(self.bc_canvas, "")

    def new_item(self):
        self.clear_form()
        self.pages.select(self.item_tab)
        self.fields["name"].focus_set()

    def edit_item(self, iid):
        with db() as con:
            r = con.execute("SELECT * FROM items WHERE id=?", (iid,)).fetchone()
        if not r:
            return
        self.clear_form()
        self.selected_id = iid
        self.form_title.set(tr("form_edit", r["item_code"]))
        for k in self.fields:
            self._set(k, qty_fmt(r[k]) if k in ("quantity", "min_stock") else r[k])
        self.fields["quantity"].configure(state="disabled")
        self.photo_current = r["photo_path"]
        self._update_loc_preview()
        self.loc_preview.set(self.loc_preview.get() + tr("loc_preview_edit"))
        self.show_photo(self.photo_current)
        draw_barcode(self.bc_canvas, r["item_code"])
        self.pages.select(self.item_tab)

    def translate_name_field(self):
        name = self._get("name")
        if not name:
            messagebox.showinfo(tr("tr_title"), tr("tr_need_name"))
            return
        self.configure(cursor="watch")
        self.update_idletasks()
        try:
            self._set("name_ar", translate_online(name, "ar"))
        except Exception as e:
            messagebox.showerror(tr("tr_title"), tr("tr_fail", e))
        finally:
            self.configure(cursor="")

    def show_photo(self, path):
        self._photo_img = None
        p = Path(path) if path else None
        if p and not p.is_absolute():
            p = photo_file(path)
        if p and p.exists():
            if Image:
                try:
                    im = Image.open(p)
                    im.thumbnail((230, 190))
                    self._photo_img = ImageTk.PhotoImage(im)
                    self.photo_label.configure(image=self._photo_img, text="", width=230, height=190)
                    return
                except Exception:
                    pass
            self.photo_label.configure(image="", text=p.name, width=28, height=11)
        else:
            self.photo_label.configure(image="", text=tr("no_photo"), width=28, height=11)

    def choose_photo(self):
        path = filedialog.askopenfilename(title=tr("choose_photo_title"), filetypes=[
            (tr("image_files"), "*.png *.jpg *.jpeg *.gif *.bmp *.webp"), (tr("all_files"), "*.*")])
        if path:
            self.photo_new, self.photo_remove = Path(path), False
            self.show_photo(path)

    def remove_photo(self):
        self.photo_new, self.photo_remove = None, True
        self.show_photo(None)

    def save_item(self):
        v = {k: self._get(k) for k in self.fields}
        if not v["name"]:
            messagebox.showerror(tr("err_name_title"), tr("err_name"))
            return
        try:
            buy = round(num(v["purchase_price"], tr("f_buy")), 2)
            sell = round(num(v["selling_price"], tr("f_sell")), 2)
            minq = num(v["min_stock"], tr("f_min"))
            qty = None if self.selected_id else num(v["quantity"], tr("f_qty"))
        except ValueError as e:
            messagebox.showerror(tr("err_number_title"), str(e))
            return
        if sell and buy and sell < buy and not messagebox.askyesno(tr("price_below_title"), tr("price_below")):
            return
        barcode = v["barcode"] or None
        if barcode:
            with db() as con:
                clash = con.execute("SELECT item_code FROM items WHERE (barcode=? OR item_code=? COLLATE NOCASE) "
                                    "AND id<>?", (barcode, barcode, self.selected_id or 0)).fetchone()
            if clash:
                messagebox.showerror(tr("save_failed"), tr("barcode_dup", barcode, clash["item_code"]))
                return
        if not self.selected_id:
            with db() as con:
                dup = con.execute("SELECT item_code FROM items WHERE is_active=1 AND name=? COLLATE NOCASE "
                                  "AND section=? AND part=?",
                                  (v["name"], v["section"], v["part"])).fetchone()
            if dup and not messagebox.askyesno(tr("dup_title"), tr("dup_msg", dup["item_code"])):
                return
        new_name = None
        if self.photo_new:
            safe = re.sub(r"[^\w.\-]", "_", self.photo_new.name)
            new_name = f"{datetime.now():%Y%m%d%H%M%S%f}_{safe}"
            try:
                shutil.copy2(self.photo_new, config.PHOTO_DIR / new_name)
            except Exception as e:
                messagebox.showerror(tr("photo_err"), str(e))
                return
        photo = new_name or (None if self.photo_remove else self.photo_current)
        common = (v["name"], v["name_ar"] or None, v["category"], v["description"], v["engine_application"],
                  barcode, v["section"], v["part"], v["condition"], v["unit"],
                  buy, sell, minq, photo, v["supplier"], v["notes"])
        try:
            with db() as con:
                if self.selected_id:
                    con.execute("""UPDATE items SET name=?,name_ar=?,category=?,description=?,engine_application=?,
                        barcode=?,section=?,part=?,condition=?,unit=?,purchase_price=?,selling_price=?,min_stock=?,
                        photo_path=?,supplier=?,notes=?,updated_at=CURRENT_TIMESTAMP WHERE id=?""",
                                common + (self.selected_id,))
                else:
                    cur = con.execute("""INSERT INTO items(name,name_ar,category,description,engine_application,
                        barcode,section,part,condition,unit,purchase_price,selling_price,min_stock,photo_path,
                        supplier,notes,quantity,date_added) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                                      common + (qty, datetime.now().strftime("%Y-%m-%d")))
                    item_id = cur.lastrowid
                    con.execute("UPDATE items SET item_code=? WHERE id=?", (f"WH-{item_id:05d}", item_id))
                    if qty > 0:
                        record_movement(con, item_id, "Opening stock", qty, "Initial quantity", buy, 0, qty)
        except Exception as e:
            if new_name:
                (config.PHOTO_DIR / new_name).unlink(missing_ok=True)
            messagebox.showerror(tr("save_failed"), str(e))
            return
        old = self.photo_current
        if old and old != photo:
            with db() as con:
                still_used = con.execute("SELECT COUNT(*) FROM items WHERE photo_path=?", (old,)).fetchone()[0]
            if not still_used:
                try:
                    photo_file(old).unlink(missing_ok=True)
                except OSError:
                    pass
        name = v["name"]
        self.clear_form()
        self.refresh_all()
        self.pages.select(self.inventory_tab)
        self.status(tr("saved", name))
