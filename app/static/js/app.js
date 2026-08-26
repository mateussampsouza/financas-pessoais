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
  editingTransactionRecurrenceGroupId: null,
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
  selectedCategoryColor: '#6366f1',
  currentUser: null
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

// --- Toast Notifications (friendly error/success feedback) ---
function showToast(message, variant = 'error') {
  const container = document.getElementById('toastContainer');
  if (!container) {
    // Fallback if the toast container isn't available for some reason
    alert(message);
    return;
  }

  const toast = document.createElement('div');
  toast.className = `toast toast-${variant}`;
  toast.innerHTML = `
    <i data-lucide="${variant === 'error' ? 'alert-circle' : 'check-circle-2'}"></i>
    <span>${escapeHtml(message)}</span>
  `;
  container.appendChild(toast);
  lucide.createIcons();

  // Trigger enter animation
  requestAnimationFrame(() => toast.classList.add('toast-visible'));

  setTimeout(() => {
    toast.classList.remove('toast-visible');
    setTimeout(() => toast.remove(), 300);
  }, 4500);
}

// --- Currency Masking Helpers (R$ 0,00 style, digits-as-cents) ---
function maskCurrencyFromDigits(digitsOnly) {
  const cents = parseInt(digitsOnly || '0', 10);
  const value = cents / 100;
  return value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
}

function parseCurrencyToFloat(formattedValue) {
  if (!formattedValue) return 0;
  const digitsOnly = String(formattedValue).replace(/\D/g, '');
  if (!digitsOnly) return 0;
  return parseInt(digitsOnly, 10) / 100;
}

function setCurrencyInputValue(inputEl, numericValue) {
  const cents = Math.round((Number(numericValue) || 0) * 100);
  inputEl.value = maskCurrencyFromDigits(String(cents));
}

function setupCurrencyMask() {
  const input = document.getElementById('txAmount');
  if (!input) return;
  input.addEventListener('input', (e) => {
    const digits = e.target.value.replace(/\D/g, '');
    e.target.value = maskCurrencyFromDigits(digits);
  });
}

// --- Auto-close calendar popovers as soon as a date is chosen ---
function setupDateAutoClose() {
  document.querySelectorAll('input[type="date"]').forEach(el => {
    el.addEventListener('change', () => el.blur());
  });
}

// --- Auth Screen ---
function showAuthScreen() {
  document.getElementById('authScreen').classList.add('active');
  document.getElementById('appContainer').classList.remove('active');
}

function showApp(user) {
  state.currentUser = user;
  document.getElementById('authScreen').classList.remove('active');
  document.getElementById('appContainer').classList.add('active');

  const usernameEl = document.getElementById('headerUsername');
  if (usernameEl) usernameEl.textContent = user.username;

  navigateTo('home');
  lucide.createIcons();
}

function switchAuthTab(tabName) {
  document.querySelectorAll('.auth-tab').forEach(el => el.classList.toggle('active', el.dataset.tab === tabName));
  document.getElementById('loginForm').classList.toggle('active', tabName === 'login');
  document.getElementById('registerForm').classList.toggle('active', tabName === 'register');
  document.getElementById('loginError').textContent = '';
  document.getElementById('registerError').textContent = '';
}

async function handleLoginSubmit(e) {
  e.preventDefault();
  const errorEl = document.getElementById('loginError');
  errorEl.textContent = '';

  const username = document.getElementById('loginUsername').value.trim();
  const password = document.getElementById('loginPassword').value;

  try {
    await API.login(username, password);
    const user = await API.getMe();
    document.getElementById('loginForm').reset();
    showApp(user);
  } catch (err) {
    errorEl.textContent = err.message;
  }
}

async function handleRegisterSubmit(e) {
  e.preventDefault();
  const errorEl = document.getElementById('registerError');
  errorEl.textContent = '';

  const username = document.getElementById('registerUsername').value.trim();
  const password = document.getElementById('registerPassword').value;
  const passwordConfirm = document.getElementById('registerPasswordConfirm').value;

  if (password !== passwordConfirm) {
    errorEl.textContent = 'As senhas não coincidem.';
    return;
  }

  try {
    await API.register(username, password);
    const user = await API.getMe();
    document.getElementById('registerForm').reset();
    showApp(user);
  } catch (err) {
    errorEl.textContent = err.message;
  }
}

function handleLogout() {
  API.logout();
  state.currentUser = null;
  showAuthScreen();
}

// Called globally by api.js whenever a request comes back 401 Unauthorized
window.onSessionExpired = function () {
  state.currentUser = null;
  showAuthScreen();
  showToast('Sessão expirada. Faça login novamente.', 'error');
};

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
    renderPeriodTotal(txs);
  } catch (err) {
    console.error(err);
  }
}

// Total (net) of the currently filtered transactions list: receitas somam, despesas subtraem.
function renderPeriodTotal(transactions) {
  const totalEl = document.getElementById('txPeriodTotalAmount');
  if (!totalEl) return;

  const total = (transactions || []).reduce((sum, tx) => {
    return sum + (tx.type === 'receita' ? tx.amount : -tx.amount);
  }, 0);

  totalEl.textContent = formatCurrency(total);
  totalEl.className = 'period-total-amount ' + (total >= 0 ? 'positive' : 'negative');
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

    // Total de despesas do período, somando todas as categorias
    const totalExpense = categories.reduce((sum, c) => sum + (c.total_expense || 0), 0);
    const totalExpenseEl = document.getElementById('categoryTotalExpense');
    if (totalExpenseEl) totalExpenseEl.textContent = formatCurrency(totalExpense);

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
      const hasExpense = (cat.total_expense || 0) > 0;
      const hasIncome = (cat.total_income || 0) > 0;

      const expenseHtml = hasExpense
        ? `<span class="cat-amount despesa">- ${formatCurrency(cat.total_expense)}</span>`
        : '';
      const incomeHtml = hasIncome
        ? `<span class="cat-amount receita">${formatCurrency(cat.total_income)}</span>`
        : '';
      const amountsHtml = (hasExpense || hasIncome)
        ? `<div class="cat-amounts">${expenseHtml}${incomeHtml}</div>`
        : `<span class="cat-amount">${formatCurrency(0)}</span>`;

      return `
        <div class="category-card" onclick="openEditCategory(${cat.id})">
          <div class="cat-left">
            <div class="cat-icon-box" style="background-color: ${cat.color};">
              <i data-lucide="${cat.icon || 'tag'}"></i>
            </div>
            <span class="cat-name">${escapeHtml(cat.name)}</span>
          </div>
          ${amountsHtml}
        </div>
      `;
    }).join('');

    lucide.createIcons();
  } catch (err) {
    console.error(err);
  }
}

// Open Form: Transaction
// forcedType: when set (e.g. 'receita'), the type select is pre-selected and locked,
// used by the bottom bar's "Receita" shortcut button.
async function openNewTransaction(forcedType = null) {
  state.editingTransactionId = null;
  state.editingTransactionRecurrenceGroupId = null;
  document.getElementById('txFormTitle').textContent = forcedType === 'receita' ? 'Nova Receita' : 'Nova Transação';
  document.getElementById('txForm').reset();
  document.getElementById('txDeleteBtn').style.display = 'none';

  document.getElementById('txRecurrence').disabled = false;
  document.getElementById('txRecurrenceLockedHint').style.display = 'none';
  document.getElementById('txRecurrence').value = 'nunca';
  document.getElementById('txRecurrenceInstallment').value = '1';
  updateRecurrenceFieldsState();

  // Set default current date and time
  const now = new Date();
  const dateStr = now.toISOString().split('T')[0];
  const timeStr = String(now.getHours()).padStart(2, '0') + ':' + String(now.getMinutes()).padStart(2, '0');
  document.getElementById('txDate').value = dateStr;
  document.getElementById('txTime').value = timeStr;

  // Reset the currency field to R$ 0,00
  setCurrencyInputValue(document.getElementById('txAmount'), 0);

  // Populate categories dropdown
  await populateCategoriesDropdown();

  const typeSelect = document.getElementById('txType');
  const lockedHint = document.getElementById('txTypeLockedHint');
  if (forcedType) {
    typeSelect.value = forcedType;
    typeSelect.disabled = true;
    lockedHint.style.display = 'block';
  } else {
    typeSelect.disabled = false;
    lockedHint.style.display = 'none';
  }

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
    document.getElementById('txType').disabled = false;
    document.getElementById('txTypeLockedHint').style.display = 'none';
    setCurrencyInputValue(document.getElementById('txAmount'), tx.amount);
    document.getElementById('txCategory').value = tx.category_id;

    const d = new Date(tx.date_time);
    const dateStr = d.toISOString().split('T')[0];
    const timeStr = String(d.getHours()).padStart(2, '0') + ':' + String(d.getMinutes()).padStart(2, '0');
    document.getElementById('txDate').value = dateStr;
    document.getElementById('txTime').value = timeStr;

    // Recurrence, quantidade and parcela are fixed at creation time and locked here:
    // editing one occurrence must never change how the rest of the series was generated.
    state.editingTransactionRecurrenceGroupId = tx.recurrence_group_id || null;
    document.getElementById('txRecurrence').value = tx.recurrence || 'nunca';
    document.getElementById('txRecurrenceQuantity').value = tx.recurrence_quantity ?? '';
    document.getElementById('txRecurrenceInstallment').value = tx.recurrence_installment ?? '';
    document.getElementById('txRecurrence').disabled = true;
    document.getElementById('txRecurrenceQuantity').disabled = true;
    document.getElementById('txRecurrenceInstallment').disabled = true;
    document.getElementById('txRecurrenceLockedHint').style.display = 'block';

    navigateTo('form-transaction');
  } catch (err) {
    showToast(err.message);
  }
}

// Recurrence Fields (Recorrência / Quantidade / Parcela)
function updateRecurrenceFieldsState() {
  if (state.editingTransactionId) return; // locked while editing an existing transaction

  const recurrence = document.getElementById('txRecurrence').value;
  const qtyInput = document.getElementById('txRecurrenceQuantity');
  const instInput = document.getElementById('txRecurrenceInstallment');
  const isNever = recurrence === 'nunca';

  qtyInput.disabled = isNever;
  instInput.disabled = isNever;

  if (isNever) {
    qtyInput.value = '';
    instInput.value = '1';
  } else if (!qtyInput.value) {
    qtyInput.value = '1';
  }
  clampRecurrenceInstallment();
}

function clampRecurrenceInstallment() {
  const qtyInput = document.getElementById('txRecurrenceQuantity');
  const instInput = document.getElementById('txRecurrenceInstallment');
  const qty = parseInt(qtyInput.value, 10) || 1;
  instInput.max = qty;
  if (parseInt(instInput.value, 10) > qty) {
    instInput.value = String(qty);
  }
}

// Restricts a numeric input to at most 2 digits (0-99), stripping non-digit chars.
function enforceTwoDigitNumericInput(e) {
  let digits = e.target.value.replace(/[^0-9]/g, '').slice(0, 2);
  if (digits !== '') {
    digits = String(Math.min(parseInt(digits, 10), 99));
  }
  e.target.value = digits;
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
    showToast(err.message);
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
  const amount = parseCurrencyToFloat(document.getElementById('txAmount').value);
  const category_id = parseInt(document.getElementById('txCategory').value);
  const dateStr = document.getElementById('txDate').value;
  const timeStr = document.getElementById('txTime').value || '12:00';

  if (!desc || isNaN(amount) || amount <= 0 || !category_id || !dateStr) {
    showToast('Por favor, preencha todos os campos obrigatórios corretamente.');
    return;
  }

  const dateTimeIso = `${dateStr}T${timeStr}:00`;

  const payload = {
    description: desc,
    type: type,
    amount: amount,
    category_id: category_id,
    date_time: dateTimeIso
  };

  // Recurrence is only set on creation; it's locked (and not sent) when editing.
  if (!state.editingTransactionId) {
    const recurrence = document.getElementById('txRecurrence').value;
    payload.recurrence = recurrence;
    if (recurrence !== 'nunca') {
      payload.recurrence_quantity = parseInt(document.getElementById('txRecurrenceQuantity').value, 10) || 1;
      payload.recurrence_installment = parseInt(document.getElementById('txRecurrenceInstallment').value, 10) || 1;
    }
  }

  try {
    if (state.editingTransactionId) {
      await API.updateTransaction(state.editingTransactionId, payload);
    } else {
      await API.createTransaction(payload);
    }
    navigateTo('transactions');
  } catch (err) {
    showToast(err.message);
  }
}

async function handleDeleteTransaction() {
  if (!state.editingTransactionId) return;

  if (state.editingTransactionRecurrenceGroupId) {
    document.getElementById('deleteRecurrenceModal').style.display = 'flex';
    return;
  }

  if (confirm('Tem certeza que deseja excluir esta transação?')) {
    await performDeleteTransaction('only');
  }
}

async function performDeleteTransaction(mode) {
  try {
    await API.deleteTransaction(state.editingTransactionId, mode);
    navigateTo('transactions');
  } catch (err) {
    showToast(err.message);
  }
}

async function handleCategorySubmit(e) {
  e.preventDefault();
  const name = document.getElementById('catName').value.trim();
  const icon = state.selectedCategoryIcon || 'tag';
  const color = state.selectedCategoryColor || '#6366f1';

  if (!name) {
    showToast('Por favor, informe o nome da categoria.');
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
    showToast(err.message);
  }
}

async function handleDeleteCategory() {
  if (!state.editingCategoryId) return;
  if (confirm('Tem certeza que deseja excluir esta categoria?')) {
    try {
      await API.deleteCategory(state.editingCategoryId);
      navigateTo('categories');
    } catch (err) {
      // Friendly feedback for the common case: category still has linked transactions
      showToast(err.message);
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

  document.getElementById('txRecurrence').addEventListener('change', updateRecurrenceFieldsState);
  document.getElementById('txRecurrenceQuantity').addEventListener('input', (e) => {
    enforceTwoDigitNumericInput(e);
    clampRecurrenceInstallment();
  });
  document.getElementById('txRecurrenceInstallment').addEventListener('input', (e) => {
    enforceTwoDigitNumericInput(e);
    clampRecurrenceInstallment();
  });

  document.getElementById('deleteFollowingBtn').addEventListener('click', () => {
    document.getElementById('deleteRecurrenceModal').style.display = 'none';
    performDeleteTransaction('following');
  });
  document.getElementById('deleteOnlyBtn').addEventListener('click', () => {
    document.getElementById('deleteRecurrenceModal').style.display = 'none';
    performDeleteTransaction('only');
  });
  document.getElementById('deleteCancelBtn').addEventListener('click', () => {
    document.getElementById('deleteRecurrenceModal').style.display = 'none';
  });

  document.getElementById('catForm').addEventListener('submit', handleCategorySubmit);
  document.getElementById('catDeleteBtn').addEventListener('click', handleDeleteCategory);

  // Setup Pickers
  setupIconPicker();
  setupColorPicker();

  // Setup currency mask & calendar auto-close
  setupCurrencyMask();
  setupDateAutoClose();

  // Auth screen wiring
  document.querySelectorAll('.auth-tab').forEach(tab => {
    tab.addEventListener('click', () => switchAuthTab(tab.dataset.tab));
  });
  document.getElementById('loginForm').addEventListener('submit', handleLoginSubmit);
  document.getElementById('registerForm').addEventListener('submit', handleRegisterSubmit);
  document.getElementById('logoutBtn').addEventListener('click', handleLogout);

  lucide.createIcons();

  // Boot: check for an existing session before showing the app
  if (Auth.isLoggedIn()) {
    API.getMe()
      .then(user => showApp(user))
      .catch(() => showAuthScreen());
  } else {
    showAuthScreen();
  }
});
