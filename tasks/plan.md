# Kế hoạch sửa các điểm còn thiếu của tri thức CN2

Ngày lập: 17/11/2026. Người dùng yêu cầu lập kế hoạch rồi bắt đầu triển khai.
Danh sách thực hiện và kết quả từng bước nằm trong `tasks/todo.md`.

## Phạm vi

Sửa các vấn đề của lượt nghiệm thu tri thức: bằng chứng bạc lá bị đưa vào trạng
thái Bayes sai, câu hỏi DO07 yêu cầu biết bệnh trước, diễn giải phủ định đạm,
thuật ngữ và hồ sơ nguồn. Giữ API tiến/lùi/chẩn đoán, schema luật và nguồn.
Không sửa thuật toán suy diễn, không tự tạo CPD hoặc tài liệu nguồn. Không
commit/push/tag; giữ nguyên ảnh và các tệp pyc đã thay đổi trước phiên này.

## Quyết định

- Chưa có nút/CPD tương đương thì ghi chú Bayes chưa hỗ trợ; bộ luật vẫn dùng
  dữ kiện đó. Không sửa CPD để làm kết quả trông hợp lý.
- DO07 chỉ là dấu hiệu cần kiểm tra, không xác nhận bệnh. Câu hỏi phải quan sát
  được mà không đòi người dùng biết bệnh. Đổi mã dữ kiện cùng luật và tài liệu;
  schema và chữ ký hàm không đổi. Không tự đổi dữ kiện mã cũ thành mã mới vì
  điều kiện bệnh xuất hiện sớm của mã cũ không tương đương hoàn toàn.
- `khong` là phủ định mệnh đề; thiếu căn cứ chọn `chua_biet`.
- Test cũ mô tả lỗi sẽ được sửa kỳ vọng theo yêu cầu mới, không bỏ test hoặc
  giảm mức kiểm tra. Thêm test hồi quy trước sửa hành vi.
- Năm nguồn chỉ được cập nhật khi tìm được bằng chứng chính thức. Không có thì
  giữ null, ghi chưa kiểm chứng; không lấy năm bản quyền làm năm xuất bản.

## Thứ tự và tiêu chí

1. Bỏ ánh xạ bạc lá sang `TrieuChung=vet_thoi` (phạm vi vừa: Bayes, test).
   Đạt khi bằng chứng được ghi chú, không làm đổi posterior so với chưa có
   bằng chứng, và không xóa dấu hiệu khác được hỗ trợ. Test tập trung trước/sau.
2. Sửa DO07 (phạm vi vừa: luật, từ vựng, test và tài liệu tri thức).
   Đạt khi câu hỏi chỉ nói bông/gié lép trắng, chỉ sinh cần kiểm tra, không xác
   nhận bệnh. Test tiến/lùi và kiểm tra schema; checkpoint toàn bộ test.
3. Đồng bộ diễn giải đạm và tâm đốm (phạm vi nhỏ: từ vựng, test).
   Đạt khi Không và Chưa biết phân biệt được; thuật ngữ nâu đỏ nhạt nhất quán.
4. Đồng bộ tài liệu xác suất và ví dụ Q2 (phạm vi vừa: hai tài liệu, test).
   Đạt khi không còn tuyên bố ánh xạ sai là tương đương; ví dụ số tái hiện được
   với bằng chứng thực sự đã nhận, giữ cảnh báo CPD giả định.
5. Kiểm chứng hồ sơ nguồn (phạm vi nhỏ: danh mục nguồn, tài liệu tri thức).
   Đạt khi có bằng chứng cho thông tin cập nhật hoặc ghi rõ khoảng trống còn
   lại; không tự khẳng định thời điểm áp dụng BL06.
6. Kiểm tra cuối và review: pytest, Ruff, check_rules, demo, đối chiếu diff.
   Không coi skip pgmpy/xfail CN1 là kiểm chứng đạt các chức năng đó.

## Phụ thuộc và giới hạn

Bước 1 trước bước 4; bước 2 và 3 trước bước 5/6. Mỗi phần sửa được kiểm thử
trước khi sang phần tiếp theo. Tách nút triệu chứng, xây CPD mới và chính sách
điều phối luật–Bayes nằm ngoài đợt sửa này, cần thiết kế/nguồn riêng.
Nếu không tìm được năm S2/S3 hoặc thời điểm BL06, báo rõ chưa kiểm chứng;
không tuyên bố toàn bộ tri thức hoặc CN2 đã hoàn tất nghiệm thu.

## Đợt tiếp theo: hoàn thiện hồ sơ tri thức

Người dùng yêu cầu ưu tiên hồ sơ tri thức sau đợt sửa trên. Giữ nguyên các
đầu việc Bayes/pgmpy còn mở; không tạo lại hay xóa lịch sử kế hoạch.

7. Đối chiếu nguồn chính thức và bổ sung căn cứ giai đoạn áp dụng BL06.
   Chỉ thêm tài liệu đã đọc với năm/trang có bằng chứng; không sửa năm S2/S3
   bằng ngày của tài liệu khác. Không thay đổi điều kiện/kết luận luật.
8. Lập `docs/doi_chieu_luat.md` cho đủ 28 id: mục nguồn, nội dung hỗ trợ và
   giới hạn suy luận; phân biệt mô tả trong tài liệu với quy tắc sàng lọc.
9. Đồng bộ danh mục nguồn, README, ghi chú rà soát và Q4. Chạy kiểm tra luật,
   test và Ruff. Hồ sơ phải công bố các khoảng trống và người cần duyệt, không
   tạo xác nhận chuyên gia hoặc kết quả thực địa chưa có.

Tiêu chí: 28 id có phiếu đối chiếu, không thiếu nguồn hoặc mục; BL06 có nguồn
cho giai đoạn chọn giống; metadata thiếu được liệt kê; schema và hành vi chạy
giữ nguyên. Tài liệu tĩnh không cần thêm test chỉ để kiểm tra câu chữ.
