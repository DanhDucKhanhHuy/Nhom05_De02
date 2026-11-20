# Mô hình đã huấn luyện

Artifact dự đoán tích hợp dùng tên `rice_leaf_classifier.keras`. Không đưa trọng
số lên Git; giữ `.gitkeep` và tài liệu này. Predictor đọc ảnh thật nhưng sẽ báo
`FileNotFoundError` khi chưa có artifact.

Trước khi phát hành, ghi lại kiến trúc và phiên bản mô hình, thứ tự lớp
(`dao_on`, `bac_la`, `dom_nau`, `la_khoe`), kích thước và cách chuẩn hóa ảnh,
phiên bản TensorFlow/Keras, nguồn/giấy phép dữ liệu, cách chia tập, các chỉ số
accuracy/precision/recall/F1, ma trận nhầm lẫn và SHA-256 của artifact. Chỉ ghi
kết quả sau một lần chạy đánh giá thực trên tập test độc lập. TV5 xác nhận có thể
nạp artifact trước khi đóng gói.

Lần chạy CN3 ngày 19/11/2026 đã tạo MobileNetV2 artifact cục bộ từ Mendeley
Data V1 (CC BY 4.0). SHA-256:
`a3c6dc43df0a237020e5fb67bb9826644b14f9dd4358c4547c8a689c28fb3898`.
Artifact bị loại khỏi Git; trước khi nộp, cần đóng gói file này hoặc cung cấp
liên kết tải hợp lệ. Metrics và lệnh tái tạo nằm trong
[`docs/cau_hoi/Q3.md`](../docs/cau_hoi/Q3.md), kết quả chi tiết ở
`artifacts/cn3/` trên máy chạy.
