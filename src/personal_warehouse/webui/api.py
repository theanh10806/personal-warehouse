"""Bridge between the web interface and the application core.

``Api`` is handed to pywebview as ``js_api`` (every public method becomes ``window.pywebview.api.<name>``),
and to the development server in ``server.py`` (same methods over HTTP).  All the rules (stock changes,
validation, exports, labels ...) live in ``personal_warehouse.core``; this module only translates between
JSON and those functions, so the UI contains no business logic.

Every method returns plain JSON-able data.  Failures are returned as ``{"ok": False, "error": "..."}`` rather
than raised, so the page can show them in its own dialog.
"""
import base64
from datetime import date, datetime, timedelta
import functools
import io
import mimetypes
from pathlib import Path
import re
import shutil
import sys
import threading
import time
import webbrowser

from personal_warehouse import __version__, config, updater
from personal_warehouse.config import (CONDITIONS, LABEL_KINDS, LABEL_SIZES, LAYOUTS, MOVE_TYPES, PARTS, SEARCH_COLS,
                                       SECTIONS, SORT_SQL, UNITS)
from personal_warehouse.core.barcode import code128_svg
from personal_warehouse.core.database import backup_db_to, db, record_movement
from personal_warehouse.core.exporter import ExcelUnavailable, export_inventory
from personal_warehouse.core.formatting import (item_name, make_location, money, num, parse_location, photo_file,
                                                qty_fmt)
from personal_warehouse.core.labels import build_label_html
from personal_warehouse.core.scanning import decode_codes
from personal_warehouse.core.stock import apply_movement, find_item
from personal_warehouse import about
from personal_warehouse.core import history, transfer
from personal_warehouse.core.translator import translate_online
from personal_warehouse.i18n import LANGS, TR, cond_t, current_lang, from_label, mv_t, tr, unit_t
from personal_warehouse.i18n import set_language as set_ui_language
from personal_warehouse.settings import load_settings, save_settings

THEMES = ("light", "dark")


def safe(fn):
    """Turn exceptions into ``{"ok": False, "error": ...}`` so one bad call never breaks the page."""
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except ValueError as e:
            return {"ok": False, "error": str(e)}
        except Exception as e:                                   # noqa: BLE001 - reported to the user
            return {"ok": False, "error": f"{type(e).__name__}: {e}"}
    return wrapper


def _stock_state(r):
    if not r["is_active"]:
        return "gone"
    if r["quantity"] <= 0:
        return "out"
    if r["min_stock"] > 0 and r["quantity"] <= r["min_stock"]:
        return "low"
    return ""


def _label_options():
    return [{"value": k, "label": tr("kind_" + k)} for k in LABEL_KINDS]


class Api:
    def __init__(self):
        self._window = None
        self._bt = None
        self._release = None                                     # latest release found by check_updates
        self._dl = None                                          # state of the running / finished update download

    # ------------------------------------------------------------------ plumbing
    def _attach(self, window):
        """Called by the desktop launcher once the pywebview window exists (private: not exposed to JS)."""
        self._window = window

    def _push(self, fn, payload):
        """Call a global JS function from Python (used by the camera loop)."""
        if self._window is None:
            return
        import json
        try:
            self._window.evaluate_js(f"window.{fn}({json.dumps(payload)})")
        except Exception:                                        # noqa: BLE001 - window may be closing
            pass

    def _dialog(self, kind, **kw):
        """Native file dialog (desktop window only). Returns a path string or None."""
        if self._window is None:
            return None
        import webview
        dlg = getattr(webview, "FileDialog", None)
        mode = {"open": getattr(dlg, "OPEN", None) or webview.OPEN_DIALOG,
                "save": getattr(dlg, "SAVE", None) or webview.SAVE_DIALOG,
                "folder": getattr(dlg, "FOLDER", None) or webview.FOLDER_DIALOG}[kind]
        if kind in ("save", "open", "folder") and "directory" not in kw:
            config.EXPORT_DIR.mkdir(parents=True, exist_ok=True)
            kw["directory"] = str(config.EXPORT_DIR)               # always start in the same, known place
        res = self._window.create_file_dialog(mode, **kw)
        if not res:
            return None
        return res if isinstance(res, str) else res[0]

    # ------------------------------------------------------------------ start-up / settings
    def bootstrap(self):
        """Everything the page needs to render: language, theme, texts, option lists."""
        lang = current_lang()
        st = load_settings()
        return {
            "ok": True, "lang": lang, "rtl": lang == "ar", "langs": LANGS,
            "theme": st.get("theme", "light") if st.get("theme") in THEMES else "light",
            "strings": {k: (v.get(lang) or v.get("en") or k) for k, v in TR.items()},
            "sections": SECTIONS, "parts": PARTS,
            "conditions": [{"value": c, "label": cond_t(c)} for c in CONDITIONS],
            "units": [{"value": u, "label": unit_t(u)} for u in UNITS],
            "move_types": [{"value": m, "label": mv_t(m)} for m in MOVE_TYPES],
            "locations": ([{"value": "", "label": tr("all_locations")}]
                          + [{"value": f"sec:{s}", "label": tr("section_n", s)} for s in SECTIONS]
                          + [{"value": f"loc:{make_location(s, p)}", "label": make_location(s, p)}
                             for s in SECTIONS for p in PARTS]),
            "label_sizes": list(LABEL_SIZES), "label_kinds": _label_options(),
            "layouts": [{"value": k, "label": tr("layout_" + k)} for k in LAYOUTS],
            "version": __version__, "data_dir": str(config.DATA_DIR), "backup_name": config.BACKUP_DIR.name,
            "keep_backups": config.KEEP_AUTO_BACKUPS, "auto_update": bool(st.get("auto_update", True)),
            "sync_dir": st.get("sync_dir") or "", "last_sync": st.get("last_sync") or "",
            "desktop": self._window is not None,
        }

    @safe
    def set_language(self, code):
        if code in LANGS:
            set_ui_language(code)
            save_settings(lang=code)
        return self.bootstrap()

    @safe
    def set_theme(self, name):
        if name in THEMES:
            save_settings(theme=name)
        return {"ok": True}

    @safe
    def set_auto_update(self, flag):
        save_settings(auto_update=bool(flag))
        return {"ok": True}

    # ------------------------------------------------------------------ dashboard
    @safe
    def dashboard(self):
        today = date.today()
        since14 = (today - timedelta(days=13)).isoformat()
        since7 = (today - timedelta(days=6)).isoformat()
        since30 = (today - timedelta(days=30)).isoformat()
        since60 = (today - timedelta(days=60)).isoformat()
        with db() as con:
            r = con.execute("""SELECT COUNT(*) n, COALESCE(SUM(quantity),0) units,
                COALESCE(SUM(quantity*purchase_price),0) value,
                COALESCE(SUM(quantity*(selling_price-purchase_price)),0) profit
                FROM items WHERE is_active=1""").fetchone()
            alerts = con.execute("""SELECT id,name,name_ar,section,part,quantity,min_stock
                FROM items WHERE is_active=1
                AND (quantity<=0 OR (min_stock>0 AND quantity<=min_stock))
                ORDER BY quantity,name LIMIT 100""").fetchall()
            sect = {x["section"]: (x["n"], x["u"]) for x in con.execute(
                "SELECT section,COUNT(*) n,COALESCE(SUM(quantity),0) u "
                "FROM items WHERE is_active=1 GROUP BY section")}
            recent = con.execute("""SELECT m.movement_date,m.movement_type,m.quantity,i.name,i.name_ar
                FROM movements m JOIN items i ON i.id=m.item_id ORDER BY m.id DESC LIMIT 30""").fetchall()
            trend = con.execute("""SELECT substr(movement_date,1,10) d, movement_type t, SUM(quantity) q
                FROM movements WHERE movement_type IN ('Stock In','Stock Out') AND substr(movement_date,1,10)>=?
                GROUP BY d,t""", (since14,)).fetchall()
            top = con.execute("""SELECT i.name,i.name_ar,SUM(m.quantity) q FROM movements m
                JOIN items i ON i.id=m.item_id WHERE m.movement_type='Stock Out' AND substr(m.movement_date,1,10)>=?
                GROUP BY m.item_id ORDER BY q DESC LIMIT 1""", (since30,)).fetchone()
            idle = con.execute("""SELECT COUNT(*) FROM items i WHERE i.is_active=1 AND i.quantity>0 AND NOT EXISTS
                (SELECT 1 FROM movements m WHERE m.item_id=i.id AND substr(m.movement_date,1,10)>=?)""",
                               (since60,)).fetchone()[0]
        out_n = sum(1 for a in alerts if a["quantity"] <= 0)
        low_n = len(alerts) - out_n
        by_day, net7 = {}, 0.0
        for t in trend:
            ins, outs = by_day.get(t["d"], (0, 0))
            by_day[t["d"]] = (ins + t["q"], outs) if t["t"] == "Stock In" else (ins, outs + t["q"])
            if t["d"] >= since7:
                net7 += t["q"] if t["t"] == "Stock In" else -t["q"]
        days = [today - timedelta(days=13 - i) for i in range(14)]
        trend_rows = [{"label": d.strftime("%d/%m"), "in": by_day.get(d.isoformat(), (0, 0))[0],
                       "out": by_day.get(d.isoformat(), (0, 0))[1]} for d in days]

        names = lambda rs, n=3: ", ".join(item_name(a) for a in rs[:n]) + (" …" if len(rs) > n else "")
        outs = [a for a in alerts if a["quantity"] <= 0]
        lows = [a for a in alerts if a["quantity"] > 0]
        insights = []
        if outs:
            insights.append({"kind": "out", "text": tr("ins_out", out_n, names(outs))})
        if lows:
            insights.append({"kind": "low", "text": tr("ins_low", low_n, names(lows))})
        if top and top["q"]:
            insights.append({"kind": "top", "text": tr("ins_top", item_name(top), qty_fmt(top["q"]))})
        if idle:
            insights.append({"kind": "idle", "text": tr("ins_idle", idle)})
        if not insights:
            insights.append({"kind": "ok", "text": tr("ins_ok")})

        legacy = sorted(s for s in sect if s not in SECTIONS)
        total = r["n"]
        pct_out = round(100 * out_n / total) if total else 0
        pct_low = round(100 * low_n / total) if total else 0
        pct_ok = max(0, 100 - pct_out - pct_low) if total else 0
        net_text = ("▲ " if net7 > 0 else "▼ " if net7 < 0 else "") + qty_fmt(abs(net7))
        return {
            "ok": True,
            "kpis": {
                "items": {"value": str(r["n"]),
                          "sub": tr("kpi_sections", sum(1 for s in SECTIONS if sect.get(s, (0, 0))[0]), len(SECTIONS))},
                "units": {"value": qty_fmt(r["units"]), "sub": tr("kpi_units_sub"),
                          "badge": {"text": tr("kpi_net7", net_text), "kind": "ok" if net7 > 0 else "bad" if net7 < 0 else "flat"}},
                "value": {"value": money(r["value"]), "sub": tr("kpi_value_sub", money(r["profit"]))},
                "alerts": {"value": str(len(alerts)), "sub": tr("kpi_alert_sub", out_n, low_n),
                           "badge": {"text": tr("kpi_attention"), "kind": "bad"} if out_n else None},
            },
            "health": {"ok": pct_ok, "low": pct_low, "out": pct_out, "total": total},
            "trend": trend_rows,
            "sections": [{"s": s, "n": sect.get(s, (0, 0))[0], "u": sect.get(s, (0, 0))[1],
                          "u_text": qty_fmt(sect.get(s, (0, 0))[1])} for s in SECTIONS + legacy],
            "insights": insights,
            "alerts": [{"id": a["id"], "name": item_name(a), "loc": make_location(a["section"], a["part"]),
                        "qty": qty_fmt(a["quantity"]), "min": qty_fmt(a["min_stock"]),
                        "state": "out" if a["quantity"] <= 0 else "low"} for a in alerts],
            "recent": [{"time": m["movement_date"][5:16], "name": item_name(m), "type": mv_t(m["movement_type"]),
                        "kind": {"Stock In": "in", "Stock Out": "out"}.get(m["movement_type"], ""),
                        "qty": qty_fmt(m["quantity"])} for m in recent],
            "remind": {"count": len(alerts), "names": names(alerts, 2), "first_id": alerts[0]["id"]} if alerts else None,
        }

    # ------------------------------------------------------------------ inventory
    @safe
    def inventory(self, f=None):
        f = f or {}
        sql, args = ["SELECT * FROM items WHERE 1=1"], []
        if not f.get("archived"):
            sql.append("AND is_active=1")
        for tok in str(f.get("search") or "").split():
            sql.append("AND (" + " OR ".join(f"{c} LIKE ?" for c in SEARCH_COLS) + ")")
            args += [f"%{tok}%"] * len(SEARCH_COLS)
        loc = str(f.get("location") or "")
        if loc.startswith("sec:") and loc[4:] in SECTIONS:
            sql.append("AND section=?")
            args.append(loc[4:])
        elif loc.startswith("loc:") and loc[4:5] in SECTIONS:
            s, p = parse_location(loc[4:])
            sql.append("AND section=? AND part=?")
            args += [s, p]
        if f.get("condition") in CONDITIONS:
            sql.append("AND condition=?")
            args.append(f["condition"])
        if f.get("low_only"):
            sql.append("AND (quantity<=0 OR (min_stock>0 AND quantity<=min_stock))")
        col = f.get("sort") if f.get("sort") in SORT_SQL else "location"
        sql.append(f"ORDER BY {SORT_SQL[col]} {'DESC' if f.get('desc') else 'ASC'}, name COLLATE NOCASE")
        with db() as con:
            rows = con.execute(" ".join(sql), args).fetchall()
        units = value = 0.0
        out = []
        for r in rows:
            if r["is_active"]:
                units += r["quantity"]
                value += r["quantity"] * r["purchase_price"]
            out.append({"id": r["id"], "code": r["item_code"], "name": item_name(r), "category": r["category"] or "",
                        "engine": r["engine_application"] or "", "location": make_location(r["section"], r["part"]),
                        "condition": cond_t(r["condition"]), "qty": f'{qty_fmt(r["quantity"])} {unit_t(r["unit"])}',
                        "buy": money(r["purchase_price"]), "sell": money(r["selling_price"]),
                        "state": _stock_state(r)})
        return {"ok": True, "rows": out, "summary": tr("inv_summary", len(rows), qty_fmt(units), money(value))}

    @safe
    def toggle_archive(self, iid, confirmed=False):
        with db() as con:
            r = con.execute("SELECT name,is_active FROM items WHERE id=?", (iid,)).fetchone()
            if not r:
                return {"ok": False, "error": tr("sel_msg")}
            if r["is_active"] and not confirmed:
                return {"ok": False, "needs_confirm": True, "title": tr("archive_title"),
                        "message": tr("archive_confirm", r["name"])}
            old = history.snapshot(con, iid)
            con.execute("UPDATE items SET is_active=?,updated_at=CURRENT_TIMESTAMP WHERE id=?",
                        (0 if r["is_active"] else 1, iid))
            history.log(con, "update", iid, history._label(old), old, history.snapshot(con, iid))
        return {"ok": True, "message": f"{tr('archived') if r['is_active'] else tr('restored')}: {r['name']}"}

    @safe
    def delete_items(self, ids, confirmed=False):
        """Permanently remove items together with their movement history (a full backup is made first)."""
        ids = sorted({int(i) for i in ids or []})
        if not ids:
            return {"ok": False, "error": tr("del_pick")}
        marks = ",".join("?" * len(ids))
        with db() as con:
            found = [r["id"] for r in con.execute(f"SELECT id FROM items WHERE id IN ({marks})", ids)]
            moves = con.execute(f"SELECT COUNT(*) FROM movements WHERE item_id IN ({marks})", ids).fetchone()[0]
        if not found:
            return {"ok": False, "error": tr("sel_msg")}
        if not confirmed:
            return {"ok": False, "needs_confirm": True, "title": tr("del_title"), "message": tr("del_confirm", len(found), moves)}
        safety = config.BACKUP_DIR / f"before_delete_{datetime.now():%Y%m%d_%H%M%S}.db"
        backup_db_to(safety)
        with db() as con:
            photos, entries = history.delete_items_logged(con, found)   # journaled: can be undone from History
        for ph in photos:                                            # photos go to Trash/, not the void
            with db() as con:
                used = con.execute("SELECT 1 FROM items WHERE photo_path=?", (ph,)).fetchone()
            if not used:
                history.trash_photo(ph)
        return {"ok": True, "count": len(found), "undo_ids": entries, "message": tr("del_done", len(found))}

    # ------------------------------------------------------------------ item form
    def _photo_uri(self, stored_or_path, box=(560, 460)):
        """Image as a data: URI (resized when Pillow is available), or '' when there is none."""
        if not stored_or_path:
            return ""
        p = Path(stored_or_path)
        if not p.is_absolute():
            p = photo_file(stored_or_path)
        if not p or not p.exists():
            return ""
        try:
            from PIL import Image
            im = Image.open(p)
            im.thumbnail(box)
            buf = io.BytesIO()
            has_alpha = im.mode in ("RGBA", "LA", "P")
            im.convert("RGBA" if has_alpha else "RGB").save(buf, format="PNG" if has_alpha else "JPEG", quality=86)
            mime = "image/png" if has_alpha else "image/jpeg"
            return f"data:{mime};base64,{base64.b64encode(buf.getvalue()).decode()}"
        except ImportError:
            if p.stat().st_size > 4_000_000:
                return ""
            mime = mimetypes.guess_type(p.name)[0] or "image/png"
            return f"data:{mime};base64,{base64.b64encode(p.read_bytes()).decode()}"
        except Exception:                                        # noqa: BLE001 - unreadable image: show none
            return ""

    @safe
    def get_item(self, iid):
        with db() as con:
            r = con.execute("SELECT * FROM items WHERE id=?", (iid,)).fetchone()
        if not r:
            return {"ok": False, "error": tr("sel_msg")}
        item = {k: r[k] for k in ("id", "item_code", "name", "name_ar", "category", "description",
                                  "engine_application", "barcode", "section", "part", "condition", "unit",
                                  "supplier", "notes", "photo_path")}
        item.update(quantity=qty_fmt(r["quantity"]), min_stock=qty_fmt(r["min_stock"]),
                    purchase_price=f'{r["purchase_price"]:g}', selling_price=f'{r["selling_price"]:g}')
        return {"ok": True, "item": item, "photo": self._photo_uri(r["photo_path"]),
                "barcode_svg": code128_svg(r["item_code"]) if r["item_code"] else ""}

    @safe
    def choose_photo(self):
        path = self._dialog("open", file_types=(f'{tr("image_files")} (*.png;*.jpg;*.jpeg;*.gif;*.bmp;*.webp)',
                                                f'{tr("all_files")} (*.*)'))
        if not path:
            return {"ok": True, "path": None}
        return {"ok": True, "path": path, "photo": self._photo_uri(path)}

    @safe
    def translate_name(self, name):
        name = (name or "").strip()
        if not name:
            return {"ok": False, "error": tr("tr_need_name")}
        try:
            return {"ok": True, "text": translate_online(name, "ar")}
        except Exception as e:                                   # noqa: BLE001
            return {"ok": False, "error": tr("tr_fail", e)}

    @safe
    def save_item(self, v):
        """Create or update an item. Questions the user must answer (price below cost, duplicate) come back as
        ``needs_confirm``; the page asks and resends with the answer's key in ``v['confirmed']``."""
        iid = v.get("id") or None
        confirmed = set(v.get("confirmed") or [])
        text = lambda k: str(v.get(k) or "").strip()
        if not text("name"):
            return {"ok": False, "error": tr("err_name"), "field": "name"}
        old = {}
        if iid:                                                  # an item may keep a location that left the map
            with db() as con:
                row = con.execute("SELECT section,part FROM items WHERE id=?", (iid,)).fetchone()
            old = dict(row) if row else {}
        for key in ("section", "part", "condition", "unit"):
            allowed = {"section": SECTIONS, "part": PARTS, "condition": CONDITIONS, "unit": UNITS}[key]
            if text(key) not in allowed and text(key) != old.get(key):
                return {"ok": False, "error": f"{key}?", "field": key}
        try:
            buy = round(num(text("purchase_price"), tr("f_buy")), 2)
            sell = round(num(text("selling_price"), tr("f_sell")), 2)
            minq = num(text("min_stock"), tr("f_min"))
            qty = None if iid else num(text("quantity"), tr("f_qty"))
        except ValueError as e:
            return {"ok": False, "error": str(e), "title": tr("err_number_title")}
        if sell and buy and sell < buy and "price_below" not in confirmed:
            return {"ok": False, "needs_confirm": "price_below", "title": tr("price_below_title"),
                    "message": tr("price_below")}
        barcode = text("barcode") or None
        if barcode:
            with db() as con:
                clash = con.execute("SELECT item_code FROM items WHERE (barcode=? OR item_code=? COLLATE NOCASE) "
                                    "AND id<>?", (barcode, barcode, iid or 0)).fetchone()
            if clash:
                return {"ok": False, "error": tr("barcode_dup", barcode, clash["item_code"]), "field": "barcode"}
        if not iid and "duplicate" not in confirmed:
            with db() as con:
                dup = con.execute("SELECT item_code FROM items WHERE is_active=1 AND name=? COLLATE NOCASE "
                                  "AND section=? AND part=?", (text("name"), text("section"), text("part"))).fetchone()
            if dup:
                return {"ok": False, "needs_confirm": "duplicate", "title": tr("dup_title"),
                        "message": tr("dup_msg", dup["item_code"])}

        new_name = None
        if v.get("photo_path"):
            src = Path(v["photo_path"])
            safe_name = re.sub(r"[^\w.\-]", "_", src.name)
            new_name = f"{datetime.now():%Y%m%d%H%M%S%f}_{safe_name}"
            try:
                shutil.copy2(src, config.PHOTO_DIR / new_name)
            except Exception as e:                               # noqa: BLE001
                return {"ok": False, "error": str(e), "title": tr("photo_err")}
        current_photo = text("current_photo") or None
        photo = new_name or (None if v.get("photo_remove") else current_photo)
        common = (text("name"), text("name_ar") or None, text("category"), text("description"),
                  text("engine_application"), barcode, text("section"), text("part"), text("condition"),
                  text("unit"), buy, sell, minq, photo, text("supplier"), text("notes"))
        try:
            with db() as con:
                if iid:
                    old_snap = history.snapshot(con, iid)
                    con.execute("""UPDATE items SET name=?,name_ar=?,category=?,description=?,engine_application=?,
                        barcode=?,section=?,part=?,condition=?,unit=?,purchase_price=?,selling_price=?,min_stock=?,
                        photo_path=?,supplier=?,notes=?,updated_at=CURRENT_TIMESTAMP WHERE id=?""", common + (iid,))
                    new_snap = history.snapshot(con, iid)
                    if history._state(old_snap) != history._state(new_snap):
                        history.log(con, "update", iid, history._label(new_snap), old_snap, new_snap)
                else:
                    cur = con.execute("""INSERT INTO items(name,name_ar,category,description,engine_application,
                        barcode,section,part,condition,unit,purchase_price,selling_price,min_stock,photo_path,
                        supplier,notes,quantity,date_added) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                                      common + (qty, datetime.now().strftime("%Y-%m-%d")))
                    iid = cur.lastrowid
                    con.execute("UPDATE items SET item_code=? WHERE id=?", (f"WH-{iid:05d}", iid))
                    if qty > 0:
                        record_movement(con, iid, "Opening stock", qty, "Initial quantity", buy, 0, qty)
                    snap = history.snapshot(con, iid)
                    history.log(con, "create", iid, history._label(snap), None, snap)
        except Exception as e:                                   # noqa: BLE001
            if new_name:
                (config.PHOTO_DIR / new_name).unlink(missing_ok=True)
            return {"ok": False, "error": str(e), "title": tr("save_failed")}
        if current_photo and current_photo != photo:
            with db() as con:
                still_used = con.execute("SELECT COUNT(*) FROM items WHERE photo_path=?", (current_photo,)).fetchone()[0]
            if not still_used:
                try:
                    history.trash_photo(current_photo)
                except OSError:
                    pass
        return {"ok": True, "id": iid, "message": tr("saved", text("name"))}

    # ------------------------------------------------------------------ stock movements
    @staticmethod
    def _choice_label(r):
        return f'{r["item_code"]} — {item_name(r)} [{make_location(r["section"], r["part"])}]'

    @safe
    def movement_items(self, query="", limit=60):
        """Items matching ``query`` (all words must appear in code / name / location)."""
        sql, args = ["SELECT id,item_code,name,name_ar,section,part FROM items WHERE is_active=1"], []
        for tok in str(query or "").split():
            sql.append("AND (item_code LIKE ? OR name LIKE ? OR IFNULL(name_ar,'') LIKE ? OR (section||part) LIKE ? "
                       "OR IFNULL(barcode,'') LIKE ?)")
            args += [f"%{tok}%"] * 5
        sql.append("ORDER BY name COLLATE NOCASE LIMIT ?")
        args.append(int(limit))
        with db() as con:
            rows = con.execute(" ".join(sql), args).fetchall()
        return {"ok": True, "items": [{"id": r["id"], "label": self._choice_label(r)} for r in rows]}

    @safe
    def item_info(self, iid, move_type="Stock In"):
        with db() as con:
            r = con.execute("SELECT * FROM items WHERE id=?", (iid,)).fetchone()
        if not r:
            return {"ok": False, "error": tr("mv_pick2")}
        low = tr("mv_low", qty_fmt(r["min_stock"])) if r["min_stock"] > 0 and r["quantity"] <= r["min_stock"] else ""
        price = f"{r['purchase_price']:.2f}" if move_type == "Stock In" else \
            f"{r['selling_price']:.2f}" if move_type == "Stock Out" else ""
        return {"ok": True, "label": self._choice_label(r), "price": price, "state": _stock_state(r),
                "info": tr("mv_info", qty_fmt(r["quantity"]), unit_t(r["unit"]), make_location(r["section"], r["part"]),
                           money(r["purchase_price"]), money(r["selling_price"]), low)}

    @safe
    def save_movement(self, v):
        iid = v.get("item_id")
        if not iid:
            return {"ok": False, "error": tr("err_pick_item")}
        typ = v.get("type")
        if typ not in MOVE_TYPES:
            return {"ok": False, "error": tr("mv_type")}
        try:
            q = num(v.get("qty"), tr("mv_qty"))
            price = round(num(v.get("price"), tr("mv_price")), 2) if str(v.get("price") or "").strip() else None
        except ValueError as e:
            return {"ok": False, "error": str(e), "title": tr("err_number_title")}
        if typ != "Adjustment" and q <= 0:
            return {"ok": False, "error": tr("err_qty")}
        try:
            r, before, after = apply_movement(iid, typ, q, price, str(v.get("reason") or "").strip())
        except ValueError as e:
            return {"ok": False, "error": str(e), "title": tr("info_title")}
        warn = tr("mv_warn") if r["min_stock"] > 0 and after <= r["min_stock"] else ""
        return {"ok": True, "warn": bool(warn),
                "message": tr("mv_done", mv_t(typ), item_name(r), qty_fmt(before), qty_fmt(after), unit_t(r["unit"]), warn)}

    @safe
    def movements(self, item_id=None):
        sql, args = "SELECT m.*,i.item_code,i.name,i.name_ar FROM movements m JOIN items i ON i.id=m.item_id", []
        if item_id:
            sql += " WHERE m.item_id=?"
            args.append(item_id)
        arrow = "←" if current_lang() == "ar" else "→"
        with db() as con:
            rows = con.execute(sql + " ORDER BY m.id DESC LIMIT 500", args).fetchall()
        return {"ok": True, "rows": [{
            "date": r["movement_date"], "code": r["item_code"], "name": item_name(r),
            "type": mv_t(r["movement_type"]), "kind": {"Stock In": "in", "Stock Out": "out"}.get(r["movement_type"], ""),
            "qty": qty_fmt(r["quantity"]),
            "change": f"{qty_fmt(r['qty_before'])} {arrow} {qty_fmt(r['qty_after'])}" if r["qty_after"] is not None else "",
            "price": money(r["unit_price"]) if r["unit_price"] is not None else "", "reason": r["reason"] or ""}
            for r in rows]}

    # ------------------------------------------------------------------ scanning
    def _scan_result(self, text, mode="lookup", qty="1"):
        """Look a scanned value up (and move stock in Stock In / Stock Out mode). Mirrors the old desktop page."""
        text = (text or "").strip()
        r, code = find_item(text)
        res = {"ok": True, "found": False, "item_id": None, "flash": "", "flash_ok": True, "rows": [],
               "photo": "", "can_move": False, "banner": "NOT FOUND", "changed": False}
        if not r:
            res["head"] = tr("scan_notfound", code) if code else tr("scan_not_wh")
            res["rows"] = [[tr("scan_content"), text[:600]]]
            return res
        flash, flash_ok, banner = "", True, f"OK {r['item_code']}"
        if mode in ("Stock In", "Stock Out"):
            if not r["is_active"]:
                flash, flash_ok = tr("scan_archived_no"), False
            else:
                try:
                    q = num(qty, tr("scan_qtyper"))
                    if q <= 0:
                        raise ValueError(tr("err_qty"))
                    price = r["purchase_price"] if mode == "Stock In" else r["selling_price"]
                    _, _before, after = apply_movement(r["id"], mode, q, price, "Scan")
                    flash = tr("scan_flash_in" if mode == "Stock In" else "scan_flash_out",
                               qty_fmt(q), qty_fmt(after), unit_t(r["unit"]))
                    banner = f"{r['item_code']} {'+' if mode == 'Stock In' else '-'}{qty_fmt(q)} = {qty_fmt(after)}"
                    res["changed"] = True
                except ValueError as e:
                    flash, flash_ok, banner = tr("scan_flash_err", e), False, "ERROR"
            with db() as con:
                r = con.execute("SELECT * FROM items WHERE id=?", (r["id"],)).fetchone()
        state = _stock_state(r)
        warn = {"gone": tr("st_archived"), "out": tr("st_out"), "low": tr("st_low")}.get(state, "")
        dash = "—"
        res.update(
            found=True, item_id=r["id"], flash=flash, flash_ok=flash_ok, banner=banner, state=state,
            head=f"{r['item_code']} — {item_name(r)}" + (f"   {warn}" if warn else ""),
            can_move=bool(r["is_active"]), photo=self._photo_uri(r["photo_path"]),
            rows=[[tr("f_category"), r["category"] or dash], [tr("f_description"), r["description"] or dash],
                  [tr("f_engine"), r["engine_application"] or dash],
                  [tr("f_barcode").split(" (")[0], r["barcode"] or dash],
                  [tr("h_location"), make_location(r["section"], r["part"])],
                  [tr("f_condition"), cond_t(r["condition"])],
                  [tr("sc_stock"), f"{qty_fmt(r['quantity'])} {unit_t(r['unit'])}"],
                  [tr("f_min"), qty_fmt(r["min_stock"])], [tr("f_buy"), money(r["purchase_price"])],
                  [tr("f_sell"), money(r["selling_price"])], [tr("f_supplier"), r["supplier"] or dash],
                  [tr("f_notes"), r["notes"] or dash], [tr("sc_added"), r["date_added"] or dash]])
        res["message"] = tr("scan_scanned", r["item_code"])
        return res

    @safe
    def scan(self, text, mode="lookup", qty="1"):
        return self._scan_result(text, mode, qty)

    @safe
    def scan_image(self, mode="lookup", qty="1"):
        path = self._dialog("open", file_types=(f'{tr("image_files")} (*.png;*.jpg;*.jpeg;*.bmp;*.webp)',
                                                f'{tr("all_files")} (*.*)'))
        if not path:
            return {"ok": True, "cancelled": True}
        return self.scan_image_path(path, mode, qty)

    @safe
    def scan_image_path(self, path, mode="lookup", qty="1"):
        try:
            import cv2
            import numpy as np
        except ImportError:
            return {"ok": False, "error": tr("cam_unavail"), "title": tr("cam_unavail_title")}
        img = cv2.imdecode(np.fromfile(path, dtype=np.uint8), cv2.IMREAD_COLOR)
        if img is None:
            return {"ok": False, "error": tr("img_read_err"), "title": tr("scan_image")}
        text = decode_codes(img)
        if not text:
            big = cv2.resize(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
            text = decode_codes(big)
        if not text:
            return {"ok": False, "error": tr("no_qr_msg"), "title": tr("no_qr")}
        return self._scan_result(text, mode, qty)

    @safe
    def camera_scan(self, mode="lookup", qty="1"):
        """Open the camera in its own window and push every result to the page (``window.onCameraScan``)."""
        try:
            import cv2
        except ImportError:
            return {"ok": False, "error": tr("cam_unavail"), "title": tr("cam_unavail_title")}
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW) if sys.platform == "win32" else cv2.VideoCapture(0)
        if not cap.isOpened():
            return {"ok": False, "error": tr("cam_open_err"), "title": tr("scan_camera")}
        win = "Scan - press Q or ESC to close"
        continuous = mode in ("Stock In", "Stock Out")
        last, last_t, banner, banner_t = "", 0.0, "", 0.0
        try:
            while True:
                ok, frame = cap.read()
                if not ok:
                    break
                text = decode_codes(frame)
                now = time.time()
                if text and (text != last or now - last_t > 2.5):
                    last, last_t = text, now
                    res = self._scan_result(text, mode, qty)
                    banner, banner_t = res["banner"], now
                    self._push("onCameraScan", res)
                    if res["found"] and not continuous:
                        break
                if banner and now - banner_t < 2.0:
                    cv2.putText(frame, banner, (10, 34), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 200, 0), 2)
                cv2.imshow(win, frame)
                if cv2.waitKey(1) & 0xFF in (27, ord("q")):
                    break
                if cv2.getWindowProperty(win, cv2.WND_PROP_VISIBLE) < 1:
                    break
        finally:
            cap.release()
            cv2.destroyAllWindows()
        return {"ok": True}

    # ------------------------------------------------------------------ storage map
    @safe
    def locations(self):
        """Storage map: 3 sections x 8 parts (fixed), per-cell counts, low-stock flags and a few item names."""
        with db() as con:
            stats = {(r["section"], r["part"]): r for r in con.execute(
                "SELECT section,part,COUNT(*) n,SUM(quantity) u,"
                "SUM(CASE WHEN quantity<=0 OR (min_stock>0 AND quantity<=min_stock) THEN 1 ELSE 0 END) low "
                "FROM items WHERE is_active=1 GROUP BY section,part")}
            names = {}
            for r in con.execute("SELECT section,part,name,name_ar FROM items WHERE is_active=1 "
                                 "ORDER BY name COLLATE NOCASE"):
                names.setdefault((r["section"], r["part"]), []).append(item_name(r))

        def cell(s, p):
            r = stats.get((s, p))
            n, u, low = (r["n"], r["u"] or 0, r["low"] or 0) if r else (0, 0, 0)
            return {"code": make_location(s, p), "n": n, "units": qty_fmt(u), "low": low,
                    "names": names.get((s, p), [])[:3]}

        legacy = [dict(cell(s, p), code=make_location(s, p))
                  for (s, p) in sorted(stats) if s not in SECTIONS or p not in PARTS]
        out = []
        for s in SECTIONS:
            cells = [cell(s, p) for p in PARTS]
            out.append({"section": s, "cells": cells, "n": sum(c["n"] for c in cells),
                        "used": sum(1 for c in cells if c["n"]), "low": sum(c["low"] for c in cells),
                        "units": qty_fmt(sum(float((stats.get((s, p)) or {"u": 0})["u"] or 0) for p in PARTS))})
        total_n = sum(x["n"] for x in out)
        return {"ok": True, "sections": out, "legacy": legacy,
                "total": {"slots": len(SECTIONS) * len(PARTS), "used": sum(x["used"] for x in out),
                          "items": total_n, "low": sum(x["low"] for x in out),
                          "max_n": max([c["n"] for x in out for c in x["cells"]] or [0])}}

    # ------------------------------------------------------------------ labels, export, backup
    @safe
    def print_labels(self, ids, o):
        ids = [int(i) for i in ids or []]
        if not ids:
            return {"ok": False, "error": tr("lbl_nothing"), "title": tr("lbl_nothing_t")}
        o = {"layout": o.get("layout") if o.get("layout") in LAYOUTS else "a4",
             "size": o.get("size") if o.get("size") in LABEL_SIZES else "Medium 70×40 mm",
             "kind": o.get("kind") if o.get("kind") in LABEL_KINDS else "qr",
             "copies": max(1, min(50, int(o.get("copies") or 1))),
             "full": bool(o.get("full")), "prices": bool(o.get("prices"))}
        if o["kind"] in ("qr", "both"):
            try:
                import qrcode  # noqa: F401
            except ImportError:
                return {"ok": False, "error": tr("qr_unavail"), "title": tr("qr_unavail_title")}
        rows = {}
        with db() as con:
            for i in range(0, len(ids), 500):
                chunk = ids[i:i + 500]
                for r in con.execute(f"SELECT * FROM items WHERE id IN ({','.join('?' * len(chunk))})", chunk):
                    rows[r["id"]] = r
        items = [rows[i] for i in ids if i in rows]
        count = len(items) * o["copies"]
        if count > 400 and not o.get("confirmed"):
            return {"ok": False, "needs_confirm": True, "title": tr("lbl_title_msg"), "message": tr("lbl_many", count)}
        path = config.LABEL_DIR / f"labels_{datetime.now():%Y%m%d_%H%M%S}.html"
        path.write_text(build_label_html(items, o), encoding="utf-8")
        for old in sorted(config.LABEL_DIR.glob("labels_*.html"))[:-20]:
            old.unlink(missing_ok=True)
        webbrowser.open(path.as_uri())
        return {"ok": True, "message": tr("lbl_opened", count, config.LABEL_DIR.name)}

    @safe
    def export_excel(self):
        name = f"Warehouse_{datetime.now():%Y%m%d}.xlsx"
        if self._window is None:                                 # dev server: no native dialog, use the data folder
            folder = config.EXPORT_DIR
            folder.mkdir(parents=True, exist_ok=True)
            path = str(folder / name)
        else:
            path = self._dialog("save", save_filename=name, file_types=(
                f'{tr("excel_files")} (*.xlsx)', f'{tr("csv_files")} (*.csv)'))
        if not path:
            return {"ok": True, "cancelled": True}
        try:
            export_inventory(path, current_lang() == "ar")
        except ExcelUnavailable:
            return {"ok": False, "error": tr("exp_unavail_msg"), "title": tr("exp_unavail")}
        return {"ok": True, "message": tr("exp_done", path)}

    @safe
    def backup_all(self):
        dest = str(config.EXPORT_DIR) if self._window is None else self._dialog("folder")
        if not dest:
            return {"ok": True, "cancelled": True}
        target = Path(dest) / f"MyWarehouse_Backup_{datetime.now():%Y%m%d_%H%M%S}"
        try:
            (target / "Database").mkdir(parents=True)
            backup_db_to(target / "Database" / "warehouse.db")
            shutil.copytree(config.PHOTO_DIR, target / "Photos")
        except Exception as e:                                   # noqa: BLE001
            return {"ok": False, "error": str(e), "title": tr("backup_fail")}
        return {"ok": True, "message": tr("backup_status", target), "title": tr("backup_done"),
                "detail": tr("backup_done_msg", target)}

    # ------------------------------------------------------------------ move to another computer / online copy
    @staticmethod
    def _pkg_error(e):
        return {"ok": False, "title": tr("tx_title"), "error": tr("tx_err_" + str(e)) if ("tx_err_" + str(e)) in TR else str(e)}

    @safe
    def transfer_export(self, password=None):
        """Save everything as one .pwbak file (database + photos) to carry to another computer."""
        name = f"MyWarehouse_{datetime.now():%Y%m%d_%H%M}{transfer.EXT}"
        if self._window is None:
            folder = config.EXPORT_DIR
            folder.mkdir(parents=True, exist_ok=True)
            path = str(folder / name)
        else:
            path = self._dialog("save", save_filename=name, file_types=(f"{tr('tx_files')} (*{transfer.EXT})",))
        if not path:
            return {"ok": True, "cancelled": True}
        if not path.lower().endswith(transfer.EXT):
            path += transfer.EXT
        try:
            m = transfer.create_package(path, password or None)
        except transfer.PackageError as e:
            return self._pkg_error(e)
        save_settings(last_export=datetime.now().strftime("%Y-%m-%d %H:%M"))
        lock = tr("tx_locked") if password else ""
        return {"ok": True, "title": tr("tx_title"), "message": tr("tx_exported", path, m["items"], m["photos"]) + lock}

    @safe
    def restore_inspect(self, path=None, password=None):
        """Pick a .pwbak (or use ``path``) and report what it contains. Nothing is changed yet."""
        if not path:
            if self._window is None:
                latest = transfer.latest_in_folder(load_settings().get("sync_dir") or config.EXPORT_DIR)
                path = str(latest) if latest else None
            else:
                path = self._dialog("open", file_types=(f"{tr('tx_files')} (*{transfer.EXT})",))
        if not path:
            return {"ok": True, "cancelled": True}
        if transfer.is_encrypted(path) and not password:
            return {"ok": True, "needs_password": True, "path": str(path), "title": tr("tx_restore_title"),
                    "message": tr("tx_pw_ask")}
        try:
            m = transfer.inspect_package(path, password)
        except transfer.PackageError as e:
            return self._pkg_error(e)
        warn = tr("tx_replace_warn") if transfer.has_data() else ""
        return {"ok": True, "path": str(path), "title": tr("tx_restore_title"),
                "message": tr("tx_restore_msg", m.get("created", "?"), m.get("items", 0), m.get("movements", 0),
                              m.get("photos", 0), warn)}

    @safe
    def restore_apply(self, path, password=None):
        try:
            m, safety = transfer.restore_package(path, password)
        except transfer.PackageError as e:
            return self._pkg_error(e)
        st = load_settings()
        if st.get("lang") in LANGS:
            set_ui_language(st["lang"])
        extra = tr("tx_restored_safety", safety.name) if safety else ""
        return {"ok": True, "title": tr("tx_restore_title"), "message": tr("tx_restored", m.get("items", 0), extra),
                "bootstrap": self.bootstrap()}

    @safe
    def sync_choose_folder(self):
        """Choose a folder that OneDrive / Google Drive / Dropbox keeps online. Backups are written there."""
        if self._window is None:
            folder = config.DATA_DIR / "Sync"
            folder.mkdir(parents=True, exist_ok=True)
            path = str(folder)
        else:
            path = self._dialog("folder")
        if not path:
            return {"ok": True, "cancelled": True}
        save_settings(sync_dir=path)
        return self.sync_now()

    @safe
    def sync_off(self):
        save_settings(sync_dir="", last_sync="")
        return {"ok": True, "bootstrap": self.bootstrap()}

    @safe
    def sync_now(self):
        folder = load_settings().get("sync_dir")
        if not folder:
            return {"ok": False, "error": tr("tx_err_sync_missing"), "title": tr("tx_title")}
        try:
            target, m = transfer.sync_to_folder(folder)
        except transfer.PackageError as e:
            return self._pkg_error(e)
        except OSError as e:
            return {"ok": False, "title": tr("tx_title"), "error": tr("tx_err_sync_fail", e)}
        save_settings(last_sync=datetime.now().strftime("%Y-%m-%d %H:%M"))
        return {"ok": True, "title": tr("tx_title"), "message": tr("tx_synced", target.name, folder),
                "bootstrap": self.bootstrap()}

    # ------------------------------------------------------------------ history / undo, restore points, backup health
    @safe
    def history_list(self, item_id=None):
        return {"ok": True, "rows": history.recent(300, item_id)}

    @safe
    def history_undo(self, entry_id, confirmed=False):
        if not confirmed:
            return {"ok": False, "needs_confirm": True, "title": tr("hx_title"), "message": tr("hx_confirm")}
        label = history.undo(int(entry_id))
        return {"ok": True, "message": tr("hx_done", label)}

    @safe
    def restore_points(self):
        return {"ok": True, "rows": [dict(r, kind_label=tr("rp_" + r["kind"])) for r in transfer.restore_points()],
                "status": transfer.backup_status(load_settings())}

    @safe
    def restore_point_apply(self, name, confirmed=False):
        path = config.BACKUP_DIR / Path(name).name               # a file name only, never a path
        if not path.is_file():
            return {"ok": False, "error": tr("hx_err_gone")}
        if transfer.is_encrypted(path):
            return {"ok": False, "error": tr("tx_err_need_password")}
        if not confirmed:
            return {"ok": False, "needs_confirm": True, "title": tr("tx_restore_title"),
                    "message": tr("rp_confirm", path.name)}
        try:
            safety = (transfer.restore_db_file(path) if path.suffix == ".db" else transfer.restore_package(path)[1])
        except transfer.PackageError as e:
            return self._pkg_error(e)
        extra = tr("tx_restored_safety", safety.name) if safety else ""
        return {"ok": True, "title": tr("tx_restore_title"), "message": tr("rp_done", path.name, extra),
                "bootstrap": self.bootstrap()}

    # ------------------------------------------------------------------ where the data lives
    @staticmethod
    def _folders():
        f = [("root", config.DATA_DIR, "loc_root"), ("db", config.DB_DIR, "loc_db"), ("photos", config.PHOTO_DIR, "loc_photos"),
             ("backup", config.BACKUP_DIR, "loc_backup"), ("trash", config.TRASH_DIR, "loc_trash"),
             ("export", config.EXPORT_DIR, "loc_export"), ("labels", config.LABEL_DIR, "loc_labels")]
        sync = load_settings().get("sync_dir")
        if sync:
            f.append(("sync", Path(sync), "loc_sync"))
        return f

    @safe
    def data_locations(self):
        rows, cloud = [], False
        for key, path, label in self._folders():
            files = [p for p in path.rglob("*") if p.is_file()] if path.is_dir() and key != "root" else []
            rows.append({"key": key, "path": str(path), "label": tr(label), "hint": tr(label + "_hint"),
                         "exists": path.is_dir(), "files": len(files),
                         "size": round(sum(p.stat().st_size for p in files) / 1048576, 1)})
        if any(w in str(config.DATA_DIR).lower() for w in ("onedrive", "dropbox", "google drive", "googledrive", "icloud")):
            cloud = True
        return {"ok": True, "rows": rows, "cloud_warning": tr("loc_cloud_warn") if cloud else "",
                "custom": config.LOCATION_FILE.exists() and not __import__("os").environ.get("PW_DATA_DIR")}

    @safe
    def open_folder(self, key):
        import os
        import subprocess
        path = {k: p for k, p, _ in self._folders()}.get(key)
        if path is None:
            return {"ok": False, "error": tr("hx_err_gone")}
        path.mkdir(parents=True, exist_ok=True)
        if self._window is None:                                 # dev browser mode: just say where it is
            return {"ok": True, "message": str(path)}
        if sys.platform == "win32":
            os.startfile(str(path))                              # noqa: S606
        elif sys.platform == "darwin":
            subprocess.Popen(["open", str(path)])
        else:
            subprocess.Popen(["xdg-open", str(path)])
        return {"ok": True}

    @safe
    def data_move(self, target=None):
        """Copy everything to a folder the user picks and remember it. The old folder is left untouched."""
        from personal_warehouse.core.database import verify_db
        if not target:
            if self._window is None:
                return {"ok": False, "error": tr("loc_desktop_only")}
            target = self._dialog("folder", directory=str(config.DATA_DIR.parent))
        if not target:
            return {"ok": True, "cancelled": True}
        new = Path(target)
        old = config.DATA_DIR.resolve()
        if new.resolve() == old or old in new.resolve().parents:
            return {"ok": False, "error": tr("loc_same"), "title": tr("loc_move_title")}
        if new.is_dir() and any(new.iterdir()) and not (new / "Database" / "warehouse.db").exists():
            new = new / "MyWarehouse"                            # never scatter our folders among someone's files
        if (new / "Database" / "warehouse.db").exists():
            return {"ok": False, "error": tr("loc_exists", new), "title": tr("loc_move_title")}
        try:
            for sub in config.SUBFOLDERS:
                (new / sub).mkdir(parents=True, exist_ok=True)
            backup_db_to(new / "Database" / "warehouse.db")
            if not verify_db(new / "Database" / "warehouse.db"):
                raise OSError(tr("tx_err_damaged"))
            for sub in ("Photos", "Trash", "Backup", "Export"):
                src = config.DATA_DIR / sub
                if src.is_dir():
                    shutil.copytree(src, new / sub, dirs_exist_ok=True)
            if config.SETTINGS_PATH.exists():
                shutil.copy2(config.SETTINGS_PATH, new / "settings.json")
            config.LOCATION_FILE.parent.mkdir(parents=True, exist_ok=True)
            config.LOCATION_FILE.write_text(str(new), encoding="utf-8")
        except OSError as e:
            return {"ok": False, "title": tr("loc_move_title"), "error": tr("loc_move_fail", e)}
        return {"ok": True, "title": tr("loc_move_title"), "message": tr("loc_moved", new, old), "restart": True}

    @safe
    def suggestions(self):
        """Values already used in the warehouse, most common first - feeds the type-ahead lists of the item form."""
        out = {}
        with db() as con:
            for col in ("name", "category", "engine_application", "supplier"):
                out[col] = [r[0] for r in con.execute(
                    f"SELECT {col} FROM items WHERE {col} IS NOT NULL AND TRIM({col})<>'' "
                    f"GROUP BY {col} COLLATE NOCASE ORDER BY COUNT(*) DESC, {col} LIMIT 300")]
        return {"ok": True, "lists": out}

    # ------------------------------------------------------------------ about, feedback, support
    @safe
    def about_info(self):
        return {"ok": True, "version": __version__, "author": about.AUTHOR_NAME, "email": about.CONTACT_EMAIL,
                "github": about.GITHUB_URL, "donate": about.DONATE,
                "kinds": [{"value": k, "label": tr("fb_kind_" + k)} for k in ("idea", "bug", "thanks", "other")]}

    @safe
    def open_link(self, key):
        url = about.LINKS.get(key)
        if not url:
            return {"ok": False, "error": tr("hx_err_gone")}
        if self._window is None:
            return {"ok": True, "url": url, "open_in_js": True}
        webbrowser.open(url)
        return {"ok": True}

    @safe
    def feedback_send(self, kind, message, contact="", include_info=True, via="mail"):
        """Open the user's mail program (or Gmail on the web) with the message ready to send to the author.

        The app has no mail server and stores no password: the message goes out from the user's own mail account."""
        message = (message or "").strip()
        if len(message) < 5:
            return {"ok": False, "error": tr("fb_empty"), "title": tr("fb_title")}
        subject, body = about.compose(tr("fb_kind_" + kind) if ("fb_kind_" + kind) in TR else kind, message, contact,
                                      bool(include_info), current_lang())
        url = about.gmail_url(subject, body) if via == "gmail" else about.mailto_url(subject, body)
        if len(url) > (about.GMAIL_LIMIT if via == "gmail" else about.MAILTO_LIMIT):
            return {"ok": False, "title": tr("fb_title"), "error": tr("fb_too_long"), "copy": f"{subject}\n\n{body}"}
        if self._window is None:
            return {"ok": True, "url": url, "open_in_js": True, "copy": f"{subject}\n\n{body}"}
        webbrowser.open(url)
        return {"ok": True, "message": tr("fb_opened", about.CONTACT_EMAIL), "copy": f"{subject}\n\n{body}"}

    # ------------------------------------------------------------------ bulk translation
    @safe
    def bulk_translate_prepare(self):
        with db() as con:
            n = con.execute("SELECT COUNT(*) FROM items WHERE is_active=1 AND (name_ar IS NULL OR name_ar='')").fetchone()[0]
        if not n:
            return {"ok": True, "count": 0, "message": tr("bt_nothing")}
        return {"ok": True, "count": n, "title": tr("tr_title"), "message": tr("bt_confirm", n)}

    @safe
    def bulk_translate_start(self):
        if self._bt and not self._bt.get("finished"):
            return {"ok": True}
        with db() as con:
            rows = con.execute("SELECT id,name FROM items WHERE is_active=1 AND (name_ar IS NULL OR name_ar='')").fetchall()
        self._bt = {"rows": [(r["id"], r["name"]) for r in rows], "out": [], "fail": 0, "streak": 0, "done": 0,
                    "finished": False}
        threading.Thread(target=self._bt_worker, args=(self._bt,), daemon=True).start()
        return {"ok": True}

    @staticmethod
    def _bt_worker(st):
        for iid, name in st["rows"]:
            try:
                st["out"].append((iid, translate_online(name, "ar")))
                st["streak"] = 0
            except Exception:                                    # noqa: BLE001
                st["fail"] += 1
                st["streak"] += 1
                if st["streak"] >= 3:                            # probably offline
                    break
            st["done"] += 1
            time.sleep(0.15)
        st["finished"] = True

    @safe
    def bulk_translate_status(self):
        st = self._bt
        if not st:
            return {"ok": True, "idle": True}
        if not st["finished"]:
            return {"ok": True, "finished": False, "message": tr("bt_progress", st["done"], len(st["rows"]))}
        if st.get("saved") is None:
            if st["out"]:
                with db() as con:
                    for i, t in st["out"]:
                        if not t:
                            continue
                        old = history.snapshot(con, i)
                        con.execute("UPDATE items SET name_ar=?,updated_at=CURRENT_TIMESTAMP WHERE id=?", (t, i))
                        history.log(con, "update", i, history._label(old), old, history.snapshot(con, i))
            st["saved"] = True
        if st["streak"] >= 3 and not st["out"]:
            return {"ok": True, "finished": True, "error": tr("bt_offline"), "title": tr("tr_title")}
        return {"ok": True, "finished": True, "title": tr("tr_title"),
                "message": tr("bt_done", len(st["out"]), st["fail"])}

    # ------------------------------------------------------------------ updates
    def _can_install(self):
        """In-app install: only in the installed desktop app (not --browser, not from source, not a Store package)."""
        return self._window is not None and updater.can_self_update()

    @safe
    def check_updates(self, manual=False):
        title = tr("upd_title")
        if updater.is_store_package():                           # the Microsoft Store updates this install
            return {"ok": True, "status": "store", "title": title, "message": tr("upd_store")} if manual \
                else {"ok": True, "status": "skip"}
        if not manual and not load_settings().get("auto_update", True):
            return {"ok": True, "status": "skip"}
        res = updater.check()
        if res["status"] == "new":
            rel = res["release"]
            self._release = rel
            can = self._can_install() and bool(rel["download"])
            return {"ok": True, "status": "new", "title": title, "url": rel["download"] or rel["page"],
                    "can_install": can, "version": rel["version"],
                    "message": tr("upd_new_body", rel["version"], __version__, rel["notes"] or ""),
                    "toast": tr("upd_status", rel["version"])}
        if not manual:
            return {"ok": True, "status": "skip"}
        if res["status"] == "current":
            return {"ok": True, "status": "current", "title": title, "message": tr("upd_none", __version__)}
        if res["status"] == "disabled":
            return {"ok": True, "status": "disabled", "title": title, "message": tr("upd_disabled")}
        return {"ok": False, "error": tr("upd_fail", res["error"]), "title": title}

    @safe
    def update_start(self):
        """Begin downloading the installer found by the last check (runs in the background)."""
        rel = self._release
        if not rel or not rel.get("download") or not self._can_install():
            return {"ok": False, "error": tr("upd_dl_fail", "no installer available")}
        if self._dl and not self._dl["finished"]:
            return {"ok": True}
        updater.clean_update_dir()
        self._dl = {"done": 0, "total": rel.get("size") or 0, "finished": False, "error": "", "cancel": False,
                    "path": "", "version": rel["version"]}
        threading.Thread(target=self._dl_worker, args=(self._dl, rel), daemon=True).start()
        return {"ok": True}

    @staticmethod
    def _dl_worker(st, rel):
        dest = updater.update_dir() / f"PersonalWarehouse-Setup-{rel['version']}.exe"

        def progress(done, total):
            st["done"], st["total"] = done, total
        try:
            updater.download(rel["download"], dest, rel.get("sha256", ""), rel.get("size", 0),
                             progress=progress, cancelled=lambda: st["cancel"])
            st["path"] = str(dest)
        except InterruptedError:
            st["error"] = "cancelled"
        except Exception as e:                                   # noqa: BLE001 - shown to the user
            st["error"] = str(e) or type(e).__name__
        st["finished"] = True

    @safe
    def update_status(self):
        st = self._dl
        if not st:
            return {"ok": True, "idle": True}
        mb = 1024 * 1024
        pct = int(st["done"] * 100 / st["total"]) if st["total"] else 0
        msg = (tr("upd_dl_progress", f"{st['done'] / mb:.1f}", f"{st['total'] / mb:.1f}") if st["total"]
               else tr("upd_dl_progress_unknown", f"{st['done'] / mb:.1f}"))
        err = "" if st["error"] == "cancelled" else st["error"]
        return {"ok": True, "percent": min(pct, 100), "message": msg, "finished": st["finished"],
                "error": tr("upd_dl_fail", err) if err else "", "cancelled": st["error"] == "cancelled"}

    @safe
    def update_cancel(self):
        if self._dl and not self._dl["finished"]:
            self._dl["cancel"] = True
        return {"ok": True}

    @safe
    def update_install(self):
        """Run the verified installer silently and close the app so it can replace the files."""
        st = self._dl
        if not (st and st["finished"] and not st["error"] and st["path"]) or not self._can_install():
            return {"ok": False, "error": tr("upd_dl_fail", "installer not ready")}
        from personal_warehouse.core.database import auto_backup
        auto_backup(overwrite=True)                              # data is backed up before anything is replaced
        updater.launch_installer(st["path"])
        threading.Timer(0.8, self._window.destroy).start()       # let this reply reach the page first
        return {"ok": True, "message": tr("upd_installing")}

    @safe
    def open_url(self, url):
        if isinstance(url, str) and url.startswith("https://"):
            webbrowser.open(url)
        return {"ok": True}

    @safe
    def quit(self):
        from personal_warehouse.core.database import auto_backup
        auto_backup(overwrite=True)
        folder = load_settings().get("sync_dir")
        if folder:                                               # keep the online copy current; never block closing
            try:
                transfer.sync_to_folder(folder)
                save_settings(last_sync=datetime.now().strftime("%Y-%m-%d %H:%M"))
            except Exception:                                    # noqa: BLE001
                pass
        if self._window is not None:
            self._window.destroy()
        return {"ok": True}
