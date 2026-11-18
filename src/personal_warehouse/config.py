"""Constants and file locations. No imports from the rest of the app, so everything can depend on it."""
import os
import re
from pathlib import Path

APP_NAME = "Personal Warehouse"
<<<<<<< HEAD
SECTIONS = list("ABC")                 # 3 sections: A, B, C
PARTS = [str(i) for i in range(1, 9)]  # 8 parts per section: 1..8  (24 locations: A1 ... C8)
=======
SECTIONS = list("ABCDEFGH")            # 8 sections: A..H
PARTS = ["1", "2", "3"]                # 3 parts per section: 1, 2, 3
>>>>>>> c8a133662267867832f0d0679ec8832dee7dfdbb
CONDITIONS = ["New", "Used", "Damaged", "Refurbished"]
UNITS = ["pcs", "sets", "boxes", "kg", "L", "m", "pairs", "other"]
MOVE_TYPES = ["Stock In", "Stock Out", "Adjustment"]
MOVE_KEYS = {"Stock In": "mv_in", "Stock Out": "mv_out", "Adjustment": "mv_adj", "Opening stock": "mv_open"}
SCHEMA_VERSION = 3
KEEP_AUTO_BACKUPS = 14
LAYOUTS = ["a4", "printer"]
LABEL_KINDS = ["qr", "barcode", "both"]
LABEL_SIZES = {"Small 50×30 mm": (50, 30, 24, 7), "Medium 70×40 mm": (70, 40, 33, 8.5),
               "Large 100×60 mm": (100, 60, 50, 12)}      # width, height, QR size (mm), font (pt)
CODE_RE = re.compile(r"WH-\d{5,}")

# PW_DATA_DIR lets tests (or portable installs) keep their data somewhere else.
DATA_DIR = Path(os.environ["PW_DATA_DIR"]) if os.environ.get("PW_DATA_DIR") else Path.home() / "Documents" / "MyWarehouse"
DB_DIR, PHOTO_DIR, BACKUP_DIR = DATA_DIR / "Database", DATA_DIR / "Photos", DATA_DIR / "Backup"
LABEL_DIR = DATA_DIR / "Labels"
DB_PATH = DB_DIR / "warehouse.db"
SETTINGS_PATH = DATA_DIR / "settings.json"

SEARCH_COLS = ["item_code", "name", "name_ar", "category", "engine_application", "description",
               "supplier", "notes", "barcode", "(section || part)"]
SORT_SQL = {"code": "item_code", "name": "name COLLATE NOCASE", "category": "category COLLATE NOCASE",
            "engine": "engine_application COLLATE NOCASE", "location": "section||part",
            "condition": "condition", "qty": "quantity", "buy": "purchase_price", "sell": "selling_price"}


def ensure_dirs():
    """Create the data folders. Called once at start-up (importing this module has no side effects)."""
    for p in (DB_DIR, PHOTO_DIR, BACKUP_DIR, LABEL_DIR):
        p.mkdir(parents=True, exist_ok=True)
