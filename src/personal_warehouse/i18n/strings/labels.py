"""UI texts (vi / en / ar) for: labels."""

from personal_warehouse.i18n.core import add as _t


_t("lbl_dialog", "In tem — {0} mặt hàng", "{0} item(s) → labels", "{0} صنف ← ملصقات")
_t("lbl_layout", "Bố cục", "Layout", "التخطيط")
_t("lbl_size", "Kích thước tem", "Label size", "حجم الملصق")
_t("lbl_kind", "Nội dung tem", "Label content", "محتوى الملصق")
_t("lbl_copies", "Số bản mỗi hàng", "Copies per item", "عدد النسخ لكل صنف")
_t("layout_a4", "Tờ A4 (cắt tem)", "A4 sheet (cut out labels)", "ورقة A4 (قص الملصقات)")
_t("layout_printer", "Máy in tem (1 tem / trang)", "Label printer (1 label per page)", "طابعة ملصقات (ملصق لكل صفحة)")
_t("kind_qr", "Mã QR", "QR code", "رمز QR")
_t("kind_barcode", "Mã vạch Code 128", "Barcode (Code 128)", "باركود (Code 128)")
_t("kind_both", "QR + Mã vạch", "QR + Barcode", "QR + باركود")
_t("lbl_full", "QR chứa đầy đủ thông tin (QR dày hơn, dữ liệu là lúc in)",
   "Full info inside the QR (denser QR, data as of print time)", "معلومات كاملة داخل QR (أكثر كثافة، البيانات وقت الطباعة)")
_t("lbl_prices", "Kèm giá nhập / giá bán trong QR", "Include purchase / selling price in the QR",
   "تضمين سعر الشراء / البيع في QR")
_t("lbl_hint", "Trang in mở trong trình duyệt (hộp thoại in tự hiện). Mặc định QR chỉ chứa mã hàng → quét nhanh và luôn ra dữ liệu mới nhất.",
   "The print page opens in your browser (print dialog appears automatically). By default the QR holds only the item code → scans fast and always shows live data.",
   "تُفتح صفحة الطباعة في المتصفح (يظهر مربع الطباعة تلقائيًا). افتراضيًا يحمل QR رمز الصنف فقط ← مسح أسرع وبيانات حيّة دائمًا.")
_t("lbl_open", "Mở trang in", "Open print page", "فتح صفحة الطباعة")
_t("lbl_loc", "Vị trí", "Loc", "الموقع")
_t("lbl_nothing_t", "Không có gì để in", "Nothing to print", "لا شيء للطباعة")
_t("lbl_nothing", "Danh sách kho đang trống.", "The inventory list is empty.", "قائمة المخزون فارغة.")
_t("lbl_all", "Chưa chọn dòng nào.\nIn tem cho tất cả {0} mặt hàng đang hiển thị?",
   "No rows selected.\nPrint labels for all {0} items shown?", "لم يتم تحديد صفوف.\nطباعة ملصقات لكل الأصناف المعروضة ({0})؟")
_t("lbl_title_msg", "In tem", "Print labels", "طباعة الملصقات")
_t("qr_unavail_title", "Không in được QR", "QR printing unavailable", "طباعة QR غير متاحة")
_t("qr_unavail", "Cài thư viện QR:\n\npip install \"qrcode[pil]\"\n\n(Tem Mã vạch không cần thư viện này.)",
   "Install the QR library:\n\npip install \"qrcode[pil]\"\n\n(Barcode-only labels work without it.)",
   "ثبّت مكتبة QR:\n\npip install \"qrcode[pil]\"\n\n(ملصقات الباركود لا تحتاجها.)")
_t("lbl_many", "Sẽ tạo {0} tem. Tiếp tục?", "This creates {0} labels. Continue?", "سيتم إنشاء {0} ملصق. متابعة؟")
_t("lbl_opened", "Đã mở trang in ({0} tem). Lưu tại {1}/", "Label page opened ({0} labels). Saved in {1}/",
   "تم فتح صفحة الطباعة ({0} ملصق). محفوظة في {1}/")
_t("lbl_err", "Lỗi in tem", "Label error", "خطأ في الملصقات")
_t("lbl_save_first", "Hãy lưu hàng trước rồi mới in tem.", "Save the item first, then print its label.",
   "احفظ الصنف أولاً ثم اطبع ملصقه.")
