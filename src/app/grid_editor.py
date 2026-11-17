"""E2 - Bản đồ lưới đánh dấu ô bệnh - TV5"""
import json

import pygame

from .giao_dien import CAO_THANH_TIEU_DE, MAU, ManHinh, Nut, ve_chu, ve_thanh_tieu_de

# mã ô theo README
KHOE, VAT_CAN, TRAM = 0, -1, 9
MUC_BENH = (1, 2, 3)
MA_HOP_LE = (KHOE, VAT_CAN, TRAM) + MUC_BENH


def tao_ban_do(so_hang=20, so_cot=20, k=8, p=60):
    cells = [[KHOE] * so_cot for _ in range(so_hang)]
    cells[0][0] = TRAM
    return {"rows": so_hang, "cols": so_cot, "start": [0, 0], "k": k, "p": p, "cells": cells}


def kiem_tra(ban_do):
    """Trả về danh sách lỗi"""
    loi = []
    cells = ban_do.get("cells") or []
    so_hang, so_cot = len(cells), len(cells[0]) if cells else 0
    if so_hang == 0 or any(len(dong) != so_cot for dong in cells):
        return ["Lưới rỗng hoặc các dòng không cùng số cột."]
    if ban_do.get("rows") != so_hang or ban_do.get("cols") != so_cot:
        loi.append("rows/cols không khớp với cells.")
    if any(o not in MA_HOP_LE for dong in cells for o in dong):
        loi.append("Có mã ô không hợp lệ.")
    r, c = ban_do.get("start", [-1, -1])
    if not (0 <= r < so_hang and 0 <= c < so_cot) or cells[r][c] == VAT_CAN:
        loi.append("Điểm xuất phát nằm ngoài lưới hoặc trên vật cản.")
    if not any(o == TRAM for dong in cells for o in dong):
        loi.append("Chưa có trạm nạp thuốc.")
    return loi


def doc_ban_do(duong_dan):
    with open(duong_dan, encoding="utf-8") as f:
        ban_do = json.load(f)
    loi = kiem_tra(ban_do)
    if loi:
        raise ValueError(loi[0])
    return ban_do


def ghi_ban_do(ban_do, duong_dan):
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


class ManHinhBanDo(ManHinh):
    def __init__(self, ung_dung, ban_do=None):
        super().__init__(ung_dung)
        self.ban_do = ban_do or tao_ban_do()
        self.nut_quay_lai = Nut("← Quay lại", (20, 20, 150, 44), ung_dung.ve_man_hinh_chinh)

    def co_o(self):
        return min(VUNG_LUOI.w // self.ban_do["cols"], VUNG_LUOI.h // self.ban_do["rows"])

    def khung_o(self, r, c):
        co = self.co_o()
        return pygame.Rect(VUNG_LUOI.x + c * co, VUNG_LUOI.y + r * co, co, co)

    def xu_ly_su_kien(self, su_kien):
        if su_kien.type == pygame.KEYDOWN and su_kien.key == pygame.K_ESCAPE:
            self.ung_dung.ve_man_hinh_chinh()
        else:
            self.nut_quay_lai.xu_ly(su_kien)

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
        y = CAO_THANH_TIEU_DE + 16
        ve_chu(be_mat, "Chú thích", (X_BANG, y), co=22, dam=True)
        y += 40
        for ma in (KHOE, 1, 2, 3, VAT_CAN, TRAM):
            pygame.draw.rect(be_mat, MAU_O[ma], (X_BANG, y, 26, 26), border_radius=4)
            ve_chu(be_mat, TEN_O[ma], (X_BANG + 38, y + 13), co=19, can="midleft")
            y += 36
        pygame.draw.circle(be_mat, MAU["chu"], (X_BANG + 13, y + 13), 11, width=3)
        ve_chu(be_mat, "Điểm xuất phát", (X_BANG + 38, y + 13), co=19, can="midleft")

        cells = self.ban_do["cells"]
        so_benh = sum(o in MUC_BENH for hang in cells for o in hang)
        so_tram = sum(o == TRAM for hang in cells for o in hang)
        y += 60
        ve_chu(be_mat, f"Lưới {self.ban_do['rows']} x {self.ban_do['cols']}", (X_BANG, y), co=19)
        ve_chu(be_mat, f"Ô bệnh: {so_benh}   Trạm: {so_tram}", (X_BANG, y + 30), co=19)

    def ve(self, be_mat):
        ve_thanh_tieu_de(be_mat, "Bản đồ ruộng")
        self.nut_quay_lai.ve(be_mat)
        self.ve_luoi(be_mat)
        self.ve_bang(be_mat)
