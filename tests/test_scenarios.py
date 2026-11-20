from concurrent.futures import ThreadPoolExecutor
import os
from pathlib import Path
import random
import sqlite3
import subprocess
import sys

import pytest

from personal_warehouse import config
from personal_warehouse.core import database, stock, transfer
from personal_warehouse.webui.api import Api
from test_webui_api import new_item


def run_child(code, **environment):
    return subprocess.run([sys.executable, "-c", code], capture_output=True, text=True,
                          timeout=30, env=dict(os.environ, PYTHONPATH=str(Path(__file__).resolve().parents[1] / "src"),
                                              PW_DATA_DIR=str(config.DATA_DIR), **environment))


def quantities(item_id):
    with database.db() as connection:
        return connection.execute("SELECT quantity FROM items WHERE id=?", (item_id,)).fetchone()[0]


@pytest.mark.parametrize("field", ["quantity", "min_stock", "purchase_price", "selling_price"])
@pytest.mark.parametrize("value", ["-1", "NaN", "Infinity", "-Infinity", "1e309", "abc", "1.2.3"])
def test_bad_numeric_input_is_atomic(data_dir, field, value):
    result = new_item(Api(), **{field: value})
    assert result["ok"] is False, result
    with database.db() as connection:
        for table in ("items", "movements", "history"):
            assert connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0] == 0


def test_random_movements_match_independent_model(data_dir):
    item_id = new_item(Api(), quantity="20")["id"]
    generator = random.Random(20261120)
    expected = 20
    accepted = 1
    for iteration in range(300):
        movement = generator.choice(config.MOVE_TYPES)
        quantity = generator.randint(0, 30) / 4
        target = expected + quantity if movement == "Stock In" else expected - quantity if movement == "Stock Out" else quantity
        valid = target >= 0 and (quantity > 0 if movement != "Adjustment" else target != expected)
        if valid:
            stock.apply_movement(item_id, movement, quantity, None, str(iteration))
            expected = target
            accepted += 1
        else:
            with pytest.raises(ValueError):
                stock.apply_movement(item_id, movement, quantity, None, str(iteration))
        assert quantities(item_id) == expected
    with database.db() as connection:
        moves = connection.execute("SELECT * FROM movements ORDER BY id").fetchall()
        assert len(moves) == accepted
        for previous, current in zip(moves, moves[1:]):
            assert previous["qty_after"] == current["qty_before"]
        assert moves[-1]["qty_after"] == expected


def test_concurrent_stock_out_never_oversells(data_dir):
    item_id = new_item(Api(), quantity="10")["id"]
    def withdraw(index):
        try:
            stock.apply_movement(item_id, "Stock Out", 1, None, str(index))
            return True
        except ValueError:
            return False
    with ThreadPoolExecutor(max_workers=8) as executor:
        results = list(executor.map(withdraw, range(24)))
    assert sum(results) == 10
    assert quantities(item_id) == 0
    with database.db() as connection:
        assert connection.execute("SELECT COUNT(*) FROM movements").fetchone()[0] == 11


def test_journal_failure_rolls_back_quantity_and_movement(data_dir, monkeypatch):
    item_id = new_item(Api())["id"]
    def fail(*args):
        raise OSError("disk full")
    monkeypatch.setattr(stock, "log", fail)
    with pytest.raises(OSError):
        stock.apply_movement(item_id, "Stock Out", 2, None, "test")
    assert quantities(item_id) == 10
    with database.db() as connection:
        assert connection.execute("SELECT COUNT(*) FROM movements").fetchone()[0] == 1


def test_process_crash_rolls_back_uncommitted_transaction(data_dir):
    item_id = new_item(Api())["id"]
    child = run_child("import os; from personal_warehouse.core.database import db; "
                      "context = db(); connection = context.__enter__(); "
                      "connection.execute('UPDATE items SET quantity=999'); os._exit(17)")
    assert child.returncode == 17, child.stderr
    assert quantities(item_id) == 10
    assert database.verify_db(config.DB_PATH)


def test_process_crash_restore_journal_recovers(data_dir):
    photo = config.PHOTO_DIR / "original.jpg"
    photo.write_bytes(b"original")
    child = run_child("import os; from personal_warehouse import config; "
                      "from personal_warehouse.core.transfer import _prepare_restore_journal; "
                      "photo = config.PHOTO_DIR / 'original.jpg'; "
                      "_prepare_restore_journal([photo]); photo.write_bytes(b'partial'); os._exit(18)")
    assert child.returncode == 18, child.stderr
    transfer.recover_restore()
    assert photo.read_bytes() == b"original"


def test_single_instance_between_processes_and_after_crash(tmp_path):
    code = ("import os; from pathlib import Path; from personal_warehouse.instance import single_instance; "
            "Path.home = classmethod(lambda cls: Path(os.environ['TEST_HOME'])); "
            "context = single_instance(); acquired = context.__enter__(); print(acquired, flush=True); "
            "input()")
    environment = dict(os.environ, PYTHONPATH=str(Path(__file__).resolve().parents[1] / "src"), TEST_HOME=str(tmp_path))
    holder = subprocess.Popen([sys.executable, "-c", code], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE, text=True, env=environment)
    try:
        assert holder.stdout.readline().strip() == "True"
        contender = subprocess.run([sys.executable, "-c", code], input="\n", capture_output=True,
                                   text=True, env=environment, timeout=15)
        assert contender.returncode == 0, contender.stderr
        assert contender.stdout.strip() == "False"
    finally:
        holder.kill()
        holder.communicate(timeout=10)
    successor = subprocess.run([sys.executable, "-c", code], input="\n", capture_output=True,
                               text=True, env=environment, timeout=15)
    assert successor.returncode == 0, successor.stderr
    assert successor.stdout.strip() == "True"


def test_demo_generation_and_export_roundtrip(tmp_path):
    root = Path(__file__).resolve().parents[1]
    destination = tmp_path / "demo"
    result = subprocess.run([sys.executable, str(root / "scripts/create_demo.py"), str(destination)],
                            capture_output=True, text=True, timeout=90)
    assert result.returncode == 0, result.stderr
    with sqlite3.connect(destination / "Database/warehouse.db") as connection:
        assert connection.execute("SELECT COUNT(*) FROM items").fetchone()[0] == 96
        assert connection.execute("SELECT COUNT(*) FROM movements").fetchone()[0] == 144
        assert connection.execute("SELECT COUNT(DISTINCT section || part) FROM items").fetchone()[0] == 24
        assert connection.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
    assert database.verify_db(destination / "Backup/demo.db")
    assert transfer.inspect_package(destination / "Export/demo.pwbak")["items"] == 96
    import csv
    with open(destination / "Export/demo.csv", encoding="utf-8-sig", newline="") as stream:
        assert len(list(csv.reader(stream))) == 97
    from openpyxl import load_workbook
    workbook = load_workbook(destination / "Export/demo.xlsx", read_only=True)
    try:
        assert len(workbook.worksheets) == 3
        assert workbook.worksheets[0].max_row == 97
        assert workbook.worksheets[1].max_row == 145
    finally:
        workbook.close()
    again = subprocess.run([sys.executable, str(root / "scripts/create_demo.py"), str(destination)],
                           capture_output=True, text=True, timeout=15)
    assert again.returncode != 0


@pytest.mark.parametrize("language", ["vi", "en", "ar"])
@pytest.mark.parametrize("theme", ["light", "dark"])
def test_api_language_theme_matrix(data_dir, language, theme):
    api = Api()
    assert api.set_language(language)["ok"]
    assert api.set_theme(theme)["ok"]
    item_id = new_item(api, name="Ốc vít العربية <M8>", name_ar="قطعة")["id"]
    for response in (api.bootstrap(), api.dashboard(), api.inventory(), api.locations(),
                     api.get_item(item_id), api.movements(item_id), api.history_list(), api.suggestions()):
        assert response["ok"], response
    assert api.bootstrap()["theme"] == theme
    assert api.bootstrap()["rtl"] == (language == "ar")


def test_real_qr_image_scan_and_invalid_image(data_dir, tmp_path):
    qrcode = pytest.importorskip("qrcode")
    pytest.importorskip("cv2")
    api = Api()
    item_id = new_item(api, barcode="DEMO-QR-001")["id"]
    image = tmp_path / "mã thử.png"
    qrcode.make("DEMO-QR-001").save(image)
    result = api.scan_image_path(str(image))
    assert result["found"] and result["item_id"] == item_id, result
    result = api.scan_image_path(str(image), "Stock Out", "2")
    assert result["changed"], result
    assert quantities(item_id) == 8
    image.write_bytes(b"invalid image")
    assert api.scan_image_path(str(image))["ok"] is False
    assert quantities(item_id) == 8


def test_migration_backup_includes_uncheckpointed_wal(data_dir):
    item_id = new_item(Api())["id"]
    connection = sqlite3.connect(config.DB_PATH)
    try:
        connection.execute("PRAGMA journal_mode=WAL")
        connection.execute("PRAGMA wal_autocheckpoint=0")
        connection.execute("UPDATE items SET quantity=42 WHERE id=?", (item_id,))
        connection.execute("PRAGMA user_version=1")
        connection.commit()
        database.pre_migration_backup()
        backup = next(config.BACKUP_DIR.glob("before_v*.db"))
        with sqlite3.connect(backup) as copied:
            assert copied.execute("SELECT quantity FROM items").fetchone()[0] == 42
    finally:
        connection.close()
