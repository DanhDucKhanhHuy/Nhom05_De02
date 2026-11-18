# Q2 – Mạng Bayes đa bằng chứng và kết hợp xác suất CNN

## 1. Mục tiêu, phạm vi và quy ước đầu ra

CNN dự đoán bốn lớp loại trừ nhau: `dao_on`, `bac_la`, `dom_nau`, `la_khoe`. Mạng Bayes không ép ba bệnh loại trừ nhau: `DaoOn`, `BacLa`, `DomNau` là ba biến nhị phân riêng, do đó cho phép đồng mắc. Để kết hợp với CNN, chương trình:
- lấy xác suất trạng thái không mắc bệnh nào làm khối lượng `la_khoe`;
- lấy trạng thái chỉ mắc đúng một bệnh làm ba lớp bệnh;
- báo riêng tổng khối lượng đồng mắc từ hai bệnh trở lên;
- chuẩn hóa bốn lớp trên phần khối lượng không bệnh hoặc đúng một bệnh.

`xac_suat_bayes` là posterior bốn lớp có điều kiện theo quy ước phân lớp trên, không phải xác suất đồng thời đầy đủ của mọi trạng thái bệnh. `xac_suat_la_khoe_dong_thoi` được lấy trực tiếp từ trạng thái `(khong, khong, khong)` của phân phối đồng thời, không nhân ba xác suất biên.

## 2. Thiết kế mạng: triệu chứng là các nút quan sát riêng

Mạng ở `src/rules/bayes.py` không còn nút đa trạng thái `TrieuChung`. Mỗi dấu hiệu được biểu diễn thành một nút nhị phân `co/khong`, vì nhiều dấu hiệu có thể cùng xuất hiện trên một mẫu lá.

Cấu trúc chính:

```text
ThoiTiet ───────┬──> DaoOn ──> VetHinhThoi ──> VetTamXamKho
                ├──> BacLa ──> BacVetUngNuoc ─┬─> BacBatDauChop
                │                            ├─> BacVangTrang
                │                            └─> BacMepLuonSong
                └──> DomNau ─> DomTronBauDuc ─┬─> DomVienSam
                                             └─> DomTamNhatXam

ThuaDam ────────┬──> DaoOn
                └──> BacLa

Giong ─────────────> DaoOn
DinhDuong ────────> DomNau

BacLa ─────────────> LaHeoCuon
DomNau ────────────> DomTrenBeLa
                  ├> DomTrenDiepTieu
                  ├> DomTrenVoTrau
                  └> HatNheBacPhan

ThoiTiet ──────────> AmU_SuongSom
```

Các cạnh từ bệnh đến dấu hiệu mô tả quan hệ nhân quả/điều kiện hóa giả định của mô hình, không khẳng định một dấu hiệu đơn lẻ đủ chẩn đoán bệnh. Một số dấu hiệu chi tiết được đặt làm nút con của dấu hiệu hình thái chính:
- `VetTamXamKho` phụ thuộc `VetHinhThoi`;
- `BacBatDauChop`, `BacVangTrang`, `BacMepLuonSong` phụ thuộc `BacVetUngNuoc`;
- `DomVienSam`, `DomTamNhatXam` phụ thuộc `DomTronBauDuc`.

Vì vậy, nếu cung cấp cả dấu hiệu chính và dấu hiệu chi tiết, Bayes giữ cả hai bằng chứng và xử lý phụ thuộc thông qua CPD, thay vì gộp chúng hoặc đếm như các nút độc lập.

## 3. Thuộc tính TV2 được Bayes hỗ trợ

Bảng sau là danh sách đầy đủ thuộc tính có trong `vocabulary.json`. “Có/Không” được ánh xạ vào hai trạng thái của cùng nút quan sát; `chua_biet` và dữ kiện thiếu không tạo evidence.

| Thuộc tính | Nút Bayes | Hỗ trợ |
|---|---|---|
| `vet_la_hinh_thoi` | `VetHinhThoi` | Có |
| `vet_la_tam_xam_kho` | `VetTamXamKho` | Có |
| `vet_bac_ung_nuoc_tren_phien_la` | `BacVetUngNuoc` | Có |
| `vet_bac_bat_dau_o_chop_la` | `BacBatDauChop` | Có |
| `vet_la_vang_den_trang` | `BacVangTrang` | Có |
| `vet_bac_mep_luon_song` | `BacMepLuonSong` | Có |
| `la_heo_hoac_cuon_lai` | `LaHeoCuon` | Có |
| `dom_tron_hoac_bau_duc_nau` | `DomTronBauDuc` | Có |
| `dom_nau_vien_sam` | `DomVienSam` | Có |
| `dom_nau_tam_nhat_xam` | `DomTamNhatXam` | Có |
| `dom_nau_tren_be_la` | `DomTrenBeLa` | Có |
| `dom_nau_tren_diep_tieu` | `DomTrenDiepTieu` | Có |
| `dom_nau_tren_vo_trau` | `DomTrenVoTrau` | Có |
| `hat_nhe_hoac_bac_phan` | `HatNheBacPhan` | Có |
| `am_u_va_suong_som` | `AmU_SuongSom` | Có |
| `thua_dam` | `ThuaDam` | Có |

Các thuộc tính chưa đưa vào mạng ở phiên bản này: `vet_la_vien_nau`, `vet_co_la_nau_do`, `dot_than_teo_nau`, `co_bong_thoi_nau`, `bong_hoac_gie_lep_trang`, `ruong_thieu_nuoc`, `sa_day`, `cay_gan_truong_thanh_la_gia_hoa`, `ruong_xac_nhan_nhiem_dom_nau`. Hệ thống giữ nguyên dữ kiện cho hệ luật TV2; Bayes ghi chú và bỏ qua, không tự gán sang một nút gần nghĩa.

Các nguyên tắc ánh xạ:
- `vet_la_tam_xam_kho` → `VetTamXamKho`, không chuyển thành `VetHinhThoi`.
- `thua_dam=khong` → `ThuaDam=khong`, không chuyển thành “đạm thấp”.
- `am_u_va_suong_som=khong` → `AmU_SuongSom=khong`, không chuyển thành “thời tiết khô”.
- Vệt bạc lá úng nước và các đặc điểm của vệt bạc có nút riêng; không ánh xạ sang triệu chứng đạo ôn.
- Các thuộc tính không được liệt kê trong bảng hỗ trợ không tạo bằng chứng Bayes.

## 4. Xử lý dữ kiện thiếu, phủ định và mã cũ

Đầu vào Mapping nhận `thuoc_tinh: co|khong|chua_biet`; giá trị Boolean cũng được chuẩn hóa rõ ràng: `True` → `co`, `False` → `khong`. Chuỗi `"False"` cũng được hiểu là phủ định, không phải bằng chứng dương. `None`, `chua_biet` và thuộc tính bị bỏ trống không tạo evidence.

Mã cũ chỉ được chuyển đổi nếu có định nghĩa tương đương:
- `TrieuChung=dom_tron` được chuyển thành `DomTronBauDuc=co`.
- `TrieuChung=vet_thoi`, `TrieuChung=chop_la_kho` và `TrieuChung=khong` không có ánh xạ tương đương nên bị bỏ qua kèm ghi chú.
- `BonDam=cao/thap` không được đổi sang `ThuaDam=co/khong`, vì “cao/thấp” không tương đương chính xác với “vượt/không vượt khuyến cáo”.
- Mã thời tiết cũ chỉ được nhận theo bảng quy tắc ở mục 5.

Nếu nhiều dữ kiện tạo ra hai trạng thái trái ngược cho cùng nút, toàn bộ bằng chứng của nút đó bị loại và ghi chú mâu thuẫn. Tập hợp và sắp xếp ghi chú giúp kết quả không phụ thuộc thứ tự nhập.

## 5. Tách số đo thời tiết khỏi quan sát ruộng/cây

`src/app/thoi_tiet.py` chỉ chuyển số đo thời tiết sang nút thời tiết `ThoiTiet` theo quy tắc kỹ thuật minh họa:
- độ ẩm tương đối `>= 80%` → `tt_am_do_cao` → `ThoiTiet=mua_am`;
- nếu điều kiện trên không đúng, lượng mưa `>= 1 mm` → `tt_mua_nhieu` → `ThoiTiet=mua_am`;
- độ ẩm `< 60%` đồng thời lượng mưa `= 0 mm` → `tt_kho_han` → `ThoiTiet=kho`;
- các trường hợp khác không tạo bằng chứng.

Các ngưỡng này chỉ phân nhóm điều kiện thời tiết để thử nghiệm mô hình, không phải ngưỡng dịch tễ/chẩn đoán. Sương mù, gió, nhiệt độ hoặc một phép đo riêng lẻ không tự tạo triệu chứng. Hệ thống không suy từ thời tiết thành ruộng thiếu nước, cây héo, có vết bệnh hoặc đã nhiễm bệnh. Thuộc tính người dùng `am_u_va_suong_som` là quan sát riêng `AmU_SuongSom`, không đồng nhất với nút đo thời tiết `ThoiTiet`.

## 6. CPD, giả định và nguồn định tính

Mỗi CPD được khai báo tại `NUT`, kèm `nguon` và `gia_dinh`. `kiem_tra_cpd()` kiểm tra:
- đủ mọi tổ hợp trạng thái cha;
- đúng số trạng thái của nút con;
- mọi xác suất hữu hạn, thuộc `[0,1]`;
- tổng từng cột bằng 1;
- cấu trúc nút theo thứ tự topo, không tham chiếu cha không tồn tại.

S1/S4 hỗ trợ mô tả dấu hiệu đạo ôn; S2 hỗ trợ nhóm dấu hiệu bạc lá; S3 hỗ trợ nhóm dấu hiệu đốm nâu. Các nguồn này không cung cấp các xác suất số đang đặt trong CPD. Các prior nút gốc, xác suất bệnh theo yếu tố nguy cơ và xác suất dấu hiệu theo bệnh đều là giả định minh họa của nhóm. Quan hệ giữa các dấu hiệu chi tiết được thể hiện bằng cạnh cha–con như mục 2, thay vì đổi tên một nút triệu chứng cũ và giữ nguyên CPD đa trạng thái.

Danh mục tài liệu: `src/rules/sources.json` và `docs/nguon_tri_thuc.md`:
- S1: “Phòng trừ bệnh đạo ôn hại lúa”, Trung tâm Khuyến nông Quốc gia, 2021. [Nguồn](https://khuyennongvn.gov.vn/khoa-hoc-cong-nghe/khcn-trong-nuoc/phong-tru-benh-dao-on-hai-lua-21414.html).
- S2: EPPO Datasheet XANTOR, mục Detection and Identification / Symptoms cập nhật 16/06/2022. [Nguồn](https://gd.eppo.int/taxon/XANTOR/datasheet).
- S7: Niño-Liu, Ronald và Bogdanove (2006), trang in 306 hỗ trợ héo/cuộn lá và giới hạn phân biệt bệnh. [Bài khoa học](https://cropgeneticsinnovation.ucdavis.edu/sites/g/files/dgvnsk6996/files/inline-files/r0604.pdf).
- S3: “Louisiana Rice Production Handbook”, LSU AgCenter, 2014, mục Brown Spot. [PDF](https://www.lsuagcenter.com/~/media/system/9/0/e/9/90e93160aba5daccea90c6d955299f74/pub2331riceproductionhandbook2014completebook.pdf).
- S4: “Hướng dẫn quản lý dịch hại lúa: bệnh đạo ôn”, UC IPM, cập nhật 07/2024. [Nguồn](https://ipm.ucanr.edu/agriculture/rice/rice-blast/).

Nguồn mô tả triệu chứng chỉ hỗ trợ cấu trúc định tính; không được diễn giải thành nguồn của các con số CPD. Cần bộ dữ liệu đồng ruộng có nhãn để ước lượng/hiệu chuẩn CPD và đánh giá calibration.

## 7. Truy vấn Bayes và công thức CNN–Bayes

Với lớp \(C\), ảnh \(I\), điều kiện ruộng \(E\), giả định ảnh và bằng chứng ruộng độc lập có điều kiện khi đã biết lớp:

\[
P(C\mid I,E)\propto P(I\mid C)P(C\mid E)
\]

CNN thường trả posterior theo prior huấn luyện \(P_{train}(C)\). Khi có prior huấn luyện, xấp xỉ likelihood ảnh bằng:

\[
P(I\mid C)\propto \frac{P_{CNN}(C\mid I)}{P_{train}(C)}
\]

Do đó:

\[
P_{kết\ hợp}(C)=
\frac{\left(P_{CNN}(C\mid I)/P_{train}(C)\right)P(C\mid E)}
{\sum_j\left(P_{CNN}(C_j\mid I)/P_{train}(C_j)\right)P(C_j\mid E)}
\]

Nếu không truyền `prior_cnn`, chương trình giả định bốn lớp huấn luyện cân bằng. Đây là giả định; nếu prior huấn luyện thực tế mất cân bằng thì phải truyền đủ bốn giá trị prior.

**Giới hạn:** nếu CNN đã học trực tiếp các triệu chứng hình ảnh cũng được nhập lại làm evidence Bayes, giả định độc lập có điều kiện có thể bị vi phạm và thông tin bị đếm trùng. Công thức kết hợp chỉ là phép kết hợp theo giả định, không tự bảo đảm hiệu chuẩn.

## 8. Posterior và điểm quyết định

`xac_suat_bayes` và `xac_suat_ket_hop` là các phân phối posterior theo mô hình/giả định đã khai báo. Chúng chưa được hiệu chuẩn thực nghiệm. `do_tin_cay_dieu_chinh` là **điểm quyết định kỹ thuật**, không phải posterior mới và không phải xác suất chẩn đoán đã hiệu chuẩn.

Ngưỡng mặc định `NGUONG_KET_LUAN = 0.60`. Điểm quyết định bằng xác suất lớp đứng đầu sau kết hợp nhân với phần xác suất không đồng mắc. Chỉ kết luận khi điểm `>= 0.60` và không hòa với lớp thứ hai; dưới ngưỡng hoặc hòa thì trả `ket_luan=None`, `trang_thai="chua_du_chac"`. Ngưỡng 0.60 là tham số kỹ thuật ban đầu, cần đánh giá trên validation độc lập.

## 9. Ví dụ xuyên suốt

Ví dụ dùng top-3 giả lập và nhiều dấu hiệu cùng lúc:

```python
from src.rules.ket_hop import ket_hop_cnn_bayes

top3 = [
    ("dao_on", 0.55),
    ("dom_nau", 0.40),
    ("bac_la", 0.03),
]
evidence = {
    "vet_bac_ung_nuoc_tren_phien_la": "co",
    "vet_bac_bat_dau_o_chop_la": "co",
    "vet_bac_mep_luon_song": "co",
    "vet_la_hinh_thoi": "co",
    "dom_tron_hoac_bau_duc_nau": "co",
    "dom_nau_vien_sam": "co",
    "thua_dam": "khong",
    "vet_la_tam_xam_kho": "chua_biet",
}

result = ket_hop_cnn_bayes(
    top3,
    evidence,
    su_dung_pgmpy=False,  # phép liệt kê độc lập
)
print("Bằng chứng thực dùng:", result["bang_chung_bayes"])
print("Posterior Bayes:", result["xac_suat_bayes"])
print("Posterior kết hợp:", result["xac_suat_ket_hop"])
print("Điểm quyết định:", result["do_tin_cay_dieu_chinh"])
print("Kết luận:", result["trang_thai"], result["ket_luan"])
print("Ghi chú:", result["ghi_chu"])
```

Trong ví dụ:
- sáu dấu hiệu có trạng thái `co` được giữ thành sáu nút khác nhau;
- `thua_dam=khong` là bằng chứng phủ định tại `ThuaDam`, không suy ra đạm thấp;
- `vet_la_tam_xam_kho=chua_biet` không tạo bằng chứng;
- các nút chi tiết được tính theo CPD có cha, không bị gộp thành một trạng thái triệu chứng duy nhất.

Với CPD giả định hiện tại và `su_dung_pgmpy=False`, kết quả minh họa:
- Bằng chứng Bayes thực dùng: `BacBatDauChop=co`, `BacMepLuonSong=co`, `BacVetUngNuoc=co`, `DomTronBauDuc=co`, `DomVienSam=co`, `ThuaDam=khong`, `VetHinhThoi=co`.
- `vet_la_tam_xam_kho=chua_biet` bị bỏ qua, không tạo bằng chứng.
- Posterior Bayes bốn lớp: đạo ôn 20.08%, bạc lá 32.49%, đốm nâu 42.48%, lá khỏe 4.94%.
- Posterior sau kết hợp CNN: đạo ôn 37.94%, bạc lá 3.35%, đốm nâu 58.37%, lá khỏe 0.34%.
- Khối lượng đồng mắc: 97.11%; điểm quyết định: 1.69%; kết luận: `chua_du_chac`.

Các số trên chỉ là đầu ra tái lập từ CPD giả định và CNN top-3 giả lập, không phải rủi ro thực địa hay xác suất đã hiệu chuẩn.

## 10. Kiểm chứng và cách chạy

Trong luồng chung, `diagnose()` thu thập dữ kiện rồi gọi CNN–Bayes. Chỉ trả gợi
ý khi luật và xác suất cùng chọn một bệnh; bất đồng/thiếu chứng cứ trả None.
Điểm kỹ thuật hiển thị trong giải thích, `do_tin_cay` vẫn None. Mã cũ dạng
Mapping chỉ được nhận khi xác nhận Có; False/None/chua_biet được ghi chú và bỏ
qua. Top-3 phải giảm dần như hợp đồng predictor.

CPD DomNau hiện đặt mua_am cao hơn kho ở cùng mức dinh dưỡng (ví dụ 0.68 so
với 0.58 khi thiếu dinh dưỡng). Đây là giả định minh họa cần duyệt, không phải
kết luận định lượng từ S3. Đợt sửa tích hợp không thay các số CPD.

```bash
python -m src.rules.bayes --khong-pgmpy
python -m src.rules.ket_hop --khong-pgmpy
python -m pytest tests/test_tv3_probability.py -q
python -m pytest -q
```

Đường pgmpy yêu cầu đúng phiên bản trong `requirements.txt`:

```bash
python -m pip install pgmpy==0.1.25
python -c "import pgmpy; print(pgmpy.__version__)"
python -m pytest tests/test_tv3_probability.py -q
```

Test pgmpy gọi `check_model()`, kiểm tra tổng từng cột CPD và đối chiếu ba cặp truy vấn bằng chứng đối lập với phép liệt kê độc lập. Test luồng `predict_top3` dùng stub, không yêu cầu TensorFlow.

## 11. Giới hạn

CNN trong `src/model/predict.py` hiện là stub; CPD và ngưỡng chưa được hiệu chuẩn từ dữ liệu đồng ruộng. Mạng chỉ hỗ trợ danh sách thuộc tính công bố ở mục 3; các thuộc tính còn lại vẫn được giữ cho hệ luật nhưng không tham gia posterior Bayes. Kết quả chỉ phục vụ kiểm thử/tích hợp và tham khảo, không thay thế kiểm tra đồng ruộng hoặc kết luận chuyên môn.
