from time import perf_counter

from src.contracts import BanDo, LoTrinh, ThuatToan
from src.drone import ActionType, DroneState
from src.search.greedy import greedy_route
from src.search.route_utils import di_theo_duong, tao_bai_toan, tao_lo_trinh

SO_VONG_TOI_DA = 200
VO_CUC = float("inf")


def optimize_order(ban_do: BanDo, k: int, p: int, thuat_toan: ThuatToan) -> LoTrinh:
    """Chọn thứ tự ghé ô bệnh; hiện chỉ có leo đồi."""
    if thuat_toan != "hill":
        raise ValueError("order_opt chỉ hỗ trợ thuật toán 'hill'.")
    return hill_climbing_route(ban_do, k, p)


def hill_climbing_route(ban_do: BanDo, k: int, p: int) -> LoTrinh:
    """Leo đồi trên thứ tự ghé ô bệnh, xuất phát từ thứ tự của tham lam."""
    bat_dau = perf_counter()
    bai_toan = tao_bai_toan(ban_do, k, p)
    bo_nho = {}

    thu_tu = thu_tu_tu_tham_lam(ban_do, k, p)
    gia_tri = danh_gia(bai_toan, thu_tu, bo_nho)
    if gia_tri == VO_CUC:
        raise ValueError("Không tìm thấy lộ trình hoàn tất với ngân sách thuốc/pin này.")

    so_vong = 0
    while so_vong < SO_VONG_TOI_DA:
        so_vong = so_vong + 1
        thu_tu_tot_nhat = None
        gia_tri_tot_nhat = gia_tri

        # xét mọi láng giềng: đổi chỗ ô i và ô j
        for i in range(len(thu_tu)):
            for j in range(i + 1, len(thu_tu)):
                lang_gieng = list(thu_tu)
                lang_gieng[i] = thu_tu[j]
                lang_gieng[j] = thu_tu[i]
                gia_tri_moi = danh_gia(bai_toan, lang_gieng, bo_nho)
                if gia_tri_moi < gia_tri_tot_nhat:
                    thu_tu_tot_nhat = lang_gieng
                    gia_tri_tot_nhat = gia_tri_moi

        if thu_tu_tot_nhat is None:
            break  # cực tiểu cục bộ
        thu_tu = thu_tu_tot_nhat
        gia_tri = gia_tri_tot_nhat

    cac_buoc = bay_theo_thu_tu(bai_toan, thu_tu)
    return tao_lo_trinh(bai_toan, cac_buoc, bat_dau)


def thu_tu_tu_tham_lam(ban_do, k, p):
    """Thứ tự các ô được phun trong lời giải tham lam"""
    lo_trinh = greedy_route(ban_do, k, p)
    thu_tu = []
    for su_kien in lo_trinh["su_kien"]:
        if su_kien["loai"] == "phun":
            thu_tu.append(tuple(su_kien["vi_tri"]))
    return thu_tu


def chang_bay(bai_toan, vi_tri, pin, dich, bo_nho):
    """Bay từ vi_tri tới dich với lượng pin đang có.

    Trả (quãng đường, pin tiêu hao), hoặc None nếu không bay an toàn được.
    Lưu kết quả vào bo_nho vì leo đồi hỏi lại cùng chặng rất nhiều lần.
    """
    khoa = (vi_tri, pin, dich)
    if khoa in bo_nho:
        return bo_nho[khoa]

    ket_qua = None
    if vi_tri == dich:
        ket_qua = (0, 0)
    else:
        trang_thai = DroneState(position=vi_tri, medicine=0, battery=pin, untreated=frozenset())
        if bai_toan.path_to(trang_thai, dich) is not None:
            _, cac_buoc = di_theo_duong(bai_toan, trang_thai, dich)
            quang_duong = 0
            pin_ton = 0
            for buoc in cac_buoc:
                quang_duong = quang_duong + buoc.cost
                pin_ton = pin_ton + buoc.battery_cost
            ket_qua = (quang_duong, pin_ton)

    bo_nho[khoa] = ket_qua
    return ket_qua


def chon_tram_nap(bai_toan, vi_tri, pin, o_tiep_theo, bo_nho):
    """Trạm gần nhất bay tới được, và từ đó (pin đầy) bay tới được ô tiếp theo"""
    tram_tot_nhat = None
    quang_duong_tot_nhat = VO_CUC
    for tram in sorted(bai_toan.stations):
        ve_tram = chang_bay(bai_toan, vi_tri, pin, tram, bo_nho)
        if ve_tram is None:
            continue
        di_tiep = chang_bay(bai_toan, tram, bai_toan.battery_capacity, o_tiep_theo, bo_nho)
        if di_tiep is None:
            continue
        if ve_tram[0] < quang_duong_tot_nhat:
            tram_tot_nhat = tram
            quang_duong_tot_nhat = ve_tram[0]
    return tram_tot_nhat


def chon_tram_cuoi(bai_toan, vi_tri, pin, bo_nho):
    """Trạm gần nhất bay về được khi đã phun xong"""
    tram_tot_nhat = None
    quang_duong_tot_nhat = VO_CUC
    for tram in sorted(bai_toan.stations):
        ve_tram = chang_bay(bai_toan, vi_tri, pin, tram, bo_nho)
        if ve_tram is None:
            continue
        if ve_tram[0] < quang_duong_tot_nhat:
            tram_tot_nhat = tram
            quang_duong_tot_nhat = ve_tram[0]
    return tram_tot_nhat


def danh_gia(bai_toan, thu_tu, bo_nho):
    """Tổng quãng đường khi bay theo thu_tu; VO_CUC nếu không bay hết được"""
    vi_tri = bai_toan.start
    thuoc = bai_toan.capacity
    pin = bai_toan.battery_capacity
    tong = 0

    for o_benh in thu_tu:
        chang = None
        if thuoc > 0:
            chang = chang_bay(bai_toan, vi_tri, pin, o_benh, bo_nho)

        if chang is None:
            # về trạm nạp rồi mới bay tới ô bệnh
            tram = chon_tram_nap(bai_toan, vi_tri, pin, o_benh, bo_nho)
            if tram is None:
                return VO_CUC
            ve_tram = chang_bay(bai_toan, vi_tri, pin, tram, bo_nho)
            tong = tong + ve_tram[0]
            vi_tri = tram
            thuoc = bai_toan.capacity
            pin = bai_toan.battery_capacity
            chang = chang_bay(bai_toan, vi_tri, pin, o_benh, bo_nho)

        tong = tong + chang[0]
        pin = pin - chang[1]
        vi_tri = o_benh
        thuoc = thuoc - 1

    tram = chon_tram_cuoi(bai_toan, vi_tri, pin, bo_nho)
    if tram is None:
        return VO_CUC
    tong = tong + chang_bay(bai_toan, vi_tri, pin, tram, bo_nho)[0]
    return tong


def tim_hanh_dong(bai_toan, trang_thai, loai):
    """Lấy toán tử phun hoặc nạp hợp lệ ở trạng thái hiện tại"""
    for buoc in bai_toan.successors(trang_thai):
        if buoc.action.kind is loai:
            return buoc
    return None


def bay_theo_thu_tu(bai_toan, thu_tu):
    """Dựng các bước thật (bay, phun, nạp) theo thứ tự đã chọn"""
    bo_nho = {}
    trang_thai = bai_toan.initial_state
    cac_buoc = []

    for o_benh in thu_tu:
        toi_thang = False
        if trang_thai.medicine > 0:
            if bai_toan.path_to(trang_thai, o_benh) is not None:
                toi_thang = True

        if not toi_thang:
            tram = chon_tram_nap(bai_toan, trang_thai.position, trang_thai.battery, o_benh, bo_nho)
            trang_thai, bay_ve = di_theo_duong(bai_toan, trang_thai, tram)
            cac_buoc.extend(bay_ve)
            nap = tim_hanh_dong(bai_toan, trang_thai, ActionType.REFILL)
            if nap is not None:
                cac_buoc.append(nap)
                trang_thai = nap.state

        trang_thai, bay_den = di_theo_duong(bai_toan, trang_thai, o_benh)
        cac_buoc.extend(bay_den)
        phun = tim_hanh_dong(bai_toan, trang_thai, ActionType.SPRAY)
        cac_buoc.append(phun)
        trang_thai = phun.state

    tram = chon_tram_cuoi(bai_toan, trang_thai.position, trang_thai.battery, bo_nho)
    trang_thai, bay_ve = di_theo_duong(bai_toan, trang_thai, tram)
    cac_buoc.extend(bay_ve)
    return cac_buoc
