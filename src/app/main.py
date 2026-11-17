"""E1 - Khung ứng dụng tích hợp Bác sĩ Lúa.

Phụ trách: TV5 | Thời hạn: T4 11/11 (theo Mẫu 01)

Cách chạy (từ thư mục Nhom05_De02):
    python -m src.app.main
"""
import pygame

from .giao_dien import MAU, ve_chu

RONG, CAO = 1100, 720
FPS = 60
TIEU_DE = "Bác sĩ Lúa"


class UngDung:
    """Cửa sổ chính: khởi tạo pygame và chạy vòng lặp sự kiện -> vẽ -> chờ khung hình kế tiếp."""

    def __init__(self):
        pygame.init()
        self.man_hinh = pygame.display.set_mode((RONG, CAO))
        pygame.display.set_caption(TIEU_DE)
        self.dong_ho = pygame.time.Clock()
        self.dang_chay = True

    def xu_ly_su_kien(self):
        for su_kien in pygame.event.get():
            if su_kien.type == pygame.QUIT:  # bấm nút X của cửa sổ
                self.dang_chay = False
            elif su_kien.type == pygame.KEYDOWN and su_kien.key == pygame.K_ESCAPE:
                self.dang_chay = False

    def ve(self):
        self.man_hinh.fill(MAU["nen"])
        ve_chu(self.man_hinh, TIEU_DE, (RONG // 2, CAO // 2 - 40), co=56, mau=MAU["nhan"],
               dam=True, can="center")
        ve_chu(self.man_hinh, "Phát hiện bệnh lá lúa · Lộ trình drone phun thuốc",
               (RONG // 2, CAO // 2 + 20), co=24, mau=MAU["chu_phu"], can="center")
        ve_chu(self.man_hinh, "Esc: thoát", (RONG // 2, CAO - 30), co=18, mau=MAU["chu_phu"],
               can="center")
        pygame.display.flip()  # đưa khung hình vừa vẽ lên màn hình

    def chay(self):
        while self.dang_chay:
            self.xu_ly_su_kien()
            self.ve()
            self.dong_ho.tick(FPS)  # giới hạn 60 khung hình/giây để không chiếm hết CPU
        pygame.quit()


def main():
    UngDung().chay()


if __name__ == "__main__":
    main()
