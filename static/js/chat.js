// ChatGPT 응답을 레시피로 저장하는 함수
async function saveAsRecipe(question, answer) {
  // 사용자에게 레시피 제목 입력받기
  const title = prompt("레시피 제목을 입력하세요:", "김치찌개 레시피");

  if (!title || title.trim() === "") {
    alert("제목을 입력해주세요.");
    return;
  }

  const formData = new FormData();
  formData.append("title", title.trim());
  formData.append("content", answer);
  formData.append("original_question", question);

  try {
    // 저장 중 로딩 표시
    const saveButton = document.querySelector(".save-recipe-btn");
    if (saveButton) {
      saveButton.disabled = true;
      saveButton.textContent = "저장 중...";
    }

    const response = await fetch("/recipes/from-chat", {
      method: "POST",
      body: formData,
    });

    const result = await response.json();

    if (result.success) {
      alert(result.message);
      // 성공시 레시피 상세 페이지로 이동
      window.location.href = result.redirect_url;
    } else {
      alert("저장 실패: " + result.message);
    }
  } catch (error) {
    console.error("저장 오류:", error);
    alert("저장 중 오류가 발생했습니다: " + error.message);
  } finally {
    // 버튼 상태 복원
    const saveButton = document.querySelector(".save-recipe-btn");
    if (saveButton) {
      saveButton.disabled = false;
      saveButton.textContent = "레시피로 저장";
    }
  }
}

// ChatGPT API 호출 함수
async function sendChatMessage() {
  const questionInput = document.getElementById("question");
  const chatContainer = document.getElementById("chat-container");
  const sendButton = document.getElementById("send-button");

  if (!questionInput || !chatContainer) {
    console.error("필수 요소를 찾을 수 없습니다.");
    return;
  }

  const question = questionInput.value.trim();
  if (!question) {
    alert("질문을 입력해주세요.");
    return;
  }

  // 버튼 비활성화 및 로딩 표시
  if (sendButton) {
    sendButton.disabled = true;
    sendButton.textContent = "답변 기다리는 중...";
  }

  // 사용자 질문 표시
  addMessageToChat("user", question);
  questionInput.value = "";

  try {
    const response = await fetch("/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        question: question,
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();

    // ChatGPT 응답 표시 (저장 버튼 포함)
    addMessageToChat("assistant", data.answer, question);
  } catch (error) {
    console.error("채팅 오류:", error);
    addMessageToChat(
      "error",
      "죄송합니다. 오류가 발생했습니다: " + error.message
    );
  } finally {
    // 버튼 상태 복원
    if (sendButton) {
      sendButton.disabled = false;
      sendButton.textContent = "질문하기";
    }
  }
}

// 채팅 메시지를 화면에 추가하는 함수
function addMessageToChat(type, message, originalQuestion = null) {
  const chatContainer = document.getElementById("chat-container");
  if (!chatContainer) return;

  const messageDiv = document.createElement("div");
  messageDiv.className = `chat-message ${type}-message`;

  if (type === "user") {
    messageDiv.innerHTML = `
          <div class="message-content">
              <strong>나:</strong> ${escapeHtml(message)}
          </div>
      `;
  } else if (type === "assistant") {
    messageDiv.innerHTML = `
          <div class="message-content">
              <strong>ChatGPT:</strong> ${escapeHtml(message).replace(
                /\n/g,
                "<br>"
              )}
          </div>
          <div class="message-actions">
              <button class="save-recipe-btn" onclick="saveAsRecipe('${escapeHtml(
                originalQuestion
              )}', '${escapeHtml(message)}')">
                  📝 레시피로 저장
              </button>
          </div>
      `;
  } else if (type === "error") {
    messageDiv.innerHTML = `
          <div class="message-content error">
              <strong>오류:</strong> ${escapeHtml(message)}
          </div>
      `;
  }

  chatContainer.appendChild(messageDiv);
  chatContainer.scrollTop = chatContainer.scrollHeight;
}

// HTML 이스케이프 함수
function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}

// 엔터키로 메시지 전송
function handleKeyPress(event) {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    sendChatMessage();
  }
}

// 페이지 로드 시 이벤트 리스너 설정
document.addEventListener("DOMContentLoaded", function () {
  const questionInput = document.getElementById("question");
  const sendButton = document.getElementById("send-button");

  if (questionInput) {
    questionInput.addEventListener("keypress", handleKeyPress);
  }

  if (sendButton) {
    sendButton.addEventListener("click", sendChatMessage);
  }
});

// 채팅 기록 불러오기
async function loadChatHistory() {
  try {
    const response = await fetch("/chat/history");
    const data = await response.json();

    const chatContainer = document.getElementById("chat-container");
    if (!chatContainer) return;

    // 기존 메시지 지우기
    chatContainer.innerHTML = "";

    // 채팅 기록 표시
    if (data.history && data.history.length > 0) {
      data.history.forEach((chat) => {
        addMessageToChat("user", chat.question);
        addMessageToChat("assistant", chat.answer, chat.question);
      });
    } else {
      chatContainer.innerHTML =
        '<p class="no-history">아직 채팅 기록이 없습니다.</p>';
    }
  } catch (error) {
    console.error("채팅 기록 로드 오류:", error);
  }
}

// 채팅 기록 삭제
async function clearChatHistory() {
  if (!confirm("정말로 모든 채팅 기록을 삭제하시겠습니까?")) {
    return;
  }

  try {
    const response = await fetch("/chat/history", {
      method: "DELETE",
    });

    if (response.ok) {
      alert("채팅 기록이 삭제되었습니다.");
      const chatContainer = document.getElementById("chat-container");
      if (chatContainer) {
        chatContainer.innerHTML =
          '<p class="no-history">채팅 기록이 없습니다.</p>';
      }
    } else {
      alert("채팅 기록 삭제에 실패했습니다.");
    }
  } catch (error) {
    console.error("채팅 기록 삭제 오류:", error);
    alert("오류가 발생했습니다.");
  }
}
