const $ = (id) => document.getElementById(id);
const EMPTY_PROMPT = "아직 프롬프트가 없습니다.";

function addBubble(role, text) {
  const article = document.createElement("article");
  article.className = `bubble ${role}`;
  const inner = document.createElement("div");
  inner.className = "bubble-inner";
  inner.textContent = text;
  article.appendChild(inner);
  $("chat-log").appendChild(article);
  $("chat-log").scrollTop = $("chat-log").scrollHeight;
}

function setBusy(isBusy, message) {
  $("send-btn").disabled = isBusy;
  const headerGenerate = $("generate-btn");
  if (headerGenerate) headerGenerate.disabled = isBusy;
  const inlineGenerate = $("generate-btn-inline");
  if (inlineGenerate) inlineGenerate.disabled = isBusy;
  $("message-input").disabled = isBusy;
  $("toast").textContent = message || "처리 중입니다.";
  $("toast").classList.toggle("hidden", !isBusy);
  document.body.classList.toggle("is-busy", isBusy);
}

function setDownloadReady(url) {
  const button = $("download-btn");
  button.dataset.url = url || "";
  button.classList.toggle("hidden", !url);
}

function showNotice(message) {
  $("toast").textContent = message;
  $("toast").classList.remove("hidden");
  window.setTimeout(() => $("toast").classList.add("hidden"), 2400);
}

async function postJson(url, payload = {}) {
  const response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  const data = await response.json();
  if (!response.ok) throw data;
  return data;
}

function imageSettings() {
  return {
    negative_prompt: $("negative-input").value.trim(),
    width: Number($("width-input").value),
    height: Number($("height-input").value),
    steps: Number($("steps-input").value),
    cfg: Number($("cfg-input").value),
  };
}

function setDrawer(open) {
  $("side-drawer").classList.toggle("is-open", open);
  $("drawer-backdrop").classList.toggle("hidden", !open);
  $("side-toggle").setAttribute("aria-expanded", String(open));
}

function resizeComposer() {
  const input = $("message-input");
  input.style.height = "auto";
  input.style.height = `${Math.min(input.scrollHeight, 180)}px`;
}

function closeGate(shouldFocus = true) {
  $("opening-gate").classList.add("is-hidden");
  if (shouldFocus) {
    window.setTimeout(() => $("message-input").focus({ preventScroll: true }), 360);
  }
}

async function downloadCurrentImage() {
  const url = $("download-btn").dataset.url || $("result-img").src;
  if (!url) {
    showNotice("다운로드할 이미지가 없습니다.");
    return;
  }

  try {
    const response = await fetch(url);
    const blob = await response.blob();
    const objectUrl = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = objectUrl;
    anchor.download = `prompt-canvas-${Date.now()}.png`;
    document.body.appendChild(anchor);
    anchor.click();
    anchor.remove();
    URL.revokeObjectURL(objectUrl);
  } catch (error) {
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = `prompt-canvas-${Date.now()}.png`;
    anchor.target = "_blank";
    document.body.appendChild(anchor);
    anchor.click();
    anchor.remove();
  }
}

async function refreshStatus() {
  try {
    const data = await fetch("/api/status").then((res) => res.json());
    $("ollama-status").textContent = data.ollama.ok ? data.ollama.active_model : "offline";
    $("ollama-status").className = data.ollama.ok ? "ok" : "fail";
    $("comfy-status").textContent = data.comfyui.ok ? `${data.comfyui.checkpoints.length} model` : "offline";
    $("comfy-status").className = data.comfyui.ok ? "ok" : "fail";
    $("model-badge").textContent = `model : ${data.model}`;
  } catch (error) {
    $("ollama-status").textContent = "offline";
    $("ollama-status").className = "fail";
    $("comfy-status").textContent = "offline";
    $("comfy-status").className = "fail";
  }
}

async function sendMessage(event) {
  event.preventDefault();
  const message = $("message-input").value.trim();
  if (!message) {
    showNotice("메시지를 입력해 주세요.");
    return;
  }

  addBubble("user", message);
  $("message-input").value = "";
  resizeComposer();
  setBusy(true, "이미지 요구사항을 최종 프롬프트로 정리하는 중입니다.");

  try {
    const data = await postJson("/api/chat", { message });
    addBubble("assistant", data.reply);
    $("current-prompt").textContent = data.current_prompt;
    $("prompt-state").textContent = "업데이트됨";
  } catch (error) {
    addBubble("assistant", error.message || "프롬프트 정리에 실패했습니다.");
  } finally {
    setBusy(false);
  }
}

async function generateImage() {
  const prompt = $("current-prompt").textContent.trim();
  if (!prompt || prompt === EMPTY_PROMPT) {
    showNotice("먼저 대화로 생성할 이미지 설명을 정리해 주세요.");
    return;
  }

  $("result-img").classList.add("hidden");
  $("image-empty").classList.remove("hidden");
  setDownloadReady("");
  setBusy(true, "ComfyUI가 이미지를 생성하는 중입니다.");

  try {
    const data = await postJson("/api/generate", { prompt, ...imageSettings() });
    $("result-img").onload = () => {
      $("image-empty").classList.add("hidden");
      $("result-img").classList.remove("hidden");
      setDownloadReady(data.image_url);
      $("result-img").scrollIntoView({ behavior: "smooth", block: "center" });
    };
    $("result-img").onerror = () => {
      $("result-img").classList.add("hidden");
      $("image-empty").classList.remove("hidden");
      showNotice("생성된 이미지를 불러오지 못했습니다.");
    };
    $("result-img").src = data.image_url;
    $("prompt-id").textContent = data.prompt_id;
    $("result-meta").classList.remove("hidden");
    addHistoryThumb(data.image_url);
  } catch (error) {
    showNotice(error.message || "이미지 생성에 실패했습니다.");
  } finally {
    setBusy(false);
  }
}

function addHistoryThumb(url) {
  const button = document.createElement("button");
  button.type = "button";
  button.className = "history-thumb";
  button.dataset.url = url;
  const img = document.createElement("img");
  img.src = url;
  img.alt = "최근 생성 이미지";
  button.appendChild(img);
  $("image-history").prepend(button);
}

async function clearConversation() {
  await postJson("/api/clear");
  $("chat-log").innerHTML = "";
  addBubble("assistant", "초기화되었습니다. 새 이미지 요구사항을 입력해 주세요.");
  $("current-prompt").textContent = EMPTY_PROMPT;
  $("prompt-state").textContent = "비어 있음";
  $("result-img").classList.add("hidden");
  $("image-empty").classList.remove("hidden");
  $("result-meta").classList.add("hidden");
  setDownloadReady("");
  $("image-history").innerHTML = "";
  setDrawer(false);
}

function bootMotionField() {
  const canvas = $("motion-field");
  if (!canvas) return;
  const ctx = canvas.getContext("2d");
  const particles = Array.from({ length: 128 }, (_, index) => ({
    seed: index * 29,
    x: Math.random(),
    y: Math.random(),
    r: 1 + Math.random() * 4.2,
    s: 0.18 + Math.random() * 0.8,
  }));
  let width = 0;
  let height = 0;
  let pointerX = 0.5;
  let pointerY = 0.5;

  function resize() {
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    width = window.innerWidth;
    height = window.innerHeight;
    canvas.width = Math.floor(width * dpr);
    canvas.height = Math.floor(height * dpr);
    canvas.style.width = `${width}px`;
    canvas.style.height = `${height}px`;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  }

  function draw(time) {
    ctx.clearRect(0, 0, width, height);
    ctx.globalCompositeOperation = "lighter";
    particles.forEach((particle) => {
      const drift = time * 0.00008 * particle.s;
      const x = ((particle.x + drift + pointerX * 0.022) % 1) * width;
      const y = ((particle.y + Math.sin(drift * 8 + particle.seed) * 0.04 + pointerY * 0.016) % 1) * height;
      ctx.beginPath();
      ctx.fillStyle = particle.seed % 4 === 0 ? "rgba(247,241,223,.52)" : "rgba(255,59,22,.92)";
      ctx.arc(x, y, particle.r, 0, Math.PI * 2);
      ctx.fill();
    });
    ctx.globalCompositeOperation = "source-over";
    window.requestAnimationFrame(draw);
  }

  window.addEventListener("resize", resize);
  window.addEventListener("pointermove", (event) => {
    pointerX = event.clientX / Math.max(width, 1);
    pointerY = event.clientY / Math.max(height, 1);
    const tiltX = (pointerX - 0.5) * 100;
    const tiltY = (pointerY - 0.5) * 100;
    document.documentElement.style.setProperty("--tilt-x", tiltX.toFixed(2));
    document.documentElement.style.setProperty("--tilt-y", tiltY.toFixed(2));
  });
  resize();
  window.requestAnimationFrame(draw);
}

function bootLightning(canvasId, options = {}) {
  const canvas = $(canvasId);
  if (!canvas) return;
  const ctx = canvas.getContext("2d");
  const bolts = [];
  const config = {
    interval: options.interval || 520,
    burstChance: options.burstChance || 0.36,
    maxBolts: options.maxBolts || 7,
    color: options.color || "255,59,22",
    secondaryColor: options.secondaryColor || "247,241,223",
    lineWidth: options.lineWidth || 3,
    branchChance: options.branchChance || 0.32,
    zone: options.zone || "full",
  };
  let width = 0;
  let height = 0;
  let lastStrike = 0;

  function resize() {
    const rect = canvas.getBoundingClientRect();
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    width = Math.max(1, rect.width || window.innerWidth);
    height = Math.max(1, rect.height || window.innerHeight);
    canvas.width = Math.floor(width * dpr);
    canvas.height = Math.floor(height * dpr);
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  }

  function edgePoint(edge) {
    if (edge === 0) return { x: Math.random() * width, y: -20 };
    if (edge === 1) return { x: width + 20, y: Math.random() * height };
    if (edge === 2) return { x: Math.random() * width, y: height + 20 };
    return { x: -20, y: Math.random() * height };
  }

  function logoZone() {
    const title = document.querySelector(".hero-copy h2");
    const hero = document.querySelector(".hero-copy");
    const rect = title?.getBoundingClientRect();
    const heroRect = hero?.getBoundingClientRect();
    if (!rect || rect.width <= 0 || rect.height <= 0) {
      return {
        left: width * 0.04,
        top: height * 0.28,
        width: width * 0.28,
        height: height * 0.34,
      };
    }
    const padX = Math.max(24, rect.width * 0.1);
    const padY = Math.max(30, rect.height * 0.2);
    const left = Math.max(0, rect.left - padX);
    const rightLimit = heroRect ? Math.min(rect.right + padX, heroRect.right - 24) : rect.right + padX;
    const right = Math.max(left + rect.width * 0.7, rightLimit);
    return {
      left,
      top: Math.max(0, rect.top - padY),
      width: Math.min(width - left, right - left),
      height: Math.min(height, rect.height + padY * 2),
    };
  }

  function zonePoint(zone, side) {
    const jitterX = (Math.random() - 0.5) * zone.width * 0.28;
    const jitterY = (Math.random() - 0.5) * zone.height * 0.28;
    if (side === "left") return { x: zone.left + zone.width * 0.02, y: zone.top + zone.height * (0.18 + Math.random() * 0.64) + jitterY };
    if (side === "right") return { x: zone.left + zone.width * 0.9, y: zone.top + zone.height * (0.18 + Math.random() * 0.64) + jitterY };
    if (side === "top") return { x: zone.left + zone.width * (0.16 + Math.random() * 0.68) + jitterX, y: zone.top + zone.height * 0.02 };
    return { x: zone.left + zone.width * (0.16 + Math.random() * 0.68) + jitterX, y: zone.top + zone.height * 0.98 };
  }

  function makePath(start, end, segments, chaos) {
    const points = [];
    const dx = end.x - start.x;
    const dy = end.y - start.y;
    const length = Math.hypot(dx, dy) || 1;
    const normalX = -dy / length;
    const normalY = dx / length;
    let offset = 0;
    for (let i = 0; i <= segments; i += 1) {
      const t = i / segments;
      offset += (Math.random() - 0.5) * chaos;
      const taper = Math.sin(t * Math.PI);
      points.push({
        x: start.x + dx * t + normalX * offset * taper + (Math.random() - 0.5) * chaos * 0.35,
        y: start.y + dy * t + normalY * offset * taper + (Math.random() - 0.5) * chaos * 0.35,
      });
    }
    return points;
  }

  function makeSkillPath(zone) {
    const sides = ["left", "right", "top", "bottom"];
    const startSide = sides[Math.floor(Math.random() * sides.length)];
    const endSide = sides.filter((side) => side !== startSide)[Math.floor(Math.random() * 3)];
    const start = zonePoint(zone, startSide);
    const end = zonePoint(zone, endSide);
    const center = {
      x: zone.left + zone.width * (0.38 + Math.random() * 0.25),
      y: zone.top + zone.height * (0.35 + Math.random() * 0.28),
    };
    const points = [start];
    const segments = 10 + Math.floor(Math.random() * 8);
    const swirl = (Math.random() > 0.5 ? 1 : -1) * (0.8 + Math.random() * 0.6);

    for (let i = 1; i < segments; i += 1) {
      const t = i / segments;
      const eased = t * t * (3 - 2 * t);
      const baseX = start.x + (end.x - start.x) * eased;
      const baseY = start.y + (end.y - start.y) * eased;
      const orbit = Math.sin(t * Math.PI * (1.4 + Math.random() * 0.55));
      const bendX = (center.x - baseX) * 0.38 * Math.sin(t * Math.PI);
      const bendY = (center.y - baseY) * 0.34 * Math.sin(t * Math.PI);
      const slashX = Math.cos(t * Math.PI * 2.5) * zone.width * 0.055 * swirl;
      const slashY = orbit * zone.height * 0.12 * swirl;
      points.push({
        x: baseX + bendX + slashX + (Math.random() - 0.5) * zone.width * 0.045,
        y: baseY + bendY + slashY + (Math.random() - 0.5) * zone.height * 0.055,
      });
    }
    points.push(end);
    return points;
  }

  function spawnBolt() {
    const isLogoSkill = config.zone === "hero-logo";
    const zone = isLogoSkill ? logoZone() : null;
    const path = isLogoSkill
      ? makeSkillPath(zone)
      : (() => {
          const startEdge = Math.floor(Math.random() * 4);
          const endEdge = (startEdge + 1 + Math.floor(Math.random() * 3)) % 4;
          const start = edgePoint(startEdge);
          const end = Math.random() > 0.32
            ? edgePoint(endEdge)
            : { x: width * (0.2 + Math.random() * 0.6), y: height * (0.18 + Math.random() * 0.64) };
          const segments = 8 + Math.floor(Math.random() * 9);
          const chaos = Math.max(width, height) * (0.035 + Math.random() * 0.045);
          return makePath(start, end, segments, chaos);
        })();
    const chaos = isLogoSkill ? Math.min(zone.width, zone.height) * 0.22 : Math.max(width, height) * 0.04;
    const branches = [];
    const sparks = [];
    path.forEach((point, index) => {
      if (index < 2 || index > path.length - 3 || Math.random() > config.branchChance) return;
      const angle = Math.random() * Math.PI * 2;
      const distance = (isLogoSkill ? Math.min(zone.width, zone.height) : Math.min(width, height)) * (0.08 + Math.random() * 0.18);
      branches.push(makePath(point, {
        x: point.x + Math.cos(angle) * distance,
        y: point.y + Math.sin(angle) * distance,
      }, 3 + Math.floor(Math.random() * 4), chaos * 0.42));
      if (isLogoSkill) {
        sparks.push({
          x: point.x,
          y: point.y,
          angle: angle + (Math.random() - 0.5) * 1.4,
          length: 12 + Math.random() * 38,
        });
      }
    });
    bolts.push({
      kind: isLogoSkill ? "skill-slash" : "lightning",
      path,
      branches,
      sparks,
      born: performance.now(),
      life: isLogoSkill ? 170 + Math.random() * 170 : 95 + Math.random() * 150,
      width: config.lineWidth * (0.7 + Math.random() * 1.2),
      flash: Math.random() > 0.42,
    });
    if (bolts.length > config.maxBolts) bolts.shift();
  }

  function strokePath(points, alpha, lineWidth, rgb) {
    if (points.length < 2) return;
    ctx.beginPath();
    ctx.moveTo(points[0].x, points[0].y);
    for (let i = 1; i < points.length; i += 1) {
      const prev = points[i - 1];
      const point = points[i];
      const midX = (prev.x + point.x) / 2;
      const midY = (prev.y + point.y) / 2;
      ctx.quadraticCurveTo(prev.x, prev.y, midX, midY);
    }
    const last = points[points.length - 1];
    ctx.lineTo(last.x, last.y);
    ctx.lineCap = "round";
    ctx.lineJoin = "round";
    ctx.strokeStyle = `rgba(${rgb},${alpha})`;
    ctx.lineWidth = lineWidth;
    ctx.stroke();
  }

  function strokeSkillSlash(points, alpha, baseWidth) {
    if (points.length < 2) return;
    const first = points[0];
    const last = points[points.length - 1];
    const gradient = ctx.createLinearGradient(first.x, first.y, last.x, last.y);
    gradient.addColorStop(0, `rgba(255,255,255,${alpha * 0.08})`);
    gradient.addColorStop(0.18, `rgba(255,84,30,${alpha * 0.94})`);
    gradient.addColorStop(0.52, `rgba(247,241,223,${alpha})`);
    gradient.addColorStop(0.82, `rgba(255,59,22,${alpha * 0.92})`);
    gradient.addColorStop(1, `rgba(255,255,255,${alpha * 0.05})`);

    strokePath(points, alpha * 0.2, baseWidth * 5.4, "255,59,22");
    strokePath(points, alpha * 0.34, baseWidth * 3.4, "255,112,54");

    ctx.save();
    ctx.shadowColor = `rgba(255,59,22,${alpha})`;
    ctx.shadowBlur = 26;
    ctx.strokeStyle = gradient;
    ctx.lineWidth = baseWidth * 2.1;
    ctx.lineCap = "round";
    ctx.lineJoin = "round";
    ctx.beginPath();
    ctx.moveTo(points[0].x, points[0].y);
    for (let i = 1; i < points.length; i += 1) {
      const prev = points[i - 1];
      const point = points[i];
      const midX = (prev.x + point.x) / 2;
      const midY = (prev.y + point.y) / 2;
      ctx.quadraticCurveTo(prev.x, prev.y, midX, midY);
    }
    ctx.lineTo(last.x, last.y);
    ctx.stroke();
    ctx.restore();

    strokePath(points, alpha * 0.9, Math.max(2, baseWidth * 0.62), "247,241,223");

    const afterImage = points.map((point, index) => ({
      x: point.x - 16 - index * 1.8,
      y: point.y + 10 + Math.sin(index) * 8,
    }));
    strokePath(afterImage, alpha * 0.18, baseWidth * 1.3, "255,59,22");
  }

  function draw(now) {
    ctx.clearRect(0, 0, width, height);
    if (now - lastStrike > config.interval * (0.45 + Math.random())) {
      spawnBolt();
      if (Math.random() < config.burstChance) window.setTimeout(spawnBolt, 40 + Math.random() * 90);
      lastStrike = now;
    }
    ctx.globalCompositeOperation = "lighter";
    for (let i = bolts.length - 1; i >= 0; i -= 1) {
      const bolt = bolts[i];
      const age = now - bolt.born;
      const alpha = Math.max(0, 1 - age / bolt.life);
      if (alpha <= 0) {
        bolts.splice(i, 1);
        continue;
      }
      if (bolt.kind === "skill-slash") {
        strokeSkillSlash(bolt.path, alpha, bolt.width * 5.6);
        bolt.branches.forEach((branch) => {
          strokePath(branch, alpha * 0.26, bolt.width * 1.8, config.color);
          strokePath(branch, alpha * 0.76, Math.max(1, bolt.width * 0.52), config.secondaryColor);
        });
        bolt.sparks?.forEach((spark) => {
          const x2 = spark.x + Math.cos(spark.angle) * spark.length;
          const y2 = spark.y + Math.sin(spark.angle) * spark.length;
          ctx.beginPath();
          ctx.moveTo(spark.x, spark.y);
          ctx.lineTo(x2, y2);
          ctx.strokeStyle = `rgba(${config.secondaryColor},${alpha * 0.68})`;
          ctx.lineWidth = Math.max(1, bolt.width * 0.46);
          ctx.stroke();
        });
        continue;
      }
      strokePath(bolt.path, alpha * 0.18, bolt.width * 4.8, config.color);
      strokePath(bolt.path, alpha * 0.58, bolt.width * 2.5, config.color);
      strokePath(bolt.path, alpha, Math.max(1, bolt.width * 0.72), config.secondaryColor);
      bolt.branches.forEach((branch) => {
        strokePath(branch, alpha * 0.44, bolt.width * 1.4, config.color);
        strokePath(branch, alpha * 0.92, Math.max(1, bolt.width * 0.42), config.secondaryColor);
      });
      bolt.sparks?.forEach((spark) => {
        const x2 = spark.x + Math.cos(spark.angle) * spark.length;
        const y2 = spark.y + Math.sin(spark.angle) * spark.length;
        ctx.beginPath();
        ctx.moveTo(spark.x, spark.y);
        ctx.lineTo(x2, y2);
        ctx.strokeStyle = `rgba(${config.secondaryColor},${alpha * 0.82})`;
        ctx.lineWidth = Math.max(1, bolt.width * 0.35);
        ctx.stroke();
      });
    }
    ctx.globalCompositeOperation = "source-over";
    window.requestAnimationFrame(draw);
  }

  window.addEventListener("resize", resize);
  resize();
  window.requestAnimationFrame(draw);
}

document.querySelectorAll(".prompt-chip").forEach((button) => {
  button.addEventListener("click", () => {
    $("message-input").value = button.dataset.prompt;
    $("message-input").focus();
    resizeComposer();
    setDrawer(false);
  });
});

$("image-history").addEventListener("click", (event) => {
  const button = event.target.closest(".history-thumb");
  if (!button) return;
  $("result-img").src = button.dataset.url;
  $("image-empty").classList.add("hidden");
  $("result-img").classList.remove("hidden");
  setDownloadReady(button.dataset.url);
});

$("enter-studio").addEventListener("click", closeGate);
$("opening-gate").addEventListener("keydown", (event) => {
  if (event.key === "Enter" || event.key === " ") closeGate();
});
$("side-toggle").addEventListener("click", () => setDrawer(!$("side-drawer").classList.contains("is-open")));
$("side-close").addEventListener("click", () => setDrawer(false));
$("drawer-backdrop").addEventListener("click", () => setDrawer(false));
$("chat-form").addEventListener("submit", sendMessage);
if ($("generate-btn")) $("generate-btn").addEventListener("click", generateImage);
if ($("generate-btn-inline")) $("generate-btn-inline").addEventListener("click", generateImage);
$("download-btn").addEventListener("click", downloadCurrentImage);
$("clear-btn").addEventListener("click", clearConversation);
$("message-input").addEventListener("input", resizeComposer);

refreshStatus();
resizeComposer();
bootMotionField();
bootLightning("gate-lightning", {
  interval: 190,
  burstChance: 0.84,
  maxBolts: 14,
  lineWidth: 3.8,
  branchChance: 0.55,
});
if (window.location.hash === "#studio") {
  closeGate(false);
}

if (window.location.hash === "#drawer") {
  closeGate(false);
  setDrawer(true);
}
