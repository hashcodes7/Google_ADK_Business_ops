# Milestone 1: Run & Execution Guide (`v1_run_steps.md`)

> ### ⚡ Primary Command
> ```powershell
> python run.py
> ```
> *(Or direct Uvicorn launch: `uvicorn src.main:app --reload --host 0.0.0.0 --port 8000`)*

This step-by-step operational guide walks you through setting up, launching, trying, and verifying the **Milestone 1** backend application from scratch.

---

## Prerequisites

Before starting, ensure you have:
- **Python**: Version `3.11` or `3.12` installed (`python --version`)
- **PowerShell** or **Command Prompt** (on Windows) or **Terminal** (on macOS/Linux)
- **Git** installed

---

## Step 1: Open Project Terminal

Open PowerShell and navigate to the project root directory:

```powershell
cd C:\Users\Harsh\HiHarsh\Coding\Python\Business_ops_GoogleADK
```

---

## Step 2: Activate the Virtual Environment

The project uses an isolated Python virtual environment inside `.venv/`.

### On Windows (PowerShell):
```powershell
.\.venv\Scripts\Activate.ps1
```

> **Note on PowerShell Script Execution Policy**:
> If PowerShell reports `cannot be loaded because running scripts is disabled on this system`, run:
> ```powershell
> Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
> ```
> Then re-run `.\.venv\Scripts\Activate.ps1`.

### On Windows (Command Prompt - cmd.exe):
```cmd
.venv\Scripts\activate.bat
```

### Alternatively (Direct Execution without Activation):
You can prefix all commands directly using the venv executable:
```powershell
.\.venv\Scripts\python.exe <script>
```

---

## Step 3: Verify Installed Dependencies

If you are setting this up fresh on a new machine, install the dependencies from `requirements.txt`:

```powershell
pip install -r requirements.txt
```

*(Packages installed: `fastapi`, `httpx`, `pydantic`, `pydantic-settings`, `uvicorn`, `rich`, `python-dotenv`, `pytest`, `pytest-asyncio`)*

---

## Step 4: Verify Environment Configuration

Ensure `.env.dev` exists in the project root:

```ini
# .env.dev
APP_ENV=dev
ECOMMERCE_API_BASE_URL=https://fakestoreapi.com
HOST=0.0.0.0
PORT=8000
```

---

## Step 5: Start the Backend Server

Launch the local development runner with hot-reloading:

```powershell
python run.py -e dev
```

*(Or via direct path: `.\.venv\Scripts\python.exe run.py -e dev`)*

### Expected Console Output:
```text
[run.py] Starting local Uvicorn server in DEV mode...
[run.py] Network Bind    : http://0.0.0.0:8000
[run.py] Local Access    : http://localhost:8000
[run.py] Swagger UI Docs : http://localhost:8000/docs
INFO:     Will watch for changes in: ['C:\\Users\\Harsh\\HiHarsh\\Coding\\Python\\Business_ops_GoogleADK']
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [1234] using WatchFiles
================================================================
  Multi-Agent Business Orchestration Platform Starting
  Environment       : DEV
  Bound Host / Port : 0.0.0.0:8000
  Application URL   : http://localhost:8000
  API Docs (Swagger): http://localhost:8000/docs
  Ecommerce Base URL: https://fakestoreapi.com
  HTTP Timeout      : 15.0s
================================================================
INFO:     Application startup complete.
```

---

## Step 6: Try the Endpoints (Interactive UI)

While the server is running, open your web browser:

### 1. Interactive Swagger Documentation
👉 **[http://localhost:8000/docs](http://localhost:8000/docs)**

- Click on any endpoint (e.g. `GET /api/v1/products`)
- Click **"Try it out"**
- Enter parameters (e.g., `limit: 3`, `sort: desc`)
- Click **"Execute"** to see live JSON responses returned from FakeStoreAPI!

### 2. Alternative ReDoc Documentation
👉 **[http://localhost:8000/redoc](http://localhost:8000/redoc)**

---

## Step 7: Try the Endpoints (Terminal / cURL)

Open a **separate** terminal window and run any of the commands below:

### 1. System Health & Liveness
```powershell
curl http://localhost:8000/health
```
**Expected Response:**
```json
{"status":"healthy"}
```

```powershell
curl http://localhost:8000/
```
**Expected Response:**
```json
{"status":"ok","environment":"dev","ecommerce_api":"https://fakestoreapi.com"}
```

---

### 2. List Products (With Limit & Sort)
Fetch the 2 highest-ID products:
```powershell
curl "http://localhost:8000/api/v1/products?limit=2&sort=desc"
```
**Expected Response Sample:**
```json
[
  {
    "id": 20,
    "title": "DANVOUY Womens T Shirt Casual Cotton Short",
    "price": 12.99,
    "description": "95%Cotton,5%Spandex, Features: Casual, Short Sleeve...",
    "category": "women's clothing",
    "image": "https://fakestoreapi.com/img/61pHAEJ4NML._AC_UX679_.jpg",
    "rating": {"rate": 3.6, "count": 145}
  },
  {
    "id": 19,
    "title": "Opna Women's Short Sleeve Moisture",
    "price": 7.95,
    "description": "100% Polyester, Machine wash, 100% cationic polyester...",
    "category": "women's clothing",
    "image": "https://fakestoreapi.com/img/51eg55uWmdL._AC_UX679_.jpg",
    "rating": {"rate": 4.5, "count": 146}
  }
]
```

---

### 3. List All Product Categories
```powershell
curl http://localhost:8000/api/v1/products/categories
```
**Expected Response:**
```json
["electronics","jewelery","men's clothing","women's clothing"]
```

---

### 4. Filter Products by Category
```powershell
curl "http://localhost:8000/api/v1/products/category/jewelery?limit=2"
```
**Expected Response Sample:**
```json
[
  {
    "id": 5,
    "title": "John Hardy Women's Legends Naga Gold & Silver Dragon Station Chain Bracelet",
    "price": 695.0,
    "description": "From our Legends Collection, the Naga was inspired by the mythical water dragon...",
    "category": "jewelery",
    "image": "https://fakestoreapi.com/img/71pWzhdJNwL._AC_UL640_QL65_ML3_.jpg",
    "rating": {"rate": 4.6, "count": 400}
  }
]
```

---

### 5. Fetch Single Product by ID
```powershell
curl http://localhost:8000/api/v1/products/1
```
**Expected Response:**
```json
{
  "id": 1,
  "title": "Fjallraven - Foldsack No. 1 Backpack, Fits 15 Laptops",
  "price": 109.95,
  "description": "Your perfect pack for everyday use and walks in the forest...",
  "category": "men's clothing",
  "image": "https://fakestoreapi.com/img/81fPKd-2AYL._AC_SL1500_.jpg",
  "rating": {"rate": 3.9, "count": 120}
}
```

---

### 6. Verify 404 Error Handling
Try requesting a product ID that does not exist:
```powershell
curl http://localhost:8000/api/v1/products/99999
```
**Expected Response (HTTP 404):**
```json
{"detail":"Product with ID 99999 not found."}
```

---

## Step 8: Run the Automated Verification Suites

You can verify the entire backend automatically at any time using two built-in suites:

### 1. Offline Pytest Suite (Unit & Mock Tests)
Tests schema validation, router error mappings, and dependency overrides without calling external networks:
```powershell
.\.venv\Scripts\pytest -v
```
**Expected Result:**
```text
======================== 9 passed in ~5s =========================
```

---

### 2. Live End-to-End Verification (Calls Real FakeStoreAPI)
Executes a full integration check against `https://fakestoreapi.com`:
```powershell
.\.venv\Scripts\python.exe -m tests.verify_live_fakestore
```
**Expected Result:**
```text
==================================================
 ALL LIVE VERIFICATION CHECKS PASSED SUCCESSFULLY!
==================================================
```

---

## Step 9: Stopping the Server

To stop the server at any time:
- In the terminal running Uvicorn, press `Ctrl + C`.
- The application will execute the ASGI lifespan shutdown hook:
```text
Shutting down Multi-Agent Business Orchestration Platform cleanly...
INFO:     Finished server process [1234]
```

---

## Quick Reference Summary

| Action | Command / URL |
| :--- | :--- |
| **Start Dev Server** | `python run.py -e dev` |
| **Interactive Docs** | [http://localhost:8000/docs](http://localhost:8000/docs) |
| **Health Check** | [http://localhost:8000/health](http://localhost:8000/health) |
| **Unit Tests** | `pytest -v` |
| **Live Integration Test** | `python -m tests.verify_live_fakestore` |
