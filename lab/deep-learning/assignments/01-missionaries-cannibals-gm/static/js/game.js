// =============================================
// game.js - 식인종/선교사 픽셀 게임 UI 로직
// AI 자동 모드 / 수동 모드 모두 지원
// =============================================

let currentMode    = "ai";   // "ai" | "manual"
let gameActive     = false;
let autoInterval   = null;
let validCommands  = [];
let commandNames   = {};
let currentBoatSide = "left";
let animatingTurn   = false;

const COMMAND_LOADS = {
  0: { m: 1, c: 0 },
  1: { m: 2, c: 0 },
  2: { m: 0, c: 1 },
  3: { m: 0, c: 2 },
  4: { m: 1, c: 1 },
};

// 픽셀 캐릭터 이모지
const CHAR_M = "🧑‍💼"; // 선교사
const CHAR_C = "👹";  // 식인종

// ── 모드 전환 ────────────────────────────────
function setMode(mode) {
  currentMode = mode;
  document.getElementById("btn-ai").classList.toggle("active", mode === "ai");
  document.getElementById("btn-manual").classList.toggle("active", mode === "manual");
  document.getElementById("ai-controls").classList.toggle("hidden", mode !== "ai");
  document.getElementById("manual-controls").classList.toggle("hidden", mode !== "manual");
}

// ── 게임 시작 ─────────────────────────────────
async function startGame() {
  stopAuto();
  const res  = await fetch("/api/start", { method: "POST" });
  const data = await res.json();

  gameActive    = true;
  validCommands = data.valid_commands;
  commandNames  = data.command_names;

  renderStatus(data.status);
  renderCommandBtns(validCommands);
  setTurn(0);
  clearLog();
  addLog("[ GAME START ] GM 준비 완료. 왼쪽: 선교사 3명, 식인종 3명", "system");
  setBoat("left");

  document.getElementById("btn-start").disabled = true;
  document.getElementById("btn-reset").disabled = false;
  document.getElementById("btn-next").disabled  = false;
  document.getElementById("btn-auto").disabled  = false;
  document.getElementById("overlay").classList.add("hidden");
}

// ── 게임 리셋 ─────────────────────────────────
function resetGame() {
  stopAuto();
  gameActive = false;
  document.getElementById("btn-start").disabled = false;
  document.getElementById("btn-reset").disabled = true;
  document.getElementById("btn-next").disabled  = true;
  document.getElementById("btn-auto").disabled  = true;
  document.getElementById("overlay").classList.add("hidden");
  renderStatus({ left_m:3, left_c:3, right_m:0, right_c:0, boat:"left" });
  setBoat("left");
  setTurn(0);
  clearLog();
  addLog("[ RESET ] START 버튼을 눌러 게임을 시작하세요.", "system");
  renderCommandBtns([]);
}

// ── AI 한 턴 진행 ──────────────────────────────
async function aiTurn() {
  if (!gameActive || animatingTurn) return;

  document.getElementById("btn-next").disabled = true;
  document.getElementById("btn-auto").disabled = true;

  const res  = await fetch("/api/ai_turn", { method: "POST" });
  const data = await res.json();

  handleTurnResult(data, "ai");
}

// ── 자동 플레이 ────────────────────────────────
function autoPlay() {
  if (autoInterval) {
    stopAuto();
    return;
  }
  document.getElementById("btn-auto").textContent = "⏹ STOP";
  // 1.5초 간격으로 AI 턴 자동 실행
  autoInterval = setInterval(async () => {
    if (!gameActive) { stopAuto(); return; }
    if (animatingTurn) return;
    const res  = await fetch("/api/ai_turn", { method: "POST" });
    const data = await res.json();
    handleTurnResult(data, "ai");
    if (data.result !== "continue") stopAuto();
  }, 1500);
}

function stopAuto() {
  if (autoInterval) {
    clearInterval(autoInterval);
    autoInterval = null;
  }
  const btn = document.getElementById("btn-auto");
  if (btn) btn.textContent = "⏩ AUTO PLAY";
}

// ── 수동 커맨드 실행 ───────────────────────────
async function manualCommand(cmdId) {
  if (!gameActive || animatingTurn) return;

  const res  = await fetch("/api/manual_turn", {
    method:  "POST",
    headers: { "Content-Type": "application/json" },
    body:    JSON.stringify({ command: cmdId }),
  });
  const data = await res.json();
  handleTurnResult(data, "manual");
}

// ── 턴 결과 처리 ──────────────────────────────
function handleTurnResult(data, mode) {
  if (data.error) {
    addLog(`[ ERROR ] ${data.error}`, "over");
    return;
  }

  animatingTurn = true;
  setTurn(data.turn);

  const prefix = mode === "ai" ? "🤖 GM" : "🎮 PLAYER";
  addLog(`[ TURN ${data.turn} ] ${prefix} → ${data.cmd_name}`, mode);
  if (data.comment) addLog(`  💬 ${data.comment}`, mode);

  animateBoatMove(data.command, data.status.boat, () => {
    renderStatus(data.status);
    setBoat(data.status.boat);
    clearBoatPassengers();
    animatingTurn = false;

    if (data.result === "win") {
      addLog("[ WIN! ] 모두 오른쪽으로 이동 성공! 🎉", "win");
      showOverlay("win", data.turn);
      gameActive = false;
    } else if (data.result === "gameover") {
      addLog("[ GAME OVER ] 선교사가 위험에 처했습니다... 💀", "over");
      showOverlay("over", data.turn);
      gameActive = false;
    } else {
      validCommands = data.valid_commands || [];
      renderCommandBtns(validCommands);
      document.getElementById("btn-next").disabled = false;
      document.getElementById("btn-auto").disabled = false;
    }
  });
}

// ── 상태 렌더링 ────────────────────────────────
function renderStatus(s) {
  document.getElementById("left-m").textContent  = s.left_m;
  document.getElementById("left-c").textContent  = s.left_c;
  document.getElementById("right-m").textContent = s.right_m;
  document.getElementById("right-c").textContent = s.right_c;

  // 픽셀 캐릭터 렌더링
  renderChars("chars-left",  s.left_m,  s.left_c);
  renderChars("chars-right", s.right_m, s.right_c);
}

function renderChars(areaId, mCount, cCount) {
  const area = document.getElementById(areaId);
  area.innerHTML = "";
  for (let i = 0; i < mCount; i++) {
    const el = document.createElement("span");
    el.className = "char-m";
    el.textContent = CHAR_M;
    area.appendChild(el);
  }
  for (let i = 0; i < cCount; i++) {
    const el = document.createElement("span");
    el.className = "char-c";
    el.textContent = CHAR_C;
    area.appendChild(el);
  }
}

// ── 배 위치 애니메이션 ─────────────────────────
function setBoat(side) {
  const wrap  = document.getElementById("boat-wrap");
  const label = document.getElementById("boat-label");
  wrap.className = `boat-wrap boat-${side}`;
  label.textContent = side === "left" ? "◀ BOAT" : "BOAT ▶";
  currentBoatSide = side;
}

function setBoatPassengers(cmdId) {
  const area = document.getElementById("boat-passengers");
  area.innerHTML = "";
  const load = COMMAND_LOADS[cmdId] || { m: 0, c: 0 };
  for (let i = 0; i < load.m; i++) {
    const el = document.createElement("span");
    el.className = "char-m";
    el.textContent = CHAR_M;
    area.appendChild(el);
  }
  for (let i = 0; i < load.c; i++) {
    const el = document.createElement("span");
    el.className = "char-c";
    el.textContent = CHAR_C;
    area.appendChild(el);
  }
}

function clearBoatPassengers() {
  document.getElementById("boat-passengers").innerHTML = "";
}

function animateBoatMove(cmdId, targetSide, done) {
  const startSide = currentBoatSide;
  setBoat(startSide);
  setBoatPassengers(cmdId);
  window.setTimeout(() => setBoat(targetSide), 80);
  window.setTimeout(done, 1080);
}

// ── 커맨드 버튼 렌더링 ─────────────────────────
function renderCommandBtns(validList) {
  const container = document.getElementById("cmd-btns");
  container.innerHTML = "";
  const allCmds = { 0:"선교사 1명", 1:"선교사 2명", 2:"식인종 1명", 3:"식인종 2명", 4:"선교사+식인종" };
  Object.entries(allCmds).forEach(([id, name]) => {
    const btn = document.createElement("button");
    btn.className   = "cmd-btn";
    btn.textContent = `[${id}] ${name}`;
    btn.disabled    = !validList.includes(parseInt(id));
    btn.onclick     = () => manualCommand(parseInt(id));
    container.appendChild(btn);
  });
}

// ── 로그 ──────────────────────────────────────
function addLog(msg, type = "system") {
  const body = document.getElementById("log-body");
  const line = document.createElement("p");
  line.className   = `log-line ${type}`;
  line.textContent = msg;
  body.appendChild(line);
  body.scrollTop = body.scrollHeight;
}

function clearLog() {
  document.getElementById("log-body").innerHTML = "";
}

// ── 턴 카운터 ──────────────────────────────────
function setTurn(n) {
  document.getElementById("turn-num").textContent = n;
}

// ── 결과 오버레이 ──────────────────────────────
function showOverlay(result, turns) {
  const overlay = document.getElementById("overlay");
  const icon    = document.getElementById("overlay-icon");
  const msg     = document.getElementById("overlay-msg");

  if (result === "win") {
    icon.textContent = "🏆";
    msg.innerHTML    = `MISSION COMPLETE!<br>${turns} TURNS`;
    msg.style.color  = "#00e676";
  } else {
    icon.textContent = "💀";
    msg.innerHTML    = `GAME OVER...<br>${turns} TURNS`;
    msg.style.color  = "#ff1744";
  }
  overlay.classList.remove("hidden");
}

// ── 초기 렌더링 ────────────────────────────────
renderStatus({ left_m:3, left_c:3, right_m:0, right_c:0, boat:"left" });
setBoat("left");
setMode("ai");
