"""Export the whole warehouse to Excel (.xlsx, 3 sheets) or CSV. No GUI code."""
import csv

from personal_warehouse.config import PARTS, SECTIONS
from personal_warehouse.core.database import db
from personal_warehouse.core.formatting import make_location
from personal_warehouse.i18n import cond_t, mv_t, tr, unit_t


class ExcelUnavailable(Exception):
    """openpyxl is not installed (CSV export still works)."""


def inventory_table():
    """Return (header, rows, movements) for the inventory sheet, in the current language."""
    head = [tr("h_code"), tr("f_name"), tr("f_name_ar"), tr("f_category"), tr("f_description"), tr("f_engine"),
            tr("f_barcode").split(" (")[0], tr("h_location"), tr("f_condition"), tr("f_qty").split(" (")[0],
            tr("f_unit"), tr("f_min"), tr("f_buy"), tr("f_sell"), tr("x_profit"), tr("x_stockval"),
            tr("f_supplier"), tr("f_notes"), tr("x_photo"), tr("sc_added"), tr("x_status")]
    with db() as con:
        items = con.execute("SELECT * FROM items ORDER BY section,part,name").fetchall()
        moves = con.execute("""SELECT m.movement_date,i.item_code,i.name,m.movement_type,
            m.quantity,m.qty_before,m.qty_after,m.unit_price,m.reason
            FROM movements m JOIN items i ON i.id=m.item_id ORDER BY m.id""").fetchall()
    data = [[r["item_code"], r["name"], r["name_ar"], r["category"], r["description"],
             r["engine_application"], r["barcode"], make_location(r["section"], r["part"]),
             cond_t(r["condition"]), r["quantity"], unit_t(r["unit"]), r["min_stock"],
             r["purchase_price"], r["selling_price"],
             round(r["selling_price"] - r["purchase_price"], 2),
             round(r["quantity"] * r["purchase_price"], 2),
             r["supplier"], r["notes"], r["photo_path"], r["date_added"],
             tr("x_active") if r["is_active"] else tr("x_archived")] for r in items]
    return head, data, moves


def export_inventory(path, rtl=False):
    """Write ``path`` (.csv or .xlsx). Raises ExcelUnavailable when an .xlsx is wanted but openpyxl is missing."""
    head, data, moves = inventory_table()
    if str(path).lower().endswith(".csv"):
        with open(path, "w", newline="", encoding="utf-8-sig") as fh:
            w = csv.writer(fh)
            w.writerow(head)
            w.writerows(data)
        return
    try:
        from openpyxl import Workbook
        from openpyxl.styles import Font, PatternFill
        from openpyxl.utils import get_column_letter
    except ImportError:
        raise ExcelUnavailable() from None
    wb = Workbook()
    sheets = [
        (wb.active, tr("x_sheet_inv"), head, data, {13, 14, 15, 16}),
        (wb.create_sheet(), tr("x_sheet_mov"),
         [tr("h_date"), tr("h_code"), tr("f_name"), tr("h_move"), tr("h_qty"),
          tr("h_change").split(" ")[0], "→", tr("h_price"), tr("h_reason")],
         [[r[0], r[1], r[2], mv_t(r[3]), r[4], r[5], r[6], r[7], r[8]] for r in moves], {8}),
        (wb.create_sheet(), tr("x_sheet_loc"), [tr("f_section"), tr("f_part"), tr("h_location")],
         [[s, p, make_location(s, p)] for s in SECTIONS for p in PARTS], set())]
    for ws, title, hd, rows, money_cols in sheets:
        ws.title = title[:31]
        ws.append(hd)
        for r in rows:
            ws.append(r)
        for c in ws[1]:
            c.font = Font(bold=True, color="FFFFFF")
            c.fill = PatternFill("solid", fgColor="1E5AA8")
        ws.freeze_panes = "A2"
        ws.auto_filter.ref = ws.dimensions
        if rtl:
            ws.sheet_view.rightToLeft = True
        for i, col in enumerate(ws.columns, 1):
            ws.column_dimensions[get_column_letter(i)].width = min(
                45, max(10, max(len(str(c.value or "")) for c in col) + 2))
            if i in money_cols:
                for c in col[1:]:
                    c.number_format = '"$"#,##0.00'
    wb.save(path)
