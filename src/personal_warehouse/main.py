"""Application start-up: settings, database, then the main window."""
import sys

from personal_warehouse import config
from personal_warehouse.core.database import auto_backup, init_db, pre_migration_backup
from personal_warehouse.i18n import LANGS, set_language
from personal_warehouse.settings import load_settings
from personal_warehouse.ui.theme import set_theme


def main():
    if sys.platform == "win32":
        try:
            from ctypes import windll
            windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            pass
    config.ensure_dirs()
    st = load_settings()
    set_language(st.get("lang") if st.get("lang") in LANGS else "vi")
    set_theme(st.get("theme", "light"))
    pre_migration_backup()
    init_db()
    auto_backup(overwrite=False)
    from personal_warehouse.ui.app import WarehouseApp      # imported late so tests can import this module without Tk
    WarehouseApp().mainloop()


if __name__ == "__main__":
    main()
