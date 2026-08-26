// API Client for Finanças Pessoais

const TOKEN_STORAGE_KEY = 'financas_token';

const Auth = {
  getToken() {
    try {
      return localStorage.getItem(TOKEN_STORAGE_KEY);
    } catch (e) {
      return null;
    }
  },
  setToken(token) {
    try {
      localStorage.setItem(TOKEN_STORAGE_KEY, token);
    } catch (e) {
      /* localStorage indisponível: sessão não persistirá entre recarregamentos */
    }
  },
  clearToken() {
    try {
      localStorage.removeItem(TOKEN_STORAGE_KEY);
    } catch (e) {
      /* no-op */
    }
  },
  isLoggedIn() {
    return !!Auth.getToken();
  }
};

// Wraps fetch(): injects the Authorization header when a token exists and
// reacts globally to an expired/invalid session (HTTP 401).
async function apiFetch(url, options = {}) {
  const token = Auth.getToken();
  const headers = Object.assign({}, options.headers || {});
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const res = await fetch(url, Object.assign({}, options, { headers }));

  if (res.status === 401) {
    Auth.clearToken();
    if (typeof window.onSessionExpired === 'function') {
      window.onSessionExpired();
    }
    throw new Error('Sessão expirada. Faça login novamente.');
  }

  return res;
}

const API = {
  // Auth
  async register(username, password) {
    const res = await fetch('/api/auth/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password })
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Erro ao criar conta');
    }
    const data = await res.json();
    Auth.setToken(data.access_token);
    return data;
  },

  async login(username, password) {
    const res = await fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password })
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Usuário ou senha inválidos');
    }
    const data = await res.json();
    Auth.setToken(data.access_token);
    return data;
  },

  logout() {
    Auth.clearToken();
  },

  async getMe() {
    const res = await apiFetch('/api/auth/me');
    if (!res.ok) throw new Error('Não foi possível carregar os dados do usuário');
    return await res.json();
  },

  // Summary
  async getSummary(baseDate = null) {
    let url = '/api/summary';
    if (baseDate) url += `?base_date=${encodeURIComponent(baseDate)}`;
    const res = await apiFetch(url);
    if (!res.ok) throw new Error('Falha ao carregar dados do resumo');
    return await res.json();
  },

  // Transactions
  async getTransactions(params = {}) {
    const query = new URLSearchParams();
    if (params.startDate) query.append('start_date', params.startDate);
    if (params.endDate) query.append('end_date', params.endDate);
    if (params.type && params.type !== 'all') query.append('type', params.type);
    if (params.categoryId) query.append('category_id', params.categoryId);

    const res = await apiFetch(`/api/transactions?${query.toString()}`);
    if (!res.ok) throw new Error('Falha ao carregar transações');
    return await res.json();
  },

  async getTransaction(id) {
    const res = await apiFetch(`/api/transactions/${id}`);
    if (!res.ok) throw new Error('Transação não encontrada');
    return await res.json();
  },

  async createTransaction(data) {
    const res = await apiFetch('/api/transactions', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Erro ao criar transação');
    }
    return await res.json();
  },

  async updateTransaction(id, data) {
    const res = await apiFetch(`/api/transactions/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Erro ao atualizar transação');
    }
    return await res.json();
  },

  async deleteTransaction(id, mode = 'only') {
    const res = await apiFetch(`/api/transactions/${id}?mode=${encodeURIComponent(mode)}`, {
      method: 'DELETE'
    });
    if (!res.ok) throw new Error('Erro ao excluir transação');
    return true;
  },

  // Categories
  async getCategories(params = {}) {
    const query = new URLSearchParams();
    if (params.startDate) query.append('start_date', params.startDate);
    if (params.endDate) query.append('end_date', params.endDate);

    const res = await apiFetch(`/api/categories?${query.toString()}`);
    if (!res.ok) throw new Error('Falha ao carregar categorias');
    return await res.json();
  },

  async getCategory(id) {
    const res = await apiFetch(`/api/categories/${id}`);
    if (!res.ok) throw new Error('Categoria não encontrada');
    return await res.json();
  },

  async createCategory(data) {
    const res = await apiFetch('/api/categories', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Erro ao criar categoria');
    }
    return await res.json();
  },

  async updateCategory(id, data) {
    const res = await apiFetch(`/api/categories/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Erro ao atualizar categoria');
    }
    return await res.json();
  },

  async deleteCategory(id) {
    const res = await apiFetch(`/api/categories/${id}`, {
      method: 'DELETE'
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Erro ao excluir categoria');
    }
    return true;
  }
};
