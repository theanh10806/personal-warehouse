"""Data tools: export to Excel / CSV and full backup."""

from pathlib import Path
from datetime import datetime
import shutil

from tkinter import filedialog
from tkinter import messagebox

from personal_warehouse import config
from personal_warehouse.core.database import backup_db_to
from personal_warehouse.core.exporter import ExcelUnavailable, export_inventory
from personal_warehouse.i18n import tr


class DataToolsFeature:
    def export_excel(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".xlsx", initialfile=f"Warehouse_{datetime.now():%Y%m%d}.xlsx",
            filetypes=[(tr("excel_files"), "*.xlsx"), (tr("csv_files"), "*.csv")])
        if not path:
            return
        try:
            export_inventory(path, self.rtl)
        except ExcelUnavailable:
            messagebox.showerror(tr("exp_unavail"), tr("exp_unavail_msg"))
            return
        except Exception as e:
            messagebox.showerror(tr("exp_fail"), str(e))
            return
        self.status(tr("exp_done", path))

    def backup_all(self):
        dest = filedialog.askdirectory(title=tr("backup_pick"))
        if not dest:
            return
        target = Path(dest) / f"MyWarehouse_Backup_{datetime.now():%Y%m%d_%H%M%S}"
        try:
            (target / "Database").mkdir(parents=True)
            backup_db_to(target / "Database" / "warehouse.db")
            shutil.copytree(config.PHOTO_DIR, target / "Photos")
            self.status(tr("backup_status", target))
            messagebox.showinfo(tr("backup_done"), tr("backup_done_msg", target))
        except Exception as e:
            messagebox.showerror(tr("backup_fail"), str(e))
