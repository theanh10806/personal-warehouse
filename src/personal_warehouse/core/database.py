"""SQLite access: connection, schema, migrations, movement log, backups."""

from contextlib import contextmanager
from datetime import datetime
import shutil
import sqlite3

from personal_warehouse import config
from personal_warehouse.config import KEEP_AUTO_BACKUPS, SCHEMA_VERSION


@contextmanager
def db():
    con = sqlite3.connect(config.DB_PATH, timeout=10)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys=ON")
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


def auto_backup(overwrite):
    target = config.BACKUP_DIR / f"warehouse_{datetime.now():%Y%m%d}.db"
    try:
        if overwrite or not target.exists():
            backup_db_to(target)
        for old in sorted(config.BACKUP_DIR.glob("warehouse_*.db"))[:-KEEP_AUTO_BACKUPS]:
            old.unlink(missing_ok=True)
    except Exception:
        pass
