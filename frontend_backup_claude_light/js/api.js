/**
 * API Service Adapter for Business Operations Frontend
 * Connects directly to FastAPI backend with Bearer Authentication
 */

class ApiService {
  constructor() {
    // If opened via file:/// or an external port, connect directly to http://127.0.0.1:8000
    if (!window.location.origin || window.location.origin === 'null' || window.location.protocol === 'file:') {
      this.baseUrl = 'http://127.0.0.1:8000';
    } else if (window.location.port !== '8000') {
      this.baseUrl = 'http://127.0.0.1:8000';
    } else {
      this.baseUrl = window.location.origin;
    }
    
    this.token = localStorage.getItem('biz_ops_token') || 'token-business-49';
    this.currentUser = JSON.parse(localStorage.getItem('biz_ops_user') || 'null') || {
      name: 'User_49',
      role: 'Business'
    };
  }

  setToken(token, user = null) {
    this.token = token;
    localStorage.setItem('biz_ops_token', token);
    if (user) {
      this.currentUser = user;
      localStorage.setItem('biz_ops_user', JSON.stringify(user));
    }
  }

  getToken() {
    return this.token;
  }

  getUserRole() {
    if (this.currentUser) return this.currentUser;
    if (this.token === 'token-admin-01') return { name: 'Admin_01', role: 'Admin' };
    return { name: 'User_49', role: 'Business' };
  }

  logout() {
    this.token = '';
    this.currentUser = null;
    localStorage.removeItem('biz_ops_token');
    localStorage.removeItem('biz_ops_user');
  }

  async checkHealth() {
    try {
      const controller = new AbortController();
      const id = setTimeout(() => controller.abort(), 2500);
      const res = await fetch(`${this.baseUrl}/api/v1/health`, {
        signal: controller.signal
      });
      clearTimeout(id);
      return res.ok;
    } catch {
      return false;
    }
  }

  async login(username, password) {
    const res = await fetch(`${this.baseUrl}/api/v1/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password })
    });
    const data = await res.json();
    if (!res.ok) {
      throw new Error(data.error || data.detail || 'Authentication failed');
    }
    this.setToken(data.token, { name: data.user_id, role: data.role });
    return data;
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseUrl}${endpoint}`;
    const headers = {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${this.token}`,
      ...(options.headers || {})
    };

    try {
      const response = await fetch(url, { ...options, headers });
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || data.detail || `HTTP Error ${response.status}`);
      }

      return data;
    } catch (err) {
      console.error(`API Error [${endpoint}]:`, err);
      throw err;
    }
  }

  // Product Operations (Shared Channel)
  async getProducts() {
    return await this.request('/api/v1/products/');
  }

  async getProductById(id) {
    return await this.request(`/api/v1/products/${id}`);
  }

  async getProductsByCategory(category) {
    return await this.request(`/api/v1/products/category/${encodeURIComponent(category)}`);
  }

  async createProduct(productData) {
    return await this.request('/api/v1/products/', {
      method: 'POST',
      body: JSON.stringify(productData)
    });
  }

  // Cart Operations (Shared Channel)
  async getCarts() {
    return await this.request('/api/v1/carts/');
  }

  // User Operations (User-Only Channel - Admin Only)
  async createUser(userData) {
    return await this.request('/api/v1/users/', {
      method: 'POST',
      body: JSON.stringify(userData)
    });
  }

  // AI Assistant Query
  async queryAssistant(message) {
    return await this.request('/api/v1/assistant/chat', {
      method: 'POST',
      body: JSON.stringify({ message })
    });
  }
}

// Global API instance
window.api = new ApiService();
