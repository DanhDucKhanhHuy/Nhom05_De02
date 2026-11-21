"""So sánh A* toàn cục, leo đồi và tham lam trên cùng bản đồ/ngân sách."""

import json
import random
import sys
from pathlib import Path

from src.contracts import BanDo, LoTrinh
from src.search.Astar import astar_route
from src.search.greedy import greedy_route
from src.search.Hill_Climbing import hill_climbing_route


def run_experiment(
    ban_do: BanDo | None = None,
    k: int | None = None,
    p: int | None = None,
) -> dict[str, LoTrinh]:
    """Chạy hai chiến lược cùng ngân sách, in và trả về các chỉ số."""
    if ban_do is None:
        map_path = Path(__file__).resolve().parents[2] / "data" / "sample" / "maps" / "map_4x4.json"
        with map_path.open(encoding="utf-8") as file:
            ban_do = json.load(file)

    k = ban_do["k"] if k is None else k
    p = ban_do["p"] if p is None else p
    ket_qua = {
        "A* toàn cục": astar_route(ban_do, k, p),
        "Leo đồi": hill_climbing_route(ban_do, k, p),
        "Tham lam gần nhất": greedy_route(ban_do, k, p),
    }

    print(
        f"Bản đồ đầu vào: {ban_do['rows']}x{ban_do['cols']}, "
        f"start={tuple(ban_do['start'])}, k={k}, p={p}"
    )
    print("Mã ô: -1=vật cản, 0=lúa khỏe, 1-3=ô bệnh, 9=trạm")
    print("Ma trận cells:")
    for hang in ban_do["cells"]:
        print(" ".join(f"{o:>2}" for o in hang))
    print(f"{'Chiến lược':<24} {'Quãng đường':>12} {'Lần về trạm':>12} {'Thời gian (s)':>15}")
    for ten, lo_trinh in ket_qua.items():
        print(
            f"{ten:<24} {lo_trinh['tong_quang_duong']:>12} "
            f"{lo_trinh['so_lan_ve_tram']:>12} {lo_trinh['thoi_gian_chay']:>15.6f}"
        )
    for ten, lo_trinh in ket_qua.items():
        print(f"\n{ten} — đường bay:")
        print(" -> ".join(str(vt) for vt in lo_trinh["duong_di"]))
        print("Sự kiện:")
        if lo_trinh["su_kien"]:
            for sk in lo_trinh["su_kien"]:
                ghi_chu = ""
                if sk["loai"] == "bay":
                    ghi_chu = f" (pin -{sk['pin_tieu_hao']}; quãng đường {sk['quang_duong']})"
                    if sk["qua_vat_can"]:
                        ghi_chu += f" (vượt vật cản {sk['qua_vat_can']})"
                print(f"  {sk['loai']} tại {sk['vi_tri']}{ghi_chu}")
        else:
            print("  Không có hành động.")
    return ket_qua


def tao_ban_do_ngau_nhien(so_hang, so_cot, so_o_benh, so_vat_can, k, p, hat_giong):
    """Bản đồ ngẫu nhiên: trạm ở góc (0, 0), ô bệnh mức 1–3, vật cản"""
    ngau_nhien = random.Random(hat_giong)
    cells = []
    for _ in range(so_hang):
        cells.append([0] * so_cot)
    cells[0][0] = 9

    cac_o_trong = []
    for hang in range(so_hang):
        for cot in range(so_cot):
            if (hang, cot) != (0, 0):
                cac_o_trong.append((hang, cot))
    ngau_nhien.shuffle(cac_o_trong)

    for i in range(so_o_benh):
        hang, cot = cac_o_trong[i]
        cells[hang][cot] = ngau_nhien.randint(1, 3)
    for i in range(so_o_benh, so_o_benh + so_vat_can):
        hang, cot = cac_o_trong[i]
        cells[hang][cot] = -1

    return {"rows": so_hang, "cols": so_cot, "start": [0, 0], "k": k, "p": p, "cells": cells}


def so_sanh_leo_doi_tham_lam(so_ban_do=10, so_hang=20, so_cot=20, so_o_benh=15,
                             so_vat_can=40, k=5, p=80):
    """So sánh leo đồi và tham lam trên nhiều bản đồ ngẫu nhiên 20 × 20"""
    print(f"\nSo sánh leo đồi và tham lam: {so_ban_do} bản đồ {so_hang}x{so_cot}, "
          f"{so_o_benh} ô bệnh, {so_vat_can} vật cản, k={k}, p={p}")
    print(f"{'Bản đồ':<8} {'Tham lam':>10} {'Leo đồi':>10} {'Giảm':>8} "
          f"{'Về trạm TL':>11} {'Về trạm LĐ':>11} {'TG TL (s)':>10} {'TG LĐ (s)':>10}")

    cac_dong = []
    for hat_giong in range(so_ban_do):
        ban_do = tao_ban_do_ngau_nhien(so_hang, so_cot, so_o_benh, so_vat_can, k, p, hat_giong)
        try:
            tham_lam = greedy_route(ban_do, k, p)
            leo_doi = hill_climbing_route(ban_do, k, p)
        except ValueError:
            print(f"{hat_giong:<8} bỏ qua: bản đồ không khả thi")
            continue

        giam = tham_lam["tong_quang_duong"] - leo_doi["tong_quang_duong"]
        cac_dong.append((tham_lam, leo_doi))
        print(f"{hat_giong:<8} {tham_lam['tong_quang_duong']:>10} {leo_doi['tong_quang_duong']:>10} "
              f"{giam:>8} {tham_lam['so_lan_ve_tram']:>11} {leo_doi['so_lan_ve_tram']:>11} "
              f"{tham_lam['thoi_gian_chay']:>10.3f} {leo_doi['thoi_gian_chay']:>10.3f}")

    if len(cac_dong) == 0:
        return cac_dong

    tong_tl = 0
    tong_ld = 0
    tg_tl = 0
    tg_ld = 0
    so_lan_tot_hon = 0
    for tham_lam, leo_doi in cac_dong:
        tong_tl = tong_tl + tham_lam["tong_quang_duong"]
        tong_ld = tong_ld + leo_doi["tong_quang_duong"]
        tg_tl = tg_tl + tham_lam["thoi_gian_chay"]
        tg_ld = tg_ld + leo_doi["thoi_gian_chay"]
        if leo_doi["tong_quang_duong"] < tham_lam["tong_quang_duong"]:
            so_lan_tot_hon = so_lan_tot_hon + 1

    n = len(cac_dong)
    print(f"Trung bình quãng đường: tham lam {tong_tl / n:.1f}, leo đồi {tong_ld / n:.1f} "
          f"(giảm {(tong_tl - tong_ld) / tong_tl * 100:.1f}%)")
    print(f"Trung bình thời gian: tham lam {tg_tl / n:.3f} s, leo đồi {tg_ld / n:.3f} s")
    print(f"Leo đồi ngắn hơn tham lam ở {so_lan_tot_hon}/{n} bản đồ, không bản đồ nào dài hơn "
          f"(vì leo đồi xuất phát từ lời giải tham lam).")
    return cac_dong


def so_sanh_astar_tham_lam(so_ban_do=10, so_hang=10, so_cot=10, so_o_benh=6,
                           so_vat_can=15, k=5, p=80):
    """So sánh A* toàn cục và tham lam trên nhiều bản đồ ngẫu nhiên.

    Bản đồ nhỏ hơn phần leo đồi vì không gian trạng thái của A* tăng theo
    2^(số ô bệnh); quá ~8 ô bệnh thì mỗi bản đồ mất hàng chục giây trở lên.
    """
    print(f"\nSo sánh A* và tham lam: {so_ban_do} bản đồ {so_hang}x{so_cot}, "
          f"{so_o_benh} ô bệnh, {so_vat_can} vật cản, k={k}, p={p}")
    print(f"{'Bản đồ':<8} {'Tham lam':>10} {'A*':>10} {'Giảm':>8} "
          f"{'Về trạm TL':>11} {'Về trạm A*':>11} {'TG TL (s)':>10} {'TG A* (s)':>10}")

    cac_dong = []
    for hat_giong in range(so_ban_do):
        ban_do = tao_ban_do_ngau_nhien(so_hang, so_cot, so_o_benh, so_vat_can, k, p, hat_giong)
        try:
            tham_lam = greedy_route(ban_do, k, p)
            a_sao = astar_route(ban_do, k, p)
        except ValueError:
            print(f"{hat_giong:<8} bỏ qua: bản đồ không khả thi")
            continue

        giam = tham_lam["tong_quang_duong"] - a_sao["tong_quang_duong"]
        cac_dong.append((tham_lam, a_sao))
        print(f"{hat_giong:<8} {tham_lam['tong_quang_duong']:>10} {a_sao['tong_quang_duong']:>10} "
              f"{giam:>8} {tham_lam['so_lan_ve_tram']:>11} {a_sao['so_lan_ve_tram']:>11} "
              f"{tham_lam['thoi_gian_chay']:>10.3f} {a_sao['thoi_gian_chay']:>10.3f}")

    if len(cac_dong) == 0:
        return cac_dong

    tong_tl = 0
    tong_as = 0
    tg_tl = 0
    tg_as = 0
    so_lan_tot_hon = 0
    for tham_lam, a_sao in cac_dong:
        tong_tl = tong_tl + tham_lam["tong_quang_duong"]
        tong_as = tong_as + a_sao["tong_quang_duong"]
        tg_tl = tg_tl + tham_lam["thoi_gian_chay"]
        tg_as = tg_as + a_sao["thoi_gian_chay"]
        if a_sao["tong_quang_duong"] < tham_lam["tong_quang_duong"]:
            so_lan_tot_hon = so_lan_tot_hon + 1

    n = len(cac_dong)
    print(f"Trung bình quãng đường: tham lam {tong_tl / n:.1f}, A* {tong_as / n:.1f} "
          f"(giảm {(tong_tl - tong_as) / tong_tl * 100:.1f}%)")
    print(f"Trung bình thời gian: tham lam {tg_tl / n:.3f} s, A* {tg_as / n:.3f} s "
          f"(chậm hơn {tg_as / max(tg_tl, 1e-9):.0f} lần)")
    print(f"A* ngắn hơn tham lam ở {so_lan_tot_hon}/{n} bản đồ, không bản đồ nào dài hơn "
          f"(vì A* với heuristic chấp nhận được cho lời giải tối ưu).")
    return cac_dong


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    run_experiment()
    so_sanh_leo_doi_tham_lam()
    so_sanh_astar_tham_lam()
