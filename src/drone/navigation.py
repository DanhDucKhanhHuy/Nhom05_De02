"""Đồ thị bay: đích hạ cánh và vật cản có thể bay vượt qua."""

from collections.abc import Iterator, Sequence

from src.contracts import ToaDo


def cac_chuyen_bay(
    cells: Sequence[Sequence[int]],
    vt: ToaDo,
) -> Iterator[tuple[ToaDo, tuple[ToaDo, ...], int, int]]:
    """Sinh (đích hạ cánh, vật cản vượt qua, bước bay, pin tiêu hao)."""
    so_hang, so_cot = len(cells), len(cells[0])
    hang, cot = vt
    for dh, dc in ((0, 1), (0, -1), (1, 0), (-1, 0)):
        ke = (hang + dh, cot + dc)
        if not (0 <= ke[0] < so_hang and 0 <= ke[1] < so_cot):
            continue
        if cells[ke[0]][ke[1]] != -1:
            yield ke, (), 1, 1
            continue

        vat_can: list[ToaDo] = []
        diem = ke
        while 0 <= diem[0] < so_hang and 0 <= diem[1] < so_cot and cells[diem[0]][diem[1]] == -1:
            vat_can.append(diem)
            diem = (diem[0] + dh, diem[1] + dc)

        if 0 <= diem[0] < so_hang and 0 <= diem[1] < so_cot:
            quang_duong = len(vat_can) + 1
            yield diem, tuple(vat_can), quang_duong, quang_duong + len(vat_can)
