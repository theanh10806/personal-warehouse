"""UI texts (vi / en / ar) for: inventory."""

from personal_warehouse.i18n.core import add as _t


_t("inv_title", "Kho hàng", "Inventory", "المخزون")
_t("lbl_search", "Tìm kiếm:", "Search:", "بحث:")
_t("all_locations", "Tất cả vị trí", "All locations", "كل المواقع")
_t("section_n", "Khu {0}", "Section {0}", "القسم {0}")
_t("all_conditions", "Mọi tình trạng", "All conditions", "كل الحالات")
_t("low_only", "Chỉ sắp hết / hết", "Low / out only", "المنخفض / النافد فقط")
_t("show_archived", "Hiện hàng đã lưu trữ", "Show archived", "إظهار المؤرشف")
_t("h_code", "Mã hàng", "Item ID", "رقم الصنف")
_t("h_name", "Tên hàng", "Item name", "اسم الصنف")
_t("h_category", "Danh mục", "Category", "الفئة")
_t("h_engine", "Động cơ / Ứng dụng", "Engine / Application", "المحرك / الاستخدام")
_t("h_location", "Vị trí", "Location", "الموقع")
_t("h_condition", "Tình trạng", "Condition", "الحالة")
_t("h_qty", "SL", "Qty", "الكمية")
_t("h_buy", "Giá nhập", "Buy (USD)", "الشراء (USD)")
_t("h_sell", "Giá bán", "Sell (USD)", "البيع (USD)")
_t("inv_summary", "{0} mục • {1} sản phẩm • giá trị nhập {2}   (cam = sắp hết, đỏ = hết hàng)",
   "{0} records • {1} units • purchase value {2}   (orange = low, red = out of stock)",
   "{0} سجل • {1} وحدة • قيمة الشراء {2}   (برتقالي = منخفض، أحمر = نافد)")
_t("archive_title", "Lưu trữ hàng", "Archive item", "أرشفة الصنف")
_t("archive_confirm", "Lưu trữ '{0}'?\nHàng sẽ ẩn khỏi danh sách nhưng vẫn giữ lịch sử. Có thể khôi phục bất cứ lúc nào.",
   "Archive '{0}'?\nIt is hidden from lists but its stock history is kept. You can restore it any time.",
   "هل تريد أرشفة '{0}'؟\nسيُخفى من القوائم مع الاحتفاظ بسجل الحركة. يمكنك استعادته في أي وقت.")
_t("archived", "Đã lưu trữ", "Archived", "تمت الأرشفة")
_t("restored", "Đã khôi phục", "Restored", "تمت الاستعادة")
