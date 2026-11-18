"""UI texts (vi / en / ar) for: movements."""

from personal_warehouse.i18n.core import add as _t


_t("mv_title", "Nhập / Xuất kho", "Stock In / Out", "إدخال / إخراج المخزون")
_t("mv_sub", "Mọi thay đổi số lượng đều được ghi lại. Gõ để tìm hàng. Điều chỉnh = nhập số lượng kiểm đếm thực tế.",
   "Every quantity change is logged. Type to search the item list. Adjustment = set the counted quantity.",
   "يتم تسجيل كل تغيير في الكمية. اكتب للبحث. التسوية = إدخال الكمية المعدودة.")
_t("mv_item", "Hàng (gõ để tìm)", "Item (type to search)", "الصنف (اكتب للبحث)")
_t("mv_type", "Loại giao dịch", "Movement", "الحركة")
_t("mv_qty", "Số lượng", "Quantity", "الكمية")
_t("mv_counted", "SL kiểm đếm", "Counted qty", "الكمية المعدودة")
_t("mv_price", "Đơn giá (USD)", "Unit price (USD)", "سعر الوحدة (USD)")
_t("mv_reason", "Lý do / tham chiếu", "Reason / reference", "السبب / المرجع")
_t("mv_save", "Lưu giao dịch", "Save movement", "حفظ الحركة")
_t("mv_pick", "Chọn một mặt hàng.", "Pick an item.", "اختر صنفًا.")
_t("mv_pick2", "Chọn hàng trong danh sách.", "Pick an item from the list.", "اختر صنفًا من القائمة.")
_t("mv_history", "Lịch sử (500 gần nhất)", "History (latest 500)", "السجل (آخر 500)")
_t("mv_only", "Chỉ hàng đang chọn", "Only the selected item", "الصنف المحدد فقط")
_t("mv_in", "Nhập kho", "Stock In", "إدخال")
_t("mv_out", "Xuất kho", "Stock Out", "إخراج")
_t("mv_adj", "Điều chỉnh", "Adjustment", "تسوية")
_t("mv_open", "Tồn đầu", "Opening stock", "رصيد افتتاحي")
_t("h_date", "Ngày", "Date", "التاريخ")
_t("h_move", "Giao dịch", "Movement", "الحركة")
_t("h_change", "Tồn trước → sau", "Stock before → after", "المخزون قبل ← بعد")
_t("h_price", "Đơn giá", "Unit price", "سعر الوحدة")
_t("h_reason", "Lý do", "Reason", "السبب")
_t("mv_info", "Tồn hiện tại: {0} {1} • Vị trí {2} • Nhập {3} • Bán {4}{5}",
   "Current stock: {0} {1} • Location {2} • Buy {3} • Sell {4}{5}",
   "المخزون الحالي: {0} {1} • الموقع {2} • الشراء {3} • البيع {4}{5}")
_t("mv_low", "   ⚠ tối thiểu {0}", "   ⚠ minimum {0}", "   ⚠ الحد الأدنى {0}")
_t("err_pick_item", "Hãy chọn hàng trong danh sách.", "Pick an item from the list.", "اختر صنفًا من القائمة.")
_t("err_qty", "Số lượng phải lớn hơn 0.", "Quantity must be greater than zero.", "يجب أن تكون الكمية أكبر من صفر.")
_t("err_not_enough", "Chỉ còn {0} {1} trong kho.", "Only {0} {1} in stock.", "المتوفر في المخزون {0} {1} فقط.")
_t("err_nochange", "Số kiểm đếm bằng tồn hiện tại.", "Counted quantity equals current stock.",
   "الكمية المعدودة تساوي المخزون الحالي.")
_t("mv_done", "{0}: {1} {2} → {3} {4}{5}", "{0}: {1} {2} → {3} {4}{5}", "{0}: {1} {2} ← {3} {4}{5}")
_t("mv_warn", "  ⚠ dưới mức tối thiểu!", "  ⚠ below minimum stock!", "  ⚠ أقل من الحد الأدنى!")
