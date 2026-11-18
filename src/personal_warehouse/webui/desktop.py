"""Desktop window: the web interface inside a native window (pywebview, WebView2 on Windows)."""
from pathlib import Path

from personal_warehouse.core.database import auto_backup
from personal_warehouse.i18n import tr
from personal_warehouse.webui.api import Api

STATIC = Path(__file__).with_name("static")


def run():
    """Open the window and block until it is closed. Raises ImportError when pywebview is not installed."""
    import webview
    api = Api()
    window = webview.create_window(
        tr("app_name"), url=str(STATIC / "index.html"), js_api=api, width=1360, height=860,
        min_size=(940, 600), background_color="#FFF3E0", text_select=False)
    api._attach(window)
    window.events.closed += lambda: auto_backup(overwrite=True)
    webview.start()
