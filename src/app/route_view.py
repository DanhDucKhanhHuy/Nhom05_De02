"""E3 - Hoạt cảnh lộ trình drone - TV5"""
import multiprocessing
import queue
import time

import pygame

from .giao_dien import CAO_THANH_TIEU_DE, MAU, ManHinh, Nut, ve_chu, ve_thanh_tieu_de
from .grid_editor import KHOE, MAU_LOI, MAU_O, MUC_BENH, TRAM, VUNG_LUOI, X_BANG

TEN_THUAT_TOAN = {"greedy": "Tham lam", "astar": "A* toàn cục"}
SO_O_ASTAR_NHANH = 8  # trên mức này A* có thể chạy rất lâu


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
    from src.search.Astar import astar_route
    from src.search.greedy import greedy_route

    k = ban_do["k"]
    p = ban_do["p"]

    if thuat_toan == "astar":
        lo_trinh = astar_route(ban_do, k, p)
    else:
        lo_trinh = greedy_route(ban_do, k, p)
    return lo_trinh


def tinh_o_tien_trinh_rieng(ban_do, thuat_toan, hang_doi):
    """Chạy trong tiến trình riêng, gửi kết quả về qua hàng đợi"""
    try:
        lo_trinh = lap_lo_trinh(ban_do, thuat_toan)
        hang_doi.put(("ok", lo_trinh))
    except ValueError as loi:
        hang_doi.put(("loi", str(loi)))
    except MemoryError:
        hang_doi.put(("loi", "Hết bộ nhớ khi tính lộ trình."))


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


def mo_ta_su_kien(su_kien):
    if su_kien is None:
        return "Sẵn sàng xuất phát"

    r, c = su_kien["vi_tri"]
    if su_kien["loai"] == "phun":
        return f"Phun thuốc ô ({r}, {c})"
    if su_kien["loai"] == "nap":
        return f"Nạp thuốc và pin tại trạm ({r}, {c})"
    if su_kien.get("qua_vat_can"):
        return f"Bay qua vật cản tới ({r}, {c})"
    return f"Bay tới ({r}, {c})"


MAU_DA_PHUN = (128, 186, 214)
MAU_VET = (40, 84, 150)
MAU_DRONE = (24, 32, 40)
TOC_DO = (1, 2, 5, 10, 20, 40)  # bước/giây
Y_DIEU_KHIEN = CAO_THANH_TIEU_DE + 300


class ManHinhLoTrinh(ManHinh):
    def __init__(self, ung_dung, ban_do, man_hinh_truoc=None, thuat_toan="greedy"):
        super().__init__(ung_dung)
        self.ban_do = ban_do
        self.man_hinh_truoc = man_hinh_truoc
        self.muc_toc_do = 3
        self.tien_trinh = None
        self.hang_doi = None
        self.tao_cac_nut()
        self.bat_dau_tinh(thuat_toan)

    def tao_cac_nut(self):
        y = Y_DIEU_KHIEN
        self.nut_quay_lai = Nut("← Bản đồ", (20, 20, 150, 44), self.quay_lai)

        self.nut_chay = Nut("Chạy", (X_BANG, y, 136, 36), self.chay_dung)
        nut_tung_buoc = Nut("Từng bước", (X_BANG + 146, y, 136, 36), self.buoc_toi)
        nut_ve_dau = Nut("Về đầu", (X_BANG + 292, y, 136, 36), self.ve_dau)
        nut_cham = Nut("−", (X_BANG + 250, y + 48, 32, 32), self.cham_lai)
        nut_nhanh = Nut("+", (X_BANG + 396, y + 48, 32, 32), self.nhanh_len)
        self.nut_dieu_khien = [self.nut_chay, nut_tung_buoc, nut_ve_dau, nut_cham, nut_nhanh]

        nut_tham_lam = Nut("Tham lam", (X_BANG + 110, y + 92, 150, 32), self.chon_tham_lam, co=18)
        nut_astar = Nut("A* toàn cục", (X_BANG + 270, y + 92, 150, 32), self.chon_astar, co=18)
        self.nut_thuat_toan = {"greedy": nut_tham_lam, "astar": nut_astar}

        self.nut_dung_tinh = Nut("Dừng tính", (X_BANG, CAO_THANH_TIEU_DE + 160, 150, 36), self.dung_tinh)

    # điều khiển
    def quay_lai(self):
        self.huy_tien_trinh()
        if self.man_hinh_truoc is not None:
            self.ung_dung.chuyen_den(self.man_hinh_truoc)
        else:
            self.ung_dung.ve_man_hinh_chinh()

    def chay_dung(self):
        if not self.khung:
            return
        buoc_cuoi = len(self.khung) - 1
        if self.buoc >= buoc_cuoi:
            self.buoc = 0  # đã hết thì chạy lại từ đầu
        if self.dang_chay:
            self.dang_chay = False
        else:
            self.dang_chay = True

    def di(self, so_buoc):
        if not self.khung:
            return
        self.dang_chay = False
        buoc_moi = self.buoc + so_buoc
        buoc_cuoi = len(self.khung) - 1
        if buoc_moi < 0:
            buoc_moi = 0
        if buoc_moi > buoc_cuoi:
            buoc_moi = buoc_cuoi
        self.buoc = buoc_moi

    def buoc_toi(self):
        self.di(1)

    def buoc_lui(self):
        self.di(-1)

    def ve_dau(self):
        self.dang_chay = False
        self.buoc = 0

    def doi_toc_do(self, thay_doi):
        muc_moi = self.muc_toc_do + thay_doi
        if muc_moi < 0:
            muc_moi = 0
        if muc_moi > len(TOC_DO) - 1:
            muc_moi = len(TOC_DO) - 1
        self.muc_toc_do = muc_moi

    def cham_lai(self):
        self.doi_toc_do(-1)

    def nhanh_len(self):
        self.doi_toc_do(1)

    def doi_thuat_toan(self, ma):
        if ma == self.thuat_toan and self.dang_tinh():
            return
        if ma == self.thuat_toan and self.khung:
            return
        # đang tính dở thì bỏ, tính lại bằng thuật toán mới
        self.bat_dau_tinh(ma)

    def chon_tham_lam(self):
        self.doi_thuat_toan("greedy")

    def chon_astar(self):
        self.doi_thuat_toan("astar")

    # tính lộ trình
    def bat_dau_tinh(self, thuat_toan):
        self.thuat_toan = thuat_toan
        for ma, nut in self.nut_thuat_toan.items():
            if ma == thuat_toan:
                nut.chon = True
            else:
                nut.chon = False

        self.lo_trinh = None
        self.loi = ""
        self.khung = []
        self.buoc = 0
        self.dang_chay = False
        self.tich_luy = 0.0

        # tính ở tiến trình riêng: cửa sổ không bị treo và dừng được giữa chừng
        self.huy_tien_trinh()
        self.hang_doi = multiprocessing.Queue()
        self.tien_trinh = multiprocessing.Process(
            target=tinh_o_tien_trinh_rieng,
            args=(self.ban_do, thuat_toan, self.hang_doi),
            daemon=True,
        )
        self.tien_trinh.start()
        self.luc_bat_dau = time.monotonic()

    def huy_tien_trinh(self):
        """Tắt tiến trình đang tính (nếu có)"""
        if self.tien_trinh is not None:
            if self.tien_trinh.is_alive():
                self.tien_trinh.terminate()
            self.tien_trinh.join(1)
        self.tien_trinh = None
        self.hang_doi = None

    def dung_tinh(self):
        """Bấm nút Dừng tính"""
        if not self.dang_tinh():
            return
        so_giay = int(time.monotonic() - self.luc_bat_dau)
        self.huy_tien_trinh()
        self.loi = f"Đã dừng sau {so_giay} giây. Chọn Tham lam để có lộ trình nhanh."

    def dang_tinh(self):
        if self.tien_trinh is None:
            return False
        return True

    def lay_ket_qua(self):
        """Xem tiến trình đã gửi kết quả về chưa; chưa có thì trả None"""
        if self.tien_trinh is None:
            return None
        try:
            return self.hang_doi.get_nowait()
        except queue.Empty:
            pass

        if self.tien_trinh.is_alive():
            return None
        # tiến trình vừa xong: chờ thêm chút cho dữ liệu kịp tới
        try:
            return self.hang_doi.get(timeout=1)
        except queue.Empty:
            return ("loi", "Tiến trình tính lộ trình bị dừng bất thường.")

    def nhan_ket_qua(self, ket_qua):
        self.huy_tien_trinh()
        loai, du_lieu = ket_qua
        if loai == "ok":
            self.lo_trinh = du_lieu
            khung, vet, thoi_diem_phun = dung_khung_hinh(self.ban_do, du_lieu)
            self.khung = khung
            self.vet = vet
            self.thoi_diem_phun = thoi_diem_phun
        else:
            self.loi = du_lieu

    def cap_nhat(self, dt):
        ket_qua = self.lay_ket_qua()
        if ket_qua is not None:
            self.nhan_ket_qua(ket_qua)

        if self.dang_chay and self.khung:
            buoc_cuoi = len(self.khung) - 1
            self.tich_luy += dt * TOC_DO[self.muc_toc_do]
            while self.tich_luy >= 1 and self.dang_chay:
                self.tich_luy -= 1
                self.buoc += 1
                if self.buoc >= buoc_cuoi:
                    self.buoc = buoc_cuoi
                    self.dang_chay = False

        if self.dang_chay:
            self.nut_chay.chu = "Dừng"
        else:
            self.nut_chay.chu = "Chạy"

    def xu_ly_su_kien(self, su_kien):
        if su_kien.type == pygame.KEYDOWN:
            if su_kien.key == pygame.K_ESCAPE:
                self.quay_lai()
            elif su_kien.key == pygame.K_SPACE:
                self.chay_dung()
            elif su_kien.key == pygame.K_RIGHT:
                self.buoc_toi()
            elif su_kien.key == pygame.K_LEFT:
                self.buoc_lui()
            elif su_kien.key == pygame.K_r:
                self.ve_dau()
            return

        tat_ca_nut = [self.nut_quay_lai] + self.nut_dieu_khien + list(self.nut_thuat_toan.values())
        if self.dang_tinh():
            tat_ca_nut.append(self.nut_dung_tinh)
        for nut in tat_ca_nut:
            if nut.xu_ly(su_kien):
                return

    # vẽ
    def co_o(self):
        co_theo_cot = VUNG_LUOI.w // self.ban_do["cols"]
        co_theo_hang = VUNG_LUOI.h // self.ban_do["rows"]
        return min(co_theo_cot, co_theo_hang)

    def khung_o(self, r, c):
        co = self.co_o()
        x = VUNG_LUOI.x + c * co
        y = VUNG_LUOI.y + r * co
        return pygame.Rect(x, y, co, co)

    def da_phun_chua(self, o):
        """Ô này đã được phun tính tới bước đang xem chưa"""
        if not self.khung:
            return False
        if o not in self.thoi_diem_phun:
            return False
        return self.thoi_diem_phun[o] <= self.buoc

    def ve_luoi(self, be_mat):
        for r, hang in enumerate(self.ban_do["cells"]):
            for c, o in enumerate(hang):
                khung = self.khung_o(r, c)
                mau = MAU_O[o]
                if o in MUC_BENH and self.da_phun_chua((r, c)):
                    mau = MAU_DA_PHUN
                pygame.draw.rect(be_mat, mau, khung)
                pygame.draw.rect(be_mat, MAU["nen"], khung, width=1)
                if o == TRAM:
                    ve_chu(be_mat, "T", khung.center, co=khung.h - 8, mau=MAU["nut"], dam=True, can="center")

    def ve_drone(self, be_mat):
        trang_thai = self.khung[self.buoc]

        # đường đã bay
        cac_diem = []
        for o in self.vet[:trang_thai["so_diem_vet"]]:
            cac_diem.append(self.khung_o(*o).center)
        if len(cac_diem) > 1:
            pygame.draw.lines(be_mat, MAU_VET, False, cac_diem, width=3)

        # drone
        tam = self.khung_o(*trang_thai["vi_tri"]).center
        ban_kinh = self.co_o() // 2 - 3
        if ban_kinh < 4:
            ban_kinh = 4
        pygame.draw.circle(be_mat, MAU["nut"], tam, ban_kinh + 2)
        pygame.draw.circle(be_mat, MAU_DRONE, tam, ban_kinh)

    def ve_thanh(self, be_mat, y, nhan, gia_tri, toi_da, mau):
        ve_chu(be_mat, f"{nhan}: {gia_tri}/{toi_da}", (X_BANG, y), co=18)
        nen = pygame.Rect(X_BANG + 150, y + 4, 280, 16)
        pygame.draw.rect(be_mat, MAU["nen_phu"], nen, border_radius=4)
        rong = 0
        if toi_da > 0:
            rong = int(nen.w * gia_tri / toi_da)
        pygame.draw.rect(be_mat, mau, (nen.x, nen.y, rong, nen.h), border_radius=4)

    def ve_dieu_khien(self, be_mat):
        y = Y_DIEU_KHIEN
        for nut in self.nut_dieu_khien:
            nut.bat = len(self.khung) > 0
            nut.ve(be_mat)

        ve_chu(be_mat, "Tốc độ:", (X_BANG, y + 64), co=18, can="midleft")
        ve_chu(be_mat, f"{TOC_DO[self.muc_toc_do]} bước/giây", (X_BANG + 339, y + 64), co=18, can="center")

        ve_chu(be_mat, "Thuật toán:", (X_BANG, y + 108), co=18, can="midleft")
        for nut in self.nut_thuat_toan.values():
            nut.ve(be_mat)
        if dem_o_benh(self.ban_do) > SO_O_ASTAR_NHANH:
            ve_chu(be_mat, f"(A* chạy nhanh khi ≤ {SO_O_ASTAR_NHANH} ô bệnh)", (X_BANG + 110, y + 130), co=15,
                   mau=MAU["chu_phu"])

        ve_chu(be_mat, "Phím: Space chạy/dừng · ← → từng bước · R về đầu", (X_BANG, y + 156), co=15,
               mau=MAU["chu_phu"])

    def ve_thong_tin(self, be_mat):
        y = CAO_THANH_TIEU_DE + 16
        ten = TEN_THUAT_TOAN[self.thuat_toan]
        ve_chu(be_mat, f"Thuật toán: {ten}", (X_BANG, y), co=22, dam=True)

        if self.loi:
            ve_chu(be_mat, "Không lập được lộ trình:", (X_BANG, y + 50), co=18, mau=MAU_LOI)
            ve_chu(be_mat, self.loi, (X_BANG, y + 76), co=17, mau=MAU_LOI)
            return
        if not self.khung:
            so_giay = int(time.monotonic() - self.luc_bat_dau)
            ve_chu(be_mat, f"Đang tính lộ trình… {so_giay} giây", (X_BANG, y + 50), co=20, mau=MAU["chu_phu"])
            so_o_benh = dem_o_benh(self.ban_do)
            if self.thuat_toan == "astar" and so_o_benh > SO_O_ASTAR_NHANH:
                ve_chu(be_mat, f"{so_o_benh} ô bệnh: A* có thể chạy rất lâu.", (X_BANG, y + 80), co=17,
                       mau=MAU_LOI)
            self.nut_dung_tinh.ve(be_mat)
            return

        trang_thai = self.khung[self.buoc]
        tong = self.lo_trinh
        so_buoc = len(self.khung) - 1
        y = y + 44
        ve_chu(be_mat, f"Bước {self.buoc}/{so_buoc}", (X_BANG, y), co=19)
        self.ve_thanh(be_mat, y + 32, "Thuốc", trang_thai["thuoc"], self.ban_do["k"], MAU_O[2])
        self.ve_thanh(be_mat, y + 60, "Pin", trang_thai["pin"], self.ban_do["p"], MAU_O[TRAM])

        dong_1 = f"Quãng đường: {trang_thai['quang_duong']}/{tong['tong_quang_duong']}"
        dong_2 = f"Ô đã phun: {trang_thai['da_phun']}/{dem_o_benh(self.ban_do)}"
        dong_3 = f"Số lần về trạm: {trang_thai['ve_tram']}/{tong['so_lan_ve_tram']}"
        dong_4 = f"Thời gian tính: {tong['thoi_gian_chay']:.2f} giây"
        ve_chu(be_mat, dong_1, (X_BANG, y + 92), co=18)
        ve_chu(be_mat, dong_2, (X_BANG, y + 118), co=18)
        ve_chu(be_mat, dong_3, (X_BANG, y + 144), co=18)
        ve_chu(be_mat, dong_4, (X_BANG, y + 170), co=18, mau=MAU["chu_phu"])

        mo_ta = mo_ta_su_kien(trang_thai["su_kien"])
        ve_chu(be_mat, mo_ta, (X_BANG, y + 206), co=19, mau=MAU["nhan"], dam=True)

    def ve_chu_thich(self, be_mat):
        cac_muc = [
            (MAU_O[KHOE], "Lúa khỏe"),
            (MAU_O[2], "Ô bệnh chưa phun"),
            (MAU_DA_PHUN, "Ô đã phun"),
            (MAU_VET, "Đường bay"),
        ]
        y_dau = CAO_THANH_TIEU_DE + 500
        for i, (mau, ten) in enumerate(cac_muc):
            cot = i % 2
            hang = i // 2
            x = X_BANG + cot * 220
            y = y_dau + hang * 30
            pygame.draw.rect(be_mat, mau, (x, y + 2, 20, 20), border_radius=4)
            ve_chu(be_mat, ten, (x + 28, y), co=17, mau=MAU["chu_phu"])

    def ve(self, be_mat):
        ve_thanh_tieu_de(be_mat, "Lộ trình drone")
        self.nut_quay_lai.ve(be_mat)
        self.ve_luoi(be_mat)
        if self.khung:
            self.ve_drone(be_mat)
        self.ve_dieu_khien(be_mat)
        self.ve_thong_tin(be_mat)
        self.ve_chu_thich(be_mat)
