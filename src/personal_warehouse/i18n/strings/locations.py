"""UI texts (vi / en / ar) for: locations."""

from personal_warehouse.i18n.core import add as _t


_t("map_title", "Sơ đồ kho", "Storage map", "خريطة التخزين")
_t("map_sub", "3 khu × 8 ngăn = 24 vị trí cố định (A1…C8). Màu càng đậm = càng nhiều mặt hàng; bấm một ô để xem hàng bên trong.",
   "3 sections × 8 parts = 24 fixed locations (A1…C8). Darker = more items; click a cell to see what is inside.",
   "3 أقسام × 8 أجزاء = 24 موقعًا ثابتًا (A1…C8). كلما كان اللون أغمق زادت الأصناف؛ اضغط على خلية لعرض محتواها.")
_t("section_big", "KHU {0}", "SECTION {0}", "القسم {0}")
_t("loc_cell", "{0}\n{1} mặt hàng • {2} sp", "{0}\n{1} items • {2} units", "{0}\n{1} صنف • {2} وحدة")
_t("map_view_flat", "Mặt bằng", "Floor plan", "المخطط")
_t("map_view_3d", "3D", "3D", "ثلاثي الأبعاد")
_t("map_stat_used", "Vị trí có hàng", "Locations in use", "مواقع مستخدمة")
_t("map_stat_free", "Vị trí trống", "Empty locations", "مواقع فارغة")
_t("map_stat_items", "Mặt hàng", "Items", "الأصناف")
_t("map_stat_low", "Sắp hết / hết", "Low / out", "منخفض / نافد")
_t("map_zone_stat", "{0}/{1} vị trí có hàng", "{0}/{1} in use", "{0}/{1} مستخدم")
_t("map_legend_empty", "Trống", "Empty", "فارغ")
_t("map_legend_more", "Nhiều hàng hơn", "More items", "أصناف أكثر")
_t("map_legend_low", "Có hàng sắp hết", "Has low stock", "يحتوي مخزونًا منخفضًا")
_t("map_pick", "Chọn một ô trên sơ đồ để xem hàng trong vị trí đó.", "Pick a cell on the map to see its items.",
   "اختر خلية على الخريطة لعرض أصنافها.")
_t("map_empty_cell", "Vị trí này đang trống.", "This location is empty.", "هذا الموقع فارغ.")
_t("map_open", "Mở trong Kho hàng", "Open in Inventory", "فتح في المخزون")
_t("map_more", "… và {0} mặt hàng nữa", "… and {0} more", "… و{0} أخرى")
_t("map_3d_hint", "Kéo để xoay · chiều cao cột = số mặt hàng", "Drag to rotate · column height = number of items",
   "اسحب للتدوير · ارتفاع العمود = عدد الأصناف")
_t("map_3d_reset", "Góc nhìn mặc định", "Default angle", "الزاوية الافتراضية")
_t("map_3d_top", "Nhìn từ trên", "Top view", "من الأعلى")
_t("map_search", "Tìm hàng trên sơ đồ", "Find items on the map", "البحث عن الأصناف على الخريطة")
_t("map_search_hint", "Tên hàng, mã hàng, mã vạch hoặc A1…", "Name, item code, barcode or A1…", "الاسم أو رمز الصنف أو الباركود أو A1…")
_t("map_filter", "Hiển thị nổi bật", "Highlight", "تمييز")
_t("map_filter_all", "Tất cả vị trí", "All locations", "جميع المواقع")
_t("map_filter_low", "Có hàng sắp hết / hết", "Low or out of stock", "مخزون منخفض أو نافد")
_t("map_filter_empty", "Vị trí chưa có mặt hàng", "Locations without items", "مواقع بدون أصناف")
_t("map_match_count", "{0} vị trí phù hợp", "{0} matching locations", "{0} مواقع مطابقة")
_t("map_alert_count", "{0} cảnh báo", "{0} alerts", "{0} تنبيهات")
_t("map_refresh", "Làm mới", "Refresh", "تحديث")
_t("map_add_here", "Thêm hàng tại đây", "Add item here", "إضافة صنف هنا")
_t("map_details", "Chi tiết vị trí", "Location details", "تفاصيل الموقع")
_t("map_load_error", "Không tải được dữ liệu vị trí.", "Could not load location data.", "تعذر تحميل بيانات الموقع.")
_t("map_warning_count", "{0} sắp hết", "{0} low", "{0} منخفض")
_t("map_out_count", "{0} hết", "{0} out", "{0} نافد")
_t("map_filter_warning", "Chỉ hàng sắp hết", "Low stock only", "المخزون المنخفض فقط")
_t("map_filter_out", "Chỉ hàng hết", "Out of stock only", "المخزون النافد فقط")
