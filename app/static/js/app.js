// PocketLedger Frontend Application Logic

let selectedCurrency = "INR";
let selectedCurrencySymbol = "₹";
let currentPage = 1;
const pageLimit = 20;
let currentTransactions = [];
let editingTxId = null;

// DOM Element References
const currencySelect = document.getElementById("currency-select");
const valIncome = document.getElementById("val-income");
const valExpenses = document.getElementById("val-expenses");
const valBalance = document.getElementById("val-balance");
const valBalanceStatus = document.getElementById("val-balance-status");
const valCount = document.getElementById("val-count");

const filterMonth = document.getElementById("filter-month");
const filterCategory = document.getElementById("filter-category");
const filterType = document.getElementById("filter-type");
const filterSearch = document.getElementById("filter-search");
const clearFiltersBtn = document.getElementById("clear-filters-btn");

const transactionRows = document.getElementById("transaction-rows");
const emptyState = document.getElementById("empty-state");
const loadingSpinner = document.getElementById("loading-spinner");
const categoryBreakdownList = document.getElementById("category-breakdown-list");
const errorBanner = document.getElementById("error-banner");
const errorMessage = document.getElementById("error-message");
const paginationControls = document.getElementById("pagination-controls");

const addTxBtn = document.getElementById("add-tx-btn");
const exportCsvBtn = document.getElementById("export-csv-btn");
const seedDataBtn = document.getElementById("seed-data-btn");

const txModal = document.getElementById("tx-modal");
const modalTitle = document.getElementById("modal-title");
const modalClose = document.getElementById("modal-close");
const modalCancel = document.getElementById("modal-cancel");
const txForm = document.getElementById("tx-form");
const txIdInput = document.getElementById("tx-id");
const txTypeInput = document.getElementById("tx-type");
const txAmountInput = document.getElementById("tx-amount");
const txCategoryInput = document.getElementById("tx-category");
const txDateInput = document.getElementById("tx-date");
const txDescriptionInput = document.getElementById("tx-description");

// Map Currency Symbols
const currencySymbols = {
    "INR": "₹",
    "USD": "$",
    "EUR": "€",
    "GBP": "£"
};

// Initialize Application
document.addEventListener("DOMContentLoaded", () => {
    txDateInput.value = new Date().toISOString().split("T")[0];

    // Event Listeners
    currencySelect.addEventListener("change", (e) => {
        selectedCurrency = e.target.value;
        selectedCurrencySymbol = currencySymbols[selectedCurrency] || "₹";
        currentPage = 1;
        fetchDashboardData();
    });

    filterMonth.addEventListener("change", () => { currentPage = 1; fetchDashboardData(); });
    filterCategory.addEventListener("change", () => { currentPage = 1; fetchDashboardData(); });
    filterType.addEventListener("change", () => { currentPage = 1; fetchDashboardData(); });
    filterSearch.addEventListener("input", debounce(() => { currentPage = 1; fetchDashboardData(); }, 300));
    clearFiltersBtn.addEventListener("click", resetFilters);

    addTxBtn.addEventListener("click", () => openModal());
    modalClose.addEventListener("click", closeModal);
    modalCancel.addEventListener("click", closeModal);
    txForm.addEventListener("submit", submitTransactionForm);

    exportCsvBtn.addEventListener("click", exportCsv);
    seedDataBtn.addEventListener("click", seedData);

    fetchDashboardData();
});

// Primary Orchestrator
async function fetchDashboardData() {
    clearError();
    setLoadingState(true);

    try {
        await Promise.all([
            loadSummary(),
            loadTransactions()
        ]);
    } catch (err) {
        handleError(err, "Failed to load dashboard data");
    } finally {
        setLoadingState(false);
    }
}

// 1. Load Summary
async function loadSummary() {
    const monthVal = filterMonth.value;
    const params = new URLSearchParams();
    if (monthVal) params.append("month", monthVal);
    params.append("currency", selectedCurrency);

    const res = await fetch(`/api/summary?${params.toString()}`);
    if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.detail || "Failed to fetch summary");
    }
    const data = await res.json();
    renderSummary(data);
}

// 2. Render Summary
function renderSummary(summary) {
    valIncome.textContent = formatAmount(summary.total_income);
    valExpenses.textContent = formatAmount(summary.total_expenses);
    
    const balance = summary.remaining_balance;
    valBalance.textContent = (balance < 0 ? "-" : "") + formatAmount(Math.abs(balance));
    
    if (balance >= 0) {
        valBalance.style.color = "var(--text-primary)";
        valBalanceStatus.textContent = "Positive Balance";
    } else {
        valBalance.style.color = "var(--expense-color)";
        valBalanceStatus.textContent = "Deficit Warning";
    }

    valCount.textContent = summary.transaction_count;
    renderCategoryBreakdown(summary.expense_category_breakdown);
}

// 3. Load Transactions (Paginated)
async function loadTransactions() {
    const params = buildFilterParams();
    params.append("page", currentPage);
    params.append("limit", pageLimit);

    const res = await fetch(`/api/transactions?${params.toString()}`);
    if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.detail || "Failed to fetch transactions");
    }
    const data = await res.json();
    currentTransactions = data.items;
    renderTransactions(data.items, data.total, data.page, data.total_pages);
}

// 4. Render Transactions
function renderTransactions(items, total, page, totalPages) {
    transactionRows.innerHTML = "";

    if (!items || items.length === 0) {
        emptyState.style.display = "block";
        if (paginationControls) paginationControls.innerHTML = "";
        return;
    }

    emptyState.style.display = "none";

    items.forEach((tx) => {
        const tr = document.createElement("tr");
        const isIncome = tx.type === "income";

        tr.innerHTML = `
            <td>${tx.date}</td>
            <td><span class="type-badge ${isIncome ? 'badge-income' : 'badge-expense'}">${tx.type}</span></td>
            <td><strong>${escapeHtml(tx.category)}</strong></td>
            <td style="color: var(--text-secondary);">${escapeHtml(tx.description || '-')}</td>
            <td class="${isIncome ? 'amount-income' : 'amount-expense'}">
                ${isIncome ? '+' : '-'}${formatAmount(tx.amount)}
            </td>
            <td style="text-align: right;">
                <div class="action-btns" style="justify-content: flex-end;">
                    <button class="btn-icon" title="Edit" onclick="openModal(${tx.id})">
                        <i class="fa-solid fa-pen-to-square"></i>
                    </button>
                    <button class="btn-icon delete" title="Delete" onclick="deleteTx(${tx.id})">
                        <i class="fa-solid fa-trash"></i>
                    </button>
                </div>
            </td>
        `;

        transactionRows.appendChild(tr);
    });

    renderPaginationControls(page, totalPages);
}

// Render Pagination Controls
function renderPaginationControls(page, totalPages) {
    if (!paginationControls) return;
    paginationControls.innerHTML = "";

    if (totalPages <= 1) return;

    const prevBtn = document.createElement("button");
    prevBtn.className = "btn btn-secondary";
    prevBtn.style.padding = "4px 10px";
    prevBtn.style.fontSize = "12px";
    prevBtn.disabled = page <= 1;
    prevBtn.innerHTML = '<i class="fa-solid fa-chevron-left"></i> Prev';
    prevBtn.addEventListener("click", () => {
        if (currentPage > 1) {
            currentPage--;
            fetchDashboardData();
        }
    });

    const info = document.createElement("span");
    info.style.fontSize = "12px";
    info.style.color = "var(--text-secondary)";
    info.textContent = `Page ${page} of ${totalPages}`;

    const nextBtn = document.createElement("button");
    nextBtn.className = "btn btn-secondary";
    nextBtn.style.padding = "4px 10px";
    nextBtn.style.fontSize = "12px";
    nextBtn.disabled = page >= totalPages;
    nextBtn.innerHTML = 'Next <i class="fa-solid fa-chevron-right"></i>';
    nextBtn.addEventListener("click", () => {
        if (currentPage < totalPages) {
            currentPage++;
            fetchDashboardData();
        }
    });

    paginationControls.appendChild(prevBtn);
    paginationControls.appendChild(info);
    paginationControls.appendChild(nextBtn);
}

// 5. Submit Form (Create / Update)
async function submitTransactionForm(e) {
    e.preventDefault();
    clearError();

    const payload = {
        type: txTypeInput.value,
        amount: parseFloat(txAmountInput.value),
        category: txCategoryInput.value,
        date: txDateInput.value,
        description: txDescriptionInput.value.trim() || null
    };

    try {
        let res;
        if (editingTxId) {
            res = await fetch(`/api/transactions/${editingTxId}`, {
                method: "PUT",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });
        } else {
            res = await fetch("/api/transactions", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });
        }

        if (!res.ok) {
            const errData = await res.json().catch(() => ({}));
            let msg = errData.detail;
            if (Array.isArray(msg)) {
                msg = msg.map(m => m.msg || JSON.stringify(m)).join(", ");
            }
            throw new Error(msg || "Validation error saving transaction.");
        }

        closeModal();
        fetchDashboardData();
    } catch (err) {
        handleError(err, "Save failed");
    }
}

// 6. Delete Transaction
async function deleteTx(txId) {
    if (!confirm("Are you sure you want to delete this transaction entry?")) return;
    clearError();

    try {
        const res = await fetch(`/api/transactions/${txId}`, { method: "DELETE" });
        if (!res.ok) {
            const errData = await res.json().catch(() => ({}));
            throw new Error(errData.detail || "Failed to delete transaction");
        }
        fetchDashboardData();
    } catch (err) {
        handleError(err, "Delete failed");
    }
}

// 7. Export CSV
function exportCsv() {
    const params = buildFilterParams();
    window.location.href = `/api/export/csv?${params.toString()}`;
}

// 8. Seed Sample Data
async function seedData() {
    clearError();
    try {
        const res = await fetch("/api/seed", { method: "POST" });
        if (!res.ok) throw new Error("Failed to seed sample data.");
        fetchDashboardData();
    } catch (err) {
        handleError(err, "Seed failed");
    }
}

// Helper: Build Filter Params
function buildFilterParams() {
    const params = new URLSearchParams();
    if (filterMonth.value) params.append("month", filterMonth.value);
    if (filterCategory.value && filterCategory.value !== "all") params.append("category", filterCategory.value);
    if (filterType.value && filterType.value !== "all") params.append("type", filterType.value);
    if (filterSearch.value.trim()) params.append("search", filterSearch.value.trim());
    return params;
}

// Helper: Reset Filters
function resetFilters() {
    filterMonth.value = "";
    filterCategory.value = "all";
    filterType.value = "all";
    filterSearch.value = "";
    currentPage = 1;
    fetchDashboardData();
}

// Helper: Category Breakdown Rendering
function renderCategoryBreakdown(categories) {
    categoryBreakdownList.innerHTML = "";

    if (!categories || categories.length === 0) {
        categoryBreakdownList.innerHTML = `
            <div class="empty-state" style="padding: 20px 0;">
                <p>No expense breakdown for this period.</p>
            </div>
        `;
        return;
    }

    categories.forEach((cat) => {
        const item = document.createElement("div");
        item.className = "category-item";
        item.innerHTML = `
            <div class="category-meta">
                <span class="category-name">
                    <span class="category-dot"></span> ${escapeHtml(cat.category)}
                </span>
                <span><strong>${formatAmount(cat.amount)}</strong> (${cat.percentage}%)</span>
            </div>
            <div class="progress-bar-bg">
                <div class="progress-bar-fill" style="width: ${cat.percentage}%;"></div>
            </div>
        `;
        categoryBreakdownList.appendChild(item);
    });
}

// Helper: Modal Management
function openModal(txId = null) {
    clearError();
    editingTxId = txId;

    if (txId) {
        modalTitle.innerHTML = '<i class="fa-solid fa-pen-to-square"></i> Edit Transaction';
        const tx = currentTransactions.find(t => t.id === txId);
        if (tx) {
            txIdInput.value = tx.id;
            txTypeInput.value = tx.type;
            txAmountInput.value = tx.amount;
            txCategoryInput.value = tx.category;
            txDateInput.value = tx.date;
            txDescriptionInput.value = tx.description || "";
        }
    } else {
        modalTitle.innerHTML = '<i class="fa-solid fa-plus-circle"></i> Add Transaction';
        txForm.reset();
        txIdInput.value = "";
        txDateInput.value = new Date().toISOString().split("T")[0];
    }

    txModal.classList.add("active");
}

function closeModal() {
    txModal.classList.remove("active");
    editingTxId = null;
}

// Helper: Loading & Error Banner Handling
function setLoadingState(isLoading) {
    if (loadingSpinner) {
        loadingSpinner.style.display = isLoading ? "block" : "none";
    }
}

function handleError(err, contextMsg = "Error") {
    console.error(contextMsg, err);
    if (errorBanner && errorMessage) {
        errorMessage.textContent = `${contextMsg}: ${err.message || err}`;
        errorBanner.style.display = "flex";
    }
}

function clearError() {
    if (errorBanner) {
        errorBanner.style.display = "none";
    }
}

// Formatting & Sanitization Utilities
function formatAmount(amount) {
    const val = typeof amount === "number" ? amount : parseFloat(amount);
    const formatted = Math.abs(val || 0).toLocaleString('en-IN', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });
    return `${selectedCurrencySymbol}${formatted}`;
}

function debounce(func, wait) {
    let timeout;
    return function (...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, args), wait);
    };
}

function escapeHtml(str) {
    if (!str) return '';
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}
