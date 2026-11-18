"""Kết hợp hỏi triệu chứng và suy diễn, truy vết luật cùng nguồn."""
import json
import math
from pathlib import Path

from src.contracts import ChanDoan, HoiNguoiDung, Top3
from src.rules import backward as backward_module
from src.rules.forward import forward_with_trace
from src.rules.ket_hop import ket_hop_cnn_bayes

RULES_PATH = Path(__file__).with_name("rules.json")
SOURCES_PATH = Path(__file__).with_name("sources.json")
DISEASE_NAMES = {"dao_on": "đạo ôn", "bac_la": "bạc lá", "dom_nau": "đốm nâu"}


def _check_top3(top3: Top3) -> None:
    """Kiểm tra đúng hợp đồng CNN trước khi đọc tri thức hoặc hỏi người dùng."""
    if not isinstance(top3, list) or len(top3) != 3:
        raise ValueError("CNN phải trả danh sách đúng ba lớp.")
    labels = set()
    probabilities = []
    for item in top3:
        if not isinstance(item, (tuple, list)) or len(item) != 2:
            raise ValueError("Mỗi dự đoán phải gồm mã lớp và xác suất.")
        label, probability = item
        if not isinstance(label, str) or label not in {*DISEASE_NAMES, "la_khoe"}:
            raise ValueError("Mã lớp CNN không hợp lệ.")
        if label in labels:
            raise ValueError("Các lớp CNN không được trùng.")
        labels.add(label)
        if (isinstance(probability, bool) or not isinstance(probability, (int, float))
                or not 0 <= probability <= 1 or not math.isfinite(probability)):
            raise ValueError("Xác suất CNN phải là số hữu hạn trong [0, 1].")
        probabilities.append(probability)
    if not 0 < sum(probabilities) <= 1 + 1e-6:
        raise ValueError("Tổng xác suất top-3 phải lớn hơn 0 và không vượt 1.")
    if probabilities != sorted(probabilities, reverse=True):
        raise ValueError("Top-3 phải sắp theo xác suất giảm dần.")


def _read_json(path: Path) -> dict:
    """Lỗi tệp phải được báo rõ, không giả thành kết quả không mắc bệnh."""
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        raise ValueError(f"Không đọc được cấu hình tri thức: {path.name}") from error
    if not isinstance(document, dict):
        raise ValueError(f"Cấu hình {path.name} phải là đối tượng JSON.")
    return document


def diagnose(top3: Top3, hoi_nguoi_dung: HoiNguoiDung) -> ChanDoan:
    """Thu thập một phiên dữ kiện rồi đối chiếu bộ luật với CNN–Bayes.

    Chỉ chọn một gợi ý khi đúng một bệnh được chứng minh và các bệnh còn lại
    bị bác bỏ trong bộ luật hiện tại, đồng thời CNN–Bayes cùng chọn bệnh đó.
    Điểm quyết định chưa hiệu chuẩn không được gán vào do_tin_cay.
    """
    _check_top3(top3)
    if not callable(hoi_nguoi_dung):
        raise ValueError("Cần truyền hàm hỏi người dùng.")
    rules = _read_json(RULES_PATH)["rules"]
    vocabulary = _read_json(backward_module.VOCABULARY_PATH)["thuoc_tinh"]
    sources = {source["ma"]: source for source in _read_json(SOURCES_PATH)["nguon"]}
    question_attributes = {
        definition["cau_hoi"]: attribute
        for attribute, definition in vocabulary.items()
        if definition["loai"] == "du_kien_nguoi_dung"
    }
    facts: set[str] = set()
    answers: dict[str, bool | None] = {}

    def ask_once(question: str) -> bool | None:
        """Nhớ theo thuộc tính trong cả phiên, kể cả câu trả lời chưa biết."""
        attribute = question_attributes[question]
        if attribute not in answers:
            answer = hoi_nguoi_dung(question)
            if answer is not True and answer is not False and answer is not None:
                raise ValueError("Hàm hỏi phải trả True, False hoặc None.")
            answers[attribute] = answer
            value = {True: "co", False: "khong", None: "chua_biet"}[answer]
            facts.add(f"{attribute}={value}")
        return answers[attribute]

    order = [label for label, _ in top3 if label in DISEASE_NAMES]
    # Vẫn kiểm tra bệnh bị lược khỏi top-3; không xem việc vắng mặt là phủ định.
    order.extend(label for label in DISEASE_NAMES if label not in order)
    states = {}
    for label in order:
        result = backward_module.backward_with_status(
            f"suy_luan=nghi_{label}", facts, rules, ask_once)
        states[label] = result["trang_thai"]
    # Hoàn tất dữ kiện cho nguy cơ, khuyến nghị và Bayes bằng chính cache này.
    # Không thêm các kết luận suy ra vào bằng chứng xác suất.
    for attribute, definition in vocabulary.items():
        if definition["loai"] == "du_kien_nguoi_dung" and attribute not in answers:
            ask_once(definition["cau_hoi"])
    probability = ket_hop_cnn_bayes(top3, facts)
    confirmed = [label for label in order if states[label] == "xac_nhan"]
    conclusion = None
    reason = "Bộ luật chưa chứng minh duy nhất một bệnh hoặc còn thiếu dữ kiện."
    if len(confirmed) == 1 and "chua_du" not in states.values():
        if probability["ket_luan"] == confirmed[0]:
            conclusion = confirmed[0]
            reason = "Bộ luật và CNN–Bayes đồng thuận về gợi ý bệnh."
        elif probability["ket_luan"] is None:
            reason = "CNN–Bayes chưa qua ngưỡng quyết định hoặc có kết quả hòa."
        else:
            other = DISEASE_NAMES.get(probability["ket_luan"], "lá khỏe")
            reason = (f"Bộ luật gợi ý {DISEASE_NAMES[confirmed[0]]}, CNN–Bayes chọn "
                      f"{other}: không đồng thuận; cần kiểm tra thêm.")

    # Tái diễn tiến từ chính dữ kiện đã thu thập để ghi đúng thứ tự bắn luật.
    _, trace = forward_with_trace(facts, rules)
    citations = []
    for step in trace:
        code = step["nguon"]["ma"]
        if code not in sources:
            raise ValueError(f"Mã nguồn không tồn tại: {code}")
        source = sources[code]
        year = source["nam"] if source["nam"] is not None else "năm chưa xác định"
        citation = (f"{code}: {source['ten']}; {source['co_quan']}; {year}; "
                    f"{step['nguon']['muc']}; {source['url']}")
        if citation not in citations:
            citations.append(citation)
    if conclusion is None:
        explanation = "Chưa đủ chắc, liên hệ cán bộ khuyến nông. Không kết luận lá khỏe."
    else:
        explanation = (f"Bộ luật gợi ý bệnh {DISEASE_NAMES[conclusion]}; "
                       "không thay thế chẩn đoán của cán bộ chuyên môn.")
    lines = [explanation, reason,
             (f"CNN–Bayes: {probability['phuong_phap_bayes']}; điểm quyết định "
              f"{probability['do_tin_cay_dieu_chinh']:.2%}, ngưỡng "
              f"{probability['nguong_ket_luan']:.2%}. "
              "Đây là điểm kỹ thuật từ CPD giả định, chưa phải xác suất đã hiệu chuẩn.")]
    lines.extend(f"Ghi chú Bayes: {note}" for note in probability["ghi_chu"])
    for step in trace:
        descriptions = []
        for atom in step["dieu_kien"]:
            attribute, value = atom.split("=", 1)
            description = vocabulary[attribute].get("mo_ta", attribute)
            value_label = {"co": "Có", "khong": "Không", "chua_biet": "Chưa biết"}.get(
                value, value)
            descriptions.append(f"{description}: {value_label}")
        lines.append(f"Luật {step['id']}: khi {'; '.join(descriptions)} "
                     f"thì {step['ket_luan']}. Nguồn {step['nguon']['ma']}, "
                     f"{step['nguon']['muc']}.")
        if step["ket_luan"] == "khuyen_nghi=chon_hat_giong_sach_benh":
            lines.append("Phạm vi: chuẩn bị hạt giống sạch bệnh trước gieo trồng, "
                         "không phải xử lý cây đang bệnh.")
        elif step["id"] == "DN10":
            lines.append("Phạm vi DN10: cân nhắc luân canh ở vụ tiếp theo khi ruộng "
                         "được xác nhận nhiễm. Mốc vụ là giới hạn thiết kế của nhóm, "
                         "chưa được nguồn hiện tại xác nhận trực tiếp.")
    return {
        "ket_luan": conclusion,
        "do_tin_cay": None,
        "luat_da_dung": [step["id"] for step in trace],
        "nguon": citations,
        "giai_thich": "\n".join(lines),
        "vet": trace,
    }
