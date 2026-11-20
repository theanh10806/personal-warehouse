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
_t("upd_new_body", "Có phiên bản mới {0} (bạn đang dùng {1}).\n\n{2}", "Version {0} is available (you have {1}).\n\n{2}",
   "الإصدار {0} متاح (لديك {1}).\n\n{2}")
_t("upd_btn_now", "Cập nhật ngay", "Update now", "حدّث الآن")
_t("upd_btn_later", "Để sau", "Later", "لاحقًا")
_t("upd_btn_page", "Mở trang tải về", "Open download page", "فتح صفحة التنزيل")
_t("upd_dl_title", "Đang tải bản cập nhật", "Downloading the update", "جارٍ تنزيل التحديث")
_t("upd_dl_progress", "Đã tải {0} / {1} MB", "Downloaded {0} / {1} MB", "تم تنزيل {0} / {1} ميجابايت")
_t("upd_dl_progress_unknown", "Đã tải {0} MB", "Downloaded {0} MB", "تم تنزيل {0} ميجابايت")
_t("upd_dl_wait", "Đang kết nối…", "Connecting…", "جارٍ الاتصال…")
_t("upd_dl_fail", "Không tải được bản cập nhật.\n{0}\n\nBạn có thể tải thủ công từ trang phát hành.",
   "The update could not be downloaded.\n{0}\n\nYou can download it manually from the release page.",
   "تعذر تنزيل التحديث.\n{0}\n\nيمكنك تنزيله يدويًا من صفحة الإصدار.")
_t("upd_installing", "Đang cài bản mới. Ứng dụng sẽ tự đóng và mở lại sau vài giây; dữ liệu của bạn được giữ nguyên.",
   "Installing the new version. The app will close and reopen in a few seconds; your data is kept.",
   "جارٍ تثبيت الإصدار الجديد. سيُغلق التطبيق ويُعاد فتحه خلال ثوانٍ؛ بياناتك محفوظة.")
_t("upd_store", "Bản cài từ Microsoft Store được cập nhật tự động qua Store.",
   "This copy comes from the Microsoft Store and is updated through the Store.",
   "هذه النسخة من متجر Microsoft وتُحدَّث عبر المتجر.")
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


# ---- moving data to another computer / online copy
_t("tx_title", "Chuyển dữ liệu", "Move your data", "نقل البيانات")
_t("tx_files", "Gói dữ liệu kho", "Warehouse data package", "حزمة بيانات المخزن")
_t("tx_card", "Chuyển sang máy mới / sao lưu online", "New computer / online backup", "جهاز جديد / نسخة على الإنترنت")
_t("tx_card_hint",
   "Xuất toàn bộ (dữ liệu + ảnh) thành 1 file .pwbak. Sang máy mới: cài app, vào đây bấm Khôi phục và chọn file đó.",
   "Export everything (data + photos) as one .pwbak file. On a new computer: install the app, come here, press Restore and pick that file.",
   "صدّر كل شيء (البيانات + الصور) في ملف .pwbak واحد. على جهاز جديد: ثبّت التطبيق، ثم اضغط استعادة واختر الملف.")
_t("tx_btn_export", "Xuất gói dữ liệu", "Export data package", "تصدير حزمة البيانات")
_t("tx_btn_restore", "Khôi phục từ gói…", "Restore from package…", "استعادة من حزمة…")
_t("tx_sync_title", "Đồng bộ online", "Online sync", "المزامنة عبر الإنترنت")
_t("tx_sync_hint",
   "Chọn một thư mục đang được OneDrive / Google Drive / Dropbox đồng bộ. App tự lưu 1 gói vào đó mỗi lần thoát (giữ 7 bản gần nhất). Máy mới chỉ cần đăng nhập cùng tài khoản đó rồi Khôi phục.",
   "Pick a folder that OneDrive / Google Drive / Dropbox keeps online. The app saves a package there every time you quit (newest 7 kept). On a new computer, sign in to the same account and Restore.",
   "اختر مجلدًا تزامنه OneDrive / Google Drive / Dropbox. يحفظ التطبيق حزمة فيه عند كل إغلاق (آخر 7 نسخ). على جهاز جديد سجّل الدخول بنفس الحساب ثم استعد.")
_t("tx_sync_none", "Chưa bật đồng bộ.", "Sync is off.", "المزامنة متوقفة.")
_t("tx_sync_on", "Đang lưu vào: {0}\nLần cuối: {1}", "Saving to: {0}\nLast: {1}", "الحفظ في: {0}\nآخر مرة: {1}")
_t("tx_btn_sync_pick", "Chọn thư mục…", "Choose folder…", "اختيار مجلد…")
_t("tx_btn_sync_now", "Đồng bộ ngay", "Sync now", "زامن الآن")
_t("tx_btn_sync_off", "Tắt đồng bộ", "Turn off", "إيقاف")
_t("tx_exported", "Đã xuất: {0}\n{1} mặt hàng, {2} ảnh. Chép file này sang máy mới (USB, email, Drive…).",
   "Exported: {0}\n{1} item(s), {2} photo(s). Copy this file to the new computer (USB, e-mail, Drive…).",
   "تم التصدير: {0}\n{1} صنف، {2} صورة. انسخ الملف إلى الجهاز الجديد.")
_t("tx_restore_title", "Khôi phục dữ liệu", "Restore data", "استعادة البيانات")
_t("tx_restore_msg", "Gói tạo lúc {0}: {1} mặt hàng, {2} lịch sử nhập/xuất, {3} ảnh.\n\n{4}Tiếp tục khôi phục?",
   "Package made {0}: {1} item(s), {2} movement(s), {3} photo(s).\n\n{4}Restore it?",
   "حزمة أُنشئت {0}: {1} صنف، {2} حركة، {3} صورة.\n\n{4}هل تريد الاستعادة؟")
_t("tx_replace_warn", "Dữ liệu hiện tại sẽ bị thay thế (có tự lưu bản trước khi khôi phục).\n\n",
   "Your current data will be replaced (a copy is saved first).\n\n",
   "سيتم استبدال بياناتك الحالية (تُحفظ نسخة قبل ذلك).\n\n")
_t("tx_restored", "Đã khôi phục {0} mặt hàng.{1}", "Restored {0} item(s).{1}", "تمت استعادة {0} صنف.{1}")
_t("tx_restored_safety", "\nBản dữ liệu cũ được giữ ở Backup/{0}", "\nYour previous data is kept in Backup/{0}",
   "\nبياناتك السابقة محفوظة في Backup/{0}")
_t("tx_synced", "Đã lưu {0}\nvào {1}", "Saved {0}\nto {1}", "تم حفظ {0}\nفي {1}")
_t("tx_err_not_package", "Đây không phải gói dữ liệu của Personal Warehouse.", "This is not a Personal Warehouse package.",
   "هذا ليس ملف حزمة لـ Personal Warehouse.")
_t("tx_err_damaged", "File bị hỏng hoặc tải chưa xong. Dữ liệu hiện tại không bị đổi.",
   "The file is damaged or incomplete. Your current data was not changed.", "الملف تالف أو غير مكتمل. لم تتغير بياناتك الحالية.")
_t("tx_err_too_new", "Gói này tạo bởi phiên bản app mới hơn. Hãy cập nhật app rồi thử lại.",
   "This package was made by a newer version of the app. Update the app and try again.",
   "أُنشئت هذه الحزمة بإصدار أحدث من التطبيق. حدّث التطبيق وحاول مجددًا.")
_t("tx_err_sync_missing", "Thư mục đồng bộ không tồn tại (ổ đĩa/Drive chưa sẵn sàng?).",
   "The sync folder does not exist (is the drive / cloud app ready?).", "مجلد المزامنة غير موجود.")
_t("tx_err_sync_fail", "Không ghi được vào thư mục đồng bộ: {0}", "Could not write to the sync folder: {0}",
   "تعذرت الكتابة في مجلد المزامنة: {0}")


# ---- history / undo, restore points, backup health, password
_t("hx_title", "Hoàn tác", "Undo", "تراجع")
_t("hx_confirm", "Hoàn tác thay đổi này? (Việc hoàn tác cũng được ghi lại và có thể hoàn tác tiếp.)",
   "Undo this change? (The undo is recorded too and can itself be undone.)",
   "هل تريد التراجع عن هذا التغيير؟ (يُسجَّل التراجع أيضًا ويمكن التراجع عنه.)")
_t("hx_done", "Đã hoàn tác: {0}", "Undone: {0}", "تم التراجع: {0}")
_t("hx_btn", "Hoàn tác", "Undo", "تراجع")
_t("hx_btn_undone", "Đã hoàn tác", "Undone", "تم التراجع")
_t("nav_history", "Lịch sử thay đổi", "Change history", "سجل التغييرات")
_t("hx_sub", "Mọi lần sửa, lưu trữ, xóa và nhập/xuất kho đều được ghi lại và hoàn tác được.",
   "Every edit, archive, delete and stock movement is recorded and can be undone.",
   "يُسجَّل كل تعديل وأرشفة وحذف وحركة مخزون ويمكن التراجع عنه.")
_t("hx_col_when", "Thời gian", "When", "الوقت")
_t("hx_col_what", "Việc đã làm", "What happened", "ما حدث")
_t("hx_col_item", "Mặt hàng", "Item", "الصنف")
_t("hx_col_detail", "Chi tiết", "Details", "التفاصيل")
_t("hx_act_create", "Thêm mới", "Created", "إضافة")
_t("hx_act_update", "Sửa", "Edited", "تعديل")
_t("hx_act_delete", "Xóa", "Deleted", "حذف")
_t("hx_act_movement", "Nhập/Xuất", "Stock move", "حركة مخزون")
_t("hx_delete_detail", "Xóa kèm {0} dòng lịch sử nhập/xuất", "Deleted with {0} movement record(s)", "حُذف مع {0} حركة")
_t("hx_err_gone", "Không tìm thấy mục này.", "That entry was not found.", "لم يتم العثور على هذا السجل.")
_t("hx_err_done", "Mục này đã được hoàn tác rồi.", "That change was already undone.", "تم التراجع عن هذا التغيير مسبقًا.")
_t("hx_err_missing", "Mặt hàng không còn tồn tại.", "The item no longer exists.", "الصنف لم يعد موجودًا.")
_t("hx_err_changed", "Mặt hàng đã được thay đổi sau đó. Hãy hoàn tác thay đổi mới hơn trước.",
   "The item was changed afterwards. Undo the newer change first.",
   "تم تغيير الصنف بعد ذلك. تراجع عن التغيير الأحدث أولًا.")
_t("hx_err_exists", "Không khôi phục được: mã hàng hoặc mặt hàng này đã tồn tại.",
   "Cannot restore: this item or its code already exists.", "تعذرت الاستعادة: الصنف أو رمزه موجود مسبقًا.")
_t("hx_err_stock", "Không hoàn tác được: tồn hiện tại ({0}) không đủ để trừ lại.",
   "Cannot undo: current stock ({0}) is too low to reverse it.", "لا يمكن التراجع: المخزون الحالي ({0}) غير كافٍ.")
_t("rp_title", "Sao lưu & điểm khôi phục", "Backups & restore points", "النسخ الاحتياطية ونقاط الاستعادة")
_t("rp_hint", "App tự sao lưu mỗi ngày (giữ 14 ngày + 8 tuần + 12 tháng) và trước khi xóa / khôi phục / nâng cấp. Mỗi bản đều được kiểm tra đọc được.",
   "The app backs up daily (kept: 14 days + 8 weeks + 12 months) and before every delete / restore / upgrade. Every copy is verified readable.",
   "يُنشئ التطبيق نسخة يوميًا (تُحفظ 14 يومًا + 8 أسابيع + 12 شهرًا) وقبل كل حذف / استعادة / ترقية. يتم التحقق من كل نسخة.")
_t("rp_auto", "Tự động", "Automatic", "تلقائي")
_t("rp_delete", "Trước khi xóa", "Before delete", "قبل الحذف")
_t("rp_restore", "Trước khi khôi phục", "Before restore", "قبل الاستعادة")
_t("rp_upgrade", "Trước khi nâng cấp", "Before upgrade", "قبل الترقية")
_t("rp_other", "Khác", "Other", "أخرى")
_t("rp_items", "{0} mặt hàng", "{0} item(s)", "{0} صنف")
_t("rp_btn", "Khôi phục bản này", "Restore this", "استعادة هذه")
_t("rp_confirm", "Quay về dữ liệu trong bản “{0}”? Dữ liệu hiện tại được lưu lại trước khi thay.",
   "Go back to the data in “{0}”? Your current data is saved first.", "العودة إلى بيانات «{0}»؟ تُحفظ بياناتك الحالية أولًا.")
_t("rp_done", "Đã khôi phục từ {0}.{1}", "Restored from {0}.{1}", "تمت الاستعادة من {0}.{1}")
_t("rp_status_local", "Sao lưu trên máy: {0}", "Backup on this computer: {0}", "نسخة على هذا الجهاز: {0}")
_t("rp_status_off_ok", "Bản ngoài máy: {0} ✓", "Copy off this computer: {0} ✓", "نسخة خارج الجهاز: {0} ✓")
_t("rp_status_off_warn", "⚠ Chưa có bản sao nào ngoài máy trong {0} ngày qua. Máy hỏng/mất là mất dữ liệu: hãy bật Đồng bộ online hoặc Xuất gói rồi cất vào USB/Drive.",
   "⚠ No copy has left this computer in the last {0} days. If this machine fails you lose the data: turn on Online sync or export a package to USB/Drive.",
   "⚠ لا توجد نسخة خارج هذا الجهاز خلال آخر {0} أيام. فعّل المزامنة أو صدّر حزمة إلى USB/Drive.")
_t("rp_status_off_never", "⚠ Chưa có bản sao nào ngoài máy. Hãy bật Đồng bộ online hoặc Xuất gói dữ liệu.",
   "⚠ No copy exists outside this computer yet. Turn on Online sync or export a data package.",
   "⚠ لا توجد نسخة خارج هذا الجهاز. فعّل المزامنة أو صدّر حزمة.")
_t("tx_pw_title", "Bảo vệ bằng mật khẩu (tùy chọn)", "Password protection (optional)", "حماية بكلمة مرور (اختياري)")
_t("tx_pw_hint", "Để trống = không mã hóa. Có mật khẩu thì file được mã hóa AES-256; mất mật khẩu là không mở lại được.",
   "Leave empty for no encryption. With a password the file is AES-256 encrypted; if you lose the password it cannot be opened.",
   "اتركه فارغًا بدون تشفير. مع كلمة مرور يُشفَّر الملف بـ AES-256؛ وبفقدانها لا يمكن فتحه.")
_t("tx_pw_f1", "Mật khẩu", "Password", "كلمة المرور")
_t("tx_pw_f2", "Nhập lại mật khẩu", "Repeat password", "أعد كلمة المرور")
_t("tx_pw_mismatch", "Hai mật khẩu không giống nhau.", "The two passwords do not match.", "كلمتا المرور غير متطابقتين.")
_t("tx_pw_ask", "Gói này được bảo vệ bằng mật khẩu. Nhập mật khẩu để mở.", "This package is password-protected. Enter the password to open it.",
   "هذه الحزمة محمية بكلمة مرور. أدخلها لفتحها.")
_t("tx_locked", "\nĐã mã hóa bằng mật khẩu.", "\nEncrypted with your password.", "\nمشفّرة بكلمة المرور.")
_t("tx_err_need_password", "Cần mật khẩu để mở gói này.", "A password is needed to open this package.", "مطلوب كلمة مرور لفتح هذه الحزمة.")
_t("tx_err_bad_password", "Sai mật khẩu (hoặc file bị hỏng).", "Wrong password (or the file is damaged).", "كلمة المرور خاطئة (أو الملف تالف).")
_t("tx_err_no_crypto", "Máy này chưa có thư viện mã hóa (pip install cryptography).", "Encryption library missing (pip install cryptography).",
   "مكتبة التشفير غير مثبتة (pip install cryptography).")
_t("tx_sync_plain", "Lưu ý: bản đồng bộ KHÔNG mã hóa. Chỉ chọn thư mục tài khoản riêng của bạn; muốn bảo mật hơn hãy dùng Xuất gói có mật khẩu.",
   "Note: sync copies are NOT encrypted. Use a folder in your own private account; for stronger protection export a password-protected package.",
   "ملاحظة: نسخ المزامنة غير مشفّرة. استخدم مجلد حسابك الخاص؛ وللحماية الأقوى صدّر حزمة بكلمة مرور.")


# ---- where the data lives
_t("loc_title", "Dữ liệu của bạn nằm ở đâu", "Where your data lives", "أين توجد بياناتك")
_t("loc_intro", "Mọi thứ nằm trong MỘT thư mục gốc, chia thư mục con cố định. Xóa/gỡ app không đụng tới thư mục này.",
   "Everything lives under ONE root folder with fixed sub-folders. Uninstalling the app never touches it.",
   "كل شيء داخل مجلد جذر واحد بمجلدات فرعية ثابتة. إزالة التطبيق لا تمس هذا المجلد.")
_t("loc_root", "Thư mục gốc", "Root folder", "المجلد الجذر")
_t("loc_root_hint", "Chứa tất cả bên dưới + settings.json", "Holds everything below + settings.json", "يحتوي كل ما يلي + settings.json")
_t("loc_db", "Cơ sở dữ liệu", "Database", "قاعدة البيانات")
_t("loc_db_hint", "warehouse.db: hàng, vị trí, nhập/xuất, lịch sử", "warehouse.db: items, locations, movements, history", "warehouse.db: الأصناف والمواقع والحركات والسجل")
_t("loc_photos", "Ảnh", "Photos", "الصور")
_t("loc_photos_hint", "Ảnh mặt hàng", "Item photos", "صور الأصناف")
_t("loc_backup", "Sao lưu tự động", "Automatic backups", "النسخ التلقائية")
_t("loc_backup_hint", "Mỗi ngày + trước khi xóa/khôi phục/nâng cấp", "Daily + before delete / restore / upgrade", "يوميًا + قبل الحذف/الاستعادة/الترقية")
_t("loc_trash", "Thùng rác (ảnh)", "Trash (photos)", "سلة المهملات (صور)")
_t("loc_trash_hint", "Ảnh của hàng đã xóa, giữ 90 ngày để Hoàn tác", "Photos of deleted items, kept 90 days for Undo", "صور الأصناف المحذوفة، 90 يومًا للتراجع")
_t("loc_export", "File xuất ra", "Exports", "الملفات المصدّرة")
_t("loc_export_hint", "Excel, gói .pwbak: hộp thoại lưu luôn mở ở đây", "Excel and .pwbak files: save dialogs always open here", "ملفات Excel و .pwbak: نوافذ الحفظ تفتح هنا دائمًا")
_t("loc_labels", "Tem in", "Labels", "الملصقات")
_t("loc_labels_hint", "Trang tem tạm (giữ 20 bản gần nhất)", "Temporary label pages (newest 20 kept)", "صفحات الملصقات المؤقتة (آخر 20)")
_t("loc_sync", "Thư mục đồng bộ online", "Online sync folder", "مجلد المزامنة")
_t("loc_sync_hint", "Bản sao ngoài máy (OneDrive / Drive / Dropbox)", "Copy outside this computer", "نسخة خارج هذا الجهاز")
_t("loc_open", "Mở", "Open", "فتح")
_t("loc_files", "{0} file • {1} MB", "{0} file(s) • {1} MB", "{0} ملف • {1} م.ب")
_t("loc_move", "Đổi thư mục dữ liệu…", "Change data folder…", "تغيير مجلد البيانات…")
_t("loc_move_title", "Đổi thư mục dữ liệu", "Change data folder", "تغيير مجلد البيانات")
_t("loc_moved", "Đã sao chép toàn bộ dữ liệu sang:\n{0}\n\nThư mục cũ ({1}) được giữ nguyên, bạn tự xóa khi chắc chắn. App sẽ đóng; mở lại để dùng vị trí mới.",
   "All data was copied to:\n{0}\n\nThe old folder ({1}) is left untouched; delete it yourself when you are sure. The app will close; reopen it to use the new place.",
   "تم نسخ كل البيانات إلى:\n{0}\n\nالمجلد القديم ({1}) لم يُمس؛ احذفه بنفسك عند التأكد. سيُغلق التطبيق؛ أعد فتحه.")
_t("loc_same", "Hãy chọn một thư mục khác với thư mục dữ liệu hiện tại (và không nằm bên trong nó).",
   "Pick a folder other than the current data folder (and not inside it).", "اختر مجلدًا مختلفًا عن المجلد الحالي (وليس بداخله).")
_t("loc_exists", "Thư mục {0} đã có dữ liệu kho. Hãy chọn thư mục trống.", "{0} already contains warehouse data. Pick an empty folder.",
   "المجلد {0} يحتوي بيانات مخزن. اختر مجلدًا فارغًا.")
_t("loc_move_fail", "Không sao chép được: {0}. Dữ liệu cũ vẫn nguyên vẹn.", "Could not copy: {0}. Your current data is untouched.",
   "تعذر النسخ: {0}. بياناتك الحالية سليمة.")
_t("loc_desktop_only", "Chỉ đổi được trong cửa sổ ứng dụng.", "Only available in the app window.", "متاح في نافذة التطبيق فقط.")
_t("loc_cloud_warn", "⚠ Thư mục dữ liệu đang nằm trong OneDrive/Dropbox/Drive. Cơ sở dữ liệu đang mở mà bị đồng bộ có thể hỏng. Nên dùng thư mục thường (vd. C:\\MyWarehouse) và dùng Đồng bộ online để sao lưu.",
   "⚠ The data folder sits inside OneDrive/Dropbox/Drive. A database that is open while being synced can get corrupted. Prefer a normal folder (e.g. C:\\MyWarehouse) and use Online sync for copies.",
   "⚠ مجلد البيانات داخل OneDrive/Dropbox/Drive. قد تتلف قاعدة بيانات مفتوحة أثناء المزامنة. استخدم مجلدًا عاديًا (مثل C:\\MyWarehouse) واستعمل المزامنة للنسخ.")

# ---- about / feedback / support
_t("nav_about", "Giới thiệu & ủng hộ", "About & support", "حول التطبيق والدعم")
_t("ab_sub", "Về ứng dụng, gửi góp ý cho tác giả và ủng hộ dự án.", "About the app, send the author feedback and support the project.",
   "حول التطبيق، أرسل ملاحظاتك للمطوّر وادعم المشروع.")
_t("ab_about", "Về ứng dụng", "About the app", "عن التطبيق")
_t("ab_desc", "Personal Warehouse là phần mềm quản lý kho cá nhân chạy offline: dữ liệu nằm trên máy của bạn, không cần tài khoản hay máy chủ. Miễn phí, mã nguồn mở (MIT).",
   "Personal Warehouse is an offline personal inventory manager: your data stays on your computer, no account or server needed. Free and open source (MIT).",
   "Personal Warehouse برنامج لإدارة المخزن الشخصي يعمل دون إنترنت: بياناتك على جهازك، دون حساب أو خادم. مجاني ومفتوح المصدر (MIT).")
_t("ab_version", "Phiên bản", "Version", "الإصدار")
_t("ab_author", "Tác giả", "Author", "المطوّر")
_t("ab_contact", "Liên hệ", "Contact", "التواصل")
_t("ab_github", "Mã nguồn & tải về (GitHub)", "Source & downloads (GitHub)", "الشيفرة والتنزيلات (GitHub)")
_t("ab_issues", "Báo lỗi trên GitHub", "Report an issue on GitHub", "الإبلاغ عن مشكلة على GitHub")
_t("ab_privacy", "Quyền riêng tư: app không gửi dữ liệu kho của bạn đi đâu. Chỉ khi bạn bấm Gửi góp ý thì thư mới được mở bằng email của chính bạn.",
   "Privacy: the app never sends your warehouse data anywhere. Only when you press Send feedback does a message open in your own e-mail.",
   "الخصوصية: لا يرسل التطبيق بيانات مخزنك إلى أي مكان. تُفتح رسالة في بريدك فقط عند الضغط على إرسال.")
_t("fb_title", "Hộp thư góp ý", "Feedback box", "صندوق الملاحظات")
_t("fb_hint", "Viết góp ý, báo lỗi hoặc ý tưởng. Bấm gửi sẽ mở email của bạn với thư đã soạn sẵn gửi tới {0}; bạn chỉ cần bấm Gửi trong email.",
   "Write a suggestion, bug or idea. Sending opens your e-mail with the message ready for {0}; just press Send there.",
   "اكتب اقتراحًا أو مشكلة أو فكرة. يفتح الإرسال بريدك والرسالة جاهزة إلى {0}؛ اضغط إرسال هناك.")
_t("fb_kind", "Loại", "Type", "النوع")
_t("fb_kind_idea", "Ý tưởng / đề xuất", "Idea / suggestion", "فكرة / اقتراح")
_t("fb_kind_bug", "Báo lỗi", "Bug report", "إبلاغ عن خطأ")
_t("fb_kind_thanks", "Lời cảm ơn", "Thanks", "شكر")
_t("fb_kind_other", "Khác", "Other", "أخرى")
_t("fb_msg", "Nội dung", "Message", "الرسالة")
_t("fb_contact", "Email / số điện thoại của bạn (không bắt buộc, để tác giả trả lời)", "Your e-mail / phone (optional, so the author can reply)",
   "بريدك / هاتفك (اختياري للرد عليك)")
_t("fb_info", "Kèm thông tin máy (phiên bản app, hệ điều hành; không kèm dữ liệu kho)", "Include system info (app version, OS; no warehouse data)",
   "إرفاق معلومات النظام (إصدار التطبيق، النظام؛ دون بيانات المخزن)")
_t("fb_send_mail", "Gửi bằng ứng dụng email", "Send with my mail app", "إرسال عبر برنامج البريد")
_t("fb_send_gmail", "Gửi bằng Gmail (web)", "Send with Gmail (web)", "إرسال عبر Gmail (ويب)")
_t("fb_copy", "Sao chép nội dung", "Copy text", "نسخ النص")
_t("fb_copied", "Đã sao chép.", "Copied.", "تم النسخ.")
_t("fb_empty", "Hãy viết nội dung góp ý (ít nhất vài chữ).", "Please write your feedback (a few words at least).", "يرجى كتابة ملاحظتك (بضع كلمات على الأقل).")
_t("fb_too_long", "Nội dung quá dài để mở qua email (giới hạn của Windows). Hãy rút gọn, dùng Gmail (web), hoặc Sao chép rồi dán vào email.",
   "The message is too long for a mail link (a Windows limit). Shorten it, use Gmail (web), or Copy it and paste into an e-mail.",
   "الرسالة طويلة جدًا لرابط بريد. اختصرها أو استخدم Gmail أو انسخها والصقها في بريد.")
_t("fb_opened", "Đã mở email gửi tới {0}. Hãy bấm Gửi trong email. Nếu không thấy gì, dùng Gmail (web) hoặc Sao chép.",
   "Your e-mail was opened for {0}. Press Send there. If nothing appeared, use Gmail (web) or Copy.",
   "تم فتح البريد إلى {0}. اضغط إرسال هناك. إن لم يظهر شيء استخدم Gmail أو النسخ.")
_t("dn_title", "Ủng hộ tác giả", "Support the author", "ادعم المطوّر")
_t("dn_text", "Ứng dụng miễn phí. Nếu nó giúp ích cho bạn, bạn có thể mời tác giả một ly cà phê. Mọi sự ủng hộ đều là động lực để tiếp tục cập nhật. Cảm ơn bạn!",
   "The app is free. If it helps you, you can buy the author a coffee. Every bit of support keeps updates coming. Thank you!",
   "التطبيق مجاني. إن أفادك يمكنك دعوة المطوّر لفنجان قهوة. كل دعم يشجع على الاستمرار. شكرًا لك!")
_t("dn_none", "Thông tin nhận ủng hộ sẽ được cập nhật sớm. Bạn vẫn có thể ủng hộ bằng cách chia sẻ app và gửi góp ý.",
   "Donation details will be added soon. You can still help by sharing the app and sending feedback.",
   "ستُضاف بيانات الدعم قريبًا. يمكنك المساعدة بمشاركة التطبيق وإرسال الملاحظات.")
_t("dn_copy", "Sao chép", "Copy", "نسخ")
