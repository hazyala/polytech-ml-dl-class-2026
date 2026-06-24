const flowIds = ["flow-input", "flow-translate", "flow-comfy", "flow-result"];

const $ = (id) => document.getElementById(id);

function setFlow(activeIndex) {
  flowIds.forEach((id, index) => {
    const node = $(id);
    node.classList.toggle("active", index === activeIndex);
    node.classList.toggle("done", index < activeIndex);
  });
}

function setBusy(isBusy, title, text) {
  $("btn-translate").disabled = isBusy;
  $("btn-generate").disabled = isBusy;
  $("status-title").textContent = title;
  $("status-text").textContent = text;
  $("progress-track").classList.toggle("hidden", !isBusy);
}

function setRuntimeStatus(elementId, ok, label, detail = "") {
  const node = $(elementId);
  node.classList.remove("pending", "ok", "fail");
  node.classList.add(ok ? "ok" : "fail");
  node.textContent = detail ? `${label} · ${detail}` : label;
}

function requestPayload() {
  return {
    korean_input: $("korean-input").value.trim(),
    neg_prompt: $("neg-input").value.trim(),
    width: Number($("width-input").value),
    height: Number($("height-input").value),
    steps: Number($("steps-input").value),
    cfg: Number($("cfg-input").value),
  };
}

function showError(data) {
  const message = data.error || "요청을 처리하지 못했습니다.";
  setBusy(false, "확인이 필요해요", message);
  $("status-text").dataset.code = data.code || "UNKNOWN_ERROR";
}

async function postJson(url, payload) {
  const response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  const data = await response.json();
  if (!response.ok) throw data;
  return data;
}

async function checkHealth() {
  try {
    const response = await fetch("/api/health");
    const data = await response.json();
    const comfyDetail = data.comfyui.ok ? `${data.comfyui.checkpoints.length} model` : "checkpoint 필요";
    const ollamaDetail = data.ollama.ok ? data.ollama.active_model : "모델 확인 필요";
    setRuntimeStatus("comfy-status", data.comfyui.ok, "Image model", comfyDetail);
    setRuntimeStatus("ollama-status", data.ollama.ok, "Prompt AI", ollamaDetail);
  } catch (error) {
    setRuntimeStatus("comfy-status", false, "Image model", "오프라인");
    setRuntimeStatus("ollama-status", false, "Prompt AI", "오프라인");
  }
}

async function translateOnly() {
  const payload = requestPayload();
  if (!payload.korean_input) {
    setBusy(false, "프롬프트를 입력하세요", "만들고 싶은 장면을 한국어로 적어주세요.");
    setFlow(0);
    return;
  }

  setBusy(true, "프롬프트를 다듬는 중", "Prompt AI가 한국어 설명을 이미지 생성용 영어 문장으로 바꾸고 있어요.");
  setFlow(1);

  try {
    const data = await postJson("/api/translate_only", payload);
    $("eng-preview").textContent = data.eng_prompt;
    setBusy(false, "프롬프트 준비 완료", "영어 프롬프트가 준비됐어요. 이제 이미지 생성을 실행할 수 있습니다.");
    setFlow(2);
  } catch (error) {
    showError(error);
    setFlow(0);
  }
}

async function generateImage() {
  const payload = requestPayload();
  if (!payload.korean_input) {
    setBusy(false, "프롬프트를 입력하세요", "만들고 싶은 장면을 한국어로 적어주세요.");
    setFlow(0);
    return;
  }

  $("result-img").classList.add("hidden");
  $("image-empty").classList.remove("hidden");
  $("result-info").classList.add("hidden");
  $("download-link").classList.add("hidden");

  setBusy(true, "이미지를 생성하는 중", "번역된 프롬프트를 ComfyUI에 전달하고 결과를 기다리고 있어요.");
  setFlow(2);

  try {
    const data = await postJson("/api/generate", payload);
    $("eng-preview").textContent = data.eng_prompt;
    $("result-img").src = data.img_url;
    $("result-img").onload = () => {
      $("image-empty").classList.add("hidden");
      $("result-img").classList.remove("hidden");
    };

    $("info-id").textContent = data.prompt_id;
    $("info-kor").textContent = data.korean_input;
    $("info-eng").textContent = data.eng_prompt;
    $("download-link").href = data.img_url;
    $("download-link").classList.remove("hidden");
    $("result-info").classList.remove("hidden");

    addHistory(data);
    setBusy(false, "완성됐어요", "생성된 이미지를 미리보기 영역에 표시했습니다.");
    setFlow(3);
  } catch (error) {
    showError(error);
    setFlow(0);
  }
}

function addHistory(data) {
  const thumb = document.createElement("button");
  thumb.type = "button";
  thumb.className = "history-thumb";
  thumb.title = data.korean_input;

  const img = document.createElement("img");
  img.src = data.img_url;
  img.alt = data.korean_input;
  thumb.appendChild(img);
  thumb.addEventListener("click", () => {
    $("result-img").src = data.img_url;
    $("image-empty").classList.add("hidden");
    $("result-img").classList.remove("hidden");
  });

  $("history-list").prepend(thumb);
}

document.querySelectorAll(".prompt-chip").forEach((button) => {
  button.addEventListener("click", () => {
    $("korean-input").value = button.textContent.trim();
    $("korean-input").focus();
  });
});

$("btn-translate").addEventListener("click", translateOnly);
$("btn-generate").addEventListener("click", generateImage);

checkHealth();
