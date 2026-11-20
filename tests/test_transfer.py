"""Moving data to another computer: one .pwbak file, restore, online sync folder."""
import json
import zipfile

import pytest

from personal_warehouse import config
from personal_warehouse.core import transfer
from personal_warehouse.core.database import db
from personal_warehouse.i18n import set_language
from personal_warehouse.webui.api import Api

from test_webui_api import new_item


@pytest.fixture()
def api(data_dir):
    set_language("en")
    return Api()


def _count():
    with db() as con:
        return con.execute("SELECT COUNT(*) FROM items").fetchone()[0]


def test_export_then_restore_on_a_fresh_computer(api, data_dir, tmp_path, monkeypatch):
    (config.PHOTO_DIR).mkdir(exist_ok=True)
    (config.PHOTO_DIR / "a.jpg").write_bytes(b"jpgdata")
    iid = new_item(api, name="Brake pad")["id"]
    api.save_movement({"item_id": iid, "type": "Stock In", "qty": "5"})
    pkg = tmp_path / "x.pwbak"
    m = transfer.create_package(pkg)
    assert m["items"] == 1 and m["movements"] == 2 and m["photos"] == 1

    # "new computer": empty data folder
    new = tmp_path / "newpc"
    new.mkdir()
    for name, sub in (("DATA_DIR", ""), ("PHOTO_DIR", "Photos"), ("BACKUP_DIR", "Backup")):
        monkeypatch.setattr(config, name, new / sub if sub else new)
    (new / "Photos").mkdir(); (new / "Backup").mkdir()
    monkeypatch.setattr(config, "DB_PATH", new / "warehouse.db")
    monkeypatch.setattr(config, "SETTINGS_PATH", new / "settings.json")
    from personal_warehouse.core.database import init_db
    init_db()
    assert _count() == 0
    r = api.restore_inspect(str(pkg))
    assert r["ok"] and "1 item" in r["message"] and "replaced" not in r["message"]
    d = api.restore_apply(str(pkg))
    assert d["ok"] and _count() == 1
    assert (new / "Photos" / "a.jpg").read_bytes() == b"jpgdata"
    assert api.movements(iid)["rows"]


def test_restore_replaces_and_keeps_undo_copy(api, data_dir, tmp_path):
    new_item(api, name="One")
    pkg = tmp_path / "one.pwbak"
    transfer.create_package(pkg)
    new_item(api, name="Two", section="B")
    assert _count() == 2
    assert "replaced" in api.restore_inspect(str(pkg))["message"]
    assert api.restore_apply(str(pkg))["ok"] and _count() == 1
    undo = sorted((data_dir / "Backup").glob("before_restore_*.pwbak"))
    assert len(undo) == 1
    assert api.restore_apply(str(undo[0]))["ok"] and _count() == 2           # undo works


def test_bad_packages_are_refused_and_data_untouched(api, data_dir, tmp_path):
    new_item(api)
    junk = tmp_path / "junk.pwbak"
    junk.write_text("hello")
    assert api.restore_inspect(str(junk))["ok"] is False
    zf = tmp_path / "other.pwbak"
    with zipfile.ZipFile(zf, "w") as z:
        z.writestr("readme.txt", "x")
    assert api.restore_apply(str(zf))["ok"] is False
    good = tmp_path / "g.pwbak"
    transfer.create_package(good)
    bad_db = tmp_path / "bad.pwbak"
    with zipfile.ZipFile(good) as src, zipfile.ZipFile(bad_db, "w") as out:
        for n in src.namelist():
            out.writestr(n, b"not a database" * 50 if n.endswith(".db") else src.read(n))
    assert api.restore_apply(str(bad_db))["ok"] is False
    newer = tmp_path / "new.pwbak"
    with zipfile.ZipFile(good) as src, zipfile.ZipFile(newer, "w") as out:
        for n in src.namelist():
            if n == "manifest.json":
                mm = json.loads(src.read(n)); mm["schema"] = 999
                out.writestr(n, json.dumps(mm))
            else:
                out.writestr(n, src.read(n))
    r = api.restore_apply(str(newer))
    assert r["ok"] is False and "newer" in r["error"]
    assert _count() == 1


def test_zip_slip_photo_names_stay_inside_photo_folder(api, data_dir, tmp_path):
    good = tmp_path / "g.pwbak"
    transfer.create_package(good)
    evil = tmp_path / "evil.pwbak"
    with zipfile.ZipFile(good) as src, zipfile.ZipFile(evil, "w") as out:
        for n in src.namelist():
            out.writestr(n, src.read(n))
        out.writestr("Photos/../../escaped.txt", "x")
    assert api.restore_apply(str(evil))["ok"]
    assert not (data_dir.parent / "escaped.txt").exists()
    assert (config.PHOTO_DIR / "escaped.txt").exists()


def test_sync_folder_keeps_newest_and_runs_on_quit(api, data_dir, tmp_path):
    from personal_warehouse.settings import save_settings
    cloud = tmp_path / "OneDrive"
    cloud.mkdir()
    for d in range(1, 10):                                  # nine old days
        (cloud / f"MyWarehouse_2020010{d}.pwbak").write_bytes(b"x")
    new_item(api)
    save_settings(sync_dir=str(cloud))
    assert api.sync_now()["ok"]
    files = sorted(cloud.glob("*.pwbak"))
    assert len(files) == transfer.KEEP_SYNC_COPIES
    assert transfer.latest_in_folder(cloud) == files[-1]
    assert transfer.inspect_package(files[-1])["items"] == 1
    new_item(api, name="Second", section="B")
    api.quit()                                              # closing the app refreshes the online copy
    assert transfer.inspect_package(files[-1])["items"] == 2
    assert api.sync_off()["ok"] and api.bootstrap()["sync_dir"] == ""
    save_settings(sync_dir=str(tmp_path / "missing"))
    assert api.sync_now()["ok"] is False
    api.quit()                                              # a missing folder must never block closing
