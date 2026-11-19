"""E3 - Hoạt cảnh lộ trình drone - TV5"""
from .grid_editor import MUC_BENH, TRAM

TEN_THUAT_TOAN = {"greedy": "Tham lam", "astar": "A* toàn cục"}
GIOI_HAN_ASTAR = 8  # A* toàn cục chỉ chạy nhanh khi ít ô bệnh


def dem_o_benh(ban_do):
    so_o_benh = 0
    for hang in ban_do["cells"]:
        for o in hang:
            if o in MUC_BENH:
                so_o_benh += 1
    return so_o_benh


def tim_cac_tram(ban_do):
    cac_tram = set()
    for r, hang in enumerate(ban_do["cells"]):
        for c, o in enumerate(hang):
            if o == TRAM:
                cac_tram.add((r, c))
    return cac_tram


def lap_lo_trinh(ban_do, thuat_toan="greedy"):
    """Gọi thuật toán CN1, trả về LoTrinh"""
    from src.search.full_astar import astar_route
    from src.search.greedy import greedy_route

    k = ban_do["k"]
    p = ban_do["p"]

    if thuat_toan == "astar":
        if dem_o_benh(ban_do) > GIOI_HAN_ASTAR:
            raise ValueError(f"A* toàn cục chỉ dùng cho bản đồ ≤ {GIOI_HAN_ASTAR} ô bệnh.")
        lo_trinh = astar_route(ban_do, k, p)
    else:
        lo_trinh = greedy_route(ban_do, k, p)
    return lo_trinh


def dung_khung_hinh(ban_do, lo_trinh):
    """Trạng thái drone sau từng sự kiện; khung 0 là lúc xuất phát"""
    k = ban_do["k"]
    p = ban_do["p"]
    cac_tram = tim_cac_tram(ban_do)
    diem_xuat_phat = tuple(ban_do["start"])

    # trạng thái lúc xuất phát
    trang_thai = {
        "vi_tri": diem_xuat_phat,
        "thuoc": k,
        "pin": p,
        "quang_duong": 0,
        "ve_tram": 0,
        "da_phun": 0,
        "so_diem_vet": 1,
        "su_kien": None,
    }
    danh_sach_khung = [trang_thai]
    vet = [diem_xuat_phat]   # các ô drone đã bay qua
    thoi_diem_phun = {}      # ô -> số thứ tự khung lúc được phun

    so_thu_tu = 0
    for su_kien in lo_trinh["su_kien"]:
        so_thu_tu += 1
        trang_thai = dict(trang_thai)  # chép trạng thái trước rồi sửa
        trang_thai["su_kien"] = su_kien
        vi_tri = tuple(su_kien["vi_tri"])

        if su_kien["loai"] == "bay":
            for o_vat_can in su_kien.get("qua_vat_can", ()):
                vet.append(tuple(o_vat_can))
            vet.append(vi_tri)

            trang_thai["vi_tri"] = vi_tri
            trang_thai["pin"] = trang_thai["pin"] - su_kien.get("pin_tieu_hao", 1)
            trang_thai["quang_duong"] = trang_thai["quang_duong"] + su_kien.get("quang_duong", 1)
            if vi_tri in cac_tram:
                trang_thai["ve_tram"] = trang_thai["ve_tram"] + 1
            trang_thai["so_diem_vet"] = len(vet)

        elif su_kien["loai"] == "phun":
            trang_thai["thuoc"] = trang_thai["thuoc"] - 1
            trang_thai["da_phun"] = trang_thai["da_phun"] + 1
            thoi_diem_phun[vi_tri] = so_thu_tu

        elif su_kien["loai"] == "nap":
            trang_thai["thuoc"] = k
            trang_thai["pin"] = p

        danh_sach_khung.append(trang_thai)

    return danh_sach_khung, vet, thoi_diem_phun
