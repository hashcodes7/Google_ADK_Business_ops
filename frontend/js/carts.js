/**
 * Carts & Orders View Controller
 */

class CartsController {
  constructor() {
    this.carts = [];
  }

  async init() {
    this.bindEvents();
    await this.loadCarts();
  }

  bindEvents() {
    const refreshBtn = document.getElementById('btn-refresh-carts');
    if (refreshBtn) {
      refreshBtn.addEventListener('click', () => this.loadCarts());
    }
  }

  async loadCarts() {
    const container = document.getElementById('carts-list-container');
    if (!container) return;

    container.innerHTML = `<div style="text-align:center; padding:24px; color:var(--text-muted); font-size:0.82rem;">Loading carts...</div>`;

    try {
      this.carts = await window.api.getCarts();
      this.renderCarts(this.carts);
    } catch (err) {
      container.innerHTML = `<div style="text-align:center; padding:24px; color:var(--status-danger); font-size:0.82rem;">Failed to load carts: ${err.message}</div>`;
      showToast(err.message, 'error');
    }
  }

  renderCarts(carts) {
    const container = document.getElementById('carts-list-container');
    if (!container) return;

    if (!carts || carts.length === 0) {
      container.innerHTML = `<div style="text-align:center; padding:24px; color:var(--text-muted); font-size:0.82rem;">No carts registered</div>`;
      return;
    }

    container.innerHTML = carts.map(cart => {
      const itemCount = (cart.products || []).reduce((acc, item) => acc + (item.quantity || 1), 0);
      const dateFormatted = cart.date ? new Date(cart.date).toLocaleDateString() : 'Recent';

      return `
        <div class="card-panel" style="margin-bottom:12px; display:flex; justify-content:space-between; align-items:center;">
          <div>
            <div style="display:flex; align-items:center; gap:8px; margin-bottom:4px;">
              <span style="font-weight:500; font-size:0.9rem; font-family:var(--font-mono);">Cart #${cart.id}</span>
              <span class="badge-category">User: ${cart.userId}</span>
              <span style="font-size:0.75rem; color:var(--text-muted);">${dateFormatted}</span>
            </div>
            <div style="font-size:0.78rem; color:var(--text-secondary);">
              Items: <strong>${itemCount}</strong> across ${(cart.products || []).length} distinct lines
            </div>
          </div>
          <div>
            <button class="btn-secondary" style="font-size:0.75rem; padding:4px 8px;" onclick="window.cartsController.inspectWithAI(${cart.id})">
              Audit with Agent
            </button>
          </div>
        </div>
      `;
    }).join('');
  }

  inspectWithAI(cartId) {
    const input = document.getElementById('assistant-input');
    if (input) {
      input.value = `Inspect cart #${cartId} and summarize items.`;
      const sendBtn = document.getElementById('btn-assistant-send');
      if (sendBtn) sendBtn.click();
    }
  }
}

window.cartsController = new CartsController();
