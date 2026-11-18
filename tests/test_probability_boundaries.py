"""Hồi quy cho dữ kiện bên ngoài và hợp đồng đầu vào CNN."""
import pytest

from src.rules import bayes
from src.rules.bayes import ANH_XA_BANG_CHUNG, bang_chung_bayes
from src.rules.ket_hop import chuan_hoa_cnn_top3


@pytest.mark.parametrize("code", sorted(ANH_XA_BANG_CHUNG))
@pytest.mark.parametrize("value", [False, None, "khong", "chua_biet", "False"])
def test_legacy_negative_or_unknown_is_not_positive(code, value):
    evidence, notes = bang_chung_bayes({code: value})
    assert evidence == {}
    assert notes and any(code in note for note in notes)


@pytest.mark.parametrize("code", sorted(ANH_XA_BANG_CHUNG))
def test_legacy_positive_forms_keep_the_documented_meaning(code):
    node, state = ANH_XA_BANG_CHUNG[code]
    for data in ([code], {code: True}, {code: "co"}):
        assert bang_chung_bayes(data) == ({node: state}, [])


@pytest.mark.parametrize("top3", [
    [("dao_on", .1), ("dom_nau", .7), ("bac_la", .1)],
    [("dao_on", 10 ** 1000), ("dom_nau", 0), ("bac_la", 0)],
])
def test_fusion_rejects_unsorted_or_out_of_range_input(top3):
    with pytest.raises(ValueError):
        chuan_hoa_cnn_top3(top3)


def test_enumeration_generates_only_states_compatible_with_observations():
    """Một nút đã quan sát không cần thử lại cả hai trạng thái."""
    rows = list(bayes._tat_ca_dong_nhat(
        ["ThoiTiet", "ThuaDam"], {"ThuaDam": "co"},
    ))
    assert rows == [
        {"ThoiTiet": "mua_am", "ThuaDam": "co"},
        {"ThoiTiet": "kho", "ThuaDam": "co"},
    ]
