/**
 * Main Dashboard Controller
 * Orchestrates Lifecycle, Fallback Offline Detection, Authentication Gate,
 * KPIs, Charts, Navigation, and Topbar Profile
 */

function showToast(message, type = 'info') {
  const container = document.getElementById('toast-container');
  if (!container) return;

  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.innerText = message;
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(6px)';
    setTimeout(() => toast.remove(), 250);
  }, 3500);
}

class DashboardApp {
  constructor() {
    this.currentView = 'dashboard';
    this.isBackendOnline = false;
    this.isAuthenticated = false;
  }

  async init() {
    this.bindGlobalScreens();
    this.setupNavigation();
    this.setupProfileMenu();
    this.setupAuthSwitcher();
    this.setupSearch();

    // Check backend health & authenticate before showing dashboard
    await this.verifyBackendAndAuth();
  }

  bindGlobalScreens() {
    const retryBtn = document.getElementById('btn-retry-backend');
    if (retryBtn) {
      retryBtn.addEventListener('click', async () => {
        retryBtn.innerText = 'Checking...';
        await this.verifyBackendAndAuth();
        retryBtn.innerText = 'Retry Connection';
      });
    }

    const loginForm = document.getElementById('form-login');
    const loginError = document.getElementById('login-error-msg');
    if (loginForm) {
      loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const username = document.getElementById('login-username').value;
        const password = document.getElementById('login-password').value;
        loginError.style.display = 'none';

        try {
          await window.api.login(username, password);
          this.isAuthenticated = true;
          this.showMainApp();
          showToast(`Signed in as ${username}`, 'success');
        } catch (err) {
          loginError.innerText = err.message;
          loginError.style.display = 'block';
        }
      });
    }

    const logoutBtn = document.getElementById('btn-logout');
    if (logoutBtn) {
      logoutBtn.addEventListener('click', () => {
        window.api.logout();
        this.isAuthenticated = false;
        this.showAuthScreen();
      });
    }
  }

  async verifyBackendAndAuth() {
    const isOnline = await window.api.checkHealth();
    this.isBackendOnline = isOnline;

    if (!isOnline) {
      this.showOfflineScreen();
      return;
    }

    // Backend is online - check if we have a valid token
    const token = window.api.getToken();
    if (!token) {
      this.showAuthScreen();
    } else {
      this.isAuthenticated = true;
      this.showMainApp();
    }
  }

  showOfflineScreen() {
    document.getElementById('screen-offline').style.display = 'flex';
    document.getElementById('screen-auth').style.display = 'none';
    document.getElementById('main-app').style.display = 'none';
  }

  showAuthScreen() {
    document.getElementById('screen-offline').style.display = 'none';
    document.getElementById('screen-auth').style.display = 'flex';
    document.getElementById('main-app').style.display = 'none';
  }

  showMainApp() {
    document.getElementById('screen-offline').style.display = 'none';
    document.getElementById('screen-auth').style.display = 'none';
    document.getElementById('main-app').style.display = 'flex';

    // Refresh UI with authenticated user data
    this.updateUserUI();

    // Initialize sub-controllers
    if (window.productsController) window.productsController.init();
    if (window.cartsController) window.cartsController.init();
    if (window.assistantController) window.assistantController.init();

    this.refreshDashboardData();
  }

  updateUserUI() {
    const user = window.api.getUserRole();
    const roleBadge = document.getElementById('user-role-badge');
    const profileName = document.getElementById('user-profile-name');
    const profileRole = document.getElementById('user-profile-role');
    const userAvatar = document.getElementById('user-avatar');
    const dropdownUserDisplay = document.getElementById('dropdown-user-display');
    const select = document.getElementById('token-switch-select');

    if (roleBadge) {
      roleBadge.innerText = user.role;
      roleBadge.style.color = user.role === 'Admin' ? 'var(--status-admin)' : 'var(--status-active)';
      roleBadge.style.background = user.role === 'Admin' ? 'var(--status-admin-bg)' : 'var(--status-active-bg)';
    }
    if (profileName) profileName.innerText = user.name;
    if (profileRole) profileRole.innerText = `${user.role} Account`;
    if (userAvatar) userAvatar.innerText = (user.name || 'U').charAt(0).toUpperCase();
    if (dropdownUserDisplay) dropdownUserDisplay.innerText = `${user.name} • ${user.role} Role`;
    if (select) select.value = window.api.getToken();
  }

  setupProfileMenu() {
    const profileBtn = document.getElementById('btn-profile-toggle');
    const dropdown = document.getElementById('profile-dropdown');

    if (profileBtn && dropdown) {
      profileBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        const isOpen = dropdown.classList.contains('show');
        if (isOpen) {
          dropdown.classList.remove('show');
          profileBtn.classList.remove('active');
        } else {
          dropdown.classList.add('show');
          profileBtn.classList.add('active');
        }
      });

      // Prevent clicks inside the dropdown from closing it
      dropdown.addEventListener('click', (e) => {
        e.stopPropagation();
      });

      // Close dropdown when clicking outside
      document.addEventListener('click', () => {
        if (dropdown.classList.contains('show')) {
          dropdown.classList.remove('show');
          profileBtn.classList.remove('active');
        }
      });
    }
  }

  setupNavigation() {
    document.querySelectorAll('.nav-item').forEach(item => {
      item.addEventListener('click', (e) => {
        const targetView = item.getAttribute('data-view');
        // If it's an external link (like Swagger Docs without data-view), let default click happen
        if (!targetView) {
          return;
        }
        e.preventDefault();
        this.switchView(targetView);
      });
    });
  }

  switchView(viewName) {
    if (!viewName) return;
    this.currentView = viewName;

    document.querySelectorAll('.nav-item').forEach(el => {
      if (el.getAttribute('data-view') === viewName) {
        el.classList.add('active');
      } else {
        el.classList.remove('active');
      }
    });

    document.querySelectorAll('.view-section').forEach(sec => {
      if (sec.id === `view-${viewName}`) {
        sec.classList.add('active-view');
      } else {
        sec.classList.remove('active-view');
      }
    });

    if (viewName === 'products' && window.productsController) {
      window.productsController.loadProducts();
    } else if (viewName === 'orders' && window.cartsController) {
      window.cartsController.loadCarts();
    } else if (viewName === 'dashboard') {
      this.refreshDashboardData();
    }
  }

  setupAuthSwitcher() {
    const select = document.getElementById('token-switch-select');
    if (select) {
      select.addEventListener('change', (e) => {
        const newToken = e.target.value;
        const newRole = newToken === 'token-admin-01' ? { name: 'Admin_01', role: 'Admin' } : { name: 'User_49', role: 'Business' };
        window.api.setToken(newToken, newRole);
        this.updateUserUI();
        showToast(`Switched active context to ${select.options[select.selectedIndex].text}`, 'info');

        // Clear chat history upon switching users with an account-specific greeting
        if (window.assistantController) {
          const roleLabel = newRole.role;
          window.assistantController.clearChat(
            `Session switched to ${newRole.name} (${roleLabel} Role). What operations would you like to perform?`
          );
        }

        if (this.currentView === 'products') window.productsController.loadProducts();
        if (this.currentView === 'orders') window.cartsController.loadCarts();
      });
    }
  }

  setupSearch() {
    const globalSearch = document.getElementById('global-search-input');
    if (globalSearch) {
      globalSearch.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
          const val = globalSearch.value.trim();
          if (val) {
            this.switchView('products');
            const pSearch = document.getElementById('product-table-search');
            if (pSearch) {
              pSearch.value = val;
              if (window.productsController) window.productsController.filterProducts(val);
            }
          }
        }
      });
    }
  }

  async refreshDashboardData() {
    try {
      const [products, carts] = await Promise.all([
        window.api.getProducts().catch(() => []),
        window.api.getCarts().catch(() => [])
      ]);

      const totalRevenue = products.reduce((acc, p) => acc + (parseFloat(p.price) || 0) * 12, 0);
      const totalOrders = carts.length;
      const totalSKUs = products.length;

      const kpiRev = document.getElementById('kpi-revenue');
      const kpiOrders = document.getElementById('kpi-orders');
      const kpiProducts = document.getElementById('kpi-products');

      if (kpiRev) kpiRev.innerText = `$${totalRevenue.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
      if (kpiOrders) kpiOrders.innerText = totalOrders;
      if (kpiProducts) kpiProducts.innerText = totalSKUs;

      this.renderCharts(products);
    } catch (err) {
      console.warn('Dashboard data fetch warning:', err);
    }
  }

  renderCharts(products) {
    const chartContainer = document.getElementById('category-distribution-bar');
    if (!chartContainer || !products || products.length === 0) return;

    const counts = {};
    products.forEach(p => {
      counts[p.category] = (counts[p.category] || 0) + 1;
    });

    const entries = Object.entries(counts);
    const maxVal = Math.max(...Object.values(counts));

    chartContainer.innerHTML = entries.map(([category, count]) => {
      const pct = Math.round((count / maxVal) * 100);
      return `
        <div style="margin-bottom: 10px;">
          <div style="display:flex; justify-content:space-between; font-size:0.78rem; margin-bottom:3px;">
            <span style="text-transform:capitalize; color:var(--text-secondary);">${category}</span>
            <span style="font-weight:500; color:var(--text-primary);">${count} items</span>
          </div>
          <div style="height:6px; background:var(--bg-subtle); border-radius:3px; overflow:hidden;">
            <div style="width:${pct}%; height:100%; background:var(--text-secondary); border-radius:3px;"></div>
          </div>
        </div>
      `;
    }).join('');
  }
}

// Bootstrap on DOM Loaded
document.addEventListener('DOMContentLoaded', () => {
  window.dashboardApp = new DashboardApp();
  window.dashboardApp.init();
});
