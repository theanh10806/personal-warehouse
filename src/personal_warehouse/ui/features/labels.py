"""Label printing actions."""

from datetime import datetime
import webbrowser

from tkinter import messagebox

from personal_warehouse import config
from personal_warehouse.core.database import db
from personal_warehouse.core.labels import build_label_html
from personal_warehouse.i18n import tr
from personal_warehouse.ui.dialogs import LabelDialog


class LabelsFeature:
    def print_selected_labels(self):
        ids = [int(i) for i in self.inv_tree.selection()]
        if not ids:
            ids = [int(i) for i in self.inv_tree.get_children()]
            if not ids:
                messagebox.showinfo(tr("lbl_nothing_t"), tr("lbl_nothing"))
                return
            if not messagebox.askyesno(tr("lbl_title_msg"), tr("lbl_all", len(ids))):
                return
        self.print_labels(ids)

    def print_current_label(self):
        if not self.selected_id:
            messagebox.showinfo(tr("lbl_title_msg"), tr("lbl_save_first"))
            return
        self.print_labels([self.selected_id])

    def print_labels(self, ids):
        dlg = LabelDialog(self, len(ids), self.rtl)
        self.wait_window(dlg)
        o = dlg.result
        if not o:
            return
        if o["kind"] in ("qr", "both"):
            try:
                import qrcode  # noqa: F401
            except ImportError:
                messagebox.showerror(tr("qr_unavail_title"), tr("qr_unavail"))
                return
        rows = {}
        with db() as con:
            for i in range(0, len(ids), 500):
                chunk = ids[i:i + 500]
                for r in con.execute(f"SELECT * FROM items WHERE id IN ({','.join('?' * len(chunk))})", chunk):
                    rows[r["id"]] = r
        items = [rows[i] for i in ids if i in rows]
        if len(items) * o["copies"] > 400 and not messagebox.askyesno(
                tr("lbl_title_msg"), tr("lbl_many", len(items) * o["copies"])):
            return
        try:
            html_text = build_label_html(items, o)
            path = config.LABEL_DIR / f"labels_{datetime.now():%Y%m%d_%H%M%S}.html"
            path.write_text(html_text, encoding="utf-8")
            for old in sorted(config.LABEL_DIR.glob("labels_*.html"))[:-20]:
                old.unlink(missing_ok=True)
            webbrowser.open(path.as_uri())
            self.status(tr("lbl_opened", len(items) * o["copies"], config.LABEL_DIR.name))
        except Exception as e:
            messagebox.showerror(tr("lbl_err"), str(e))
