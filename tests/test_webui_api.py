"""The web interface's Python bridge: every rule is exercised through the same calls the page makes."""
import json
import threading
import urllib.request

import pytest

from personal_warehouse.i18n import set_language
from personal_warehouse.webui.api import Api


@pytest.fixture()
def api(data_dir):
    set_language("en")
    return Api()


def new_item(api, **kw):
    v = dict(name="Oil filter", section="A", part="1", condition="New", unit="pcs", quantity="10", min_stock="3",
             purchase_price="5", selling_price="9", confirmed=["duplicate"])
    v.update(kw)
    return api.save_item(v)


def test_bootstrap_has_texts_and_options(api):
    b = api.bootstrap()
    assert b["ok"] and b["lang"] == "en" and not b["rtl"]
    assert b["strings"]["nav_dashboard"] == "Dashboard"
    assert len(b["locations"]) == 1 + 3 + 24
    assert api.set_language("ar")["rtl"] is True
    assert api.set_language("vi")["strings"]["nav_dashboard"] != "Dashboard"


def test_save_item_validation_and_confirmations(api):
    assert api.save_item({"name": ""})["error"]
    r = new_item(api, selling_price="2")                       # below cost -> asks first
    assert r["needs_confirm"] == "price_below"
    r = new_item(api, selling_price="2", confirmed=["price_below", "duplicate"])
    assert r["ok"] and r["id"] == 1
    r = new_item(api, confirmed=[])                             # same name + place -> duplicate question
    assert r["needs_confirm"] == "duplicate"
    assert new_item(api, name="Other", barcode="BC1")["ok"]
    assert "BC1" in new_item(api, name="Third", barcode="BC1")["error"]
    assert new_item(api, quantity="abc", name="Bad")["ok"] is False


def test_edit_keeps_quantity_and_returns_barcode(api):
    iid = new_item(api)["id"]
    got = api.get_item(iid)
    assert got["item"]["item_code"] == "WH-00001" and "<svg" in got["barcode_svg"]
    v = dict(got["item"], id=iid, quantity="999", name="Renamed", current_photo=None)
    assert api.save_item(v)["ok"]
    assert api.get_item(iid)["item"]["quantity"] == "10"     # quantity is only changed by movements
    assert api.get_item(iid)["item"]["name"] == "Renamed"


def test_movements_and_dashboard(api):
    iid = new_item(api, quantity="4", min_stock="3")["id"]
    assert "Only 4" in api.save_movement({"item_id": iid, "type": "Stock Out", "qty": "9"})["error"]
    assert api.save_movement({"item_id": iid, "type": "Stock Out", "qty": "2", "price": "9"})["warn"] is True
    assert api.save_movement({"item_id": iid, "type": "Stock In", "qty": "0"})["ok"] is False
    assert api.save_movement({"item_id": iid, "type": "Adjustment", "qty": "50"})["ok"]
    assert [m["type"] for m in api.movements(iid)["rows"]][:2] == ["Adjustment", "Stock Out"]
    d = api.dashboard()
    assert d["ok"] and d["kpis"]["units"]["value"] == "50" and d["remind"] is None
    assert d["trend"][-1]["out"] == 2 and len(d["trend"]) == 14
    assert api.item_info(iid, "Stock In")["price"] == "5.00"
    assert api.movement_items("oil")["items"][0]["id"] == iid


def test_inventory_filters_sort_and_archive(api):
    a = new_item(api, name="Alpha", section="B", part="2", quantity="0")["id"]
    new_item(api, name="Beta", quantity="50")
    assert len(api.inventory({})["rows"]) == 2
    assert [r["name"] for r in api.inventory({"low_only": True})["rows"]] == ["Alpha"]
    assert api.inventory({"search": "bet"})["rows"][0]["name"] == "Beta"
    assert [r["name"] for r in api.inventory({"location": "loc:B2"})["rows"]] == ["Alpha"]
    assert [r["name"] for r in api.inventory({"location": "sec:A"})["rows"]] == ["Beta"]
    assert [r["name"] for r in api.inventory({"sort": "name", "desc": True})["rows"]] == ["Beta", "Alpha"]
    assert api.toggle_archive(a)["needs_confirm"]
    assert api.toggle_archive(a, True)["ok"]
    assert len(api.inventory({})["rows"]) == 1 and len(api.inventory({"archived": True})["rows"]) == 2
    assert "Restored" in api.toggle_archive(a)["message"]
    assert "x" not in api.inventory({"sort": "'; DROP TABLE items;--"})["summary"]   # unknown sort column is ignored


def test_scan_lookup_and_stock_modes(api):
    iid = new_item(api, quantity="5")["id"]
    r = api.scan("WH-00001")
    assert r["found"] and r["item_id"] == iid and r["can_move"]
    assert api.scan("1")["found"]                                # bare number
    r = api.scan("WH-00001", "Stock In", "3")
    assert r["changed"] and "8" in r["flash"]
    r = api.scan("WH-00001", "Stock Out", "100")
    assert r["flash_ok"] is False and not r["changed"]
    assert api.scan("WH-00099")["found"] is False
    assert api.scan("hello")["found"] is False


def test_locations_map(api):
    new_item(api, section="C", part="3", quantity="7")
    cell = [c for s in api.locations()["sections"] for c in s["cells"] if c["code"] == "C3"][0]
    assert cell["n"] == 1 and cell["units"] == "7"
    m = api.locations()
    assert m["total"]["slots"] == 24 and m["total"]["used"] == 1 and m["total"]["items"] == 1
    assert [z["section"] for z in m["sections"]] == ["A", "B", "C"] and all(len(z["cells"]) == 8 for z in m["sections"])
    assert m["sections"][2]["used"] == 1 and m["sections"][2]["units"] == "7" and cell["names"]


def test_delete_items_removes_history_and_makes_backup(api, data_dir):
    a = new_item(api, name="Alpha")["id"]
    b = new_item(api, name="Beta", section="B")["id"]
    api.save_movement({"item_id": a, "type": "Stock In", "qty": "5"})
    assert api.delete_items([])["ok"] is False
    q = api.delete_items([a, b])
    assert q["needs_confirm"] and "3" in q["message"]                # 2 items, 3 movements (2 opening + 1 in)
    assert api.inventory({})["rows"] and len(api.inventory({})["rows"]) == 2   # nothing happens before confirming
    r = api.delete_items([a], True)
    assert r["ok"] and r["count"] == 1
    assert [x["name"] for x in api.inventory({"archived": True})["rows"]] == ["Beta"]
    assert api.movements(a)["rows"] == []
    assert list((data_dir / "Backup").glob("before_delete_*.db"))
    assert api.delete_items([a], True)["ok"] is False                # already gone


def test_layout_is_three_sections_by_eight_parts_and_old_places_survive(api, data_dir):
    from personal_warehouse import config
    from personal_warehouse.core.database import db
    assert config.SECTIONS == ["A", "B", "C"] and config.PARTS == [str(i) for i in range(1, 9)]
    assert new_item(api, section="C", part="8")["ok"]
    assert new_item(api, name="X", section="D", part="1")["ok"] is False          # D is not on the map any more
    iid = new_item(api, name="Old")["id"]
    with db() as con:                                                              # an item saved under the old layout
        con.execute("UPDATE items SET section='F', part='2' WHERE id=?", (iid,))
    d = api.dashboard()
    assert [s["s"] for s in d["sections"]] == ["A", "B", "C", "F"]                 # its stock is still counted
    loc = api.locations()
    assert [c["code"] for c in loc["legacy"]] == ["F2"] and len(loc["sections"]) == 3 and len(loc["sections"][0]["cells"]) == 8
    v = api.get_item(iid)["item"]
    assert api.save_item(dict(v, id=iid, name="Old renamed", current_photo=None))["ok"]   # can still be edited in place
    assert api.save_item(dict(v, id=iid, section="C", part="1", current_photo=None))["ok"]  # and moved to the new map


def test_labels_export_backup(api, data_dir, monkeypatch):
    import webbrowser
    opened = []
    monkeypatch.setattr(webbrowser, "open", lambda u: opened.append(u))
    iid = new_item(api)["id"]
    assert api.print_labels([], {})["ok"] is False
    r = api.print_labels([iid], {"kind": "barcode", "layout": "a4", "size": "Medium 70×40 mm", "copies": 2})
    assert r["ok"] and opened and "labels_" in opened[0]
    assert api.print_labels([iid] * 9, {"kind": "barcode", "copies": 300})["needs_confirm"]
    r = api.export_excel()
    assert r["ok"] and (data_dir / "Export").glob("*.xlsx")
    assert api.backup_all()["ok"]


def test_http_bridge_serves_page_and_api(api):
    from personal_warehouse.webui.server import make_server
    srv = make_server(0, api)
    port = srv.server_address[1]
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    try:
        html = urllib.request.urlopen(f"http://127.0.0.1:{port}/").read().decode()
        assert 'data-http="1"' in html
        req = urllib.request.Request(f"http://127.0.0.1:{port}/api/bootstrap", data=b"[]", method="POST")
        assert json.load(urllib.request.urlopen(req))["ok"] is True
        bad = urllib.request.Request(f"http://127.0.0.1:{port}/api/_attach", data=b"[]", method="POST")
        with pytest.raises(urllib.error.HTTPError):
            urllib.request.urlopen(bad)                          # private methods are not reachable
    finally:
        srv.shutdown()


# ---------------------------------------------------------------------------------------------- in-app update
def _release(**kw):
    rel = {"version": "9.9.9", "page": "https://github.com/o/r/releases/tag/v9.9.9", "notes": "- better",
           "download": "https://github.com/o/r/releases/download/v9.9.9/PersonalWarehouse-Setup-9.9.9.exe",
           "sha256": "", "size": 0}
    rel.update(kw)
    return rel


def test_update_offers_install_only_in_the_installed_desktop_app(api, monkeypatch):
    from personal_warehouse import updater
    monkeypatch.setattr(updater, "check", lambda: {"status": "new", "release": _release(), "error": ""})
    r = api.check_updates(False)
    assert r["status"] == "new" and r["can_install"] is False and r["url"].endswith(".exe")   # no window -> browser fallback
    api._window = object()
    monkeypatch.setattr(updater, "can_self_update", lambda: True)
    assert api.check_updates(False)["can_install"] is True
    assert api.check_updates(False)["status"] == "new"        # "Later" is not remembered: asked again next launch


def test_update_is_silent_when_offline_or_store(api, monkeypatch):
    from personal_warehouse import updater
    monkeypatch.setattr(updater, "check", lambda: {"status": "error", "release": None, "error": "offline"})
    assert api.check_updates(False)["status"] == "skip"
    assert api.check_updates(True)["ok"] is False
    monkeypatch.setattr(updater, "is_store_package", lambda: True)
    assert api.check_updates(False)["status"] == "skip"
    assert api.check_updates(True)["status"] == "store"


def test_update_download_then_install(api, monkeypatch, tmp_path):
    import time
    from personal_warehouse import updater
    api._window = type("W", (), {"destroy": lambda self: closed.append(1)})()
    closed, launched = [], []
    monkeypatch.setattr(updater, "can_self_update", lambda: True)
    monkeypatch.setattr(updater, "update_dir", lambda: tmp_path)
    monkeypatch.setattr(updater, "check", lambda: {"status": "new", "release": _release(), "error": ""})
    monkeypatch.setattr(updater, "launch_installer", launched.append)

    def fake_download(url, dest, sha256="", size=0, progress=None, cancelled=None, **kw):
        dest.write_bytes(b"MZ")
        progress(2, 2)
        return dest
    monkeypatch.setattr(updater, "download", fake_download)
    assert api.update_install()["ok"] is False                 # nothing downloaded yet
    api.check_updates(False)
    assert api.update_start()["ok"]
    for _ in range(50):
        st = api.update_status()
        if st["finished"]:
            break
        time.sleep(0.05)
    assert st["finished"] and not st["error"] and st["percent"] == 100
    r = api.update_install()
    assert r["ok"] and len(launched) == 1 and launched[0].endswith("PersonalWarehouse-Setup-9.9.9.exe")
    time.sleep(1.2)
    assert closed == [1]                                       # the app closes itself so the installer can replace files


def test_update_download_failure_and_cancel(api, monkeypatch, tmp_path):
    import time
    from personal_warehouse import updater
    api._window = object()
    monkeypatch.setattr(updater, "can_self_update", lambda: True)
    monkeypatch.setattr(updater, "update_dir", lambda: tmp_path)
    monkeypatch.setattr(updater, "check", lambda: {"status": "new", "release": _release(), "error": ""})

    def boom(*a, **k):
        raise ValueError("Downloaded file failed the SHA-256 check")
    monkeypatch.setattr(updater, "download", boom)
    api.check_updates(False)
    api.update_start()
    for _ in range(50):
        st = api.update_status()
        if st["finished"]:
            break
        time.sleep(0.05)
    assert "SHA-256" in st["error"]
    assert api.update_install()["ok"] is False                 # a failed download is never installed
