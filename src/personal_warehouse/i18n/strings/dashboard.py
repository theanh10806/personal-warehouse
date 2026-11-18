"""UI texts (vi / en / ar) for: dashboard."""

from personal_warehouse.i18n.core import add as _t


_t("dash_title", "Tổng quan kho", "Warehouse overview", "نظرة عامة على المستودع")
_t("dash_sub", "Tồn kho, giá trị và những việc cần chú ý.", "Stock, value and what needs attention.",
   "المخزون والقيمة وما يحتاج إلى انتباه.")
_t("m_items", "Số mặt hàng", "Item records", "عدد الأصناف")
_t("m_units", "Tổng số lượng tồn", "Units in stock", "الوحدات في المخزون")
_t("m_value", "Giá trị nhập (vốn)", "Purchase value", "قيمة الشراء")
_t("m_profit", "Lợi nhuận gộp dự kiến", "Potential gross profit", "الربح الإجمالي المتوقع")
_t("m_alerts", "Sắp hết / hết hàng", "Low / out of stock", "منخفض / نافد")
<<<<<<< HEAD
_t("card_sections", "Tồn kho theo khu", "Stock by section", "المخزون حسب القسم")
_t("card_alerts", "Cần chú ý", "Needs attention", "يحتاج إلى انتباه")
_t("card_recent", "Hoạt động gần đây", "Recent activity", "النشاط الأخير")
=======
_t("card_sections", "TỒN KHO THEO KHU", "STOCK BY SECTION", "المخزون حسب القسم")
_t("card_alerts", "CẦN CHÚ Ý", "NEEDS ATTENTION", "يحتاج إلى انتباه")
_t("card_recent", "HOẠT ĐỘNG GẦN ĐÂY", "RECENT ACTIVITY", "النشاط الأخير")
>>>>>>> c8a133662267867832f0d0679ec8832dee7dfdbb
_t("qa_add", "＋ Thêm hàng mới", "＋ Add a new item", "＋ إضافة صنف جديد")
_t("qa_inv", "Xem kho hàng", "View inventory", "عرض المخزون")
_t("qa_move", "Nhập / xuất kho", "Record movement", "تسجيل حركة")
_t("qa_scan", "Quét mã", "Scan a code", "مسح رمز")
_t("qa_labels", "In tem mã", "Print labels", "طباعة الملصقات")
_t("qa_export", "Xuất Excel / CSV", "Export Excel / CSV", "تصدير Excel / CSV")
_t("qa_backup", "Sao lưu", "Back up", "نسخ احتياطي")
_t("col_item", "Mặt hàng", "Item", "الصنف")
_t("col_loc", "Vị trí", "Location", "الموقع")
_t("col_qty", "SL", "Qty", "الكمية")
_t("col_min", "Tối thiểu", "Min", "الحد الأدنى")
_t("col_time", "Thời gian", "Time", "الوقت")
_t("col_type", "Loại", "Type", "النوع")
<<<<<<< HEAD

# --- redesigned dashboard (KPI cards, trend chart, smart insights) ---
_t("card_trend", "Nhập / xuất 14 ngày qua", "Stock in / out, last 14 days", "الإدخال والإخراج خلال آخر 14 يومًا")
_t("legend_in", "Nhập", "In", "إدخال")
_t("legend_out", "Xuất", "Out", "إخراج")
_t("trend_empty", "Chưa có nhập / xuất nào trong 14 ngày qua.", "No stock in / out in the last 14 days.",
   "لا توجد حركات إدخال أو إخراج خلال آخر 14 يومًا.")
_t("card_insights", "Gợi ý thông minh", "Smart insights", "رؤى ذكية")
_t("ins_sub", "Tự tính từ dữ liệu kho của bạn, không cần mạng.", "Worked out from your own data, no internet needed.",
   "تُحسب من بيانات مخزونك دون حاجة إلى الإنترنت.")
_t("ins_ok", "Kho đang ổn: không có mặt hàng nào sắp hết.", "All good: nothing is running low.",
   "كل شيء بخير: لا يوجد صنف يوشك على النفاد.")
_t("ins_out", "{0} mặt hàng đã hết: {1}", "{0} item(s) out of stock: {1}", "{0} صنف نافد: {1}")
_t("ins_low", "{0} mặt hàng sắp hết, nên nhập thêm: {1}", "{0} item(s) running low, consider restocking: {1}",
   "{0} صنف منخفض، يُنصح بإعادة التوريد: {1}")
_t("ins_top", "Xuất nhiều nhất 30 ngày qua: {0} ({1})", "Top mover in the last 30 days: {0} ({1})",
   "الأكثر إخراجًا خلال آخر 30 يومًا: {0} ({1})")
_t("ins_idle", "{0} mặt hàng không có nhập / xuất suốt 60 ngày, nên cân nhắc xử lý.",
   "{0} item(s) had no movement for 60 days, worth a look.", "{0} صنف بلا أي حركة منذ 60 يومًا، يستحق المراجعة.")
_t("kpi_sections", "{0}/{1} khu đang có hàng", "{0}/{1} sections in use", "{0}/{1} أقسام مستخدمة")
_t("kpi_units_sub", "đơn vị đang nằm trong kho", "units on the shelves", "وحدات في المخزن")
_t("kpi_net7", "{0} · 7 ngày", "{0} · 7 days", "{0} · 7 أيام")
_t("kpi_value_sub", "Lãi gộp dự kiến {0}", "Potential gross profit {0}", "الربح الإجمالي المتوقع {0}")
_t("kpi_alert_sub", "{0} hết hàng · {1} sắp hết", "{0} out · {1} low", "{0} نافد · {1} منخفض")
_t("kpi_attention", "Cần nhập", "Restock", "إعادة توريد")
_t("dash_view_all", "Xem tất cả", "View all", "عرض الكل")
_t("top_search", "Tìm hàng theo tên, mã, vị trí… rồi nhấn Enter", "Search items by name, code or location, then press Enter",
   "ابحث عن صنف بالاسم أو الرمز أو الموقع ثم اضغط Enter")

=======
>>>>>>> c8a133662267867832f0d0679ec8832dee7dfdbb
