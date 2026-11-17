"""Thành phần giao diện dùng chung cho CN4: bảng màu và phông chữ tiếng Việt.

Phụ trách: TV5
"""
import pygame

# Bảng màu: nền sáng, chữ đậm để dễ đọc cho người lớn tuổi.
MAU = {
    "nen": (244, 241, 232),        # nền chính
    "nen_phu": (232, 228, 214),    # thanh tiêu đề, khung
    "chu": (31, 42, 31),           # chữ chính
    "chu_phu": (88, 96, 84),       # chữ phụ, chú thích
    "nhan": (63, 125, 58),         # màu nhấn (xanh lúa)
    "vien": (200, 194, 176),       # đường viền
}

# Phông có đủ dấu tiếng Việt, ưu tiên theo thứ tự (Windows, macOS, Linux).
_PHONG_UU_TIEN = ["segoeui", "arial", "tahoma", "helveticaneue", "dejavusans", "notosans"]
_bo_nho_phong = {}


def phong_chu(co, dam=False):
    """Lấy phông chữ cỡ `co` (có dấu tiếng Việt), lưu lại để không phải nạp lại mỗi khung hình."""
    khoa = (co, dam)
    if khoa not in _bo_nho_phong:
        ten = next((t for t in _PHONG_UU_TIEN if pygame.font.match_font(t)), None)
        if ten:
            _bo_nho_phong[khoa] = pygame.font.SysFont(ten, co, bold=dam)
        else:  # máy không có phông nào trong danh sách: dùng phông mặc định của pygame
            _bo_nho_phong[khoa] = pygame.font.Font(None, co)
    return _bo_nho_phong[khoa]


def ve_chu(be_mat, noi_dung, vi_tri, co=20, mau=None, dam=False, can="topleft"):
    """Vẽ một dòng chữ lên be_mat. `can` là điểm neo của vi_tri: topleft, center, midtop...

    Trả về hình chữ nhật chữ chiếm, để xếp các thành phần tiếp theo.
    """
    anh = phong_chu(co, dam).render(noi_dung, True, mau or MAU["chu"])
    khung = anh.get_rect(**{can: vi_tri})
    be_mat.blit(anh, khung)
    return khung
