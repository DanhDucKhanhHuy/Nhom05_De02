# Kiểm thử Chức năng 2 trên Python đang có của máy

Ngày chạy: 18/11/2026. Thư mục thực thi: Nhom05_De02.

## Môi trường và phạm vi

- Dùng Python 3.14.3 64-bit hiện có; tạo riêng `.venv-cn2-py314`.
- Không sửa mã nguồn, luật, test hoặc requirements trong đợt kiểm thử này.
  Các thay đổi đã có trước đợt chạy được giữ nguyên.
- Cài `requirements-dev.txt`, `pgmpy==0.1.25`, `requests==2.32.3`
  và các phụ thuộc của chúng. Danh sách phiên bản thực tế: `installed.txt`.
- Đây là môi trường kiểm thử CN2, không phải môi trường đầy đủ của mọi chức năng.
- Cài đúng toàn bộ `requirements.txt` chưa thực hiện được: bước dry-run
  thất bại tại `tensorflow==2.16.1` vì không có bản phân phối phù hợp với
  Python 3.14/Windows đang chạy. Chi tiết: `requirements_full.txt`.
- `pip check`: No broken requirements found. Kết quả này áp dụng cho các
  package đã cài, không có nghĩa toàn bộ requirements của repo đã được đáp ứng.

## Kết quả chạy thật

- Toàn bộ pytest: **200 passed, 9 xfailed**, không có failed/error/skipped,
  thời gian pytest báo 30.62 giây. Chín xfail thuộc CN1 chưa triển khai.
  Lưu tại `full.txt`, `full.xml`.
- Nhóm test tiến/lùi/chi tiết suy diễn/luật: **87 passed**; `engine.txt`.
- Test pgmpy trước đây bỏ qua nay đã thực sự chạy đạt, gồm `check_model`,
  tổng cột CPD và đối chiếu sáu truy vấn trong ba cặp với phép liệt kê.
- Ruff: All checks passed; `ruff.txt`.
- Kiểm tra luật: 28 luật hợp lệ; `check_rules.txt`.
- Demo chạy thành công, giải thích dùng backend `pgmpy – VariableElimination`.
  Predictor vẫn GIẢ, kết luận chưa đủ chắc; `demo.txt`.

## Kiểm tra bổ sung độc lập

- Nạp và kiểm tra trường luật, ID, mã nguồn và thuộc tính/giá trị từ vựng.
- 30 kịch bản với đủ dữ kiện: mỗi kịch bản đảo thứ tự luật 5 lần;
  bao đóng không đổi, dữ kiện đầu vào không bị sửa, vết không lặp ID luật,
  suy diễn lại đạt điểm cố định. Facts rỗng không sinh kết luận.
- 90 đối chiếu đích bệnh giữa suy diễn tiến và lùi đều khớp; không cần hỏi
  khi dữ kiện đã đầy đủ. Chi tiết: `independent_checks.txt`.
- Mạng pgmpy có 22 nút, 50 cột CPD; `check_model()` trả True,
  mỗi cột cộng bằng 1. Truy vấn độc lập khớp phép liệt kê trong sai số 1e-8.
- Ba cặp bằng chứng Có/Không cho triệu chứng đặc trưng làm hậu nghiệm bệnh
  thay đổi đúng chiều trong mô hình:
  - Đạo ôn / VetHinhThoi: 0.8838776754 / 0.0847036754.
  - Bạc lá / BacVetUngNuoc: 0.9191991681 / 0.1215057443.
  - Đốm nâu / DomTronBauDuc: 0.9052980005 / 0.1048509659.
- Không nạp TensorFlow trong kiểm tra Bayes độc lập. Chi tiết:
  `pgmpy_independent.json`. Các con số trên kiểm tra tính toán theo CPD hiện có,
  không phải độ chính xác hoặc xác suất đã được hiệu chuẩn ngoài thực địa.
- Không tìm thấy import experta/durable_rules/pyke/clips/clipspy/rule_engine
  trong src/rules bằng phân tích AST; `independent_inventory.txt`.
- Có 20 dòng ảnh và đủ 20 file, mỗi lớp 5 ảnh. Cả 20 dòng còn trống nguồn,
  giấy phép, ngày và người thu thập trong nguon.csv. Nhãn thực tế chưa được
  kiểm chứng độc lập; chỉ đối chiếu nhãn thư mục/danh mục.

## Kết luận và việc còn thiếu

**Đạt kiểm thử kỹ thuật CN2 trong phạm vi đã chạy trên Python 3.14.3;
CHƯA ĐẠT nghiệm thu toàn bộ Chức năng 2.**

1. Sửa phương án quản lý phụ thuộc để cài tái lập trên Python 3.14:
   requirements hiện tại không cài nguyên bộ được. Không tự nâng phiên bản
   hoặc đổi code để che lỗi trong đợt kiểm tra này.
2. Predictor còn là bản giả; chưa đánh giá ảnh thật, CNN thật hoặc độ chính xác
   toàn luồng. Tích hợp CNN thật thuộc phần việc phối hợp với CN3.
3. Bổ sung hồ sơ nguồn/quyền sử dụng và căn cứ nhãn cho ảnh đã có.
4. CPD và ngưỡng 0.60 là giả định chưa hiệu chuẩn. Cần biên bản duyệt nếu
   nghiệm thu như mô hình minh họa; cần đánh giá dữ liệu riêng nếu tuyên bố
   hiệu quả thực tế.
5. Theo hồ sơ tri thức: còn giới hạn DN10 và truy cập nguồn S3/S6.
   Đợt này chưa mở lại nguồn, không coi việc kiểm tra tham chiếu là đã
   xác nhận nguồn hỗ trợ toàn bộ nội dung.
6. Cần người khác rà soát độc lập và duyệt các giới hạn còn lại.

## Chạy lại

Trong PowerShell tại Nhom05_De02:

```powershell
$testTemp = Join-Path $env:TEMP ('bacsi-cn2-' + [guid]::NewGuid().ToString('N'))
.\.venv-cn2-py314\Scripts\python.exe -m pytest -q -p no:cacheprovider --basetemp $testTemp
.\.venv-cn2-py314\Scripts\python.exe -m ruff check .
.\.venv-cn2-py314\Scripts\python.exe -m scripts.check_rules
.\.venv-cn2-py314\Scripts\python.exe demo.py
```

Không cần kích hoạt môi trường hoặc thay Python mặc định. Nếu cần dựng lại
môi trường kiểm thử cùng phiên bản, dùng Python 3.14.3 tạo venv mới rồi cài
danh sách `artifacts/kiem_thu_cn2_py314_20261118/installed.txt`.

Không commit/push/tag.
