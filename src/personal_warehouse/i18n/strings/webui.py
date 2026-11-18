"""UI texts (vi / en / ar) used only by the web interface."""

from personal_warehouse.i18n.core import add as _t


_t("ui_ok", "Đồng ý", "OK", "موافق")
_t("ui_confirm", "Xác nhận", "Confirm", "تأكيد")
_t("ui_close", "Đóng", "Close", "إغلاق")
_t("ui_error", "Lỗi", "Error", "خطأ")
_t("ui_theme", "Đổi giao diện sáng / tối", "Toggle light / dark", "تبديل الوضع الفاتح / الداكن")
_t("ui_menu", "Thu gọn / mở rộng menu", "Collapse / expand menu", "طي / توسيع القائمة")
_t("ui_nodata", "Chưa có dữ liệu.", "No data yet.", "لا توجد بيانات بعد.")
_t("ui_no_match", "Không có mặt hàng phù hợp.", "No matching items.", "لا توجد أصناف مطابقة.")
_t("ui_clear", "Xóa", "Clear", "مسح")
_t("ui_items_unit", "mặt hàng", "items", "أصناف")
_t("ui_units_unit", "đơn vị", "units", "وحدات")
_t("dash_health", "Sức khỏe tồn kho", "Stock health", "صحة المخزون")
_t("dash_health_sub", "Tỷ lệ mặt hàng còn đủ so với mức tối thiểu.", "Share of items at or above their minimum.",
   "نسبة الأصناف التي بلغت حدها الأدنى أو تجاوزته.")
_t("health_ok", "Đủ tồn", "Enough", "كافٍ")
_t("health_low", "Thấp", "Low", "منخفض")
_t("health_out", "Hết", "Out", "نافد")
_t("health_center", "đủ tồn", "in stock", "كافٍ")
_t("dash_remind", "Nhắc: {0} sản phẩm cần nhập thêm!", "Reminder: {0} item(s) need restocking!",
   "تذكير: {0} صنف يحتاج إلى تعبئة!")
_t("dash_remind_sub", "Nhập lại trước khi hết hàng: {0}.", "Restock before you run out: {0}.",
   "أعد التعبئة قبل نفاد المخزون: {0}.")
_t("dash_all_ok", "Mọi thứ ổn!", "Everything is in order!", "كل شيء على ما يرام!")
_t("dash_all_ok_sub", "Không có mặt hàng nào sắp hết.", "Nothing is running low.", "لا يوجد ما ينفد.")
_t("dash_view_low", "Xem hàng sắp hết", "View low stock", "عرض المنخفض")
_t("sel_rows", "Đã chọn {0}", "{0} selected", "تم تحديد {0}")
_t("mv_qty_hint", "Số lượng hiện tại", "Current stock", "المخزون الحالي")
_t("lbl_sel_none", "Không có dòng nào được chọn: in nhãn cho tất cả {0} mặt hàng đang hiển thị?",
   "No rows selected: print labels for all {0} items shown?",
   "لم يتم تحديد صفوف: طباعة ملصقات لجميع الأصناف الظاهرة ({0})؟")
_t("ui_pick_file", "Chọn tệp…", "Choose file…", "اختر ملفًا…")
_t("ui_dev_only", "Chức năng này cần chạy trong cửa sổ ứng dụng.", "This needs the desktop window.",
   "تحتاج هذه الميزة إلى نافذة التطبيق.")
_t("ui_show_more", "Hiện thêm {0} dòng", "Show {0} more rows", "عرض {0} صفوف إضافية")
_t("btn_delete", "Xóa vĩnh viễn", "Delete permanently", "حذف نهائي")
_t("del_title", "Xóa vĩnh viễn", "Delete permanently", "حذف نهائي")
_t("del_confirm",
   "Xóa vĩnh viễn {0} mặt hàng, kèm {1} dòng lịch sử nhập/xuất của chúng?\n\nKhông thể hoàn tác. Một bản sao lưu toàn bộ dữ liệu sẽ được tạo trước khi xóa.",
   "Permanently delete {0} item(s) and their {1} stock-movement record(s)?\n\nThis cannot be undone. A full backup of your data is made first.",
   "حذف {0} صنف نهائيًا مع {1} من سجلات الحركة الخاصة بها؟\n\nلا يمكن التراجع. سيتم إنشاء نسخة احتياطية كاملة قبل الحذف.")
_t("del_done", "Đã xóa {0} mặt hàng. Bản sao lưu trước khi xóa: {1}", "Deleted {0} item(s). Backup made before deleting: {1}",
   "تم حذف {0} صنف. النسخة الاحتياطية قبل الحذف: {1}")
_t("del_pick", "Hãy tick chọn hoặc bấm vào ít nhất một dòng để xóa.", "Tick or click at least one row to delete.",
   "حدد صفًا واحدًا على الأقل للحذف.")
_t("loc_legacy", "NGOÀI SƠ ĐỒ MỚI", "OUTSIDE THE CURRENT MAP", "خارج الخريطة الحالية")
_t("loc_legacy_hint", "Các vị trí cũ không còn trong sơ đồ (A–C × 1–8). Mở hàng để chuyển sang vị trí mới.",
   "Old locations that are not on the map any more (A–C × 1–8). Open the item to move it to a new place.",
   "مواقع قديمة لم تعد في الخريطة (A–C × 1–8). افتح الصنف لنقله إلى مكان جديد.")
