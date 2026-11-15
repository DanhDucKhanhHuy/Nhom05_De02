# Biên bản kiểm chứng

## Cập nhật CN2 – 15/11/2026

- `python -m scripts.check_rules`: đạt; 27 luật, bốn mã nguồn, từ vựng, luật chẩn đoán/khuyến nghị, chuỗi nhiều bước và kiểm tra chu trình hợp lệ.
- `python -m pytest tests/test_rules.py -q`: 17 passed.
- `python -m pytest`: 19 passed, 9 xfailed. Cả 9 xfail đều thuộc CN1 đang triển khai; không còn xfail CN2.
- `python -m ruff check .`: đạt.
- `python demo.py`: mã thoát 0; nêu rõ chẩn đoán tích hợp chưa cài, suy diễn luật CN2 chạy riêng được.
- Kiểm tra thủ công `rules.json` với `sources.json`, `vocabulary.json` và `docs/nguon_tri_thuc.md`: DO01/DO03 đã trỏ đúng nguồn; DN04/DN06/DN08 đã sửa thuật ngữ và ý nghĩa; BL02/BL03 khớp nội dung S2; mỗi bệnh có luật khuyến nghị riêng.
- Bốn nguồn đang dùng là S1–S4. S2 và S3 không ghi năm xuất bản; trường năm để `null`, phần ghi chú nói rõ thiếu năm. S2 dùng trang HTML.
- Các kiểm tra trên không chứng minh nội dung tri thức đã được chuyên gia địa phương chứng nhận hoặc hiệu quả chẩn đoán trên dữ liệu thật.

## Trạng thái các phần khác

CN2 hiện có suy diễn tiến/lùi và dữ liệu luật, nhưng hàm `diagnose` chưa được tích hợp; mạng Bayes vẫn do TV3 phụ trách. CN1, CNN và giao diện vẫn đang phát triển. Dự đoán CNN còn là bản giả. Các test xfail ở module khác phản ánh phần chưa triển khai tương ứng; test CN2 không còn xfail.

Kiểm chứng này chạy trên Python có sẵn trong môi trường làm việc, không xác nhận tương thích Python 3.10/3.11 hay cài đặt TensorFlow. Trước khi tuyên bố CN2 hoàn tất, cần một thành viên khác rà soát luật, nguồn và thay đổi hợp đồng dữ liệu.
