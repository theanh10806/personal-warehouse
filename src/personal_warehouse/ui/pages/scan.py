"""Scan page: USB scanner, camera or image file."""

import sys
import time

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox

from personal_warehouse.core.database import db
from personal_warehouse.core.formatting import item_name, make_location, money, num, photo_file, qty_fmt
from personal_warehouse.core.scanning import decode_codes
from personal_warehouse.core.stock import apply_movement, find_item
from personal_warehouse.i18n import cond_t, mv_t, tr, unit_t
from personal_warehouse.ui.imaging import Image, ImageTk
from personal_warehouse.ui.theme import C, fnt, px
from personal_warehouse.ui.widgets import btn, card, lbl


class ScanPage:
    def _build_scan(self):
        f = self.scan_tab
        self._page_head(f, tr("scan_title"), tr("scan_sub"))
        top = card(f, padx=16, pady=14)
        top.pack(fill="x")
        row = tk.Frame(top, bg=C["card"])
        row.pack(fill="x")
        self.scan_var = tk.StringVar()
        self.scan_entry = ttk.Entry(row, textvariable=self.scan_var, font=fnt(14), width=10, justify=self.just)
        self.scan_entry.bind("<Return>", self._scan_enter)
        scan_btns = tk.Frame(row, bg=C["card"])
        btn(scan_btns, tr("scan_lookup_btn"), self._scan_flush, "primary").pack(side=self.s1, padx=self.pad(0, 8))
        btn(scan_btns, tr("scan_camera"), self.camera_scan, "soft").pack(side=self.s1, padx=self.pad(0, 8))
        btn(scan_btns, tr("scan_image"), self.scan_from_image, "soft").pack(side=self.s1)
        self._scan_row, self._scan_btns_frame, self._scan_stacked = row, scan_btns, None
        row.bind("<Configure>", self._adapt_scan_row, add="+")
        row2 = tk.Frame(top, bg=C["card"])
        row2.pack(fill="x", pady=(12, 0))
        lbl(row2, tr("scan_mode"), 10, False, C["muted"], C["card"]).pack(side=self.s1)
        self.scan_mode = tk.StringVar(value=tr("scan_lookup"))
        ttk.Combobox(row2, textvariable=self.scan_mode, state="readonly", width=16, justify=self.just,
                     values=[tr("scan_lookup"), mv_t("Stock In"), mv_t("Stock Out")]).pack(side=self.s1, padx=8)
        lbl(row2, tr("scan_qtyper"), 10, False, C["muted"], C["card"]).pack(side=self.s1, padx=self.pad(12, 0))
        self.scan_qty = tk.StringVar(value="1")
        ttk.Spinbox(row2, from_=1, to=9999, textvariable=self.scan_qty, width=7, justify=self.just).pack(side=self.s1, padx=8)
        hint = lbl(top, tr("scan_mode_hint"), 9, False, C["muted"], C["card"], justify=self.just, anchor=self.a1)
        hint.pack(fill="x", pady=(8, 0))
        top.bind("<Configure>", lambda e: hint.configure(wraplength=max(px(160), top.winfo_width() - px(40)))
                 if isinstance(top.winfo_width(), (int, float)) and top.winfo_width() > 1 else None, add="+")

        body = tk.Frame(f, bg=C["bg"])
        body.pack(fill="both", expand=True, pady=12)
        main = card(body, padx=18, pady=16)
        main.grid(row=0, column=1 if self.rtl else 0, sticky="nsew")
        self.scan_head = tk.StringVar(value=tr("scan_wait"))
        self._scan_head_lbl = tk.Label(main, textvariable=self.scan_head, bg=C["card"], fg=C["title"],
                                       font=fnt(16, True), anchor=self.a1, justify=self.just, wraplength=px(300))
        self._scan_head_lbl.pack(fill="x")
        main.bind("<Configure>", lambda e: self._scan_head_lbl.configure(wraplength=max(px(200), main.winfo_width() - px(50)))
                  if isinstance(main.winfo_width(), (int, float)) and main.winfo_width() > 1 else None, add="+")
        self.scan_flash = tk.Label(main, text="", bg=C["card"], fg=C["ok"], font=fnt(13, True), anchor=self.a1)
        self.scan_flash.pack(fill="x", pady=(4, 0))
        self.scan_grid = tk.Frame(main, bg=C["card"])
        self.scan_grid.pack(fill="both", expand=True, pady=(10, 0))
        side = card(body, padx=16, pady=16)
        side.grid(row=0, column=0 if self.rtl else 1, sticky="nsew", padx=self.pad(12, 0))
        self._scan_body = body
        self._scan_main_card = main
        self._scan_side_card = side
        self._scan_side_by_side = None
        body.grid_columnconfigure(1 if self.rtl else 0, weight=1)
        body.grid_columnconfigure(0 if self.rtl else 1, weight=0)
        body.grid_rowconfigure(0, weight=1)
        body.bind("<Configure>", self._adapt_scan_layout, add="+")
        self.scan_photo = tk.Label(side, text=tr("no_photo"), bg=C["empty"], fg=C["muted"], width=28, height=11)
        self.scan_photo.pack(pady=(0, 12))
        self.scan_btns = {}
        for key, text, kind in [("move", tr("btn_move"), "primary"), ("edit", tr("btn_edit"), "soft"),
                                ("print", tr("btn_print_one"), "soft")]:
            b = btn(side, text, lambda k=key: self._scan_do(k), kind, state="disabled")
            b.pack(fill="x", pady=3)
            self.scan_btns[key] = b

    def _adapt_scan_row(self, event=None):
        """Wide: entry + buttons on one line. Narrow: buttons wrap under the entry instead of being cut off."""
        width = self._scan_row.winfo_width()
        if not isinstance(width, (int, float)) or width <= 1:
            return
        stacked = width < px(720)
        if stacked == self._scan_stacked:
            return
        self._scan_stacked = stacked
        self.scan_entry.pack_forget()
        self._scan_btns_frame.pack_forget()
        if stacked:
            self.scan_entry.pack(fill="x", ipady=5)
            self._scan_btns_frame.pack(fill="x", pady=(10, 0), anchor=self.a1)
        else:
            self._scan_btns_frame.pack(side=self.s2)
            self.scan_entry.pack(side=self.s1, fill="x", expand=True, padx=self.pad(0, 10), ipady=5)

    def _adapt_scan_layout(self, event=None):
        """Keep scan details readable by moving the preview card below on narrow windows (mirrored in RTL)."""
        if not hasattr(self, "_scan_body"):
            return
        width = self._scan_body.winfo_width()
        if not isinstance(width, (int, float)) or width <= 1:
            return
        side_by_side = width >= px(860)
        if side_by_side == self._scan_side_by_side:
            return
        self._scan_side_by_side = side_by_side
        body, main, side = self._scan_body, self._scan_main_card, self._scan_side_card
        mc, sc = (1, 0) if self.rtl else (0, 1)
        for col in (0, 1):
            body.grid_columnconfigure(col, weight=0, minsize=0)
        if side_by_side:
            main.grid_configure(row=0, column=mc, columnspan=1, sticky="nsew")
            side.grid_configure(row=0, column=sc, columnspan=1, sticky="nsew", padx=self.pad(12, 0), pady=0)
            body.grid_columnconfigure(mc, weight=1)
            body.grid_columnconfigure(sc, weight=0, minsize=px(286))
        else:
            main.grid_configure(row=0, column=0, columnspan=2, sticky="nsew")
            side.grid_configure(row=1, column=0, columnspan=2, sticky="ew", padx=0, pady=(12, 0))
            body.grid_columnconfigure(0, weight=1)
        body.grid_rowconfigure(0, weight=1)
        body.grid_rowconfigure(1, weight=0)

    def _scan_mode_key(self):
        lab = self.scan_mode.get()
        if lab == mv_t("Stock In"):
            return "Stock In"
        if lab == mv_t("Stock Out"):
            return "Stock Out"
        return "lookup"

    def _scan_enter(self, e=None):
        if self._scan_job:
            self.after_cancel(self._scan_job)
        self._scan_job = self.after(250, self._scan_flush)

    def _scan_flush(self):
        self._scan_job = None
        text = self.scan_var.get().strip()
        self.scan_var.set("")
        if text:
            self.handle_scan(text)
        self.scan_entry.focus_set()

    def _scan_value_wrap(self):
        w = self._scan_main_card.winfo_width()
        return max(px(200), (w if isinstance(w, (int, float)) and w > 1 else px(700)) - px(220))

    def _scan_write(self, rows):
        for w in self.scan_grid.winfo_children():
            w.destroy()
        kc, vc = (1, 0) if self.rtl else (0, 1)
        for i, (k, v) in enumerate(rows):
            lbl(self.scan_grid, k, 10, False, C["muted"], C["card"], anchor=self.a1, justify=self.just).grid(
                row=i, column=kc, sticky="ne", padx=(0, 18) if not self.rtl else (18, 0), pady=3)
            lbl(self.scan_grid, v, 11, False, C["ink"], C["card"], anchor=self.a1, justify=self.just,
                wraplength=self._scan_value_wrap()).grid(row=i, column=vc, sticky=self.a1, pady=3)
        self.scan_grid.columnconfigure(vc, weight=1)

    def _thumb(self, stored, box=(230, 190)):
        p = photo_file(stored) if stored else None
        if Image and p and p.exists():
            try:
                im = Image.open(p)
                im.thumbnail(box)
                return ImageTk.PhotoImage(im)
            except Exception:
                pass
        return None

    def handle_scan(self, text):
        """Process a scanned value. Returns (found, short ascii message for the camera overlay)."""
        text = (text or "").strip()
        r, code = find_item(text)
        self.pages.select(self.scan_tab)
        self.scan_item_id = None
        for b in self.scan_btns.values():
            b.configure(state="disabled")
        self._scan_img = None
        self.scan_photo.configure(image="", text=tr("no_photo"), width=28, height=11)
        self.scan_flash.configure(text="")
        if not r:
            if code:
                self.scan_head.set(tr("scan_notfound", code))
            else:
                self.scan_head.set(tr("scan_not_wh"))
            self._scan_write([(tr("scan_content"), text[:600])])
            return False, "NOT FOUND"
        self.bell()
        flash, flash_ok, banner = "", True, f"OK {r['item_code']}"
        mode = self._scan_mode_key()
        if mode != "lookup":
            if not r["is_active"]:
                flash, flash_ok = tr("scan_archived_no"), False
            else:
                try:
                    q = num(self.scan_qty.get(), tr("scan_qtyper"))
                    if q <= 0:
                        raise ValueError(tr("err_qty"))
                    price = r["purchase_price"] if mode == "Stock In" else r["selling_price"]
                    _, before, after = apply_movement(r["id"], mode, q, price, "Scan")
                    key = "scan_flash_in" if mode == "Stock In" else "scan_flash_out"
                    flash = tr(key, qty_fmt(q), qty_fmt(after), unit_t(r["unit"]))
                    banner = f"{r['item_code']} {'+' if mode == 'Stock In' else '-'}{qty_fmt(q)} = {qty_fmt(after)}"
                    self.refresh_all()
                except ValueError as e:
                    flash, flash_ok, banner = tr("scan_flash_err", e), False, "ERROR"
            with db() as con:
                r = con.execute("SELECT * FROM items WHERE id=?", (r["id"],)).fetchone()
        self.scan_item_id = r["id"]
        warn = ""
        if not r["is_active"]:
            warn = "   " + tr("st_archived")
        elif r["quantity"] <= 0:
            warn = "   " + tr("st_out")
        elif r["min_stock"] > 0 and r["quantity"] <= r["min_stock"]:
            warn = "   " + tr("st_low")
        self.scan_head.set(f"{r['item_code']} — {item_name(r)}{warn}")
        self.scan_flash.configure(text=flash, fg=C["ok"] if flash_ok else C["danger"])
        dash = "—"
        self._scan_write([
            (tr("f_category"), r["category"] or dash),
            (tr("f_description"), r["description"] or dash),
            (tr("f_engine"), r["engine_application"] or dash),
            (tr("f_barcode").split(" (")[0], r["barcode"] or dash),
            (tr("h_location"), make_location(r["section"], r["part"])),
            (tr("f_condition"), cond_t(r["condition"])),
            (tr("sc_stock"), f"{qty_fmt(r['quantity'])} {unit_t(r['unit'])}"),
            (tr("f_min"), qty_fmt(r["min_stock"])),
            (tr("f_buy"), money(r["purchase_price"])),
            (tr("f_sell"), money(r["selling_price"])),
            (tr("f_supplier"), r["supplier"] or dash),
            (tr("f_notes"), r["notes"] or dash),
            (tr("sc_added"), r["date_added"] or dash)])
        self._scan_img = self._thumb(r["photo_path"])
        if self._scan_img:
            self.scan_photo.configure(image=self._scan_img, text="", width=230, height=190)
        self.scan_btns["edit"].configure(state="normal")
        self.scan_btns["print"].configure(state="normal")
        if r["is_active"]:
            self.scan_btns["move"].configure(state="normal")
        self.status(tr("scan_scanned", r["item_code"]))
        return True, banner

    def _scan_do(self, kind):
        iid = self.scan_item_id
        if not iid:
            return
        if kind == "move":
            self.go_movement(iid)
        elif kind == "edit":
            self.edit_item(iid)
        else:
            self.print_labels([iid])

    def camera_scan(self):
        try:
            import cv2
        except ImportError:
            messagebox.showerror(tr("cam_unavail_title"), tr("cam_unavail"))
            return
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW) if sys.platform == "win32" else cv2.VideoCapture(0)
        if not cap.isOpened():
            messagebox.showerror(tr("scan_camera"), tr("cam_open_err"))
            return
        win = "Scan - press Q or ESC to close"
        continuous = self._scan_mode_key() != "lookup"      # stock in/out: keep scanning
        last, last_t, banner, banner_t = "", 0.0, "", 0.0
        try:
            while True:
                ok, frame = cap.read()
                if not ok:
                    break
                text = decode_codes(frame)
                now = time.time()
                if text and (text != last or now - last_t > 2.5):
                    last, last_t = text, now
                    found, banner = self.handle_scan(text)
                    banner_t = now
                    self.update()
                    if found and not continuous:
                        break
                if banner and now - banner_t < 2.0:
                    cv2.putText(frame, banner, (10, 34), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 200, 0), 2)
                cv2.imshow(win, frame)
                if cv2.waitKey(1) & 0xFF in (27, ord("q")):
                    break
                if cv2.getWindowProperty(win, cv2.WND_PROP_VISIBLE) < 1:
                    break
        finally:
            cap.release()
            cv2.destroyAllWindows()

    def scan_from_image(self):
        path = filedialog.askopenfilename(title=tr("img_open_title"), filetypes=[
            (tr("image_files"), "*.png *.jpg *.jpeg *.bmp *.webp"), (tr("all_files"), "*.*")])
        if not path:
            return
        try:
            import cv2
            import numpy as np
        except ImportError:
            messagebox.showerror(tr("cam_unavail_title"), tr("cam_unavail"))
            return
        img = cv2.imdecode(np.fromfile(path, dtype=np.uint8), cv2.IMREAD_COLOR)
        if img is None:
            messagebox.showerror(tr("scan_image"), tr("img_read_err"))
            return
        text = decode_codes(img)
        if not text:
            big = cv2.resize(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), None, fx=2, fy=2,
                             interpolation=cv2.INTER_CUBIC)
            text = decode_codes(big)
        if text:
            self.handle_scan(text)
        else:
            messagebox.showinfo(tr("no_qr"), tr("no_qr_msg"))
