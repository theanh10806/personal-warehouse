"""Desktop window: the web interface inside a native window (pywebview, WebView2 on Windows)."""
from pathlib import Path

from personal_warehouse.core.database import auto_backup
from personal_warehouse.i18n import tr
from personal_warehouse.webui.api import Api

STATIC = Path(__file__).with_name("static")


def _windows_icon(title):
    """Give the running window + taskbar the app icon (the packaged .exe already has it; this covers `python -m`)."""
    try:
        import ctypes
        ico = STATIC / "icon.ico"
        if not ico.exists():
            return
        u = ctypes.windll.user32
        hwnd = u.FindWindowW(None, title)
        for size, which in ((32, 0), (16, 1)):                    # ICON_SMALL=0 / ICON_BIG=1 -> use both sizes
            h = u.LoadImageW(None, str(ico), 1, 256 if which == 0 else 16, 256 if which == 0 else 16, 0x10)  # IMAGE_ICON, LR_LOADFROMFILE
            if hwnd and h:
                u.SendMessageW(hwnd, 0x80, 1 if which == 0 else 0, h)                                        # WM_SETICON
    except Exception:                                             # noqa: BLE001 - cosmetic only
        pass


def run():
    """Open the window and block until it is closed. Raises ImportError when pywebview is not installed."""
    import sys
    import webview
    if sys.platform == "win32":
        try:                                                       # own taskbar identity (not "python.exe")
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("PersonalWarehouse.App")
        except Exception:                                          # noqa: BLE001
            pass
    api = Api()
    window = webview.create_window(
        tr("app_name"), url=str(STATIC / "index.html"), js_api=api, width=1360, height=860,
        min_size=(940, 600), background_color="#FFF3E0", text_select=False)
    api._attach(window)
    window.events.closed += lambda: auto_backup(overwrite=True)
    if sys.platform == "win32":
        window.events.shown += lambda: _windows_icon(tr("app_name"))
    # Windows (WinForms) cannot build its icon from a PNG and crashes, so there we only use _windows_icon() above
    # (and the .exe's own icon). The Linux (GTK/Qt) backends accept the PNG.
    icon = STATIC / "icon.png"
    if sys.platform != "win32" and icon.exists():
        webview.start(icon=str(icon))
    else:
        webview.start()
