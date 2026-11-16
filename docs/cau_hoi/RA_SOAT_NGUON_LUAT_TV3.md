# Ghi chú rà soát chéo nguồn luật – TV3

**Trạng thái:** cập nhật hồ sơ ngày 17/11/2026. Đây là đối chiếu tài liệu, không phải biên bản chuyên gia ký duyệt. Mã nguồn cũ ngoài danh mục hiện hành không được dùng để chứng minh luật.

## Kết quả cấu trúc

- Bộ luật hiện có 28 luật; mỗi luật có mã nguồn và mục trích dẫn.
- Bốn nguồn chính S1–S4 được luật trích dẫn; S5 (IARI, 2013) bổ sung giai đoạn chọn giống của BL06. S2/S3 chưa xác minh năm xuất bản, không suy đoán từ máy chủ hoặc bản quyền website.
- BL02 chỉ dùng dấu hiệu vị trí bắt đầu gần chóp lá. BL03 chỉ dùng màu hoại tử quan sát được; không khẳng định tăng kích thước hoặc trình tự đổi màu theo thời gian.
- DN09 giới hạn quản lý cỏ dại trong vụ. DN10 ghi riêng luân canh cho vụ tiếp theo khi vụ hiện tại bị nhiễm.
- DO07 chỉ hỏi quan sát bông/gié lép trắng và yêu cầu kiểm tra thêm. Cách suy từ dấu hiệu sang gợi ý là lựa chọn mô hình hóa của nhóm, không phải chứng minh bệnh chắc chắn trong nguồn.
- BL06 dùng khi chuẩn bị giống để gieo; không diễn giải là điều trị cây đang bệnh. S5 hỗ trợ giai đoạn này, chưa hỗ trợ lịch tháng/vụ cụ thể tại Việt Nam.
- [Phiếu đối chiếu đủ 28 luật](../doi_chieu_luat.md) ghi rõ mục nguồn và giới hạn từng luật. Chưa có kiểm định thực địa hoặc duyệt chuyên gia địa phương.

## Việc còn cần xác minh

Người phụ trách nguồn cần tìm năm xuất bản đáng tin cậy cho S2/S3 hoặc thay bằng tài liệu có năm xác định. Trong lúc chưa có bằng chứng, giữ năm là `null` và ghi rõ thiếu năm trong danh mục nguồn.

Nguồn và cách đối chiếu chi tiết được duy trì tại `docs/nguon_tri_thuc.md`; dữ liệu chuẩn nằm trong `src/rules/sources.json` và `src/rules/rules.json`.
