import importlib.util
import sqlite3
from pathlib import Path

import pytest

from personal_warehouse import config, i18n, settings
from personal_warehouse.core import barcode, database, exporter, formatting, labels, stock


def _add_item(name="Bolt", qty=5, code="WH-00001", **kw):
    with database.db() as con:
        con.execute("INSERT INTO items(item_code,name,section,part,quantity,min_stock,purchase_price,selling_price)"
                    " VALUES(?,?,?,?,?,?,?,?)",
                    (code, name, kw.get("section", "A"), kw.get("part", "1"), qty, kw.get("min_stock", 0),
                     kw.get("buy", 1.0), kw.get("sell", 2.0)))
        return con.execute("SELECT id FROM items WHERE item_code=?", (code,)).fetchone()[0]


def test_num_parsing():
    assert formatting.num("1,234.50", "x") == 1234.5
    assert formatting.num("1,5", "x") == 1.5          # decimal comma
    assert formatting.num("", "x") == 0.0
    with pytest.raises(ValueError):
        formatting.num("abc", "x")
    with pytest.raises(ValueError):
        formatting.num("-1", "x")


def test_locations():
    assert formatting.make_location("A", "1") == "A1"
    assert formatting.parse_location("H3") == ("H", "3")


def test_code128_structure():
    text = "WH-00001"
    bars, total = barcode.code128_bars(text)
    assert total == (len(text) + 2) * 11 + 13   # start + data + checksum symbols, then stop
    assert bars[0] == (0, 2)                     # Code 128-B start symbol begins with a 2-module bar
    assert "<svg" in barcode.code128_svg(text)


def test_init_db_is_idempotent_and_has_columns(data_dir):
    database.init_db()
    con = sqlite3.connect(config.DB_PATH)
    cols = {r[1] for r in con.execute("PRAGMA table_info(items)")}
    assert {"min_stock", "is_active", "barcode", "name_ar"} <= cols
    assert con.execute("PRAGMA user_version").fetchone()[0] == config.SCHEMA_VERSION


def test_old_v2_database_is_upgraded(data_dir):
    """A database from an older version (parts A/B/C, no newer columns) must open and be migrated."""
    config.DB_PATH.unlink()
    con = sqlite3.connect(config.DB_PATH)
    con.executescript("""CREATE TABLE items (id INTEGER PRIMARY KEY AUTOINCREMENT, item_code TEXT UNIQUE,
        name TEXT NOT NULL, category TEXT, description TEXT, engine_application TEXT, section TEXT NOT NULL,
        part TEXT NOT NULL, condition TEXT NOT NULL DEFAULT 'New', quantity REAL NOT NULL DEFAULT 0,
        unit TEXT NOT NULL DEFAULT 'pcs', purchase_price REAL NOT NULL DEFAULT 0,
        selling_price REAL NOT NULL DEFAULT 0, photo_path TEXT, date_added TEXT, supplier TEXT, notes TEXT,
        created_at TEXT, updated_at TEXT);
        CREATE TABLE movements (id INTEGER PRIMARY KEY AUTOINCREMENT, item_id INTEGER NOT NULL,
        movement_type TEXT NOT NULL, quantity REAL NOT NULL, reason TEXT, movement_date TEXT NOT NULL);
        INSERT INTO items(item_code,name,section,part,quantity) VALUES('WH-00001','Old','A','B',4);
        PRAGMA user_version=1;""")
    con.close()
    database.pre_migration_backup()
    database.init_db()
    with database.db() as c:
        row = c.execute("SELECT part,is_active,min_stock FROM items").fetchone()
    assert (row["part"], row["is_active"], row["min_stock"]) == ("2", 1, 0)
    assert list(config.BACKUP_DIR.glob("before_v*.db"))          # old database was copied first


def test_movement_log_roundtrip(data_dir):
    iid = _add_item(qty=5)
    with database.db() as con:
        database.record_movement(con, iid, "Stock In", 3, "test", 1.5, 5, 8)
        r = con.execute("SELECT * FROM movements").fetchone()
    assert (r["qty_before"], r["qty_after"], r["unit_price"]) == (5, 8, 1.5)


def test_apply_movement_rules(data_dir):
    iid = _add_item(qty=5)
    _, before, after = stock.apply_movement(iid, "Stock In", 3, 1.0, "r")
    assert (before, after) == (5, 8)
    assert stock.apply_movement(iid, "Stock Out", 8, 2.0, "")[2] == 0
    with pytest.raises(ValueError):                       # cannot go below zero
        stock.apply_movement(iid, "Stock Out", 1, 2.0, "")
    assert stock.apply_movement(iid, "Adjustment", 7, None, "count")[2] == 7
    with pytest.raises(ValueError):                       # adjustment to the same number is rejected
        stock.apply_movement(iid, "Adjustment", 7, None, "")
    with database.db() as con:
        assert con.execute("SELECT COUNT(*) FROM movements").fetchone()[0] == 3


def test_find_item_variants(data_dir):
    iid = _add_item(code="WH-00042")
    with database.db() as con:
        con.execute("UPDATE items SET barcode='ABC123' WHERE id=?", (iid,))
    assert stock.find_item("wh-00042")[0]["id"] == iid                       # case-insensitive code
    assert stock.find_item("ABC123")[0]["id"] == iid                         # manufacturer barcode
    assert stock.find_item("WAREHOUSE ITEM WH-00042\nName: Bolt")[0]["id"] == iid   # full QR payload
    assert stock.find_item("42")[0]["id"] == iid                             # bare number
    assert stock.find_item("nothing")[0] is None
    assert stock.find_item("")[0] is None


def test_settings_keep_unrelated_keys(data_dir):
    settings.save_settings(lang="en", theme="dark")
    settings.save_settings(auto_update=False)
    settings.save_settings(notified_version="3.1.0")      # later saves must not drop earlier keys
    st = settings.load_settings()
    assert st == {"lang": "en", "theme": "dark", "auto_update": False, "notified_version": "3.1.0"}


def test_every_text_has_all_three_languages():
    assert len(i18n.TR) > 200
    for key, d in i18n.TR.items():
        assert set(d) == {"vi", "en", "ar"} and all(d.values()), key


def test_format_placeholders_match_across_languages():
    """A {0}/{1} that exists in one language but not another would crash or hide data in that language."""
    import re
    for key, d in i18n.TR.items():
        slots = {lang: sorted(set(re.findall(r"\{\d+\}", text))) for lang, text in d.items()}
        assert slots["vi"] == slots["en"] == slots["ar"], key


def test_language_switch():
    i18n.set_language("en")
    assert i18n.tr("nav_inventory") == "Inventory"
    i18n.set_language("vi")
    assert i18n.tr("nav_inventory") == "Kho hàng"
    i18n.set_language("xx")                                # unknown codes are ignored
    assert i18n.current_lang() == "vi"
    assert i18n.cond_t("Used") == "Đã dùng"
    assert i18n.from_label(config.CONDITIONS, i18n.cond_t, "Đã dùng") == "Used"


def test_label_html_barcode_only():
    row = {"item_code": "WH-00001", "name": "Bolt <M8>", "name_ar": None, "category": "Fasteners",
           "engine_application": "", "section": "A", "part": "1", "condition": "New"}
    html_text = labels.build_label_html([row], {"layout": "a4", "size": "Medium 70×40 mm", "kind": "barcode",
                                                "copies": 2, "full": False, "prices": False})
    assert html_text.count('class="label"') == 2
    assert "Bolt &lt;M8&gt;" in html_text           # user text is escaped


def test_export_csv_and_missing_excel(data_dir, tmp_path):
    _add_item(name="Bolt, \"M8\"")
    out = tmp_path / "out.csv"
    exporter.export_inventory(out)
    text = out.read_text(encoding="utf-8-sig")
    assert "WH-00001" in text and '"Bolt, ""M8"""' in text          # csv quoting survives
    try:
        import openpyxl  # noqa: F401
    except ImportError:
        with pytest.raises(exporter.ExcelUnavailable):
            exporter.export_inventory(tmp_path / "out.xlsx")
    else:
        exporter.export_inventory(tmp_path / "out.xlsx", rtl=True)
        assert (tmp_path / "out.xlsx").stat().st_size > 0


def test_changelog_extract():
    spec = importlib.util.spec_from_file_location(
        "extract_notes", Path(__file__).resolve().parents[1] / "packaging" / "extract_notes.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    text = "# Changelog\n\n## [3.1.0] - x\n- new\n\n## [3.0.0] - y\n- old\n"
    assert mod.extract(text, "3.1.0") == "- new"
    assert mod.extract(text, "9.9.9") == ""


def test_core_layers_do_not_import_tkinter():
    """Architecture guard: config / i18n / core / settings / updater / main must stay usable without a GUI."""
    import os
    import subprocess
    import sys
    code = ("import sys, personal_warehouse.main, personal_warehouse.updater, personal_warehouse.core.stock, "
            "personal_warehouse.core.exporter, personal_warehouse.core.labels, personal_warehouse.core.scanning, "
            "personal_warehouse.i18n, personal_warehouse.settings; "
            "bad = [m for m in sys.modules if m == 'tkinter' or m.startswith('tkinter.')]; "
            "assert not bad, bad")
    env = dict(os.environ, PYTHONPATH=str(Path(__file__).resolve().parents[1] / "src"))
    r = subprocess.run([sys.executable, "-c", code], env=env, capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
