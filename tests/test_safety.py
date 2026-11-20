"""Everything is recoverable: change history + undo, photo trash, verified backups, encrypted packages."""
from datetime import date, timedelta

import pytest

from personal_warehouse import config
from personal_warehouse.core import database, history, transfer
from personal_warehouse.core.database import db
from personal_warehouse.i18n import set_language
from personal_warehouse.webui.api import Api

from test_webui_api import new_item


@pytest.fixture()
def api(data_dir):
    set_language("en")
    return Api()


def item(api, iid):
    return api.get_item(iid)["item"]


def row(iid):
    with db() as con:
        return con.execute("SELECT * FROM items WHERE id=?", (iid,)).fetchone()


def edit(api, iid, **kw):
    v = dict(item(api, iid), id=iid, current_photo=None, confirmed=["price_below"])
    v.update(kw)
    return api.save_item(v)


def undo(api, entry):
    r = api.history_undo(entry, True)
    assert r["ok"], r
    return r


def last(api, action=None):
    rows = [h for h in api.history_list()["rows"] if action in (None, h["action"])]
    return rows[0]["id"]


def test_edit_is_journaled_and_undone(api):
    iid = new_item(api, name="Filter", selling_price="20")["id"]
    assert edit(api, iid, name="Filter XL", selling_price="25")["ok"]
    h = api.history_list()["rows"][0]
    assert h["action"] == "update" and "Filter XL" in h["detail"]
    undo(api, h["id"])
    assert item(api, iid)["name"] == "Filter" and float(item(api, iid)["selling_price"]) == 20
    assert api.history_undo(h["id"], True)["ok"] is False             # cannot undo twice
    redo = last(api)
    undo(api, redo)                                                     # undo of the undo = redo
    assert item(api, iid)["name"] == "Filter XL"


def test_unchanged_save_adds_no_entry(api):
    iid = new_item(api)["id"]
    n = len(api.history_list()["rows"])
    edit(api, iid)
    assert len(api.history_list()["rows"]) == n


def test_undo_refuses_when_item_changed_since(api):
    iid = new_item(api, name="A")["id"]
    edit(api, iid, name="B")
    first = last(api)
    edit(api, iid, name="C")
    r = api.history_undo(first, True)
    assert r["ok"] is False and "newer" in r["error"]
    assert item(api, iid)["name"] == "C"
    undo(api, last(api))                                                # newest first works
    undo(api, first)
    assert item(api, iid)["name"] == "A"


def test_archive_and_restore_undo(api):
    iid = new_item(api)["id"]
    assert api.toggle_archive(iid, True)["ok"]
    undo(api, last(api))
    assert row(iid)["is_active"] == 1


def test_delete_can_be_undone_with_history_and_photo(api, data_dir, tmp_path):
    src = tmp_path / "p.jpg"
    src.write_bytes(b"photo")
    iid = new_item(api, name="Gear", photo_path=str(src))["id"]
    stored = item(api, iid)["photo_path"]
    api.save_movement({"item_id": iid, "type": "Stock Out", "qty": "4"})
    assert (config.PHOTO_DIR / stored).exists()
    assert api.delete_items([iid], True)["ok"]
    assert not (config.PHOTO_DIR / stored).exists() and (config.TRASH_DIR / stored).exists()   # trashed, not erased
    assert api.get_item(iid)["ok"] is False
    entry = last(api, "delete")
    undo(api, entry)
    back = row(iid)
    assert back["name"] == "Gear" and back["item_code"] == f"WH-{iid:05d}" and back["quantity"] == 6
    assert (config.PHOTO_DIR / stored).read_bytes() == b"photo"
    assert len(api.movements(iid)["rows"]) == 2                          # opening stock + the stock-out
    assert api.history_undo(entry, True)["ok"] is False


def test_undo_create_only_when_untouched(api):
    a = new_item(api, name="Fresh")["id"]
    undo(api, last(api, "create"))
    assert api.get_item(a)["ok"] is False
    undo(api, last(api, "delete"))                                       # and it comes back
    assert item(api, a)["name"] == "Fresh"
    api.save_movement({"item_id": a, "type": "Stock In", "qty": "1"})
    assert api.history_undo(last(api, "create"), True)["ok"] is False    # has later activity


def test_movement_undo_adds_compensating_entry_not_erasure(api):
    iid = new_item(api, quantity="10")["id"]
    api.save_movement({"item_id": iid, "type": "Stock Out", "qty": "3"})
    api.save_movement({"item_id": iid, "type": "Stock In", "qty": "2"})
    assert row(iid)["quantity"] == 9
    undo(api, [h for h in api.history_list()["rows"] if h["action"] == "movement"][1]["id"])   # the stock-out
    assert row(iid)["quantity"] == 12
    assert len(api.movements(iid)["rows"]) == 4                           # ledger only grows
    api.save_movement({"item_id": iid, "type": "Stock Out", "qty": "12"})
    first_in = [h for h in api.history_list()["rows"] if h["action"] == "movement"][-1]
    # reversing the opening-less "in" now would go negative -> refused with a readable reason
    ins = [h for h in api.history_list()["rows"] if h["action"] == "movement" and "Stock In" in h["detail"]][0]
    assert api.history_undo(ins["id"], True)["ok"] is False
    assert first_in


def test_undo_needs_confirmation(api):
    iid = new_item(api)["id"]
    edit(api, iid, name="Z")
    assert api.history_undo(last(api), False)["needs_confirm"]


def test_verified_backup_and_retention(data_dir, monkeypatch):
    p = data_dir / "Backup" / "x.db"
    assert database.verified_backup(p) and database.verify_db(p)
    bad = data_dir / "bad.db"
    bad.write_bytes(b"garbage" * 100)
    assert not database.verify_db(bad)
    folder = data_dir / "Backup"
    today = date.today()
    for n in range(0, 800, 1):                                           # a backup for each of the last ~2 years
        (folder / f"warehouse_{(today - timedelta(days=n)):%Y%m%d}.db").write_bytes(b"x")
    for k in range(30):
        (folder / f"before_delete_20200101_0000{k:02d}.db").write_bytes(b"x")
    database.prune_backups(folder)
    left = sorted(folder.glob("warehouse_*.db"))
    assert config.KEEP_AUTO_BACKUPS <= len(left) <= config.KEEP_AUTO_BACKUPS + config.KEEP_WEEKLY_BACKUPS + config.KEEP_MONTHLY_BACKUPS
    assert (folder / f"warehouse_{today:%Y%m%d}.db").exists()
    assert any((today - timedelta(days=300)) > d for d in
               [date(int(f.stem[10:14]), int(f.stem[14:16]), int(f.stem[16:18])) for f in left])   # monthly tier reaches back
    assert len(list(folder.glob("before_delete_*.db"))) == config.KEEP_SAFETY_BACKUPS


def test_restore_points_list_and_go_back(api, data_dir):
    new_item(api, name="One")
    database.auto_backup(overwrite=True)
    new_item(api, name="Two", section="B")
    rows = api.restore_points()["rows"]
    auto = [r for r in rows if r["kind"] == "auto"][0]
    assert auto["items"] == 1
    assert api.restore_point_apply(auto["name"])["needs_confirm"]
    assert api.restore_point_apply(auto["name"], True)["ok"]
    assert len(api.inventory({})["rows"]) == 1
    assert any(r["kind"] == "restore" for r in api.restore_points()["rows"])   # a way back was kept
    assert api.restore_point_apply("../../etc/passwd", True)["ok"] is False


def test_encrypted_package_roundtrip_and_wrong_password(api, data_dir, tmp_path):
    pytest.importorskip("cryptography")
    new_item(api, name="Secret part")
    pkg = tmp_path / "s.pwbak"
    r = api.transfer_export  # api path uses a dialog only in desktop mode; here it writes to Export/
    out = api.transfer_export("pa55 word")
    assert out["ok"] and "Encrypted" in out["message"]
    enc = next((data_dir / "Export").glob("*.pwbak"))
    raw = enc.read_bytes()
    assert raw.startswith(transfer.MAGIC) and b"Secret part" not in raw and b"SQLite" not in raw
    assert api.restore_inspect(str(enc))["needs_password"]
    bad = api.restore_inspect(str(enc), "nope")
    assert bad["ok"] is False and "Wrong password" in bad["error"]
    good = api.restore_inspect(str(enc), "pa55 word")
    assert good["ok"] and "1 item" in good["message"]
    new_item(api, name="Later", section="B")
    assert api.restore_apply(str(enc), "pa55 word")["ok"]
    assert [x["name"] for x in api.inventory({})["rows"]] == ["Secret part"]
    # tampering / truncation is detected, never half-restored
    cut = tmp_path / "cut.pwbak"
    cut.write_bytes(raw[: len(raw) - 40])
    assert api.restore_apply(str(cut), "pa55 word")["ok"] is False
    flipped = bytearray(raw)
    flipped[-1] ^= 1
    (tmp_path / "flip.pwbak").write_bytes(bytes(flipped))
    assert api.restore_apply(str(tmp_path / "flip.pwbak"), "pa55 word")["ok"] is False
    assert [x["name"] for x in api.inventory({})["rows"]] == ["Secret part"]
    assert pkg  # (unused path kept for readability)
    assert r


def test_large_encrypted_file_spans_chunks(tmp_path):
    pytest.importorskip("cryptography")
    src = tmp_path / "big.bin"
    src.write_bytes(b"0123456789" * 300_000)                              # ~3 MB -> 3+ chunks
    enc, dec = tmp_path / "big.enc", tmp_path / "big.dec"
    transfer.encrypt_file(src, enc, "pw")
    transfer.decrypt_file(enc, dec, "pw")
    assert dec.read_bytes() == src.read_bytes()
    empty = tmp_path / "e"
    empty.write_bytes(b"")
    transfer.encrypt_file(empty, tmp_path / "e.enc", "pw")
    transfer.decrypt_file(tmp_path / "e.enc", tmp_path / "e.dec", "pw")
    assert (tmp_path / "e.dec").read_bytes() == b""


def test_package_carries_trash_and_history_so_undo_works_on_new_pc(api, data_dir, tmp_path, monkeypatch):
    src = tmp_path / "p.jpg"
    src.write_bytes(b"photo")
    iid = new_item(api, name="Gone", photo_path=str(src))["id"]
    stored = item(api, iid)["photo_path"]
    api.delete_items([iid], True)
    pkg = tmp_path / "t.pwbak"
    transfer.create_package(pkg)
    (config.TRASH_DIR / stored).unlink()
    (config.PHOTO_DIR / stored).unlink(missing_ok=True)
    assert api.restore_apply(str(pkg))["ok"]
    undo(api, last(api, "delete"))
    assert (config.PHOTO_DIR / stored).read_bytes() == b"photo"


def test_backup_status_warns_without_offsite_copy(api, data_dir):
    st = api.restore_points()["status"]
    assert st["offsite"] == "" and not st["offsite_ok"]
    api.transfer_export()
    assert api.restore_points()["status"]["offsite_ok"]


def test_trash_is_purged_after_retention(data_dir, monkeypatch):
    import os, time
    config.TRASH_DIR.mkdir(exist_ok=True)
    old, new = config.TRASH_DIR / "old.jpg", config.TRASH_DIR / "new.jpg"
    old.write_bytes(b"x"); new.write_bytes(b"x")
    t = time.time() - (config.TRASH_DAYS + 1) * 86400
    os.utime(old, (t, t))
    history.purge_trash()
    assert not old.exists() and new.exists()


# ---------------------------------------------------------------- delete UX, suggestions, data location
def test_delete_returns_undo_ids_and_no_longer_claims_irreversible(api):
    iid = new_item(api, name="Valve")["id"]
    r = api.delete_items([iid], False)
    assert r["needs_confirm"] and "cannot be undone" not in r["message"].lower() and "Undo" in r["message"]
    d = api.delete_items([iid], True)
    assert d["ok"] and len(d["undo_ids"]) == 1
    assert api.history_undo(d["undo_ids"][0], True)["ok"]
    assert api.get_item(iid)["ok"]


def test_suggestions_most_used_first(api):
    new_item(api, name="A1", category="Brakes")
    new_item(api, name="A2", category="Brakes", section="B")
    new_item(api, name="A3", category="Engine", section="C")
    cats = api.suggestions()["lists"]["category"]
    assert cats[0] == "Brakes" and "Engine" in cats


def test_data_locations_are_listed_and_opening_is_restricted(api, data_dir):
    r = api.data_locations()
    keys = [x["key"] for x in r["rows"]]
    assert keys[:3] == ["root", "db", "photos"] and {"backup", "trash", "export"} <= set(keys)
    assert all(x["path"].startswith(str(data_dir)) for x in r["rows"])
    assert api.open_folder("../etc")["ok"] is False


def test_move_data_copies_everything_and_remembers(api, data_dir, tmp_path, monkeypatch):
    monkeypatch.setattr(config, "LOCATION_FILE", data_dir.parent / (data_dir.name + "_ptr") / "location.txt")
    (config.PHOTO_DIR).mkdir(exist_ok=True)
    (config.PHOTO_DIR / "a.jpg").write_bytes(b"x")
    new_item(api, name="Moved")
    dest = data_dir.parent / (data_dir.name + "_elsewhere")        # outside the current data folder
    dest.mkdir()
    (dest / "someone_elses_file.txt").write_text("keep me")          # non-empty -> we make a MyWarehouse subfolder
    r = api.data_move(str(dest))
    assert r["ok"] and r["restart"], r
    new = dest / "MyWarehouse"
    assert (new / "Photos" / "a.jpg").read_bytes() == b"x" and transfer.inspect_package  # copied photos
    from personal_warehouse.core.database import verify_db
    assert verify_db(new / "Database" / "warehouse.db")
    assert config.LOCATION_FILE.read_text() == str(new)
    assert (data_dir / "Database" / "warehouse.db").exists()          # old data untouched
    assert api.data_move(str(new))["ok"] is False                      # already holds data
    assert api.data_move(str(data_dir / "Photos"))["ok"] is False       # inside the current folder


def test_default_location_rule(monkeypatch, tmp_path):
    monkeypatch.delenv("PW_DATA_DIR", raising=False)
    ptr = tmp_path / "loc.txt"
    chosen = tmp_path / "chosen"
    chosen.mkdir()
    ptr.write_text(str(chosen))
    monkeypatch.setattr(config, "LOCATION_FILE", ptr)
    assert config.resolve_data_dir() == chosen
    ptr.write_text(str(tmp_path / "gone"))                              # stale pointer -> falls back, never crashes
    assert config.resolve_data_dir().name == "MyWarehouse"
