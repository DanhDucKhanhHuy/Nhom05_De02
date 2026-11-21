# Bác sĩ Lúa

Ứng dụng giúp nông dân Đồng bằng sông Cửu Long phát hiện sớm bệnh trên lá lúa, nhận tư vấn xử lý và lập lộ trình cho drone phun thuốc đúng những ô ruộng bị bệnh.

Đồ án cuối kỳ – Học kỳ 1, năm học 2026 – 2027 · Thời gian thực hiện: 02/11 – 06/12/2026

> **Trạng thái:** CN2 có 28 luật, suy diễn tiến/lùi, Bayes và luồng chẩn đoán kết hợp giữ nguyên API. CN3 đã huấn luyện CNN tự thiết kế và MobileNetV2, đánh giá trên test độc lập (MobileNetV2 accuracy 0,9005; F1 macro 0,8893), và chạy `predict_top3` thật trên 20 ảnh. Artifact `.keras` bị loại khỏi Git, cần đóng gói hoặc liên kết khi nộp. Nhãn ảnh thực tế chưa được xác minh độc lập. CN1 có tham lam và A* toàn cục, `plan_route` chưa ghép. Ứng dụng Pygame có bản đồ lưới, hoạt cảnh lộ trình và màn hình chẩn đoán ảnh. Xem `docs/kiem_chung.md` và `tasks/todo.md`.

---

## 1. Bài toán

Đồng bằng sông Cửu Long làm ra hơn một nửa sản lượng lúa cả nước. Mỗi vụ, bà con phải đối mặt với các bệnh như đạo ôn, bạc lá, đốm nâu; phát hiện muộn vài ngày có thể mất cả ruộng, trong khi cán bộ khuyến nông không thể có mặt ở mọi cánh đồng.

Luồng sử dụng của Bác sĩ Lúa:

1. Nông dân chụp ảnh lá lúa và tải lên ứng dụng.
2. Mô hình CNN nhận diện bệnh, trả về 3 bệnh có xác suất cao nhất.
3. Hệ chuyên gia hỏi thêm vài triệu chứng (suy diễn lùi) để xác nhận, rồi đưa ra kết luận kèm giải thích và khuyến nghị có ghi nguồn.
4. Người dùng đánh dấu các ô ruộng bị bệnh trên bản đồ lưới; hệ thống lập lộ trình drone và hiển thị hoạt cảnh từng bước.

## 2. Chức năng

| # | Chức năng | Kỹ thuật chính | Thư mục |
|---|-----------|----------------|---------|
| 1 | Lập lộ trình drone phun thuốc | Mô hình hóa không gian trạng thái; **tự cài đặt** A* cho từng chặng; leo đồi hoặc beam search chọn thứ tự ghé ô bệnh (TSP có ràng buộc nạp thuốc/pin); so sánh với chiến lược tham lam | `src/search/` |
| 2 | Hệ chuyên gia tư vấn và mạng Bayes | ≥ 20 luật lấy từ tài liệu khuyến nông chính thống; **tự cài đặt** suy diễn tiến và suy diễn lùi; mạng Bayes ≥ 5 nút bằng pgmpy | `src/rules/` |
| 3 | Nhận diện bệnh lá lúa | CNN tự thiết kế và transfer learning (MobileNetV2 hoặc EfficientNetB0) bằng TensorFlow/Keras; tăng cường dữ liệu; đánh giá accuracy, precision, recall, F1, ma trận nhầm lẫn | `src/model/` |
| 4 | Ứng dụng tích hợp | Giao diện tiếng Việt, bản đồ lưới, hoạt cảnh lộ trình (Pygame hoặc matplotlib) | `src/app/` |

**Phần mở rộng (không bắt buộc):** kết hợp xác suất CNN với mạng Bayes và thời tiết thực tế của tỉnh; lấy thời tiết từ API công khai để cảnh báo sớm nguy cơ đạo ôn; giao diện chữ to cho nông dân lớn tuổi.

**Liên hệ phần đọc sách giữa kỳ:** TSP (Example 4) → Chức năng 1 · Knowledge Representation (Ch.6) → Chức năng 2 · Machine Learning (Ch.10) → Chức năng 3.

## 3. Cấu trúc thư mục

```text
Nhom05_De02/
├── .gitignore
├── README.md
├── AGENTS.md              # quy tắc cho thành viên và AI
├── requirements.txt       # thư viện chức năng
├── requirements-dev.txt   # pytest, ruff
├── requirements-web.txt   # flask cho demo web CN2
├── pyproject.toml
├── demo.py                # chạy thử tích hợp
├── src/
│   ├── __init__.py
│   ├── contracts.py       # kiểu dữ liệu dùng chung giữa các module
│   ├── drone/             # TV1 – CN1: không gian trạng thái drone
│   │   ├── __init__.py
│   │   ├── state.py       # trạng thái: vị trí, thuốc, pin, ô chưa phun
│   │   ├── operators.py   # hành động bay / phun / nạp
│   │   ├── navigation.py
│   │   ├── problem.py
│   │   └── A_star.py      # A* cho từng chặng
│   ├── search/            # TV1 – CN1: lập lộ trình
│   │   ├── __init__.py
│   │   ├── greedy.py      # tham lam (đã chạy)
│   │   ├── full_astar.py  # A* toàn cục (đã chạy)
│   │   ├── route_utils.py
│   │   ├── experiment.py  # so sánh thuật toán
│   │   ├── run.py         # plan_route (chưa cài)
│   │   ├── order_opt.py   # leo đồi / beam (chưa cài)
│   │   ├── astar.py       # (chưa cài)
│   │   └── grid.py        # (chưa cài)
│   ├── rules/             # TV2/TV3 – CN2
│   │   ├── __init__.py
│   │   ├── rules.json     # luật IF–THEN có nguồn
│   │   ├── sources.json
│   │   ├── vocabulary.json
│   │   ├── forward.py     # suy diễn tiến
│   │   ├── backward.py    # suy diễn lùi
│   │   ├── trace.py       # vết luật đã dùng
│   │   ├── bayes.py       # mạng Bayes
│   │   ├── ket_hop.py     # kết hợp CNN + Bayes
│   │   └── diagnose.py
│   ├── model/             # TV4 – CN3
│   │   ├── __init__.py
│   │   ├── prepare_data.py
│   │   ├── data_pipeline.py
│   │   ├── custom_cnn.py
│   │   ├── transfer.py
│   │   ├── training.py
│   │   └── predict.py     # predictor ảnh thật; cần artifact .keras
│   ├── web/               # CN2 – demo web hệ luật (Flask)
│   │   ├── __init__.py
│   │   ├── templates/index.html
│   │   └── static/        # app.js, style.css
│   └── app/               # TV5 – CN4; thời tiết TV3
│       ├── __init__.py
│       ├── main.py        # E1 – cửa sổ, menu
│       ├── giao_dien.py   # màu, phông, nút dùng chung
│       ├── grid_editor.py # E2 – bản đồ lưới
│       ├── route_view.py  # E3 – hoạt cảnh lộ trình
│       ├── chan_doan_view.py # E4 – màn hình chẩn đoán ảnh
│       ├── chan_doan.py   # điều phối chẩn đoán ảnh
│       └── thoi_tiet.py   # thời tiết Open-Meteo
├── data/
│   ├── sample/
│   │   ├── README.md
│   │   └── maps/map_4x4.json
│   ├── raw/               # bộ ảnh tải về, không lên Git
│   └── anh_thuc_te/       # giữ nguon.csv; ảnh không lên Git
├── models/                # README.md; *.keras không lên Git
├── docs/
│   ├── mo_hinh_bai_toan.md
│   ├── interfaces.md      # hợp đồng hàm giữa các phần
│   ├── nguon_tri_thuc.md
│   ├── doi_chieu_luat.md
│   ├── du_lieu.md
│   ├── kiem_chung.md
│   ├── decisions/         # ghi chép quyết định thiết kế
│   ├── cau_hoi/           # trả lời Q1 – Q4
│   └── ho_so_nhom/ai_log.md
├── artifacts/             # kết quả kiểm thử CN2 đã lưu
├── tasks/                 # plan.md, todo.md
├── scripts/
│   ├── __init__.py
│   ├── check_rules.py     # kiểm tra bộ luật
│   └── train_cn3.py       # huấn luyện CNN (CN3)
└── tests/                 # pytest; fixtures/ là dữ liệu mẫu cho test
    ├── test_demo.py
    ├── test_search.py
    ├── test_forward.py, test_backward.py, test_rules.py, test_reasoning_details.py,
    │   test_knowledge_regressions.py, test_diagnose*.py
    ├── test_tv3_probability.py, test_probability_boundaries.py
    ├── test_predict.py, test_model_data.py
    ├── test_web.py
    └── test_grid_editor.py, test_route_view.py, test_chan_doan_view.py
```

## 4. Cài đặt

Dùng **Python 3.10 hoặc 3.11** cho môi trường chức năng. Sau khi clone, chuyển
vào gốc repo chứa README (`Nhom05_De02`). Nếu clone đặt tên khác thì dùng tên đó.

```text
python --version
python -m venv .venv
```

Kích hoạt theo shell; các lệnh sau đó dùng chung:

- Windows PowerShell: `.venv\Scripts\Activate.ps1`
- Windows cmd: `.venv\Scripts\activate.bat`
- macOS/Linux bash hoặc zsh: `source .venv/bin/activate`

```text
python -m pip install -r requirements-dev.txt
python -m pip install -r requirements.txt
```

Có thể chỉ cài requirements-dev để chạy test/demo khung. Bộ chức năng bắt đầu
bằng `tensorflow==2.16.1`, `numpy==1.26.4` (<2), `pgmpy==0.1.25`; xem toàn bộ
trong `requirements.txt`. Đây là ghim phụ thuộc trực tiếp, chưa phải lockfile
bắc cầu. **Chưa cài thử** toàn bộ trên Python 3.10/3.11.
Nguồn: [TensorFlow 2.16.1](https://pypi.org/project/tensorflow/2.16.1/),
[pgmpy 0.1.25](https://pypi.org/project/pgmpy/0.1.25/).

- `scikit-learn` chỉ tính chỉ số đánh giá; A*, leo đồi/beam, suy diễn tiến/lùi tự cài.
- `requests` dành cho thời tiết; bản khung không gọi API.
- Notebook huấn luyện có thể chạy Colab/Kaggle GPU, đặt ở `src/model/notebooks/`.
- Demo không cần TensorFlow, mô hình hoặc ảnh tải ngoài.

## 5. Dữ liệu và nguồn tri thức

- **Ảnh lá lúa:** bộ dữ liệu công khai (Kaggle, Mendeley Data), tối thiểu 4 lớp: đạo ôn, bạc lá, đốm nâu, lá khỏe. Đường dẫn tải và giấy phép ghi trong `docs/du_lieu.md`. Tải về và giải nén vào `data/raw/`.
- **Ảnh thực tế:** ≥ 20 ảnh tự chụp hoặc sưu tầm trong `data/anh_thuc_te/`; nguồn từng ảnh ghi trong `data/anh_thuc_te/nguon.csv`.
- **Tri thức cho hệ chuyên gia:** 28 luật, danh mục S1–S7. S2 là datasheet EPPO cập nhật 2022; S7 là bài khoa học năm 2006 cho héo/cuộn lá. Xem [hồ sơ nguồn](docs/nguon_tri_thuc.md) và [đối chiếu 28 luật](docs/doi_chieu_luat.md). S3 tải trực tiếp lỗi, S6 mở lại timeout; DN10 còn giới hạn nguồn về mốc vụ và điều kiện kích hoạt. Chưa có duyệt chuyên gia địa phương. Không có thuốc/hoạt chất/liều lượng trong luật.

## 6. Cách chạy khung hiện tại

### Demo web hệ luật CN2

Từ thư mục chứa README, chạy PowerShell:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-web.txt
.\.venv\Scripts\python.exe -m flask --app src.web run
```

Mở http://127.0.0.1:5000. Ở **Suy diễn tiến**, bấm **Mẫu vết hình thoi**
để xem DO01 → DO12 hoặc **Mẫu thừa đạm** để xem DO11. Ở **Suy diễn lùi**,
chọn mục tiêu, bấm **Bắt đầu hỏi** và trả lời từng câu. Bấm mã luật trong
vết suy luận để mở mục nguồn tương ứng. Demo này minh họa hệ luật CN2 bằng
dữ kiện do người dùng cung cấp.

API của trang nhận JSON. `POST /api/forward` nhận đối tượng `answers` ánh xạ
mã thuộc tính sang `co`, `khong` hoặc `chua_biet`. Đầu ra gồm `input_facts`,
`derived_facts` và `trace`. `POST /api/backward/step` nhận thêm `goal`
và trả `status`, `next_question` (mã thuộc tính hoặc null) và `trace`.
Gửi `answers: {}` ở bước đầu. Trình duyệt giữ câu trả lời trong lượt hỏi
hiện tại và gửi lại trong mỗi bước.

Chạy từ gốc repo trên Windows/macOS/Linux:

```text
python -m src.app.main
python demo.py
python -m src.search.experiment
python -m pytest
ruff check .
python -m scripts.check_rules
```

`python -m src.app.main` mở ứng dụng (cần `pygame`). Vào **Bản đồ ruộng và lộ trình drone**: tô ô bệnh,
vật cản, trạm bằng chuột (trái tô, phải xóa), mở/lưu file JSON, tạo bản đồ ngẫu nhiên, chỉnh k/p,
rồi bấm **Lập lộ trình** để xem drone bay từng bước (Space chạy/dừng, ← → từng bước, R về đầu).
Thuật toán: tham lam của CN1; A* toàn cục chỉ bật khi bản đồ ≤ 8 ô bệnh vì chạy chậm.

Vào **Chẩn đoán bệnh từ ảnh lá lúa**: chọn ảnh, bấm **Chẩn đoán**, trả lời từng câu hỏi triệu chứng
(Có / Không / Chưa biết, hoặc phím C / K / B). Màn hình hiện top-3 của CNN, kết luận, giải thích,
luật đã dùng và nguồn. Chưa có `models/rice_leaf_classifier.keras` thì màn hình báo chưa có mô hình
và không kết luận.

`python -m src.search.experiment` chạy thử trên bản đồ mẫu
`data/sample/maps/map_4x4.json`, in ma trận và chi tiết lộ trình A* toàn cục,
đồng thời so sánh với tham lam gần nhất.

Nếu ruff chưa có trong PATH dùng `python -m ruff check .`. Demo đọc bản đồ 4 × 4,
thông báo CNN chưa sẵn sàng nếu chưa có artifact, báo “chưa cài đặt” cho CN1.
Không có số dự đoán mặc định hoặc kết luận bệnh giả.

Các module chưa cung cấp CLI xử lý tham số. Một số thuật toán CN1/CN2 và mô hình
đã có hàm thư viện; các hàm chưa triển khai ném `NotImplementedError`. Không coi
các phần chưa triển khai là chức năng hoàn thành.

Các test của thuật toán chưa triển khai còn đánh dấu xfail; test CN2 không còn
xfail. `python -m scripts.check_rules` kiểm tra schema, tối thiểu 20 luật,
mã nguồn, từ vựng, chu trình, chuỗi suy diễn chẩn đoán–khuyến nghị và nội dung
cấm. Tiêu chí bắt buộc không đạt sẽ trả mã lỗi.

## 7. Quy ước dữ liệu giữa các module

Chi tiết trong `docs/interfaces.md`.

**Mã lớp bệnh** (dùng chung cho CNN, hệ luật, mạng Bayes): `dao_on` (đạo ôn), `bac_la` (bạc lá), `dom_nau` (đốm nâu), `la_khoe` (lá khỏe).

**Bản đồ lưới** (file JSON, kích thước thật tối thiểu 20 × 20; ví dụ dưới rút gọn 4 × 4 để minh họa):

```json
{
  "rows": 4,
  "cols": 4,
  "start": [0, 0],
  "k": 3,
  "p": 20,
  "cells": [
    [9,  0,  0, 2],
    [0, -1,  1, 0],
    [0, -1,  0, 3],
    [1,  0,  0, 0]
  ]
}
```

**k** là số ô phun tối đa mỗi lần nạp; **p** là số bước bay mỗi lần nạp pin. Mức bệnh 1–3 không nhân số lần phun; mỗi ô cần phun một lần. Điểm cần xác nhận với thầy ghi ở `docs/mo_hinh_bai_toan.md`.

Mã ô: `0` lúa khỏe · `1`, `2`, `3` lúa bệnh theo mức · `-1` vật cản (kênh mương có cây cao, trụ điện) · `9` trạm nạp thuốc/đổi pin.

**Hàm giao tiếp chính** (type hint và schema ở `docs/interfaces.md`):

| Hàm | Module | Đầu ra |
|-----|--------|--------|
| `predict_top3(duong_dan_anh)` | `src/model/predict.py` | 3 nhãn/xác suất từ ảnh và mô hình thật; cần artifact `.keras` |
| `diagnose(top3, hoi_nguoi_dung)` | `src/rules/diagnose.py` | kết luận, độ tin cậy, các luật đã dùng (giải thích), nguồn tài liệu |
| `plan_route(ban_do, k, p, thuat_toan)` | `src/search/run.py` | các ô đi qua, sự kiện phun/nạp, tổng quãng đường, số lần về trạm, thời gian chạy |

## 8. Thành viên và phân công

| Mã | Họ và tên | MSSV | Phụ trách |
|----|-----------|------|-----------|
| TV1 | … | … | **Nhóm trưởng** · CN1 – lập lộ trình drone; hồ sơ nhóm, nộp bài; Q1 |
| TV2 | … | … | CN2 – hệ chuyên gia (luật, suy diễn tiến/lùi); ghép báo cáo; Q4 |
| TV3 | … | … | CN2 – mạng Bayes, kết hợp CNN với Bayes; ảnh thực tế; mở rộng thời tiết; Q2 |
| TV4 | … | … | CN3 – mô hình CNN; Q3 |
| TV5 | … | … | CN4 – ứng dụng tích hợp; quản lý Git/README; slide, đóng gói code |

Phân công chi tiết: `docs/ho_so_nhom/` (Mẫu 01 – Kế hoạch và phân công công việc).

## 9. Kế hoạch và tiến độ

| Tuần | Thời gian | Nội dung chính | Mốc |
|------|-----------|----------------|-----|
| 1 | 02/11 – 08/11 | Mô hình hóa 3 bài toán, quy ước module, README, Mẫu 01 | **Kiểm soát lần 1 – 23h59 CN 08/11** |
| 2 | 09/11 – 15/11 | A*, tham lam; ≥ 20 luật, suy diễn tiến; dữ liệu, CNN tự thiết kế; khung ứng dụng | |
| 3 | 16/11 – 22/11 | Leo đồi/beam và so sánh; suy diễn lùi; mạng Bayes; transfer learning; hoạt cảnh | **Kiểm soát lần 2 – 23h59 CN 22/11** |
| 4 | 23/11 – 29/11 | Tích hợp ứng dụng; thử ≥ 20 ảnh thực tế; Q1 – Q4; phần mở rộng | |
| 5 | 30/11 – 06/12 | Báo cáo, slide, đóng gói code; Mẫu 03, 04 | **Nộp cuối kỳ – 23h59 CN 06/12** |

- [ ] Mô hình hóa bài toán, README bản đầu, Mẫu 01, Mẫu 02 Tuần 1
- [ ] CN1 chạy được: A*, tham lam, leo đồi/beam, bảng so sánh
- [ ] CN2 chạy được: ≥ 20 luật, suy diễn tiến, suy diễn lùi, mạng Bayes
- [ ] CN3: kết quả đánh giá 2 mô hình, thử ≥ 20 ảnh thực tế
- [ ] CN4: ứng dụng chạy đầu – cuối, có hoạt cảnh lộ trình
- [ ] Nộp báo cáo .docx, slide .pptx, code .zip

## 10. Quy ước làm việc với Git

- `main` chỉ chứa bản chạy được. Mỗi chức năng một nhánh: `cn1-tim-kiem`, `cn2-chuyen-gia`, `cn2-bayes`, `cn3-cnn`, `cn4-ung-dung`.
- Ghép vào `main` qua pull request, có ít nhất 1 thành viên khác duyệt.
- Commit nhỏ và thường xuyên, thông điệp có tiền tố chức năng, ví dụ: `[CN1] Thêm A* với heuristic Manhattan`.
- Không commit dữ liệu ảnh, trọng số mô hình, khóa API (đã khai báo trong `.gitignore`).
- Mặc định trọng số không lên Git; **gói nộp cuối kỳ phải kèm `.keras` hoặc link tải** (xem `models/README.md`).
- Gốc repo hiện là `Nhom05_De02`, cây src đã đúng từ trước; không có thư mục cũ cần di chuyển trong phiên dựng khung.

## 11. Lưu ý khi sử dụng

Kết quả của Bác sĩ Lúa **chỉ mang tính tham khảo**, không thay thế chẩn đoán và khuyến cáo của cán bộ khuyến nông, bảo vệ thực vật. Trước khi sử dụng thuốc, cần làm theo hướng dẫn trên nhãn và khuyến cáo của cơ quan chuyên môn địa phương.

## 12. Khai báo sử dụng AI và bản quyền

- Việc sử dụng AI tạo sinh trong quá trình thực hiện được khai báo trong Mẫu 04 (`docs/ho_so_nhom/`).
- Mã nguồn phục vụ mục đích học tập. Dữ liệu ảnh và tài liệu tham khảo thuộc về tác giả, cơ quan gốc; xem `docs/du_lieu.md` và `docs/nguon_tri_thuc.md`.
