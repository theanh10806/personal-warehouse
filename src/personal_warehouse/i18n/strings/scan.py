"""UI texts (vi / en / ar) for: scan."""

from personal_warehouse.i18n.core import add as _t


_t("scan_title", "Quét mã QR / Mã vạch", "Scan QR / Barcode", "مسح QR / الباركود")
_t("scan_sub", "Bấm vào ô rồi quét bằng máy quét USB / Bluetooth — hoặc dùng camera, hoặc mở ảnh. Dữ liệu hiển thị là THỜI GIAN THỰC.",
   "Click the box and scan with a USB / Bluetooth scanner — or use the camera, or open a photo. Data shown is LIVE.",
   "اضغط على الحقل وامسح بقارئ USB / بلوتوث — أو استخدم الكاميرا أو افتح صورة. البيانات المعروضة حيّة.")
_t("scan_mode", "Chế độ quét", "Scan mode", "وضع المسح")
_t("scan_lookup", "Tra cứu", "Look up", "بحث")
_t("scan_qtyper", "SL mỗi lần quét", "Qty per scan", "الكمية لكل مسح")
_t("scan_mode_hint", "Chế độ Nhập / Xuất: mỗi lần quét tự cộng / trừ kho — rất nhanh khi nhận và xuất hàng.",
   "Stock In / Out mode: every scan adds / removes stock automatically — fast for receiving and shipping.",
   "وضع إدخال / إخراج: كل مسح يضيف / يخصم من المخزون تلقائيًا — سريع للاستلام والشحن.")
_t("scan_camera", "📷 Camera", "📷 Camera", "📷 الكاميرا")
_t("scan_image", "Mở ảnh…", "Open image…", "فتح صورة…")
_t("scan_lookup_btn", "Tra cứu", "Look up", "بحث")
_t("scan_wait", "Đang chờ quét…", "Waiting for a scan…", "بانتظار المسح…")
_t("scan_not_wh", "Không phải mã của kho này", "Not a warehouse code", "ليس رمز مستودع")
_t("scan_content", "Nội dung", "Content", "المحتوى")
_t("scan_notfound", "{0}: không có trong CSDL", "{0}: not found in this database", "{0}: غير موجود في قاعدة البيانات")
_t("scan_scanned", "Đã quét {0}", "Scanned {0}", "تم مسح {0}")
_t("scan_flash_in", "＋{0} → tồn {1} {2}", "＋{0} → stock {1} {2}", "＋{0} ← المخزون {1} {2}")
_t("scan_flash_out", "－{0} → tồn {1} {2}", "－{0} → stock {1} {2}", "－{0} ← المخزون {1} {2}")
_t("scan_flash_err", "⚠ {0}", "⚠ {0}", "⚠ {0}")
_t("scan_archived_no", "Hàng đã lưu trữ — không thể nhập / xuất.", "Archived item — cannot move stock.",
   "صنف مؤرشف — لا يمكن تحريك المخزون.")
_t("st_archived", "(ĐÃ LƯU TRỮ)", "(ARCHIVED)", "(مؤرشف)")
_t("st_out", "⚠ HẾT HÀNG", "⚠ OUT OF STOCK", "⚠ نافد")
_t("st_low", "⚠ SẮP HẾT", "⚠ LOW STOCK", "⚠ مخزون منخفض")
_t("sc_stock", "Tồn hiện tại", "In stock now", "المخزون الآن")
_t("sc_added", "Ngày thêm", "Date added", "تاريخ الإضافة")
_t("cam_unavail_title", "Không dùng được camera", "Camera scan unavailable", "مسح الكاميرا غير متاح")
_t("cam_unavail", "Cài OpenCV:\n\npip install opencv-python\n\n(Máy quét USB hoặc 'Mở ảnh…' không cần thư viện này.)",
   "Install OpenCV:\n\npip install opencv-python\n\n(A USB scanner or 'Open image…' work without it.)",
   "ثبّت OpenCV:\n\npip install opencv-python\n\n(قارئ USB أو 'فتح صورة…' لا يحتاجانه.)")
_t("cam_open_err", "Không mở được camera. Kiểm tra xem ứng dụng khác có đang dùng không.",
   "Cannot open the camera. Check that no other app is using it.",
   "تعذر فتح الكاميرا. تأكد أن تطبيقًا آخر لا يستخدمها.")
_t("img_read_err", "Không đọc được file ảnh.", "Cannot read that image file.", "تعذرت قراءة ملف الصورة.")
_t("img_open_title", "Mở ảnh chụp mã QR / mã vạch", "Open a photo / screenshot of a code", "افتح صورة لرمز QR / باركود")
_t("no_qr", "Không đọc được mã", "No code found", "لم يتم العثور على رمز")
_t("no_qr_msg", "Không đọc được mã nào từ ảnh này.\nHãy thử ảnh nét và gần hơn.",
   "No code could be read from that image.\nTry a sharper, closer photo.",
   "تعذرت قراءة أي رمز من هذه الصورة.\nجرّب صورة أوضح وأقرب.")
