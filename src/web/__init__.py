"""Ứng dụng Flask để trình diễn hệ luật CN2."""
import json
from pathlib import Path

from flask import Flask, jsonify, render_template, request

from src.rules.backward import backward_with_status
from src.rules.forward import forward_with_trace

RULE_DIR = Path(__file__).resolve().parents[1] / "rules"
ANSWERS = {"co": "Có", "khong": "Không", "chua_biet": "Chưa biết"}
DISEASES = {"dao_on": "đạo ôn", "bac_la": "bạc lá", "dom_nau": "đốm nâu"}
RECOMMENDATIONS = {
    "theo_doi_ruong_thuong_xuyen": "Theo dõi ruộng thường xuyên trong vụ",
    "chon_hat_giong_sach_benh": "Chọn hạt giống sạch bệnh trước khi gieo",
    "quan_ly_dinh_duong_dat_nuoc_phu_hop": "Quản lý dinh dưỡng, đất và nước phù hợp",
    "luan_canh_vu_tiep_theo_neu_bi_nhiem": "Cân nhắc luân canh vụ sau nếu đã xác nhận nhiễm",
}
RULE_TYPES = {
    "chan_doan": "Gợi ý bệnh",
    "nguy_co": "Nguy cơ",
    "trung_gian": "Cần kiểm tra",
    "khuyen_nghi": "Khuyến nghị",
}


class NeedAnswer(Exception):
    """Tạm dừng suy diễn tại câu hỏi đầu tiên chưa có câu trả lời."""


def read_knowledge(filename):
    return json.loads((RULE_DIR / filename).read_text(encoding="utf-8"))


def create_app():
    """Nạp tri thức và đăng ký giao diện cùng API suy diễn."""
    app = Flask(__name__)
    app.config["MAX_CONTENT_LENGTH"] = 16 * 1024
    rules = read_knowledge("rules.json")["rules"]
    vocabulary = read_knowledge("vocabulary.json")["thuoc_tinh"]
    sources = {item["ma"]: item for item in read_knowledge("sources.json")["nguon"]}
    questions = {
        key: item for key, item in vocabulary.items()
        if item["loai"] == "du_kien_nguoi_dung"
    }
    attributes = {item["cau_hoi"]: key for key, item in questions.items()}
    labels = {
        **{f"suy_luan=nghi_{key}": f"Nghi {name}" for key, name in DISEASES.items()},
        **{f"yeu_to_nguy_co={key}": f"Yếu tố nguy cơ {name}" for key, name in DISEASES.items()},
        **{f"can_kiem_tra={key}": f"Cần kiểm tra dấu hiệu {name}" for key, name in DISEASES.items()},
        **{f"khuyen_nghi={key}": name for key, name in RECOMMENDATIONS.items()},
        **{
            f"{key}={value}": f"{item['mo_ta']}: {label}"
            for key, item in questions.items()
            for value, label in ANSWERS.items()
        },
    }
    goals = {rule["thi"]: labels[rule["thi"]] for rule in rules
             if rule["loai"] in {"chan_doan", "khuyen_nghi"}}

    def read_request():
        data = request.get_json(silent=True)
        if not isinstance(data, dict) or not isinstance(data.get("answers"), dict):
            raise ValueError("Cần gửi danh sách câu trả lời đúng định dạng.")
        facts = set()
        for key, value in data["answers"].items():
            if key not in questions or not isinstance(value, str) or value not in ANSWERS:
                raise ValueError("Có thuộc tính hoặc câu trả lời không hợp lệ.")
            facts.add(f"{key}={value}")
        return data, facts

    @app.get("/")
    def index():
        return render_template(
            "index.html", rules=rules, sources=sources, questions=questions,
            labels=labels, goals=goals, rule_types=RULE_TYPES,
        )

    @app.post("/api/forward")
    def forward():
        try:
            _, facts = read_request()
        except ValueError as error:
            return jsonify(error=str(error)), 400
        known, trace = forward_with_trace(facts, rules)
        return jsonify(input_facts=sorted(facts), derived_facts=sorted(known - facts), trace=trace)

    @app.post("/api/backward/step")
    def backward():
        try:
            data, facts = read_request()
            goal = data.get("goal")
            if not isinstance(goal, str) or goal not in goals:
                raise ValueError("Hãy chọn mục tiêu suy diễn hợp lệ.")
        except ValueError as error:
            return jsonify(error=str(error)), 400

        def ask(question):
            # Dữ kiện đã trả lời được bộ suy diễn xử lý trước khi gọi hàm hỏi.
            raise NeedAnswer(attributes[question])

        try:
            result = backward_with_status(goal, facts, rules, ask)
        except NeedAnswer as pending:
            return jsonify(status="dang_hoi", next_question=pending.args[0], trace=[])
        return jsonify(status=result["trang_thai"], next_question=None, trace=result["vet"])

    return app
