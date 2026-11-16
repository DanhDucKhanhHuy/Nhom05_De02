# Q2 – Mạng Bayes và kết hợp xác suất CNN

## 1. Mục tiêu và quy ước lớp

CNN nhận ảnh lá lúa và trả về top-3 trong bốn nhãn loại trừ nhau:

| Mã | Nhãn |
|---|---|
| `dao_on` | Đạo ôn |
| `bac_la` | Bạc lá |
| `dom_nau` | Đốm nâu |
| `la_khoe` | Lá khỏe |

Mạng Bayes C5 mô hình hóa ba biến bệnh nhị phân riêng biệt. Vì vậy, **mạng Bayes cho phép nhiều bệnh đồng thời**; đây không phải mô hình bốn lớp loại trừ nhau. Để so sánh với đầu ra CNN, chương trình chuyển phân phối đồng thời sang bốn lớp:

- `dao_on`: chỉ mắc đạo ôn;
- `bac_la`: chỉ mắc bạc lá;
- `dom_nau`: chỉ mắc đốm nâu;
- `la_khoe`: không mắc cả ba bệnh.

Trạng thái mắc từ hai bệnh trở lên không bị gán tùy tiện vào một lớp. Khối lượng xác suất này được trả riêng ở `xac_suat_dong_mac`. Bốn lớp được chuẩn hóa có điều kiện trên các trạng thái không bệnh hoặc đúng một bệnh. Do đó, `xac_suat` là phân phối bốn lớp dùng để kết hợp CNN; xác suất lá khỏe đồng thời chưa điều kiện hóa được trả riêng tại `xac_suat_la_khoe_dong_thoi`.

## 2. Mô hình mạng Bayes C5

Mạng được khai báo tại `src/rules/bayes.py`, gồm tám nút:

- Nút gốc: `ThoiTiet`, `BonDam`, `Giong`, `DinhDuong`.
- Nút bệnh: `DaoOn`, `BacLa`, `DomNau`.
- Nút triệu chứng: `TrieuChung`.

Cấu trúc phụ thuộc:

```text
ThoiTiet ─┬────────> DaoOn ───────┐
BonDam ───┤                       │
Giong ────┘                       │
                                 ├──> TrieuChung
ThoiTiet ───────────> BacLa ──────┤
BonDam ─────────────>             │
                                 │
DinhDuong ──────────> DomNau ─────┘
ThoiTiet ───────────>
```

Mỗi CPD được lưu trong `NUT`. Khóa CPD là tổ hợp trạng thái các nút cha theo thứ tự khai báo; mỗi cột là phân phối xác suất của nút con và phải có tổng bằng 1. Hàm `kiem_tra_cpd()` kiểm tra tính đầy đủ của tổ hợp cha, số trạng thái, tổng từng cột và tổng phân phối đồng thời.

### 2.1. Căn cứ và giới hạn CPD

Các CPD hiện tại là **giả định định tính để minh họa mô hình**, chưa phải tần suất thống kê hoặc xác suất đã hiệu chuẩn từ dữ liệu đồng ruộng. Các nguồn dưới đây hỗ trợ cấu trúc quan hệ/nhóm triệu chứng ở mức mô tả, không cung cấp các con số trong bảng CPD:

| Thành phần | Căn cứ mô tả | Giới hạn |
|---|---|---|
| `DaoOn` | S1, S4 | Không có tần suất số để suy ra từng ô CPD |
| `BacLa` | S2 | Không có tần suất số để suy ra từng ô CPD |
| `DomNau` | S3 | Không có tần suất số để suy ra từng ô CPD |
| `TrieuChung` | S1–S4 | Bảng triệu chứng là mô hình hóa rút gọn, không phải mô hình bệnh học đầy đủ |
| `ThoiTiet`, `BonDam`, `Giong`, `DinhDuong` | Giả định thiết kế của nhóm | Prior nút gốc không phải tỷ lệ phổ biến thực tế |

Danh mục nguồn hiện hành được lấy từ `src/rules/sources.json` và `docs/nguon_tri_thuc.md`:

- **S1:** “Phòng trừ bệnh đạo ôn hại lúa”, Trung tâm Khuyến nông Quốc gia, 2021. [Trang tài liệu](https://khuyennongvn.gov.vn/khoa-hoc-cong-nghe/khcn-trong-nuoc/phong-tru-benh-dao-on-hai-lua-21414.html).
- **S2:** “Bệnh bạc lá vi khuẩn trên lúa”, Đại học Nông nghiệp Tamil Nadu (TNAU), cổng Agritech – Crop Protection. [Trang HTML](https://www.agritech.tnau.ac.in/expert_system/paddy/cpdisblb.html). Trang không ghi năm xuất bản; không suy đoán năm từ ngày tệp máy chủ.
- **S3:** “Bệnh đốm nâu”, Viện Nghiên cứu và Phát triển Lúa, Bộ Nông nghiệp Sri Lanka. [Trang tài liệu](https://doa.gov.lk/rrdi_ricediseases_brownspot/). Trang không ghi năm xuất bản; © 2026 không được xem là năm xuất bản.
- **S4:** “Hướng dẫn quản lý dịch hại lúa: bệnh đạo ôn”, Chương trình Quản lý dịch hại tổng hợp, Đại học California, cập nhật 07/2024. [Trang tài liệu](https://ipm.ucanr.edu/agriculture/rice/rice-blast/).

S2 và S3 vẫn để năm `null` trong danh mục nguồn. Nhóm cần dữ liệu thực nghiệm có nhãn để ước lượng/hiệu chuẩn CPD và kiểm tra độ tin cậy trước khi diễn giải các xác suất như rủi ro thực tế.

## 3. Thống nhất bằng chứng TV2–TV3

Nguồn từ điển thuộc tính đầu vào là `src/rules/vocabulary.json`. TV3 nhận trực tiếp dạng:

```python
{
    "vet_bac_ung_nuoc_tren_phien_la": "co",
    "am_u_va_suong_som": "co",
    "thua_dam": "co",
}
```

Các ánh xạ hiện có và thuộc tính chưa được mô hình hỗ trợ:

| Thuộc tính TV2 | Trạng thái | Bằng chứng Bayes |
|---|---|---|
| `vet_bac_ung_nuoc_tren_phien_la` | `co` | Chưa có nút/CPD tương đương; bỏ qua và ghi chú |
| `dom_tron_hoac_bau_duc_nau` | `co` | `TrieuChung=dom_tron` |
| `am_u_va_suong_som` | `co` | `ThoiTiet=mua_am` |
| `thua_dam` | `co` | `BonDam=cao` |

Chỉ ánh xạ thuộc tính khi nghĩa của trạng thái khớp nút Bayes. Vệt úng nước của bạc lá không phải vết hình thoi; ánh xạ cũ sang `vet_thoi` đã bị bỏ. Vết hình thoi, tâm vết xám khô và viền nâu hiện được ghi chú và bỏ qua; đợt sửa này không mở rộng nút/CPD triệu chứng. Dữ kiện bị Bayes bỏ qua vẫn được hệ luật sử dụng. `am_u_va_suong_som=khong` không đủ để kết luận thời tiết khô; `thua_dam=khong` không đủ để kết luận đạm thấp. `chua_biet` và thuộc tính chưa có ánh xạ cũng được bỏ qua.

Nếu nhiều bằng chứng đưa ra trạng thái trái ngược cho cùng một nút Bayes, toàn bộ bằng chứng của nút đó bị loại và ghi chú mâu thuẫn. Việc tổng hợp theo tập trạng thái và sắp xếp ghi chú giúp kết quả không phụ thuộc thứ tự nhập. Mã thời tiết do bộ lấy thời tiết tạo (ví dụ `tt_am_do_cao`) vẫn được nhận; triệu chứng dùng chung lấy trực tiếp từ `vocabulary.json`.

## 4. Truy vấn hậu nghiệm và xác suất lá khỏe

Theo định lý Bayes:

\[
P(H\mid E)=\frac{P(E\mid H)P(H)}{P(E)}
\]

Mạng có thể tính phân phối đồng thời ba nút bệnh:

\[
P(D_o,D_b,D_n\mid E)
\]

Xác suất lá khỏe được lấy trực tiếp từ trạng thái đồng thời không mắc cả ba bệnh:

\[
P(la\_khoe\mid E)=P(D_o=0,D_b=0,D_n=0\mid E)
\]

Không sử dụng phép nhân các xác suất biên, vì các biến bệnh không được giả định độc lập vô điều kiện. Chương trình trả phân phối đồng thời tại `phan_phoi_dong_thoi`, xác suất lá khỏe chính xác theo mô hình tại `xac_suat_la_khoe_dong_thoi` và khối lượng đồng mắc tại `xac_suat_dong_mac`.

Có hai đường tính: `pgmpy` với `VariableElimination`, và phép liệt kê độc lập toàn bộ phân phối đồng thời. Khi cài `pgmpy==0.1.25`, chương trình dựng mạng, gọi `check_model()` và truy vấn đồng thời ba biến bệnh. Nếu thiếu pgmpy hoặc thư viện không tương thích, chương trình ghi rõ lý do và dùng phép liệt kê.

## 5. C6 – Công thức kết hợp CNN–Bayes

### 5.1. Chuẩn hóa CNN top-3

CNN trả đúng ba lớp khác nhau trong bốn lớp. Lớp bị lược khỏi top-3 nhận phần xác suất còn lại:

\[
P_{CNN}(C_{omit})=1-\sum_{C\in top3}P_{CNN}(C)
\]

Top-3 sai số lượng, mã lớp, lớp trùng, xác suất không hữu hạn/ngoài [0,1], tổng bằng 0 hoặc tổng vượt 1 đều bị từ chối. Chương trình không tự sửa một phân phối đầu vào sai thành phân phối hợp lệ.

### 5.2. Công thức nghiệm thu

Khi tập CNN cân bằng lớp:

\[
P(C\mid ảnh,điều\ kiện)\propto
P_{CNN}(C)\times P(C\mid điều\ kiện)
\]

Sau đó chuẩn hóa:

\[
P_{kết\ hợp}(C)=
\frac{P_{CNN}(C)P(C\mid điều\ kiện)}
{\sum_jP_{CNN}(C_j)P(C_j\mid điều\ kiện)}
\]

Giả định sử dụng: ảnh và điều kiện ruộng độc lập có điều kiện khi đã biết lớp bệnh. Đây là giả định mô hình, không phải sự thật đã được chứng minh; nếu CNN và bằng chứng người dùng cùng chứa thông tin triệu chứng, có thể xảy ra đếm trùng bằng chứng.

### 5.3. Hiệu chỉnh prior khi dữ liệu CNN mất cân bằng

Nếu prior lớp trong tập huấn luyện CNN không cân bằng, truyền `prior_cnn` gồm đủ bốn lớp. Chương trình xấp xỉ likelihood ảnh bằng:

\[
P(ảnh\mid C)\propto\frac{P_{CNN}(C)}{P_{train}(C)}
\]

và kết hợp:

\[
P(C\mid ảnh,điều\ kiện)\propto
\frac{P_{CNN}(C)}{P_{train}(C)}
P(C\mid điều\ kiện)
\]

Nếu không truyền prior, chương trình giả định tập huấn luyện cân bằng bốn lớp. Prior phải có đủ bốn mã lớp và mọi giá trị phải hữu hạn, dương. Mẫu số kết hợp bằng 0 sẽ phát sinh lỗi, không trả phân phối giả.

### 5.4. Ngưỡng kết luận và hòa

Ngưỡng mặc định là `NGUONG_KET_LUAN = 0.60`. Vì CNN chỉ biểu diễn bốn lớp đơn bệnh/lá khỏe, độ chắc dùng cho quyết định được giảm bảo thủ theo xác suất đồng mắc:

\[
S_{quyet\_dinh}=P_{ket\_hop}(C_{dau})\times(1-P_{dong\_mac})
\]

Đây là điểm quyết định kỹ thuật, không phải xác suất đã hiệu chuẩn. Nếu điểm này **lớn hơn hoặc bằng** ngưỡng và không hòa với lớp thứ hai, hệ thống kết luận lớp đứng đầu. Nếu thấp hơn ngưỡng hoặc hai lớp đầu hòa trong sai số số học, trả `ket_luan=None`, `trang_thai="chua_du_chac"`. Ngưỡng có thể truyền vào `ket_hop_cnn_bayes(..., nguong=...)` hoặc CLI `--nguong`.

## 6. Ví dụ chạy xuyên suốt

Ví dụ dưới đây dùng đầu ra CNN giả lập để kiểm thử tích hợp, không phải kết quả mô hình đã huấn luyện:

```python
from src.rules.ket_hop import ket_hop_cnn_bayes

top3 = [
    ("dao_on", 0.55),
    ("dom_nau", 0.40),
    ("bac_la", 0.03),
]
evidence = {
    "vet_bac_ung_nuoc_tren_phien_la": "co",
    "am_u_va_suong_som": "co",
    "thua_dam": "co",
}

result = ket_hop_cnn_bayes(
    top3,
    evidence,
    su_dung_pgmpy=False,  # dùng phép liệt kê độc lập để tái lập ví dụ
)
print(result["xac_suat_bayes"])
print(result["xac_suat_ket_hop"])
print(result["trang_thai"], result["ket_luan"])
print("Điểm quyết định =", result["do_tin_cay_dieu_chinh"])
print("P(đồng mắc) =", result["xac_suat_dong_mac"])
print("Bằng chứng thực dùng =", result["bang_chung_bayes"])
print("Ghi chú =", result["ghi_chu"])
```

Với CPD hiện tại và phép liệt kê, chỉ có `ThoiTiet=mua_am`, `BonDam=cao` được đưa vào mạng. Dữ kiện vệt úng nước được ghi chú là chưa có trạng thái tương đương, không chuyển thành vết hình thoi. Phân phối Bayes bốn lớp có điều kiện xấp xỉ: đạo ôn 26.06%, bạc lá 40.53%, đốm nâu 16.04%, lá khỏe 17.37%. Xác suất đồng thời của trạng thái không mắc cả ba bệnh là 6.24%; khối lượng đồng mắc từ hai bệnh là 64.08%.

Sau khi kết hợp CNN giả và chuẩn hóa, phân phối bốn lớp xấp xỉ: đạo ôn 64.24%, bạc lá 5.45%, đốm nâu 28.75%, lá khỏe 1.56%. Điểm quyết định là 64.24% × (1 − 64.08%) ≈ 23.08%, thấp hơn ngưỡng 0.60. Kết quả là `trang_thai="chua_du_chac"`, `ket_luan=None`. Đây là ví dụ CPD giả định và CNN giả, không phải xác suất thực địa hay bằng chứng xác nhận đạo ôn. Test `test_q2_example_reports_the_evidence_actually_used` tái hiện các con số cùng ghi chú bỏ qua dữ kiện.

## 7. Cách chạy và kiểm thử

```bash
python -m src.rules.bayes --khong-pgmpy
python -m src.rules.ket_hop --khong-pgmpy
python -m pytest
```

Để kiểm chứng riêng đường pgmpy, cài đúng phiên bản khai báo:

```bash
python -m pip install pgmpy==0.1.25
python -c "import pgmpy; print(pgmpy.__version__)"
python -m pytest tests/test_tv3_probability.py -q
```

Để cài toàn bộ môi trường ứng dụng (bao gồm CNN/TensorFlow), dùng
`python -m pip install -r requirements.txt`.

Bộ kiểm thử TV3 bao gồm ánh xạ bằng chứng, mâu thuẫn không phụ thuộc thứ tự, dữ kiện chưa biết/không hỗ trợ, phân phối đồng thời, Top-3 và các ca biên, hiệu chỉnh prior, ngưỡng dưới/bằng/trên, hòa, tích bằng 0, cùng kiểm tra pgmpy so với phép liệt kê độc lập trên ba truy vấn. Test `predict_top3` sử dụng module giả lập, không cần TensorFlow.

## 8. Giới hạn

Các CPD chưa được học từ dữ liệu có nhãn; CNN trong `src/model/predict.py` hiện là stub. Ngưỡng 0.60 là ngưỡng kỹ thuật ban đầu, chưa được tối ưu trên validation. Kết quả chỉ phục vụ kiểm thử/tích hợp và hỗ trợ tham khảo; không thay thế kiểm tra đồng ruộng hoặc tư vấn của cán bộ bảo vệ thực vật.
