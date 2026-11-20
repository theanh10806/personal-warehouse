"""Constants and file locations. No imports from the rest of the app, so everything can depend on it."""
import os
import re
from pathlib import Path

APP_NAME = "Personal Warehouse"
SECTIONS = list("ABC")                 # 3 sections: A, B, C
PARTS = [str(i) for i in range(1, 9)]  # 8 parts per section: 1..8  (24 locations: A1 ... C8)
CONDITIONS = ["New", "Used", "Damaged", "Refurbished"]
UNITS = ["pcs", "sets", "boxes", "kg", "L", "m", "pairs", "other"]
MOVE_TYPES = ["Stock In", "Stock Out", "Adjustment"]
MOVE_KEYS = {"Stock In": "mv_in", "Stock Out": "mv_out", "Adjustment": "mv_adj", "Opening stock": "mv_open"}
SCHEMA_VERSION = 4
KEEP_AUTO_BACKUPS = 14      # newest daily copies kept ...
KEEP_WEEKLY_BACKUPS = 8     # ... plus one per week for 8 weeks ...
KEEP_MONTHLY_BACKUPS = 12   # ... plus one per month for 12 months
KEEP_SAFETY_BACKUPS = 20    # "before delete / restore / upgrade" copies, per kind
TRASH_DAYS = 90             # photos of deleted / replaced items stay recoverable this long
OFFSITE_WARN_DAYS = 7       # warn when no copy has left this computer for this long
LAYOUTS = ["a4", "printer"]
LABEL_KINDS = ["qr", "barcode", "both"]
LABEL_SIZES = {"Small 50×30 mm": (50, 30, 24, 7), "Medium 70×40 mm": (70, 40, 33, 8.5),
               "Large 100×60 mm": (100, 60, 50, 12)}      # width, height, QR size (mm), font (pt)
CODE_RE = re.compile(r"WH-\d{5,}")

LOCATION_FILE = Path.home() / ".personal_warehouse" / "location.txt"   # remembers a data folder the user chose
SUBFOLDERS = ("Database", "Photos", "Backup", "Trash", "Labels", "Export")


def _documents_dir():
    """The real 'Documents' folder (Windows may redirect it into OneDrive, so ask the system, not Path.home())."""
    if os.name == "nt":
        try:
            import ctypes
            from ctypes import wintypes
            buf = ctypes.create_unicode_buffer(wintypes.MAX_PATH)
            if ctypes.windll.shell32.SHGetFolderPathW(None, 5, None, 0, buf) == 0 and buf.value:   # CSIDL_PERSONAL
                return Path(buf.value)
        except Exception:
            pass
    return Path.home() / "Documents"


def resolve_data_dir():
    """One rule, always the same answer: PW_DATA_DIR (tests / portable) > folder the user chose > the
    folder older versions already use > <Documents>/MyWarehouse."""
    if os.environ.get("PW_DATA_DIR"):
        return Path(os.environ["PW_DATA_DIR"])
    try:
        chosen = LOCATION_FILE.read_text(encoding="utf-8").strip()
        if chosen and Path(chosen).is_dir():
            return Path(chosen)
    except OSError:
        pass
    legacy = Path.home() / "Documents" / "MyWarehouse"
    return legacy if legacy.exists() else _documents_dir() / "MyWarehouse"


DATA_DIR = resolve_data_dir()
DB_DIR, PHOTO_DIR, BACKUP_DIR = DATA_DIR / "Database", DATA_DIR / "Photos", DATA_DIR / "Backup"
LABEL_DIR = DATA_DIR / "Labels"
TRASH_DIR = DATA_DIR / "Trash"
EXPORT_DIR = DATA_DIR / "Export"          # default place for every file the app writes for you (Excel, .pwbak)
DB_PATH = DB_DIR / "warehouse.db"
SETTINGS_PATH = DATA_DIR / "settings.json"

SEARCH_COLS = ["item_code", "name", "name_ar", "category", "engine_application", "description",
               "supplier", "notes", "barcode", "(section || part)"]
SORT_SQL = {"code": "item_code", "name": "name COLLATE NOCASE", "category": "category COLLATE NOCASE",
            "engine": "engine_application COLLATE NOCASE", "location": "section||part",
            "condition": "condition", "qty": "quantity", "buy": "purchase_price", "sell": "selling_price"}


def ensure_dirs():
    """Create the data folders. Called once at start-up (importing this module has no side effects)."""
    for p in (DB_DIR, PHOTO_DIR, BACKUP_DIR, LABEL_DIR, TRASH_DIR, EXPORT_DIR):
        p.mkdir(parents=True, exist_ok=True)
