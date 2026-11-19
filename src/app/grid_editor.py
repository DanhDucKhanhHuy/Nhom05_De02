"""E2 - Bản đồ lưới đánh dấu ô bệnh - TV5"""
import json
import random
from pathlib import Path

import pygame

from .giao_dien import CAO_THANH_TIEU_DE, MAU, ManHinh, Nut, ve_chu, ve_thanh_tieu_de

# mã ô theo README
KHOE, VAT_CAN, TRAM = 0, -1, 9
MUC_BENH = (1, 2, 3)
MA_HOP_LE = (KHOE, VAT_CAN, TRAM) + MUC_BENH


def tao_ban_do(so_hang=20, so_cot=20, k=8, p=100):
    cells = [[KHOE] * so_cot for _ in range(so_hang)]
    cells[0][0] = TRAM
    return {"rows": so_hang, "cols": so_cot, "start": [0, 0], "k": k, "p": p, "cells": cells}


def o_toi_duoc(cells, start):
    """Các ô đi tới được từ start (loang BFS)"""
    so_hang, so_cot = len(cells), len(cells[0])
    da_tham, hang_doi = {tuple(start)}, [tuple(start)]
    for r, c in hang_doi:
        for r2, c2 in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)):
            if (0 <= r2 < so_hang and 0 <= c2 < so_cot and (r2, c2) not in da_tham
                    and cells[r2][c2] != VAT_CAN):
                da_tham.add((r2, c2))
                hang_doi.append((r2, c2))
    return da_tham


def tao_ngau_nhien(so_hang=20, so_cot=20, k=8, p=100, ty_le_benh=0.15, ty_le_vat_can=0.1,
                   so_tram=2, rng=None):
    rng = rng or random.Random()
    while True:
        ban_do = tao_ban_do(so_hang, so_cot, k, p)
        cells = ban_do["cells"]
        o_trong = [(r, c) for r in range(so_hang) for c in range(so_cot) if (r, c) != (0, 0)]
        rng.shuffle(o_trong)
        so_vat_can, so_benh = int(len(o_trong) * ty_le_vat_can), int(len(o_trong) * ty_le_benh)
        for r, c in o_trong[:so_tram - 1]:
            cells[r][c] = TRAM
        o_trong = o_trong[so_tram - 1:]
        for r, c in o_trong[:so_vat_can]:
            cells[r][c] = VAT_CAN
        for r, c in o_trong[so_vat_can:so_vat_can + so_benh]:
            cells[r][c] = rng.choice(MUC_BENH)
        # mọi ô không phải vật cản phải tới được
        so_o_di_duoc = sum(o != VAT_CAN for hang in cells for o in hang)
        if len(o_toi_duoc(cells, [0, 0])) == so_o_di_duoc:
            return ban_do


def la_so_nguyen(x):
    return isinstance(x, int) and not isinstance(x, bool)


def kiem_tra(ban_do):
    """Trả về danh sách lỗi"""
    if not isinstance(ban_do, dict):
        return ["File không phải bản đồ."]
    cells = ban_do.get("cells")
    if (not isinstance(cells, list) or not cells
            or not all(isinstance(dong, list) and dong for dong in cells)):
        return ["Lưới rỗng hoặc sai định dạng."]
    so_hang, so_cot = len(cells), len(cells[0])
    if any(len(dong) != so_cot for dong in cells):
        return ["Các dòng không cùng số cột."]

    loi = []
    if ban_do.get("rows") != so_hang or ban_do.get("cols") != so_cot:
        loi.append("rows/cols không khớp với cells.")
    if any(not la_so_nguyen(o) or o not in MA_HOP_LE for dong in cells for o in dong):
        loi.append("Có mã ô không hợp lệ.")
    start = ban_do.get("start")
    if (not isinstance(start, list) or len(start) != 2 or not all(map(la_so_nguyen, start))
            or not (0 <= start[0] < so_hang and 0 <= start[1] < so_cot)
            or cells[start[0]][start[1]] == VAT_CAN):
        loi.append("Điểm xuất phát nằm ngoài lưới hoặc trên vật cản.")
    if not any(o == TRAM for dong in cells for o in dong):
        loi.append("Chưa có trạm nạp thuốc.")
    for khoa in ("k", "p"):
        if not la_so_nguyen(ban_do.get(khoa)) or ban_do[khoa] < 1:
            loi.append(f"{khoa} phải là số nguyên ≥ 1.")
    return loi


def doc_ban_do(duong_dan):
    try:
        with open(duong_dan, encoding="utf-8") as f:
            ban_do = json.load(f)
    except (json.JSONDecodeError, UnicodeDecodeError):
        raise ValueError("File không đúng định dạng JSON.")
    loi = kiem_tra(ban_do)
    if loi:
        raise ValueError(loi[0])
    return ban_do


def ghi_ban_do(ban_do, duong_dan):
    loi = kiem_tra(ban_do)
    if loi:
        raise ValueError(loi[0])
    # mỗi hàng của lưới ghi trên một dòng cho dễ đọc
    dong = ",\n".join("    [" + ", ".join(f"{o:2d}" for o in hang) + "]" for hang in ban_do["cells"])
    noi_dung = (
        "{\n"
        f'  "rows": {ban_do["rows"]},\n'
        f'  "cols": {ban_do["cols"]},\n'
        f'  "start": [{ban_do["start"][0]}, {ban_do["start"][1]}],\n'
        f'  "k": {ban_do["k"]},\n'
        f'  "p": {ban_do["p"]},\n'
        f'  "cells": [\n{dong}\n  ]\n'
        "}\n"
    )
    with open(duong_dan, "w", encoding="utf-8") as f:
        f.write(noi_dung)


MAU_O = {
    KHOE: (196, 224, 168),
    1: (247, 214, 112),
    2: (238, 150, 72),
    3: (196, 62, 52),
    VAT_CAN: (92, 92, 88),
    TRAM: (58, 118, 196),
}
TEN_O = {
    KHOE: "Lúa khỏe",
    1: "Bệnh mức 1",
    2: "Bệnh mức 2",
    3: "Bệnh mức 3",
    VAT_CAN: "Vật cản",
    TRAM: "Trạm nạp",
}
VUNG_LUOI = pygame.Rect(20, CAO_THANH_TIEU_DE + 16, 600, 600)
X_BANG = 650
X_COT2 = 900
XUAT_PHAT = "xuat_phat"
CONG_CU = [KHOE, 1, 2, 3, VAT_CAN, TRAM, XUAT_PHAT]
MAU_LOI = (176, 48, 40)
GIOI_HAN = {"k": 50, "p": 500}
THU_MUC_MAU = Path(__file__).resolve().parents[2] / "data" / "sample" / "maps"


def hoi_duong_dan(luu):
    """Hộp thoại chọn file, hủy thì trả None"""
    import tkinter
    from tkinter import filedialog

    goc = tkinter.Tk()
    goc.withdraw()
    goc.attributes("-topmost", True)
    kieu = [("Bản đồ JSON", "*.json")]
    if luu:
        duong_dan = filedialog.asksaveasfilename(defaultextension=".json", filetypes=kieu,
                                                 initialdir=THU_MUC_MAU, initialfile="ban_do.json")
    else:
        duong_dan = filedialog.askopenfilename(filetypes=kieu, initialdir=THU_MUC_MAU)
    goc.destroy()
    return duong_dan or None


class ManHinhBanDo(ManHinh):
    def __init__(self, ung_dung, ban_do=None):
        super().__init__(ung_dung)
        self.ban_do = ban_do or tao_ban_do()
        self.nut_quay_lai = Nut("← Quay lại", (20, 20, 150, 44), ung_dung.ve_man_hinh_chinh)
        self.dang_to = None  # loại ô đang tô khi giữ chuột
        self.nut_cong_cu = {}
        y = CAO_THANH_TIEU_DE + 56
        for ma in CONG_CU:
            ten = "Điểm xuất phát" if ma == XUAT_PHAT else TEN_O[ma]
            self.nut_cong_cu[ma] = Nut(ten, (X_BANG + 40, y, 200, 32),
                                       lambda m=ma: self.chon_cong_cu(m), co=18)
            y += 40
        self.chon_cong_cu(1)

        y = CAO_THANH_TIEU_DE + 56
        self.nut_tep = [
            Nut("Mở file…", (X_COT2, y, 180, 32), lambda: self.mo_file(hoi_duong_dan(False)), co=18),
            Nut("Lưu file…", (X_COT2, y + 40, 180, 32), lambda: self.luu_file(hoi_duong_dan(True)), co=18),
            Nut("Bản đồ ngẫu nhiên", (X_COT2, y + 80, 180, 32), self.ngau_nhien, co=18),
            Nut("Xóa hết", (X_COT2, y + 120, 180, 32), self.xoa_het, co=18),
        ]
        y_ts = CAO_THANH_TIEU_DE + 256
        for i, (khoa, buoc) in enumerate((("k", 1), ("p", 5))):
            yy = y_ts + i * 40
            self.nut_tep += [
                Nut("−", (X_COT2 + 108, yy, 32, 32), lambda k=khoa, b=buoc: self.chinh(k, -b), co=20),
                Nut("+", (X_COT2 + 148, yy, 32, 32), lambda k=khoa, b=buoc: self.chinh(k, b), co=20),
            ]
        self.nut_tep.append(Nut("Lập lộ trình", (X_COT2, y_ts + 90, 180, 40), self.lap_lo_trinh, co=20))
        self.thong_bao, self.la_loi = "", False

    def lap_lo_trinh(self):
        """Bấm nút Lập lộ trình: kiểm tra rồi mở màn hình E3"""
        from .route_view import ManHinhLoTrinh, dem_o_benh

        danh_sach_loi = kiem_tra(self.ban_do)
        if len(danh_sach_loi) > 0:
            self.bao(f"Bản đồ chưa hợp lệ:\n{danh_sach_loi[0]}", loi=True)
            return

        if dem_o_benh(self.ban_do) == 0:
            self.bao("Chưa có ô bệnh nào để phun.", loi=True)
            return

        self.bao("")
        # chép bản đồ để màn hình lộ trình không sửa bản gốc
        ban_sao = json.loads(json.dumps(self.ban_do))
        man_hinh_moi = ManHinhLoTrinh(self.ung_dung, ban_sao, self)
        self.ung_dung.chuyen_den(man_hinh_moi)

    def ngau_nhien(self):
        bd = self.ban_do
        self.ban_do = tao_ngau_nhien(bd["rows"], bd["cols"], bd["k"], bd["p"])
        self.bao("Đã tạo bản đồ ngẫu nhiên")

    def xoa_het(self):
        bd = self.ban_do
        self.ban_do = tao_ban_do(bd["rows"], bd["cols"], bd["k"], bd["p"])
        self.bao("Đã xóa hết")

    def chinh(self, khoa, buoc):
        self.ban_do[khoa] = min(GIOI_HAN[khoa], max(1, self.ban_do[khoa] + buoc))

    def bao(self, noi_dung, loi=False):
        self.thong_bao, self.la_loi = noi_dung, loi

    def mo_file(self, duong_dan):
        if not duong_dan:
            return
        try:
            self.ban_do = doc_ban_do(duong_dan)
            self.bao(f"Đã mở {Path(duong_dan).name}")
        except (OSError, ValueError) as e:
            self.bao(f"Không mở được:\n{e}", loi=True)

    def luu_file(self, duong_dan):
        if not duong_dan:
            return
        try:
            ghi_ban_do(self.ban_do, duong_dan)
            self.bao(f"Đã lưu {Path(duong_dan).name}")
        except (OSError, ValueError) as e:
            self.bao(f"Không lưu được:\n{e}", loi=True)

    def chon_cong_cu(self, ma):
        self.cong_cu = ma
        for m, nut in self.nut_cong_cu.items():
            nut.chon = m == ma

    def o_tai(self, vi_tri):
        co = self.co_o()
        r = (vi_tri[1] - VUNG_LUOI.y) // co
        c = (vi_tri[0] - VUNG_LUOI.x) // co
        if 0 <= r < self.ban_do["rows"] and 0 <= c < self.ban_do["cols"]:
            return r, c
        return None

    def to_o(self, r, c, ma):
        cells = self.ban_do["cells"]
        if ma == XUAT_PHAT:
            if cells[r][c] == VAT_CAN:
                cells[r][c] = KHOE
            self.ban_do["start"] = [r, c]
        elif ma == VAT_CAN and [r, c] == list(self.ban_do["start"]):
            return  # không đặt vật cản lên điểm xuất phát
        else:
            cells[r][c] = ma

    def co_o(self):
        return min(VUNG_LUOI.w // self.ban_do["cols"], VUNG_LUOI.h // self.ban_do["rows"])

    def khung_o(self, r, c):
        co = self.co_o()
        return pygame.Rect(VUNG_LUOI.x + c * co, VUNG_LUOI.y + r * co, co, co)

    def xu_ly_su_kien(self, su_kien):
        if su_kien.type == pygame.KEYDOWN and su_kien.key == pygame.K_ESCAPE:
            self.ung_dung.ve_man_hinh_chinh()
            return
        if self.nut_quay_lai.xu_ly(su_kien):
            return
        if any(nut.xu_ly(su_kien) for nut in self.nut_cong_cu.values()):
            return
        if any(nut.xu_ly(su_kien) for nut in self.nut_tep):
            self.dang_to = None
            return

        # chuột trái: tô, chuột phải: xóa
        if su_kien.type == pygame.MOUSEBUTTONDOWN and su_kien.button in (1, 3):
            o = self.o_tai(su_kien.pos)
            if o:
                self.dang_to = KHOE if su_kien.button == 3 else self.cong_cu
                self.to_o(*o, self.dang_to)
                if self.dang_to == XUAT_PHAT:
                    self.dang_to = None
        elif su_kien.type == pygame.MOUSEMOTION and self.dang_to is not None:
            o = self.o_tai(su_kien.pos)
            if o:
                self.to_o(*o, self.dang_to)
        elif su_kien.type == pygame.MOUSEBUTTONUP:
            self.dang_to = None

    def ve_luoi(self, be_mat):
        for r, hang in enumerate(self.ban_do["cells"]):
            for c, o in enumerate(hang):
                khung = self.khung_o(r, c)
                pygame.draw.rect(be_mat, MAU_O[o], khung)
                pygame.draw.rect(be_mat, MAU["nen"], khung, width=1)
                if o == TRAM:
                    ve_chu(be_mat, "T", khung.center, co=khung.h - 8, mau=MAU["nut"], dam=True, can="center")
        r, c = self.ban_do["start"]
        pygame.draw.circle(be_mat, MAU["chu"], self.khung_o(r, c).center, self.co_o() // 2 - 2, width=3)

    def ve_bang(self, be_mat):
        ve_chu(be_mat, "Công cụ", (X_BANG, CAO_THANH_TIEU_DE + 16), co=22, dam=True)
        for ma, nut in self.nut_cong_cu.items():
            y = nut.khung.y + 3
            if ma == XUAT_PHAT:
                pygame.draw.circle(be_mat, MAU["chu"], (X_BANG + 13, y + 13), 11, width=3)
            else:
                pygame.draw.rect(be_mat, MAU_O[ma], (X_BANG, y, 26, 26), border_radius=4)
            nut.ve(be_mat)

        cells = self.ban_do["cells"]
        so_benh = sum(o in MUC_BENH for hang in cells for o in hang)
        so_tram = sum(o == TRAM for hang in cells for o in hang)
        y = CAO_THANH_TIEU_DE + 356
        ve_chu(be_mat, f"Lưới {self.ban_do['rows']} x {self.ban_do['cols']}", (X_BANG, y), co=19)
        ve_chu(be_mat, f"Ô bệnh: {so_benh}   Trạm: {so_tram}", (X_BANG, y + 30), co=19)
        ve_chu(be_mat, "Chuột trái: tô · Chuột phải: xóa", (X_BANG, y + 70), co=17, mau=MAU["chu_phu"])

        ve_chu(be_mat, "Tệp", (X_COT2, CAO_THANH_TIEU_DE + 16), co=22, dam=True)
        ve_chu(be_mat, "Drone", (X_COT2, CAO_THANH_TIEU_DE + 216), co=22, dam=True)
        y_ts = CAO_THANH_TIEU_DE + 256
        ve_chu(be_mat, f"Thuốc k: {self.ban_do['k']}", (X_COT2, y_ts + 16), co=18, can="midleft")
        ve_chu(be_mat, f"Pin p: {self.ban_do['p']}", (X_COT2, y_ts + 56), co=18, can="midleft")
        for nut in self.nut_tep:
            nut.ve(be_mat)
        for i, dong in enumerate(self.thong_bao.split("\n")):
            ve_chu(be_mat, dong, (X_BANG, y + 120 + i * 26), co=18,
                   mau=MAU_LOI if self.la_loi else MAU["nhan"])

    def ve(self, be_mat):
        ve_thanh_tieu_de(be_mat, "Bản đồ ruộng")
        self.nut_quay_lai.ve(be_mat)
        self.ve_luoi(be_mat)
        self.ve_bang(be_mat)
