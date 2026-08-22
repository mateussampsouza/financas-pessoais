// API Client for Finanças Pessoais

const API = {
  // Summary
  async getSummary(baseDate = null) {
    let url = '/api/summary';
    if (baseDate) url += `?base_date=${encodeURIComponent(baseDate)}`;
    const res = await fetch(url);
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

    const res = await fetch(`/api/transactions?${query.toString()}`);
    if (!res.ok) throw new Error('Falha ao carregar transações');
    return await res.json();
  },

  async getTransaction(id) {
    const res = await fetch(`/api/transactions/${id}`);
    if (!res.ok) throw new Error('Transação não encontrada');
    return await res.json();
  },

  async createTransaction(data) {
    const res = await fetch('/api/transactions', {
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
    const res = await fetch(`/api/transactions/${id}`, {
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

  async deleteTransaction(id) {
    const res = await fetch(`/api/transactions/${id}`, {
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

    const res = await fetch(`/api/categories?${query.toString()}`);
    if (!res.ok) throw new Error('Falha ao carregar categorias');
    return await res.json();
  },

  async getCategory(id) {
    const res = await fetch(`/api/categories/${id}`);
    if (!res.ok) throw new Error('Categoria não encontrada');
    return await res.json();
  },

  async createCategory(data) {
    const res = await fetch('/api/categories', {
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
    const res = await fetch(`/api/categories/${id}`, {
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
    const res = await fetch(`/api/categories/${id}`, {
      method: 'DELETE'
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Erro ao excluir categoria');
    }
    return true;
  }
};
