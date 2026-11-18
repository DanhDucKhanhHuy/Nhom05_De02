# Dữ liệu ảnh

## Bộ dữ liệu công khai cho CNN

Đã chọn bộ **A Rice Leaf Disease Dataset for Multi-Class Disease
Classification**, Hasan, Hossain và Biswas, Mendeley Data V1, DOI
[10.17632/n8jpkpfz5p.1](https://data.mendeley.com/datasets/n8jpkpfz5p/1), xuất bản
29/09/2026. Trang bộ dữ liệu ghi 6.758 ảnh thuộc 10 lớp và giấy phép CC BY 4.0.
Tập CN3 lấy bốn lớp sau (2.820 ảnh theo mô tả bộ dữ liệu):

| Lớp nguồn | Mã lớp dự án | Số ảnh nguồn |
|---|---|---:|
| Leaf Blast | `dao_on` | 521 |
| Bacterial Leaf Blight | `bac_la` | 785 |
| Brown Spot | `dom_nau` | 761 |
| Healthy | `la_khoe` | 753 |

Ghi attribution theo CC BY 4.0 và kiểm tra nhãn thực tế trong archive sau khi
tải. Chỉ chọn thư mục bốn lớp trên; các lớp bệnh khác không nhập vào classifier.
Ảnh gốc/giải nén nằm trong `data/raw/` (bị loại khỏi Git).

## Ảnh kiểm tra thực tế

TV3 ghi nguồn từng ảnh trong `data/anh_thuc_te/nguon.csv`; không commit ảnh.
Số liệu đánh giá chỉ được bổ sung sau khi chạy thật. Ngày 18/11/2026 đã kiểm kê
20 tệp: 5 ảnh mỗi thư mục bệnh/lá khỏe. Trước khi chia tập, bộ tiền xử lý loại
khỏi source bất kỳ ảnh nào có SHA-256 trùng với 20 tệp giữ làm holdout; trong
đó đã phát hiện 5 ảnh khỏe trùng byte với bộ công khai. Cột nhãn hiện lấy từ thư mục người dùng
đã phân loại, chưa được xác minh độc lập; metadata nguồn không xác nhận ảnh
được chụp tại Đồng bằng sông Cửu Long. Dùng chúng để xem xét dự đoán từng ảnh,
không đưa ra độ chính xác thực địa cho đến khi nhãn/nguồn được người phụ trách
xác nhận.

Danh mục ảnh đang giữ đúng tên tệp (kể cả khoảng trắng và hoa/thường). Metadata
ngày/người thu thập còn thiếu; không lấy thời gian sửa tệp làm ngày thu thập.
