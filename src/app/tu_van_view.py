"""E5 - Tư vấn theo triệu chứng: hệ luật CN2 + mạng Bayes, không cần CNN - TV5"""
import json
import threading
from pathlib import Path

import pygame

from .chan_doan_view import TEN_LOP, ngat_dong
from .giao_dien import CAO_THANH_TIEU_DE, MAU, ManHinh, Nut, ve_chu, ve_thanh_tieu_de

THU_MUC_LUAT = Path(__file__).resolve().parents[1] / "rules"
# (tên, vĩ độ, kinh độ) các thành phố, thị xã vùng ĐBSCL
DIA_DIEM = [
    ("Cần Thơ", 10.045, 105.746),
    ("Long Xuyên", 10.386, 105.435),
    ("Châu Đốc", 10.707, 105.117),
    ("Rạch Giá", 10.012, 105.081),
    ("Cao Lãnh", 10.460, 105.633),
    ("Mỹ Tho", 10.360, 106.360),
    ("Tân An", 10.535, 106.413),
    ("Vĩnh Long", 10.254, 105.972),
    ("Bến Tre", 10.243, 106.375),
    ("Trà Vinh", 9.935, 106.345),
    ("Sóc Trăng", 9.603, 105.980),
    ("Vị Thanh", 9.784, 105.470),
    ("Bạc Liêu", 9.285, 105.724),
    ("Cà Mau", 9.177, 105.150),
]
TEN_TRA_LOI = {"co": "Có", "khong": "Không", "chua_biet": "Chưa biết"}
THU_TU_LOP = ("dao_on", "bac_la", "dom_nau", "la_khoe")
MAU_LOP = {
    "dao_on": (200, 80, 60),
    "bac_la": (214, 170, 60),
    "dom_nau": (150, 96, 50),
    "la_khoe": (90, 160, 90),
}
TEN_KHUYEN_NGHI = {
    "theo_doi_ruong_thuong_xuyen": "theo dõi ruộng thường xuyên",
    "chon_hat_giong_sach_benh": "chọn hạt giống sạch bệnh",
    "quan_ly_dinh_duong_dat_nuoc_phu_hop": "quản lý dinh dưỡng, đất, nước phù hợp",
    "luan_canh_vu_tiep_theo_neu_bi_nhiem": "luân canh vụ sau nếu bị nhiễm",
}
MAU_LOI = (176, 48, 40)
X_TRAI = 20
RONG_TRAI = 600
X_PHAI = 650
RONG_PHAI = 430


def doc_json(ten_file):
    duong_dan = THU_MUC_LUAT / ten_file
    with open(duong_dan, encoding="utf-8") as f:
        return json.load(f)


def lay_danh_sach_cau_hoi():
    """Các thuộc tính người dùng trả lời được, theo thứ tự trong vocabulary.json"""
    tu_vung = doc_json("vocabulary.json")["thuoc_tinh"]
    danh_sach = []
    for ma, dinh_nghia in tu_vung.items():
        if dinh_nghia["loai"] == "du_kien_nguoi_dung":
            danh_sach.append((ma, dinh_nghia["cau_hoi"]))
    return danh_sach


def doc_ten_ket_luan(ket_luan):
    """'suy_luan=nghi_dao_on' -> 'Nghi đạo ôn'"""
    ten_benh = {"dao_on": "đạo ôn", "bac_la": "bạc lá", "dom_nau": "đốm nâu"}
    loai, gia_tri = ket_luan.split("=", 1)
    if loai == "suy_luan" and gia_tri.startswith("nghi_"):
        benh = gia_tri[len("nghi_"):]
        return "Nghi " + ten_benh.get(benh, benh)
    if loai == "yeu_to_nguy_co":
        return "Yếu tố nguy cơ " + ten_benh.get(gia_tri, gia_tri)
    if loai == "can_kiem_tra":
        return "Cần kiểm tra thêm " + ten_benh.get(gia_tri, gia_tri)
    if loai == "khuyen_nghi":
        return "Khuyến nghị: " + TEN_KHUYEN_NGHI.get(gia_tri, gia_tri)
    return ket_luan


def suy_dien(tra_loi, ma_thoi_tiet):
    """Từ câu trả lời (+ thời tiết) chạy suy diễn tiến và mạng Bayes"""
    from src.rules.bayes import truy_van
    from src.rules.forward import forward_with_trace

    # suy diễn tiến: dữ kiện dạng thuộc_tính=giá_trị
    cac_su_kien = set()
    for ma, gia_tri in tra_loi.items():
        cac_su_kien.add(f"{ma}={gia_tri}")
    cac_luat = doc_json("rules.json")["rules"]
    _, vet = forward_with_trace(cac_su_kien, cac_luat)

    # Bayes: câu trả lời + mã thời tiết (nếu đã lấy)
    bang_chung = dict(tra_loi)
    for ma in ma_thoi_tiet:
        bang_chung[ma] = "co"
    ket_qua_bayes = truy_van(bang_chung)

    ket_qua = {}
    ket_qua["xac_suat"] = ket_qua_bayes["xac_suat"]
    ket_qua["phuong_phap"] = ket_qua_bayes["phuong_phap"]
    ket_qua["vet"] = vet
    return ket_qua


class ManHinhTuVan(ManHinh):
    def __init__(self, ung_dung):
        super().__init__(ung_dung)
        self.cau_hoi = lay_danh_sach_cau_hoi()
        self.tra_loi = {}        # thuộc tính -> co / khong / chua_biet
        self.vi_tri = 0          # đang hỏi câu thứ mấy
        self.ma_thoi_tiet = []   # vd ["tt_am_do_cao"]
        self.chi_so_dia_diem = 0  # đang chọn địa điểm nào trong DIA_DIEM
        self.thoi_tiet = ""      # dòng chữ hiện thời tiết
        self.loi_thoi_tiet = ""
        self.dang_lay_thoi_tiet = False
        self.ket_qua_thoi_tiet = None
        self.tao_cac_nut()
        self.cap_nhat_ket_qua()

    def tao_cac_nut(self):
        y = CAO_THANH_TIEU_DE + 170
        self.nut_quay_lai = Nut("← Quay lại", (20, 20, 150, 44), self.quay_lai)
        self.nut_co = Nut("Có (C)", (X_TRAI, y, 180, 44), self.tra_loi_co)
        self.nut_khong = Nut("Không (K)", (X_TRAI + 200, y, 180, 44), self.tra_loi_khong)
        self.nut_chua_biet = Nut("Chưa biết (B)", (X_TRAI + 400, y, 180, 44), self.tra_loi_chua_biet)
        self.nut_cau_truoc = Nut("← Câu trước", (X_TRAI, y + 60, 180, 38), self.cau_truoc, co=18)
        self.nut_lam_lai = Nut("Làm lại", (X_TRAI + 200, y + 60, 180, 38), self.lam_lai, co=18)
        y_thoi_tiet = CAO_THANH_TIEU_DE + 470
        nut_truoc = Nut("<", (X_TRAI, y_thoi_tiet, 40, 40), self.dia_diem_truoc, co=20)
        nut_sau = Nut(">", (X_TRAI + 200, y_thoi_tiet, 40, 40), self.dia_diem_sau, co=20)
        self.nut_thoi_tiet = Nut("Lấy thời tiết", (X_TRAI + 260, y_thoi_tiet, 180, 40),
                                 self.lay_thoi_tiet, co=18)
        self.cac_nut = [self.nut_quay_lai, self.nut_co, self.nut_khong, self.nut_chua_biet,
                        self.nut_cau_truoc, self.nut_lam_lai, nut_truoc, nut_sau, self.nut_thoi_tiet]

    # trả lời
    def da_hoi_het(self):
        return self.vi_tri >= len(self.cau_hoi)

    def tra_loi_cau(self, gia_tri):
        if self.da_hoi_het():
            return
        ma, _ = self.cau_hoi[self.vi_tri]
        self.tra_loi[ma] = gia_tri
        self.vi_tri = self.vi_tri + 1
        self.cap_nhat_ket_qua()

    def tra_loi_co(self):
        self.tra_loi_cau("co")

    def tra_loi_khong(self):
        self.tra_loi_cau("khong")

    def tra_loi_chua_biet(self):
        self.tra_loi_cau("chua_biet")

    def cau_truoc(self):
        if self.vi_tri == 0:
            return
        self.vi_tri = self.vi_tri - 1
        ma, _ = self.cau_hoi[self.vi_tri]
        if ma in self.tra_loi:
            del self.tra_loi[ma]
        self.cap_nhat_ket_qua()

    def lam_lai(self):
        self.tra_loi = {}
        self.vi_tri = 0
        self.cap_nhat_ket_qua()

    def cap_nhat_ket_qua(self):
        """Mỗi lần trả lời thì tính lại luật và Bayes (nhanh, khoảng 0,01 giây)"""
        self.ket_qua = suy_dien(self.tra_loi, self.ma_thoi_tiet)

    def quay_lai(self):
        self.ung_dung.ve_man_hinh_chinh()

    # thời tiết (gọi mạng nên chạy ở luồng riêng)
    def ten_dia_diem(self):
        ten, _, _ = DIA_DIEM[self.chi_so_dia_diem]
        return ten

    def doi_dia_diem(self, buoc):
        """Chọn địa điểm trước/sau, đi vòng tròn"""
        if self.dang_lay_thoi_tiet:
            return
        so_dia_diem = len(DIA_DIEM)
        self.chi_so_dia_diem = (self.chi_so_dia_diem + buoc) % so_dia_diem

    def dia_diem_truoc(self):
        self.doi_dia_diem(-1)

    def dia_diem_sau(self):
        self.doi_dia_diem(1)

    def lay_thoi_tiet(self):
        if self.dang_lay_thoi_tiet:
            return
        self.dang_lay_thoi_tiet = True
        self.loi_thoi_tiet = ""
        dia_diem = DIA_DIEM[self.chi_so_dia_diem]
        luong = threading.Thread(target=self.tai_thoi_tiet, args=(dia_diem,), daemon=True)
        luong.start()

    def tai_thoi_tiet(self, dia_diem):
        from src.app.thoi_tiet import lay_thoi_tiet, tao_bang_chung_bayes

        ten, vi_do, kinh_do = dia_diem
        try:
            thoi_tiet = lay_thoi_tiet(vi_do, kinh_do)
            cac_ma = tao_bang_chung_bayes(thoi_tiet)
            chu = (f"{ten}: {thoi_tiet['temperature_c']} °C, độ ẩm {thoi_tiet['humidity_percent']} %, "
                   f"mưa {thoi_tiet['precipitation_mm']} mm")
            self.ket_qua_thoi_tiet = ("ok", cac_ma, chu)
        except (OSError, ValueError, KeyError) as loi:
            self.ket_qua_thoi_tiet = ("loi", [], f"Không lấy được thời tiết: {loi}")

    def cap_nhat(self, dt):
        if self.ket_qua_thoi_tiet is None:
            return
        loai, cac_ma, chu = self.ket_qua_thoi_tiet
        self.ket_qua_thoi_tiet = None
        self.dang_lay_thoi_tiet = False
        if loai == "ok":
            self.ma_thoi_tiet = cac_ma
            self.thoi_tiet = chu
            self.cap_nhat_ket_qua()
        else:
            self.loi_thoi_tiet = chu

    def xu_ly_su_kien(self, su_kien):
        if su_kien.type == pygame.KEYDOWN:
            if su_kien.key == pygame.K_ESCAPE:
                self.quay_lai()
            elif su_kien.key == pygame.K_c:
                self.tra_loi_co()
            elif su_kien.key == pygame.K_k:
                self.tra_loi_khong()
            elif su_kien.key == pygame.K_b:
                self.tra_loi_chua_biet()
            elif su_kien.key == pygame.K_BACKSPACE:
                self.cau_truoc()
            return

        for nut in self.cac_nut:
            if nut.xu_ly(su_kien):
                return

    # vẽ
    def ve_cau_hoi(self, be_mat):
        y = CAO_THANH_TIEU_DE + 16
        tong = len(self.cau_hoi)
        if self.da_hoi_het():
            ve_chu(be_mat, f"Đã trả lời hết {tong} câu", (X_TRAI, y), co=20, dam=True)
            ve_chu(be_mat, "Bấm “Câu trước” để sửa, hoặc “Làm lại”.", (X_TRAI, y + 40), co=19,
                   mau=MAU["chu_phu"])
        else:
            ve_chu(be_mat, f"Câu {self.vi_tri + 1}/{tong}", (X_TRAI, y), co=20, dam=True)
            _, cau = self.cau_hoi[self.vi_tri]
            cac_dong = ngat_dong(cau, 22, RONG_TRAI)
            for i, dong in enumerate(cac_dong):
                ve_chu(be_mat, dong, (X_TRAI, y + 40 + i * 30), co=22)

        dang_hoi = not self.da_hoi_het()
        self.nut_co.bat = dang_hoi
        self.nut_khong.bat = dang_hoi
        self.nut_chua_biet.bat = dang_hoi
        self.nut_cau_truoc.bat = self.vi_tri > 0
        for nut in self.cac_nut:
            nut.ve(be_mat)

    def ve_cau_da_tra_loi(self, be_mat):
        """Liệt kê vài câu trả lời gần nhất"""
        y = CAO_THANH_TIEU_DE + 290
        ve_chu(be_mat, "Đã trả lời:", (X_TRAI, y), co=18, dam=True)
        cac_cau_da_tra_loi = []
        for ma, cau in self.cau_hoi[:self.vi_tri]:
            cac_cau_da_tra_loi.append((cau, self.tra_loi[ma]))
        gan_nhat = cac_cau_da_tra_loi[-6:]
        for i, (cau, gia_tri) in enumerate(gan_nhat):
            chu = f"{TEN_TRA_LOI[gia_tri]} – {cau}"
            dong = ngat_dong(chu, 16, RONG_TRAI)[0]
            mau = MAU["nhan"] if gia_tri == "co" else MAU["chu_phu"]
            ve_chu(be_mat, dong, (X_TRAI, y + 28 + i * 24), co=16, mau=mau)

    def ve_thoi_tiet(self, be_mat):
        # tên địa điểm nằm giữa hai nút < >
        y_nut = CAO_THANH_TIEU_DE + 470
        ve_chu(be_mat, self.ten_dia_diem(), (X_TRAI + 120, y_nut + 20), co=18, can="center")

        y = CAO_THANH_TIEU_DE + 520
        if self.dang_lay_thoi_tiet:
            ve_chu(be_mat, "Đang lấy thời tiết…", (X_TRAI, y), co=17, mau=MAU["chu_phu"])
        elif self.loi_thoi_tiet:
            ve_chu(be_mat, self.loi_thoi_tiet[:80], (X_TRAI, y), co=16, mau=MAU_LOI)
        elif self.thoi_tiet:
            ve_chu(be_mat, self.thoi_tiet, (X_TRAI, y), co=17)
            if self.ma_thoi_tiet:
                bang_chung = ", ".join(self.ma_thoi_tiet)
            else:
                bang_chung = "không có"
            ve_chu(be_mat, f"Bằng chứng đưa vào Bayes: {bang_chung}", (X_TRAI, y + 24), co=16,
                   mau=MAU["chu_phu"])
        else:
            ve_chu(be_mat, "Thời tiết là bằng chứng thêm cho Bayes (cần mạng).", (X_TRAI, y), co=16,
                   mau=MAU["chu_phu"])

    def ve_xac_suat(self, be_mat):
        y = CAO_THANH_TIEU_DE + 16
        ve_chu(be_mat, "Xác suất theo mạng Bayes", (X_PHAI, y), co=20, dam=True)
        xac_suat = self.ket_qua["xac_suat"]
        for i, lop in enumerate(THU_TU_LOP):
            gia_tri = xac_suat[lop]
            y_dong = y + 40 + i * 36
            ve_chu(be_mat, TEN_LOP[lop], (X_PHAI, y_dong), co=18)
            nen = pygame.Rect(X_PHAI + 90, y_dong + 3, 250, 18)
            pygame.draw.rect(be_mat, MAU["nen_phu"], nen, border_radius=4)
            rong = int(nen.w * gia_tri)
            pygame.draw.rect(be_mat, MAU_LOP[lop], (nen.x, nen.y, rong, nen.h), border_radius=4)
            ve_chu(be_mat, f"{gia_tri * 100:.1f}%", (X_PHAI + 350, y_dong), co=18)

        # lớp cao nhất
        lop_cao_nhat = THU_TU_LOP[0]
        for lop in THU_TU_LOP:
            if xac_suat[lop] > xac_suat[lop_cao_nhat]:
                lop_cao_nhat = lop
        chu = f"Bayes nghiêng về: {TEN_LOP[lop_cao_nhat]} ({xac_suat[lop_cao_nhat] * 100:.1f}%)"
        ve_chu(be_mat, chu, (X_PHAI, y + 190), co=19, mau=MAU["nhan"], dam=True)
        ve_chu(be_mat, f"Cách tính: {self.ket_qua['phuong_phap']}", (X_PHAI, y + 218), co=15,
               mau=MAU["chu_phu"])

    def ve_luat(self, be_mat):
        y = CAO_THANH_TIEU_DE + 270
        ve_chu(be_mat, "Luật đã kích hoạt (suy diễn tiến)", (X_PHAI, y), co=20, dam=True)
        vet = self.ket_qua["vet"]
        if len(vet) == 0:
            ve_chu(be_mat, "(chưa có luật nào)", (X_PHAI, y + 34), co=17, mau=MAU["chu_phu"])
            return
        for i, buoc in enumerate(vet[:9]):
            chu = f"{buoc['id']} → {doc_ten_ket_luan(buoc['ket_luan'])} (nguồn {buoc['nguon']['ma']})"
            dong = ngat_dong(chu, 16, RONG_PHAI)[0]
            ve_chu(be_mat, dong, (X_PHAI, y + 34 + i * 26), co=16)
        if len(vet) > 9:
            ve_chu(be_mat, f"… và {len(vet) - 9} luật nữa", (X_PHAI, y + 34 + 9 * 26), co=16,
                   mau=MAU["chu_phu"])

    def ve(self, be_mat):
        ve_thanh_tieu_de(be_mat, "Tư vấn theo triệu chứng")
        self.ve_cau_hoi(be_mat)
        self.ve_cau_da_tra_loi(be_mat)
        self.ve_thoi_tiet(be_mat)
        self.ve_xac_suat(be_mat)
        self.ve_luat(be_mat)
        ve_chu(be_mat, "Xác suất từ CPD giả định của nhóm, chỉ để tham khảo.", (X_PHAI, 690), co=15,
               mau=MAU["chu_phu"])
