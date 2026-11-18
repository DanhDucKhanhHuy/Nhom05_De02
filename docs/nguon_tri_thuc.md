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

| Mã | Tài liệu / cơ quan | Năm | Căn cứ và giới hạn |
|---|---|---:|---|
| S1 | [Phòng trừ bệnh đạo ôn hại lúa](https://khuyennongvn.gov.vn/khoa-hoc-cong-nghe/khcn-trong-nuoc/phong-tru-benh-dao-on-hai-lua-21414.html); Trung tâm Khuyến nông Quốc gia | 2021 | Cập nhật ngày 20/08/2021. |
| S2 | [EPPO Datasheet: Xanthomonas oryzae pv. oryzae (XANTOR)](https://gd.eppo.int/taxon/XANTOR/datasheet); European and Mediterranean Plant Protection Organization (EPPO) | 2022 | Năm của phần Detection and Identification được xác minh bằng ngày cập nhật 16/06/2022; không dùng năm bản quyền website. Symptoms hỗ trợ BL01–BL04. Thay tệp tổng hợp tin báo năm 2012. Héo/cuộn lá có nguồn khoa học S7 bổ sung; BL06 trỏ S6. Đã mở ngày 18/11/2026. |
| S3 | [Louisiana Rice Production Handbook](https://www.lsuagcenter.com/~/media/system/9/0/e/9/90e93160aba5daccea90c6d955299f74/pub2331riceproductionhandbook2014completebook.pdf); LSU AgCenter, Louisiana State University Agricultural Center | 2014 | Bản mang tên tệp 2014; chương Disease Management, Brown Spot, trang in 91–92. Ngày 18/11/2026 đối chiếu được văn bản bản chỉ mục; URL trực tiếp trả 404, chưa kiểm chứng truy cập tải trực tiếp. Không tự chuyển sang ấn bản mới. Nguồn nêu dinh dưỡng, luân canh, đất và nước; mốc vụ sau của DN10 là giới hạn thiết kế. |
| S4 | [Hướng dẫn quản lý dịch hại lúa: bệnh đạo ôn](https://ipm.ucanr.edu/agriculture/rice/rice-blast/); Chương trình Quản lý dịch hại tổng hợp, Đại học California | 2024 | Trang ghi nội dung cập nhật 07/2024. |
| S5 | [Entrepreneurship Development Through Seed Production, Technical Bulletin TB-ICN 109/2013](https://www.iari.res.in/files/Publication/Others/EDSP_Eng-21102013.pdf); Indian Agricultural Research Institute (IARI), Regional Station, Karnal | 2013 | Trích dẫn chuẩn và dòng Printed: February, 2013 ở trang PDF 4 xác nhận năm. Bài Safe Seed Storage, trang in 28 / trang PDF 36, nêu chọn hạt sạch bệnh để gieo. Bổ sung căn cứ giai đoạn áp dụng BL06 cùng S6; không trích biện pháp hóa học, không dùng để đặt CPD. Đã đọc ngày 17/11/2026. |
| S6 | [ICAR Kharif Agro-Advisories for Farmers 2025](https://icar.gov.in/sites/default/files/2025-10/ICAR-En-Kharif-Agro-Advisories-for-Farmers-2025.pdf); Indian Council of Agricultural Research (ICAR) | 2025 | Ấn phẩm ghi năm 2025 theo hồ sơ ngày 17/11/2026. Dùng cho chọn giống của BL06. Lượt mở ngày 18/11/2026 bị timeout; trang ICAR thông báo bảo trì, chưa kiểm chứng lại nội dung tải trực tiếp. S5 hỗ trợ giai đoạn chọn giống; không đưa hóa chất vào luật. |
| S7 | [Xanthomonas oryzae pathovars: model pathogens of a model crop, Molecular Plant Pathology 7(5), 303–324](https://cropgeneticsinnovation.ucdavis.edu/sites/g/files/dgvnsk6996/files/inline-files/r0604.pdf); Iowa State University và University of California, Davis; bài của D. O. Niño-Liu, P. C. Ronald và A. J. Bogdanove | 2006 | Năm và DOI 10.1111/j.1364-3703.2006.00344.x ở trang in 303 / PDF 1. Trang in 306 / PDF 4 mô tả lá héo/cuộn ở giai đoạn tiến triển và cảnh báo dễ nhầm bạc lá với sọc lá vi khuẩn. Chỉ hỗ trợ BL05 ở mức cần kiểm tra, không xác nhận bệnh. Đã mở ngày 18/11/2026. |

Ngày rà soát: 18/11/2026. Có bảy nguồn; luật dùng trực tiếp S1–S4, S6, S7; S5 bổ sung giai đoạn chọn giống. S3 đọc được bản chỉ mục nhưng tải trực tiếp lỗi 404; S6 mở lại bị timeout. Các giới hạn này chưa hoàn tất nghiệm thu.

## Ma trận bệnh × thông tin và đối chiếu luật

| Bệnh / nhóm | Dữ kiện hoặc sự kiện | Luật | Nguồn, mục |
|---|---|---|---|
| Đạo ôn – triệu chứng lá | Hình thoi; tâm xám khô; viền nâu | DO01–DO03 | S1, mục 1; S4, triệu chứng trên lá |
| Đạo ôn – cổ lá, thân, bông | Cổ lá nâu đỏ; đốt teo nâu; cổ bông thối nâu; bông hoặc gié lép trắng cần kiểm tra | DO04–DO07 | S1, mục 1 |
| Đạo ôn – điều kiện thuận lợi | Âm u/sương sớm; thiếu nước; sạ dày; thừa đạm | DO08–DO11 | S1, mục 2 |
| Đạo ôn – khuyến nghị | Theo dõi ruộng thường xuyên, phát hiện bệnh sớm | DO12 | S1, mục 3 |
| Bạc lá – triệu chứng | Vệt úng nước đến vàng/trắng trên phiến lá; vệt bắt đầu ở chóp; mép lượn sóng; lá héo/cuộn cần kiểm tra | BL01–BL05 | S2, EPPO Symptoms (2022); BL05 dùng S7, trang in 306 (2006) |
| Bạc lá – khuyến nghị | Chọn hạt giống sạch bệnh khi chuẩn bị gieo trồng | BL06 | S6, hướng dẫn lúa, chọn hạt giống; S5 bổ sung giai đoạn chọn giống, trang in 28 / PDF 36 |
| Đốm nâu – hình dạng, vị trí | Đốm tròn/bầu dục, viền sẫm, tâm nhạt/xám; vết trên bẹ lá, diệp tiêu, vỏ trấu | DN01–DN04, DN06–DN07 | S3, mục Brown Spot, trang in 92 |
| Đốm nâu – giai đoạn/nguy cơ và ảnh hưởng hạt | Bệnh nặng hơn khi cây gần trưởng thành; ảnh hưởng diệp tiêu, bẹ, vỏ trấu, bông/hạt; hạt có thể nhẹ hoặc bạc phấn | DN05, DN08 | S3, mục Brown Spot, trang in 92 |
| Đốm nâu – khuyến nghị điều kiện canh tác | Quản lý dinh dưỡng, đất và nước phù hợp | DN09 | S3, mục Brown Spot, trang in 92 |
| Đốm nâu – luân canh | Luật hiện gắn điều kiện ruộng xác nhận nhiễm và thời điểm vụ tiếp theo | DN10 | S3 nêu luân canh là biện pháp quản lý đốm nâu nhưng không nêu điều kiện xác nhận nhiễm hoặc mốc vụ; hai giới hạn này do hệ thống đặt ra và chưa có căn cứ trực tiếp ở nguồn thay thế |

### Các sửa đổi về nguồn và thuật ngữ

- `DO07` chỉ hỏi dấu hiệu quan sát `bong_hoac_gie_lep_trang`, không yêu cầu
  người dùng biết trước bệnh hoặc thời điểm bệnh xuất hiện. S1 mô tả bông/gié
  lép trắng khi bệnh xuất hiện sớm; chiều quan sát ngược không xác nhận bệnh.
  Đây là quy tắc sàng lọc cần kiểm tra thêm, không phải dấu hiệu đặc hiệu hay
  luật xác nhận đạo ôn. Mã cũ `bong_lek_trang_khi_benh_xuat_hien_som` không tự
  chuyển sang mã mới; cần nhập lại quan sát theo câu hỏi mới.

- `DO01` và `DO03` không còn trỏ nhầm triệu chứng đạo ôn tới S2 (nguồn bạc lá).
  `DO01` trỏ S1, mục 1; `DO03` trỏ S4, mục triệu chứng trên lá.
- `DN04` mô tả đốm trên **bẹ lá** theo nguồn; `DN06` dùng **diệp tiêu (bao mầm)**,
  tương ứng bộ phận cây được mô tả là coleoptile; `DN08` mô tả ảnh hưởng lên hoa
  non và hạt. Không còn dùng “bao tử”.
- `BL02` chỉ hỏi vị trí bắt đầu của vệt; không còn khẳng định vệt tăng kích thước.
  `BL03` hỏi màu vệt quan sát được (vàng đến trắng); không gán vị trí mép/hoại
  tử hoặc khẳng định trình tự đổi màu. Cách hỏi khớp mô tả có năm của S2.
- `DN09` được đổi sang quản lý dinh dưỡng, đất và nước phù hợp theo S3. `DN10`
  giữ điều kiện ruộng đã xác nhận nhiễm và vụ kế tiếp như giới hạn thận trọng
  của hệ thống; S3 năm 2014 chỉ trực tiếp nêu luân canh là biện pháp quản lý,
  không nêu điều kiện xác nhận hoặc mốc vụ.
- `vet_bac_ung_nuoc_tren_phien_la` thay mã cũ `vet_bac_dau_la_uot_nuoc`:
  S2 mô tả vệt úng nước đến vàng trên phiến lá hoặc bắt đầu ở chóp; thuộc tính
  BL01 chỉ hỏi sự hiện diện trên phiến lá, còn vị trí bắt đầu được hỏi riêng ở
  BL02. BL03 chỉ hỏi màu vệt vàng đến trắng, không còn “vàng kim” hoặc “hoại tử
  ở mép” vì các chi tiết đó không được S2 hiện tại nêu trực tiếp.
- `DN08` dùng “hạt nhẹ hoặc bạc phấn” theo S3; không gọi là hạt lép hoặc “phôi bột”.
- `thua_dam=khong` chỉ dùng khi xác nhận lượng bón không vượt khuyến cáo;
  nếu chưa đủ căn cứ đối chiếu thì chọn `chua_biet`. Không suy ra thiếu đạm.
- `BL06`: S6 ghi hạt lúa được chứng nhận, sạch bệnh; S5 bổ sung căn cứ chọn hạt
  sạch bệnh để gieo: áp dụng khi chuẩn bị
  lần gieo trồng sắp tới, không phải điều trị cây đang bị bệnh. Chưa xác minh
  tháng/vụ lúa cụ thể cho địa phương Việt Nam; không tự đặt lịch mùa vụ.
- S2 là datasheet EPPO, mục triệu chứng cập nhật 16/06/2022; BL05 dùng S7.
  Không giữ tệp tổng hợp tin báo năm 2012 làm nguồn chuyên môn chuẩn.

### Dùng chung bằng chứng với mạng Bayes

Bayes có 22 nút và hỗ trợ 16/25 thuộc tính. Vệt úng nước vào BacVetUngNuoc;
hình thoi vào VetHinhThoi; âm u/sương sớm vào AmU_SuongSom; thừa đạm vào
ThuaDam. Có/Không vào hai trạng thái của cùng nút; Chưa biết/thiếu không tạo
evidence. Chín thuộc tính chưa hỗ trợ được giữ cho hệ luật và ghi chú ở Bayes.
Danh sách đầy đủ ở Q2 và ANH_XA_THUOC_TINH. Không còn nút TrieuChung gộp nhiều
dấu hiệu. Mã cũ chỉ tạo evidence khi xác nhận Có; False/None/chua_biet không
thành dương tính. Kết luận suy ra không được gửi lại như quan sát Bayes.

Mã lớp kết luận dùng thống nhất: `dao_on`, `bac_la`, `dom_nau`. `loai=chan_doan`
tạo `suy_luan=nghi_<ma_benh>`; `loai=khuyen_nghi` tạo một khuyến nghị có nguồn.
Các luật DO12, BL06 và DN09 tạo chuỗi hai bước từ triệu chứng đến nghi bệnh rồi
khuyến nghị. DN10 chỉ chạy khi dữ kiện người dùng xác nhận ruộng đã nhiễm bệnh;
không chạy từ `suy_luan=nghi_dom_nau`. DO08–DO11 và DN05 chỉ tạo yếu tố nguy cơ,
không xác nhận bệnh. DO07 và BL05 sinh dấu hiệu cần kiểm tra, không phải kết luận.

Lượt 18/11/2026 thay nguồn tin báo S2 bằng datasheet EPPO cập nhật 2022;
BL05 trích bài khoa học S7 (2006). S3 đọc được văn bản bản chỉ mục nhưng tải
trực tiếp lỗi; S6 mở lại bị timeout. Trạng thái truy cập ghi trong sources.json.

## Hồ sơ đối chiếu và nghiệm thu

[Phiếu đối chiếu từng luật](doi_chieu_luat.md) liệt kê đủ 28 id, mục nguồn,
căn cứ và giới hạn. Phân biệt nội dung mô tả trong nguồn với cách nhóm tổ chức
gợi ý, sàng lọc cần kiểm tra và kích hoạt khuyến nghị. Không tuyên bố nguồn
chứng minh mọi quan hệ ngược từ triệu chứng tới bệnh.

Phạm vi khuyến nghị: DO12 theo dõi trong vụ; BL06 chuẩn bị giống trước gieo
trồng; DN09 quản lý dinh dưỡng, đất và nước phù hợp; DN10 luân canh vụ sau khi vụ hiện tại đã
được xác nhận nhiễm. Phạm vi này cần giữ khi trình bày kết quả cho người dùng.
BL06 trích nguồn chính S6; S5 bổ sung giai đoạn chọn giống trong hồ sơ, không
được tự thêm vào vết như nguồn chính khác.

Hồ sơ đã đối chiếu nội dung và ghi rõ khoảng trống. Chưa có lịch mùa vụ địa phương
hoặc biên bản chuyên gia ký duyệt. DN10 chưa có căn cứ nguồn trực tiếp cho điều kiện
“đã xác nhận nhiễm” và mốc “vụ kế tiếp”. Cần khôi phục truy cập S3/S6 và duyệt các giới hạn nguồn; metadata có năm
không tự chứng minh mọi nội dung luật.

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
