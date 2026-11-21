"""E4 - Chẩn đoán bệnh từ ảnh lá lúa - TV5"""
import os
import threading

import pygame

from .giao_dien import CAO_THANH_TIEU_DE, MAU, ManHinh, Nut, phong_chu, ve_chu, ve_thanh_tieu_de
from .grid_editor import MAU_LOI

TEN_LOP = {"dao_on": "Đạo ôn", "bac_la": "Bạc lá", "dom_nau": "Đốm nâu", "la_khoe": "Lá khỏe"}
THU_MUC_ANH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "anh_thuc_te")
VUNG_ANH = pygame.Rect(20, CAO_THANH_TIEU_DE + 16, 400, 400)
X_PHAI = 450
RONG_PHAI = 630
VUNG_KET_QUA = pygame.Rect(X_PHAI, CAO_THANH_TIEU_DE + 76, RONG_PHAI, 528)
CAO_DONG = 24
SO_DONG_HIEN = 22  # 528 / 24
MAU_THANH = (238, 150, 72)


def hoi_anh():
    """Hộp thoại chọn ảnh, hủy thì trả None"""
    import tkinter
    from tkinter import filedialog

    goc = tkinter.Tk()
    goc.withdraw()
    goc.attributes("-topmost", True)
    kieu = [("Ảnh lá lúa", "*.jpg *.jpeg *.png *.bmp"), ("Tất cả", "*.*")]
    duong_dan = filedialog.askopenfilename(filetypes=kieu, initialdir=THU_MUC_ANH)
    goc.destroy()
    if duong_dan == "":
        return None
    return duong_dan


def do_rong_chu(noi_dung, co):
    phong = phong_chu(co)
    kich_thuoc = phong.size(noi_dung)
    return kich_thuoc[0]


def ngat_dong(noi_dung, co, rong_toi_da):
    """Chia chữ thành nhiều dòng vừa chiều rộng"""
    cac_dong = []
    cac_doan = noi_dung.split("\n")
    for doan in cac_doan:
        dong = ""
        cac_tu = doan.split(" ")
        for tu in cac_tu:
            if dong == "":
                dong_thu = tu
            else:
                dong_thu = dong + " " + tu

            if do_rong_chu(dong_thu, co) <= rong_toi_da:
                dong = dong_thu
            elif dong == "":
                dong = tu  # một từ quá dài thì để nguyên
            else:
                cac_dong.append(dong)
                dong = tu
        cac_dong.append(dong)
    return cac_dong


def ten_lop(ma):
    if ma in TEN_LOP:
        return TEN_LOP[ma]
    return ma


def tao_dong(chu, mau, dam):
    dong = {}
    dong["chu"] = chu
    dong["mau"] = mau
    dong["dam"] = dam
    return dong


def tao_noi_dung_ket_qua(ket_qua):
    """Danh sách dòng để hiện kết quả"""
    cac_dong = []

    if ket_qua["ket_luan"] is None:
        cac_dong.append(tao_dong("Kết luận: chưa đủ chắc chắn", MAU_LOI, True))
    else:
        ten = ten_lop(ket_qua["ket_luan"])
        cac_dong.append(tao_dong("Kết luận: " + ten, MAU["nhan"], True))

    if ket_qua["do_tin_cay"] is not None:
        phan_tram = round(ket_qua["do_tin_cay"] * 100)
        cac_dong.append(tao_dong("Độ tin cậy: " + str(phan_tram) + "%", MAU["chu"], False))

    cac_dong.append(tao_dong("", MAU["chu"], False))
    cac_dong.append(tao_dong("Giải thích", MAU["chu"], True))
    if "giai_thich" in ket_qua:
        cac_dong.append(tao_dong(ket_qua["giai_thich"], MAU["chu"], False))

    cac_dong.append(tao_dong("", MAU["chu"], False))
    cac_dong.append(tao_dong("Luật đã dùng", MAU["chu"], True))
    if len(ket_qua["luat_da_dung"]) == 0:
        cac_dong.append(tao_dong("(không có)", MAU["chu_phu"], False))
    else:
        chuoi_luat = ""
        for ma_luat in ket_qua["luat_da_dung"]:
            if chuoi_luat == "":
                chuoi_luat = ma_luat
            else:
                chuoi_luat = chuoi_luat + ", " + ma_luat
        cac_dong.append(tao_dong(chuoi_luat, MAU["chu"], False))

    cac_dong.append(tao_dong("", MAU["chu"], False))
    cac_dong.append(tao_dong("Nguồn", MAU["chu"], True))
    if len(ket_qua["nguon"]) == 0:
        cac_dong.append(tao_dong("(không có)", MAU["chu_phu"], False))
    else:
        for nguon in ket_qua["nguon"]:
            cac_dong.append(tao_dong("- " + nguon, MAU["chu_phu"], False))
    return cac_dong


class ManHinhChanDoan(ManHinh):
    def __init__(self, ung_dung):
        super().__init__(ung_dung)
        self.duong_dan_anh = None
        self.anh = None
        self.top3 = None
        self.ket_qua = None
        self.loi = ""
        self.dong_ket_qua = []
        self.cuon = 0

        # trao đổi với luồng chẩn đoán
        self.dang_chay = False
        self.lan = 0
        self.cau_hoi = None
        self.so_cau = 0
        self.tra_loi = None
        self.bo_qua = False
        self.da_tra_loi = threading.Event()

        # luồng ghi kết quả vào đây
        self.luong_xong = False
        self.luong_top3 = None
        self.luong_ket_qua = None
        self.luong_loi = ""

        self.tao_cac_nut()

    def tao_cac_nut(self):
        self.nut_quay_lai = Nut("← Quay lại", (20, 20, 150, 44), self.quay_lai)
        y = CAO_THANH_TIEU_DE + 16
        self.nut_chon_anh = Nut("Chọn ảnh…", (X_PHAI, y, 200, 44), self.chon_anh)
        self.nut_chan_doan = Nut("Chẩn đoán", (X_PHAI + 216, y, 200, 44), self.bat_dau)

        y = CAO_THANH_TIEU_DE + 260
        self.nut_co = Nut("Có (C)", (X_PHAI, y, 160, 44), self.tra_loi_co)
        self.nut_khong = Nut("Không (K)", (X_PHAI + 176, y, 160, 44), self.tra_loi_khong)
        self.nut_chua_biet = Nut("Chưa biết (B)", (X_PHAI + 352, y, 160, 44), self.tra_loi_chua_biet)
        self.nut_bo_qua = Nut("Bỏ qua các câu còn lại", (X_PHAI, y + 60, 336, 40), self.bo_qua_het, co=18)

    # chọn ảnh
    def quay_lai(self):
        self.huy_luong()
        self.ung_dung.ve_man_hinh_chinh()

    def chon_anh(self):
        if self.dang_chay:
            return
        duong_dan = hoi_anh()
        if duong_dan is not None:
            self.mo_anh(duong_dan)

    def mo_anh(self, duong_dan):
        self.duong_dan_anh = duong_dan
        self.top3 = None
        self.ket_qua = None
        self.dong_ket_qua = []
        self.loi = ""
        try:
            anh_goc = pygame.image.load(duong_dan)
        except (pygame.error, OSError):
            self.anh = None
            return

        # thu nhỏ giữ tỉ lệ
        ti_le_ngang = VUNG_ANH.w / anh_goc.get_width()
        ti_le_doc = VUNG_ANH.h / anh_goc.get_height()
        if ti_le_ngang < ti_le_doc:
            ti_le = ti_le_ngang
        else:
            ti_le = ti_le_doc
        rong = int(anh_goc.get_width() * ti_le)
        cao = int(anh_goc.get_height() * ti_le)
        self.anh = pygame.transform.smoothscale(anh_goc, (rong, cao))

    # chạy chẩn đoán
    def bat_dau(self):
        if self.duong_dan_anh is None:
            return
        if self.dang_chay:
            return
        self.top3 = None
        self.ket_qua = None
        self.dong_ket_qua = []
        self.loi = ""
        self.cuon = 0
        self.so_cau = 0
        self.cau_hoi = None
        self.bo_qua = False
        self.luong_xong = False
        self.dang_chay = True
        self.lan = self.lan + 1

        # chạy ở luồng riêng, câu hỏi chờ người dùng bấm nút
        luong = threading.Thread(target=self.chay, args=(self.lan,), daemon=True)
        luong.start()

    def chay(self, lan):
        """Chạy trong luồng riêng: gọi CN3 rồi CN2"""
        from src.app.chan_doan import diagnose_image
        from src.model import predict

        top3 = None
        ket_qua = None
        loi = ""
        try:
            # chưa có mô hình thì không có top-3
            if predict.MODEL_PATH.is_file():
                top3 = predict.predict_top3(self.duong_dan_anh)
            ket_qua = diagnose_image(self.duong_dan_anh, self.hoi)
        except (OSError, ValueError, RuntimeError) as e:
            loi = str(e)

        # đã bấm Quay lại thì bỏ kết quả
        if lan != self.lan:
            return
        self.luong_top3 = top3
        self.luong_ket_qua = ket_qua
        self.luong_loi = loi
        self.luong_xong = True

    def hoi(self, cau_hoi):
        """CN2 gọi hàm này mỗi câu hỏi; chờ người dùng trả lời"""
        if self.bo_qua:
            return None
        self.tra_loi = None
        self.da_tra_loi.clear()
        self.so_cau = self.so_cau + 1
        self.cau_hoi = cau_hoi
        self.da_tra_loi.wait()  # chờ bấm nút
        return self.tra_loi

    def tra_loi_cau(self, gia_tri):
        if self.cau_hoi is None:
            return
        self.tra_loi = gia_tri
        self.cau_hoi = None
        self.da_tra_loi.set()  # cho luồng chạy tiếp

    def tra_loi_co(self):
        self.tra_loi_cau(True)

    def tra_loi_khong(self):
        self.tra_loi_cau(False)

    def tra_loi_chua_biet(self):
        self.tra_loi_cau(None)

    def bo_qua_het(self):
        self.bo_qua = True
        self.tra_loi_cau(None)

    def huy_luong(self):
        """Rời màn hình: cho luồng chạy hết, bỏ kết quả"""
        self.lan = self.lan + 1
        self.bo_qua = True
        self.da_tra_loi.set()

    def nhan_ket_qua(self):
        self.luong_xong = False
        self.dang_chay = False
        if self.luong_loi != "":
            self.loi = self.luong_loi
            return

        self.top3 = self.luong_top3
        self.ket_qua = self.luong_ket_qua
        self.dong_ket_qua = []
        for muc in tao_noi_dung_ket_qua(self.ket_qua):
            cac_dong_nho = ngat_dong(muc["chu"], 18, VUNG_KET_QUA.w - 10)
            for chu in cac_dong_nho:
                self.dong_ket_qua.append(tao_dong(chu, muc["mau"], muc["dam"]))

    def cap_nhat(self, dt):
        if self.luong_xong:
            self.nhan_ket_qua()

        if self.dang_chay:
            self.nut_chon_anh.bat = False
        else:
            self.nut_chon_anh.bat = True

        if self.duong_dan_anh is None:
            self.nut_chan_doan.bat = False
        elif self.dang_chay:
            self.nut_chan_doan.bat = False
        else:
            self.nut_chan_doan.bat = True

    def cuon_ket_qua(self, so_dong):
        cuon_toi_da = len(self.dong_ket_qua) - SO_DONG_HIEN
        if cuon_toi_da < 0:
            cuon_toi_da = 0
        cuon_moi = self.cuon + so_dong
        if cuon_moi < 0:
            cuon_moi = 0
        if cuon_moi > cuon_toi_da:
            cuon_moi = cuon_toi_da
        self.cuon = cuon_moi

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
            elif su_kien.key == pygame.K_DOWN:
                self.cuon_ket_qua(1)
            elif su_kien.key == pygame.K_UP:
                self.cuon_ket_qua(-1)
            return

        # lăn chuột: lên thì y > 0
        if su_kien.type == pygame.MOUSEWHEEL:
            if su_kien.y > 0:
                self.cuon_ket_qua(-3)
            else:
                self.cuon_ket_qua(3)
            return

        if self.nut_quay_lai.xu_ly(su_kien):
            return
        if self.nut_chon_anh.xu_ly(su_kien):
            return
        if self.nut_chan_doan.xu_ly(su_kien):
            return

        # nút trả lời chỉ bấm được khi đang hỏi
        if self.cau_hoi is None:
            return
        if self.nut_co.xu_ly(su_kien):
            return
        if self.nut_khong.xu_ly(su_kien):
            return
        if self.nut_chua_biet.xu_ly(su_kien):
            return
        self.nut_bo_qua.xu_ly(su_kien)

    # vẽ
    def ve_anh(self, be_mat):
        pygame.draw.rect(be_mat, MAU["nen_phu"], VUNG_ANH, border_radius=8)
        if self.anh is not None:
            khung = self.anh.get_rect()
            khung.center = VUNG_ANH.center
            be_mat.blit(self.anh, khung)
        elif self.duong_dan_anh is not None:
            ve_chu(be_mat, "Không xem trước được ảnh này", VUNG_ANH.center, co=18,
                   mau=MAU["chu_phu"], can="center")
        else:
            ve_chu(be_mat, "Chưa chọn ảnh", VUNG_ANH.center, co=20, mau=MAU["chu_phu"], can="center")

        if self.duong_dan_anh is not None:
            ten_file = os.path.basename(self.duong_dan_anh)
            ve_chu(be_mat, ten_file, (VUNG_ANH.x, VUNG_ANH.bottom + 8), co=16, mau=MAU["chu_phu"])

    def ve_top3(self, be_mat):
        from src.model import predict

        y = VUNG_ANH.bottom + 40
        ve_chu(be_mat, "CNN (top-3)", (VUNG_ANH.x, y), co=20, dam=True)
        if not predict.MODEL_PATH.is_file():
            ve_chu(be_mat, "Chưa có mô hình CNN (.keras)", (VUNG_ANH.x + 140, y + 3), co=16, mau=MAU_LOI)
        if self.top3 is None:
            return

        y = y + 32
        for lop in self.top3:
            ma = lop[0]
            xac_suat = lop[1]
            ve_chu(be_mat, ten_lop(ma), (VUNG_ANH.x, y), co=18)

            nen = pygame.Rect(VUNG_ANH.x + 100, y + 4, 230, 16)
            pygame.draw.rect(be_mat, MAU["nen_phu"], nen, border_radius=4)
            rong = int(nen.w * xac_suat)
            pygame.draw.rect(be_mat, MAU_THANH, (nen.x, nen.y, rong, nen.h), border_radius=4)

            phan_tram = round(xac_suat * 100)
            ve_chu(be_mat, str(phan_tram) + "%", (nen.right + 10, y), co=18)
            y = y + 28

    def ve_cau_hoi(self, be_mat):
        y = VUNG_KET_QUA.y
        ve_chu(be_mat, "Câu hỏi " + str(self.so_cau), (X_PHAI, y), co=20, dam=True)

        cac_dong = ngat_dong(self.cau_hoi, 24, RONG_PHAI)
        y_dong = y + 40
        for dong in cac_dong:
            ve_chu(be_mat, dong, (X_PHAI, y_dong), co=24)
            y_dong = y_dong + 32

        self.nut_co.ve(be_mat)
        self.nut_khong.ve(be_mat)
        self.nut_chua_biet.ve(be_mat)
        self.nut_bo_qua.ve(be_mat)
        y_ghi_chu = self.nut_bo_qua.khung.bottom + 10
        ve_chu(be_mat, "Bỏ qua: các câu sau tính là chưa biết", (X_PHAI, y_ghi_chu), co=15,
               mau=MAU["chu_phu"])

    def ve_ket_qua(self, be_mat):
        # chỉ vẽ từ dòng self.cuon, tối đa SO_DONG_HIEN dòng
        y = VUNG_KET_QUA.y
        so_dong_da_ve = 0
        vi_tri = self.cuon
        while vi_tri < len(self.dong_ket_qua) and so_dong_da_ve < SO_DONG_HIEN:
            dong = self.dong_ket_qua[vi_tri]
            ve_chu(be_mat, dong["chu"], (VUNG_KET_QUA.x, y), co=18, mau=dong["mau"], dam=dong["dam"])
            y = y + CAO_DONG
            so_dong_da_ve = so_dong_da_ve + 1
            vi_tri = vi_tri + 1

        if len(self.dong_ket_qua) > SO_DONG_HIEN:
            ve_chu(be_mat, "Lăn chuột hoặc ↑ ↓ để xem thêm", (X_PHAI, VUNG_KET_QUA.bottom + 6), co=15,
                   mau=MAU["chu_phu"])

    def ve_trang_thai(self, be_mat):
        y = VUNG_KET_QUA.y
        if self.loi != "":
            ve_chu(be_mat, "Không chẩn đoán được:", (X_PHAI, y), co=20, mau=MAU_LOI)
            y_dong = y + 32
            for dong in ngat_dong(self.loi, 18, RONG_PHAI):
                ve_chu(be_mat, dong, (X_PHAI, y_dong), co=18, mau=MAU_LOI)
                y_dong = y_dong + 24
        elif self.cau_hoi is not None:
            self.ve_cau_hoi(be_mat)
        elif self.dang_chay:
            ve_chu(be_mat, "Đang chẩn đoán…", (X_PHAI, y), co=20, mau=MAU["chu_phu"])
        elif self.ket_qua is not None:
            self.ve_ket_qua(be_mat)
        elif self.duong_dan_anh is None:
            ve_chu(be_mat, "Bấm \"Chọn ảnh…\" để chọn ảnh lá lúa.", (X_PHAI, y), co=20,
                   mau=MAU["chu_phu"])
        else:
            ve_chu(be_mat, "Bấm \"Chẩn đoán\" rồi trả lời các câu hỏi triệu chứng.", (X_PHAI, y), co=20,
                   mau=MAU["chu_phu"])

    def ve(self, be_mat):
        ve_thanh_tieu_de(be_mat, "Chẩn đoán bệnh lá lúa")
        self.nut_quay_lai.ve(be_mat)
        self.nut_chon_anh.ve(be_mat)
        self.nut_chan_doan.ve(be_mat)
        self.ve_anh(be_mat)
        self.ve_top3(be_mat)
        self.ve_trang_thai(be_mat)
