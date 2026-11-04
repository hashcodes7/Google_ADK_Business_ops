# Milestone 8: Handcrafted Utilitarian Frontend, Password Gate & Offline Fallback (`v8_frontend_and_auth_gate.md`)

> ### ⚡ Primary Command
> ```powershell
> python run.py --env dev
> ```
> *(Starts backend on `http://127.0.0.1:8000`. Then open `frontend/index.html` in browser)*

This document details **Milestone 8 (v8)**: Developing an isolated, human-built, handcrafted utilitarian frontend interface, an authentication password gate, an offline fallback screen, and hot-swappable login endpoints.

---

## 1. Architectural Overview & Frontend Isolation

The frontend is strictly decoupled and maintained inside the isolated [`frontend/`](../frontend/) directory:

```
frontend/
├── index.html            # 4-zone layout (Navigation, Topbar, Main Workspace, Assistant)
├── css/
│   └── style.css         # Handcrafted blueprint/typewriter aesthetic (Courier Prime + IBM Plex Sans)
├── js/
│   ├── api.js            # Inbound HTTP adapter with Bearer Auth & offline health probe
│   ├── dashboard.js      # Main controller: screen toggling, manual retry, KPIs, and auth switcher
│   ├── products.js       # Product catalog views: real-time filter, SKU inspect, and Admin modal
│   ├── carts.js          # Customer shopping carts: live feed & AI inspection trigger
│   └── assistant.js      # AI Business Assistant (Copilot) chat interface & quick prompts
└── assets/               # Isolated directory for static images and brand media
```

---

## 2. Core Features Implemented in v8

### A. Handcrafted, Human-Built UI Aesthetic
- Replaced synthetic, hyper-perfect gradients and neon glassmorphism with an intentional, tactile **workshop / blueprint aesthetic**:
  - **Color Palette**: Warm paper tones (`#F7F5F0`), Manila folder sidebars (`#EFECE6`), drafted ink borders (`#292524`), and carpenter terracotta accents (`#C2410C`).
  - **Typography**: Paired mechanical typewriter font (**Courier Prime**) for headers, buttons, tags, and IDs with **IBM Plex Sans** for readable body content.
  - **Physical Feedback**: Tactile offset drop shadows (`2px 2px 0px #1C1917`), subtle gridded drafting paper backgrounds, and organic, slightly imperfect corner radii.

### B. Offline Fallback Screen
- When the FastAPI backend is not active, the application automatically displays a clear, informative **Offline Fallback Screen**:
  - Informs the user that the service is offline.
  - Displays the command required to run: `python run.py --env dev`.
  - Includes a manual **"Retry Connection"** button (with no annoying automatic polling loops).

### C. Standard Password Gate (`123456`)
- Integrated a password authentication gate:
  - Default temporary password for all operator accounts: `123456`.
  - Endpoint: `POST /api/v1/auth/login` accepts `{ username, password }` and returns token + role metadata.
  - Built-in accounts:
    - **`user49`** ➔ `token-business-49` (Role: `Business`)
    - **`admin`** ➔ `token-admin-01` (Role: `Admin`)
  - A clean "Sign out" button in the top bar allows returning to the login gate at any time.

### D. CORS & Bootstrap URL Announcement
- FastAPI configuration (`app/main.py`) includes `CORSMiddleware` supporting requests from any local development server or file origin.
- Server bootstrap (`run.py` and application `lifespan`) prints:
  ```text
  ⚡ Starting Business Operations Backend (dev)
  backend URL is : http://127.0.0.1:8000
  ```

---

## 3. Verification

Run the full hexagonal RBAC test suite to ensure no backend regressions:
```powershell
pytest tests/test_hexagonal_architecture.py -s -v --env-file dev
```

Expected output:
- `💚 [Result] Auth Guard -> test_hexagonal_architecture.py -> None context rejected with AuthenticationException`
- `💚 [Result] RBAC Read -> test_hexagonal_architecture.py -> Role.BUSINESS permitted for PRODUCTS_READ`
- `💚 [Result] RBAC Selective Guard -> test_hexagonal_architecture.py -> Role.BUSINESS denied PRODUCTS_WRITE`
- `💚 [Result] User-Only API -> test_hexagonal_architecture.py -> POST /users restricted to Admin, denied to Business`
- `💚 [Result] Agent-Only API -> test_hexagonal_architecture.py -> inspect_cart_by_id executed successfully via shared service`
- `💚 [Result] Agent Inbound Adapter -> test_hexagonal_architecture.py -> ADK tools executed with agent context`
