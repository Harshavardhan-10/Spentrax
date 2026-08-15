# Smart Expense & Budget Manager

A full-stack expense tracking application with budgets, statistical recurring-expense detection, spending analytics, and AI-powered insights. Built with **FastAPI + SQLAlchemy + SQLite** on the backend and **React + Vite + Chart.js** on the frontend.

## Features

- **Authentication** — register, login, JWT sessions, profile management and password change (bcrypt + PyJWT).
- **Expenses** — full CRUD with category, payment method, filters (category / date range / amount range / keyword search), sorting and pagination.
- **Categories** — 11 seeded default categories plus user-defined custom categories (defaults cannot be modified or deleted).
- **Budgets** — per-category monthly budgets with live utilization and status: `HEALTHY`, `WARNING`, `CRITICAL`, `EXCEEDED`.
- **Recurring expenses** — statistical detection of subscriptions (same merchant, similar amount, regular interval) with confidence scoring; toggle or delete detected entries.
- **Analytics** — monthly totals and averages, highest/lowest expense, top category, category breakdown with percentages, 12-month trends and month-over-month comparison.
- **CSV import / export** — round-trip import with row validation, duplicate detection and error reporting.
- **AI insights** — monthly plain-language summary, budget recommendations (based on 3-month averages), spending insights, and anomaly explanations. Rules-based by default; a swappable OpenAI-compatible provider is available via environment variables.
- **Dashboard** — summary cards, spending trend, category breakdown, budget utilization, recent expenses, AI insights and detected recurring expenses.

## Architecture

```
Smart_Expense_Manager/
├── Backend/
│   ├── main.py                  # FastAPI app: routers, CORS, lifespan, error handlers
│   ├── alembic.ini              # Alembic configuration
│   ├── migrations/              # Schema migrations (one initial migration)
│   ├── app/
│   │   ├── api/                 # Routers: auth, users, categories, expenses, budgets,
│   │   │                        #   recurring, analytics, dashboard, csv, ai
│   │   ├── core/                # config, database, security, dependencies, exceptions, logging
│   │   ├── models/              # SQLAlchemy ORM models
│   │   ├── schemas/             # Pydantic request/response schemas
│   │   ├── services/            # Business logic
│   │   │   └── ai/              # AI provider abstraction + rule-based fallbacks + prompts
│   │   ├── ml/                  # Statistical recurring & anomaly detection
│   │   └── utils/               # response envelope, date utils, CSV helpers
│   └── tests/                   # pytest suite (82 tests)
└── Frontend/
    ├── src/
    │   ├── components/          # Common + feature components
    │   ├── pages/               # Login, Register, Dashboard, Expenses, Budgets, ...
    │   ├── services/            # Axios API clients (one per resource)
    │   ├── context/             # AuthContext, AppContext (categories)
    │   ├── hooks/               # useAuth, useExpenses, useBudgets, useAI
    │   └── utils/               # formatCurrency, formatDate, constants
    └── index.html / vite.config.js
```

Key design decisions:

- Every API response uses a consistent envelope: success `{success: true, data, message?}`, error `{success: false, message, error_code}`.
- User identity always comes from the JWT; the client never supplies a user id, and all queries are scoped to the authenticated user.
- Detection (recurring, anomalies) is purely statistical. The AI layer only explains or summarizes — it never decides or mutates data, and it only ever receives aggregated, user-scoped data.
- The AI provider is swappable (`AI_PROVIDER`, `AI_API_KEY`, `AI_MODEL`). When unset, deterministic rule-based logic keeps every feature working.

## Setup

### Backend

Requirements: Python 3.10+.

```bash
cd Backend
python -m venv venv
venv\Scripts\activate            # Windows (PowerShell)
pip install -r requirements.txt

copy .env.example .env           # then fill in a real SECRET_KEY
alembic upgrade head             # create the SQLite schema

uvicorn main:app --reload        # http://localhost:8000  (docs at /docs)
```

Environment variables (`Backend/.env`):

| Variable | Default | Description |
| --- | --- | --- |
| `SECRET_KEY` | — | JWT signing secret (must be set) |
| `DATABASE_URL` | `sqlite:///./expense.db` | SQLAlchemy database URL |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `1440` | JWT lifetime in minutes |
| `CORS_ORIGINS` | `http://localhost:5173,...` | Allowed frontend origins |
| `AI_PROVIDER` | `` (empty) | `openai` to enable an LLM provider |
| `AI_API_KEY` / `AI_BASE_URL` / `AI_MODEL` | — | Provider credentials (server-side only) |

### Frontend

Requirements: Node.js 18+.

```bash
cd Frontend
npm install
npm run dev                      # http://localhost:5173
```

## Migrations

Schema changes are handled with Alembic:

```bash
cd Backend
alembic revision --autogenerate -m "describe change"
alembic upgrade head
```

The test suite creates its own temporary database, so migrations are not required to run tests.

## Testing

```bash
cd Backend
venv\Scripts\python -m pytest tests -q
```

The suite (82 tests) covers authentication (duplicate email, invalid credentials, expired tokens), user profile and password change, categories (defaults, custom CRUD, access rules), expenses (CRUD, filters, pagination, validation, cross-user isolation), budgets (duplication, usage reporting, statuses), recurring detection, analytics, CSV import/export, AI endpoints, and security primitives.

## API summary

| Method | Path | Description |
| --- | --- | --- |
| POST | `/auth/register`, `/auth/login` | Register / login (returns JWT) |
| GET/POST | `/categories` | List / create categories |
| POST/GET | `/expenses` | Create / list (filter, search, paginate) |
| PUT/DELETE | `/expenses/{id}` | Update / delete an expense |
| POST/GET | `/budgets` | Create / list budgets with usage |
| PUT/DELETE | `/budgets/{id}` | Update / delete a budget |
| POST | `/recurring/detect` | Run recurring-expense detection |
| GET | `/recurring` | List detected recurring expenses |
| GET | `/analytics/monthly`, `/categories`, `/trends`, `/comparison` | Analytics |
| GET | `/dashboard` | Dashboard aggregate |
| POST/GET | `/csv/import`, `/csv/export` | CSV import / export |
| POST | `/ai/categorize` | Suggest a category for a transaction |
| GET | `/ai/insights?refresh=true`, `/ai/summary`, `/ai/recommendations`, `/ai/anomalies` | AI features |
| PUT | `/users/me` | Update profile |
| POST | `/users/me/change-password` | Change password |

## Security notes

- Passwords are hashed with bcrypt; JWT tokens are signed with the app secret and expire.
- API keys for the optional AI provider are read from the backend `.env` only and never sent to the browser.
- All user data is isolated per account; cross-user access attempts return `404`/`403`.
