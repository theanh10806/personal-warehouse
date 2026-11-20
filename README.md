# Personal Warehouse (Kho Cá Nhân)

Phần mềm quản lý kho **offline** (Tkinter + SQLite) cho Windows. Giao diện Tiếng Việt / English / العربية,
sáng / tối, tạo tem QR và mã vạch Code 128, quét bằng máy quét USB, camera hoặc ảnh, xuất Excel/CSV, tự sao lưu.

## Dành cho người dùng

1. Vào trang **Releases** của dự án trên GitHub.
2. Tải `PersonalWarehouse-Setup-x.y.z.exe` và chạy (không cần quyền admin, không cần cài Python).
3. Dữ liệu nằm ở `Documents\MyWarehouse`. Cài bản mới hoặc gỡ ứng dụng **không** xóa dữ liệu.
4. **Icon ứng dụng**: chạy một lần `python packaging/make_icons.py duong_dan/icon.png` (cần Pillow). Lệnh tạo `icon.png`, `icon.ico` (trong `webui/static/`) và ảnh Microsoft Store (`packaging/Assets/`). **Hãy commit các file này lên GitHub**: build (`build.ps1`, `installer.iss`) tự dùng chúng nên bản tải từ GitHub có icon ở file .exe, trình cài đặt, thanh tác vụ, cửa sổ và thanh bên của app.
5. **Giới thiệu, góp ý, ủng hộ**: trang *Giới thiệu & ủng hộ*. Góp ý mở email (hoặc Gmail web) của người dùng với thư soạn sẵn gửi `theanh1129@gmail.com`; app không lưu mật khẩu nào. Sửa tên tác giả và thông tin ủng hộ trong `src/personal_warehouse/about.py` (mục `DONATE`); ảnh QR đặt tên `donate_qr.png` trong `webui/static/` sẽ tự hiện.
6. **Sang máy mới / sao lưu online**: *Cài đặt → Xuất gói dữ liệu* tạo file `.pwbak` (dữ liệu + ảnh). Trên máy mới cài app, vào *Cài đặt → Khôi phục từ gói…*.
   Hoặc bật *Đồng bộ online* và chọn một thư mục OneDrive / Google Drive / Dropbox: app tự lưu gói vào đó mỗi lần thoát.
7. **An toàn dữ liệu**: trang *Lịch sử thay đổi* ghi mọi thao tác và cho *Hoàn tác* (kể cả xóa). *Cài đặt → Sao lưu & điểm khôi phục* liệt kê các bản tự sao lưu để quay lại. Quy tắc 3-2-1: bản trên máy (tự động) + bản ngoài máy (Đồng bộ online hoặc Xuất gói, nên đặt mật khẩu) + giữ nhiều bản theo thời gian.
8. Khi có bản mới, app báo trong lúc mở (tắt được ở **Cài đặt → Cập nhật**). Bấm đồng ý để mở trang tải về,
   chạy bộ cài mới là xong; cơ sở dữ liệu tự nâng cấp và có bản sao lưu trước khi nâng cấp.

## Chạy từ mã nguồn

### Sao lưu và chuyển máy

Dữ liệu làm việc và sao lưu chính nằm trên máy. Xuất gói `.pwbak` để giữ bản đầy đủ (cơ sở dữ liệu, ảnh, lịch sử), sao chép qua USB hoặc chuyển sang máy khác. Trên máy mới, cài ứng dụng và chọn **Khôi phục từ gói**; thao tác này thay thế dữ liệu sau xác nhận, không hợp nhất hai kho.

Sao lưu cloud là bản bổ sung qua thư mục Google Drive/OneDrive/Dropbox: app ghi gói lúc thoát hoặc khi bấm **Sao lưu ngay**, giữ 7 bản theo ngày và thay bản cùng ngày. Phần mềm cloud tải tệp lên; ứng dụng không xác nhận được việc tải lên đã hoàn tất. Không đặt cơ sở dữ liệu đang làm việc trực tiếp vào thư mục cloud. Bản sao tự động vào thư mục cloud chưa mã hóa; có thể xuất gói có mật khẩu để tự lưu lên cloud.

```bash
git clone https://github.com/theanh10806/personal-warehouse
cd personal-warehouse
pip install -e ".[all]"        # hoặc chỉ: pip install -e .
personal-warehouse             # hoặc: python -m personal_warehouse

### Giao diện

Mặc định app mở giao diện web (HTML/CSS/JS) trong một cửa sổ riêng nhờ `pywebview` (Windows dùng WebView2).
- `personal-warehouse --browser`: chạy cùng giao diện đó trong trình duyệt thường (không cần pywebview), tiện để thử.
- `personal-warehouse --tk`: giao diện Tkinter cũ. App tự dùng bản này nếu chưa cài `pywebview`.
- Mã giao diện nằm ở `src/personal_warehouse/webui/static/` (`index.html`, `app.css`, `app.js`); cầu nối với dữ liệu ở `webui/api.py`.
```

Thư viện tùy chọn: `openpyxl` (xuất Excel), `pillow` (xem ảnh), `qrcode[pil]` (tem QR),
`opencv-python` (quét bằng camera/ảnh). Thiếu thư viện nào thì chỉ tính năng đó bị tắt.

## Dành cho người phát triển / phát hành

### Thiết lập một lần
1. Tạo repo công khai `theanh10806/personal-warehouse` và đẩy mã lên nhánh `main`.
2. `GITHUB_REPO` đã được cấu hình thành `theanh10806/personal-warehouse` trong bản phát hành này.
3. Trong repo: **Settings → Actions → General → Workflow permissions** chọn *Read and write permissions*.

### Mỗi lần ra bản mới
1. Sửa code, chạy `python -m pytest`.
2. Tăng `__version__` trong `src/personal_warehouse/__init__.py` (ví dụ `3.1.0`).
3. Thêm mục `## [3.1.0] - ngày` vào `CHANGELOG.md` (nội dung này thành ghi chú phát hành, hiện trong hộp thoại cập nhật).
4. Commit, rồi:
   ```bash
   git tag v3.1.0
   git push origin main --tags
   ```
5. GitHub Actions tự chạy test, build `.exe`, tạo bộ cài và đăng lên Releases. Người dùng nhận thông báo lần mở app tiếp theo.

Workflow từ chối phát hành nếu tag không khớp `__version__`. Tag có dấu gạch (`v3.1.0-beta`) được đăng là pre-release và **không**
gây thông báo cho người dùng.

### Build thủ công trên Windows
```powershell
powershell -ExecutionPolicy Bypass -File packaging\build.ps1
```
Cần Python 3.9+; cài thêm [Inno Setup 6](https://jrsoftware.org/isinfo.php) nếu muốn tạo bộ cài (kết quả ở `Output\`).

### Cấu trúc mã nguồn

Ba lớp, phụ thuộc một chiều: `ui` → `core` → `config`; `i18n` dùng được ở mọi lớp. Các lớp ngoài `ui` **không bao giờ** import
`tkinter` (có test bảo vệ), nên logic có thể kiểm thử và tái sử dụng mà không cần giao diện.

```
src/personal_warehouse/
  config.py            hằng số, đường dẫn dữ liệu (đổi bằng PW_DATA_DIR)
  settings.py          settings.json (ngôn ngữ, giao diện, tùy chọn cập nhật)
  updater.py           kiểm tra bản mới trên GitHub Releases
  main.py              khởi động: cài đặt, CSDL, mở cửa sổ

  core/                logic nghiệp vụ, không có giao diện
    database.py        kết nối SQLite, tạo bảng, nâng cấp CSDL, sao lưu
    stock.py           nhập/xuất/điều chỉnh tồn kho, tìm hàng từ mã quét
    formatting.py      định dạng tiền/số, mã vị trí, tên hiển thị
    barcode.py         mã vạch Code 128
    labels.py          trang in tem QR / mã vạch (HTML)
    scanning.py        đọc mã từ ảnh/camera (OpenCV, pyzbar)
    exporter.py        xuất Excel / CSV
    history.py         nhật ký thay đổi + hoàn tác, thùng rác ảnh
    transfer.py        gói .pwbak: xuất / khôi phục / đồng bộ thư mục online
    translator.py      dịch tên hàng sang tiếng Ả Rập (online)

  i18n/                ngôn ngữ (vi / en / ar)
    core.py            bảng dịch, ngôn ngữ hiện tại, tr()
    strings/           mỗi tính năng một file: common, dashboard, inventory, item_form,
                       movements, locations, scan, labels, export, settings

  ui/                  giao diện Tkinter
    app.py             cửa sổ chính, ghép các trang lại với nhau
    theme.py           bảng màu sáng/tối, font
    widgets.py         card, label, button, bảng, bộ chuyển trang
    dialogs.py         hộp thoại (chọn kiểu tem)
    pages/             mỗi trang một file: dashboard, inventory, item_form, movements,
                       locations, scan, settings
    features/          hành động dùng chung: labels (in tem), updates, data_tools (xuất/sao lưu)

tests/                 pytest, chạy được không cần Tk (ui được test bằng Tk giả, xem conftest.py)
packaging/             PyInstaller + Inno Setup + trích ghi chú phát hành
.github/workflows/     ci.yml (test), release.yml (build + phát hành khi push tag)
```

### Muốn sửa / thêm gì thì vào đâu

| Việc cần làm | Nơi sửa |
|---|---|
| Sửa một câu chữ hoặc thêm câu mới | `i18n/strings/<tính năng>.py` (đủ 3 ngôn ngữ, có test kiểm tra) |
| Thêm ngôn ngữ thứ 4 | `LANGS` trong `i18n/core.py`, rồi thêm giá trị thứ 4 vào mọi `_t(...)` |
| Đổi quy tắc tồn kho / cách quét mã | `core/stock.py` |
| Thêm cột vào bảng hàng | `init_db()` trong `core/database.py` (dùng `_add_column`), tăng `SCHEMA_VERSION` trong `config.py` |
| Đổi giao diện một trang | `ui/pages/<trang>.py` |
| Đổi màu / font | `ui/theme.py` |
| Thêm trang mới | tạo `ui/pages/<ten>.py` (class mixin có `_build_<ten>` và `refresh_<ten>`), thêm vào danh sách kế thừa và `_build`/`_build_sidebar` trong `ui/app.py`, thêm file chữ trong `i18n/strings/` |
| Thêm định dạng xuất | `core/exporter.py` (logic) + `ui/features/data_tools.py` (nút/hộp thoại) |

Quy ước cần giữ để người dùng cũ không mất dữ liệu: **không đổi `AppId` trong `installer.iss`**, và mọi thay đổi cấu trúc
bảng phải thêm cột bằng `_add_column` trong `init_db()` (không xóa/đổi tên cột) rồi tăng `SCHEMA_VERSION`.

## Giấy phép
MIT, xem `LICENSE`.
