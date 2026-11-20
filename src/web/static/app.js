"use strict";

const knowledge = JSON.parse(document.querySelector("#knowledge-data").textContent);
const forward = document.querySelector("#forward");
const backward = document.querySelector("#backward");
const forwardResult = document.querySelector("#forward-result");
const backwardResult = document.querySelector("#backward-result");
const goal = document.querySelector("#goal");
const statusLabels = {
  xac_nhan: "Chứng minh được mục tiêu theo bộ luật",
  bac_bo: "Các nhánh của bộ luật bị dữ kiện bác bỏ",
  chua_du: "Chưa đủ dữ kiện"
};
let answers = {};

function element(tag, text, className) {
  const node = document.createElement(tag);
  node.textContent = text;
  if (className) node.className = className;
  return node;
}

function label(atom) {
  return knowledge.labels[atom] ?? atom;
}

function listFacts(output, title, facts, empty) {
  output.append(element("h3", title));
  if (!facts.length) {
    output.append(element("p", empty));
    return;
  }
  const list = document.createElement("ul");
  for (const fact of facts) list.append(element("li", label(fact)));
  output.append(list);
}

function renderTrace(output, trace) {
  if (!trace.length) return;
  const list = element("ol", "", "trace");
  for (const step of trace) {
    const source = knowledge.sources[step.nguon.ma];
    const item = document.createElement("li");
    const link = element("a", step.id);
    link.href = "#luat-" + step.id;
    link.addEventListener("click", () => {
      const rule = document.getElementById("luat-" + step.id);
      if (rule.hidden) {
        search.value = "";
        filterRules();
      }
      rule.open = true;
    });
    item.append(link, element("div", step.dieu_kien.map(label).join(" và ") + " → " + label(step.ket_luan)));
    item.append(element("small", source.ma + " · " + source.ten + " · " + step.nguon.muc));
    list.append(item);
  }
  output.append(element("h3", "Vết suy luận"), list);
}

async function post(form, payload) {
  const response = await fetch(form.action, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify(payload)
  });
  if (response.ok) return response.json();
  const error = await response.json().catch(() => ({}));
  throw new Error(error.error || "Không thể chạy suy diễn. Hãy thử lại.");
}

async function run(form, output, action) {
  if (form.getAttribute("aria-busy") === "true") return;
  const controls = Array.from(form.querySelectorAll("button, select"));
  form.setAttribute("aria-busy", "true");
  for (const control of controls) control.disabled = true;
  try {
    await action();
  } catch (error) {
    output.querySelector(".error")?.remove();
    output.append(element("p", error.message, "error"));
  } finally {
    for (const control of controls) control.disabled = false;
    form.removeAttribute("aria-busy");
  }
}

for (const button of forward.querySelectorAll("[data-sample]")) {
  button.addEventListener("click", () => {
    forward.reset();
    const select = forward.elements.namedItem(button.dataset.sample);
    select.value = "co";
    select.closest("details").open = true;
    forward.requestSubmit();
  });
}

forward.addEventListener("reset", () => forwardResult.replaceChildren());
forward.addEventListener("submit", (event) => {
  event.preventDefault();
  const inputs = Object.fromEntries([...new FormData(forward)].filter(([, value]) => value));
  forwardResult.replaceChildren();
  run(forward, forwardResult, async () => {
    const data = await post(forward, {answers: inputs});
    const result = element("div", "", "result");
    listFacts(result, "Dữ kiện đã nhập", data.input_facts, "Chưa nhập dữ kiện.");
    listFacts(result, "Sự kiện suy ra", data.derived_facts, "Chưa có sự kiện mới theo bộ luật.");
    renderTrace(result, data.trace);
    forwardResult.replaceChildren(result);
  });
});

async function backwardStep(nextAnswers) {
  await run(backward, backwardResult, async () => {
    const data = await post(backward, {goal: goal.value, answers: nextAnswers});
    answers = nextAnswers;
    const result = element("div", "", "result");
    if (data.status === "dang_hoi") {
      const question = knowledge.questions[data.next_question];
      result.append(element("h3", question.cau_hoi));
      const hint = question.dien_giai_ghep || question.dien_giai_phu_dinh;
      if (hint) result.append(element("p", hint, "muted"));
      const choices = element("div", "", "actions");
      for (const choice of question.lua_chon) {
        const button = element("button", choice.nhan, "secondary");
        button.type = "button";
        button.addEventListener("click", () => backwardStep({
          ...answers, [data.next_question]: choice.ma
        }));
        choices.append(button);
      }
      result.append(choices);
    } else {
      result.append(element("h3", statusLabels[data.status]));
      if (data.status === "bac_bo") {
        result.append(element("p", "Trạng thái này chỉ áp dụng cho mục tiêu trong bộ luật."));
      }
      renderTrace(result, data.trace);
    }
    const history = Object.entries(answers).map(([key, value]) => key + "=" + value);
    if (history.length) listFacts(result, "Câu trả lời đã ghi nhận", history);
    backwardResult.replaceChildren(result);
    const heading = result.querySelector("h3");
    heading.tabIndex = -1;
    heading.focus();
  });
}

function clearBackward() {
  answers = {};
  backwardResult.replaceChildren();
}

backward.addEventListener("submit", (event) => {
  event.preventDefault();
  clearBackward();
  backwardStep({});
});
backward.addEventListener("reset", clearBackward);
goal.addEventListener("change", clearBackward);

const search = document.querySelector("#search");
const ruleCount = document.querySelector("#rule-count");
const rules = [...document.querySelectorAll(".rule")];
const normalize = (value) => value.toLocaleLowerCase("vi").normalize("NFD")
  .replace(/\p{M}/gu, "").replaceAll("đ", "d");

function filterRules() {
  const query = normalize(search.value.trim());
  let count = 0;
  for (const rule of rules) {
    rule.hidden = !normalize(rule.textContent).includes(query);
    if (!rule.hidden) count += 1;
  }
  ruleCount.textContent = count + "/" + rules.length + " luật";
}

search.addEventListener("input", filterRules);
