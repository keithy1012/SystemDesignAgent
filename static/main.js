async function sendMessage() {
  const input = document.getElementById("user-input");
  const chatBox = document.getElementById("chat-box");
  const designSection = document.getElementById("design-section");
  const designContent = document.getElementById("design-content");
  const userMessage = input.value.trim();

  if (!userMessage) return;

  chatBox.innerHTML += `<div class="user-msg mb-2"><strong>You:</strong> ${userMessage}</div>`;
  input.value = "";
  chatBox.scrollTop = chatBox.scrollHeight;

  const res = await fetch("/chat/send", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message: userMessage }),
  });

  const data = await res.json();

  if (data.ready) {
    chatBox.innerHTML += `<div class="ai-msg mb-2"><strong>AI:</strong> Great! I have enough context. Generating design...</div>`;
    chatBox.scrollTop = chatBox.scrollHeight;

    setTimeout(() => {
      designSection.style.display = "block";
      designContent.innerHTML = `
        <pre>${JSON.stringify(data.design, null, 2)}</pre>
      `;
      chatBox.scrollTop = chatBox.scrollHeight;
    }, 1200);
  } else {
    chatBox.innerHTML += `<div class="ai-msg mb-2"><strong>AI:</strong> ${data.question}</div>`;
    chatBox.scrollTop = chatBox.scrollHeight;
  }
}
