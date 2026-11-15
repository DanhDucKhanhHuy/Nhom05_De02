"""C5 - Mạng Bayes >= 5 nút bằng pgmpy, bảng CPD, ví dụ truy vấn xác suất hậu nghiệm.
"""

from __future__ import annotations

import argparse
import itertools
import json
import math
from pathlib import Path
from typing import Iterable, Mapping

MA_BENH_BAYES = {"dao_on": "DaoOn", "bac_la": "BacLa", "dom_nau": "DomNau"}
VOCABULARY_PATH = Path(__file__).with_name("vocabulary.json")

# Căn cứ định tính cho cấu trúc/nhóm triệu chứng; không có nguồn nào cung cấp
# các tần suất số dùng trong CPD. Các con số CPD và prior nút gốc là giả định.
NGUON_CPD = {
    "DaoOn": ("S1", "S4"),
    "BacLa": ("S2",),
    "DomNau": ("S3",),
    "TrieuChung": ("S1", "S2", "S3", "S4"),
    "ThoiTiet": (),
    "BonDam": (),
    "Giong": (),
    "DinhDuong": (),
}

#: Đặc tả mạng: giá trị của từng nút, nút cha và bảng CPD.
#: Khóa của ``cpd`` là tổ hợp giá trị các nút cha (theo đúng thứ tự ``cha``);
#: giá trị là xác suất của các giá trị trong ``gia_tri``.
NUT: dict[str, dict] = {
    "ThoiTiet": {
        "nhan": "Thời tiết",
        "gia_tri": ["mua_am", "kho"],
        "cha": [],
        "cpd": {(): [0.60, 0.40]},
    },
    "BonDam": {
        "nhan": "Bón đạm",
        "gia_tri": ["cao", "thap"],
        "cha": [],
        "cpd": {(): [0.45, 0.55]},
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
        "cha": ["ThoiTiet", "BonDam", "Giong"],
        "cpd": {
            ("mua_am", "cao", "nhiem"): [0.75, 0.25],
            ("mua_am", "cao", "khang"): [0.45, 0.55],
            ("mua_am", "thap", "nhiem"): [0.50, 0.50],
            ("mua_am", "thap", "khang"): [0.20, 0.80],
            ("kho", "cao", "nhiem"): [0.35, 0.65],
            ("kho", "cao", "khang"): [0.15, 0.85],
            ("kho", "thap", "nhiem"): [0.15, 0.85],
            ("kho", "thap", "khang"): [0.05, 0.95],
        },
    },
    "BacLa": {
        "nhan": "Bệnh bạc lá",
        "gia_tri": ["co", "khong"],
        "cha": ["ThoiTiet", "BonDam"],
        "cpd": {
            ("mua_am", "cao"): [0.70, 0.30],
            ("mua_am", "thap"): [0.45, 0.55],
            ("kho", "cao"): [0.30, 0.70],
            ("kho", "thap"): [0.12, 0.88],
        },
    },
    "DomNau": {
        "nhan": "Bệnh đốm nâu",
        "gia_tri": ["co", "khong"],
        "cha": ["DinhDuong", "ThoiTiet"],
        "cpd": {
            ("thieu", "mua_am"): [0.70, 0.30],
            ("thieu", "kho"): [0.60, 0.40],
            ("du", "mua_am"): [0.30, 0.70],
            ("du", "kho"): [0.20, 0.80],
        },
    },
    "TrieuChung": {
        "nhan": "Triệu chứng trên lá",
        "gia_tri": ["vet_thoi", "chop_la_kho", "dom_tron", "khong"],
        "cha": ["DaoOn", "BacLa", "DomNau"],
        "cpd": {
            ("co", "khong", "khong"): [0.85, 0.05, 0.02, 0.08],
            ("khong", "co", "khong"): [0.03, 0.85, 0.02, 0.10],
            ("khong", "khong", "co"): [0.02, 0.03, 0.85, 0.10],
            ("co", "co", "khong"): [0.50, 0.40, 0.03, 0.07],
            ("co", "khong", "co"): [0.50, 0.03, 0.40, 0.07],
            ("khong", "co", "co"): [0.02, 0.45, 0.45, 0.08],
            ("co", "co", "co"): [0.34, 0.33, 0.33, 0.00],
            ("khong", "khong", "khong"): [0.02, 0.02, 0.03, 0.93],
        },
    },
}

#: Ánh xạ sự kiện của hệ luật sang bằng chứng của mạng Bayes.
ANH_XA_BANG_CHUNG: dict[str, tuple[str, str]] = {
    "tc_vet_thoi": ("TrieuChung", "vet_thoi"),
    "tc_chop_la_kho": ("TrieuChung", "chop_la_kho"),
    "tc_dom_tron": ("TrieuChung", "dom_tron"),
    "tc_dom_nhieu": ("TrieuChung", "dom_tron"),
    "tc_khong_co": ("TrieuChung", "khong"),
    "tt_am_do_cao": ("ThoiTiet", "mua_am"),
    "tt_suong_mu": ("ThoiTiet", "mua_am"),
    "tt_mua_nhieu": ("ThoiTiet", "mua_am"),
    "tt_kho_han": ("ThoiTiet", "kho"),
    "tq_dam_cao": ("BonDam", "cao"),
    "tq_giong_nhiem": ("Giong", "nhiem"),
    "tq_dat_ngheo": ("DinhDuong", "thieu"),
    "tq_thieu_kali": ("DinhDuong", "thieu"),
}


# Ánh xạ trực tiếp thuộc tính chung trong vocabulary.json sang trạng thái nút.
# Chỉ ánh xạ khi ngữ nghĩa tương đương; phủ định một triệu chứng không đồng nghĩa
# với "không có triệu chứng".
ANH_XA_THUOC_TINH: dict[str, dict[str, tuple[str, str] | None]] = {
    "vet_la_hinh_thoi": {
        "co": ("TrieuChung", "vet_thoi"),
        "khong": None,
        "chua_biet": None,
    },
    "vet_la_tam_xam_kho": {
        "co": ("TrieuChung", "vet_thoi"),
        "khong": None,
        "chua_biet": None,
    },
    "vet_la_vien_nau": {
        "co": ("TrieuChung", "vet_thoi"),
        "khong": None,
        "chua_biet": None,
    },
    "dom_tron_hoac_bau_duc_nau": {
        "co": ("TrieuChung", "dom_tron"),
        "khong": None,
        "chua_biet": None,
    },
    "dom_nau_vien_sam": {
        "co": ("TrieuChung", "dom_tron"),
        "khong": None,
        "chua_biet": None,
    },
    "dom_nau_tam_nhat_xam": {
        "co": ("TrieuChung", "dom_tron"),
        "khong": None,
        "chua_biet": None,
    },
    "am_u_va_suong_som": {
        "co": ("ThoiTiet", "mua_am"),
        "khong": ("ThoiTiet", "kho"),
        "chua_biet": None,
    },
    "thua_dam": {
        "co": ("BonDam", "cao"),
        "khong": ("BonDam", "thap"),
        "chua_biet": None,
    },
}

TRANG_THAI_BANG_CHUNG = {"co", "khong", "chua_biet"}


def _thuoc_tinh_trong_vocabulary(key: str) -> bool:
    try:
        document = json.loads(VOCABULARY_PATH.read_text(encoding="utf-8"))
        definition = document.get("thuoc_tinh", {}).get(key, {})
        return definition.get("loai") == "du_kien_nguoi_dung"
    except (OSError, ValueError):
        return False


def bang_chung_bayes(
    bang_chung: Mapping[str, object] | Iterable[str] | None,
) -> tuple[dict[str, str], list[str]]:
    """Chuẩn hóa bằng chứng TV2/TV3 theo thứ tự bất biến.

    - Mapping hỗ trợ ``thuoc_tinh: co|khong|chua_biet``.
    - Iterable hỗ trợ mã sự kiện cũ hoặc ``thuoc_tinh=gia_tri``.
    - ``chua_biet`` được bỏ qua; thuộc tính không có ánh xạ được ghi chú.
    - Nếu các dữ kiện mâu thuẫn cùng một nút Bayes, loại toàn bộ nút đó.
      Quy tắc này không phụ thuộc thứ tự nhập.
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
            else:
                entries.append((item, True))

    candidates: dict[str, set[str]] = {}
    notes: set[str] = set()
    for key, raw_value in entries:
        if key in ANH_XA_THUOC_TINH or _thuoc_tinh_trong_vocabulary(key):
            value = str(raw_value).lower()
            if value not in TRANG_THAI_BANG_CHUNG:
                raise ValueError(
                    f"Trạng thái của thuộc tính {key} không hợp lệ: {raw_value!r}."
                )
            if value == "chua_biet":
                notes.add(f"Bỏ qua {key}=chua_biet: người dùng chưa xác định trạng thái.")
                continue
            mapped = ANH_XA_THUOC_TINH.get(key, {}).get(value)
            if mapped is None:
                notes.add(
                    f"Bỏ qua {key}={value}: thuộc tính có trong vocabulary nhưng "
                    "chưa có ánh xạ tương đương trong mạng Bayes."
                )
                continue
            node, state = mapped
        else:
            if key not in ANH_XA_BANG_CHUNG:
                notes.add(f"Bỏ qua {key}: không có trong vocabulary hoặc mã sự kiện Bayes.")
                continue
            node, state = ANH_XA_BANG_CHUNG[key]

        candidates.setdefault(node, set()).add(state)

    result: dict[str, str] = {}
    for node in sorted(candidates):
        states = candidates[node]
        if len(states) == 1:
            result[node] = next(iter(states))
        else:
            notes.add(
                f"Bỏ qua nút {node}: bằng chứng mâu thuẫn "
                f"({', '.join(sorted(states))})."
            )
    return result, sorted(notes)


def _xac_suat_dong_nhat(dong: dict[str, str]) -> float:
    xac_suat = 1.0
    for ten_nut, dac_ta in NUT.items():
        khoa = tuple(dong[cha] for cha in dac_ta["cha"])
        chi_so = dac_ta["gia_tri"].index(dong[ten_nut])
        xac_suat *= dac_ta["cpd"][khoa][chi_so]
    return xac_suat


def kiem_tra_cpd() -> None:
    """Kiểm tra mỗi bảng CPD có đủ tổ hợp cha và tổng xác suất bằng 1."""
    for ten_nut, dac_ta in NUT.items():
        to_hop_mong_doi = set(itertools.product(
            *[NUT[cha]["gia_tri"] for cha in dac_ta["cha"]]
        )) if dac_ta["cha"] else {()}
        if set(dac_ta["cpd"]) != to_hop_mong_doi:
            raise ValueError(
                f"CPD của {ten_nut} thiếu hoặc thừa tổ hợp trạng thái cha."
            )
        for khoa, gia_tri in dac_ta["cpd"].items():
            if len(gia_tri) != len(dac_ta["gia_tri"]):
                raise ValueError(f"CPD của {ten_nut} tại {khoa} sai số giá trị.")
            if any(not isinstance(value, (int, float)) or not math.isfinite(value)
                   or not 0.0 <= value <= 1.0 for value in gia_tri):
                raise ValueError(f"CPD của {ten_nut} tại {khoa} có xác suất ngoài [0, 1].")
            if abs(sum(gia_tri) - 1.0) > 1e-6:
                raise ValueError(f"CPD của {ten_nut} tại {khoa} không cộng lại bằng 1.")
    tong = sum(_xac_suat_dong_nhat(dong) for dong in _tat_ca_dong_nhat())
    if abs(tong - 1.0) > 1e-6:
        raise ValueError(f"Phân phối đồng thời cộng lại bằng {tong}, không phải 1.")


def _tat_ca_dong_nhat():
    ten_nut = list(NUT)
    for to_hop in itertools.product(*[NUT[n]["gia_tri"] for n in ten_nut]):
        yield dict(zip(ten_nut, to_hop))


def _truy_van_liet_ke(bang_chung: dict[str, str]) -> dict[str, dict[str, float]]:
    """Tính phân phối biên chính xác bằng liệt kê (dùng khi không có pgmpy)."""
    tong = 0.0
    tich: dict[str, dict[str, float]] = {
        ten: {gia_tri: 0.0 for gia_tri in dac_ta["gia_tri"]} for ten, dac_ta in NUT.items()
    }
    for dong in _tat_ca_dong_nhat():
        if any(dong[nut] != gia_tri for nut, gia_tri in bang_chung.items()):
            continue
        p = _xac_suat_dong_nhat(dong)
        tong += p
        for ten_nut, gia_tri in dong.items():
            tich[ten_nut][gia_tri] += p
    if tong <= 0:
        raise ValueError(f"Bằng chứng không thể xảy ra: {bang_chung}")
    return {
        ten: {gia_tri: gia_tri_xac_suat / tong for gia_tri, gia_tri_xac_suat in ds.items()}
        for ten, ds in tich.items()
    }


def xay_dung_mang_pgmpy():
    """Dựng ``DiscreteBayesianNetwork`` của pgmpy từ đặc tả CPD ở trên."""
    import numpy as np
    from pgmpy.factors.discrete import TabularCPD

    try:  # pgmpy >= 1.0
        from pgmpy.models import DiscreteBayesianNetwork as LopMang
    except ImportError:  # pgmpy 0.1.x
        from pgmpy.models import BayesianNetwork as LopMang

    mang = LopMang()
    for ten_nut, dac_ta in NUT.items():
        mang.add_node(ten_nut)
        for cha in dac_ta["cha"]:
            mang.add_edge(cha, ten_nut)

    ds_cpd = []
    for ten_nut, dac_ta in NUT.items():
        cot = [
            dac_ta["cpd"][tuple(to_hop)]
            for to_hop in itertools.product(*[NUT[cha]["gia_tri"] for cha in dac_ta["cha"]])
        ]
        gia_tri = np.array(cot, dtype=float).T
        tham_so = {
            "variable": ten_nut,
            "variable_card": len(dac_ta["gia_tri"]),
            "values": gia_tri,
            # Phải khai báo tên trạng thái, nếu không pgmpy gán mặc định "0", "1"
            # và truy vấn theo tên (mua_am, cao, nhiem...) sẽ lỗi KeyError.
            "state_names": {ten_nut: list(dac_ta["gia_tri"])},
        }
        for cha in dac_ta["cha"]:
            tham_so["state_names"][cha] = list(NUT[cha]["gia_tri"])
        if dac_ta["cha"]:
            tham_so["evidence"] = list(dac_ta["cha"])
            tham_so["evidence_card"] = [len(NUT[cha]["gia_tri"]) for cha in dac_ta["cha"]]
        ds_cpd.append(TabularCPD(**tham_so))

    mang.add_cpds(*ds_cpd)
    if not mang.check_model():
        raise ValueError("Mô hình Bayes không hợp lệ (kiểm tra CPD).")
    return mang


def _truy_van_joint_liet_ke(bang_chung: dict[str, str]) -> dict[tuple[str, str, str], float]:
    """Phân phối đồng thời chính xác của ba biến bệnh khi có bằng chứng."""
    disease_nodes = ("DaoOn", "BacLa", "DomNau")
    total = 0.0
    joint = {
        states: 0.0
        for states in itertools.product(*[NUT[node]["gia_tri"] for node in disease_nodes])
    }
    for row in _tat_ca_dong_nhat():
        if any(row[node] != state for node, state in bang_chung.items()):
            continue
        probability = _xac_suat_dong_nhat(row)
        total += probability
        joint[(row["DaoOn"], row["BacLa"], row["DomNau"])] += probability
    if total <= 0:
        raise ValueError(f"Bằng chứng không thể xảy ra: {bang_chung}")
    return {states: value / total for states, value in joint.items()}


def _truy_van_joint_pgmpy(bang_chung: dict[str, str]) -> dict[tuple[str, str, str], float]:
    """Truy vấn phân phối đồng thời ba bệnh bằng VariableElimination."""
    from pgmpy.inference import VariableElimination

    network = xay_dung_mang_pgmpy()
    factor = VariableElimination(network).query(
        variables=["DaoOn", "BacLa", "DomNau"],
        evidence=bang_chung or None,
        show_progress=False,
    )
    states = itertools.product(
        *(NUT[node]["gia_tri"] for node in ("DaoOn", "BacLa", "DomNau"))
    )
    result = {}
    for state_tuple in states:
        assignment = dict(zip(("DaoOn", "BacLa", "DomNau"), state_tuple))
        result[state_tuple] = float(factor.get_value(**assignment))
    total = sum(result.values())
    if total <= 0:
        raise ValueError("Phân phối đồng thời pgmpy có tổng bằng 0.")
    return {key: value / total for key, value in result.items()}


def _phan_phoi_bon_lop(
    joint: Mapping[tuple[str, str, str], float],
) -> tuple[dict[str, float], float]:
    """Đổi 3 biến bệnh có thể đồng mắc thành bốn lớp loại trừ nhau.

    Lớp bệnh tương ứng đúng một bệnh; lá khỏe tương ứng không bệnh nào.
    Khối lượng xác suất đồng mắc từ hai bệnh trở lên được báo riêng và loại
    khỏi mẫu số phân loại bốn lớp, sau đó bốn lớp được chuẩn hóa có điều kiện.
    """
    class_mass = {"dao_on": 0.0, "bac_la": 0.0, "dom_nau": 0.0, "la_khoe": 0.0}
    multi_mass = 0.0
    for states, probability in joint.items():
        present = [node for node, state in zip(("DaoOn", "BacLa", "DomNau"), states)
                   if state == "co"]
        if len(present) == 0:
            class_mass["la_khoe"] += probability
        elif len(present) == 1:
            class_label = {
                "DaoOn": "dao_on",
                "BacLa": "bac_la",
                "DomNau": "dom_nau",
            }[present[0]]
            class_mass[class_label] += probability
        else:
            multi_mass += probability
    valid_mass = sum(class_mass.values())
    if valid_mass <= 0:
        raise ValueError("Không có khối lượng xác suất cho bốn lớp đơn bệnh/lá khỏe.")
    return ({label: value / valid_mass for label, value in class_mass.items()}, multi_mass)


def truy_van(
    bang_chung: Mapping[str, object] | Iterable[str] | None = None,
    su_dung_pgmpy: bool = True,
) -> dict:
    """Truy vấn hậu nghiệm và phân phối bốn lớp loại trừ nhau.

    Mạng nền cho phép nhiều bệnh đồng thời. Để tương thích đầu ra CNN bốn lớp,
    chỉ các trạng thái không bệnh hoặc đúng một bệnh được đưa vào phân phối lớp;
    xác suất đồng mắc được trả riêng ở ``xac_suat_dong_mac``.
    """
    kiem_tra_cpd()
    evidence, notes = bang_chung_bayes(bang_chung)
    method = "Liệt kê độc lập toàn bộ phân phối đồng thời"
    joint = None
    if su_dung_pgmpy:
        try:
            joint = _truy_van_joint_pgmpy(evidence)
            method = "pgmpy – VariableElimination (truy vấn đồng thời)"
        except ImportError:
            notes.append("Chưa cài pgmpy: dùng phép liệt kê độc lập.")
        except Exception as error:  # fallback minh bạch cho lỗi tương thích
            notes.append(f"pgmpy không truy vấn được ({error}); dùng phép liệt kê độc lập.")
    if joint is None:
        joint = _truy_van_joint_liet_ke(evidence)

    classes, multi_mass = _phan_phoi_bon_lop(joint)
    exact_healthy_mass = joint[("khong", "khong", "khong")]
    marginals = {
        node: {
            state: sum(prob for states, prob in joint.items()
                       if states[index] == state)
            for state in NUT[node]["gia_tri"]
        }
        for index, node in enumerate(("DaoOn", "BacLa", "DomNau"))
    }
    return {
        "xac_suat": {label: round(value, 10) for label, value in classes.items()},
        "chi_tiet": marginals,
        "phan_phoi_dong_thoi": {
            "|".join(states): round(probability, 10)
            for states, probability in joint.items()
        },
        "xac_suat_dong_mac": round(multi_mass, 10),
        "xac_suat_la_khoe_dong_thoi": round(exact_healthy_mass, 10),
        "bang_chung": evidence,
        "phuong_phap": method,
        "ghi_chu": sorted(set(notes)),
        "ghi_chu_la_khoe": (
            "P(lá khỏe) đồng thời là P(¬đạo ôn, ¬bạc lá, ¬đốm nâu), "
            "lấy trực tiếp từ phân phối đồng thời; không nhân các xác suất biên. "
            "Phân phối bốn lớp dùng thêm điều kiện không có đồng mắc."
        ),
        "gia_dinh_phan_lop": (
            "Mạng cho phép đồng mắc. Đầu ra bốn lớp là phân phối có điều kiện "
            "trên các trạng thái không bệnh hoặc đúng một bệnh; xác suất đồng mắc "
            "được báo riêng."
        ),
    }


def in_cau_truc() -> None:
    print("Mạng Bayes 8 nút (bảng CPD khai báo trong NUT):")
    for ten_nut, dac_ta in NUT.items():
        cha = ", ".join(dac_ta["cha"]) or "—"
        print(f"  {ten_nut:<11} | cha: {cha:<28} | giá trị: {', '.join(dac_ta['gia_tri'])}")
    print(
        "\nGhi chú: CPD là giả định định tính; S1–S4 chỉ hỗ trợ cấu trúc và nhóm triệu chứng, "
        "không cung cấp tần suất số trong bảng. Cần hiệu chuẩn bằng dữ liệu đồng ruộng.\n"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Truy vấn mạng Bayes bệnh lá lúa.")
    parser.add_argument(
        "--bang-chung",
        nargs="*",
        default=None,
        help="Mã sự kiện đã biết (ví dụ tc_vet_thoi tt_am_do_cao tq_dam_cao).",
    )
    parser.add_argument(
        "--khong-pgmpy",
        action="store_true",
        help="Bắt buộc dùng phép liệt kê thay vì pgmpy (để đối chiếu kết quả).",
    )
    args = parser.parse_args(argv)

    in_cau_truc()
    ds = args.bang_chung
    for nhan, bang_chung in (
        ("Truy vấn 1: chưa có bằng chứng (tiên nghiệm)", None),
        (
            "Truy vấn 2: vết hình thoi + mưa ẩm + bón nhiều đạm",
            ds or ["tc_vet_thoi", "tt_am_do_cao", "tq_dam_cao"],
        ),
    ):
        ket_qua = truy_van(bang_chung, su_dung_pgmpy=not args.khong_pgmpy)
        print(f"{nhan}")
        print(f"  Bằng chứng nút: {ket_qua['bang_chung'] or '—'} ({ket_qua['phuong_phap']})")
        for ma, p in ket_qua["xac_suat"].items():
            print(f"    P({ma:<8}) = {p:.1%}")
        for ghi_chu in ket_qua["ghi_chu"]:
            print(f"  * {ghi_chu}")
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())