const form = document.getElementById("chat-form");
const input = document.getElementById("input");
const sendBtn = document.getElementById("send");
const messagesEl = document.getElementById("messages");

const history = [];

function addMessage(role, text, opts = {}) {
  const wrap = document.createElement("div");
  wrap.className = `msg ${role}` + (opts.typing ? " typing" : "");
  const bubble = document.createElement("div");
  bubble.className = "bubble";
  bubble.textContent = text;
  wrap.appendChild(bubble);
  messagesEl.appendChild(wrap);
  messagesEl.scrollTop = messagesEl.scrollHeight;
  return wrap;
}

async function sendMessage(text) {
  addMessage("user", text);
  history.push({ role: "user", content: text });

  const typing = addMessage("bot", "Grok is thinking…", { typing: true });
  sendBtn.disabled = true;

  try {
    const resp = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ messages: history }),
    });
    const data = await resp.json();
    typing.remove();

    if (!resp.ok) {
      addMessage("bot", `⚠️ ${data.error || "Something went wrong."}`);
      return;
    }
    addMessage("bot", data.reply);
    history.push({ role: "assistant", content: data.reply });
  } catch (err) {
    typing.remove();
    addMessage("bot", `⚠️ Network error: ${err.message}`);
  } finally {
    sendBtn.disabled = false;
    input.focus();
  }
}

form.addEventListener("submit", (e) => {
  e.preventDefault();
  const text = input.value.trim();
  if (!text) return;
  input.value = "";
  sendMessage(text);
});
