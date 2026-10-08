# 👛 PocketLedger - Personal Expense Tracker

PocketLedger is a personal expense-tracking application built with **FastAPI**, **SQLAlchemy**, **SQLite / PostgreSQL**, and a **Glassmorphism Web Dashboard**. It allows users to record income and expense entries, categorize transactions, view monthly financial summaries, and export transaction data as CSV.

---

## 📌 Features

- 💵 **Income & Expense Tracking**: Record financial entries with amounts, categories, dates, and descriptions.
- 🏷️ **Category Organization**: Categorize entries into *Food, Travel, Rent, Shopping, Bills, Salary, Freelance, Investment, Other*.
- 📊 **Monthly Summaries**: View total income, total expenses, remaining balance, and visual category spending breakdowns.
- 🔍 **Filtering & Pagination**: Search by description and filter by month (`YYYY-MM`), category, or type (`income`/`expense`) with pagination.
- 💱 **Currency Boundary**: Presentation support for INR (`₹`), USD (`$`), EUR (`€`), and GBP (`£`).
- 📥 **CSV Export**: Stream CSV downloads using exact active filter parameters.
- 🩺 **Health & Readiness Probes**: Endpoint probes (`/health` and `/ready`) for system monitoring.

---

## ⚙️ Environment Variables

PocketLedger reads configuration from environment variables (or `.env` file):

| Variable | Default Value | Description |
| :--- | :--- | :--- |
| `APP_NAME` | `PocketLedger` | Name of the application |
| `APP_VERSION` | `0.1.0` | Application version |
| `APP_ENV` | `development` | Environment mode (`development`, `testing`, `production`) |
| `APP_PORT` | `8000` | Port for the Uvicorn web server |
| `LOG_LEVEL` | `INFO` | Logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |
| `DATABASE_URL` | `sqlite:///./pocketledger.db` | SQLAlchemy database connection string |

---

## 🚀 Setup & Installation

### 1. Create Python Environment

```bash
# Create virtual environment named .venv
python -m venv .venv

# Activate virtual environment
# On Linux / macOS:
source .venv/bin/activate

# On Windows (PowerShell):
.\.venv\Scripts\Activate.ps1
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Seed Sample Data (Optional Development Command)

```bash
python scripts/seed.py
```

---

## 💻 Running the Application

Start the local Uvicorn development server:

```bash
python -m uvicorn app.main:app --reload --port 8000
```

- **Web Dashboard**: [http://localhost:8000](http://localhost:8000)
- **Interactive OpenAPI / Swagger Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🧪 Running Automated Tests

Run the full test suite with `pytest`:

```bash
pytest
```

---

## 🔌 API Endpoint Examples

| Method | Endpoint | Description | Example Request |
| :--- | :--- | :--- | :--- |
| `GET` | `/health` | Liveness check | `curl http://localhost:8000/health` |
| `GET` | `/ready` | Database readiness check | `curl http://localhost:8000/ready` |
| `GET` | `/api/transactions` | Paginated list with filters | `curl "http://localhost:8000/api/transactions?month=2026-10&page=1&limit=20"` |
| `POST` | `/api/transactions` | Create new entry | `curl -X POST http://localhost:8000/api/transactions -H "Content-Type: application/json" -d '{"type":"income","amount":50000.00,"category":"Salary","date":"2026-10-01"}'` |
| `GET` | `/api/transactions/{id}` | Fetch single transaction | `curl http://localhost:8000/api/transactions/1` |
| `PUT` | `/api/transactions/{id}` | Update transaction | `curl -X PUT http://localhost:8000/api/transactions/1 -H "Content-Type: application/json" -d '{"amount":55000.00}'` |
| `DELETE` | `/api/transactions/{id}` | Delete transaction | `curl -X DELETE http://localhost:8000/api/transactions/1` |
| `GET` | `/api/summary` | Monthly summary calculation | `curl "http://localhost:8000/api/summary?month=2026-10&currency=INR"` |
| `GET` | `/api/export/csv` | Download CSV export | `curl "http://localhost:8000/api/export/csv?month=2026-10" -o export.csv` |
