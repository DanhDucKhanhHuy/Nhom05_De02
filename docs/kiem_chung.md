# Biên bản kiểm chứng TV3 – CN2

## Phạm vi

Đã rà soát và chỉnh sửa phần xác suất trong `src/rules/bayes.py`,
`src/rules/ket_hop.py`, tài liệu `docs/cau_hoi/Q2_xac_suat.md` và bổ sung
`tests/test_tv3_probability.py`. Các module ngoài phạm vi bảy ưu tiên được giữ
nguyên.

## Kết quả kiểm tra trong môi trường thực thi hiện tại

- `python -m pytest -q` (16/11/2026): **141 passed, 1 skipped, 9 xfailed**.
- 1 test bị skip là kiểm thử tích hợp pgmpy vì môi trường này chưa có `pgmpy`;
  việc cài `pgmpy==0.1.25` không thực hiện được do môi trường không truy cập được
  PyPI (DNS/network). Test được viết để yêu cầu đúng phiên bản `0.1.25`, gọi
  `check_model()`, kiểm tra tổng từng cột CPD và so sánh truy vấn pgmpy với phép
  liệt kê độc lập trên ba bộ bằng chứng khi chạy trong môi trường đã cài thư viện.
- 9 xfail là các kiểm thử thuật toán tìm kiếm chưa triển khai trong `tests/test_search.py`;
  không thuộc phần xác suất TV3.
- `python -m scripts.check_rules`: đạt, 28 luật, nguồn, mô tả/câu hỏi, từ vựng và chuỗi suy diễn hợp lệ.
- `python -m ruff check .`: đạt sau khi sắp xếp import kiểm thử.
- `python demo.py`: chạy thành công; đầu ra CNN ghi rõ là giả, demo không gọi Bayes.
- `python -m src.rules.bayes --khong-pgmpy`: chạy thành công.
- `python -m src.rules.ket_hop --khong-pgmpy`: chạy thành công; ví dụ mặc định dùng
  top-3 giả lập và ba thuộc tính từ vocabulary.
- `python -m compileall -q src tests`: đạt.

Lưu ý: môi trường thực thi hiện tại dùng Python 3.13 và không có Ruff/pgmpy.
Dự án khai báo pgmpy==0.1.25 và khuyến nghị Python 3.10–3.11; cần chạy lại
kiểm thử pgmpy trong môi trường nhóm có đúng Python và dependency. Không ghi
nhận kiểm thử pgmpy là đã chạy thành công khi chưa thực hiện được.

## Đối chiếu bảy ưu tiên

1. **Bằng chứng TV2–TV3:** TV3 nhận trực tiếp các thuộc tính trong
   `vocabulary.json`. Chỉ ánh xạ khi nghĩa của thuộc tính và trạng thái Bayes
   trùng nhau; “không âm u và có sương sớm” không thành trời khô, “không thừa
   đạm” không thành đạm thấp. Triệu chứng không khớp trạng thái Bayes được bỏ
   qua có ghi chú. `chua_biet`, thuộc tính chưa ánh xạ và mã lạ có thông báo
   riêng. Mâu thuẫn cùng nút bị loại không phụ thuộc thứ tự nhập.
2. **Biểu diễn bệnh:** ba biến bệnh trong mạng vẫn cho phép đồng mắc. Bốn lớp
   đầu ra là các trạng thái không bệnh hoặc đúng một bệnh; khối lượng đồng mắc
   được trả riêng. Xác suất lá khỏe đồng thời lấy từ trạng thái
   `(khong, khong, khong)` của phân phối đồng thời, không nhân xác suất biên.
3. **CNN–Bayes:** dùng tích `P_CNN × P(Bệnh|điều kiện)` rồi chuẩn hóa. Có tham số
   `prior_cnn` để hiệu chỉnh prior huấn luyện; mặc định giả định tập CNN cân bằng.
   Giả định độc lập có điều kiện và nguy cơ đếm trùng được ghi trong code/Q2.
4. **Chưa đủ chắc:** ngưỡng mặc định 0.60; dùng điểm quyết định giảm theo
   xác suất đồng mắc, dùng `>=` để kết luận. Hòa hoặc điểm dưới ngưỡng trả
   `ket_luan=None`. Có test dưới, bằng, trên ngưỡng và hòa.
5. **Ca biên:** kiểm tra Top-3, mã lớp, trùng lớp, xác suất không hữu hạn/ngoài
   miền, tổng không hợp lệ, bằng chứng rỗng/chưa biết/mâu thuẫn/không hỗ trợ và
   tích CNN–Bayes bằng 0.
6. **pgmpy:** mã dựng mô hình, `check_model()`, kiểm tra CPD và test đối chiếu
   ba truy vấn đã có. Chưa thể xác nhận runtime pgmpy trong môi trường hiện tại
   do thiếu package và không có mạng; test sẽ chạy khi cài đúng phiên bản.
   `predict_top3` giả được kiểm tra mà không import TensorFlow.
7. **CPD/Q2:** code khai báo nguồn định tính theo từng nút; Q2 thống nhất với
   công thức, cách phân lớp, ngưỡng, bằng chứng, nguồn S1–S4 và ví dụ đầu-cuối.
   CPD vẫn là giả định, chưa hiệu chuẩn thực nghiệm.

## Giới hạn còn lại

- CNN trong `src/model/predict.py` vẫn là stub, không phải mô hình ảnh đã huấn luyện.
- Các con số CPD và ngưỡng 0.60 chưa được hiệu chuẩn bằng dữ liệu đồng ruộng.
- Cần cài đúng dependency trong Python 3.10–3.11 của nhóm, chạy test pgmpy,
  rồi mới xác nhận ưu tiên 6 hoàn tất về mặt thực thi.
- S2 có ngày đăng 11/07/2012; S3 là ấn phẩm năm 2014. Không dùng nguồn cũ thiếu metadata làm nguồn chuẩn cho các luật này.
