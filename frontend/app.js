const API_URL = "http://127.0.0.1:8000";

const STORAGE_SESSIONS = "saw_sessions";
const STORAGE_ACTIVE = "saw_active_session";

let sessions = [];
let activeSessionId = null;

// ========================================
// INIT
// ========================================

document.addEventListener("DOMContentLoaded", () => {
  loadState();

  if (sessions.length === 0) {
    createSession();
  }

  if (!activeSessionId || !findSession(activeSessionId)) {
    activeSessionId = sessions[0].id;
  }

  renderHistoryList();
  renderMessages();
  bindUI();
});

function bindUI() {
  document.getElementById("new-session-btn")
    .addEventListener("click", () => createSession());

  document.getElementById("sidebar-toggle")
    .addEventListener("click", toggleSidebar);

  const textarea = document.getElementById("query");

  textarea.addEventListener("input", () => {
    textarea.style.height = "auto";
    textarea.style.height = Math.min(textarea.scrollHeight, 200) + "px";
  });

  textarea.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendQuery();
    }
  });
}

function toggleSidebar() {
  const panel = document.getElementById("history-panel");
  const toggle = document.getElementById("sidebar-toggle");
  const isOpen = panel.classList.toggle("is-open");
  toggle.setAttribute("aria-expanded", String(isOpen || window.innerWidth > 860));
}

// ========================================
// STATE / STORAGE
// ========================================

function loadState() {
  try {
    sessions = JSON.parse(localStorage.getItem(STORAGE_SESSIONS)) || [];
  } catch (e) {
    sessions = [];
  }
  activeSessionId = localStorage.getItem(STORAGE_ACTIVE);
}

function saveState() {
  localStorage.setItem(STORAGE_SESSIONS, JSON.stringify(sessions));
  localStorage.setItem(STORAGE_ACTIVE, activeSessionId);
}

function findSession(id) {
  return sessions.find(s => s.id === id);
}

function getActiveSession() {
  return findSession(activeSessionId);
}

function createSession() {
  const session = {
    id: "s_" + Date.now() + "_" + Math.random().toString(36).slice(2, 7),
    title: "New session",
    createdAt: Date.now(),
    messages: [{
      sender: "bot",
      text: "Hello! Ask me something about your documents, or upload an image or PDF for analysis.",
      time: Date.now(),
    }],
  };

  sessions.unshift(session);
  activeSessionId = session.id;
  saveState();
  renderHistoryList();
  renderMessages();
  setStatus("Ready", "idle");
  return session;
}

function selectSession(id) {
  activeSessionId = id;
  saveState();
  renderHistoryList();
  renderMessages();

  if (window.innerWidth <= 860) {
    document.getElementById("history-panel").classList.remove("is-open");
  }
}

// ========================================
// RENDERING: HISTORY
// ========================================

function renderHistoryList() {
  const list = document.getElementById("history-list");

  if (sessions.length === 0) {
    list.innerHTML = `<p class="history-empty">No sessions yet — send a message to start one.</p>`;
    return;
  }

  list.innerHTML = sessions.map(s => {
    const isActive = s.id === activeSessionId;
    return `
      <button class="history-item ${isActive ? "is-active" : ""}"
              data-id="${s.id}"
              ${isActive ? 'aria-current="true"' : ""}>
        <span class="history-title">${escapeHtml(s.title)}</span>
        <span class="history-meta">${formatMeta(s.createdAt)}</span>
      </button>
    `;
  }).join("");

  list.querySelectorAll(".history-item").forEach(item => {
    item.addEventListener("click", () => selectSession(item.dataset.id));
  });
}

function formatMeta(timestamp) {
  const d = new Date(timestamp);
  const today = new Date();
  const isToday = d.toDateString() === today.toDateString();
  const time = d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });

  if (isToday) return `Today · ${time}`;

  const yesterday = new Date(today);
  yesterday.setDate(today.getDate() - 1);
  if (d.toDateString() === yesterday.toDateString()) return `Yesterday · ${time}`;

  return `${d.toLocaleDateString([], { month: "short", day: "numeric" })} · ${time}`;
}

// ========================================
// RENDERING: MESSAGES
// ========================================

function renderMessages() {
  const chatBox = document.getElementById("chat-box");
  const session = getActiveSession();

  chatBox.innerHTML = "";

  if (!session) return;

  session.messages.forEach(msg => appendMessageToDOM(msg.sender, msg.text, msg.time));
  scrollChatToBottom();
}

function appendMessageToDOM(sender, text, time) {
  const chatBox = document.getElementById("chat-box");
  const wrapper = document.createElement("div");
  wrapper.className = `message ${sender}`;

  const avatarLabel = sender === "bot" ? "AI" : "You";
  const safeText = escapeHtml(text).replace(/\n/g, "<br>");

  wrapper.innerHTML = `
    <span class="msg-avatar">${avatarLabel}</span>
    <div class="msg-body">
      <div class="msg-bubble"><p>${safeText}</p></div>
      <span class="message-time">${formatTime(time)}</span>
    </div>
  `;

  chatBox.appendChild(wrapper);
  return wrapper;
}

function formatTime(timestamp) {
  return new Date(timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

function scrollChatToBottom() {
  const chatBox = document.getElementById("chat-box");
  chatBox.scrollTop = chatBox.scrollHeight;
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}

// ========================================
// MESSAGE HELPERS
// ========================================

function addMessage(sender, text) {
  const session = getActiveSession();
  if (!session) return;

  const time = Date.now();
  session.messages.push({ sender, text, time });

  if (sender === "user" && session.title === "New session") {
    session.title = text.length > 40 ? text.slice(0, 40) + "…" : text;
  }

  saveState();
  renderHistoryList();
  appendMessageToDOM(sender, text, time);
  scrollChatToBottom();
}

function showTypingIndicator() {
  const chatBox = document.getElementById("chat-box");
  const wrapper = document.createElement("div");
  wrapper.className = "message bot";
  wrapper.id = "typing-indicator";
  wrapper.innerHTML = `
    <span class="msg-avatar">AI</span>
    <div class="msg-body">
      <div class="msg-bubble">
        <span class="typing-dots"><span></span><span></span><span></span></span>
      </div>
    </div>
  `;
  chatBox.appendChild(wrapper);
  scrollChatToBottom();
}

function removeTypingIndicator() {
  const el = document.getElementById("typing-indicator");
  if (el) el.remove();
}

function setBusy(isBusy) {
  ["send-btn", "analyze-btn", "upload-btn"].forEach(id => {
    document.getElementById(id).disabled = isBusy;
  });
}

function setStatus(text, kind) {
  const status = document.getElementById("status");
  const pill = document.getElementById("connection-status");

  status.innerText = text;
  pill.classList.remove("busy", "error");

  if (kind === "busy") {
    pill.classList.add("busy");
    pill.innerText = "Working";
  } else if (kind === "error") {
    pill.classList.add("error");
    pill.innerText = "Error";
  } else {
    pill.innerText = "Ready";
  }
}

// ========================================
// NORMAL CHAT
// ========================================

async function sendQuery() {

    const input = document.getElementById("query");
    const query = input.value.trim();

    if (!query) {
        return;
    }

    addMessage("user", query);
    input.value = "";
    input.style.height = "auto";

    setBusy(true);
    setStatus("AI is processing your request...", "busy");
    showTypingIndicator();

    try {

        const response = await fetch(
            `${API_URL}/chat?query=${encodeURIComponent(query)}`,
            { method: "POST" }
        );

        if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
        }

        const data = await response.json();
        const jobId = data.job_id;

        setStatus("Agent is working...", "busy");

        await checkJob(jobId);

    } catch (error) {

        console.error(error);
        removeTypingIndicator();
        setStatus("Error connecting to server.", "error");

    } finally {
        setBusy(false);
    }
}

// ========================================
// IMAGE ANALYSIS
// ========================================

async function analyzeImage() {

    const input = document.getElementById("query");
    const imageInput = document.getElementById("image");

    const query = input.value.trim();
    const image = imageInput.files[0];

    if (!image) {
        setStatus("Please select an image.", "error");
        return;
    }

    if (!query) {
        setStatus("Please enter a question about the image.", "error");
        return;
    }

    addMessage("user", `🖼️ ${query}`);
    input.value = "";
    input.style.height = "auto";

    setBusy(true);
    setStatus("Uploading image...", "busy");
    showTypingIndicator();

    try {

        const formData = new FormData();
        formData.append("query", query);
        formData.append("image", image);

        const response = await fetch(
            `${API_URL}/vision-chat`,
            { method: "POST", body: formData }
        );

        if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
        }

        const data = await response.json();
        const jobId = data.job_id;

        setStatus("Vision Agent is analyzing the image...", "busy");

        await checkJob(jobId);

        imageInput.value = "";

    } catch (error) {

        console.error(error);
        removeTypingIndicator();
        setStatus("Error analyzing image.", "error");

    } finally {
        setBusy(false);
    }
}

// ========================================
// PDF UPLOAD
// ========================================

async function uploadPDF() {

    const pdfInput = document.getElementById("pdf");
    const pdf = pdfInput.files[0];

    if (!pdf) {
        setStatus("Please select a PDF.", "error");
        return;
    }

    setBusy(true);
    setStatus("Uploading and indexing PDF...", "busy");

    try {

        const formData = new FormData();
        formData.append("pdf", pdf);

        const response = await fetch(
            `${API_URL}/upload-pdf`,
            { method: "POST", body: formData }
        );

        if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
        }

        const data = await response.json();
        console.log("PDF response:", data);

        if (data.status === "success") {

            const result = data.result;

            addMessage(
                "bot",
                `📄 PDF uploaded successfully!\n\nFile: ${result.filename}\nPages: ${result.pages}\nChunks: ${result.chunks}\n\nYou can now ask questions about this PDF.`
            );

            setStatus("PDF indexed successfully.", "idle");

        } else {
            setStatus(data.message || "PDF upload failed.", "error");
        }

        pdfInput.value = "";

    } catch (error) {

        console.error(error);
        setStatus("Error uploading PDF.", "error");

    } finally {
        setBusy(false);
    }
}

// ========================================
// CHECK JOB STATUS
// ========================================

async function checkJob(jobId) {

    while (true) {

        try {

            const response = await fetch(
                `${API_URL}/job-status?job_id=${jobId}`
            );

            const data = await response.json();

            if (data.status === "finished") {

                removeTypingIndicator();
                addMessage("bot", data.result);
                setStatus("Completed", "idle");
                break;

            }

            if (data.status === "failed") {

                removeTypingIndicator();
                addMessage("bot", "Sorry, something went wrong while processing your request.");
                setStatus("Failed", "error");
                break;

            }

            setStatus("Agent is working...", "busy");

            await new Promise(resolve => setTimeout(resolve, 1500));

        } catch (error) {

            console.error(error);
            removeTypingIndicator();
            setStatus("Error checking job status.", "error");
            break;

        }

    }

}