"""Run the web interface in an ordinary browser (``python -m personal_warehouse --browser``).

The same ``Api`` object the desktop window uses is exposed over HTTP on 127.0.0.1, with the same method names,
so the page behaves identically.  Handy for trying the UI without pywebview and for automated screenshots.
Only the local machine can connect.
"""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import threading
import webbrowser

from personal_warehouse.webui.api import Api

STATIC = Path(__file__).with_name("static")


class Handler(SimpleHTTPRequestHandler):
    api = None

    def log_message(self, *args):                       # keep the console quiet
        pass

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def do_GET(self):
        if self.path.split("?")[0] in ("/", "/index.html"):           # tell the page to talk HTTP instead of pywebview
            body = (STATIC / "index.html").read_text(encoding="utf-8").replace("<html ", '<html data-http="1" ', 1).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        super().do_GET()

    def do_POST(self):
        name = self.path.rsplit("/", 1)[-1]
        fn = getattr(self.api, name, None) if self.path.startswith("/api/") and not name.startswith("_") else None
        if not callable(fn):
            self.send_error(404)
            return
        try:
            args = json.loads(self.rfile.read(int(self.headers.get("Content-Length") or 0)) or b"[]")
            body = json.dumps(fn(*args), ensure_ascii=False).encode("utf-8")
            code = 200
        except Exception as e:                           # noqa: BLE001 - reported to the page
            body, code = json.dumps({"ok": False, "error": str(e)}).encode("utf-8"), 500
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def make_server(port=0, api=None):
    Handler.api = api or Api()
    return ThreadingHTTPServer(("127.0.0.1", port), partial(Handler, directory=str(STATIC)))


def serve(port=8765, open_browser=True):
    srv = make_server(port)
    url = f"http://127.0.0.1:{srv.server_address[1]}/"
    print(f"Personal Warehouse running at {url}  (Ctrl+C to stop)")
    if open_browser:
        threading.Timer(0.4, lambda: webbrowser.open(url)).start()
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        srv.server_close()
