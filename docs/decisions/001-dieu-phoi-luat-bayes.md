# ADR-001: Điều phối bộ luật và CNN–Bayes

Trạng thái: áp dụng trong đợt tích hợp người dùng duyệt ngày 18/11/2026.

## Bối cảnh

Luật và xác suất từng trả hai kết luận riêng. Một CNN rất thiên về bạc lá có
thể cho kết quả trái với luật gợi ý đạo ôn. Các CPD/ngưỡng hiện là giả định,
chưa có đánh giá hiệu chuẩn. Không thay hợp đồng hàm để giải quyết bất đồng.

## Quyết định

`diagnose(top3, callback)` giữ chữ ký, bốn trường kết quả và hai trường tùy
chọn đã có. Suy diễn lùi xếp câu hỏi theo top-3, nhớ mỗi thuộc tính một lần;
sau đó hỏi các thuộc tính người dùng còn thiếu theo vocabulary. Dữ kiện này
được dùng chung cho tiến và Bayes, bao gồm nguy cơ và xác nhận khuyến nghị.
Chỉ quan sát được gửi cho Bayes; không gửi kết luận do luật suy ra.

Chọn một gợi ý khi đúng một bệnh được luật chứng minh, các bệnh khác bị bác
bỏ trong bộ luật hiện tại, và CNN–Bayes cùng chọn bệnh đó qua ngưỡng. Nếu còn
nhánh chưa đủ, nhiều gợi ý, hòa, dưới ngưỡng hoặc bất đồng thì trả None. Không
suy lá khỏe từ việc không chứng minh được bệnh. Vết vẫn giữ các luật thực sự
đã bắn, kể cả khi chưa chọn được một nhãn cuối.

`do_tin_cay=None`: điểm quyết định và ngưỡng hiển thị trong `giai_thich` cùng
phương pháp, ghi chú bỏ qua và cảnh báo giả định. Không gọi điểm kỹ thuật là
xác suất bệnh đã hiệu chuẩn. Thiếu pgmpy dùng fallback có thông báo; lỗi mô
hình/đầu vào không được che thành một phiên chẩn đoán thành công giả.

`diagnose_image(path, callback)` gọi predictor một lần rồi chuyển top-3 cho
diagnose. Nếu predictor có IS_STUB=True, kết quả chỉ minh họa, ket_luan và
do_tin_cay luôn None, có thông báo GIẢ. Lỗi predictor được truyền lên.

## Lý do và hệ quả

Không chọn nhãn chỉ vì số cao hơn: hai phương pháp có giả định khác nhau.
Không đưa posterior vào facts: tránh biến giả định thành chứng cứ chắc chắn.
Hỏi đầy đủ giúp hai nhánh dùng cùng dữ kiện và kích hoạt được khuyến nghị;
đổi lại người dùng có thể phải trả lời tới 25 thuộc tính. Đây là lựa chọn dễ
giải thích cho đồ án; chưa tối ưu số câu hỏi của giao diện thực tế.

Các hàm tiến/lùi và API trả về không đổi. Nút/CPD không đổi số. Phép liệt kê
chỉ duyệt miền của biến chưa biết thay vì thử lại các trạng thái đã quan sát;
đây là tối ưu tính toán, không đổi mô hình.

## Kiểm chứng

Test test_diagnose_fusion.py kiểm tra đồng thuận, bất đồng, thiếu dữ kiện,
nhiều bệnh, cache và chỉ gửi quan sát. test_diagnose_image.py kiểm tra bản
giả, predictor thật giả lập và truyền lỗi. Các test cũ vẫn giữ nguyên.
