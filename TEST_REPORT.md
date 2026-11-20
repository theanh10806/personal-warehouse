# Báo cáo kiểm thử ngày 20/11/2026

## Rà soát trước phát hành: lịch sử và nút chức năng

- Toàn bộ Python: **170 passed**, một cảnh báo anyio; JUnit: `.pytest_tmp/prerelease-results.xml`.
- JavaScript: **4 passed**, kiểm tra cú pháp thành công. Đã thêm bước JavaScript vào CI và workflow phát hành; chưa chạy các workflow từ GitHub trong lượt này.
- Edge thật: mở 9 trang Kho hàng, Thêm/Sửa, Nhập/Xuất, Quét mã, Sơ đồ, Lịch sử, Giới thiệu, Cài đặt, Tổng quan; thực hiện xác nhận Undo rồi Redo trên kho mẫu riêng `.pytest_tmp/release-demo-1`.
- Đã xem ảnh lịch sử `.pytest_tmp/history-release.png`; kiểm tra chuyển trang nhanh sau sửa lỗi focus không ghi nhận JavaScript exception.
- Đã kiểm tra liên kết giữa các action tĩnh của nút và trình xử lý; đây không phải bằng chứng đã bấm mọi nút và mọi tổ hợp trạng thái.
- Sắp xếp lịch sử theo ID giảm dần, không theo chuỗi thời gian; ID phân biệt các thao tác cùng giây. Thêm mô tả giới hạn 300 dòng, tham chiếu mục gốc và nhãn Undo/Redo riêng.
- Sửa: Undo tạo hàng tồn đầu 0 phải từ chối khi đã nhập hàng; Redo xóa sau khôi phục đối chiếu đầy đủ giao dịch; Undo lấy khóa ghi trước khi đọc để tránh thực thi hai lần đồng thời.
- Bản ghi gốc vẫn thể hiện đã bị đảo ngược sau Redo: kết quả hiện tại nằm ở dòng mới liên kết với nó; không sửa lại lịch sử cũ để giả vờ Undo chưa từng xảy ra.
- Chưa build/cài đặt EXE, thử nâng cấp trên Windows sạch, camera/USB/máy in hoặc cập nhật thật. Chưa tăng version, tạo tag, push hay publish GitHub Release. Phải hoàn tất các bước nghiệm thu bộ cài trong RELEASE_CHECKLIST.md trước khi phát hành.

## Kiểm tra bổ sung sơ đồ kho trên Edge

Đã chạy trình duyệt Edge headless thật trên kho mẫu ở localhost; kiểm tra 24 ô, mở chi tiết A1, tìm bằng mã vạch, không có kết quả, lọc cảnh báo/vị trí trống và thêm hàng tự điền A1. Không lưu mặt hàng mới trong thử nghiệm này.

Đã chụp và xem ảnh desktop 1440 px và màn hình nhỏ 390 px, kiểm tra theme tối. Phát hiện sidebar/thanh công cụ gây tràn ngang trên màn hình nhỏ và sửa CSS; chạy lại đạt, không có JavaScript exception trong các thao tác đã thử. Ảnh lưu tại `.pytest_tmp/map-desktop.png` và `.pytest_tmp/map-mobile.png`.

Kiểm tra này bổ sung cho phạm vi bên dưới; chưa thay thế kiểm thử cửa sổ pywebview, thiết bị thật hoặc toàn bộ tương tác giao diện.

## Kết quả

- Windows, Python 3.14.3: **164 passed**, không có failed/skipped, 33,96 giây.
- Một cảnh báo từ plugin anyio về API pytest sắp bị loại bỏ.
- `node --check src/personal_warehouse/webui/static/app.js`: thành công.
- `git diff --check`: không có lỗi khoảng trắng.
- Kết quả máy đọc được: `.pytest_tmp/scenarios-results.xml`.

## Dữ liệu mẫu

Đường dẫn: `demo-data/warehouse-20261120`, tách khỏi dữ liệu sử dụng thực tế.

- 96 mặt hàng, đủ 24 vị trí A1–C8, 4 tình trạng và 8 đơn vị.
- 144 biến động: tồn đầu kỳ, nhập, xuất và điều chỉnh.
- Có tồn bằng 0, tồn thấp, số lượng lẻ, tên tiếng Việt/Ả Rập, ký tự đặc biệt và ảnh PNG.
- `Export/demo.csv`, `Export/demo.xlsx`, `Export/demo.pwbak`, `Backup/demo.db`.
- SQLite integrity_check: ok. CSV/Excel được đọc lại để đối chiếu số hàng; bản sao DB và gói dữ liệu được xác minh.

Tạo kho mẫu mới (thư mục đích phải trống):

```powershell
python scripts/create_demo.py demo-data/another-demo
```

Mở kho mẫu bằng tiến trình riêng, không đổi biến môi trường của PowerShell hiện tại:

```powershell
python -c "import os; os.environ['PW_DATA_DIR']=os.path.abspath('demo-data/warehouse-20261120'); from personal_warehouse.main import main; main(['--browser'])"
```

Cần đóng phiên Personal Warehouse đang chạy trước khi mở kho mẫu vì ứng dụng có khóa một phiên.

## Phạm vi đã chạy

| Nhóm | Kiểm tra |
|---|---|
| Mặt hàng | Tạo/sửa, giữ nguyên tồn khi sửa thông tin, trùng hàng/mã, xác nhận, lọc/sắp xếp, lưu trữ và xóa |
| Đầu vào | 28 tổ hợp trường số và dữ liệu sai; kiểm tra không tạo hàng, biến động hoặc lịch sử khi bị từ chối |
| Sổ kho | 300 thao tác nhập/xuất/điều chỉnh có seed cố định, đối chiếu mô hình độc lập và chuỗi trước/sau |
| Đồng thời | 24 yêu cầu xuất trên tồn 10: đúng 10 thành công, tồn cuối 0 |
| Giao dịch | Lỗi ghi lịch sử hoàn tác cả tồn và biến động; tiến trình thoát đột ngột không giữ cập nhật chưa commit |
| Một phiên | Hai tiến trình tranh khóa; tiến trình sau chạy được khi tiến trình giữ khóa bị kill |
| Quét | Tra mã hàng, mã riêng, payload QR, số thứ tự; tạo và giải mã ảnh QR thật, ảnh không hợp lệ |
| Lịch sử | Hoàn tác/sửa lại, xóa và lấy lại ảnh, từ chối hoàn tác ghi đè thay đổi mới |
| Sao lưu | Sao lưu xác minh, lưu giữ bản cũ, gói mã hóa/sai mật khẩu, gói hỏng/phiên bản mới/path traversal |
| Khôi phục | Bản an toàn, rollback khi thay DB lỗi, nhật ký phục hồi sau tiến trình thoát đột ngột |
| Nâng cấp | Nâng schema cũ; chặn khi sao lưu lỗi; snapshot gồm dữ liệu đã commit còn trong WAL |
| Cấu hình | Giữ khóa không liên quan, thay tệp lỗi không phá tệp cũ |
| Giao diện | API với 3 ngôn ngữ × 2 theme; Tk smoke/layout bằng đối tượng giả; HTTP bridge thật trên localhost |
| Khác | Dashboard, bản đồ vị trí, CSV/Excel, HTML tem/mã vạch, đồng bộ thư mục, cập nhật giả lập, giới thiệu/góp ý |

## Giới hạn

Không thể liệt kê hoặc chứng minh mọi tình huống có thể xảy ra. Bộ kiểm thử không thay thế thử nghiệm thiết bị và nghiệm thu giao diện.

- Chưa thao tác tự động trên trình duyệt/WebView2 thật; kiểm tra JavaScript chỉ là cú pháp.
- Chưa thử camera, máy quét USB, máy in và căn chỉnh tem trên giấy thật.
- Chưa tải/cài bản cập nhật thật, gửi email, gọi dịch online hoặc xác minh đồng bộ cloud từ đầu đến cuối.
- Chưa ngắt điện vật lý, mô phỏng hỏng ổ cứng hoặc kiểm thử tải dài ngày.
- Dừng tiến trình được thử bằng os._exit/kill; không tương đương mất điện của máy.
- Chưa đo phần trăm coverage hoặc xác nhận mọi nhánh chương trình đều được thực thi.

Chạy lại toàn bộ:

```powershell
python -m pytest -q --basetemp=.pytest_tmp/manual-run --tb=short --junitxml=.pytest_tmp/manual-results.xml
```

Chỉ dùng một thư mục basetemp dành riêng cho mỗi lần chạy đồng thời; pytest có thể xóa nội dung thư mục này.
