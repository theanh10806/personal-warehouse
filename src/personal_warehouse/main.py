"""Application start-up: settings, database, then the main window."""
import sys

from personal_warehouse import config
from personal_warehouse.core.database import auto_backup, init_db, pre_migration_backup
from personal_warehouse.i18n import LANGS, set_language
from personal_warehouse.settings import load_settings


def main(argv=None):
    from personal_warehouse.instance import single_instance
    with single_instance() as acquired:
        if not acquired:
            if sys.platform == "win32":
                import ctypes
                ctypes.windll.user32.MessageBoxW(None, "Personal Warehouse is already running.",
                                               "Personal Warehouse", 64)
            else:
                print("Personal Warehouse is already running.")
            return
        if not _version_allowed():
            return
        _run(argv)


def _version_allowed():
    """Only the newest installed version may run (Store and GitHub copies share one marker); older ones say so and stop."""
    from personal_warehouse import version_guard
    result = version_guard.check()
    if result["status"] != "older":
        version_guard.record()
        return True
    lang = load_settings().get("lang")                        # the language is only known once settings are read
    set_language(lang if lang in LANGS else "vi")
    text = version_guard.older_message(result["installed"])
    if sys.platform == "win32":
        import ctypes
        ctypes.windll.user32.MessageBoxW(None, text, "Personal Warehouse", 0x40)
    else:
        print(text)
    return False


def _run(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if sys.platform == "win32":
        try:
            from ctypes import windll
            windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            pass
    config.ensure_dirs()
    from personal_warehouse.core.transfer import recover_restore
    recover_restore()
    st = load_settings()
    set_language(st.get("lang") if st.get("lang") in LANGS else "vi")
    pre_migration_backup()
    init_db()
    auto_backup(overwrite=False)
    from personal_warehouse.core.history import purge_trash
    purge_trash()
    if "--tk" not in argv:
        if "--browser" in argv:                                # same web UI in your normal browser (no pywebview needed)
            from personal_warehouse.webui.server import serve
            serve()
            return
        try:
            from personal_warehouse.webui.desktop import run
            run()
            return
        except ImportError:
            print("pywebview is not installed (pip install pywebview): falling back to the classic Tk window.")
    from personal_warehouse.ui.theme import set_theme
    from personal_warehouse.ui.app import WarehouseApp      # imported late so tests can import this module without Tk
    set_theme(st.get("theme", "light"))
    WarehouseApp().mainloop()


if __name__ == "__main__":
    main()
