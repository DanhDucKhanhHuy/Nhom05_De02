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
