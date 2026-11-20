"""Create a separate demo warehouse; refuse to reuse a nonempty directory."""
import argparse
import base64
import json
import os
from pathlib import Path
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    destination = args.destination.resolve()
    if destination.exists() and any(destination.iterdir()):
        parser.error("Destination must be empty; existing data will never be overwritten")
    destination.mkdir(parents=True, exist_ok=True)
    os.environ["PW_DATA_DIR"] = str(destination)
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
    from personal_warehouse import config
    from personal_warehouse.core.database import db, init_db, verified_backup
    from personal_warehouse.core.exporter import export_inventory
    from personal_warehouse.core.transfer import create_package
    from personal_warehouse.i18n import set_language
    from personal_warehouse.webui.api import Api
    config.ensure_dirs()
    init_db()
    set_language("vi")
    api = Api()
    photo = destination / "sample.png"
    photo.write_bytes(base64.b64decode(
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+jRZkAAAAASUVORK5CYII="))
    for slot, (section, part) in enumerate((section, part) for section in config.SECTIONS for part in config.PARTS):
        for variant, condition in enumerate(config.CONDITIONS):
            index = slot * 4 + variant
            result = api.save_item({
                "name": f"Mẫu {index + 1:03d} – Bộ lọc, ốc vít <M8>",
                "name_ar": f"قطعة {index + 1}", "category": f"Nhóm {variant + 1}",
                "description": "Dữ liệu thử nghiệm\nKhông phải hàng thật",
                "section": section, "part": part, "condition": condition,
                "unit": config.UNITS[index % len(config.UNITS)],
                "quantity": str((0, 2, 10.5, 100)[variant]), "min_stock": "3",
                "purchase_price": "12.50", "selling_price": "20.75",
                "barcode": f"DEMO-{index + 1:05d}", "supplier": "Nhà cung cấp mẫu",
                "notes": "Chỉ dùng kiểm thử", "photo_path": str(photo) if variant == 2 else None,
                "confirmed": ["duplicate", "price_below"],
            })
            if not result.get("ok"):
                raise RuntimeError(result)
            if variant == 3:
                item_id = result["id"]
                for movement, quantity in (("Stock In", "5"), ("Stock Out", "3"), ("Adjustment", "99")):
                    result = api.save_movement({"item_id": item_id,
                                                "type": movement, "qty": quantity, "reason": "Demo"})
                    if not result.get("ok"):
                        raise RuntimeError(result)
    export_inventory(config.EXPORT_DIR / "demo.csv")
    export_inventory(config.EXPORT_DIR / "demo.xlsx")
    if not verified_backup(config.BACKUP_DIR / "demo.db"):
        raise RuntimeError("Backup verification failed")
    manifest = create_package(config.EXPORT_DIR / "demo.pwbak")
    with db() as connection:
        report = {"items": connection.execute("SELECT COUNT(*) FROM items").fetchone()[0],
                  "movements": manifest["movements"], "locations": 24,
                  "integrity": connection.execute("PRAGMA integrity_check").fetchone()[0]}
    (destination / "demo-summary.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report))


if __name__ == "__main__":
    main()
