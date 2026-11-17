"""E2 - Bản đồ lưới đánh dấu ô bệnh - TV5"""
import json

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
