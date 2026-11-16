"""UI texts (vi / en / ar) for: settings."""

from personal_warehouse.i18n.core import add as _t


_t("set_title", "Cài đặt", "Settings", "الإعدادات")
_t("set_sub", "Ngôn ngữ, giao diện và công cụ dữ liệu.", "Language, appearance and data tools.",
   "اللغة والمظهر وأدوات البيانات.")
_t("set_lang", "Ngôn ngữ", "Language", "اللغة")
_t("set_theme", "Giao diện", "Appearance", "المظهر")
_t("theme_light", "Sáng", "Light", "فاتح")
_t("theme_dark", "Tối", "Dark", "داكن")
_t("set_rtl", "Tiếng Ả Rập hiển thị từ phải sang trái.", "Arabic is shown right-to-left.", "تُعرض العربية من اليمين إلى اليسار.")
_t("set_translate", "Dịch tên hàng sang tiếng Ả Rập", "Translate item names to Arabic", "ترجمة أسماء الأصناف إلى العربية")
_t("set_translate_hint", "Dùng dịch vụ dịch máy trực tuyến (cần Internet), chỉ với hàng chưa có tên tiếng Ả Rập. Nên kiểm tra lại kết quả.",
   "Uses an online machine-translation service (Internet needed), only for items without an Arabic name. Please review the results.",
   "يستخدم خدمة ترجمة آلية عبر الإنترنت، فقط للأصناف بلا اسم عربي. يُنصح بمراجعة النتائج.")
_t("bt_nothing", "Tất cả hàng đã có tên tiếng Ả Rập.", "All items already have an Arabic name.", "كل الأصناف لها اسم عربي بالفعل.")
_t("bt_confirm", "Dịch {0} tên hàng sang tiếng Ả Rập bằng dịch vụ trực tuyến?\nCần Internet; tên hàng sẽ được gửi tới dịch vụ dịch.",
   "Translate {0} item names to Arabic with an online service?\nInternet is needed; the names are sent to the translation service.",
   "ترجمة {0} اسم صنف إلى العربية عبر خدمة إنترنت؟\nيلزم الإنترنت؛ ستُرسل الأسماء إلى خدمة الترجمة.")
_t("bt_progress", "Đang dịch… {0}/{1}", "Translating… {0}/{1}", "جارٍ الترجمة… {0}/{1}")
_t("bt_done", "Đã dịch {0} tên hàng ({1} lỗi).", "Translated {0} names ({1} failed).", "تمت ترجمة {0} اسم ({1} فشل).")
_t("bt_offline", "Không kết nối được dịch vụ dịch. Kiểm tra Internet.", "Cannot reach the translation service. Check the Internet.",
   "تعذر الوصول إلى خدمة الترجمة. تحقق من الإنترنت.")
_t("upd_title", "Cập nhật", "Updates", "التحديثات")
_t("upd_version", "Phiên bản hiện tại: {0}", "Current version: {0}", "الإصدار الحالي: {0}")
_t("upd_check", "Kiểm tra cập nhật", "Check for updates", "التحقق من التحديثات")
_t("upd_auto", "Tự kiểm tra khi mở ứng dụng", "Check automatically when the app starts",
   "التحقق تلقائيًا عند تشغيل التطبيق")
_t("upd_available", "Có phiên bản mới {0} (bạn đang dùng {1}).\n\n{2}\n\nMở trang tải về?",
   "Version {0} is available (you have {1}).\n\n{2}\n\nOpen the download page?",
   "الإصدار {0} متاح (لديك {1}).\n\n{2}\n\nفتح صفحة التنزيل؟")
_t("upd_none", "Bạn đang dùng phiên bản mới nhất ({0}).", "You are up to date ({0}).",
   "أنت تستخدم أحدث إصدار ({0}).")
_t("upd_fail", "Không kiểm tra được cập nhật (cần Internet).\n{0}", "Could not check for updates (Internet needed).\n{0}",
   "تعذر التحقق من التحديثات (يلزم الإنترنت).\n{0}")
_t("upd_disabled", "Chưa cấu hình kho GitHub nên chưa kiểm tra cập nhật được.",
   "No GitHub repository is configured, so update checks are off.",
   "لم يتم إعداد مستودع GitHub، لذا فحص التحديثات متوقف.")
_t("upd_status", "Có phiên bản mới: {0}", "New version available: {0}", "إصدار جديد متاح: {0}")
_t("data_info", "Thư mục dữ liệu:\n{0}\nTự sao lưu: {1}/ (mỗi ngày, giữ {2} bản)",
   "Data folder:\n{0}\nAuto-backup: {1}/ (daily, last {2})", "مجلد البيانات:\n{0}\nنسخ تلقائي: {1}/ (يوميًا، آخر {2})")
