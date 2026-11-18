# Phiếu đối chiếu 28 luật CN2

Ngày đối chiếu: 18/11/2026. Dữ liệu chuẩn là `src/rules/rules.json`,
`src/rules/vocabulary.json` và `src/rules/sources.json`.

## Phương pháp và ý nghĩa trạng thái

Lượt cập nhật 18/11/2026 giữ nguyên phân biệt mô tả nguồn với lựa chọn mô hình
của nhóm. Luật chan_doan chỉ tạo nghi bệnh; không có độ nhạy/đặc hiệu đã đo.
S2 nay là datasheet EPPO (mục triệu chứng cập nhật 2022), BL05 dùng S7 (2006).
Nội dung S3 đọc được từ bản chỉ mục nhưng URL tải trực tiếp lỗi 404; S6 mở lại
bị timeout. Chưa có xác nhận chuyên gia địa phương hoặc thử nghiệm thực địa.
Trang PDF được đếm từ 1; số trang in được ghi riêng khi khác.

## Đạo ôn: DO01–DO12

- **DO01** — `vet_la_hinh_thoi=co` → nghi đạo ôn. S1, mục 1, đoạn trên lá:
  hình dạng vết được mô tả. Chỉ là gợi ý, không xác nhận nguyên nhân.
- **DO02** — `vet_la_tam_xam_kho=co` → nghi đạo ôn. S1, mục 1, đoạn trên lá:
  mô tả phần giữa hoại tử, khô xám. Không khẳng định dấu hiệu đặc hiệu.
- **DO03** — `vet_la_vien_nau=co` → nghi đạo ôn. S4, Symptoms / Leaf Symptoms:
  có mô tả viền nâu. Không coi riêng màu viền là chẩn đoán xác định.
- **DO04** — `vet_co_la_nau_do=co` → nghi đạo ôn. S1, mục 1, đoạn cổ lá:
  có vị trí và màu vết tương ứng. Không thêm diễn biến thời gian vào điều kiện.
- **DO05** — `dot_than_teo_nau=co` → nghi đạo ôn. S1, mục 1, đoạn đốt thân:
  màu nâu và teo đốt. Câu trả lời Có phải xác nhận đủ hai phần.
- **DO06** — `co_bong_thoi_nau=co` → nghi đạo ôn. S1, mục 1, đoạn cổ bông/
  cổ gié: vết nâu, thối tóp. Chỉ suy ra gợi ý.
- **DO07** — `bong_hoac_gie_lep_trang=co` → cần kiểm tra đạo ôn. S1, mục 1,
  đoạn cổ bông/cổ gié: khi bệnh xuất hiện sớm, bông hoặc gié có thể lép trắng.
  Câu hỏi hiện tại chỉ thu thập dấu hiệu quan sát được, không yêu cầu người dùng
  biết trước bệnh hoặc thời điểm khởi phát. Chuyển dấu hiệu này thành yêu cầu
  kiểm tra là lựa chọn sàng lọc của hệ thống, không phải xác nhận bệnh.
- **DO08** — `am_u_va_suong_som=co` → yếu tố nguy cơ đạo ôn. S1, mục 2.
  Dùng tổ hợp AND đã khai báo, không khẳng định tổ hợp này là điều kiện duy nhất.
- **DO09** — `ruong_thieu_nuoc=co` → yếu tố nguy cơ đạo ôn. S1, mục 2.
  Không suy ra thời tiết khô hoặc bệnh đã xuất hiện.
- **DO10** — `sa_day=co` → yếu tố nguy cơ đạo ôn. S1, mục 2.
  Không tự đặt ngưỡng định lượng mật độ gieo sạ.
- **DO11** — `thua_dam=co` → yếu tố nguy cơ đạo ôn. S1, mục 2.
  Không tự đặt lượng bón; dữ kiện chưa biết không thành phủ định.
- **DO12** — nghi đạo ôn → theo dõi ruộng thường xuyên. S1, mục 3.
  Áp dụng theo dõi trong vụ; không kèm khuyến cáo hóa học.

## Bạc lá: BL01–BL06

- **BL01** — `vet_bac_ung_nuoc_tren_phien_la=co` → nghi bạc lá. S2,
  Detection and Identification / Symptoms (cập nhật 16/06/2022). Không tự thêm vị trí bắt đầu ở mép lá.
- **BL02** — `vet_bac_bat_dau_o_chop_la=co` → nghi bạc lá. S2, cùng mục.
  Chỉ dùng vị trí bắt đầu; không thêm quy luật tăng kích thước.
- **BL03** — `vet_la_vang_den_trang=co` → nghi bạc lá. S2 ghi
  tổn thương chuyển vàng đến trắng; thuộc tính hiện chỉ hỏi màu vệt quan sát,
  không gán vị trí mép/hoại tử hoặc khẳng định trình tự bệnh.
- **BL04** — `vet_bac_mep_luon_song=co` → nghi bạc lá. S2, cùng mục.
  Mô tả mép vệt; không coi riêng dấu hiệu này là xác nhận bệnh.
- **BL05** — `la_heo_hoac_cuon_lai=co` → cần kiểm tra bạc lá. S7, trang
  in 306 / PDF 4 mô tả héo/cuộn và cảnh báo nhầm bạc lá với sọc lá vi khuẩn.
  Chỉ yêu cầu kiểm tra, không xác nhận bệnh.
- **BL06** — nghi bạc lá → chọn hạt giống sạch bệnh. S6, phần hướng dẫn lúa,
  khuyến nghị dùng hạt được chứng nhận và sạch bệnh; S5, bài Safe Seed Storage,
  trang in 28 / PDF 36, bổ sung giai đoạn chọn giống để gieo. Dùng cho chuẩn bị
  lần gieo trồng sắp tới; không diễn giải là điều trị cây đang bệnh. Việc nhắc
  biện pháp khi nghi bệnh là cách tổ chức tư vấn của hệ thống, không phải điều
  kiện nguồn bắt buộc.

### Phạm vi giai đoạn của BL06

S5 có năm 2013 trong trích dẫn chuẩn ở PDF 4; nội dung chọn giống ở PDF 36.
Đây là căn cứ bổ sung chung về chọn giống, không xác nhận tháng/vụ lúa cụ thể
cho Việt Nam. S6 là nguồn chính cho khuyến nghị của BL06; S2 chỉ hỗ trợ triệu
chứng bạc lá. Không gán năm 2013 cho S2.
Khi tích hợp giao diện, cần hiển thị rõ giai đoạn chuẩn bị gieo trồng.

## Đốm nâu: DN01–DN10

- **DN01** — `dom_tron_hoac_bau_duc_nau=co` → nghi đốm nâu. S3, Symptoms:
  hình dạng và màu tương ứng. Không khẳng định độc quyền triệu chứng.
- **DN02** — `dom_nau_vien_sam=co` → nghi đốm nâu. S3, Symptoms,
  mô tả viền đốm. Chỉ là gợi ý.
- **DN03** — `dom_nau_tam_nhat_xam=co` → nghi đốm nâu. S3, Symptoms,
  phần tâm đốm. Giữ thuật ngữ nâu đỏ nhạt hoặc xám.
- **DN04** — `dom_nau_tren_be_la=co` → nghi đốm nâu. S3, Symptoms,
  đoạn về bẹ lá. Không nhầm bẹ lá với phiến lá.
- **DN05** — `cay_gan_truong_thanh_la_gia_hoa=co` → yếu tố nguy cơ đốm nâu.
  S3, Plant parts and life stages affected. Đây là bối cảnh bệnh phổ biến hơn,
  không chứng minh già hóa là nguyên nhân bệnh.
- **DN06** — `dom_nau_tren_diep_tieu=co` → cần kiểm tra đốm nâu. S3,
  Symptoms, đoạn diệp tiêu. Không dùng từ bao tử.
- **DN07** — `dom_nau_tren_vo_trau=co` → nghi đốm nâu. S3, Symptoms,
  đoạn vỏ trấu. Không đồng nhất mọi dạng đổi màu hạt với bệnh này.
- **DN08** — `hat_nhe_hoac_bac_phan=co` → nghi đốm nâu. S3, Symptoms,
  đoạn ảnh hưởng khi hoa non bị tấn công. Dấu hiệu hạt không xác nhận nguyên
  nhân; không suy ra hoa đã bị nhiễm chỉ từ ngoại hình hạt.
- **DN09** — nghi đốm nâu → quản lý dinh dưỡng, đất và nước phù hợp. S3,
  chương Disease Management, mục Brown Spot, nêu duy trì điều kiện sinh trưởng
  tốt bằng bón phân phù hợp, luân canh, san phẳng ruộng, chuẩn bị đất và quản
  lý nước. Thời điểm áp dụng theo vụ đang canh tác là cách trình bày của hệ
  thống; nguồn nêu đây là biện pháp giảm thiệt hại, không gắn riêng với lúc
  vừa phát hiện triệu chứng.
- **DN10** — `ruong_xac_nhan_nhiem_dom_nau=co` → cân nhắc luân canh ở vụ kế tiếp.
  S3 nêu luân canh trong nhóm biện pháp quản lý đốm nâu, nhưng không nêu riêng
  điều kiện “ruộng hiện tại đã nhiễm” hoặc mốc “vụ kế tiếp”; điều kiện kích hoạt
  xác nhận và mốc vụ là giới hạn thận trọng/cách tổ chức của hệ thống, chưa được
  nguồn thay thế xác nhận trực tiếp.

## Hồ sơ nguồn và việc chưa xác minh

- S1: cơ quan khuyến nông, cập nhật 2021.
- S2: datasheet EPPO; mục triệu chứng cập nhật 16/06/2022. Thay tệp tổng hợp tin
  báo năm 2012. Năm thuộc phần nội dung được dùng, không phải bản quyền web.
- S3: giữ ấn bản ghi trong hồ sơ. Đối chiếu được Brown Spot từ văn bản bản chỉ
  mục (trang in 91–92), nhưng tải trực tiếp lỗi 404. Chưa khôi phục liên kết tải.
- S4: UC IPM, nội dung cập nhật 07/2024.
- S5: IARI, năm 2013 ở trích dẫn chuẩn.
- S6: ICAR 2025 theo hồ sơ; ngày 18/11 mở lại timeout, website thông báo bảo trì.
- S7: bài khoa học năm 2006 lưu trên UC Davis, DOI và cơ quan tác giả ở PDF 1.

Không thay tài liệu bằng một ấn bản khác chỉ để sửa URL. Không đưa thông tin
ảnh thiếu nguồn hoặc giấy phép vào hồ sơ như đã xác minh. Luật vẫn chỉ là mô
hình gợi ý và sàng lọc; chưa có biên bản chuyên gia địa phương ký duyệt.
