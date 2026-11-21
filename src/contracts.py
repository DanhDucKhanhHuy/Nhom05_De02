"""Kiểu dữ liệu chung cho giao tiếp giữa các chức năng; không chứa thuật toán."""
from collections.abc import Callable
from typing import Literal, TypedDict

MaLop = Literal["dao_on", "bac_la", "dom_nau", "la_khoe"]
ToaDo = tuple[int, int]
Top3 = list[tuple[MaLop, float]]
HoiNguoiDung = Callable[[str], bool | None]
ThuatToan = Literal["hill", "greedy"]


class BanDo(TypedDict):
    """Bản đồ đọc trực tiếp từ JSON; start là danh sách [hàng, cột]."""

    rows: int
    cols: int
    start: list[int]
    k: int
    p: int
    cells: list[list[int]]


class NguonLuat(TypedDict):
    """Trích dẫn nguồn cụ thể gắn với một luật."""

    ma: str
    muc: str


class Luat(TypedDict):
    """Luật dạng thuộc_tính=giá_trị theo hợp đồng CN2."""

    id: str
    loai: Literal["chan_doan", "nguy_co", "trung_gian", "khuyen_nghi"]
    neu: list[str]
    thi: str
    nguon: NguonLuat


class VetLuat(TypedDict):
    """Một luật thực sự được dùng, cùng điều kiện và nguồn đã chụp lại."""

    id: str
    dieu_kien: list[str]
    ket_luan: str
    nguon: NguonLuat


TrangThaiSuyDien = Literal["xac_nhan", "bac_bo", "chua_du"]


class KetQuaSuyDienLui(TypedDict):
    """Trạng thái chứng minh đích và vết của nhánh chứng minh thành công."""

    trang_thai: TrangThaiSuyDien
    vet: list[VetLuat]


class ChiTietChanDoan(TypedDict, total=False):
    """Các trường bổ sung tùy chọn, không phá hợp đồng bốn trường cũ."""

    giai_thich: str
    vet: list[VetLuat]


class ChanDoan(ChiTietChanDoan):
    """Kết luận có thể chưa xác định khi không đủ dữ kiện."""

    ket_luan: MaLop | None
    do_tin_cay: float | None
    luat_da_dung: list[str]
    nguon: list[str]


class SuKien(TypedDict):
    """Sự kiện theo thứ tự thực thi."""

    loai: Literal["bay", "phun", "nap"]
    vi_tri: ToaDo


class SuKienBay(SuKien, total=False):
    """Thông tin pin và vật cản bổ sung cho một chặng bay."""

    quang_duong: int
    pin_tieu_hao: int
    qua_vat_can: tuple[ToaDo, ...]


class LoTrinh(TypedDict):
    """Đường đi gồm ô đầu và đích của từng bước bay, có thể lặp ô."""

    duong_di: list[ToaDo]
    su_kien: list[SuKien | SuKienBay]
    tong_quang_duong: int
    so_lan_ve_tram: int
    thoi_gian_chay: float
