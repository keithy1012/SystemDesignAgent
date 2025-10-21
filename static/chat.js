async function sendMessage() {
  const input = document.getElementById("user-input");
  const chatBox = document.getElementById("chat-box");
  const userMessage = input.value.trim();
  if (!userMessage) return;

  chatBox.innerHTML += `<div class="text-end text-primary mb-2"><strong>You:</strong> ${userMessage}</div>`;
  input.value = "";

  const res = await fetch("/chat/send", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message: userMessage }),
  });

  const data = await res.json();

  if (data.ready) {
    chatBox.innerHTML += `<div class="text-success"><strong>AI:</strong> Got it! Generating system design...</div>`;
    setTimeout(() => {
      window.location.href = "/results";
    }, 1500);
  } else {
    chatBox.innerHTML += `<div class="text-secondary mb-2"><strong>AI:</strong> ${data.question}</div>`;
  }

  chatBox.scrollTop = chatBox.scrollHeight;
}
