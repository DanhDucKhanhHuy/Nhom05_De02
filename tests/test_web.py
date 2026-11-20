"""Kiểm tra hợp đồng HTTP của bản demo hệ luật."""
import pytest

flask = pytest.importorskip("flask")


@pytest.fixture
def client():
    from src.web import create_app

    return create_app().test_client()


def test_forward_truy_vet_va_chan_thuoc_tinh_suy_ra(client):
    result = client.post("/api/forward", json={"answers": {"vet_la_hinh_thoi": "co"}})
    assert result.status_code == 200
    assert [step["id"] for step in result.json["trace"]] == ["DO01", "DO12"]
    assert result.json["trace"][0]["nguon"]["ma"] == "S1"
    result = client.post("/api/forward", json={"answers": {"suy_luan": "nghi_dao_on"}})
    assert result.status_code == 400


@pytest.mark.parametrize(("answer", "status"), [
    ("co", "xac_nhan"), ("khong", "bac_bo"), ("chua_biet", "chua_du"),
])
def test_backward_tung_buoc(client, answer, status):
    goal = "khuyen_nghi=theo_doi_ruong_thuong_xuyen"
    answers = {}
    while True:
        result = client.post("/api/backward/step", json={"goal": goal, "answers": answers})
        assert result.status_code == 200
        if result.json["status"] != "dang_hoi":
            break
        attribute = result.json["next_question"]
        assert attribute not in answers
        if not answers:
            assert attribute == "vet_la_hinh_thoi"
        answers[attribute] = answer
        assert len(answers) <= 6
    assert result.json["status"] == status
    assert [step["id"] for step in result.json["trace"]] == (
        ["DO01", "DO12"] if answer == "co" else []
    )
