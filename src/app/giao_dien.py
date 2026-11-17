"""Giao diện dùng chung - TV5"""
import pygame

MAU = {
    "nen": (244, 241, 232),
    "nen_phu": (232, 228, 214),
    "chu": (31, 42, 31),
    "chu_phu": (88, 96, 84),
    "nhan": (63, 125, 58),
    "vien": (200, 194, 176),
    "nut": (255, 255, 255),
    "nut_re": (226, 238, 222),
    "tat": (170, 168, 158),
}

# phông có dấu tiếng Việt
_PHONG_UU_TIEN = ["segoeui", "arial", "tahoma", "helveticaneue", "dejavusans", "notosans"]
_bo_nho_phong = {}


def phong_chu(co, dam=False):
    khoa = (co, dam)
    if khoa not in _bo_nho_phong:
        ten = next((t for t in _PHONG_UU_TIEN if pygame.font.match_font(t)), None)
        if ten:
            _bo_nho_phong[khoa] = pygame.font.SysFont(ten, co, bold=dam)
        else:
            _bo_nho_phong[khoa] = pygame.font.Font(None, co)
    return _bo_nho_phong[khoa]


def ve_chu(be_mat, noi_dung, vi_tri, co=20, mau=None, dam=False, can="topleft"):
    anh = phong_chu(co, dam).render(noi_dung, True, mau or MAU["chu"])
    khung = anh.get_rect(**{can: vi_tri})
    be_mat.blit(anh, khung)
    return khung


class ManHinh:
    """Lớp cha các màn hình"""

    def __init__(self, ung_dung):
        self.ung_dung = ung_dung

    def xu_ly_su_kien(self, su_kien):
        pass

    def cap_nhat(self, dt):
        pass

    def ve(self, be_mat):
        pass


CAO_THANH_TIEU_DE = 84


def ve_thanh_tieu_de(be_mat, tieu_de):
    pygame.draw.rect(be_mat, MAU["nen_phu"], (0, 0, be_mat.get_width(), CAO_THANH_TIEU_DE))
    ve_chu(be_mat, tieu_de, (190, CAO_THANH_TIEU_DE // 2), co=28, dam=True, can="midleft")


class Nut:
    """Nút bấm"""

    def __init__(self, chu, khung, khi_bam, co=20, bat=True):
        self.chu = chu
        self.khung = pygame.Rect(khung)
        self.khi_bam = khi_bam
        self.co = co
        self.bat = bat

    def xu_ly(self, su_kien):
        if (self.bat and su_kien.type == pygame.MOUSEBUTTONDOWN and su_kien.button == 1
                and self.khung.collidepoint(su_kien.pos)):
            self.khi_bam()
            return True
        return False

    def ve(self, be_mat):
        re_chuot = self.bat and self.khung.collidepoint(pygame.mouse.get_pos())
        pygame.draw.rect(be_mat, MAU["nut_re"] if re_chuot else MAU["nut"], self.khung, border_radius=8)
        pygame.draw.rect(be_mat, MAU["nhan"] if re_chuot else MAU["vien"], self.khung,
                         width=2, border_radius=8)
        ve_chu(be_mat, self.chu, self.khung.center, co=self.co,
               mau=MAU["chu"] if self.bat else MAU["tat"], can="center")
