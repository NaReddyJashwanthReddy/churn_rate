// ---------------------------------------------------------------------------
// Configuration
// ---------------------------------------------------------------------------

// Point this at your FastAPI backend (see backend/app.py).
const API_BASE = "http://localhost:8000";

// ---------------------------------------------------------------------------
// Element refs
// ---------------------------------------------------------------------------

const runDemoBtn = document.getElementById("runDemoBtn");
const csvFileInput = document.getElementById("csvFileInput");
const fileLabelText = document.getElementById("fileLabelText");
const uploadBtn = document.getElementById("uploadBtn");
const thresholdInput = document.getElementById("thresholdInput");
const statusMsg = document.getElementById("statusMsg");

const dashboard = document.getElementById("dashboard");
const statTotal = document.getElementById("statTotal");
const statChurn = document.getElementById("statChurn");
const statRetained = document.getElementById("statRetained");
const statRate = document.getElementById("statRate");

const fiTableBody = document.getElementById("fiTableBody");
const fiEmpty = document.getElementById("fiEmpty");

const filterTabs = document.getElementById("filterTabs");
const searchInput = document.getElementById("searchInput");
const customerTable = document.getElementById("customerTable");
const customerTableBody = document.getElementById("customerTableBody");
const tableEmpty = document.getElementById("tableEmpty");

const overlay = document.getElementById("overlay");
const detailPanel = document.getElementById("detailPanel");
const detailContent = document.getElementById("detailContent");
const closeDetail = document.getElementById("closeDetail");

// ---------------------------------------------------------------------------
// State
// ---------------------------------------------------------------------------

const state = {
  predictions: [],
  featureImportance: [],
  filter: "all",       // all | churn | retained
  search: "",
  sortKey: "churn_probability",
  sortDir: "desc",      // asc | desc
};

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function setStatus(message, type = "") {
  statusMsg.textContent = message;
  statusMsg.className = "status" + (type ? ` ${type}` : "");
}

function setLoading(isLoading) {
  runDemoBtn.disabled = isLoading;
  uploadBtn.disabled = isLoading || !csvFileInput.files.length;
}

function fmtNum(value, decimals = 0) {
  if (value === null || value === undefined || Number.isNaN(value)) return "—";
  return Number(value).toLocaleString(undefined, {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });
}

function fmtPct(value) {
  if (value === null || value === undefined || Number.isNaN(value)) return "—";
  return `${Math.round(value * 100)}%`;
}

// ---------------------------------------------------------------------------
// API calls
// ---------------------------------------------------------------------------

async function runDemo() {
  setLoading(true);
  setStatus("Running predictions on the demo dataset…");
  try {
    const threshold = parseFloat(thresholdInput.value) || 0.5;
    const res = await fetch(`${API_BASE}/predict-demo?threshold=${threshold}`, {
      method: "POST",
    });
    if (!res.ok) throw new Error((await res.json()).detail || res.statusText);
    const data = await res.json();
    onPredictionsLoaded(data, "Demo dataset");
  } catch (err) {
    setStatus(`Couldn't run the demo: ${err.message}`, "error");
  } finally {
    setLoading(false);
  }
}

async function uploadAndPredict() {
  const file = csvFileInput.files[0];
  if (!file) return;

  setLoading(true);
  setStatus(`Uploading ${file.name}…`);
  try {
    const threshold = parseFloat(thresholdInput.value) || 0.5;
    const formData = new FormData();
    formData.append("file", file);
    formData.append("threshold", threshold);

    const res = await fetch(`${API_BASE}/predict-upload`, {
      method: "POST",
      body: formData,
    });
    if (!res.ok) throw new Error((await res.json()).detail || res.statusText);
    const data = await res.json();
    onPredictionsLoaded(data, file.name);
  } catch (err) {
    setStatus(`Upload failed: ${err.message}`, "error");
  } finally {
    setLoading(false);
  }
}

function onPredictionsLoaded(data, sourceLabel) {
  state.predictions = data.predictions || [];
  state.featureImportance = data.feature_importance || [];

  if (!state.predictions.length) {
    setStatus(`${sourceLabel}: no customers found in the response.`, "error");
    dashboard.classList.add("hidden");
    return;
  }

  setStatus(`${sourceLabel}: scored ${data.summary.total} customers.`, "success");
  dashboard.classList.remove("hidden");

  renderSummary(data.summary);
  renderFeatureImportance(state.featureImportance);
  renderCustomerTable();
}

// ---------------------------------------------------------------------------
// Rendering
// ---------------------------------------------------------------------------

function renderSummary(summary) {
  statTotal.textContent = fmtNum(summary.total);
  statChurn.textContent = fmtNum(summary.churn);
  statRetained.textContent = fmtNum(summary.retained);
  statRate.textContent = `${summary.churn_rate}%`;
}

function renderFeatureImportance(features) {
  fiTableBody.innerHTML = "";

  if (!features.length) {
    fiEmpty.classList.remove("hidden");
    return;
  }
  fiEmpty.classList.add("hidden");

  const maxPct = Math.max(...features.map((f) => f.importance_pct || 0), 1);

  features.forEach((f) => {
    const tr = document.createElement("tr");
    const barWidth = ((f.importance_pct || 0) / maxPct) * 100;
    tr.innerHTML = `
      <td>${f.rank}</td>
      <td>${escapeHtml(f.feature)}</td>
      <td>
        <div class="fi-bar-wrap">
          <div class="fi-bar-track"><div class="fi-bar-fill" style="width:${barWidth}%"></div></div>
          <span class="fi-pct">${f.importance_pct}%</span>
        </div>
      </td>
    `;
    fiTableBody.appendChild(tr);
  });
}

function getFilteredSortedRows() {
  let rows = state.predictions;

  if (state.filter === "churn") rows = rows.filter((r) => r.churn_flag);
  else if (state.filter === "retained") rows = rows.filter((r) => !r.churn_flag);

  if (state.search) {
    const q = state.search.toLowerCase();
    rows = rows.filter((r) => String(r.customer_id ?? "").toLowerCase().includes(q));
  }

  const { sortKey, sortDir } = state;
  rows = [...rows].sort((a, b) => {
    let av = a[sortKey];
    let bv = b[sortKey];
    if (typeof av === "string") av = av.toLowerCase();
    if (typeof bv === "string") bv = bv.toLowerCase();
    if (av === undefined || av === null) av = -Infinity;
    if (bv === undefined || bv === null) bv = -Infinity;
    if (av < bv) return sortDir === "asc" ? -1 : 1;
    if (av > bv) return sortDir === "asc" ? 1 : -1;
    return 0;
  });

  return rows;
}

function renderCustomerTable() {
  const rows = getFilteredSortedRows();
  customerTableBody.innerHTML = "";

  if (!rows.length) {
    tableEmpty.classList.remove("hidden");
  } else {
    tableEmpty.classList.add("hidden");
  }

  rows.forEach((r) => {
    const tr = document.createElement("tr");
    const badge = r.churn_flag
      ? `<span class="badge risk">At risk · ${fmtPct(r.churn_probability)}</span>`
      : `<span class="badge safe">Retained · ${fmtPct(r.churn_probability)}</span>`;

    tr.innerHTML = `
      <td>${escapeHtml(String(r.customer_id ?? "—"))}</td>
      <td>${escapeHtml(String(r.plan_type ?? "—"))}</td>
      <td>${fmtNum(r.tenure_days)}</td>
      <td>${fmtNum(r.watch_hours_30d, 1)}</td>
      <td>${fmtNum(r.login_count_30d)}</td>
      <td>${fmtNum(r.days_since_last_login)}</td>
      <td>${badge}</td>
    `;
    tr.addEventListener("click", () => openDetail(r));
    customerTableBody.appendChild(tr);
  });

  // reflect current sort in header arrows
  customerTable.querySelectorAll("th[data-sort]").forEach((th) => {
    th.classList.remove("sorted", "asc");
    if (th.dataset.sort === state.sortKey) {
      th.classList.add("sorted");
      if (state.sortDir === "asc") th.classList.add("asc");
    }
  });
}

const FIELD_LABELS = {
  customer_id: "Customer ID",
  plan_type: "Plan",
  tenure_days: "Tenure (days)",
  watch_hours_30d: "Watch hours (30d)",
  login_count_30d: "Logins (30d)",
  days_since_last_login: "Days since last login",
  support_ticket_count: "Support tickets",
  payment_failure_count: "Payment failures",
  monthly_revenue: "Monthly revenue",
  churn_probability: "Churn probability",
  churn_flag: "Churn flag",
};

const FIELD_ORDER = [
  "plan_type",
  "tenure_days",
  "watch_hours_30d",
  "login_count_30d",
  "days_since_last_login",
  "support_ticket_count",
  "payment_failure_count",
  "monthly_revenue",
];

function openDetail(record) {
  const riskBadge = record.churn_flag
    ? `<span class="badge risk">At risk</span>`
    : `<span class="badge safe">Retained</span>`;

  let rowsHtml = "";
  FIELD_ORDER.forEach((key) => {
    if (record[key] === undefined) return;
    const value = key === "monthly_revenue" ? `$${fmtNum(record[key], 2)}` : fmtNum(record[key], key === "watch_hours_30d" ? 1 : 0);
    rowsHtml += `
      <div class="detail-row">
        <span class="label">${FIELD_LABELS[key] || key}</span>
        <span class="value">${value}</span>
      </div>`;
  });

  rowsHtml += `
    <div class="detail-row">
      <span class="label">Churn probability</span>
      <span class="value">${fmtPct(record.churn_probability)}</span>
    </div>`;

  detailContent.innerHTML = `
    <h3>${escapeHtml(String(record.customer_id ?? "Customer"))}</h3>
    <p style="margin:0 0 16px;">${riskBadge}</p>
    ${rowsHtml}
  `;

  overlay.classList.remove("hidden");
  detailPanel.classList.add("open");
  detailPanel.setAttribute("aria-hidden", "false");
}

function closeDetailPanel() {
  overlay.classList.add("hidden");
  detailPanel.classList.remove("open");
  detailPanel.setAttribute("aria-hidden", "true");
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}

// ---------------------------------------------------------------------------
// Event listeners
// ---------------------------------------------------------------------------

runDemoBtn.addEventListener("click", runDemo);

csvFileInput.addEventListener("change", () => {
  const file = csvFileInput.files[0];
  fileLabelText.textContent = file ? file.name : "Choose CSV file";
  uploadBtn.disabled = !file;
});

uploadBtn.addEventListener("click", uploadAndPredict);

filterTabs.addEventListener("click", (e) => {
  const btn = e.target.closest(".tab");
  if (!btn) return;
  filterTabs.querySelectorAll(".tab").forEach((t) => t.classList.remove("active"));
  btn.classList.add("active");
  state.filter = btn.dataset.filter;
  renderCustomerTable();
});

let searchDebounce;
searchInput.addEventListener("input", () => {
  clearTimeout(searchDebounce);
  searchDebounce = setTimeout(() => {
    state.search = searchInput.value.trim();
    renderCustomerTable();
  }, 150);
});

customerTable.querySelectorAll("th[data-sort]").forEach((th) => {
  th.addEventListener("click", () => {
    const key = th.dataset.sort;
    if (state.sortKey === key) {
      state.sortDir = state.sortDir === "asc" ? "desc" : "asc";
    } else {
      state.sortKey = key;
      state.sortDir = "desc";
    }
    renderCustomerTable();
  });
});

closeDetail.addEventListener("click", closeDetailPanel);
overlay.addEventListener("click", closeDetailPanel);
document.addEventListener("keydown", (e) => {
  if (e.key === "Escape") closeDetailPanel();
});
