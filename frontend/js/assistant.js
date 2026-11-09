/**
 * AI Business Assistant Controller
 * Connected to Google ADK Ecommerce Agent
 */

class AssistantController {
  constructor() {
    this.historyContainer = null;
    this.input = null;
    this.isProcessing = false;
  }

  init() {
    this.historyContainer = document.getElementById('assistant-chat-history');
    this.input = document.getElementById('assistant-input');
    this.bindEvents();
  }

  bindEvents() {
    const sendBtn = document.getElementById('btn-assistant-send');
    if (sendBtn) {
      sendBtn.addEventListener('click', () => this.sendMessage());
    }

    const clearBtn = document.getElementById('btn-clear-chat');
    if (clearBtn) {
      clearBtn.addEventListener('click', () => {
        this.clearChat();
        showToast('Chat history cleared', 'info');
      });
    }

    if (this.input) {
      this.input.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
          e.preventDefault();
          this.sendMessage();
        }
      });
    }

    // Quick chip prompts
    document.querySelectorAll('.quick-chip').forEach(chip => {
      chip.addEventListener('click', () => {
        if (this.input) {
          this.input.value = chip.getAttribute('data-prompt') || chip.innerText;
          this.sendMessage();
        }
      });
    });
  }

  appendMessage(role, text, toolCall = null) {
    if (!this.historyContainer) return;

    const bubble = document.createElement('div');
    bubble.className = `chat-bubble ${role}`;

    let html = `<div>${this.escapeHtml(text)}</div>`;
    if (toolCall) {
      html += `<div class="tool-execution-badge">↳ Tool: ${toolCall}</div>`;
    }

    bubble.innerHTML = html;
    this.historyContainer.appendChild(bubble);
    this.historyContainer.scrollTop = this.historyContainer.scrollHeight;
    return bubble;
  }

  escapeHtml(str) {
    const div = document.createElement('div');
    div.innerText = str;
    return div.innerHTML;
  }

  async sendMessage() {
    if (this.isProcessing || !this.input) return;
    const text = this.input.value.trim();
    if (!text) return;

    this.input.value = '';
    this.appendMessage('user', text);
    this.isProcessing = true;

    // Loading indicator bubble
    const loadingBubble = this.appendMessage('assistant', 'Consulting tools...');

    try {
      const response = await window.api.queryAssistant(text);
      loadingBubble.remove();
      this.appendMessage('assistant', response.reply || response.response, response.tool_used);
    } catch (err) {
      loadingBubble.remove();
      this.appendMessage('assistant', `Unable to complete request: ${err.message}`);
    } finally {
      this.isProcessing = false;
    }
  }

  clearChat(customGreeting = null) {
    if (!this.historyContainer) return;
    const greeting = customGreeting || "How can I help with store operations today? I can query products, inspect customer shopping carts, or summarize stock.";
    this.historyContainer.innerHTML = `
      <div class="chat-bubble system">
        Google ADK Ecommerce Agent • gemini-flash-lite-latest
      </div>
      <div class="chat-bubble assistant">
        ${this.escapeHtml(greeting)}
      </div>
    `;
    if (this.input) {
      this.input.value = '';
    }
  }
}

window.assistantController = new AssistantController();
