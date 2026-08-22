// Main Application Logic

const AVAILABLE_ICONS = [
  'utensils', 'car', 'home', 'gamepad-2', 'wallet', 'trending-up',
  'heart-pulse', 'graduation-cap', 'tag', 'shopping-cart', 'coffee',
  'plane', 'tv', 'gift', 'smartphone', 'wifi', 'briefcase', 'zap'
];

const AVAILABLE_COLORS = [
  '#ef4444', '#f97316', '#f59e0b', '#eab308',
  '#10b981', '#06b6d4', '#3b82f6', '#6366f1',
  '#8b5cf6', '#d946ef', '#ec4899', '#64748b'
];

// App State
const state = {
  currentView: 'home',
  editingTransactionId: null,
  editingCategoryId: null,
  txFilter: {
    startDate: '',
    endDate: '',
    type: 'all'
  },
  catFilter: {
    startDate: '',
    endDate: ''
  },
  categoriesCache: [],
  selectedCategoryIcon: 'tag',
  selectedCategoryColor: '#6366f1'
};

// Utilities
function formatCurrency(value) {
  return Number(value || 0).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
}

function formatDateDisplay(dateString) {
  if (!dateString) return '';
  const d = new Date(dateString);
  const day = String(d.getDate()).padStart(2, '0');
  const month = String(d.getMonth() + 1).padStart(2, '0');
  const year = d.getFullYear();
  const hours = String(d.getHours()).padStart(2, '0');
  const minutes = String(d.getMinutes()).padStart(2, '0');
  return `${day}/${month}/${year} ${hours}:${minutes}`;
}

function getMonthStartAndEndDates() {
  const now = new Date();
  const year = now.getFullYear();
  const month = now.getMonth();
  
  const start = new Date(year, month, 1);
  const end = new Date(year, month + 1, 0);

  const startStr = `${start.getFullYear()}-${String(start.getMonth() + 1).padStart(2, '0')}-01`;
  const endStr = `${end.getFullYear()}-${String(end.getMonth() + 1).padStart(2, '0')}-${String(end.getDate()).padStart(2, '0')}`;
  
  return { startStr, endStr };
}

// Navigation & View Routing
function navigateTo(viewName) {
  state.currentView = viewName;

  document.querySelectorAll('.view').forEach(el => el.classList.remove('active'));
  document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));

  const targetView = document.getElementById(`view-${viewName}`);
  if (targetView) targetView.classList.add('active');

  const targetNav = document.querySelector(`.nav-item[data-view="${viewName}"]`);
  if (targetNav) targetNav.classList.add('active');

  // Trigger loads based on view
  if (viewName === 'home') {
    loadHomeData();
  } else if (viewName === 'transactions') {
    loadTransactionsData();
  } else if (viewName === 'categories') {
    loadCategoriesData();
  }

  window.scrollTo({ top: 0, behavior: 'smooth' });
}

// Home View
async function loadHomeData() {
  try {
    const summary = await API.getSummary();
    
    // Balance
    const balEl = document.getElementById('homeBalanceAmount');
    balEl.textContent = formatCurrency(summary.current_balance);
    balEl.className = 'balance-amount ' + (summary.current_balance >= 0 ? 'positive' : 'negative');

    // Horizontal Bar Chart
    renderHomeHorizontalBar(summary.total_income, summary.total_expense);

    // Recent Transactions
    renderTransactionsList(summary.recent_transactions, 'homeRecentList', true);
  } catch (err) {
    console.error(err);
  }
}

// Transactions View
async function loadTransactionsData() {
  try {
    const txs = await API.getTransactions({
      startDate: state.txFilter.startDate,
      endDate: state.txFilter.endDate,
      type: state.txFilter.type
    });
    renderTransactionsList(txs, 'transactionsList', false);
  } catch (err) {
    console.error(err);
  }
}

function renderTransactionsList(transactions, containerId, isRecentView = false) {
  const container = document.getElementById(containerId);
  if (!container) return;

  if (!transactions || transactions.length === 0) {
    container.innerHTML = `
      <div class="empty-state">
        <i data-lucide="inbox"></i>
        <p>${isRecentView ? 'Nenhuma transação nos últimos 3 dias' : 'Nenhuma transação encontrada no período'}</p>
      </div>
    `;
    lucide.createIcons();
    return;
  }

  container.innerHTML = transactions.map(tx => {
    const isIncome = tx.type === 'receita';
    const sign = isIncome ? '+' : '-';
    const cat = tx.category || { name: 'Sem categoria', icon: 'tag', color: '#6366f1' };

    return `
      <div class="transaction-card" onclick="openEditTransaction(${tx.id})">
        <div class="tx-left">
          <div class="tx-icon-box" style="background-color: ${cat.color}25; color: ${cat.color};">
            <i data-lucide="${cat.icon || 'tag'}"></i>
          </div>
          <div class="tx-info">
            <span class="tx-desc">${escapeHtml(tx.description)}</span>
            <div class="tx-meta">
              <span class="tx-category-tag" style="color: ${cat.color}">
                ● ${escapeHtml(cat.name)}
              </span>
              <span>•</span>
              <span>${formatDateDisplay(tx.date_time)}</span>
            </div>
          </div>
        </div>
        <div class="tx-right">
          <span class="tx-amount ${tx.type}">${sign} ${formatCurrency(tx.amount)}</span>
          <span class="tx-badge ${tx.type}">${tx.type}</span>
        </div>
      </div>
    `;
  }).join('');

  lucide.createIcons();
}

// Categories View
async function loadCategoriesData() {
  try {
    const categories = await API.getCategories({
      startDate: state.catFilter.startDate,
      endDate: state.catFilter.endDate
    });
    state.categoriesCache = categories;

    // Render Donut Chart
    renderCategoryDonut(categories);

    // Render Category Cards
    const container = document.getElementById('categoriesList');
    if (!container) return;

    if (!categories || categories.length === 0) {
      container.innerHTML = `
        <div class="empty-state">
          <i data-lucide="tag"></i>
          <p>Nenhuma categoria cadastrada</p>
        </div>
      `;
      lucide.createIcons();
      return;
    }

    container.innerHTML = categories.map(cat => {
      return `
        <div class="category-card" onclick="openEditCategory(${cat.id})">
          <div class="cat-left">
            <div class="cat-icon-box" style="background-color: ${cat.color};">
              <i data-lucide="${cat.icon || 'tag'}"></i>
            </div>
            <span class="cat-name">${escapeHtml(cat.name)}</span>
          </div>
          <span class="cat-amount">${formatCurrency(cat.total_expense)}</span>
        </div>
      `;
    }).join('');

    lucide.createIcons();
  } catch (err) {
    console.error(err);
  }
}

// Open Form: Transaction
async function openNewTransaction() {
  state.editingTransactionId = null;
  document.getElementById('txFormTitle').textContent = 'Nova Transação';
  document.getElementById('txForm').reset();
  document.getElementById('txDeleteBtn').style.display = 'none';

  // Set default current date and time
  const now = new Date();
  const dateStr = now.toISOString().split('T')[0];
  const timeStr = String(now.getHours()).padStart(2, '0') + ':' + String(now.getMinutes()).padStart(2, '0');
  document.getElementById('txDate').value = dateStr;
  document.getElementById('txTime').value = timeStr;

  // Populate categories dropdown
  await populateCategoriesDropdown();

  navigateTo('form-transaction');
}

async function openEditTransaction(id) {
  try {
    state.editingTransactionId = id;
    document.getElementById('txFormTitle').textContent = 'Editar Transação';
    document.getElementById('txDeleteBtn').style.display = 'block';

    await populateCategoriesDropdown();

    const tx = await API.getTransaction(id);
    document.getElementById('txDescription').value = tx.description;
    document.getElementById('txType').value = tx.type;
    document.getElementById('txAmount').value = tx.amount;
    document.getElementById('txCategory').value = tx.category_id;
    
    const d = new Date(tx.date_time);
    const dateStr = d.toISOString().split('T')[0];
    const timeStr = String(d.getHours()).padStart(2, '0') + ':' + String(d.getMinutes()).padStart(2, '0');
    document.getElementById('txDate').value = dateStr;
    document.getElementById('txTime').value = timeStr;
    document.getElementById('txRepeatMonthly').checked = !!tx.repeat_monthly;

    navigateTo('form-transaction');
  } catch (err) {
    alert(err.message);
  }
}

async function populateCategoriesDropdown() {
  const select = document.getElementById('txCategory');
  select.innerHTML = '<option value="">Selecione uma categoria...</option>';
  
  const cats = await API.getCategories();
  cats.forEach(c => {
    const opt = document.createElement('option');
    opt.value = c.id;
    opt.textContent = c.name;
    select.appendChild(opt);
  });
}

// Open Form: Category
function openNewCategory() {
  state.editingCategoryId = null;
  document.getElementById('catFormTitle').textContent = 'Nova Categoria';
  document.getElementById('catForm').reset();
  document.getElementById('catDeleteBtn').style.display = 'none';

  selectCategoryIcon('tag');
  selectCategoryColor('#6366f1');

  navigateTo('form-category');
}

async function openEditCategory(id) {
  try {
    state.editingCategoryId = id;
    document.getElementById('catFormTitle').textContent = 'Editar Categoria';
    document.getElementById('catDeleteBtn').style.display = 'block';

    const cat = await API.getCategory(id);
    document.getElementById('catName').value = cat.name;
    selectCategoryIcon(cat.icon || 'tag');
    selectCategoryColor(cat.color || '#6366f1');

    navigateTo('form-category');
  } catch (err) {
    alert(err.message);
  }
}

// Icon & Color Pickers Setup
function setupIconPicker() {
  const container = document.getElementById('iconPickerGrid');
  container.innerHTML = AVAILABLE_ICONS.map(icon => `
    <div class="icon-choice" data-icon="${icon}" onclick="selectCategoryIcon('${icon}')">
      <i data-lucide="${icon}"></i>
    </div>
  `).join('');
  lucide.createIcons();
}

function selectCategoryIcon(icon) {
  state.selectedCategoryIcon = icon;
  document.querySelectorAll('.icon-choice').forEach(el => {
    el.classList.toggle('selected', el.dataset.icon === icon);
  });
}

function setupColorPicker() {
  const container = document.getElementById('colorPickerGrid');
  container.innerHTML = AVAILABLE_COLORS.map(color => `
    <div class="color-choice" style="background-color: ${color};" data-color="${color}" onclick="selectCategoryColor('${color}')"></div>
  `).join('');
}

function selectCategoryColor(color) {
  state.selectedCategoryColor = color;
  document.querySelectorAll('.color-choice').forEach(el => {
    el.classList.toggle('selected', el.dataset.color === color);
  });
}

// Form Submissions
async function handleTransactionSubmit(e) {
  e.preventDefault();
  const desc = document.getElementById('txDescription').value.trim();
  const type = document.getElementById('txType').value;
  const amount = parseFloat(document.getElementById('txAmount').value);
  const category_id = parseInt(document.getElementById('txCategory').value);
  const dateStr = document.getElementById('txDate').value;
  const timeStr = document.getElementById('txTime').value || '12:00';
  const repeat_monthly = document.getElementById('txRepeatMonthly').checked;

  if (!desc || isNaN(amount) || amount <= 0 || !category_id || !dateStr) {
    alert('Por favor, preencha todos os campos obrigatórios corretamente.');
    return;
  }

  const dateTimeIso = `${dateStr}T${timeStr}:00`;

  const payload = {
    description: desc,
    type: type,
    amount: amount,
    category_id: category_id,
    date_time: dateTimeIso,
    repeat_monthly: repeat_monthly
  };

  try {
    if (state.editingTransactionId) {
      await API.updateTransaction(state.editingTransactionId, payload);
    } else {
      await API.createTransaction(payload);
    }
    navigateTo('transactions');
  } catch (err) {
    alert(err.message);
  }
}

async function handleDeleteTransaction() {
  if (!state.editingTransactionId) return;
  if (confirm('Tem certeza que deseja excluir esta transação?')) {
    try {
      await API.deleteTransaction(state.editingTransactionId);
      navigateTo('transactions');
    } catch (err) {
      alert(err.message);
    }
  }
}

async function handleCategorySubmit(e) {
  e.preventDefault();
  const name = document.getElementById('catName').value.trim();
  const icon = state.selectedCategoryIcon || 'tag';
  const color = state.selectedCategoryColor || '#6366f1';

  if (!name) {
    alert('Por favor, informe o nome da categoria.');
    return;
  }

  const payload = { name, icon, color };

  try {
    if (state.editingCategoryId) {
      await API.updateCategory(state.editingCategoryId, payload);
    } else {
      await API.createCategory(payload);
    }
    navigateTo('categories');
  } catch (err) {
    alert(err.message);
  }
}

async function handleDeleteCategory() {
  if (!state.editingCategoryId) return;
  if (confirm('Tem certeza que deseja excluir esta categoria?')) {
    try {
      await API.deleteCategory(state.editingCategoryId);
      navigateTo('categories');
    } catch (err) {
      alert(err.message);
    }
  }
}

function escapeHtml(str) {
  if (!str) return '';
  return str.replace(/[&<>"']/g, function(m) {
    switch (m) {
      case '&': return '&amp;';
      case '<': return '&lt;';
      case '>': return '&gt;';
      case '"': return '&quot;';
      case "'": return '&#39;';
      default: return m;
    }
  });
}

// Initialization on DOM Load
document.addEventListener('DOMContentLoaded', () => {
  // Set default initial dates for filters (1st day and last day of current month)
  const { startStr, endStr } = getMonthStartAndEndDates();
  
  state.txFilter.startDate = startStr;
  state.txFilter.endDate = endStr;
  document.getElementById('txFilterStart').value = startStr;
  document.getElementById('txFilterEnd').value = endStr;

  state.catFilter.startDate = startStr;
  state.catFilter.endDate = endStr;
  document.getElementById('catFilterStart').value = startStr;
  document.getElementById('catFilterEnd').value = endStr;

  // Filter Listeners: Transactions
  document.getElementById('txFilterStart').addEventListener('change', (e) => {
    state.txFilter.startDate = e.target.value;
    loadTransactionsData();
  });
  document.getElementById('txFilterEnd').addEventListener('change', (e) => {
    state.txFilter.endDate = e.target.value;
    loadTransactionsData();
  });

  // Type Toggle Filter
  document.querySelectorAll('.type-toggle-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.type-toggle-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      state.txFilter.type = btn.dataset.type;
      loadTransactionsData();
    });
  });

  // Filter Listeners: Categories
  document.getElementById('catFilterStart').addEventListener('change', (e) => {
    state.catFilter.startDate = e.target.value;
    loadCategoriesData();
  });
  document.getElementById('catFilterEnd').addEventListener('change', (e) => {
    state.catFilter.endDate = e.target.value;
    loadCategoriesData();
  });

  // Forms setup
  document.getElementById('txForm').addEventListener('submit', handleTransactionSubmit);
  document.getElementById('txDeleteBtn').addEventListener('click', handleDeleteTransaction);

  document.getElementById('catForm').addEventListener('submit', handleCategorySubmit);
  document.getElementById('catDeleteBtn').addEventListener('click', handleDeleteCategory);

  // Setup Pickers
  setupIconPicker();
  setupColorPicker();

  // Load initial home view
  navigateTo('home');
  lucide.createIcons();
});
