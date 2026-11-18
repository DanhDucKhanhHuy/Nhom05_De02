"""Hồi quy cho ý nghĩa dữ kiện giữa tri thức và Bayes."""
import json
from pathlib import Path

import pytest

from src.rules import bayes
from src.rules.backward import backward_with_status
from src.rules.forward import forward
from src.rules.ket_hop import VI_DU_BANG_CHUNG, VI_DU_CNN, ket_hop_cnn_bayes

ROOT = Path(__file__).resolve().parents[1]


def read_knowledge():
    """Đọc dữ liệu thật để kiểm tra đường đi của cùng một bằng chứng."""
    rules = json.loads((ROOT / "src/rules/rules.json").read_text(encoding="utf-8"))["rules"]
    vocabulary = json.loads(
        (ROOT / "src/rules/vocabulary.json").read_text(encoding="utf-8")
    )["thuoc_tinh"]
    return rules, vocabulary


def test_bacterial_sign_updates_its_own_bayes_node():
    """Vệt bạc lá đi vào nút riêng, không bị đổi thành hình thoi đạo ôn."""
    baseline = bayes.truy_van({}, su_dung_pgmpy=False)
    result = bayes.truy_van(
        {"vet_bac_ung_nuoc_tren_phien_la": "co"}, su_dung_pgmpy=False,
    )
    assert result["bang_chung"] == {"BacVetUngNuoc": "co"}
    assert result["chi_tiet"]["BacLa"]["co"] > baseline["chi_tiet"]["BacLa"]["co"]
    # Không có bằng chứng VetHinhThoi; các bệnh vẫn có thể tương quan qua cha chung.
    assert "VetHinhThoi" not in result["bang_chung"]


def test_unsupported_bacterial_sign_keeps_other_supported_symptoms():
    """Hai dấu hiệu khác nhau không bị mất vì ánh xạ nhầm cùng một nút."""
    evidence, notes = bayes.bang_chung_bayes({
        "vet_bac_ung_nuoc_tren_phien_la": "co",
        "dom_tron_hoac_bau_duc_nau": "co",
    })
    assert evidence == {
        "BacVetUngNuoc": "co",
        "DomTronBauDuc": "co",
    }
    assert not any("mâu thuẫn" in note for note in notes)


def test_bacterial_sign_still_supports_the_rule_engine():
    """Bỏ ánh xạ Bayes sai không làm mất luật bạc lá có nguồn."""
    rules, _ = read_knowledge()
    result = forward({"vet_bac_ung_nuoc_tren_phien_la=co"}, rules)
    assert "suy_luan=nghi_bac_la" in result
    assert "khuyen_nghi=chon_hat_giong_sach_benh" in result
    assert "suy_luan=nghi_dao_on" not in result


def test_white_panicle_is_an_observation_not_a_preexisting_diagnosis():
    """DO07 nhận dấu hiệu không đặc hiệu và chỉ yêu cầu kiểm tra thêm."""
    rules, vocabulary = read_knowledge()
    atom = "bong_hoac_gie_lep_trang=co"
    definition = vocabulary["bong_hoac_gie_lep_trang"]
    assert definition["cau_hoi"] == "Bạn có thấy toàn bộ bông hoặc từng gié bị lép trắng không?"
    assert "không đặc hiệu" in definition["dien_giai_ghep"]
    result = forward({atom}, rules)
    assert result == {atom, "can_kiem_tra=dao_on"}
    # Không đổi dữ kiện mã cũ có điều kiện bệnh thành quan sát mới.
    assert forward({"bong_lek_trang_khi_benh_xuat_hien_som=co"}, rules) == {
        "bong_lek_trang_khi_benh_xuat_hien_som=co",
    }


@pytest.mark.parametrize("answer, expected", [
    (True, "xac_nhan"), (False, "bac_bo"), (None, "chua_du"),
])
def test_white_panicle_can_be_asked_without_knowing_the_disease(answer, expected):
    rules, _ = read_knowledge()
    questions = []

    def ask(question):
        questions.append(question)
        return answer

    result = backward_with_status("can_kiem_tra=dao_on", set(), rules, ask)
    assert questions == ["Bạn có thấy toàn bộ bông hoặc từng gié bị lép trắng không?"]
    assert result["trang_thai"] == expected
    assert [step["id"] for step in result["vet"]] == (["DO07"] if answer is True else [])


def test_q2_example_reports_the_evidence_actually_used():
    """Ví dụ Q2 dùng đúng các nút quan sát riêng đã công bố."""
    result = ket_hop_cnn_bayes(VI_DU_CNN, VI_DU_BANG_CHUNG, su_dung_pgmpy=False)
    assert result["bang_chung_bayes"] == {
        "AmU_SuongSom": "co",
        "BacVetUngNuoc": "co",
        "ThuaDam": "co",
    }
    assert sum(result["xac_suat_bayes"].values()) == pytest.approx(1.0)
    assert sum(result["xac_suat_ket_hop"].values()) == pytest.approx(1.0)
    assert result["xac_suat_dong_mac"] > 0
    assert result["ket_luan"] is None
    assert result["trang_thai"] == "chua_du_chac"
