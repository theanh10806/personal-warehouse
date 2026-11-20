"""Change journal: every edit, archive, delete and stock movement is recorded and can be undone.

Rules that keep undo safe:
* An entry stores the item's state before and after. Undo only runs when the item is still exactly in the
  "after" state, so it can never silently overwrite newer work (undo the newer change first).
* Deleting never destroys anything: the row, its movements and its photo (moved to ``Trash/``) are kept in the
  entry, so a delete can be undone. Photos stay in the trash ``TRASH_DAYS`` days.
* Stock movements are never erased (that would falsify the ledger); undoing one adds a compensating adjustment.
* An undo is itself journaled (label starts with ``↩``), so it can be undone again ("redo").
"""
from datetime import datetime
import json
import os
import shutil
import time

from personal_warehouse import config
from personal_warehouse.core.database import db, record_movement
from personal_warehouse.i18n import mv_t, tr

UNDO_MARK = "↩ "
_SKIP = {"id", "item_code", "quantity", "created_at", "updated_at", "date_added", "_restored_movements", "_undo_of", "_undo_depth"}
_FIELD_KEYS = {"name": "f_name", "name_ar": "f_name_ar", "category": "f_category", "description": "f_description",
               "engine_application": "f_engine", "barcode": "f_barcode", "section": "f_section", "part": "f_part",
               "condition": "f_condition", "unit": "f_unit", "purchase_price": "f_buy", "selling_price": "f_sell",
               "min_stock": "f_min", "supplier": "f_supplier", "notes": "f_notes", "photo_path": "x_photo",
               "is_active": "x_status"}


# ------------------------------------------------------------------ journal
def snapshot(con, iid):
    r = con.execute("SELECT * FROM items WHERE id=?", (iid,)).fetchone()
    return dict(r) if r else None


def _state(d):
    return {k: v for k, v in (d or {}).items() if k not in _SKIP}


def log(con, action, item_id, label, before=None, after=None):
    return con.execute("INSERT INTO history(ts,action,item_id,label,before,after) VALUES(?,?,?,?,?,?)",
                (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), action, item_id, label,
                 None if before is None else json.dumps(before, ensure_ascii=False),
                 None if after is None else json.dumps(after, ensure_ascii=False))).lastrowid


def _label(d):
    return f'{d.get("item_code") or ""} {d.get("name") or ""}'.strip()


def _changes(before, after):
    b, a = _state(before), _state(after)
    out = []
    for k in _FIELD_KEYS:
        if k in a and a.get(k) != b.get(k):
            name = tr(_FIELD_KEYS[k]).split(" (")[0].rstrip(" *:")
            out.append(f"{name}: {b.get(k) if b.get(k) not in (None, '') else '–'} → {a.get(k) if a.get(k) not in (None, '') else '–'}")
    return "; ".join(out[:4]) + (" …" if len(out) > 4 else "")


def recent(limit=300, item_id=None):
    sql, args = "SELECT * FROM history", []
    if item_id:
        sql += " WHERE item_id=?"
        args.append(item_id)
    with db() as con:
        rows = con.execute(sql + " ORDER BY id DESC LIMIT ?", args + [limit]).fetchall()
    out = []
    for r in rows:
        b = json.loads(r["before"]) if r["before"] else None
        a = json.loads(r["after"]) if r["after"] else None
        if r["action"] == "update" and a and b:
            detail = _changes(b, a)
        elif r["action"] == "movement" and a:
            detail = f'{mv_t(a.get("type"))}: {a.get("qty_before"):g} → {a.get("qty_after"):g}'
        elif r["action"] == "delete" and b:
            detail = tr("hx_delete_detail", len(b.get("movements", [])))
        else:
            detail = ""
        metadata = a or b or {}
        depth = metadata.get("_undo_depth", 1 if (r["label"] or "").startswith(UNDO_MARK) else 0)
        out.append({"id": r["id"], "ts": r["ts"], "action": r["action"], "label": (r["label"] or "").removeprefix(UNDO_MARK),
                    "detail": detail, "undone": bool(r["undone"]),
                    "operation": "undo" if depth % 2 else "redo" if depth else "change",
                    "reverse_label": tr("hx_redo") if depth % 2 else tr("hx_btn"),
                    "source_id": metadata.get("_undo_of")})
    return out


# ------------------------------------------------------------------ photo trash
def trash_photo(name):
    """Move a photo out of the way instead of deleting it."""
    if not name:
        return
    src = config.PHOTO_DIR / name
    if src.is_file():
        config.TRASH_DIR.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(config.TRASH_DIR / name))
        os.utime(config.TRASH_DIR / name, None)                 # age in the trash starts now


def untrash_photo(name):
    src, dst = config.TRASH_DIR / (name or ""), config.PHOTO_DIR / (name or "")
    if name and src.is_file() and not dst.exists():
        shutil.move(str(src), str(dst))


def purge_trash():
    cutoff = time.time() - config.TRASH_DAYS * 86400
    try:
        for f in config.TRASH_DIR.glob("*"):
            if f.is_file() and f.stat().st_mtime < cutoff:
                f.unlink(missing_ok=True)
    except OSError:
        pass


# ------------------------------------------------------------------ recording helpers used by the API
def delete_items_logged(con, ids):
    """Delete items (and their movements) recording one restorable entry per item.

    Returns (photo names to trash, journal entry ids)."""
    photos, entries = [], []
    for iid in ids:
        item = snapshot(con, iid)
        if not item:
            continue
        moves = [dict(m) for m in con.execute("SELECT * FROM movements WHERE item_id=? ORDER BY id", (iid,))]
        ph = item.get("photo_path")
        entries.append(log(con, "delete", iid, _label(item),
                           {"items": [item], "movements": moves, "photos": [ph] if ph else []}))
        con.execute("DELETE FROM movements WHERE item_id=?", (iid,))
        con.execute("DELETE FROM items WHERE id=?", (iid,))
        if ph:
            photos.append(ph)
    return photos, entries


def _insert(con, table, row):
    cols = list(row)
    con.execute(f"INSERT INTO {table}({','.join(cols)}) VALUES({','.join('?' * len(cols))})", [row[c] for c in cols])


# ------------------------------------------------------------------ undo
def undo(entry_id):
    """Reverse one journal entry. Raises ValueError with a readable message when it is no longer safe."""
    import sqlite3
    from personal_warehouse.core.formatting import qty_fmt
    photos_back = []
    with db() as con:
        con.execute("BEGIN IMMEDIATE")
        e = con.execute("SELECT * FROM history WHERE id=?", (entry_id,)).fetchone()
        if not e:
            raise ValueError(tr("hx_err_gone"))
        if e["undone"]:
            raise ValueError(tr("hx_err_done"))
        before = json.loads(e["before"]) if e["before"] else None
        after = json.loads(e["after"]) if e["after"] else None
        act, iid, label = e["action"], e["item_id"], (e["label"] or "")
        mark = label if label.startswith(UNDO_MARK) else UNDO_MARK + label
        cur = snapshot(con, iid) if iid else None

        if act == "update":
            if not cur:
                raise ValueError(tr("hx_err_missing"))
            if _state(cur) != _state(after):
                raise ValueError(tr("hx_err_changed"))
            cols = list(_state(before))
            con.execute(f"UPDATE items SET {','.join(c + '=?' for c in cols)},updated_at=CURRENT_TIMESTAMP WHERE id=?",
                        [before[c] for c in cols] + [iid])
            if before.get("photo_path") and before["photo_path"] != cur.get("photo_path"):
                photos_back.append(before["photo_path"])
            log(con, "update", iid, mark, cur, snapshot(con, iid))

        elif act == "create":
            if not cur:
                raise ValueError(tr("hx_err_missing"))
            moves = [dict(move) for move in con.execute("SELECT * FROM movements WHERE item_id=? ORDER BY id", (iid,))]
            expected_moves = after.get("_restored_movements")
            ledger_changed = moves != expected_moves if expected_moves is not None else len(moves) != (1 if after["quantity"] > 0 else 0)
            if _state(cur) != _state(after) or cur["quantity"] != after["quantity"] or ledger_changed:
                raise ValueError(tr("hx_err_changed"))
            photos, _ = delete_items_logged(con, [iid])
            con.execute("UPDATE history SET label=? WHERE id=(SELECT MAX(id) FROM history)", (mark,))
            for ph in photos:
                trash_photo(ph)

        elif act == "delete":
            for it in before["items"]:
                if con.execute("SELECT 1 FROM items WHERE id=? OR item_code=?", (it["id"], it["item_code"])).fetchone():
                    raise ValueError(tr("hx_err_exists"))
                try:
                    _insert(con, "items", it)
                except sqlite3.IntegrityError:
                    raise ValueError(tr("hx_err_exists")) from None
            for m in before["movements"]:
                _insert(con, "movements", m)
            photos_back += [p for p in before.get("photos", []) if p]
            it = before["items"][0]
            restored = snapshot(con, it["id"])
            restored["_restored_movements"] = before["movements"]
            log(con, "create", it["id"], mark, None, restored)

        elif act == "movement":
            if not cur:
                raise ValueError(tr("hx_err_missing"))
            new = cur["quantity"] - (after["qty_after"] - after["qty_before"])
            if new < -1e-9:
                raise ValueError(tr("hx_err_stock", qty_fmt(cur["quantity"])))
            new = max(new, 0.0)
            if abs(new - cur["quantity"]) < 1e-9:
                raise ValueError(tr("err_nochange"))
            con.execute("UPDATE items SET quantity=?,updated_at=CURRENT_TIMESTAMP WHERE id=?", (new, iid))
            record_movement(con, iid, "Adjustment", new, f"Undo #{entry_id}", None, cur["quantity"], new)
            log(con, "movement", iid, mark, None, {"type": "Adjustment", "qty": new, "qty_before": cur["quantity"],
                                                    "qty_after": new})
        else:
            raise ValueError(tr("hx_err_gone"))
        generated = con.execute("SELECT * FROM history ORDER BY id DESC LIMIT 1").fetchone()
        field = "after" if generated["after"] else "before"
        payload = json.loads(generated[field])
        metadata = after or before or {}
        depth = metadata.get("_undo_depth", 1 if label.startswith(UNDO_MARK) else 0)
        payload.update(_undo_of=entry_id, _undo_depth=depth + 1)
        con.execute(f"UPDATE history SET {field}=? WHERE id=?", (json.dumps(payload, ensure_ascii=False), generated["id"]))
        con.execute("UPDATE history SET undone=1 WHERE id=?", (entry_id,))
    for ph in photos_back:
        untrash_photo(ph)
    return label
