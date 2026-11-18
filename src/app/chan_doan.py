"""Điều phối ảnh qua predictor và phiên chẩn đoán, không tải mô hình tại đây."""
from pathlib import Path

from src.contracts import ChanDoan, HoiNguoiDung
from src.model import predict
from src.rules.diagnose import diagnose


def diagnose_image(duong_dan_anh: str, hoi_nguoi_dung: HoiNguoiDung) -> ChanDoan:
    """Không kết luận bệnh khi artifact chưa có; giữ lỗi ảnh/predictor."""
    if not Path(duong_dan_anh).is_file():
        predict.predict_top3(duong_dan_anh)
    if not predict.MODEL_PATH.is_file():
        return {
            "ket_luan": None,
            "do_tin_cay": None,
            "luat_da_dung": [],
            "nguon": [],
            "giai_thich": "Chưa có mô hình CNN đã huấn luyện; chưa thể phân tích ảnh.",
            "vet": [],
        }
    result = diagnose(predict.predict_top3(duong_dan_anh), hoi_nguoi_dung)
    if predict.IS_STUB:
        result = dict(result)
        result["ket_luan"] = None
        result["do_tin_cay"] = None
        result["giai_thich"] = (
            "Dự đoán CNN GIẢ: chỉ kiểm tra luồng, không dùng xác nhận bệnh.\n"
            + result.get("giai_thich", "")
        )
    return result
