"""
C6 – Kết hợp xác suất CNN và mạng Bayes trên bốn lớp loại trừ nhau.

Công thức: P(C|ảnh, điều kiện) ∝ P_CNN(C) × P(C|điều kiện).
Nếu CNN được huấn luyện với prior lớp không cân bằng, chia P_CNN cho
prior huấn luyện trước khi nhân để giảm ảnh hưởng prior bị lặp.
"""
from __future__ import annotations

import argparse
import math
import sys
from typing import Iterable, Mapping

from .bayes import truy_van

MA_BENH = ("dao_on", "bac_la", "dom_nau", "la_khoe")
TEN_BENH = {
    "dao_on": "Đạo ôn",
    "bac_la": "Bạc lá",
    "dom_nau": "Đốm nâu",
    "la_khoe": "Lá khỏe",
}
NGUONG_KET_LUAN = 0.60
VI_DU_CNN = [("dao_on", 0.55), ("dom_nau", 0.40), ("bac_la", 0.03)]
VI_DU_BANG_CHUNG = [
    "vet_bac_ung_nuoc_tren_phien_la=co",
    "am_u_va_suong_som=co",
    "thua_dam=co",
]


def chuan_hoa_cnn_top3(cnn_top3: Iterable[tuple[str, float]]) -> dict[str, float]:
    """Kiểm tra top-3 nghiêm ngặt và suy ra phần còn lại cho lớp bị lược."""
    items = list(cnn_top3)
    if len(items) != 3:
        raise ValueError("CNN phải cung cấp đúng 3 lớp dự đoán (top-3).")
    result: dict[str, float] = {}
    for item in items:
        if not isinstance(item, (tuple, list)) or len(item) != 2:
            raise ValueError("Mỗi phần tử CNN phải có dạng (ma_benh, xac_suat).")
        label, probability = item
        if not isinstance(label, str) or label not in MA_BENH:
            raise ValueError(f"Mã lớp CNN không hợp lệ: {label!r}.")
        if label in result:
            raise ValueError(f"Mã lớp CNN bị trùng: {label}.")
        if isinstance(probability, bool) or not isinstance(probability, (int, float)):
            raise ValueError("Xác suất CNN phải là số thực hữu hạn.")
        if not 0.0 <= probability <= 1.0:
            raise ValueError("Xác suất CNN phải thuộc [0, 1].")
        probability = float(probability)
        if not math.isfinite(probability) or not 0.0 <= probability <= 1.0:
            raise ValueError(f"Xác suất CNN phải hữu hạn và thuộc [0, 1]: {probability}.")
        result[label] = probability

    probabilities = list(result.values())
    if probabilities != sorted(probabilities, reverse=True):
        raise ValueError("Top-3 phải sắp theo xác suất giảm dần.")

    missing = set(MA_BENH) - set(result)
    if len(missing) != 1:
        raise ValueError("Top-3 phải gồm đúng 3 lớp khác nhau trong 4 lớp đã quy ước.")
    total = sum(result.values())
    if total <= 0.0 or total > 1.0 + 1e-9:
        raise ValueError("Tổng xác suất top-3 phải thuộc (0, 1].")
    omitted = next(iter(missing))
    result[omitted] = max(0.0, 1.0 - total)
    normalizer = sum(result.values())
    if normalizer <= 0:
        raise ValueError("Không thể chuẩn hóa phân phối CNN.")
    return {label: value / normalizer for label, value in result.items()}


def chuan_hoa_bayes(
    bang_chung: Mapping[str, object] | Iterable[str] | None = None,
    su_dung_pgmpy: bool = True,
) -> tuple[dict[str, float], dict]:
    """Lấy phân phối bốn lớp đã chuẩn hóa từ mạng Bayes."""
    result = truy_van(bang_chung, su_dung_pgmpy=su_dung_pgmpy)
    raw = {label: float(result["xac_suat"].get(label, 0.0)) for label in MA_BENH}
    if any(not math.isfinite(value) or value < 0.0 for value in raw.values()):
        raise ValueError("Xác suất Bayes phải hữu hạn và không âm.")
    total = sum(raw.values())
    if total <= 0.0:
        raise ValueError("Mạng Bayes trả về tổng xác suất bằng 0.")
    return ({label: value / total for label, value in raw.items()}, result)


def _chuan_hoa_prior(prior: Mapping[str, float] | None) -> dict[str, float]:
    """Prior huấn luyện; mặc định cân bằng bốn lớp."""
    if prior is None:
        return {label: 0.25 for label in MA_BENH}
    if set(prior) != set(MA_BENH):
        raise ValueError("prior_cnn phải khai báo đủ và đúng bốn mã lớp.")
    values = {}
    for label, raw in prior.items():
        if isinstance(raw, bool) or not isinstance(raw, (int, float)):
            raise ValueError("Prior lớp phải là số thực hữu hạn dương.")
        value = float(raw)
        if not math.isfinite(value) or value <= 0.0:
            raise ValueError("Prior lớp phải hữu hạn và lớn hơn 0.")
        values[label] = value
    total = sum(values.values())
    if not math.isfinite(total) or total <= 0.0:
        raise ValueError("Tổng prior CNN phải hữu hạn và lớn hơn 0.")
    return {label: value / total for label, value in values.items()}


def ket_hop_cnn_bayes(
    cnn_top3: Iterable[tuple[str, float]],
    bang_chung: Mapping[str, object] | Iterable[str] | None = None,
    prior_cnn: Mapping[str, float] | None = None,
    nguong: float = NGUONG_KET_LUAN,
    su_dung_pgmpy: bool = True,
) -> dict:
    """
    Nhân likelihood CNN đã hiệu chỉnh prior với hậu nghiệm Bayes theo điều kiện.

    Giả định: ảnh và điều kiện ruộng độc lập có điều kiện khi biết lớp bệnh.
    Nếu không có prior_cnn, giả định tập huấn luyện cân bằng bốn lớp.
    """
    if isinstance(nguong, bool) or not isinstance(nguong, (int, float)):
        raise ValueError("Ngưỡng kết luận phải là số thuộc [0, 1].")
    nguong = float(nguong)
    if not math.isfinite(nguong) or not 0.0 <= nguong <= 1.0:
        raise ValueError("Ngưỡng kết luận phải hữu hạn và thuộc [0, 1].")

    cnn = chuan_hoa_cnn_top3(cnn_top3)
    bayes, bayes_detail = chuan_hoa_bayes(bang_chung, su_dung_pgmpy)
    training_prior = _chuan_hoa_prior(prior_cnn)

    unnormalized = {
        label: (cnn[label] / training_prior[label]) * bayes[label]
        for label in MA_BENH
    }
    normalizer = sum(unnormalized.values())
    if not math.isfinite(normalizer) or normalizer <= 0.0:
        raise ValueError("Tổng tích CNN–Bayes bằng 0 hoặc không hữu hạn.")
    combined = {label: value / normalizer for label, value in unnormalized.items()}
    ranking = sorted(combined.items(), key=lambda item: (-item[1], item[0]))
    tied = len(ranking) > 1 and math.isclose(
        ranking[0][1], ranking[1][1], rel_tol=0.0, abs_tol=1e-12
    )
    multi_mass = float(bayes_detail["xac_suat_dong_mac"])
    # CNN chỉ có bốn lớp đơn bệnh/lá khỏe; giảm độ chắc nếu Bayes dự báo đồng mắc.
    confidence = ranking[0][1] * max(0.0, 1.0 - multi_mass)
    confident = confidence >= nguong and not tied
    conclusion = ranking[0][0] if confident else None
    status = "da_ket_luan" if confident else "chua_du_chac"

    return {
        "xac_suat_cnn": cnn,
        "xac_suat_bayes": bayes,
        "prior_cnn": training_prior,
        "xac_suat_ket_hop": combined,
        "top3_ket_qua": ranking[:3],
        "ket_luan": conclusion,
        "trang_thai": status,
        "nguong_ket_luan": nguong,
        "do_tin_cay_dieu_chinh": confidence,
        "hoa": tied,
        "phuong_phap_bayes": bayes_detail["phuong_phap"],
        "bang_chung_bayes": bayes_detail["bang_chung"],
        "ghi_chu": bayes_detail["ghi_chu"],
        "xac_suat_dong_mac": multi_mass,
        "phuong_phap": (
            "P(lớp|ảnh, điều kiện) ∝ "
            "P_CNN(ảnh|lớp) × P(lớp|điều kiện), chuẩn hóa"
        ),
        "gia_dinh": (
            "Giả định ảnh và điều kiện ruộng độc lập có điều kiện khi biết lớp. "
            "P_CNN được xem là posterior; chia prior huấn luyện để xấp xỉ likelihood. "
            "Nếu không truyền prior_cnn, giả định tập CNN cân bằng bốn lớp. "
            "Độ chắc quyết định còn được giảm theo khối lượng đồng mắc vì CNN chỉ có "
            "bốn lớp đơn bệnh/lá khỏe."
        ),
        "canh_bao": (
            "CPD Bayes là ước lượng định tính, chưa hiệu chuẩn từ dữ liệu đồng ruộng; "
            "kết quả chỉ hỗ trợ tham khảo, không thay thế chẩn đoán chuyên môn."
        ),
    }


def _parse_top3(value: str) -> list[tuple[str, float]]:
    parsed = []
    for part in value.split(","):
        label, probability = part.strip().split(":", 1)
        parsed.append((label.strip(), float(probability)))
    return parsed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Kết hợp CNN + mạng Bayes.")
    parser.add_argument(
        "--top3",
        default=",".join(f"{label}:{prob}" for label, prob in VI_DU_CNN),
        help="Top-3 dạng dao_on:0.55,dom_nau:0.40,bac_la:0.03",
    )
    parser.add_argument(
        "--bang-chung",
        nargs="*",
        default=VI_DU_BANG_CHUNG,
        help="Mã sự kiện cũ hoặc thuộc_tính=co|khong|chua_biet",
    )
    parser.add_argument("--nguong", type=float, default=NGUONG_KET_LUAN)
    parser.add_argument("--khong-pgmpy", action="store_true")
    args = parser.parse_args(argv)

    result = ket_hop_cnn_bayes(
        _parse_top3(args.top3),
        args.bang_chung,
        nguong=args.nguong,
        su_dung_pgmpy=not args.khong_pgmpy,
    )
    print("=== KẾT QUẢ KẾT HỢP CNN + BAYES ===")
    for label, probability in result["top3_ket_qua"]:
        print(f"  {TEN_BENH[label]:<12}: {probability:.2%}")
    print("Điểm quyết định:", f'{result["do_tin_cay_dieu_chinh"]:.2%}')
    print("Trạng thái:", result["trang_thai"])
    print("Kết luận:", TEN_BENH[result["ket_luan"]] if result["ket_luan"] else "Chưa đủ chắc")
    print("Bằng chứng Bayes:", result["bang_chung_bayes"])
    print("Xác suất đồng mắc:", result["xac_suat_dong_mac"])
    for note in result["ghi_chu"]:
        print("Ghi chú:", note)
    print("Giả định:", result["gia_dinh"])
    print("Cảnh báo:", result["canh_bao"])
    return 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    raise SystemExit(main())
