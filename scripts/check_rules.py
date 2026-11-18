"""Kiểm tra bộ luật, nguồn, từ vựng và chuỗi suy diễn của CN2."""
import argparse
import json
import re
import unicodedata
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
RULE_FIELDS = {"id", "loai", "neu", "thi", "nguon"}
RULE_TYPES = {"chan_doan", "nguy_co", "trung_gian", "khuyen_nghi"}
DISEASES = {"dao_on", "bac_la", "dom_nau"}
ATOM_PATTERN = re.compile(r"^([a-z][a-z0-9_]*)=([a-z][a-z0-9_]*)$")
FORBIDDEN_PATTERN = re.compile(
    r"\b(?:thuoc|hoat[ _-]*chat|lieu|pesticide|fungicide|herbicide|insecticide)\b"
)
UNIT_PATTERN = re.compile(r"\d+(?:[.,]\d+)?\s*(?:mg|ml|kg|g|l|cc|lit|%|wp|ec|sc|wg)(?!\w)")


def _normalize(text: str) -> str:
    """Chuẩn hóa chữ để quét từ cấm mà không nhầm "tài liệu" với "liều"."""
    normalized = text.lower().replace("đ", "d")
    normalized = "".join(
        char
        for char in unicodedata.normalize("NFD", normalized)
        if unicodedata.category(char) != "Mn"
    )
    return normalized.replace("tai lieu", "tailieu")


def _check_sources(sources: object) -> tuple[dict[str, dict[str, Any]], list[str]]:
    """Kiểm tra mã nguồn duy nhất và thông tin nhận diện tối thiểu."""
    errors: list[str] = []
    if not isinstance(sources, dict) or not isinstance(sources.get("nguon"), list):
        return {}, ["Danh mục nguồn cần có danh sách nguon."]
    entries = sources["nguon"]
    if len(entries) < 4:
        errors.append(f"Danh mục cần ít nhất 4 nguồn; hiện có {len(entries)}.")
    result: dict[str, dict[str, Any]] = {}
    for index, entry in enumerate(entries):
        prefix = f"Nguồn {index + 1}"
        if not isinstance(entry, dict):
            errors.append(f"{prefix}: cần là đối tượng.")
            continue
        code = entry.get("ma")
        if not isinstance(code, str) or not code.strip():
            errors.append(f"{prefix}: ma phải là chuỗi không rỗng.")
            continue
        if code in result:
            errors.append(f"{prefix}: mã nguồn {code} bị trùng.")
        result[code] = entry
        for field in ("ten", "co_quan", "url"):
            if not isinstance(entry.get(field), str) or not entry[field].strip():
                errors.append(f"{prefix}: thiếu {field}.")
        year = entry.get("nam")
        if year is not None and (not isinstance(year, int) or isinstance(year, bool)):
            errors.append(f"{prefix}: nam phải là số nguyên hoặc null.")
        if year is None and not any(
            phrase in str(entry.get("ghi_chu", "")).lower()
            for phrase in ("không ghi năm", "thiếu năm", "khong ghi nam", "thieu nam")
        ):
            errors.append(f"{prefix}: thiếu năm nhưng chưa ghi rõ tình trạng năm xuất bản.")
    return result, errors


def _valid_vocabulary(vocabulary: object) -> tuple[dict[str, Any], list[str]]:
    """Kiểm tra cấu trúc từ vựng và lựa chọn tiếng Việt cho dữ kiện được hỏi."""
    errors: list[str] = []
    if not isinstance(vocabulary, dict) or not isinstance(vocabulary.get("thuoc_tinh"), dict):
        return {}, ["Từ vựng cần có đối tượng thuoc_tinh."]
    attributes = vocabulary["thuoc_tinh"]
    for name, definition in attributes.items():
        prefix = f"Thuộc tính {name}"
        if not isinstance(definition, dict):
            errors.append(f"{prefix}: định nghĩa phải là đối tượng.")
            continue
        attribute_type = definition.get("loai")
        description = definition.get("mo_ta")
        if not isinstance(description, str) or not description.strip():
            errors.append(f"{prefix}: thiếu mô tả ý nghĩa thuộc tính.")
        if not isinstance(attribute_type, str) or attribute_type not in {
            "du_kien_nguoi_dung", "su_kien_suy_ra"
        }:
            errors.append(f"{prefix}: loại phải là dữ kiện người dùng hoặc sự kiện suy ra.")
        values = definition.get("gia_tri")
        if not isinstance(values, list) or not values or any(
            not isinstance(value, str) or not value for value in values
        ) or len(values) != len(set(values)):
            errors.append(f"{prefix}: gia_tri phải là danh sách chuỗi duy nhất, không rỗng.")
            continue
        if attribute_type == "du_kien_nguoi_dung":
            question = definition.get("cau_hoi")
            if not isinstance(question, str) or not question.strip():
                errors.append(f"{prefix}: thiếu câu hỏi tiếng Việt.")
            elif not any(char in "ăâđêôơưĂÂĐÊÔƠƯ" for char in question):
                errors.append(f"{prefix}: câu hỏi cần viết bằng tiếng Việt.")
            if not {"co", "khong", "chua_biet"}.issubset(values):
                errors.append(f"{prefix}: cần giá trị co, khong và chua_biet.")
            choices = definition.get("lua_chon")
            if not isinstance(choices, list) or any(not isinstance(item, dict) for item in choices):
                errors.append(f"{prefix}: thiếu danh sách lựa chọn.")
                continue
            if any(not isinstance(item.get("ma"), str)
                   or not isinstance(item.get("nhan"), str) for item in choices):
                errors.append(f"{prefix}: mỗi lựa chọn cần mã và nhãn dạng chuỗi.")
                continue
            choice_map = {item["ma"]: item["nhan"] for item in choices}
            if len(choice_map) != len(choices):
                errors.append(f"{prefix}: mã lựa chọn bị trùng.")
            if set(choice_map) != set(values):
                errors.append(f"{prefix}: lựa chọn phải khớp toàn bộ giá trị hợp lệ.")
            if ("chua_biet" not in values or
                    choice_map.get("chua_biet") != "Chưa biết"):
                errors.append(f"{prefix}: phải có lựa chọn Chưa biết.")
            if choice_map.get("co") != "Có" or choice_map.get("khong") != "Không":
                errors.append(f"{prefix}: nhãn lựa chọn phải là Có và Không.")
            has_and = " và " in question.lower() if isinstance(question, str) else False
            has_or = " hoặc " in question.lower() if isinstance(question, str) else False
            expected_join = (
                "AND_OR" if has_and and has_or else "AND" if has_and
                else "OR" if has_or else None
            )
            if expected_join:
                if definition.get("phep_ghep") != expected_join:
                    errors.append(
                        f"{prefix}: câu hỏi ghép cần khai báo phép ghép {expected_join}."
                    )
                if not isinstance(definition.get("dien_giai_ghep"), str) or not definition[
                    "dien_giai_ghep"
                ].strip():
                    errors.append(f"{prefix}: câu hỏi ghép cần diễn giải rõ ý nghĩa.")
            elif "phep_ghep" in definition or "dien_giai_ghep" in definition:
                errors.append(f"{prefix}: khai báo phép ghép nhưng câu hỏi không có từ nối tương ứng.")
        elif attribute_type == "su_kien_suy_ra" and any(
            key in definition for key in ("cau_hoi", "lua_chon")
        ):
            errors.append(f"{prefix}: sự kiện suy ra không được khai báo như câu hỏi người dùng.")
    return attributes, errors


def _find_cycle(graph: dict[str, set[str]]) -> bool:
    """Trả True nếu đồ thị sự kiện có chu trình."""
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node: str) -> bool:
        if node in visiting:
            return True
        if node in visited:
            return False
        visiting.add(node)
        if any(visit(neighbor) for neighbor in graph.get(node, set())):
            return True
        visiting.remove(node)
        visited.add(node)
        return False

    return any(visit(node) for node in graph)


def validate_rules(
    document: object,
    vocabulary: object | None = None,
    sources: object | None = None,
    min_rules: int = 20,
    require_coverage: bool = True,
) -> list[str]:
    """Trả lỗi bắt buộc để script có thể chặn bộ luật chưa đạt tiêu chí."""
    if not isinstance(document, dict) or not isinstance(document.get("rules"), list):
        return ["Cần đối tượng chứa danh sách rules."]
    rules = document["rules"]
    errors: list[str] = []
    if len(rules) < min_rules:
        errors.append(f"Cần ít nhất {min_rules} luật; hiện có {len(rules)}.")
    attributes: dict[str, Any] = {}
    if vocabulary is not None:
        attributes, vocab_errors = _valid_vocabulary(vocabulary)
        errors.extend(vocab_errors)
    if sources is None:
        source_map = {}
    else:
        source_map, source_errors = _check_sources(sources)
        errors.extend(source_errors)

    seen: set[str] = set()
    graph: dict[str, set[str]] = {}
    parsed_rules: list[tuple[dict[str, Any], list[str], str]] = []
    for index, rule in enumerate(rules):
        prefix = f"Luật {index + 1}"
        if not isinstance(rule, dict) or set(rule) != RULE_FIELDS:
            errors.append(f"{prefix}: cần đúng các trường {sorted(RULE_FIELDS)}.")
            continue
        rule_id, kind = rule["id"], rule["loai"]
        if not isinstance(rule_id, str) or not rule_id.strip():
            errors.append(f"{prefix}: id phải là chuỗi không rỗng.")
        elif rule_id in seen:
            errors.append(f"{prefix}: id trùng.")
        else:
            seen.add(rule_id)
        if not isinstance(kind, str) or kind not in RULE_TYPES:
            errors.append(f"{prefix}: loai không hợp lệ.")
        conditions = rule["neu"]
        if not isinstance(conditions, list) or not conditions or any(
            not isinstance(value, str) or not value.strip() for value in conditions
        ):
            errors.append(f"{prefix}: neu phải là danh sách sự kiện không rỗng.")
            continue
        conclusion = rule["thi"]
        if not isinstance(conclusion, str) or not conclusion.strip():
            errors.append(f"{prefix}: thi phải là sự kiện không rỗng.")
            continue
        source = rule["nguon"]
        if not isinstance(source, dict) or set(source) != {"ma", "muc"}:
            errors.append(f"{prefix}: nguon cần có đúng ma và muc trích dẫn.")
        elif (not isinstance(source.get("ma"), str) or not source["ma"].strip()
              or not isinstance(source.get("muc"), str) or not source["muc"].strip()):
            errors.append(f"{prefix}: nguon.ma và nguon.muc phải không rỗng.")
        elif sources is not None and source["ma"] not in source_map:
            errors.append(f"{prefix}: mã nguồn {source['ma']} không tồn tại.")

        atoms = [*conditions, conclusion]
        valid_atoms = True
        for atom in atoms:
            match = ATOM_PATTERN.fullmatch(atom) if isinstance(atom, str) else None
            if not match:
                errors.append(f"{prefix}: sự kiện {atom!r} phải có dạng thuộc_tính=giá_trị.")
                valid_atoms = False
                continue
            if vocabulary is not None:
                attr, value = match.groups()
                definition = attributes.get(attr)
                allowed_values = definition.get("gia_tri", []) if isinstance(definition, dict) else []
                if not isinstance(allowed_values, list) or value not in allowed_values:
                    errors.append(f"{prefix}: thuộc tính hoặc giá trị {atom!r} không có trong từ vựng.")
                    valid_atoms = False
        if valid_atoms:
            conclusion_attribute = conclusion.split("=", 1)[0]
            definition = attributes.get(conclusion_attribute, {})
            if vocabulary is not None and (
                not isinstance(definition, dict) or definition.get("loai") != "su_kien_suy_ra"
            ):
                errors.append(f"{prefix}: thi phải là thuộc tính sự kiện suy ra.")
            expected_output = {
                "chan_doan": "suy_luan",
                "nguy_co": "yeu_to_nguy_co",
                "trung_gian": "can_kiem_tra",
                "khuyen_nghi": "khuyen_nghi",
            }.get(kind) if isinstance(kind, str) else None
            if expected_output and conclusion_attribute != expected_output:
                errors.append(f"{prefix}: loai {kind} phải suy ra thuộc tính {expected_output}.")
            for condition in conditions:
                graph.setdefault(condition, set()).add(conclusion)
            parsed_rules.append((rule, conditions, conclusion))

        content = _normalize(json.dumps(rule, ensure_ascii=False))
        if FORBIDDEN_PATTERN.search(content):
            errors.append(f"{prefix}: có dấu hiệu đề cập nội dung bị cấm về sản phẩm hoặc liều lượng.")
        if UNIT_PATTERN.search(content):
            errors.append(f"{prefix}: có dấu hiệu đơn vị liều hoặc dạng chế phẩm.")

    if _find_cycle(graph):
        errors.append("Đồ thị sự kiện chứa chu trình suy diễn.")
    if vocabulary is not None and require_coverage:
        for disease in DISEASES:
            suspicion = f"suy_luan=nghi_{disease}"
            if not any(rule["loai"] == "chan_doan" and result == suspicion
                       for rule, _, result in parsed_rules):
                errors.append(f"Thiếu luật chẩn đoán cho bệnh {disease}.")
            if not any(rule["loai"] == "khuyen_nghi" and suspicion in conditions
                       for rule, conditions, _ in parsed_rules):
                errors.append(f"Thiếu luật khuyến nghị cho bệnh {disease}.")
        input_attributes = {
            name for name, definition in attributes.items()
            if isinstance(definition, dict) and definition.get("loai") == "du_kien_nguoi_dung"
        }
        has_two_step_chain = any(
            rule["loai"] == "khuyen_nghi"
            and any(
                prior_result == premise
                and prior_rule["loai"] == "chan_doan"
                and any(condition.split("=", 1)[0] in input_attributes
                        for condition in prior_conditions)
                for premise in conditions
                for prior_rule, prior_conditions, prior_result in parsed_rules
            )
            for rule, conditions, _ in parsed_rules
        )
        if not has_two_step_chain:
            errors.append("Thiếu chuỗi suy diễn ít nhất hai bước từ dữ kiện người dùng đến khuyến nghị.")
    return errors


def main() -> None:
    """Kiểm tra luật; tiêu chí bắt buộc không đạt sẽ trả mã thoát khác 0."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", nargs="?", type=Path, default=ROOT / "src/rules/rules.json")
    parser.add_argument("--vocabulary", type=Path, default=ROOT / "src/rules/vocabulary.json")
    parser.add_argument("--sources", type=Path, default=ROOT / "src/rules/sources.json")
    args = parser.parse_args()
    try:
        document = json.loads(args.path.read_text(encoding="utf-8"))
        vocabulary = json.loads(args.vocabulary.read_text(encoding="utf-8"))
        sources = json.loads(args.sources.read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        parser.exit(1, f"Không đọc được cấu hình tri thức: {error}\n")
    errors = validate_rules(document, vocabulary, sources)
    if errors:
        parser.exit(1, "\n".join(errors) + "\n")
    print(f"Đạt kiểm tra bắt buộc: {len(document['rules'])} luật, nguồn, từ vựng và chuỗi suy diễn hợp lệ.")


if __name__ == "__main__":
    import sys

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    main()
