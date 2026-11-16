"""Printable label pages (QR / barcode) built as HTML."""

import base64
from datetime import datetime
import html as htmllib
import io

from personal_warehouse.config import LABEL_SIZES
from personal_warehouse.core.barcode import code128_svg
from personal_warehouse.core.formatting import item_name, make_location, money, qty_fmt
from personal_warehouse.i18n import cond_t, tr


def item_payload(r, with_prices=True, limit=300):
    def clip(v, n=limit):
        return " ".join(str(v or "").split())[:n]
    lines = [f"WAREHOUSE ITEM {r['item_code']}", f"Name: {clip(r['name'], 120)}"]
    for label, key in (("Category", "category"), ("Description", "description"),
                       ("Engine/Application", "engine_application")):
        if clip(r[key]):
            lines.append(f"{label}: {clip(r[key])}")
    lines += [f"Location: {make_location(r['section'], r['part'])}",
              f"Condition: {r['condition']}",
              f"Stock at print ({datetime.now():%Y-%m-%d}): {qty_fmt(r['quantity'])} {r['unit']}"]
    if r["min_stock"]:
        lines.append(f"Min stock: {qty_fmt(r['min_stock'])}")
    if with_prices:
        lines += [f"Purchase: {money(r['purchase_price'])}", f"Selling: {money(r['selling_price'])}"]
    for label, key in (("Supplier", "supplier"), ("Notes", "notes")):
        if clip(r[key]):
            lines.append(f"{label}: {clip(r[key])}")
    if r["date_added"]:
        lines.append(f"Added: {r['date_added']}")
    text = "\n".join(lines)
    return text if len(text.encode("utf-8")) <= 1500 or limit <= 80 else item_payload(r, with_prices, 80)


def qr_b64(text):
    import qrcode
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=10, border=2)
    qr.add_data(text)
    qr.make(fit=True)
    buf = io.BytesIO()
    qr.make_image(fill_color="black", back_color="white").save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()


def build_label_html(items, o):
    w, h, qr_mm, pt = LABEL_SIZES[o["size"]]
    kind = o["kind"]
    use_qr, use_bc = kind in ("qr", "both"), kind in ("barcode", "both")
    single = o["layout"] == "printer"
    e = htmllib.escape
    if kind == "both":
        qr_mm = round(qr_mm * 0.6, 1)
    bc_h = round(h * (0.22 if kind == "both" else 0.3), 1)
    labels = []
    for r in items:
        code = r["item_code"] or ""
        parts = []
        if not use_bc:
            parts.append(f'<div class="code">{e(code)}</div>')
        parts.append(f'<div class="name">{e(item_name(r))}</div>')
        sub = " • ".join(x for x in (r["category"], r["engine_application"]) if x)
        if sub:
            parts.append(f'<div class="sub">{e(sub)}</div>')
        parts.append(f'<div>{e(tr("lbl_loc"))} <b>{make_location(r["section"], r["part"])}</b>'
                     f' • {e(cond_t(r["condition"]))}</div>')
        text_html = f'<div class="t" dir="auto">{"".join(parts)}</div>'
        img = ""
        if use_qr:
            payload = item_payload(r, o["prices"]) if o["full"] else code
            img = f'<img class="qr" src="data:image/png;base64,{qr_b64(payload)}">'
        bc = (f'<div class="bc">{code128_svg(code)}</div><div class="bcn">{e(code)}</div>') if use_bc else ""
        if kind == "qr":
            body = f'<div class="row">{img}{text_html}</div>'
        elif kind == "barcode":
            body = f'{text_html}{bc}'
        else:
            body = f'<div class="row">{img}{text_html}</div>{bc}'
        labels += [f'<div class="label">{body}</div>'] * o["copies"]
    page = f"@page{{size:{w}mm {h}mm;margin:0}}" if single else "@page{size:A4;margin:8mm}"
    label_css = (f".label{{width:{w}mm;height:{h}mm;display:flex;flex-direction:column;justify-content:center;"
                 f"gap:1mm;padding:2mm;overflow:hidden;break-inside:avoid;page-break-inside:avoid;"
                 + ("page-break-after:always;break-after:page;" if single else "border:.2mm dashed #999;") + "}")
    return f"""<!doctype html><html><head><meta charset="utf-8"><title>Labels</title><style>
{page}
*{{box-sizing:border-box}} body{{margin:0;font-family:'Segoe UI',Arial,sans-serif;color:#000}}
.sheet{{display:flex;flex-wrap:wrap;gap:{0 if single else 2}mm}}
{label_css}
.row{{display:flex;align-items:center;gap:2mm;min-height:0;overflow:hidden}}
.qr{{width:{qr_mm}mm;height:{qr_mm}mm;flex:none;image-rendering:pixelated}}
.t{{font-size:{pt}pt;line-height:1.25;min-width:0;overflow:hidden}}
.code{{font-weight:700;font-size:1.15em}}
.name{{font-weight:600;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}}
.sub{{color:#333;display:-webkit-box;-webkit-line-clamp:1;-webkit-box-orient:vertical;overflow:hidden}}
.bc svg{{display:block;width:100%;height:{bc_h}mm}}
.bcn{{text-align:center;font-family:'Courier New',monospace;font-weight:700;font-size:{max(pt - 1, 6)}pt;line-height:1}}
@media screen{{body{{padding:10px;background:#eee}} .label{{background:#fff}}}}
</style></head><body><div class="sheet">{"".join(labels)}</div>
<script>window.addEventListener('load',()=>setTimeout(()=>window.print(),500))</script></body></html>"""
