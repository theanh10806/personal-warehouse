"""Stock rules: changing quantities (always logged) and finding an item from a scanned / typed code."""
import math

from personal_warehouse.config import CODE_RE
from personal_warehouse.core.database import db, record_movement
from personal_warehouse.core.formatting import qty_fmt
from personal_warehouse.core.history import log
from personal_warehouse.i18n import tr, unit_t


def apply_movement(iid, typ, q, price, reason):
    """Change stock and log it. Returns (row, before, after); raises ValueError with a readable message.

    ``typ`` is "Stock In", "Stock Out" or "Adjustment" (for an adjustment ``q`` is the counted quantity).
    """
    if typ not in ("Stock In", "Stock Out", "Adjustment"):
        raise ValueError("Invalid movement type")
    if not all(isinstance(value, (int, float)) and not isinstance(value, bool)
               and math.isfinite(value) and value >= 0 for value in ((q,) if price is None else (q, price))):
        raise ValueError("Quantity and price must be finite non-negative numbers")
    if typ != "Adjustment" and q == 0:
        raise ValueError("Movement quantity must be positive")
    with db() as con:
        con.execute("BEGIN IMMEDIATE")
        r = con.execute("SELECT quantity,unit,min_stock,name,name_ar,item_code FROM items WHERE id=?", (iid,)).fetchone()
        if r is None:
            raise ValueError("Item does not exist")
        before = r["quantity"]
        after = before + q if typ == "Stock In" else before - q if typ == "Stock Out" else q
        if not math.isfinite(after):
            raise ValueError("Stock quantity exceeds the supported range")
        if after < -1e-9:
            raise ValueError(tr("err_not_enough", qty_fmt(before), unit_t(r["unit"])))
        after = max(after, 0.0)
        if typ == "Adjustment" and abs(after - before) < 1e-9:
            raise ValueError(tr("err_nochange"))
        con.execute("UPDATE items SET quantity=?,updated_at=CURRENT_TIMESTAMP WHERE id=?", (after, iid))
        record_movement(con, iid, typ, q, reason, price, before, after)
        log(con, "movement", iid, f'{r["item_code"]} {r["name"]}', None,
            {"type": typ, "qty": q, "qty_before": before, "qty_after": after})
    return r, before, after


def find_item(text):
    """Match an item code, a custom barcode, a full QR payload or a bare number. Returns (row, code)."""
    text = (text or "").strip()
    if not text:
        return None, None
    with db() as con:
        r = con.execute("SELECT * FROM items WHERE item_code=? COLLATE NOCASE OR barcode=?",
                        (text, text)).fetchone()
        if r:
            return r, r["item_code"]
        m = CODE_RE.search(text.upper())
        code = m.group(0) if m else (f"WH-{int(text):05d}" if text.isdigit() and len(text) < 9 else None)
        if code:
            r = con.execute("SELECT * FROM items WHERE item_code=?", (code,)).fetchone()
    return r, code
