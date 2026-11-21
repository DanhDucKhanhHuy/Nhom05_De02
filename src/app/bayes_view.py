"""E6 - Mạng Bayes 5 nút theo ví dụ của đề: độ ẩm, nhiệt độ, lượng đạm, đạo ôn, vết hình thoi - TV5"""
import pygame

from .giao_dien import CAO_THANH_TIEU_DE, MAU, ManHinh, Nut, ve_chu, ve_thanh_tieu_de

MAU_NUT_MANG = (232, 240, 226)
MAU_DAO_ON = (200, 80, 60)
CO_O = (240, 96)  # rộng, cao của một ô nút mạng

# Bốn nút nhập được: (mã, tên hiện, vị trí góc trái ô, các lựa chọn)
# Mỗi lựa chọn: (chữ trên nút, bằng chứng gửi cho bayes.truy_van hoặc None = chưa biết)
CAC_NUT_NHAP = [
    ("do_am", "Độ ẩm", (40, CAO_THANH_TIEU_DE + 40), [
        ("Cao", ("ThoiTiet", "mua_am")),
        ("Thấp", ("ThoiTiet", "kho")),
        ("Chưa biết", None),
    ]),
    ("nhiet_do", "Nhiệt độ", (430, CAO_THANH_TIEU_DE + 40), [
        ("20–30 °C", ("NhietDo", "thuan_loi")),
        ("Ngoài", ("NhietDo", "khong_thuan_loi")),
        ("Chưa biết", None),
    ]),
    ("dam", "Lượng đạm bón", (820, CAO_THANH_TIEU_DE + 40), [
        ("Thừa", ("thua_dam", "co")),
        ("Vừa đủ", ("thua_dam", "khong")),
        ("Chưa biết", None),
    ]),
    ("vet", "Vết hình thoi", (430, CAO_THANH_TIEU_DE + 440), [
        ("Có", ("vet_la_hinh_thoi", "co")),
        ("Không", ("vet_la_hinh_thoi", "khong")),
        ("Chưa biết", None),
    ]),
]
VI_TRI_DAO_ON = (430, CAO_THANH_TIEU_DE + 240)


def tinh_xac_suat(lua_chon):
    """lua_chon: mã nút -> bằng chứng (hoặc None). Trả P(đạo ôn), P(vết hình thoi)"""
    from src.rules import bayes

    bang_chung = {}
    for gia_tri in lua_chon.values():
        if gia_tri is not None:
            ten, trang_thai = gia_tri
            bang_chung[ten] = trang_thai

    ket_qua = bayes.truy_van(bang_chung)
    p_dao_on = ket_qua["chi_tiet"]["DaoOn"]["co"]

    # vết hình thoi chỉ có cha là đạo ôn: P(vết) = P(vết|có)·P(có) + P(vết|không)·P(không)
    if lua_chon.get("vet") is not None:
        _, trang_thai_vet = lua_chon["vet"]
        if trang_thai_vet == "co":
            p_vet = 1.0
        else:
            p_vet = 0.0
    else:
        cpd_vet = bayes.NUT["VetHinhThoi"]["cpd"]
        p_vet_khi_co = cpd_vet[("co",)][0]
        p_vet_khi_khong = cpd_vet[("khong",)][0]
        p_vet = p_vet_khi_co * p_dao_on + p_vet_khi_khong * (1 - p_dao_on)

    return p_dao_on, p_vet, ket_qua["phuong_phap"]


class ManHinhBayes(ManHinh):
    def __init__(self, ung_dung):
        super().__init__(ung_dung)
        self.lua_chon = {}
        for ma, _, _, _ in CAC_NUT_NHAP:
            self.lua_chon[ma] = None
        self.tao_cac_nut()
        self.tinh_lai()

    def tao_cac_nut(self):
        self.nut_quay_lai = Nut("← Quay lại", (20, 20, 150, 44), self.quay_lai)
        self.nut_dat_lai = Nut("Đặt lại", (930, 20, 150, 44), self.dat_lai)
        # mỗi ô có 3 nút lựa chọn ở hàng dưới
        self.nut_lua_chon = []  # (mã nút mạng, bằng chứng, Nut)
        for ma, _, (x, y), cac_lua_chon in CAC_NUT_NHAP:
            for i, (chu, bang_chung) in enumerate(cac_lua_chon):
                khung = (x + 8 + i * 77, y + 54, 72, 32)
                nut = Nut(chu, khung, self.tao_ham_chon(ma, bang_chung), co=15)
                self.nut_lua_chon.append((ma, bang_chung, nut))

    def tao_ham_chon(self, ma, bang_chung):
        """Tạo hàm cho nút: bấm thì chọn bằng chứng này cho nút mạng ma"""
        def chon():
            self.chon(ma, bang_chung)
        return chon

    def chon(self, ma, bang_chung):
        self.lua_chon[ma] = bang_chung
        self.tinh_lai()

    def dat_lai(self):
        for ma in self.lua_chon:
            self.lua_chon[ma] = None
        self.tinh_lai()

    def tinh_lai(self):
        p_dao_on, p_vet, phuong_phap = tinh_xac_suat(self.lua_chon)
        self.p_dao_on = p_dao_on
        self.p_vet = p_vet
        self.phuong_phap = phuong_phap

    def quay_lai(self):
        self.ung_dung.ve_man_hinh_chinh()

    def xu_ly_su_kien(self, su_kien):
        if su_kien.type == pygame.KEYDOWN and su_kien.key == pygame.K_ESCAPE:
            self.quay_lai()
            return
        if self.nut_quay_lai.xu_ly(su_kien):
            return
        if self.nut_dat_lai.xu_ly(su_kien):
            return
        for _, _, nut in self.nut_lua_chon:
            if nut.xu_ly(su_kien):
                return

    # vẽ
    def ve_o(self, be_mat, x, y, ten, dam_vien=False):
        khung = pygame.Rect(x, y, CO_O[0], CO_O[1])
        pygame.draw.rect(be_mat, MAU_NUT_MANG, khung, border_radius=10)
        if dam_vien:
            do_day = 3
        else:
            do_day = 2
        pygame.draw.rect(be_mat, MAU["nhan"], khung, width=do_day, border_radius=10)
        ve_chu(be_mat, ten, (x + CO_O[0] // 2, y + 18), co=19, dam=True, can="center")
        return khung

    def ve_mui_ten(self, be_mat, diem_dau, diem_cuoi):
        pygame.draw.line(be_mat, MAU["chu_phu"], diem_dau, diem_cuoi, width=3)
        # đầu mũi tên: hai vạch ngắn
        x2, y2 = diem_cuoi
        x1, y1 = diem_dau
        huong = pygame.math.Vector2(x2 - x1, y2 - y1)
        if huong.length() == 0:
            return
        huong = huong.normalize() * 14
        canh_1 = huong.rotate(150)
        canh_2 = huong.rotate(-150)
        pygame.draw.line(be_mat, MAU["chu_phu"], diem_cuoi, (x2 + canh_1.x, y2 + canh_1.y), width=3)
        pygame.draw.line(be_mat, MAU["chu_phu"], diem_cuoi, (x2 + canh_2.x, y2 + canh_2.y), width=3)

    def ve_cac_mui_ten(self, be_mat):
        x_dao_on, y_dao_on = VI_TRI_DAO_ON
        dinh_dao_on = (x_dao_on + CO_O[0] // 2, y_dao_on)
        for ma, _, (x, y), _ in CAC_NUT_NHAP:
            if ma == "vet":
                continue
            day_o = (x + CO_O[0] // 2, y + CO_O[1])
            self.ve_mui_ten(be_mat, day_o, dinh_dao_on)
        # đạo ôn -> vết hình thoi
        _, _, (x_vet, y_vet), _ = CAC_NUT_NHAP[3]
        self.ve_mui_ten(be_mat, (x_dao_on + CO_O[0] // 2, y_dao_on + CO_O[1]),
                        (x_vet + CO_O[0] // 2, y_vet))

    def ve_dao_on(self, be_mat):
        x, y = VI_TRI_DAO_ON
        self.ve_o(be_mat, x, y, "Bệnh đạo ôn", dam_vien=True)
        nen = pygame.Rect(x + 16, y + 44, CO_O[0] - 32, 18)
        pygame.draw.rect(be_mat, MAU["nen_phu"], nen, border_radius=4)
        rong = int(nen.w * self.p_dao_on)
        pygame.draw.rect(be_mat, MAU_DAO_ON, (nen.x, nen.y, rong, nen.h), border_radius=4)
        ve_chu(be_mat, f"P(có) = {self.p_dao_on * 100:.1f}%", (x + CO_O[0] // 2, y + 78), co=18,
               mau=MAU_DAO_ON, dam=True, can="center")

    def ve(self, be_mat):
        ve_thanh_tieu_de(be_mat, "Mạng Bayes 5 nút")
        self.nut_quay_lai.ve(be_mat)
        self.nut_dat_lai.ve(be_mat)
        self.ve_cac_mui_ten(be_mat)

        for ma, ten, (x, y), _ in CAC_NUT_NHAP:
            self.ve_o(be_mat, x, y, ten)
        self.ve_dao_on(be_mat)

        for ma, bang_chung, nut in self.nut_lua_chon:
            nut.chon = self.lua_chon[ma] == bang_chung
            nut.ve(be_mat)

        # dự đoán vết hình thoi khi chưa nhập
        if self.lua_chon["vet"] is None:
            _, _, (x_vet, y_vet), _ = CAC_NUT_NHAP[3]
            ve_chu(be_mat, f"Dự đoán P(có vết) = {self.p_vet * 100:.1f}%",
                   (x_vet + CO_O[0] + 16, y_vet + 60), co=17, mau=MAU["chu_phu"])

        # giải thích bên trái
        x_chu = 40
        y_chu = CAO_THANH_TIEU_DE + 250
        ve_chu(be_mat, "Cách đọc:", (x_chu, y_chu), co=18, dam=True)
        cac_dong = [
            "Chọn trạng thái cho các nút đã biết,",
            "để \"Chưa biết\" nếu không quan sát.",
            "Mũi tên: nút cha → nút con.",
            "Ô đạo ôn hiện xác suất hậu nghiệm",
            "P(đạo ôn | bằng chứng đã chọn).",
        ]
        for i, dong in enumerate(cac_dong):
            ve_chu(be_mat, dong, (x_chu, y_chu + 28 + i * 24), co=16, mau=MAU["chu_phu"])

        ve_chu(be_mat, f"Cách tính: {self.phuong_phap}. Mạng đầy đủ có 23 nút; ở đây nhập 5 nút "
               "theo ví dụ của đề.", (40, 670), co=15, mau=MAU["chu_phu"])
        ve_chu(be_mat, "Số trong bảng xác suất là giả định của nhóm, chỉ để tham khảo.", (40, 692), co=15,
               mau=MAU["chu_phu"])
