"""SQLite access: connection, schema, migrations, movement log, backups."""

from contextlib import contextmanager
from datetime import datetime
import os
from pathlib import Path
import shutil
import sqlite3

from personal_warehouse import config
from personal_warehouse.config import KEEP_AUTO_BACKUPS, SCHEMA_VERSION


@contextmanager
def db():
    con = sqlite3.connect(config.DB_PATH, timeout=10)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys=ON")
    con.execute("PRAGMA synchronous=FULL")             # a power cut must not lose or corrupt committed work
    try:
        yield con
        con.commit()
    except Exception:
        con.rollback()
        raise
    finally:
        con.close()


def _add_column(con, table, col, ddl):
    if col not in [r["name"] for r in con.execute(f"PRAGMA table_info({table})")]:
        con.execute(f"ALTER TABLE {table} ADD COLUMN {col} {ddl}")


def init_db():
    with db() as con:
        con.executescript("""
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT, item_code TEXT UNIQUE, name TEXT NOT NULL,
            category TEXT, description TEXT, engine_application TEXT,
            section TEXT NOT NULL, part TEXT NOT NULL, condition TEXT NOT NULL DEFAULT 'New',
            quantity REAL NOT NULL DEFAULT 0, unit TEXT NOT NULL DEFAULT 'pcs',
            purchase_price REAL NOT NULL DEFAULT 0, selling_price REAL NOT NULL DEFAULT 0,
            photo_path TEXT, date_added TEXT, supplier TEXT, notes TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP, updated_at TEXT DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS movements (
            id INTEGER PRIMARY KEY AUTOINCREMENT, item_id INTEGER NOT NULL,
            movement_type TEXT NOT NULL, quantity REAL NOT NULL, reason TEXT, movement_date TEXT NOT NULL,
            FOREIGN KEY(item_id) REFERENCES items(id));
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT NOT NULL, action TEXT NOT NULL, item_id INTEGER,
            label TEXT, before TEXT, after TEXT, undone INTEGER NOT NULL DEFAULT 0);
        CREATE INDEX IF NOT EXISTS idx_history_item ON history(item_id, id);
        CREATE INDEX IF NOT EXISTS idx_items_name ON items(name);
        CREATE INDEX IF NOT EXISTS idx_items_location ON items(section, part);
        """)
        version = con.execute("PRAGMA user_version").fetchone()[0]
        # Columns are checked on every start (idempotent), so a database whose version number
        # is ahead of its real structure is repaired instead of crashing.
        _add_column(con, "items", "min_stock", "REAL NOT NULL DEFAULT 0")
        _add_column(con, "items", "is_active", "INTEGER NOT NULL DEFAULT 1")
        _add_column(con, "items", "barcode", "TEXT")
        _add_column(con, "items", "name_ar", "TEXT")
        _add_column(con, "movements", "qty_before", "REAL")
        _add_column(con, "movements", "qty_after", "REAL")
        _add_column(con, "movements", "unit_price", "REAL")
        con.execute("CREATE INDEX IF NOT EXISTS idx_movements_item ON movements(item_id, id)")
        con.execute("CREATE INDEX IF NOT EXISTS idx_items_barcode ON items(barcode)")
        if version < 2:                                    # v2 parts A/B/C -> 1/2/3 (one-time data change)
            con.execute("UPDATE items SET part='1' WHERE part='A'")
            con.execute("UPDATE items SET part='2' WHERE part='B'")
            con.execute("UPDATE items SET part='3' WHERE part='C'")
        con.execute(f"PRAGMA user_version={SCHEMA_VERSION}")


def pre_migration_backup():
    """Keep a copy of the old database before the schema is upgraded."""
    try:
        if config.DB_PATH.exists():
            con = sqlite3.connect(config.DB_PATH)
            ver = con.execute("PRAGMA user_version").fetchone()[0]
            con.close()
            if ver < SCHEMA_VERSION:
                shutil.copy2(config.DB_PATH, config.BACKUP_DIR / f"before_v{SCHEMA_VERSION}_{datetime.now():%Y%m%d_%H%M%S}.db")
    except Exception:
        pass


def record_movement(con, item_id, typ, qty, reason, price, before, after):
    con.execute("""INSERT INTO movements(item_id,movement_type,quantity,reason,movement_date,
                   qty_before,qty_after,unit_price) VALUES(?,?,?,?,?,?,?,?)""",
                (item_id, typ, qty, reason, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), before, after, price))


def backup_db_to(path):
    with db() as src:
        dst = sqlite3.connect(path)
        try:
            src.backup(dst)
        finally:
            dst.close()


def verify_db(path):
    """True when ``path`` is a healthy warehouse database (SQLite integrity check + our tables exist)."""
    try:
        con = sqlite3.connect(f"file:{Path(path).as_posix()}?mode=ro", uri=True)
        try:
            if con.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
                return False
            names = {r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'")}
            return {"items", "movements"} <= names
        finally:
            con.close()
    except sqlite3.Error:
        return False


def verified_backup(path):
    """Back up to ``path`` and prove the copy is readable; a bad copy is deleted and reported as False."""
    path = Path(path)
    backup_db_to(path)
    if verify_db(path):
        return True
    path.unlink(missing_ok=True)
    return False


def prune_backups(folder=None, today=None):
    """Grandfather-father-son retention for ``warehouse_YYYYMMDD.db``: newest daily + one per week + one per month.

    Safety copies (``before_*``) are trimmed separately, newest KEEP_SAFETY_BACKUPS of each kind.
    """
    folder = Path(folder or config.BACKUP_DIR)
    keep, weeks, months = set(), set(), set()
    dated = []
    for f in folder.glob("warehouse_*.db"):
        try:
            dated.append((datetime.strptime(f.stem.split("_")[1], "%Y%m%d").date(), f))
        except (ValueError, IndexError):
            pass
    dated.sort(reverse=True)
    for n, (d, f) in enumerate(dated):
        wk, mo = d.isocalendar()[:2], (d.year, d.month)
        if n < config.KEEP_AUTO_BACKUPS:
            keep.add(f)
        if wk not in weeks and len(weeks) < config.KEEP_WEEKLY_BACKUPS:
            weeks.add(wk)
            keep.add(f)
        if mo not in months and len(months) < config.KEEP_MONTHLY_BACKUPS:
            months.add(mo)
            keep.add(f)
    for _, f in dated:
        if f not in keep:
            f.unlink(missing_ok=True)
    for kind in ("before_delete_*.db", "before_v*.db", "before_restore_*.pwbak"):
        for old in sorted(folder.glob(kind))[:-config.KEEP_SAFETY_BACKUPS]:
            old.unlink(missing_ok=True)


def auto_backup(overwrite):
    target = config.BACKUP_DIR / f"warehouse_{datetime.now():%Y%m%d}.db"
    try:
        if overwrite or not target.exists():
            tmp = target.with_name(target.name + ".tmp")        # never replace a good backup with a half-written one
            if verified_backup(tmp):
                os.replace(tmp, target)
        prune_backups()
    except Exception:
        pass
