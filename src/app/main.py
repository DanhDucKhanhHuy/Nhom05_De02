"""E1 - Khung ứng dụng - TV5. Chạy: python -m src.app.main"""
import pygame

from .giao_dien import MAU, Nut, ve_chu, ve_thanh_tieu_de

RONG, CAO = 1100, 720
FPS = 60
TIEU_DE = "Bác sĩ Lúa"


class ManHinh:
    def __init__(self, ung_dung):
        self.ung_dung = ung_dung

    def xu_ly_su_kien(self, su_kien):
        pass

    def cap_nhat(self, dt):
        pass

    def ve(self, be_mat):
        pass


class ManHinhChinh(ManHinh):
    def __init__(self, ung_dung):
        super().__init__(ung_dung)
        x, rong, cao = RONG // 2 - 230, 460, 64
        self.cac_nut = [
            Nut("Chẩn đoán bệnh từ ảnh lá lúa", (x, 320, rong, cao), co=24,
                khi_bam=lambda: ung_dung.chuyen_den(ManHinhTamThoi(
                    ung_dung, "Chẩn đoán bệnh từ ảnh lá lúa",
                    "Sẽ ghép khi CNN (CN3) và hệ chuyên gia (CN2) hoàn thành."))),
            Nut("Bản đồ ruộng và lộ trình drone", (x, 400, rong, cao), co=24,
                khi_bam=lambda: ung_dung.chuyen_den(ManHinhTamThoi(
                    ung_dung, "Bản đồ ruộng và lộ trình drone",
                    "Bản đồ lưới (E2) và hoạt cảnh lộ trình (E3) đang được làm."))),
            Nut("Thoát", (x, 480, rong, cao), co=24, khi_bam=ung_dung.thoat),
        ]

    def xu_ly_su_kien(self, su_kien):
        if su_kien.type == pygame.KEYDOWN and su_kien.key == pygame.K_ESCAPE:
            self.ung_dung.thoat()
            return
        for nut in self.cac_nut:
            if nut.xu_ly(su_kien):
                break

    def ve(self, be_mat):
        ve_chu(be_mat, TIEU_DE, (RONG // 2, 190), co=60, mau=MAU["nhan"], dam=True, can="center")
        ve_chu(be_mat, "Phát hiện bệnh lá lúa · Lộ trình drone phun thuốc", (RONG // 2, 252),
               co=24, mau=MAU["chu_phu"], can="center")
        for nut in self.cac_nut:
            nut.ve(be_mat)
        ve_chu(be_mat, "Nhóm 5 – Đề 02 · Kết quả chỉ mang tính tham khảo, không thay thế cán bộ "
               "khuyến nông", (RONG // 2, CAO - 30), co=16, mau=MAU["chu_phu"], can="center")


class ManHinhTamThoi(ManHinh):
    def __init__(self, ung_dung, tieu_de, ghi_chu):
        super().__init__(ung_dung)
        self.tieu_de = tieu_de
        self.ghi_chu = ghi_chu
        self.nut_quay_lai = Nut("← Quay lại", (20, 20, 150, 44), ung_dung.ve_man_hinh_chinh)

    def xu_ly_su_kien(self, su_kien):
        if su_kien.type == pygame.KEYDOWN and su_kien.key == pygame.K_ESCAPE:
            self.ung_dung.ve_man_hinh_chinh()
        else:
            self.nut_quay_lai.xu_ly(su_kien)

    def ve(self, be_mat):
        ve_thanh_tieu_de(be_mat, self.tieu_de)
        self.nut_quay_lai.ve(be_mat)
        ve_chu(be_mat, self.ghi_chu, (RONG // 2, CAO // 2), co=24, mau=MAU["chu_phu"], can="center")


class UngDung:
    def __init__(self):
        pygame.init()
        self.cua_so = pygame.display.set_mode((RONG, CAO))
        pygame.display.set_caption(TIEU_DE)
        self.dong_ho = pygame.time.Clock()
        self.dang_chay = True
        self.man_hinh = ManHinhChinh(self)

    def chuyen_den(self, man_hinh):
        self.man_hinh = man_hinh

    def ve_man_hinh_chinh(self):
        self.chuyen_den(ManHinhChinh(self))

    def thoat(self):
        self.dang_chay = False

    def chay(self):
        while self.dang_chay:
            dt = self.dong_ho.tick(FPS) / 1000  # 60 khung/giây
            for su_kien in pygame.event.get():
                if su_kien.type == pygame.QUIT:
                    self.thoat()
                else:
                    self.man_hinh.xu_ly_su_kien(su_kien)
            self.man_hinh.cap_nhat(dt)
            self.cua_so.fill(MAU["nen"])
            self.man_hinh.ve(self.cua_so)
            pygame.display.flip()  # hiện lên màn hình
        pygame.quit()


def main():
    UngDung().chay()


if __name__ == "__main__":
    main()
