# Changelog

Định dạng theo [Keep a Changelog](https://keepachangelog.com/). Nội dung mục của mỗi phiên bản
được dùng làm ghi chú phát hành trên GitHub (và hiển thị trong hộp thoại cập nhật của app).


## [3.7.0] - 2026-11-20
### Changed
- **Sơ đồ kho** làm lại: mặt bằng 3 khu × 8 ngăn lấp đầy chiều ngang (không còn ô trống), màu đậm theo số mặt hàng, chấm đỏ khi có hàng sắp hết, thẻ thống kê trên đầu, bấm một ô để xem hàng ngay bên dưới (nút *Mở trong Kho hàng*).
### Added
- Chế độ xem **3D** (kéo để xoay, chiều cao cột = số mặt hàng, nút Nhìn từ trên), không cần thư viện ngoài.

## [3.6.2] - 2026-11-20
### Fixed
- Windows: `python -m personal_warehouse` báo `Argument 'picture' must be a picture that can be used as a Icon` khi mở cửa sổ (pywebview/WinForms không nhận icon PNG). Nay trên Windows không truyền icon PNG; icon cửa sổ/thanh tác vụ đặt bằng file `.ico`.

## [3.6.1] - 2026-11-20
- Gắn icon thật (`icon.png`, `icon.ico`, ảnh Microsoft Store tạo từ `packaging/StoreListing/icon-source.png`); thêm tên tác giả Võ Thế Anh.

## [3.6.0] - 2026-11-20
### Added
- Trang **Giới thiệu & ủng hộ**: thông tin app/phiên bản/liên hệ, liên kết GitHub, **hộp thư góp ý** (mở email hoặc Gmail web của người dùng với thư soạn sẵn gửi theanh1129@gmail.com, tùy chọn kèm thông tin máy, không kèm dữ liệu kho), khu vực **ủng hộ** (danh sách + nút sao chép + ảnh QR `donate_qr.png`).
- **Icon ứng dụng**: `packaging/make_icons.py` tạo `icon.png`/`icon.ico`/ảnh Microsoft Store từ một ảnh; `build.ps1` (PyInstaller `--icon`), `installer.iss` (SetupIconFile), thanh bên, favicon, cửa sổ và thanh tác vụ Windows tự dùng icon. Cần commit các file icon lên GitHub.

## [3.5.0] - 2026-11-20
### Fixed
- Hộp thoại xóa vẫn ghi "Không thể hoàn tác" (chữ cũ) và không có đường quay lại. Nay: nói rõ có thể lấy lại, nút nhãn "Xóa" (không còn "vĩnh viễn"), và sau khi xóa hiện ngay nút **Hoàn tác** (20 giây) + nhắc trang Lịch sử thay đổi.
### Added
- **Nhập nhanh**: Enter = sang ô kế, Enter ở ô cuối hoặc Ctrl+Enter = lưu (hàng mới: lưu rồi mở form trống, giữ lại vị trí/danh mục/NCC/đơn vị…); nút *Lưu & thêm tiếp*; gợi ý từ dữ liệu cũ cho Tên hàng, Danh mục, Động cơ/Ứng dụng, Nhà cung cấp; ô số tự bôi đen để gõ đè; Nhập/Xuất: Enter ở ô số lượng = lưu.
- **Vị trí dữ liệu rõ ràng**: một thư mục gốc, thư mục con cố định (Database, Photos, Backup, Trash, Export, Labels). Cài đặt liệt kê đường dẫn, dung lượng, nút *Mở*; *Đổi thư mục dữ liệu…* sao chép + kiểm tra rồi ghi nhớ (thư mục cũ giữ nguyên). Mọi hộp thoại lưu/mở file luôn bắt đầu ở `Export/`. Tìm đúng thư mục Documents của Windows (kể cả khi bị chuyển vào OneDrive) và cảnh báo nếu CSDL nằm trong thư mục đang đồng bộ cloud.
- Nút "Sao lưu" cũ (copy thư mục) được gộp vào *Xuất gói dữ liệu* để chỉ còn một cách sao lưu thủ công.

## [3.4.0] - 2026-11-19
### Added
- **Lịch sử thay đổi + Hoàn tác** (trang mới): mọi lần thêm, sửa, lưu trữ, xóa và nhập/xuất kho đều được ghi lại; bấm *Hoàn tác* để quay lại. Chỉ hoàn tác khi mặt hàng chưa bị đổi tiếp (tránh ghi đè công việc mới); bản thân việc hoàn tác cũng được ghi nên làm lại được. Nhập/xuất không bao giờ bị xóa khỏi sổ, hoàn tác = thêm một dòng điều chỉnh bù.
- **Xóa không mất hẳn**: xóa mặt hàng giữ lại toàn bộ dòng dữ liệu + lịch sử nhập/xuất trong nhật ký; ảnh chuyển vào `Trash/` (90 ngày) thay vì xóa.
- **Mã hóa gói dữ liệu bằng mật khẩu** (AES-256-GCM, scrypt). Phát hiện file bị sửa/cắt cụt; sai mật khẩu không làm đổi dữ liệu. Cần `cryptography` (đã nằm trong `[all]`).
- **Điểm khôi phục**: danh sách các bản sao lưu tự động và các bản "trước khi xóa / khôi phục / nâng cấp", khôi phục bằng một nút; luôn có bản lưu dữ liệu hiện tại trước khi thay.
- **Sao lưu theo chuẩn**: mỗi bản đều được kiểm tra đọc được (integrity check + SHA-256 trong gói); giữ 14 ngày + 8 tuần + 12 tháng; `synchronous=FULL`; cảnh báo 3-2-1 nếu quá 7 ngày chưa có bản nào ngoài máy.

## [3.3.0] - 2026-11-19
### Added
- **Chuyển sang máy mới**: Cài đặt → *Xuất gói dữ liệu* tạo 1 file `.pwbak` (CSDL + ảnh + ngôn ngữ/giao diện). Máy mới: cài app → *Khôi phục từ gói…*. Có kiểm tra file (đúng định dạng, không hỏng, không từ bản app mới hơn) trước khi đụng vào dữ liệu, và tự giữ bản cũ `Backup/before_restore_*.pwbak` để quay lại.
- **Đồng bộ online**: chọn thư mục OneDrive / Google Drive / Dropbox; app lưu gói vào đó mỗi lần thoát (giữ 7 bản). Máy mới đăng nhập cùng tài khoản rồi Khôi phục.

## [3.2.0] - 2026-11-19
### Added
- Tự cập nhật ngay trong app: khi mở app (có Internet) sẽ báo bản mới; bấm **Cập nhật ngay** để app tự tải (có thanh tiến trình, kiểm tra SHA-256), tự cài và mở lại, hoặc bấm **Để sau**. Dữ liệu được sao lưu trước khi cài và không bị thay đổi.
- Bản cài từ Microsoft Store không dùng cơ chế này (Store tự cập nhật).

## [3.1.0] - 2026-11-19
### Added
- Giao diện mới dựng bằng web (pywebview) theo phong cách dashboard: kem / đỏ / vàng / teal, sáng + tối, VI / EN / AR (RTL). Giao diện Tkinter cũ vẫn dùng được với `--tk`.

### Changed
### Fixed
- Tiếng Ả Rập (RTL): đảo đúng thứ tự cột của form Thêm/Sửa hàng, form Nhập/Xuất, sơ đồ kho, trang Quét mã, hộp thoại
  in tem và trang Cài đặt; khoảng cách giữa thẻ chính và thẻ ảnh nằm đúng phía.
- Thanh cuộn của bảng không còn bị khung bảng đè mất.

## [3.0.0] - 2026-11-16
### Added
- Dự án hóa: package `personal_warehouse`, cài bằng pip, file `.exe` và bộ cài Windows.
- Tự kiểm tra bản cập nhật qua GitHub Releases (có thể tắt trong Cài đặt).
- Biến môi trường `PW_DATA_DIR` để đổi thư mục dữ liệu.
- Bộ kiểm thử tự động và CI.

### Changed
- Tách mã nguồn thành các module theo chức năng: `core/` (dữ liệu, tồn kho, tem, xuất file), `i18n/` (bản dịch theo
  tính năng), `ui/` (giao diện, mỗi trang một file). Hành vi giữ nguyên.
- `save_settings` giữ nguyên các khóa cài đặt khác khi ghi file.
