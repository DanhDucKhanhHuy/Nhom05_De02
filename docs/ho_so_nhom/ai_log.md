# Nhật ký sử dụng AI — chuẩn bị Mẫu 04

Mỗi người thêm một dòng sau khi dùng AI; kiểm chứng nội dung trước khi nhận.
Bảng dưới là mẫu trống, không phải lịch sử sử dụng thật. Không ghi khóa API
hoặc thông tin riêng tư. Khi nộp, chuyển thông tin sang đúng Mẫu 04 của thầy.

| Ngày (YYYY-MM-DD) | Người (TV1–TV5) | Công cụ AI | Việc làm, phần tự kiểm chứng | File bị ảnh hưởng |
|---|---|---|---|---|
| … | … | … | … | … |
| 2026-11-17 | TV5 | Claude (Claude Code) | Gợi ý khung Pygame E1 (menu, chuyển màn hình, phông tiếng Việt). Tự chạy thử `python -m src.app.main`, đọc lại từng hàm | `src/app/main.py`, `src/app/giao_dien.py` |
| 2026-11-18 | TV5 | Claude (Claude Code) | Gợi ý E2: đọc/ghi/kiểm tra JSON, vẽ lưới, tô ô, mở/lưu file, bản đồ ngẫu nhiên (BFS), chỉnh k/p; viết test. Tự chạy test, thử tô ô, mở file sai để xem báo lỗi | `src/app/grid_editor.py`, `tests/test_grid_editor.py` |
| 2026-11-19 | TV5 | Claude (Claude Code) | Gợi ý E3: dựng khung hình từ `LoTrinh` của CN1, hoạt cảnh chạy/dừng/từng bước, chọn thuật toán; viết test; cập nhật README phần ứng dụng. Tự chạy test, xem drone bay hết lộ trình và về trạm | `src/app/route_view.py`, `tests/test_route_view.py`, `README.md` |
| 2026-11-19 | TV5 | Claude (Claude Code) | Gợi ý E4: màn hình chẩn đoán ảnh, hỏi triệu chứng ở luồng riêng, hiện top-3, kết luận, giải thích, luật, nguồn; nối nút ở menu; viết test. Tự chạy test, xem ảnh chụp màn hình hỏi đáp và kết quả | `src/app/chan_doan_view.py`, `src/app/main.py`, `tests/test_chan_doan_view.py`, `README.md` |
| 2026-11-21 | TV5 | Claude (Claude Code) | Khôi phục phần CN4 bị bản tải lên ghi đè (menu Chẩn đoán, nút Lập lộ trình, README phần ứng dụng). Tự chạy test, mở app bấm thử từng nút | `src/app/main.py`, `src/app/grid_editor.py`, `README.md` |
| 2026-11-21 | TV5 | Claude (Claude Code) | Khôi phục code CN3 bị ghi đè; E4 xử lý khi chưa có mô hình CNN (không gọi `predict_top3`, hiện thông báo), sửa test E4 dùng mô hình giả. Tự chạy toàn bộ test, mở app chẩn đoán khi chưa có file .keras | `src/app/chan_doan_view.py`, `tests/test_chan_doan_view.py`, `README.md` |
