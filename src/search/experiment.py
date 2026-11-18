"""So sánh A* toàn cục và tham lam trên cùng bản đồ/ngân sách."""

import json
import sys
from pathlib import Path

from src.contracts import BanDo, LoTrinh
from src.search.full_astar import astar_route
from src.search.greedy import greedy_route


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


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    run_experiment()
