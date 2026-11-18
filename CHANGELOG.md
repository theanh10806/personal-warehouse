# Changelog

Định dạng theo [Keep a Changelog](https://keepachangelog.com/). Nội dung mục của mỗi phiên bản
được dùng làm ghi chú phát hành trên GitHub (và hiển thị trong hộp thoại cập nhật của app).

## Chưa phát hành
- Giao diện mới dựng bằng web (pywebview) theo phong cách dashboard: kem / đỏ / vàng / teal, sáng + tối, VI / EN / AR (RTL). Giao diện Tkinter cũ vẫn dùng được với `--tk`.

## [Unreleased]
### Changed
- Giao diện mới theo phong cách dashboard kho hiện đại: thanh bên có thể thu gọn thành icon, thanh trên cùng có ô
  tìm kiếm chung, thẻ chỉ số (KPI) có biểu tượng, biểu đồ nhập/xuất 14 ngày, khung "Gợi ý thông minh" (tính offline
  từ dữ liệu kho), danh sách cần chú ý và hoạt động gần đây.
- Mọi trang đều có thanh cuộn dọc (và cuộn bằng chuột) khi cửa sổ nhỏ; bố cục tự xếp lại 4 → 2 → 1 cột theo chiều rộng.
- Cửa sổ mở theo kích thước màn hình (có tính DPI), kích thước tối thiểu 720×500.
- Bảng dữ liệu co giãn theo chiều rộng và hiện thanh cuộn ngang chỉ khi thật sự thiếu chỗ.

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
