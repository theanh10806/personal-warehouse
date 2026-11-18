"""UI texts (vi / en / ar) for: item_form."""

from personal_warehouse.i18n.core import add as _t


_t("form_new", "Hàng mới", "New item", "صنف جديد")
_t("form_edit", "Sửa {0}", "Edit {0}", "تعديل {0}")
_t("f_name", "Tên hàng *", "Item name *", "اسم الصنف *")
_t("f_name_ar", "Tên tiếng Ả Rập", "Arabic name", "الاسم بالعربية")
_t("f_category", "Danh mục", "Category", "الفئة")
_t("f_description", "Mô tả", "Description", "الوصف")
_t("f_engine", "Động cơ / Ứng dụng", "Engine / Application", "المحرك / الاستخدام")
_t("f_barcode", "Mã vạch nhà SX / SKU (tùy chọn)", "Manufacturer barcode / SKU (optional)",
   "باركود المصنّع / SKU (اختياري)")
_t("f_section", "Khu", "Section", "القسم")
_t("f_part", "Ngăn", "Part", "الجزء")
_t("f_condition", "Tình trạng", "Condition", "الحالة")
_t("f_unit", "Đơn vị", "Unit", "الوحدة")
_t("f_qty", "Số lượng (tồn đầu)", "Quantity (opening stock)", "الكمية (رصيد افتتاحي)")
_t("f_min", "Tồn tối thiểu (cảnh báo)", "Minimum stock (alert)", "الحد الأدنى للمخزون (تنبيه)")
_t("f_buy", "Giá nhập (USD)", "Purchase price (USD)", "سعر الشراء (USD)")
_t("f_sell", "Giá bán (USD)", "Selling price (USD)", "سعر البيع (USD)")
_t("f_supplier", "Nhà cung cấp", "Supplier", "المورّد")
_t("f_notes", "Ghi chú", "Notes", "ملاحظات")
_t("loc_preview", "Vị trí lưu: {0}   (mã hàng tự động tạo khi lưu)",
   "Storage location: {0}   (item code is assigned automatically on save)",
   "موقع التخزين: {0}   (يُنشأ رمز الصنف تلقائيًا عند الحفظ)")
_t("loc_preview_edit", "   •   Số lượng chỉ thay đổi ở 'Nhập / Xuất kho'.",
   "   •   Quantity is changed in 'Stock In / Out'.", "   •   تتغير الكمية من 'إدخال / إخراج' فقط.")
_t("photo_title", "ẢNH HÀNG", "ITEM PHOTO", "صورة الصنف")
_t("choose_photo", "Chọn ảnh…", "Choose photo…", "اختر صورة…")
_t("remove_photo", "Xóa ảnh", "Remove photo", "إزالة الصورة")
_t("choose_photo_title", "Chọn ảnh hàng", "Choose item photo", "اختر صورة الصنف")
_t("pillow_tip", "Mẹo: pip install pillow\nđể xem ảnh jpg/bmp", "Tip: pip install pillow\nfor jpg/bmp preview",
   "نصيحة: pip install pillow\nلمعاينة صور jpg/bmp")
_t("bc_preview", "MÃ VẠCH (CODE 128)", "BARCODE (CODE 128)", "الباركود (CODE 128)")
_t("bc_none", "Lưu hàng để tạo mã vạch", "Save the item to get a barcode", "احفظ الصنف للحصول على باركود")
_t("err_name_title", "Thiếu tên hàng", "Missing item name", "اسم الصنف مفقود")
_t("err_name", "Vui lòng nhập tên hàng.", "Please enter an item name.", "الرجاء إدخال اسم الصنف.")
_t("price_below_title", "Giá bán thấp hơn giá nhập", "Selling price below cost", "سعر البيع أقل من التكلفة")
_t("price_below", "Giá bán thấp hơn giá nhập. Vẫn lưu?", "Selling price is lower than purchase price. Save anyway?",
   "سعر البيع أقل من سعر الشراء. هل تريد الحفظ على أي حال؟")
_t("dup_title", "Có thể bị trùng", "Possible duplicate", "تكرار محتمل")
_t("dup_msg", "{0} có cùng tên ở vị trí này. Vẫn tạo bản ghi mới?\n(Dùng Nhập kho để cộng thêm số lượng.)",
   "{0} has the same name in this location. Create another record anyway?\n(Use Stock In to add quantity.)",
   "{0} يحمل الاسم نفسه في هذا الموقع. هل تريد إنشاء سجل آخر؟\n(استخدم الإدخال لإضافة كمية.)")
_t("barcode_dup", "Mã vạch '{0}' đã được dùng cho {1}.", "Barcode '{0}' is already used by {1}.",
   "الباركود '{0}' مستخدم بالفعل للصنف {1}.")
_t("photo_err", "Lỗi ảnh", "Photo error", "خطأ في الصورة")
_t("tr_need_name", "Hãy nhập tên hàng trước.", "Enter the item name first.", "أدخل اسم الصنف أولاً.")
_t("tr_fail", "Không dịch được (cần Internet).\n{0}", "Could not translate (Internet needed).\n{0}",
   "تعذرت الترجمة (يلزم الإنترنت).\n{0}")
_t("tr_title", "Dịch tên hàng", "Translate name", "ترجمة الاسم")
