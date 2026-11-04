/**
 * Products View Controller
 */

class ProductsController {
  constructor() {
    this.products = [];
    this.activeFilter = 'all';
  }

  async init() {
    this.bindEvents();
    await this.loadProducts();
  }

  bindEvents() {
    const refreshBtn = document.getElementById('btn-refresh-products');
    if (refreshBtn) {
      refreshBtn.addEventListener('click', () => this.loadProducts());
    }

    const searchInput = document.getElementById('product-table-search');
    if (searchInput) {
      searchInput.addEventListener('input', (e) => this.filterProducts(e.target.value));
    }

    const createBtn = document.getElementById('btn-create-product');
    const modal = document.getElementById('modal-create-product');
    const closeBtn = document.getElementById('btn-modal-close');
    const form = document.getElementById('form-create-product');

    if (createBtn && modal) {
      createBtn.addEventListener('click', () => {
        const user = window.api.getUserRole();
        if (user.role !== 'Admin') {
          showToast('Product creation requires Admin role (token-admin-01).', 'info');
        }
        modal.classList.add('active');
      });
    }

    if (closeBtn && modal) {
      closeBtn.addEventListener('click', () => modal.classList.remove('active'));
    }

    if (form) {
      form.addEventListener('submit', async (e) => {
        e.preventDefault();
        await this.handleCreateProduct(new FormData(form));
      });
    }
  }

  async loadProducts() {
    const tbody = document.getElementById('products-table-body');
    if (!tbody) return;

    tbody.innerHTML = `<tr><td colspan="6" style="text-align:center; padding:24px; color:var(--text-muted); font-size:0.82rem;">Loading catalog...</td></tr>`;

    try {
      this.products = await window.api.getProducts();
      this.renderTable(this.products);
    } catch (err) {
      tbody.innerHTML = `<tr><td colspan="6" style="text-align:center; padding:24px; color:var(--status-danger); font-size:0.82rem;">Failed to load products: ${err.message}</td></tr>`;
      showToast(err.message, 'error');
    }
  }

  renderTable(items) {
    const tbody = document.getElementById('products-table-body');
    if (!tbody) return;

    if (!items || items.length === 0) {
      tbody.innerHTML = `<tr><td colspan="6" style="text-align:center; padding:24px; color:var(--text-muted); font-size:0.82rem;">No products found</td></tr>`;
      return;
    }

    tbody.innerHTML = items.map(p => `
      <tr>
        <td style="color:var(--text-muted); font-family:var(--font-mono); font-size:0.75rem;">#${p.id || '—'}</td>
        <td>
          <div class="product-cell">
            <img src="${p.image || 'https://via.placeholder.com/32'}" class="table-img" alt="${p.title}" onerror="this.src='https://via.placeholder.com/32'">
            <div>
              <div style="font-weight:500; font-size:0.84rem; max-width:300px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">${p.title}</div>
              <div style="font-size:0.75rem; color:var(--text-muted); max-width:300px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">${p.description || ''}</div>
            </div>
          </div>
        </td>
        <td><span class="badge-category">${p.category}</span></td>
        <td style="font-family:var(--font-mono); font-size:0.82rem; font-weight:500;">$${parseFloat(p.price).toFixed(2)}</td>
        <td><span style="color:var(--status-active); font-size:0.75rem;">Active</span></td>
        <td>
          <button class="btn-secondary" style="padding:3px 8px; font-size:0.75rem;" onclick="window.productsController.viewDetail(${p.id})">Inspect</button>
        </td>
      </tr>
    `).join('');
  }

  filterProducts(query) {
    const q = (query || '').toLowerCase().trim();
    if (!q) {
      this.renderTable(this.products);
      return;
    }
    const filtered = this.products.filter(p => 
      p.title.toLowerCase().includes(q) || 
      p.category.toLowerCase().includes(q) ||
      (p.description && p.description.toLowerCase().includes(q))
    );
    this.renderTable(filtered);
  }

  async viewDetail(id) {
    try {
      const item = await window.api.getProductById(id);
      showToast(`Product #${item.id}: ${item.title} ($${item.price})`, 'info');
    } catch (err) {
      showToast(err.message, 'error');
    }
  }

  async handleCreateProduct(formData) {
    const payload = {
      title: formData.get('title'),
      price: parseFloat(formData.get('price')),
      description: formData.get('description'),
      category: formData.get('category'),
      image: formData.get('image') || 'https://fakestoreapi.com/img/placeholder.png'
    };

    try {
      const created = await window.api.createProduct(payload);
      showToast(`Product created: #${created.id}`, 'success');
      document.getElementById('modal-create-product').classList.remove('active');
      document.getElementById('form-create-product').reset();
      await this.loadProducts();
    } catch (err) {
      showToast(`Creation failed: ${err.message}`, 'error');
    }
  }
}

window.productsController = new ProductsController();
