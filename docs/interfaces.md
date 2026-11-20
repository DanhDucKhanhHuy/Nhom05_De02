# Giao tiếp giữa các module

Python 3.10/3.11; tọa độ `(hàng, cột)` bắt đầu từ 0. Kiểu chuẩn nằm trong
`src/contracts.py`. Tọa độ JSON là mảng; tọa độ trong kết quả Python là tuple.

## 1. Nhận diện: TV4 → TV2/TV3/TV5

```python
from pathlib import Path
from src.contracts import Top3

def predict_top3(duong_dan_anh: str | Path) -> Top3: ...
```

Module `src/model/predict.py`. Trả đúng 3 tuple `(mã_lớp, xác_suất)`, nhãn không
trùng, xác suất hữu hạn trong [0,1], sắp giảm dần. Tổng top 3 ≤1 vì còn lớp thứ tư.
Mã lớp: `dao_on`, `bac_la`, `dom_nau`, `la_khoe`.

Ví dụ **GIẢ**, chạy được với khung và không đọc ảnh:

```python
from src.model.predict import IS_STUB, predict_top3
assert IS_STUB is True
predict_top3("anh_chua_ton_tai.jpg")
# [("dao_on", 0.55), ("dom_nau", 0.40), ("bac_la", 0.03)]
```

Không dùng số giả để xác nhận bệnh hay báo cáo độ chính xác. TV4 thay hàm,
đặt `IS_STUB=False`, giữ hợp đồng và bổ sung test với ảnh/mô hình thực.
Bản thật dự kiến ném `FileNotFoundError` nếu thiếu ảnh/mô hình, `ValueError`
nếu ảnh hỏng. Bản giả hiện không kiểm tra các lỗi này.

## 2. Chẩn đoán: TV2 → TV5

```python
from src.contracts import ChanDoan, HoiNguoiDung, Top3

def diagnose(top3: Top3, hoi_nguoi_dung: HoiNguoiDung) -> ChanDoan: ...
```

Module `src/rules/diagnose.py`. Callback `(câu_hỏi: str) -> bool | None`:
True = có, False = không, None = chưa biết. Không xem chưa biết là phủ định.
Đầu ra gồm `ket_luan` (mã lớp hoặc None), `do_tin_cay` ([0,1] hoặc None),
`luat_da_dung` (list id), `nguon` (list chuỗi trích nguồn).
Không tự gán độ tin cậy nếu chưa có phương pháp định lượng.

Hai trường tùy chọn bổ sung tương thích: `giai_thich` (chuỗi tiếng Việt) và
`vet` (danh sách `VetLuat` mô tả các lần suy diễn thực tế). Bốn trường cũ giữ nguyên.
`diagnose()` cung cấp cả hai trường; `do_tin_cay=None` vì chưa có xác suất đã
hiệu chuẩn. CNN xếp thứ tự hỏi và tham gia CNN–Bayes; gợi ý cuối cần cả luật
và xác suất đồng thuận. Hàm kiểm tra cả ba bệnh, kể cả bệnh vắng trong top-3.
Sau suy diễn lùi, hàm hỏi các thuộc tính người dùng còn thiếu, dùng chung
dữ kiện cho tiến và Bayes. Không gửi kết luận suy ra như bằng chứng Bayes.

Ví dụ chạy với câu trả lời chưa biết:

```python
diagnose([("dao_on", 0.55), ("dom_nau", 0.40), ("bac_la", 0.03)],
         lambda cau_hoi: None)
# {"ket_luan": None, "do_tin_cay": None, "luat_da_dung": [], "nguon": [],
#  "giai_thich": "Chưa đủ chắc, liên hệ cán bộ khuyến nông. ...",
#  "vet": []}
```

Đầu vào sai ném `ValueError`. Chỉ chọn một gợi ý khi đúng một bệnh được chứng minh
và các bệnh khác bị bác bỏ trong bộ luật hiện tại, đồng thời CNN–Bayes cùng
chọn bệnh đó qua ngưỡng; bất đồng, dưới ngưỡng, hòa hoặc nhiều gợi ý thì
`ket_luan=None`. Không suy ra lá khỏe chỉ vì thiếu dấu hiệu bệnh. Callback được
nhớ theo thuộc tính trong cả phiên, không hỏi lại giữa các mục tiêu.
Kết luận, luật và nguồn trong báo cáo
phải từ tri thức đã kiểm chứng, không từ ví dụ ký hiệu của test.

Điểm kỹ thuật, ngưỡng và phương pháp Bayes được ghi trong `giai_thich`, không
gán vào `do_tin_cay`. Quyết định và giới hạn ở
[ADR-001](decisions/001-dieu-phoi-luat-bayes.md).

`src/app/chan_doan.py` cung cấp `diagnose_image(duong_dan_anh: str,
hoi_nguoi_dung: HoiNguoiDung) -> ChanDoan`. Hàm gọi predictor một lần, giữ lỗi
predictor. IS_STUB=True luôn trả ket_luan=None kèm giải thích GIẢ, không xác
nhận bệnh từ số giả. Không cần TensorFlow để thử luồng với predictor giả.

## 3. Lộ trình: TV1 → TV5

```python
from src.contracts import BanDo, LoTrinh, ThuatToan

def plan_route(ban_do: BanDo, k: int, p: int, thuat_toan: ThuatToan) -> LoTrinh: ...
```

Module `src/search/run.py`; thuật toán là `hill`, `beam` hoặc `greedy`.
k,p truyền vào ưu tiên hơn giá trị mặc định trong JSON. Không sửa bản đồ đầu vào.
Đầu vào sai hoặc không có hành trình hoàn tất dự kiến ném `ValueError`.
Hiện hàm luôn ném `NotImplementedError`.

Để so sánh A* toàn cục với tham lam gần nhất, chạy
`python -m src.search.experiment`. Mặc định dùng bản đồ mẫu; có thể truyền bản đồ
và ngân sách vào `run_experiment(ban_do, k, p)`. Hàm in và trả hai lộ trình cùng
các chỉ số `tong_quang_duong`, `so_lan_ve_tram`, `thoi_gian_chay`. A* toàn cục
tìm tối ưu theo quãng đường bay nhưng có thể tốn nhiều thời gian/bộ nhớ khi số ô
bệnh lớn; kết quả mặc định trên bản đồ 4 × 4 chỉ là minh họa, không đại diện cho
hiệu năng trên ruộng 20 × 20.

Ví dụ hợp đồng **chưa chạy được**, trường hợp hình thức không có ô bệnh:

```python
ban_do = {"rows": 1, "cols": 1, "start": [0, 0], "k": 1, "p": 2, "cells": [[9]]}
plan_route(ban_do, 1, 2, "hill")
# Hiện: raise NotImplementedError("chưa cài đặt")
# Kết quả hình thức mong đợi khi được triển khai:
# {"duong_di": [(0, 0)], "su_kien": [], "tong_quang_duong": 0,
#  "so_lan_ve_tram": 0, "thoi_gian_chay": <số giây đo thực tế>}
```

`duong_di` gồm ô bắt đầu và đích từng bước bay, giữ cả ô lặp lại.
`su_kien` theo thứ tự thực thi, mỗi phần tử có `loai` và `vi_tri`:

```python
# Minh họa định dạng, không phải hành trình đã tính:
{"loai": "bay", "vi_tri": (0, 1)}
{"loai": "phun", "vi_tri": (0, 1)}
{"loai": "nap", "vi_tri": (0, 0)}
```

Bay tới ô kề 4 hướng; phun/nạp tại vị trí hiện tại. Ban đầu đã đủ thuốc/pin nên
không cần nạp đầu. `tong_quang_duong` bằng tổng số ô lưới bay qua. Mỗi sự kiện `bay` có thêm
`quang_duong`, `pin_tieu_hao` và `qua_vat_can`; khi vượt vật cản, pin tiêu hao
bao gồm 1 pin phụ cho mỗi ô vật cản và `duong_di` vẫn liệt kê ô đã bay qua.
`so_lan_ve_tram` đếm
mỗi bước bay đáp xuống ô 9, kể cả lần về cuối; không tính vị trí đầu hoặc nạp
đứng yên. `thoi_gian_chay` là giây đo thật ≥0. Xem `mo_hinh_bai_toan.md` về an toàn.

## 4. Schema bản đồ JSON

Đối tượng gồm `rows`, `cols` nguyên dương, `start` là [hàng,cột], `k`, `p`
nguyên dương và `cells` là ma trận số nguyên rows × cols. Không nhận boolean
thay cho số nguyên. start trong lưới và phải là trạm. Cho phép nhiều trạm.

- 0: lúa khỏe.
- 1, 2, 3: mức bệnh; mỗi ô chỉ cần phun một lần.
- −1: vật cản, không được hạ cánh; có thể bay vượt qua và tốn thêm 1 pin cho
  mỗi ô vật cản bị vượt.
- 9: trạm nạp thuốc và pin.

Ví dụ đầy đủ: `data/sample/maps/map_4x4.json`, chép bản minh họa README,
không phải khảo sát ruộng thật. Bản đồ đánh giá chính thức tối thiểu 20 × 20;
lưới nhỏ chỉ phục vụ test/demo. TV1 cài kiểm tra schema và khả thi.

## 5. Schema luật, nguồn và từ vựng

`src/rules/rules.json` có danh sách `rules`. Mỗi luật có đúng năm trường:

- `id`: chuỗi duy nhất.
- `loai`: `chan_doan`, `nguy_co`, `trung_gian` hoặc `khuyen_nghi`.
- `neu`: danh sách sự kiện không rỗng, kết hợp bằng AND.
- `thi`: một sự kiện được suy ra.
- `nguon`: đối tượng `{ "ma": "S1", "muc": "Mục 1, triệu chứng trên lá" }`.

Sự kiện có dạng `thuoc_tinh=gia_tri`. Ví dụ kiểm thử ký hiệu:

```json
{"id":"T1","loai":"chan_doan","neu":["vet_la_hinh_thoi=co"],
 "thi":"suy_luan=nghi_dao_on","nguon":{"ma":"S1","muc":"Mục 1"}}
```

`src/rules/vocabulary.json` khai báo toàn bộ thuộc tính và giá trị. Thuộc tính
`du_kien_nguoi_dung` phải có câu hỏi tiếng Việt và lựa chọn Có/Không/Chưa biết;
`su_kien_suy_ra` chỉ do luật tạo.
`co` xác nhận toàn bộ mệnh đề thuộc tính; `khong` phủ định đúng mệnh đề đó;
`chua_biet` là chưa xác định. Thuộc tính không có dữ kiện không đồng nghĩa với
`khong`. Nếu câu hỏi ghép nhiều dấu hiệu, từ vựng khai báo phép AND/OR và giải
thích cách chọn Có. Với mệnh đề AND, `khong` không cho biết thành phần nào sai;
không được suy ngược thành trạng thái trái ngược của từng thành phần.
`src/rules/sources.json` ánh xạ mã nguồn tới tên tài liệu, cơ quan, năm (hoặc
ghi rõ năm chưa xác định) và URL. Mục trích dẫn cụ thể nằm trong `nguon.muc`.
Ánh xạ sang Bayes chỉ dùng khi trạng thái có cùng nghĩa; bằng chứng không tương
đương hoặc phủ định mơ hồ được ghi chú và bỏ qua, không tự đổi sang trạng thái
đối lập.

`python -m scripts.check_rules` kiểm tra schema, id duy nhất, tối thiểu 20 luật,
mã nguồn tồn tại, từ vựng/giá trị, đủ luật chẩn đoán và khuyến nghị cho ba bệnh,
chu trình, chuỗi nhiều bước, nội dung và đơn vị bị cấm. Vi phạm tiêu chí bắt
buộc trả mã thoát khác 0. Script không xác nhận nguồn có thật sự chứng minh
từng luật; cần duyệt thủ công theo `docs/nguon_tri_thuc.md`.

## 6. Giao tiếp nội bộ phục vụ test

- `astar(cells: list[list[int]], start: ToaDo, goal: ToaDo) -> list[ToaDo] | None`:
  đường gồm hai đầu; None khi không tới; start=goal trả [start].
- `forward(facts: set[str], rules: list[Luat]) -> set[str]`: bao đóng gồm facts.
- `backward(goal: str, facts: set[str], rules: list[Luat],
  hoi_nguoi_dung: HoiNguoiDung) -> bool`: True khi chứng minh được; False khi
  chưa chứng minh được, không đồng nghĩa phủ định y học.

API bổ sung, không thay chữ ký hoặc kiểu trả về của hai hàm cũ:

- `forward_with_trace(facts, rules) -> tuple[set[str], list[VetLuat]]`: trả bao đóng
  và vết theo thứ tự thêm sự kiện mới; không bắn lại kết luận đã biết.
- `backward_with_status(goal, facts, rules, hoi_nguoi_dung) -> KetQuaSuyDienLui`:
  trả `trang_thai` và `vet` của nhánh chứng minh thành công.
- `VetLuat` gồm `id`, `dieu_kien` (list sự kiện), `ket_luan`, `nguon` (`ma`, `muc`).
  Điều kiện và nguồn được sao chép, sửa vết không sửa luật gốc.
- `trang_thai`: `xac_nhan` khi chứng minh được; `bac_bo` khi mọi nhánh bị dữ kiện
  bác bỏ rõ; `chua_du` khi thiếu dữ kiện, có câu trả lời None, không có luật hỗ trợ
  hoặc chỉ có chu trình chưa chứng minh được. Bác bỏ đích không phải chẩn đoán
  không bệnh ngoài thực tế.
- AND: một điều kiện bác bỏ thì cắt sớm; ở API ba trạng thái, gặp chưa biết vẫn
  xét điều kiện tiếp theo vì có thể tìm được phủ định rõ. OR: một nhánh xác nhận
  là đủ; nếu chưa thành công mà còn nhánh chưa đủ thì không được trả bác bỏ.
- `backward()` cũ vẫn cắt sớm cả khi chưa chứng minh được một điều kiện AND,
  giữ số câu hỏi theo hành vi cũ. Cả hai API chỉ hỏi thuộc tính hỏi được, mỗi thuộc
  tính một lần trong một lời gọi và không sửa facts/rules đầu vào.
- None không khớp `co` hoặc `khong`; chỉ khớp nếu đích yêu cầu rõ `chua_biet`.

Test thuật toán xfail chỉ khi NotImplementedError; kết quả sai vẫn fail. Khi
hàm đạt, bỏ dấu xfail tương ứng và giữ các kiểm tra. XPASS là lỗi để nhắc cập nhật
trạng thái. BFS chỉ nằm trong tests, không phải mã CN1.
