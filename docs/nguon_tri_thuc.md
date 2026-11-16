# Tri thức hệ luật CN2

## Cách biểu diễn

`src/rules/rules.json` dùng schema thống nhất gồm `id`, `loai`, `neu`, `thi` và
`nguon`. Mỗi sự kiện có dạng `thuoc_tinh=gia_tri`; nhiều phần tử `neu` được nối
bằng AND. `nguon` là đối tượng `{ "ma": "S1", "muc": "..." }`, trỏ tới mã
nguồn và mục cụ thể trong `src/rules/sources.json`.

`src/rules/vocabulary.json` phân biệt dữ kiện người dùng (`du_kien_nguoi_dung`)
với sự kiện suy ra (`su_kien_suy_ra`). Mọi câu hỏi đầu vào có câu hỏi tiếng Việt,
các lựa chọn Có/Không/Chưa biết. “Chưa biết” không được hiểu là Không. Sự kiện
suy ra không tạo câu hỏi cho người dùng.

`co` xác nhận toàn bộ mệnh đề được hỏi; `khong` phủ định đúng mệnh đề đó;
`chua_biet` là chưa xác định. Không có dữ kiện thì không thêm sự kiện phủ định.
Với câu hỏi ghép, `phep_ghep` và `dien_giai_ghep` ghi rõ AND/OR; với AND, trả lời
Không chỉ nói tổ hợp không đúng, không cho biết thành phần nào sai. Các loại suy
ra `suy_luan`, `yeu_to_nguy_co`, `can_kiem_tra` và `khuyen_nghi` được giữ riêng.

Các luật chẩn đoán chỉ tạo gợi ý nghi bệnh; không có ngưỡng hoặc cụm “khả năng
cao”. Luật khuyến nghị chỉ chứa biện pháp canh tác được trích nguồn. Bộ luật
không chứa tên sản phẩm, hoạt chất, liều lượng hoặc nồng độ.

## Danh mục nguồn

| Mã | Tài liệu, cơ quan | Năm | Phần dùng và cách đối chiếu |
|---|---|---:|---|
| S1 | “Phòng trừ bệnh đạo ôn hại lúa”, Trung tâm Khuyến nông Quốc gia. [Trang tài liệu](https://khuyennongvn.gov.vn/khoa-hoc-cong-nghe/khcn-trong-nuoc/phong-tru-benh-dao-on-hai-lua-21414.html) | 2021 | Mục 1: vết lá, cổ lá, đốt thân, cổ bông. Mục 2: điều kiện thuận lợi. Mục 3: vệ sinh đồng ruộng, theo dõi và phát hiện sớm. Trang ghi cập nhật ngày 20/08/2021. |
| S2 | “Bệnh bạc lá vi khuẩn trên lúa”, Đại học Nông nghiệp Tamil Nadu (TNAU), cổng Agritech – Crop Protection. [Trang HTML](https://www.agritech.tnau.ac.in/expert_system/paddy/cpdisblb.html) | **Thiếu năm xuất bản xác minh** | Mục Symptoms: vệt úng nước đến vàng trên phiến lá hoặc bắt đầu ở chóp, mép lượn sóng; vùng hoại tử ở mép vàng trắng hoặc vàng kim. Không suy diễn trình tự đổi màu hay tăng kích thước từ mục này. Mục Cultural methods: hạt giống sạch bệnh. Trang không ghi năm xuất bản; danh mục máy chủ ghi ngày tệp 17/11/2020, không dùng ngày này làm năm xuất bản. |
| S3 | “Bệnh đốm nâu”, Viện Nghiên cứu và Phát triển Lúa, Bộ Nông nghiệp Sri Lanka. [Trang tài liệu](https://doa.gov.lk/rrdi_ricediseases_brownspot/) | **Không ghi năm** | Mục Triệu chứng: đốm trên bẹ lá, diệp tiêu, vỏ trấu; hoa non bị bệnh có thể làm hạt phát triển kém hoặc nhẹ/dạng phấn. Mục điều kiện phát sinh và quản lý bệnh: cây gần trưởng thành, lá già hóa; cỏ dại trong vụ; luân canh cho vụ tiếp theo. Trang không nêu ngày xuất bản; © 2026 là năm bản quyền website, không xác nhận năm xuất bản tài liệu. |
| S4 | “Hướng dẫn quản lý dịch hại lúa: bệnh đạo ôn”, Chương trình Quản lý dịch hại tổng hợp, Đại học California. [Trang tài liệu](https://ipm.ucanr.edu/agriculture/rice/rice-blast/) | 2024 | Mục Triệu chứng trên lá: vết hình thoi, tâm xám/trắng, viền nâu. Trang ghi nội dung cập nhật 07/2024. |

Ngày rà soát nguồn: 16/11/2026. Bộ luật dùng bốn tài liệu từ cơ quan/đơn vị
nghiên cứu và khuyến nông phù hợp. S2 và S3 chưa xác định được năm xuất bản;
thông tin này được ghi rõ là thiếu, không suy đoán năm. Dấu thời gian tệp S2
trên danh mục máy chủ và © 2026 trên trang S3 không được xem là năm xuất bản.
Các nguồn ngoài Việt Nam
chỉ dùng cho mô tả triệu chứng hoặc canh tác chung; cần chuyên gia địa phương
rà soát trước khi áp dụng thực tế.

## Ma trận bệnh × thông tin và đối chiếu luật

| Bệnh / nhóm | Dữ kiện hoặc sự kiện | Luật | Nguồn, mục |
|---|---|---|---|
| Đạo ôn – triệu chứng lá | Hình thoi; tâm xám khô; viền nâu | DO01–DO03 | S1, mục 1; S4, triệu chứng trên lá |
| Đạo ôn – cổ lá, thân, bông | Cổ lá nâu đỏ; đốt teo nâu; cổ bông thối nâu; bông lép trắng sớm cần kiểm tra | DO04–DO07 | S1, mục 1 |
| Đạo ôn – điều kiện thuận lợi | Âm u/sương sớm; thiếu nước; sạ dày; thừa đạm | DO08–DO11 | S1, mục 2 |
| Đạo ôn – khuyến nghị | Theo dõi ruộng thường xuyên, phát hiện bệnh sớm | DO12 | S1, mục 3 |
| Bạc lá – triệu chứng | Vệt úng nước đến vàng trên phiến lá; vệt bắt đầu ở chóp; vùng hoại tử vàng trắng/vàng kim ở mép; mép lượn sóng; héo mạ cần kiểm tra | BL01–BL05 | S2, mục Triệu chứng |
| Bạc lá – khuyến nghị | Sử dụng hạt giống sạch bệnh | BL06 | S2, mục Biện pháp canh tác |
| Đốm nâu – hình dạng, vị trí | Đốm tròn/bầu dục, viền sẫm, tâm nhạt/xám; vết trên bẹ lá, diệp tiêu, vỏ trấu | DN01–DN04, DN06–DN07 | S3, mục Triệu chứng |
| Đốm nâu – giai đoạn/nguy cơ và ảnh hưởng hạt | Bệnh phổ biến hơn khi cây gần trưởng thành/lá bắt đầu già hóa; hoa non nhiễm có thể làm cản trở phát triển hạt hoặc tạo hạt nhẹ/bạc phấn | DN05, DN08 | S3, mục bộ phận cây/giai đoạn bị ảnh hưởng; mục Triệu chứng |
| Đốm nâu – khuyến nghị trong vụ | Quản lý cỏ dại trong vụ hiện tại | DN09 | S3, mục Quản lý bệnh trong vụ |
| Đốm nâu – khuyến nghị cho vụ tiếp theo | Chỉ khi ruộng đã được xác nhận nhiễm: cân nhắc luân canh ở vụ tiếp theo | DN10 | S3, mục Disease Management, điều kiện “If the crop is infected” và danh sách biện pháp cho next season |

### Các sửa đổi về nguồn và thuật ngữ

- `DO01` và `DO03` không còn trỏ nhầm triệu chứng đạo ôn tới S2 (nguồn bạc lá).
  `DO01` trỏ S1, mục 1; `DO03` trỏ S4, mục triệu chứng trên lá.
- `DN04` mô tả đốm trên **bẹ lá** theo nguồn; `DN06` dùng **diệp tiêu (bao mầm)**,
  tương ứng bộ phận cây được mô tả là coleoptile; `DN08` mô tả ảnh hưởng lên hoa
  non và hạt. Không còn dùng “bao tử”.
- `BL02` chỉ hỏi vị trí bắt đầu của vệt; không còn khẳng định vệt tăng kích thước.
  `BL03` hỏi màu vùng hoại tử quan sát được ở mép lá; không khẳng định có trình
  tự chuyển màu theo thời gian. Hai dấu hiệu được diễn đạt theo mô tả S2.
- `DN09` giới hạn quản lý cỏ dại trong vụ. `DN10` tách luân canh thành khuyến
  nghị cho vụ tiếp theo; luật DN10 hỏi riêng ruộng đã được xác định nhiễm để
  không biến “nghi bệnh” thành “đã nhiễm”. Câu hỏi xác nhận là điều kiện an toàn
  của hệ thống; S3 chỉ yêu cầu ruộng bị nhiễm, không quy định ai xác nhận.
- `vet_bac_ung_nuoc_tren_phien_la` thay mã cũ `vet_bac_dau_la_uot_nuoc`:
  S2 mô tả vệt úng nước đến vàng trên phiến lá hoặc bắt đầu ở chóp; thuộc tính
  BL01 chỉ hỏi sự hiện diện trên phiến lá, còn vị trí bắt đầu được hỏi riêng ở
  BL02.
- `DN08` dùng “hạt nhẹ hoặc bạc phấn” theo S3; không gọi là hạt lép hoặc “phôi bột”.
- `BL06`: S2 có khuyến nghị dùng hạt giống sạch bệnh nhưng không chỉ rõ thời điểm
  mùa vụ; thời điểm áp dụng vẫn chưa được nguồn xác minh.
- `S2` không ghi năm xuất bản; `S3` cũng không ghi năm. Không dùng ngày tệp máy
  chủ hoặc năm bản quyền trang thay cho năm xuất bản.

### Dùng chung bằng chứng với mạng Bayes

Bayes chỉ nhận ánh xạ được ghi trong `src/rules/bayes.py` khi khái niệm trùng
trạng thái nút. Vệt úng nước trên phiến lá và đốm tròn/bầu dục có ánh xạ triệu
chứng; điều kiện âm u **và** sương sớm chỉ có thể ánh xạ sang thời tiết ẩm khi
cả hai cùng được xác nhận; thừa đạm chỉ ánh xạ sang đạm cao khi được xác nhận.
Các dấu hiệu không khớp loại triệu chứng tổng quát của Bayes được bỏ qua và ghi
chú. `am_u_va_suong_som=khong` không trở thành trời khô; `thua_dam=khong` không
trở thành đạm thấp. Điều kiện ruộng thiếu nước không đồng nghĩa với thời tiết khô.

Mã lớp kết luận dùng thống nhất: `dao_on`, `bac_la`, `dom_nau`. `loai=chan_doan`
tạo `suy_luan=nghi_<ma_benh>`; `loai=khuyen_nghi` tạo một khuyến nghị có nguồn.
Các luật DO12, BL06 và DN09 tạo chuỗi hai bước từ triệu chứng đến nghi bệnh rồi
khuyến nghị. DN10 chỉ chạy khi dữ kiện người dùng xác nhận ruộng đã nhiễm bệnh;
không chạy từ `suy_luan=nghi_dom_nau`. DO08–DO11 và DN05 chỉ tạo yếu tố nguy cơ,
không xác nhận bệnh. DO07 và BL05 sinh dấu hiệu cần kiểm tra, không phải kết luận.

## Câu hỏi Q4 – Vì sao phải truy vết luật và nguồn?

Mỗi gợi ý cần truy ngược được tới các dữ kiện đã nhập, id luật đã khớp và mục
tài liệu hỗ trợ. Cách làm này giúp người dùng kiểm tra căn cứ, giúp nhóm phát
hiện luật dùng sai phạm vi và cập nhật tri thức có kiểm soát. Việc ghi nguồn
không tự chứng minh luật đúng; nguồn vẫn cần được đối chiếu và rà soát chuyên
môn. Xem phần trả lời dùng cho báo cáo tại `docs/cau_hoi/Q4.md`.

## Giới hạn

Bộ luật có 28 luật và bao phủ ba bệnh mục tiêu ở mức gợi ý. Chưa có kiểm định
thực địa hay số liệu đo độ chính xác; không gán xác suất hoặc khẳng định bệnh
chắc chắn. Công cụ kiểm tra cấu trúc, nguồn, từ vựng, số luật, chu trình và
chuỗi suy diễn; việc nguồn có thực sự hỗ trợ từng phát biểu vẫn cần con người
đối chiếu.
