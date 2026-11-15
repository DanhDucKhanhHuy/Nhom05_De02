"""Kiểu dữ liệu chung cho giao tiếp giữa các chức năng; không chứa thuật toán."""
from collections.abc import Callable
from typing import Literal, TypedDict

MaLop = Literal["dao_on", "bac_la", "dom_nau", "la_khoe"]
ToaDo = tuple[int, int]
Top3 = list[tuple[MaLop, float]]
HoiNguoiDung = Callable[[str], bool | None]
ThuatToan = Literal["hill", "beam", "greedy"]


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


class ChanDoan(TypedDict):
    """Kết luận có thể chưa xác định khi không đủ dữ kiện."""

    ket_luan: MaLop | None
    do_tin_cay: float | None
    luat_da_dung: list[str]
    nguon: list[str]


class SuKien(TypedDict):
    """Sự kiện theo thứ tự thực thi, gồm cả bước bay."""

    loai: Literal["bay", "phun", "nap"]
    vi_tri: ToaDo


class LoTrinh(TypedDict):
    """Đường đi gồm ô đầu và đích của từng bước bay, có thể lặp ô."""

    duong_di: list[ToaDo]
    su_kien: list[SuKien]
    tong_quang_duong: int
    so_lan_ve_tram: int
    thoi_gian_chay: float
