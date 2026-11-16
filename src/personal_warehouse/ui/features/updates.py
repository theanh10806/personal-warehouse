"""In-app update check (GitHub Releases)."""

import threading
import webbrowser

from tkinter import messagebox

from personal_warehouse import __version__, updater
from personal_warehouse.i18n import tr
from personal_warehouse.settings import load_settings, save_settings


class UpdatesFeature:
    def _auto_update_check(self):
        if load_settings().get("auto_update", True):
            self.check_updates(manual=False)

    def check_updates(self, manual):
        """Ask GitHub in a background thread; the result is picked up by _update_poll on the UI thread."""
        if getattr(self, "_upd", None) and not self._upd.get("finished"):
            return
        self._upd = {"finished": False, "result": None, "manual": manual}

        def work(st):
            st["result"] = updater.check()
            st["finished"] = True
        threading.Thread(target=work, args=(self._upd,), daemon=True).start()
        self.after(300, self._update_poll)

    def _update_poll(self):
        st = self._upd
        if not st:
            return
        if not st["finished"]:
            self.after(300, self._update_poll)
            return
        res, manual = st["result"], st["manual"]
        if res["status"] == "new":
            rel = res["release"]
            self.status(tr("upd_status", rel["version"]))
            # Ask once per version when checking automatically; always ask on a manual check.
            if manual or load_settings().get("notified_version") != rel["version"]:
                save_settings(notified_version=rel["version"])
                if messagebox.askyesno(tr("upd_title"), tr("upd_available", rel["version"], __version__,
                                                           rel["notes"] or "")):
                    webbrowser.open(rel["download"] or rel["page"])
        elif manual:
            if res["status"] == "current":
                messagebox.showinfo(tr("upd_title"), tr("upd_none", __version__))
            elif res["status"] == "disabled":
                messagebox.showinfo(tr("upd_title"), tr("upd_disabled"))
            else:
                messagebox.showerror(tr("upd_title"), tr("upd_fail", res["error"]))
