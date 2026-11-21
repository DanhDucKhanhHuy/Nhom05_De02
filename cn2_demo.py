"""Demo hệ luật bằng Pygame. Chạy: python -m src.app.cn2_demo."""
import json
from pathlib import Path

import pygame

from src.rules.backward import backward_with_status
from src.rules.forward import forward_with_trace

from .giao_dien import MAU, Nut, phong_chu, ve_chu

RULE_DIR = Path(__file__).resolve().parents[1] / "rules"
VALUES = ["", "co", "khong", "chua_biet"]
VALUE_LABELS = ["Chưa trả lời", "Có", "Không", "Chưa biết"]
STATUS = {
    "xac_nhan": "Chứng minh được mục tiêu",
    "bac_bo": "Các nhánh chứng minh bị dữ kiện bác bỏ",
    "chua_du": "Chưa đủ dữ kiện",
}


class NeedAnswer(Exception):
    """Đánh dấu câu hỏi chưa được trả lời."""


class DemoCN2:
    """Giữ dữ kiện và điều phối hai chế độ suy diễn."""

    def __init__(self):
        def read(name):
            return json.loads((RULE_DIR / name).read_text(encoding="utf-8"))

        self.rules = read("rules.json")["rules"]
        self.vocabulary = read("vocabulary.json")["thuoc_tinh"]
        self.sources = {s["ma"]: s for s in read("sources.json")["nguon"]}
        self.questions = {
            key: item for key, item in self.vocabulary.items()
            if item["loai"] == "du_kien_nguoi_dung"
        }
        self.by_question = {item["cau_hoi"]: key for key, item in self.questions.items()}
        self.goals = list(dict.fromkeys(
            rule["thi"] for rule in self.rules if rule["loai"] in {"chan_doan", "khuyen_nghi"}
        ))
        self.goal_index = 0
        self.mode = "tien"
        self.reset()

    def reset(self):
        self.answers = {}
        self.pending = None
        self.trace = []
        self.lines = []
        self.scroll = 0
        self.goal_index = self.goals.index("khuyen_nghi=theo_doi_ruong_thuong_xuyen")

    def label(self, atom):
        key, value = atom.split("=", 1)
        name = self.vocabulary[key]["mo_ta"]
        value_label = dict(zip(VALUES, VALUE_LABELS)).get(value, value.replace("_", " "))
        return f"{name}: {value_label}"

    def forward(self):
        facts = {f"{key}={value}" for key, value in self.answers.items()}
        known, self.trace = forward_with_trace(facts, self.rules)
        self.lines = ["DỮ KIỆN ĐÃ NHẬP"]
        self.lines += [self.label(fact) for fact in sorted(facts)] or ["Chưa nhập dữ kiện."]
        self.lines += ["SỰ KIỆN SUY RA"]
        self.lines += [self.label(fact) for fact in sorted(known - facts)] or ["Chưa có sự kiện mới."]
        self.scroll = 0

    def backward(self):
        facts = {f"{key}={value}" for key, value in self.answers.items()}

        def ask(question):
            raise NeedAnswer(self.by_question[question])

        self.trace = []
        self.pending = None
        try:
            result = backward_with_status(self.goals[self.goal_index], facts, self.rules, ask)
            self.trace = result["vet"]
            self.lines = [STATUS[result["trang_thai"]]]
        except NeedAnswer as question:
            self.pending = question.args[0]
            self.lines = [self.questions[self.pending]["cau_hoi"]]
            item = self.questions[self.pending]
            hint = item.get("dien_giai_ghep") or item.get("dien_giai_phu_dinh")
            if hint:
                self.lines.append(hint)
        self.lines += ["CÂU TRẢ LỜI ĐÃ GHI NHẬN"]
        self.lines += [self.label(fact) for fact in sorted(facts)]
        self.scroll = 0

    def content(self):
        lines = list(self.lines)
        if self.trace:
            lines.append("VẾT LUẬT VÀ NGUỒN")
        for step in self.trace:
            source = self.sources[step["nguon"]["ma"]]
            lines += [
                f"Luật {step['id']}",
                " và ".join(self.label(atom) for atom in step["dieu_kien"]),
                "→ " + self.label(step["ket_luan"]),
                f"{source['ma']} · {source['ten']} · {source['nam']}",
                step["nguon"]["muc"],
                source["url"],
                source["ghi_chu"],
            ]
        return lines


def main():
    """Chạy cửa sổ demo với danh sách dấu hiệu và kết quả có cuộn."""
    pygame.init()
    screen = pygame.display.set_mode((1100, 760))
    pygame.display.set_caption("Bác sĩ Lúa · Demo CN2")
    clock = pygame.time.Clock()
    demo = DemoCN2()
    buttons = []
    page = 0
    running = True

    def button(text, rect, callback):
        control = Nut(text, rect, callback, co=17)
        control.ve(screen)
        buttons.append(control)

    def change_mode(mode):
        demo.mode = mode
        demo.reset()

    def answer(key, value):
        if value:
            demo.answers[key] = value
        else:
            demo.answers.pop(key, None)
        if demo.mode == "lui":
            demo.backward()
        else:
            demo.forward()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
            elif event.type == pygame.MOUSEWHEEL:
                demo.scroll = max(0, demo.scroll - event.y * 55)
            else:
                for control in buttons:
                    if control.xu_ly(event):
                        break
        screen.fill(MAU["nen"])
        buttons = []
        ve_chu(screen, "Bác sĩ Lúa · Hệ chuyên gia CN2", (24, 20), co=29, dam=True)
        button("Suy diễn tiến", (24, 70, 170, 42), lambda: change_mode("tien"))
        button("Suy diễn lùi", (206, 70, 170, 42), lambda: change_mode("lui"))
        button("Làm lại", (388, 70, 120, 42), demo.reset)
        ve_chu(screen, f"Chế độ đang chọn: Suy diễn {demo.mode}", (24, 124), co=19)
        if demo.mode == "tien":
            def sample(key):
                demo.reset()
                demo.answers[key] = "co"
                demo.forward()

            button("Mẫu hình thoi", (24, 160, 180, 40), lambda: sample("vet_la_hinh_thoi"))
            button("Mẫu thừa đạm", (216, 160, 180, 40), lambda: sample("thua_dam"))
            keys = list(demo.questions)
            pages = (len(keys) + 4) // 5
            page %= pages
            for offset, key in enumerate(keys[page * 5:page * 5 + 5]):
                y = 220 + offset * 83
                ve_chu(screen, demo.questions[key]["mo_ta"], (24, y), co=16)
                value = demo.answers.get(key, "")
                next_value = VALUES[(VALUES.index(value) + 1) % len(VALUES)]
                button(VALUE_LABELS[VALUES.index(value)], (24, y + 28, 190, 36),
                       lambda k=key, v=next_value: answer(k, v))

            def next_page():
                nonlocal page
                page = (page + 1) % pages

            button(f"Trang {page + 1}/{pages} · Tiếp", (24, 660, 220, 40), next_page)
        else:
            ve_chu(screen, "Mục tiêu cần chứng minh", (24, 165), co=18, dam=True)
            value = demo.goals[demo.goal_index].split("=", 1)[1].replace("_", " ")
            ve_chu(screen, value[:49], (24, 200), co=16)

            def next_goal():
                index = (demo.goal_index + 1) % len(demo.goals)
                demo.reset()
                demo.goal_index = index

            button("Đổi mục tiêu", (24, 245, 180, 40), next_goal)
            button("Bắt đầu hỏi", (216, 245, 180, 40), demo.backward)
            if demo.pending:
                for index, value in enumerate(VALUES[1:]):
                    button(VALUE_LABELS[index + 1], (24 + index * 135, 320, 125, 44),
                           lambda v=value, k=demo.pending: answer(k, v))
        pygame.draw.rect(screen, MAU["nut"], (530, 120, 550, 580), border_radius=8)
        clip = pygame.Rect(548, 135, 514, 550)
        screen.set_clip(clip)
        wrapped = []
        for line in demo.content():
            words = line.split()
            current = ""
            for word in words:
                candidate = (current + " " + word).strip()
                if current and phong_chu(16).size(candidate)[0] > clip.width:
                    wrapped.append(current)
                    current = word
                else:
                    current = candidate
            wrapped.append(current)
        demo.scroll = min(demo.scroll, max(0, len(wrapped) * 26 - clip.height))
        for index, line in enumerate(wrapped):
            ve_chu(screen, line, (clip.x, clip.y + index * 26 - demo.scroll), co=16)
        screen.set_clip(None)
        ve_chu(screen, "Cuộn chuột để xem kết quả và nguồn. Esc để thoát.", (548, 708), co=16)
        ve_chu(screen, "Gợi ý theo bộ luật. Cần chuyên môn kiểm tra để xác định bệnh.", (24, 735), co=16)
        pygame.display.flip()
        clock.tick(30)
    pygame.quit()


if __name__ == "__main__":
    main()
