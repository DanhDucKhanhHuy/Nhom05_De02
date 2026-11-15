"""Suy diễn lùi, hỏi người dùng về dữ kiện đầu vào còn thiếu."""
import json
from pathlib import Path

from src.contracts import HoiNguoiDung, KetQuaSuyDienLui, Luat, TrangThaiSuyDien, VetLuat
from src.rules.trace import rule_step, unique_steps

VOCABULARY_PATH = Path(__file__).with_name("vocabulary.json")


def _questions() -> dict[str, str]:
    """Đọc câu hỏi tiếng Việt, chỉ lấy thuộc tính du_kien_nguoi_dung.

    Thuộc tính suy ra không được hỏi, kể cả khi có trường cau_hoi trong từ vựng.
    Nếu không đọc được tệp, trả bảng rỗng: vẫn chứng minh bằng facts và luật,
    nhưng không thể hỏi thêm dữ kiện.
    """
    try:
        document = json.loads(VOCABULARY_PATH.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return {
        name: definition["cau_hoi"]
        for name, definition in document.get("thuoc_tinh", {}).items()
        if isinstance(definition, dict)
        and definition.get("loai") == "du_kien_nguoi_dung"
        and isinstance(definition.get("cau_hoi"), str)
    }


def backward(goal: str, facts: set[str], rules: list[Luat], hoi_nguoi_dung: HoiNguoiDung) -> bool:
    """Chứng minh đích bằng facts, luật đệ quy hoặc câu trả lời người dùng.

    True nghĩa là chứng minh được; False nghĩa là chưa chứng minh được,
    không phải khẳng định đích sai. Không sửa facts hoặc rules của bên gọi.

    Mỗi thuộc tính chỉ hỏi một lần trong một lời gọi. Callback trả True, False,
    None lần lượt khớp giá trị co, khong, chua_biet. None không chứng minh được
    co hoặc khong; chỉ khớp khi đích yêu cầu rõ giá trị chua_biet.
    """
    result = _backward_result(goal, facts, rules, hoi_nguoi_dung, stop_on_unknown=True)
    return result["trang_thai"] == "xac_nhan"


def backward_with_status(
    goal: str, facts: set[str], rules: list[Luat], hoi_nguoi_dung: HoiNguoiDung,
) -> KetQuaSuyDienLui:
    """Phân biệt chứng minh được, bị dữ kiện bác bỏ và chưa đủ căn cứ.

    Bác bỏ chỉ xét đích trong bộ luật hiện tại, không khẳng định không mắc bệnh.
    Khác API bool cũ, gặp chưa biết trong AND vẫn xét tiếp để tìm dữ kiện bác bỏ.
    """
    return _backward_result(goal, facts, rules, hoi_nguoi_dung, stop_on_unknown=False)


def _backward_result(
    goal: str, facts: set[str], rules: list[Luat], hoi_nguoi_dung: HoiNguoiDung,
    stop_on_unknown: bool,
) -> KetQuaSuyDienLui:
    """Dùng chung thuật toán; cờ giữ nguyên cách cắt sớm của API bool cũ."""
    answers: dict[str, bool | None] = {}
    visiting: set[str] = set()
    questions = _questions()

    def prove(target: str) -> tuple[TrangThaiSuyDien, list[VetLuat]]:
        """Thử dữ kiện đã biết, các luật cùng kết luận, rồi mới hỏi nếu được phép."""
        if target in facts:
            return "xac_nhan", []
        # Chỉ chặn đích đang nằm trên nhánh đệ quy, không chặn các nhánh khác.
        if target in visiting:
            return "chua_du", []
        visiting.add(target)
        try:
            has_rule = False
            all_rejected = True
            for rule in rules:
                if rule["thi"] != target:
                    continue
                has_rule = True
                state: TrangThaiSuyDien = "xac_nhan"
                branch_trace: list[VetLuat] = []
                # AND: sai rõ ràng thì cắt ngay; chưa biết không được đổi thành sai.
                for condition in rule["neu"]:
                    condition_state, condition_trace = prove(condition)
                    if condition_state == "bac_bo":
                        state = "bac_bo"
                        break
                    if condition_state == "chua_du":
                        state = "chua_du"
                        if stop_on_unknown:
                            break
                    branch_trace.extend(condition_trace)
                if state == "xac_nhan":
                    return state, unique_steps([*branch_trace, rule_step(rule)])
                if state != "bac_bo":
                    all_rejected = False
                # OR: nhánh chưa thành công vẫn phải thử luật khác cùng kết luận.
            attribute, separator, value = target.partition("=")
            if separator and attribute in questions:
                if any(fact.startswith(f"{attribute}=") for fact in facts):
                    if f"{attribute}=chua_biet" in facts:
                        return "chua_du", []
                    return "bac_bo", []
                # Cache theo thuộc tính, nên hỏi a=co rồi a=khong không hỏi A hai lần.
                if attribute not in answers:
                    answers[attribute] = hoi_nguoi_dung(questions[attribute])
                answer = answers[attribute]
                if answer is not True and answer is not False and answer is not None:
                    raise ValueError("Hàm hỏi phải trả True, False hoặc None.")
                answer_value = {True: "co", False: "khong", None: "chua_biet"}[answer]
                if value == answer_value:
                    return "xac_nhan", []
                if answer is None:
                    return "chua_du", []
                return "bac_bo", []
            if has_rule and all_rejected:
                return "bac_bo", []
            return "chua_du", []
        finally:
            # Luôn bỏ dấu khi rời nhánh, kể cả khi return sớm hoặc callback báo lỗi.
            visiting.remove(target)

    state, trace = prove(goal)
    return {"trang_thai": state, "vet": trace}
