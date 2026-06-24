const chatLog = document.getElementById("chat-log");
const chatForm = document.getElementById("chat-form");
const messageInput = document.getElementById("message-input");
const sendButton = document.getElementById("send-btn");
const clearButton = document.getElementById("clear-btn");
const drawerClearButton = document.getElementById("drawer-clear-btn");
const streamIndicator = document.getElementById("stream-indicator");
const modelBadge = document.getElementById("model-badge");
const historyCount = document.getElementById("history-count");
const drawerModel = document.getElementById("drawer-model");
const drawerHistory = document.getElementById("drawer-history");
const sideToggle = document.getElementById("side-toggle");
const sideClose = document.getElementById("side-close");
const sideDrawer = document.getElementById("side-drawer");
const drawerBackdrop = document.getElementById("drawer-backdrop");

let isStreaming = false;

function scrollToBottom() {
  chatLog.scrollTop = chatLog.scrollHeight;
}

function resizeInput() {
  messageInput.style.height = "auto";
  messageInput.style.height = `${Math.min(messageInput.scrollHeight, 208)}px`;
}

function setStreaming(active) {
  isStreaming = active;
  messageInput.disabled = active;
  sendButton.disabled = active;
  streamIndicator.classList.toggle("hidden", !active);
}

function setDrawer(open) {
  sideDrawer.classList.toggle("is-open", open);
  drawerBackdrop.classList.toggle("hidden", !open);
  sideToggle.setAttribute("aria-expanded", String(open));
}

function removeEmptyState() {
  const emptyState = document.getElementById("empty-state");
  if (emptyState) emptyState.remove();
}

function appendMessage(role, text = "", streaming = false) {
  removeEmptyState();

  const bubble = document.createElement("div");
  bubble.className = `bubble ${role === "user" ? "user" : "assistant"}${streaming ? " streaming" : ""}`;

  const inner = document.createElement("div");
  inner.className = "bubble-inner";
  inner.textContent = text;

  bubble.appendChild(inner);
  chatLog.appendChild(bubble);
  scrollToBottom();
  return { bubble, inner };
}

function parseSseBlock(block) {
  const eventLine = block.split("\n").find((line) => line.startsWith("event:"));
  const dataLine = block.split("\n").find((line) => line.startsWith("data:"));
  if (!eventLine || !dataLine) return null;

  try {
    return {
      event: eventLine.slice(6).trim(),
      data: JSON.parse(dataLine.slice(5).trim()),
    };
  } catch (error) {
    return {
      event: "error",
      data: { message: "Could not parse the streaming response." },
    };
  }
}

function syncStatusLabels(data) {
  const model = data.model || "unknown";
  const count = `${data.history_count || 0} messages`;
  modelBadge.textContent = `model : ${model}`;
  historyCount.textContent = count;
  drawerModel.textContent = model;
  drawerHistory.textContent = count;
}

async function refreshStatus() {
  try {
    const response = await fetch("/api/status");
    const data = await response.json();
    syncStatusLabels(data);
  } catch (error) {
    modelBadge.textContent = "model : offline";
    drawerModel.textContent = "offline";
  }
}

async function sendMessage(text) {
  const prompt = text.trim();
  if (!prompt || isStreaming) return;

  messageInput.value = "";
  resizeInput();
  appendMessage("user", prompt);
  const ai = appendMessage("assistant", "", true);
  setStreaming(true);

  try {
    const response = await fetch("/api/stream", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: prompt }),
    });

    if (!response.ok || !response.body) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.message || `HTTP ${response.status}`);
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder("utf-8");
    let buffer = "";

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const blocks = buffer.split("\n\n");
      buffer = blocks.pop() || "";

      for (const block of blocks) {
        const parsed = parseSseBlock(block);
        if (!parsed) continue;

        if (parsed.event === "open" && parsed.data.model) {
          modelBadge.textContent = `model : ${parsed.data.model}`;
          drawerModel.textContent = parsed.data.model;
        }

        if (parsed.event === "token") {
          ai.inner.textContent += parsed.data.text || "";
          scrollToBottom();
        }

        if (parsed.event === "error") {
          ai.inner.textContent = parsed.data.message || "Response generation failed.";
        }

        if (parsed.event === "end") {
          ai.bubble.classList.remove("streaming");
        }
      }
    }
  } catch (error) {
    ai.inner.textContent = `Connection error: ${error.message}`;
  } finally {
    ai.bubble.classList.remove("streaming");
    setStreaming(false);
    messageInput.focus();
    refreshStatus();
    scrollToBottom();
  }
}

async function clearHistory() {
  if (!window.confirm("Reset this session conversation?")) return;

  await fetch("/api/clear", { method: "POST" });
  chatLog.innerHTML = `
    <div class="welcome" id="empty-state">
      <p>StreamDesk</p>
      <span>Conversation reset. Send a new message to start streaming again.</span>
    </div>
  `;
  refreshStatus();
}

chatForm.addEventListener("submit", (event) => {
  event.preventDefault();
  sendMessage(messageInput.value);
});

messageInput.addEventListener("input", resizeInput);

messageInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    chatForm.requestSubmit();
  }
});

document.querySelectorAll(".prompt-chip").forEach((button) => {
  button.addEventListener("click", () => {
    messageInput.value = button.dataset.prompt || "";
    resizeInput();
    messageInput.focus();
    setDrawer(false);
  });
});

clearButton.addEventListener("click", clearHistory);
drawerClearButton.addEventListener("click", clearHistory);
sideToggle.addEventListener("click", () => setDrawer(!sideDrawer.classList.contains("is-open")));
sideClose.addEventListener("click", () => setDrawer(false));
drawerBackdrop.addEventListener("click", () => setDrawer(false));

document.addEventListener("keydown", (event) => {
  if (event.key === "Escape") setDrawer(false);
});

refreshStatus();
resizeInput();
scrollToBottom();

if (window.location.hash === "#setup") {
  setDrawer(true);
}
