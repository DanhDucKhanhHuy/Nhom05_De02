# Công việc sửa tri thức CN2

- [x] Đọc hướng dẫn, hợp đồng, hiện trạng và kiểm tra không có kế hoạch dở dang.
- [x] Ghi kế hoạch theo phạm vi người dùng đã yêu cầu thực hiện.
- [x] 1. RED/GREEN: bỏ ánh xạ bạc lá sai, giữ các bằng chứng hợp lệ khác.
- [x] 2. RED/GREEN: DO07 hỏi quan sát, chỉ gợi ý cần kiểm tra.
- [x] Checkpoint: chạy toàn bộ test sau bước 1–2.
- [x] 3. Làm rõ phủ định đạm và thuật ngữ tâm đốm, kiểm tra hồi quy.
- [x] 4. Đồng bộ tài liệu tri thức/Q2 và tái hiện ví dụ số.
- [x] 5. Tra cứu năm S2/S3 và phạm vi BL06; lưu kết quả hoặc đánh dấu thiếu.
- [x] 6. Chạy pytest, Ruff, check_rules, demo và review diff cuối.

## Khoảng trống không tự điền

- [ ] Nút/CPD triệu chứng riêng cho Bayes: chưa có thiết kế/CPD đã duyệt.
- [ ] Năm S2/S3: cần bằng chứng chính thức.
- [x] Giai đoạn áp dụng BL06: S5 hỗ trợ chọn giống để gieo; không đặt lịch
  tháng/vụ cho địa phương khi chưa có nguồn.
- [ ] Kiểm chứng pgmpy: môi trường hiện tại chưa cài thư viện.

Không commit/push/tag. Không đụng ảnh và các tệp pyc có sẵn thay đổi.

## Kết quả thực thi ngày 17/11/2026

- Python 3.14.3; dùng `PYTHONDONTWRITEBYTECODE=1`, tắt cache pytest và dùng
  `--basetemp` UUID mới trong Temp cho những test cần thư mục tạm.
- Bước 1: RED 4 failed / 28 passed / 1 skipped; GREEN 32 passed / 1 skipped.
- Bước 2: RED 5 failed / 30 passed; checkpoint GREEN 148 passed / 1 skipped /
  9 xfailed. Test cũ yêu cầu chính ánh xạ/câu hỏi sai được cập nhật theo đặc tả;
  không bỏ test, skip hoặc xfail để che lỗi.
- Thêm 8 ca hồi quy trong `tests/test_knowledge_regressions.py`, gồm ba trạng
  thái câu trả lời và ví dụ số Q2. Việc sửa diễn giải tĩnh không cần vòng RED
  riêng; kiểm tra hồi quy liên quan đã chạy đạt.
- Cuối cùng: `python -m pytest -q -p no:cacheprovider --basetemp <Temp UUID>`:
  149 passed, 1 skipped (thiếu pgmpy), 9 xfailed (CN1 chưa triển khai).
- `python -m ruff check .`: All checks passed.
- `python -m scripts.check_rules`: 28 luật hợp lệ.
- `python demo.py`: chạy đạt với CNN giả và kết quả chưa đủ chắc.
- `python -m src.rules.ket_hop --khong-pgmpy`: chạy đạt, vệt úng nước được
  báo chưa hỗ trợ; điểm quyết định 23.08%, kết luận None.
- Review bằng AST và diff: NUT/CPD, hợp đồng, thuật toán tiến/lùi/diagnose và
  sources.json không đổi; chỉ điều kiện DO07 đổi, cả 28 trích nguồn giữ nguyên.
- Kiểm tra diff khoảng trắng với `cr-at-eol` đạt, không chuẩn hóa CRLF của repo.
- Đã mở lại trang chính thức S1/S2/S3; chưa có bằng chứng năm S2/S3 hoặc mùa vụ
  của BL06. Giữ null và ghi thiếu; không xem các khoảng trống này là hoàn tất.

## Đợt hoàn thiện hồ sơ theo yêu cầu tiếp theo

- [x] 7a. Đọc nguồn IARI: năm 2013 ở trích dẫn chuẩn, chọn hạt sạch bệnh để gieo
  ở trang in 28 / trang PDF 36. Chưa có bằng chứng năm xuất bản S2/S3.
- [x] 7b. Thêm nguồn bổ sung và ghi rõ phạm vi áp dụng BL06.
- [x] 8. Đối chiếu đủ 28 id với nội dung nguồn và giới hạn suy luận.
- [x] 9. Đồng bộ tài liệu, kiểm tra dữ liệu và chạy các lệnh nghiệm thu.

### Kết quả bổ sung hồ sơ

- Thêm S5: IARI, Technical Bulletin TB-ICN 109/2013; năm ở trích dẫn chuẩn
  PDF 4, giai đoạn chọn giống ở trang in 28 / PDF 36. Nguồn này không thay thế
  S2 và không xác nhận năm S2/S3. Không đưa các nội dung hóa học vào luật.
- Danh mục có 4 nguồn chính và 1 nguồn bổ sung; `docs/doi_chieu_luat.md` có
  đủ 28 id, không trùng hoặc thiếu. Các liên kết tài liệu nội bộ đã kiểm tra.
- BL06 chuẩn bị giống để gieo; chưa xác định lịch tháng/vụ địa phương. Khi
  tích hợp giao diện phải giữ giai đoạn này; runtime hiện chỉ trích nguồn chính.
- Nội dung chưa kiểm chứng: năm S2/S3, kiểm định thực địa và duyệt chuyên gia.
  Tài liệu TNAU 2020/2025 đã đọc không thay đầy đủ S2/S3; bản IRRI trên dịch vụ
  chia sẻ chưa xác minh bản gốc; không dùng các tài liệu đó để điền năm trang cũ.
- Pytest: 149 passed, 1 skipped (pgmpy), 9 xfailed (CN1); Ruff/check_rules đạt.
- Đợt hồ sơ chỉ sửa tài liệu, danh mục nguồn và README, không sửa hành vi chạy.
