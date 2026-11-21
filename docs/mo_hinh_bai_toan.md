# Mô hình bài toán

## CN1: lộ trình drone

### Cài đặt mô hình trạng thái

Mô hình được tách trong `src/drone/`: `state.py` định nghĩa trạng thái bất biến
`DroneState(position, medicine, battery, untreated)`; `operators.py` định nghĩa
ba hành động và chi phí; `problem.py` kiểm tra bản đồ, tạo trạng thái đầu, kiểm
tra đích và sinh các trạng thái kế tiếp hợp lệ. `A_star.py` tìm đường ngắn nhất
giữa hai ô, bay vượt vật cản (không hạ cánh lên đó) và lọc các đường không đủ pin
quay về trạm. Mỗi ô vật cản bay vượt qua cộng thêm 1 pin ngoài mức pin theo số
bước bay.
`a_star(cells, start, goal)` trả `(đường_đi, số_bước, thứ_tự_mở_rộng)` hoặc `None`.
`DroneProblem.path_to(state, destination)` gọi A* với pin còn lại và điều kiện an
toàn về trạm, trả đường đi gồm cả ô đầu/cuối hoặc `None`. A* chỉ xử lý từng chặng,
không tự chọn thứ tự phun toàn bộ các ô bệnh. Chạy
`python -m src.search.experiment` để in ma trận và chi tiết lộ trình A* toàn cục,
đối chiếu với tham lam gần nhất trên `data/sample/maps/map_4x4.json`. A* toàn cục
là tối ưu theo quãng đường bay nhưng có thể tốn nhiều tài nguyên khi số ô bệnh
tăng.

Trạng thái đầy đủ là `(hàng, cột, thuốc_còn_lại, pin_còn_lại, tập_ô_bệnh_chưa_phun)`.
Bản đồ và tập trạm là dữ liệu tĩnh. Thuốc và pin là số nguyên không âm.
Trạng thái đầu: ở `start` (phải là trạm), thuốc = k, pin = p, chưa phun ô bệnh nào.
Đích: tập ô bệnh chưa phun rỗng và vị trí hiện tại là một trạm.

- Bay: di chuyển theo 4 hướng. Có thể bay qua một hay nhiều ô vật cản liên tiếp
  nhưng chỉ hạ cánh ở ô không phải vật cản; mỗi ô đi qua tốn 1 pin cơ bản và
  thêm 1 pin phạt. Quãng đường vẫn tính theo số ô lưới đã bay qua.
- Phun: tại ô bệnh chưa phun, thuốc ≥1; thuốc −1, bỏ ô khỏi tập chưa phun.
  Phun không trừ pin, chi phí bay bằng 0.
- Nạp: chỉ tại ô 9; đặt thuốc = k, pin = p; chi phí bay bằng 0.
  Giả định trạm nạp không giới hạn lượt và chưa tính thời gian nạp.

k là số ô phun tối đa mỗi lần nạp. p là số bước bay tối đa mỗi lần nạp pin.
Mức 1–3 chỉ ghi mức bệnh; mỗi ô cần một lần phun, tiêu hao một đơn vị thuốc.
**CẦN XÁC NHẬN VỚI THẦY**: tài liệu khác của nhóm từng giả định mức m cần m
lần phun. Bản khung dùng cách hiểu README; nếu thầy đổi phải sửa mô hình,
giao tiếp và kiểm thử cùng nhau trước khi triển khai.

An toàn: sau mỗi toán tử, pin ≥ mức pin tiêu hao ít nhất để tới trạm gần nhất,
có xét vật cản và pin phạt khi bay vượt. Đường không tới được coi có khoảng cách
vô hạn.

Điều kiện khả thi: lưới chữ nhật khớp rows/cols, mã ô hợp lệ, start là trạm;
k,p nguyên dương; mọi ô bệnh tới được từ mạng trạm có thể tiếp cận từ start.
Mạng trạm nối hai trạm nếu mức pin tiêu hao ít nhất để bay giữa chúng ≤ p.
Với mỗi ô bệnh, phải có hai trạm trong mạng tiếp cận được (có thể trùng nhau)
sao cho tổng pin tiêu hao ít nhất từ trạm thứ nhất qua ô bệnh tới trạm thứ hai
≤ p. Với giả định
nạp không giới hạn và chi phí phun bằng 0, có thể phục vụ từng ô riêng khi k ≥1.
Điều kiện chỉ liên thông hoặc chỉ đủ pin đến ô bệnh là chưa đủ.

Chia hai tầng: TV1 tự cài A* tìm từng chặng giữa ô bệnh/trạm, sau đó tự cài leo
đồi chọn thứ tự ghé. Tầng thứ hai phải chèn lượt nạp hợp lệ và kiểm tra
thuốc/pin trên toàn hành trình. So sánh với tham lam cùng bản đồ và ngân sách.
Không coi đường A* từng chặng là lời giải đầy đủ của bài toán có tài nguyên.
Không khả thi: `plan_route` dự kiến ném `ValueError`, không trả đường đi một phần
như thể hoàn tất.

## CN2: hệ chuyên gia và mạng Bayes

Đầu vào: top 3 lớp/xác suất từ CNN, sự kiện triệu chứng người dùng xác nhận
(có thể chưa biết), tập luật có nguồn. Suy diễn tiến/lùi do TV2 tự cài.
Đầu ra: kết luận hoặc chưa đủ dữ kiện, độ tin cậy, id luật đã dùng, nguồn.
Bayes do TV3 dùng pgmpy với ≥5 nút; cấu trúc/CPT cần căn cứ và giải thích.
Chưa có luật thật, nguồn đã duyệt hoặc CPT; không suy ra xác suất thật từ số giả.

## CN3: nhận diện ảnh

Đầu vào: đường dẫn ảnh, tiền xử lý và thứ tự nhãn thống nhất với mô hình .keras.
Đầu ra: đúng 3 cặp (mã lớp, xác suất) giảm dần; xác suất hữu hạn trong [0,1].
Tổng top 3 ≤1 vì còn lớp thứ tư. Bản giả hiện trả số cố định để thử tích hợp;
không đọc ảnh, không chẩn đoán, không phải kết quả đo. Huấn luyện và đánh giá
CNN/transfer learning là phần việc tương lai của TV4.
