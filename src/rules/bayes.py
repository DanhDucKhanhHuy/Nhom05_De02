"""C5 - Mạng Bayes cho bệnh lá lúa và các dấu hiệu quan sát độc lập."""

from __future__ import annotations

import argparse
import itertools
import json
import math
import sys
from pathlib import Path
from typing import Iterable, Mapping

MA_BENH_BAYES = {"dao_on": "DaoOn", "bac_la": "BacLa", "dom_nau": "DomNau"}
BENH_NODES = ("DaoOn", "BacLa", "DomNau")
VOCABULARY_PATH = Path(__file__).with_name("vocabulary.json")

# Nguồn chỉ hỗ trợ cấu trúc/nhóm triệu chứng. Các số trong CPD là giả định
# định tính do nhóm đặt để kiểm thử mô hình, không phải tần suất thực nghiệm.
NGUON_CPD = {
    "ThoiTiet": (),
    "ThuaDam": (),
    "Giong": (),
    "DinhDuong": (),
    "DaoOn": ("S1", "S4"),
    "BacLa": ("S2",),
    "DomNau": ("S3",),
    "AmU_SuongSom": (),
    "VetHinhThoi": ("S1", "S4"),
    "VetTamXamKho": ("S1", "S4"),
    "BacVetUngNuoc": ("S2",),
    "BacBatDauChop": ("S2",),
    "BacVangTrang": ("S2",),
    "BacMepLuonSong": ("S2",),
    "LaHeoCuon": ("S2",),
    "DomTronBauDuc": ("S3",),
    "DomVienSam": ("S3",),
    "DomTamNhatXam": ("S3",),
    "DomTrenBeLa": ("S3",),
    "DomTrenDiepTieu": ("S3",),
    "DomTrenVoTrau": ("S3",),
    "HatNheBacPhan": ("S3",),
}

# Ghi rõ giả định quan hệ và giới hạn từng CPD. Số xác suất không được suy ra
# trực tiếp từ các tài liệu S1-S4.
GIA_DINH_CPD = {
    "ThoiTiet": "Prior minh họa cho nhóm thời tiết ẩm/mưa so với khô; không phải tần suất khí hậu.",
    "ThuaDam": "Prior minh họa cho việc bón đạm vượt khuyến cáo; không phải tỷ lệ ruộng thực tế.",
    "Giong": "Prior minh họa giống nhiễm/kháng; chưa học từ cơ cấu giống.",
    "DinhDuong": "Prior minh họa đất đủ/thiếu dinh dưỡng; chưa học từ xét nghiệm đất.",
    "DaoOn": "Giả định đạo ôn thuận lợi hơn khi thời tiết ẩm, đạm vượt khuyến cáo và giống nhiễm; S1/S4 chỉ hỗ trợ định tính.",
    "BacLa": "Giả định bạc lá thuận lợi hơn khi thời tiết ẩm và đạm vượt khuyến cáo; S2 hỗ trợ định tính.",
    "DomNau": "Giả định đốm nâu thuận lợi hơn khi dinh dưỡng thiếu và thời tiết khô; S3 hỗ trợ định tính.",
    "AmU_SuongSom": "Quan sát âm u kèm sương được điều kiện hóa theo nhóm thời tiết; không đại diện tình trạng ruộng/cây.",
    "VetHinhThoi": "Dấu hiệu hình thoi phụ thuộc trạng thái đạo ôn; S1/S4 hỗ trợ nhận dạng định tính.",
    "VetTamXamKho": "Tâm xám khô được mô hình hóa là dấu hiệu con của tổn thương hình thoi; không đồng nhất với hình thoi.",
    "BacVetUngNuoc": "Vệt úng nước phụ thuộc bạc lá; S2 hỗ trợ mô tả triệu chứng.",
    "BacBatDauChop": "Vị trí bắt đầu gần chóp lá chỉ được xét khi có vệt bạc lá; đây là quan hệ phụ thuộc hình thái.",
    "BacVangTrang": "Màu vàng đến trắng chỉ được xét khi có vệt bạc lá; không tự suy ra từ thời tiết.",
    "BacMepLuonSong": "Mép lượn sóng chỉ được xét khi có vệt bạc lá; S2 hỗ trợ mô tả.",
    "LaHeoCuon": "Héo/cuộn lá phụ thuộc bạc lá trong mô hình đơn giản; dấu hiệu không đặc hiệu.",
    "DomTronBauDuc": "Đốm tròn/bầu dục phụ thuộc đốm nâu; S3 hỗ trợ mô tả.",
    "DomVienSam": "Viền sẫm là dấu hiệu con khi đã có đốm; không được coi là cùng nghĩa với tâm xám.",
    "DomTamNhatXam": "Tâm nhạt/xám là dấu hiệu con khi đã có đốm; không được gộp với viền sẫm.",
    "DomTrenBeLa": "Đốm trên bẹ lá phụ thuộc đốm nâu; S3 hỗ trợ vị trí quan sát.",
    "DomTrenDiepTieu": "Đốm trên diệp tiêu phụ thuộc đốm nâu; S3 hỗ trợ vị trí quan sát.",
    "DomTrenVoTrau": "Đốm trên vỏ trấu phụ thuộc đốm nâu; S3 hỗ trợ vị trí quan sát.",
    "HatNheBacPhan": "Hạt nhẹ/bạc phấn phụ thuộc đốm nâu; dấu hiệu không tự xác nhận bệnh.",
}


def _cpd_nhi_phan(parent_co: float, parent_khong: float) -> dict:
    """CPD nhị phân: P(node=co | parent=co/khong)."""
    return {
        ("co",): [parent_co, 1.0 - parent_co],
        ("khong",): [parent_khong, 1.0 - parent_khong],
    }


def _nut_nhi_phan(label: str, parent: str, p_parent_co: float, p_parent_khong: float,
                  source: tuple[str, ...]) -> dict:
    return {
        "nhan": label,
        "gia_tri": ["co", "khong"],
        "cha": [parent],
        "cpd": _cpd_nhi_phan(p_parent_co, p_parent_khong),
        "nguon": source,
    }


# NUT được sắp theo thứ tự topo: cha luôn đứng trước con.
NUT: dict[str, dict] = {
    "ThoiTiet": {
        "nhan": "Nhóm thời tiết đo/quan sát",
        "gia_tri": ["mua_am", "kho"],
        "cha": [],
        "cpd": {(): [0.60, 0.40]},
    },
    "ThuaDam": {
        "nhan": "Bón đạm vượt khuyến cáo",
        "gia_tri": ["co", "khong"],
        "cha": [],
        "cpd": {(): [0.35, 0.65]},
    },
    "Giong": {
        "nhan": "Giống lúa",
        "gia_tri": ["nhiem", "khang"],
        "cha": [],
        "cpd": {(): [0.50, 0.50]},
    },
    "DinhDuong": {
        "nhan": "Dinh dưỡng đất",
        "gia_tri": ["du", "thieu"],
        "cha": [],
        "cpd": {(): [0.55, 0.45]},
    },
    "DaoOn": {
        "nhan": "Bệnh đạo ôn",
        "gia_tri": ["co", "khong"],
        "cha": ["ThoiTiet", "ThuaDam", "Giong"],
        "cpd": {
            ("mua_am", "co", "nhiem"): [0.78, 0.22],
            ("mua_am", "co", "khang"): [0.48, 0.52],
            ("mua_am", "khong", "nhiem"): [0.54, 0.46],
            ("mua_am", "khong", "khang"): [0.24, 0.76],
            ("kho", "co", "nhiem"): [0.38, 0.62],
            ("kho", "co", "khang"): [0.18, 0.82],
            ("kho", "khong", "nhiem"): [0.16, 0.84],
            ("kho", "khong", "khang"): [0.06, 0.94],
        },
    },
    "BacLa": {
        "nhan": "Bệnh bạc lá",
        "gia_tri": ["co", "khong"],
        "cha": ["ThoiTiet", "ThuaDam"],
        "cpd": {
            ("mua_am", "co"): [0.75, 0.25],
            ("mua_am", "khong"): [0.52, 0.48],
            ("kho", "co"): [0.35, 0.65],
            ("kho", "khong"): [0.15, 0.85],
        },
    },
    "DomNau": {
        "nhan": "Bệnh đốm nâu",
        "gia_tri": ["co", "khong"],
        "cha": ["DinhDuong", "ThoiTiet"],
        "cpd": {
            ("thieu", "mua_am"): [0.68, 0.32],
            ("thieu", "kho"): [0.58, 0.42],
            ("du", "mua_am"): [0.32, 0.68],
            ("du", "kho"): [0.20, 0.80],
        },
    },
    "AmU_SuongSom": {
        "nhan": "Quan sát âm u và sương sớm",
        "gia_tri": ["co", "khong"],
        "cha": ["ThoiTiet"],
        "cpd": {
            ("mua_am",): [0.78, 0.22],
            ("kho",): [0.12, 0.88],
        },
    },
    "VetHinhThoi": _nut_nhi_phan("Vết lá hình thoi", "DaoOn", 0.84, 0.06, ("S1", "S4")),
    "VetTamXamKho": _nut_nhi_phan("Tâm vết xám và khô", "VetHinhThoi", 0.72, 0.10, ("S1", "S4")),
    "BacVetUngNuoc": _nut_nhi_phan("Vệt bạc lá úng nước", "BacLa", 0.84, 0.06, ("S2",)),
    "BacBatDauChop": _nut_nhi_phan("Vệt bạc bắt đầu gần chóp lá", "BacVetUngNuoc", 0.78, 0.10, ("S2",)),
    "BacVangTrang": _nut_nhi_phan("Vệt bạc màu vàng đến trắng", "BacVetUngNuoc", 0.76, 0.12, ("S2",)),
    "BacMepLuonSong": _nut_nhi_phan("Mép vệt bạc lượn sóng", "BacVetUngNuoc", 0.74, 0.08, ("S2",)),
    "LaHeoCuon": _nut_nhi_phan("Lá héo hoặc cuộn", "BacLa", 0.62, 0.20, ("S2",)),
    "DomTronBauDuc": _nut_nhi_phan("Đốm nâu tròn hoặc bầu dục", "DomNau", 0.86, 0.07, ("S3",)),
    "DomVienSam": _nut_nhi_phan("Viền đốm nâu sẫm", "DomTronBauDuc", 0.72, 0.14, ("S3",)),
    "DomTamNhatXam": _nut_nhi_phan("Tâm đốm nâu nhạt hoặc xám", "DomTronBauDuc", 0.66, 0.16, ("S3",)),
    "DomTrenBeLa": _nut_nhi_phan("Đốm nâu trên bẹ lá", "DomNau", 0.42, 0.05, ("S3",)),
    "DomTrenDiepTieu": _nut_nhi_phan("Đốm nâu trên diệp tiêu", "DomNau", 0.38, 0.04, ("S3",)),
    "DomTrenVoTrau": _nut_nhi_phan("Đốm nâu trên vỏ trấu", "DomNau", 0.30, 0.03, ("S3",)),
    "HatNheBacPhan": _nut_nhi_phan("Hạt nhẹ hoặc bạc phấn", "DomNau", 0.58, 0.10, ("S3",)),
}
for _name, _sources in NGUON_CPD.items():
    NUT[_name]["nguon"] = _sources
    NUT[_name]["gia_dinh"] = GIA_DINH_CPD[_name]

# Mỗi thuộc tính được hỗ trợ ánh xạ vào một nút quan sát riêng, không dùng nút
# TrieuChung đa trạng thái. None nghĩa là chưa hỗ trợ trong mạng.
ANH_XA_THUOC_TINH: dict[str, dict[str, tuple[str, str] | None]] = {
    "vet_la_hinh_thoi": {"co": ("VetHinhThoi", "co"), "khong": ("VetHinhThoi", "khong"), "chua_biet": None},
    "vet_la_tam_xam_kho": {"co": ("VetTamXamKho", "co"), "khong": ("VetTamXamKho", "khong"), "chua_biet": None},
    "vet_la_vien_nau": {"co": None, "khong": None, "chua_biet": None},
    "vet_co_la_nau_do": {"co": None, "khong": None, "chua_biet": None},
    "dot_than_teo_nau": {"co": None, "khong": None, "chua_biet": None},
    "co_bong_thoi_nau": {"co": None, "khong": None, "chua_biet": None},
    "bong_hoac_gie_lep_trang": {"co": None, "khong": None, "chua_biet": None},
    "am_u_va_suong_som": {"co": ("AmU_SuongSom", "co"), "khong": ("AmU_SuongSom", "khong"), "chua_biet": None},
    "ruong_thieu_nuoc": {"co": None, "khong": None, "chua_biet": None},
    "sa_day": {"co": None, "khong": None, "chua_biet": None},
    "thua_dam": {"co": ("ThuaDam", "co"), "khong": ("ThuaDam", "khong"), "chua_biet": None},
    "vet_bac_ung_nuoc_tren_phien_la": {"co": ("BacVetUngNuoc", "co"), "khong": ("BacVetUngNuoc", "khong"), "chua_biet": None},
    "vet_bac_bat_dau_o_chop_la": {"co": ("BacBatDauChop", "co"), "khong": ("BacBatDauChop", "khong"), "chua_biet": None},
    "vet_la_vang_den_trang": {"co": ("BacVangTrang", "co"), "khong": ("BacVangTrang", "khong"), "chua_biet": None},
    "vet_bac_mep_luon_song": {"co": ("BacMepLuonSong", "co"), "khong": ("BacMepLuonSong", "khong"), "chua_biet": None},
    "la_heo_hoac_cuon_lai": {"co": ("LaHeoCuon", "co"), "khong": ("LaHeoCuon", "khong"), "chua_biet": None},
    "dom_tron_hoac_bau_duc_nau": {"co": ("DomTronBauDuc", "co"), "khong": ("DomTronBauDuc", "khong"), "chua_biet": None},
    "dom_nau_vien_sam": {"co": ("DomVienSam", "co"), "khong": ("DomVienSam", "khong"), "chua_biet": None},
    "dom_nau_tam_nhat_xam": {"co": ("DomTamNhatXam", "co"), "khong": ("DomTamNhatXam", "khong"), "chua_biet": None},
    "dom_nau_tren_be_la": {"co": ("DomTrenBeLa", "co"), "khong": ("DomTrenBeLa", "khong"), "chua_biet": None},
    "cay_gan_truong_thanh_la_gia_hoa": {"co": None, "khong": None, "chua_biet": None},
    "dom_nau_tren_diep_tieu": {"co": ("DomTrenDiepTieu", "co"), "khong": ("DomTrenDiepTieu", "khong"), "chua_biet": None},
    "dom_nau_tren_vo_trau": {"co": ("DomTrenVoTrau", "co"), "khong": ("DomTrenVoTrau", "khong"), "chua_biet": None},
    "hat_nhe_hoac_bac_phan": {"co": ("HatNheBacPhan", "co"), "khong": ("HatNheBacPhan", "khong"), "chua_biet": None},
    "ruong_xac_nhan_nhiem_dom_nau": {"co": None, "khong": None, "chua_biet": None},
}

# Mã sự kiện cũ chỉ được giữ khi có quy tắc chuyển đổi được công bố.
ANH_XA_BANG_CHUNG: dict[str, tuple[str, str]] = {
    "tt_am_do_cao": ("ThoiTiet", "mua_am"),
    "tt_mua_nhieu": ("ThoiTiet", "mua_am"),
    "tt_kho_han": ("ThoiTiet", "kho"),
    "tq_giong_nhiem": ("Giong", "nhiem"),
    "tq_dat_ngheo": ("DinhDuong", "thieu"),
}
# Mã cũ duy nhất có mô tả tương đương đủ rõ với thuộc tính mới.
ANH_XA_MA_CU = {
    ("TrieuChung", "dom_tron"): ("DomTronBauDuc", "co"),
}
TRANG_THAI_BANG_CHUNG = {"co", "khong", "chua_biet"}


def _thuoc_tinh_trong_vocabulary(key: str) -> bool:
    try:
        document = json.loads(VOCABULARY_PATH.read_text(encoding="utf-8"))
        return document.get("thuoc_tinh", {}).get(key, {}).get("loai") == "du_kien_nguoi_dung"
    except (OSError, ValueError):
        return False


def _chuan_hoa_trang_thai(raw_value: object, key: str) -> str:
    if isinstance(raw_value, bool):
        return "co" if raw_value else "khong"
    if raw_value is None:
        return "chua_biet"
    value = str(raw_value).strip().lower()
    aliases = {"true": "co", "false": "khong", "yes": "co", "no": "khong"}
    value = aliases.get(value, value)
    if value not in TRANG_THAI_BANG_CHUNG:
        raise ValueError(f"Trạng thái của thuộc tính {key} không hợp lệ: {raw_value!r}.")
    return value


def bang_chung_bayes(
    bang_chung: Mapping[str, object] | Iterable[str] | None,
) -> tuple[dict[str, str], list[str]]:
    """Chuẩn hóa nhiều bằng chứng độc lập; chua_biet/thiếu không tạo evidence.

    Mapping nhận thuộc_tính -> co|khong|chua_biet hoặc bool. Iterable nhận
    thuộc_tính=trạng_thái, mã sự kiện cũ đã công bố, hoặc tên thuộc tính đơn
    (được hiểu là quan sát co). Các mã cũ không có tương đương bị bỏ qua.
    """
    if bang_chung is None:
        return {}, []
    if isinstance(bang_chung, Mapping):
        entries = [(str(key), value) for key, value in bang_chung.items()]
    else:
        entries = []
        for item in bang_chung:
            if not isinstance(item, str):
                raise ValueError("Bằng chứng dạng danh sách phải là chuỗi.")
            if "=" in item:
                key, value = item.split("=", 1)
                entries.append((key.strip(), value.strip()))
            elif item in ANH_XA_BANG_CHUNG:
                entries.append((item, True))
            elif item in ANH_XA_THUOC_TINH:
                entries.append((item, "co"))
            else:
                entries.append((item, True))

    candidates: dict[str, set[str]] = {}
    notes: set[str] = set()
    for key, raw_value in entries:
        # Cú pháp node=state cũ: chỉ giữ khi node/state có quy tắc tương đương.
        if key == "TrieuChung":
            old_value = str(raw_value).strip()
            mapped = ANH_XA_MA_CU.get((key, old_value))
            if mapped is None:
                notes.add(f"Bỏ qua mã cũ {key}={old_value}: không có định nghĩa tương đương trong mạng mới.")
                continue
            node, state = mapped
        elif key in ANH_XA_THUOC_TINH or _thuoc_tinh_trong_vocabulary(key):
            value = _chuan_hoa_trang_thai(raw_value, key)
            if value == "chua_biet":
                notes.add(f"Bỏ qua {key}=chua_biet: người dùng chưa xác định trạng thái.")
                continue
            mapped = ANH_XA_THUOC_TINH.get(key, {}).get(value)
            if mapped is None:
                notes.add(f"Bỏ qua {key}={value}: thuộc tính có trong vocabulary nhưng Bayes chưa hỗ trợ.")
                continue
            node, state = mapped
        elif key in ANH_XA_BANG_CHUNG:
            node, state = ANH_XA_BANG_CHUNG[key]
        elif key in {"ThoiTiet", "Giong", "DinhDuong"}:
            value = str(raw_value).strip()
            if value not in NUT[key]["gia_tri"]:
                notes.add(f"Bỏ qua mã cũ {key}={value}: trạng thái không được định nghĩa.")
                continue
            node, state = key, value
        elif key == "BonDam":
            notes.add("Bỏ qua mã cũ BonDam: cao/thấp không tương đương chính xác với thừa/không thừa đạm.")
            continue
        else:
            notes.add(f"Bỏ qua {key}: không có trong vocabulary hoặc danh mục mã cũ.")
            continue
        candidates.setdefault(node, set()).add(state)

    result: dict[str, str] = {}
    for node in sorted(candidates):
        states = candidates[node]
        if len(states) == 1:
            result[node] = next(iter(states))
        else:
            notes.add(f"Bỏ qua nút {node}: bằng chứng mâu thuẫn ({', '.join(sorted(states))}).")
    return result, sorted(notes)


def _ancestors_and_nodes(targets: Iterable[str]) -> list[str]:
    needed: set[str] = set()

    def add(node: str) -> None:
        if node in needed:
            return
        needed.add(node)
        for parent in NUT[node]["cha"]:
            add(parent)

    for target in targets:
        add(target)
    return [node for node in NUT if node in needed]


def _xac_suat_dong_nhat(dong: dict[str, str], nodes: Iterable[str] | None = None) -> float:
    selected = list(nodes) if nodes is not None else list(NUT)
    probability = 1.0
    for node in selected:
        spec = NUT[node]
        key = tuple(dong[parent] for parent in spec["cha"])
        index = spec["gia_tri"].index(dong[node])
        probability *= spec["cpd"][key][index]
    return probability


def kiem_tra_cpd() -> None:
    """Kiểm tra đầy đủ CPD, xác suất và tính hợp lệ của cấu trúc DAG."""
    if set(NGUON_CPD) != set(NUT) or set(GIA_DINH_CPD) != set(NUT):
        raise ValueError("Thiếu provenance/giả định CPD cho một hoặc nhiều nút.")
    for node, spec in NUT.items():
        parents = spec["cha"]
        if any(parent not in NUT for parent in parents):
            raise ValueError(f"Nút {node} tham chiếu cha không tồn tại.")
        if any(list(NUT).index(parent) >= list(NUT).index(node) for parent in parents):
            raise ValueError(f"Cấu trúc NUT không theo thứ tự topo tại {node}.")
        expected = set(itertools.product(*[NUT[parent]["gia_tri"] for parent in parents])) if parents else {()}
        if set(spec["cpd"]) != expected:
            raise ValueError(f"CPD của {node} thiếu/thừa tổ hợp trạng thái cha.")
        for parent_state, values in spec["cpd"].items():
            if len(values) != len(spec["gia_tri"]):
                raise ValueError(f"CPD của {node} tại {parent_state} sai số trạng thái.")
            if any(isinstance(value, bool) or not isinstance(value, (int, float))
                   or not math.isfinite(value) or not 0.0 <= value <= 1.0 for value in values):
                raise ValueError(f"CPD của {node} tại {parent_state} có xác suất ngoài [0, 1].")
            if not math.isclose(sum(values), 1.0, abs_tol=1e-9):
                raise ValueError(f"CPD của {node} tại {parent_state} không cộng bằng 1.")


def _tat_ca_dong_nhat(nodes: Iterable[str] | None = None):
    selected = list(nodes) if nodes is not None else list(NUT)
    for values in itertools.product(*[NUT[node]["gia_tri"] for node in selected]):
        yield dict(zip(selected, values))


def _truy_van_joint_liet_ke(bang_chung: dict[str, str]) -> dict[tuple[str, str, str], float]:
    """Phép liệt kê độc lập trên bao đóng tổ tiên của evidence và ba bệnh."""
    query_nodes = BENH_NODES
    required = _ancestors_and_nodes([*query_nodes, *bang_chung.keys()])
    total = 0.0
    joint = {
        states: 0.0
        for states in itertools.product(*[NUT[node]["gia_tri"] for node in query_nodes])
    }
    for row in _tat_ca_dong_nhat(required):
        if any(row[node] != state for node, state in bang_chung.items()):
            continue
        probability = _xac_suat_dong_nhat(row, required)
        total += probability
        joint[(row["DaoOn"], row["BacLa"], row["DomNau"])] += probability
    if total <= 0.0:
        raise ValueError(f"Bằng chứng không thể xảy ra: {bang_chung}")
    return {states: value / total for states, value in joint.items()}


def xay_dung_mang_pgmpy():
    """Dựng DiscreteBayesianNetwork từ đặc tả NUT."""
    import numpy as np
    from pgmpy.factors.discrete import TabularCPD

    try:
        from pgmpy.models import DiscreteBayesianNetwork as Network
    except ImportError:
        from pgmpy.models import BayesianNetwork as Network

    network = Network()
    for node, spec in NUT.items():
        network.add_node(node)
        for parent in spec["cha"]:
            network.add_edge(parent, node)
    cpds = []
    for node, spec in NUT.items():
        parent_states = itertools.product(*[NUT[parent]["gia_tri"] for parent in spec["cha"]])
        columns = [spec["cpd"][tuple(states)] for states in parent_states]
        params = {
            "variable": node,
            "variable_card": len(spec["gia_tri"]),
            "values": np.asarray(columns, dtype=float).T,
            "state_names": {node: list(spec["gia_tri"])},
        }
        if spec["cha"]:
            params["evidence"] = list(spec["cha"])
            params["evidence_card"] = [len(NUT[parent]["gia_tri"]) for parent in spec["cha"]]
            for parent in spec["cha"]:
                params["state_names"][parent] = list(NUT[parent]["gia_tri"])
        cpds.append(TabularCPD(**params))
    network.add_cpds(*cpds)
    if not network.check_model():
        raise ValueError("Mô hình Bayes không hợp lệ (check_model thất bại).")
    return network


def _truy_van_joint_pgmpy(bang_chung: dict[str, str]) -> dict[tuple[str, str, str], float]:
    from pgmpy.inference import VariableElimination

    network = xay_dung_mang_pgmpy()
    factor = VariableElimination(network).query(
        variables=list(BENH_NODES), evidence=bang_chung or None, show_progress=False
    )
    result = {}
    for states in itertools.product(*[NUT[node]["gia_tri"] for node in BENH_NODES]):
        assignment = dict(zip(BENH_NODES, states))
        result[states] = float(factor.get_value(**assignment))
    total = sum(result.values())
    if total <= 0.0:
        raise ValueError("Phân phối đồng thời pgmpy có tổng bằng 0.")
    return {key: value / total for key, value in result.items()}


def _phan_phoi_bon_lop(joint: Mapping[tuple[str, str, str], float]):
    class_mass = {"dao_on": 0.0, "bac_la": 0.0, "dom_nau": 0.0, "la_khoe": 0.0}
    multi_mass = 0.0
    for states, probability in joint.items():
        present = [node for node, state in zip(BENH_NODES, states) if state == "co"]
        if len(present) == 0:
            class_mass["la_khoe"] += probability
        elif len(present) == 1:
            class_mass[{"DaoOn": "dao_on", "BacLa": "bac_la", "DomNau": "dom_nau"}[present[0]]] += probability
        else:
            multi_mass += probability
    valid_mass = sum(class_mass.values())
    if valid_mass <= 0:
        raise ValueError("Không có khối lượng xác suất cho bốn lớp đơn bệnh/lá khỏe.")
    return ({key: value / valid_mass for key, value in class_mass.items()}, multi_mass)


def truy_van(
    bang_chung: Mapping[str, object] | Iterable[str] | None = None,
    su_dung_pgmpy: bool = True,
) -> dict:
    """Trả posterior bệnh, phân phối đồng thời, evidence thực dùng và ghi chú."""
    kiem_tra_cpd()
    evidence, notes = bang_chung_bayes(bang_chung)
    method = "Liệt kê độc lập trên bao đóng tổ tiên"
    joint = None
    if su_dung_pgmpy:
        try:
            joint = _truy_van_joint_pgmpy(evidence)
            method = "pgmpy – VariableElimination"
        except ImportError:
            notes.append("Chưa cài pgmpy: dùng phép liệt kê độc lập.")
        except Exception as error:
            notes.append(f"pgmpy không truy vấn được ({error}); dùng phép liệt kê độc lập.")
    if joint is None:
        joint = _truy_van_joint_liet_ke(evidence)
    classes, multi_mass = _phan_phoi_bon_lop(joint)
    exact_healthy = joint[("khong", "khong", "khong")]
    marginals = {
        node: {
            state: sum(prob for states, prob in joint.items() if states[index] == state)
            for state in NUT[node]["gia_tri"]
        }
        for index, node in enumerate(BENH_NODES)
    }
    return {
        "xac_suat": {label: round(value, 10) for label, value in classes.items()},
        "chi_tiet": marginals,
        "phan_phoi_dong_thoi": {"|".join(states): round(prob, 10) for states, prob in joint.items()},
        "xac_suat_dong_mac": round(multi_mass, 10),
        "xac_suat_la_khoe_dong_thoi": round(exact_healthy, 10),
        "bang_chung": evidence,
        "phuong_phap": method,
        "ghi_chu": sorted(set(notes)),
        "ghi_chu_la_khoe": (
            "P(lá khỏe) = P(¬đạo ôn, ¬bạc lá, ¬đốm nâu) lấy từ phân phối đồng thời; "
            "không nhân các xác suất biên. Phân phối bốn lớp loại trừ đồng mắc."
        ),
        "gia_dinh_phan_lop": (
            "Mạng cho phép đồng mắc; đầu ra CNN bốn lớp là phân phối có điều kiện "
            "trên không bệnh hoặc đúng một bệnh. Khối lượng đồng mắc báo riêng."
        ),
        "thuoc_tinh_bayes_ho_tro": sorted(
            key for key, states in ANH_XA_THUOC_TINH.items()
            if states["co"] is not None and states["khong"] is not None
        ),
    }


def in_cau_truc() -> None:
    print(f"Mạng Bayes {len(NUT)} nút; quan sát triệu chứng là các nút riêng:")
    for node, spec in NUT.items():
        print(f"  {node:<20} | cha: {', '.join(spec['cha']) or '—'} | {', '.join(spec['gia_tri'])}")
    print("\nCPD là giả định định tính; nguồn S1-S4 không cung cấp tần suất số. Cần hiệu chuẩn thực nghiệm.")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Truy vấn mạng Bayes bệnh lá lúa.")
    parser.add_argument("--bang-chung", nargs="*", default=None,
                        help="thuộc_tính=co|khong|chua_biet hoặc mã sự kiện cũ đã công bố")
    parser.add_argument("--khong-pgmpy", action="store_true")
    args = parser.parse_args(argv)
    in_cau_truc()
    evidence = args.bang_chung or [
        "vet_bac_ung_nuoc_tren_phien_la=co",
        "vet_bac_bat_dau_o_chop_la=co",
        "vet_bac_mep_luon_song=co",
        "thua_dam=co",
    ]
    result = truy_van(evidence, su_dung_pgmpy=not args.khong_pgmpy)
    print("\nBằng chứng thực dùng:", result["bang_chung"])
    for label, probability in result["xac_suat"].items():
        print(f"  P({label}) = {probability:.2%}")
    for note in result["ghi_chu"]:
        print("  *", note)
    return 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    raise SystemExit(main())
