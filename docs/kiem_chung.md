# Biên bản kiểm chứng TV3 – mô hình Bayes đa bằng chứng

## Phạm vi thay đổi

Chỉ thay đổi phần xác suất và các kiểm thử trực tiếp phụ thuộc vào hợp đồng bằng chứng Bayes:
- `src/rules/bayes.py`: thiết kế lại cấu trúc mạng, nút quan sát riêng, ánh xạ thuộc tính/mã cũ, CPD và truy vấn.
- `src/app/thoi_tiet.py`: công bố ngưỡng chuyển số đo thành trạng thái thời tiết; không suy từ thời tiết sang tình trạng cây/ruộng.
- `src/rules/ket_hop.py`: giữ nguyên bộ kết hợp CNN–Bayes hiện có; kiểm thử tích hợp được cập nhật theo evidence node mới.
- `tests/test_tv3_probability.py`: kiểm thử mô hình và hợp đồng mới.
- `tests/test_knowledge_regressions.py`, `tests/test_rules.py`: chỉ cập nhật các kiểm thử đang khẳng định ánh xạ Bayes cũ, không sửa logic hệ luật hoặc nội dung luật của thành viên khác.
- `docs/cau_hoi/Q2_xac_suat.md`: cập nhật cấu trúc, thuộc tính hỗ trợ, CPD, công thức và ví dụ.

Không chỉnh sửa `rules.json`, `vocabulary.json`, thuật toán tìm kiếm, CNN, giao diện hoặc các module hệ luật khác.

## 1. Kết quả kiểm thử trong môi trường hiện tại

Lệnh `python -m pytest -q`:
- **154 passed**
- **1 skipped**: kiểm thử tích hợp pgmpy do môi trường chạy hiện tại không có package `pgmpy`.
- **9 xfailed**: các ca tìm kiếm được đánh dấu chưa triển khai từ trước, không thuộc phạm vi TV3.
- **0 failed**

Kiểm thử riêng `tests/test_tv3_probability.py`:
- **34 passed**
- **1 skipped**: kiểm thử pgmpy chưa chạy do thiếu package trong môi trường hiện tại.
- **0 failed**

Do thiếu pgmpy trong môi trường thực thi của biên bản này, không ghi nhận `check_model()` và đối chiếu pgmpy là đã chạy thành công ở đây. Test tích hợp được giữ bắt buộc đúng `pgmpy==0.1.25`; cần chạy lại trên máy thành viên đã cài dependency này để xác nhận runtime.

## 2. Đối chiếu yêu cầu

1. **Nút triệu chứng riêng:** đã bỏ `TrieuChung` đa trạng thái. Các dấu hiệu hỗ trợ có node nhị phân riêng, cho phép đồng thời nhiều bằng chứng.
2. **Bạc lá:** đã hỗ trợ vệt úng nước, vị trí bắt đầu ở chóp, màu vàng-trắng, mép lượn sóng và héo/cuộn; từng thuộc tính được công bố ở Q2 và `ANH_XA_THUOC_TINH`.
3. **Ánh xạ đúng nghĩa:** `co/khong` vào hai trạng thái cùng node; `chua_biet`, `None` và dữ kiện thiếu không tạo evidence. `False` và chuỗi `"False"` là phủ định, không phải dương tính.
4. **Bỏ ánh xạ gần nghĩa:** tâm xám-khô không thành hình thoi; `thua_dam=khong` không thành đạm thấp; `am_u_va_suong_som=khong` không thành thời tiết khô; vệt bạc lá không thành dấu hiệu đạo ôn.
5. **Mã cũ:** chỉ `TrieuChung=dom_tron` được chuyển thành `DomTronBauDuc=co` theo định nghĩa tương đương; các trạng thái `vet_thoi`, `chop_la_kho`, `khong` không tự chuyển đổi. `BonDam=cao/thap` bị bỏ qua vì không tương đương chính xác với vượt/không vượt khuyến cáo.
6. **CPD và phụ thuộc:** mọi node có giả định và provenance. Dấu hiệu chi tiết là node con của dấu hiệu hình thái chính ở nhóm bạc lá, đốm nâu và đạo ôn. Các con số CPD vẫn là giả định định tính, không phải xác suất đã hiệu chuẩn.
7. **Thời tiết:** số đo độ ẩm/mưa chỉ được chuyển thành `ThoiTiet` theo ngưỡng được ghi rõ trong `src/app/thoi_tiet.py`. Không suy ra thiếu nước ruộng, héo cây hoặc triệu chứng từ số đo thời tiết.
8. **pgmpy:** test yêu cầu đúng version `0.1.25`, gọi `check_model()`, kiểm tra tổng từng cột CPD và đối chiếu ba cặp truy vấn đối lập với phép liệt kê độc lập. Chưa xác nhận runtime trong môi trường biên bản vì thiếu package.
9. **Q2 và quyết định:** công thức CNN–Bayes, ví dụ đa triệu chứng và sự khác biệt giữa posterior với `do_tin_cay_dieu_chinh` đã được cập nhật.

## 3. Cách xác nhận pgmpy trên máy nhóm

Trong môi trường Python dự án:

```bash
python -m pip install pgmpy==0.1.25
python -c "import pgmpy; print(pgmpy.__version__)"
python -m pytest tests/test_tv3_probability.py -q
```

Kết quả version phải là `0.1.25`. Test phải chạy qua phần `test_pgmpy_025_and_three_opposing_query_pairs_match_independent_enumeration`, không được hiển thị `skipped`. Nếu lỗi, lưu nguyên traceback để sửa đúng tương thích runtime.

## 4. Giới hạn

- CNN trong `src/model/predict.py` hiện vẫn là stub.
- CPD và prior chưa được ước lượng từ bộ dữ liệu đồng ruộng có nhãn.
- Ngưỡng quyết định 0.60 chưa được hiệu chuẩn trên tập validation.
- Danh sách thuộc tính được Bayes hỗ trợ chỉ là tập con công bố ở Q2; thuộc tính còn lại không bị xóa khỏi vocabulary/hệ luật, chỉ không tham gia truy vấn Bayes.

## 5. Kiểm chứng tích hợp ngày 18/11/2026

- Python 3.14.3; pytest với cache tắt và basetemp riêng: **199 passed, 1 skipped, 9 xfailed**, không có failed/error. Skip vì thiếu pgmpy; xfail thuộc CN1.
- `python -m ruff check .`: All checks passed.
- `python -m scripts.check_rules`: 28 luật hợp lệ.
- Bổ sung test ánh xạ phủ định/không rõ, top-3 sai, đồng thuận/bất đồng luật và CNN–Bayes, phiên hỏi dùng chung và predictor giả.
- Đã nối diagnose với fusion và diagnose_image; không đưa kết luận suy ra vào bằng chứng quan sát. CNN giả luôn trả kết luận chưa đủ chắc.
- Review giữ nguyên số CPD, trạng thái/cấu trúc mạng, điều kiện/kết luận 28 luật, hợp đồng công khai và thuật toán tiến/lùi. Trích nguồn và diễn giải giả định được cập nhật.
- Danh mục ảnh có 20 dòng đối chiếu tên file; nguồn, giấy phép và người/ngày thu thập còn thiếu, không tự điền.
- Chưa kiểm chứng pgmpy, CNN thật, độ chính xác thực địa hoặc ngưỡng đã hiệu chuẩn. S3 đọc qua bản chỉ mục nhưng URL tải gốc 404; S6 chưa mở lại được. DN10 cần duyệt phạm vi thời điểm áp dụng.
- Kết quả xác nhận luồng code trong phạm vi test; chưa đủ để nghiệm thu toàn bộ Chức năng 2.

## 6. Cập nhật CN3-CNN ngày 19/11/2026

- Đã thay predictor số cố định bằng đường đọc ảnh RGB 224 × 224, nạp artifact
  `.keras` và kiểm tra đầu ra softmax theo bốn lớp chuẩn. `IS_STUB` chỉ hạ sau
  suy luận hợp lệ; ứng dụng báo chưa có mô hình khi artifact chưa tồn tại.
- Đã bổ sung chia dữ liệu theo lớp, gom ảnh byte trùng bằng SHA-256, pipeline
  augmentation chỉ cho train, CNN tự thiết kế, MobileNetV2/EfficientNetB0,
  huấn luyện lưu checkpoint và hàm đánh giá macro cùng ma trận nhầm lẫn.
- Dùng Python 3.11.9 và TensorFlow 2.16.1. Suite đầy đủ: **215 passed,
  9 xfailed**; `ruff check .`, `scripts.check_rules` và `python demo.py` đạt.
- Huấn luyện CNN tự thiết kế 14 epoch: test accuracy 0,6980, precision macro
  0,6888, recall macro 0,6730, F1 macro 0,6721.
- Huấn luyện MobileNetV2 ImageNet 20 epoch: test accuracy 0,9005, precision
  macro 0,8895, recall macro 0,8902, F1 macro 0,8893. Ma trận nhầm lẫn, chỉ số
  từng lớp, support, cấu hình và SHA-256 được ghi ở Q3 và JSON trong
  `artifacts/cn3/`.
- MobileNetV2 được chọn theo validation loss thấp nhất và lưu cục bộ tại
  `models/rice_leaf_classifier.keras` (SHA-256
  `a3c6dc43df0a237020e5fb67bb9826644b14f9dd4358c4547c8a689c28fb3898`). Smoke
  test nạp artifact, dự đoán `bac_la` đầu bảng với xác suất 0,8766 trên ảnh
  `BL_001.JPG`; top-3 đã tạo cho đủ 20 ảnh tại CSV artifacts.
- Các chỉ số test đo trên tập Mendeley đã chia độc lập; không phải độ chính
  xác thực địa. 20 ảnh ngoài tập dùng để thử dự đoán, nhãn thư mục và nguồn ảnh
  chưa được xác minh độc lập. Mô hình và ảnh không được commit. Trước nghiệm
  thu CN3, cần thành viên khác duyệt thay đổi và khi nộp phải kèm artifact hoặc
  liên kết tải được.
