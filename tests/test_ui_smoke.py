"""Builds and drives the real window code against a fake Tk (see conftest.fake_tk).

This does not check how anything looks. It checks that every page builds in every language and theme, that
the pages are wired to each other and to the core layer, and that the main user flows change the database.
"""
import importlib
from types import SimpleNamespace

import pytest

from personal_warehouse import config, i18n
from personal_warehouse.core import database


@pytest.fixture()
def ui(fake_tk, data_dir):
    theme = importlib.import_module("personal_warehouse.ui.theme")
    app_mod = importlib.import_module("personal_warehouse.ui.app")
    i18n.set_language("en")
    theme.set_theme("light")
    return SimpleNamespace(app=app_mod, theme=theme, fake=fake_tk, win=app_mod.WarehouseApp())


def _rows(sql, *args):
    with database.db() as con:
        return con.execute(sql, args).fetchall()


@pytest.mark.parametrize("lang", ["vi", "en", "ar"])
@pytest.mark.parametrize("theme", ["light", "dark"])
def test_builds_in_every_language_and_theme(fake_tk, data_dir, lang, theme):
    ui_theme = importlib.import_module("personal_warehouse.ui.theme")
    app_mod = importlib.import_module("personal_warehouse.ui.app")
    i18n.set_language(lang)
    ui_theme.set_theme(theme)
    win = app_mod.WarehouseApp()
    assert win.rtl == (lang == "ar")
    win.rebuild()                                        # what switching language / theme does
    i18n.set_language("vi")


def test_item_form_saves_and_edits(ui):
    w = ui.win
    w.new_item()
    w.fields["name"].set("Oil filter")
    w.fields["category"].set("Filters")
    w.fields["quantity"].set("4")
    w.fields["min_stock"].set("2")
    w.fields["purchase_price"].set("3.5")
    w.fields["selling_price"].set("6")
    w.fields["section"].set("B")
    w.fields["part"].set("2")
    w.save_item()
    row = _rows("SELECT * FROM items")[0]
    assert (row["item_code"], row["name"], row["section"], row["part"], row["quantity"]) == \
           ("WH-00001", "Oil filter", "B", "2", 4)
    assert _rows("SELECT movement_type FROM movements")[0][0] == "Opening stock"

    w.edit_item(row["id"])
    assert w.fields["name"].get() == "Oil filter"
    w.fields["name"].set("Oil filter XL")
    w.save_item()
    assert _rows("SELECT name, quantity FROM items")[0][:] == ("Oil filter XL", 4)   # edit never touches stock


def test_item_form_rejects_bad_input(ui):
    w = ui.win
    w.new_item()
    w.save_item()                                         # no name
    w.fields["name"].set("X")
    w.fields["purchase_price"].set("abc")
    w.save_item()                                         # not a number
    assert _rows("SELECT COUNT(*) FROM items")[0][0] == 0
    assert ui.fake.messagebox.showerror.call_count == 2


def test_movement_page_changes_stock(ui):
    w = ui.win
    iid = None
    with database.db() as con:
        con.execute("INSERT INTO items(item_code,name,section,part,quantity) VALUES('WH-00001','Bolt','A','1',10)")
        iid = con.execute("SELECT id FROM items").fetchone()[0]
    w.refresh_all()
    assert iid in w.item_choice_map.values()
    w.go_movement(iid)
    w.mov_qty.set("4")
    w.save_movement()                                     # default movement type is Stock In
    assert _rows("SELECT quantity FROM items")[0][0] == 14
    w.mov_type.set(i18n.mv_t("Stock Out"))
    w.mov_qty.set("20")
    w.save_movement()                                     # too much: refused
    assert _rows("SELECT quantity FROM items")[0][0] == 14
    assert len(_rows("SELECT * FROM movements")) == 1


def test_scan_lookup_and_scan_stock_out(ui):
    w = ui.win
    with database.db() as con:
        con.execute("INSERT INTO items(item_code,name,section,part,quantity,min_stock) "
                    "VALUES('WH-00007','Gasket','C','3',5,3)")
    w.refresh_all()
    found, _ = w.handle_scan("WH-00007")
    assert found and _rows("SELECT quantity FROM items")[0][0] == 5     # lookup never changes stock
    w.scan_mode.set(i18n.mv_t("Stock Out"))
    w.scan_qty.set("3")
    found, banner = w.handle_scan("WH-00007")
    assert found and _rows("SELECT quantity FROM items")[0][0] == 2
    assert _rows("SELECT reason FROM movements")[0][0] == "Scan"
    assert w.handle_scan("WH-99999")[0] is False
    assert w.handle_scan("hello")[0] is False


def test_archive_and_dashboard_refresh(ui):
    w = ui.win
    with database.db() as con:
        con.execute("INSERT INTO items(item_code,name,section,part,quantity) VALUES('WH-00001','A','A','1',0)")
        con.execute("INSERT INTO items(item_code,name,section,part,quantity,min_stock) "
                    "VALUES('WH-00002','B','H','3',1,5)")
    w.refresh_all()
    assert w.metric_vars["alerts"].get() == "2"          # one out of stock + one below minimum
    w.inv_tree.selection = lambda: ["1"]
    w.archive_selected()
    assert _rows("SELECT is_active FROM items WHERE id=1")[0][0] == 0


def test_export_and_backup_actions(ui, tmp_path):
    w = ui.win
    with database.db() as con:
        con.execute("INSERT INTO items(item_code,name,section,part) VALUES('WH-00001','A','A','1')")
    ui.fake.filedialog.asksaveasfilename = lambda **k: str(tmp_path / "inv.csv")
    w.export_excel()
    assert "WH-00001" in (tmp_path / "inv.csv").read_text(encoding="utf-8-sig")
    ui.fake.filedialog.askdirectory = lambda **k: str(tmp_path / "bk")
    (tmp_path / "bk").mkdir()
    w.backup_all()
    assert list((tmp_path / "bk").glob("MyWarehouse_Backup_*/Database/warehouse.db"))


def test_print_labels_writes_page(ui, monkeypatch):
    from personal_warehouse.ui.features import labels as labels_feature
    opened = []
    monkeypatch.setattr(labels_feature.webbrowser, "open", opened.append)
    options = {"layout": "printer", "size": "Small 50×30 mm", "kind": "barcode", "copies": 2,
               "full": False, "prices": False}
    monkeypatch.setattr(labels_feature, "LabelDialog", lambda *a, **k: SimpleNamespace(result=options))
    with database.db() as con:
        con.execute("INSERT INTO items(item_code,name,section,part) VALUES('WH-00001','A','A','1')")
    ui.win.print_labels([1])
    page = next(config.LABEL_DIR.glob("labels_*.html"))
    assert page.read_text(encoding="utf-8").count('class="label"') == 2 and opened


def test_update_check_flow(ui, monkeypatch):
    from personal_warehouse.ui.features import updates as upd
    release = {"version": "99.0.0", "page": "https://github.com/o/r/releases/tag/v99.0.0", "download": "", "notes": "n"}
    monkeypatch.setattr(upd.updater, "check", lambda: {"status": "new", "release": release, "error": ""})
    opened = []
    monkeypatch.setattr(upd.webbrowser, "open", opened.append)
    w = ui.win
    w.check_updates(manual=True)
    for _ in range(50):                                   # the worker thread finishes almost at once
        if w._upd["finished"]:
            break
        __import__("time").sleep(0.02)
    w._update_poll()
    assert opened == [release["page"]]
