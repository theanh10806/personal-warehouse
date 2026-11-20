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
        from ctypes import wintypes
        ico = STATIC / "icon.ico"
        if not ico.exists():
            return
        u = ctypes.windll.user32
        u.FindWindowW.argtypes = [wintypes.LPCWSTR, wintypes.LPCWSTR]
        u.FindWindowW.restype = wintypes.HWND
        u.LoadImageW.argtypes = [wintypes.HINSTANCE, wintypes.LPCWSTR, wintypes.UINT,
                                ctypes.c_int, ctypes.c_int, wintypes.UINT]
        u.LoadImageW.restype = wintypes.HANDLE
        u.SendMessageW.argtypes = [wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
        u.SendMessageW.restype = ctypes.c_ssize_t
        hwnd = u.FindWindowW(None, title)
        for size, which in ((32, 1), (16, 0)):
            h = u.LoadImageW(None, str(ico), 1, size, size, 0x8010)
            if hwnd and h:
                u.SendMessageW(hwnd, 0x80, which, h)
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
