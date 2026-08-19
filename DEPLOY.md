# Deploy to Render (lifetime-free)

## Free-stack overview

| Piece | Where | Cost |
|---|---|---|
| Frontend (static) | Render static site `spentrax-web` | free, forever, always on |
| API (FastAPI) | Render free web service `spentrax-api` | free, forever (spins down after 15 min idle, cold start ~30-60s) |
| Database (Postgres) | **Neon** free tier (not Render!) | free, forever — Render's free Postgres expires after 30 days |

## 0. Create the database (Neon)

1. https://neon.tech -> sign up -> **Create a project** (any region, e.g. Frankfurt)
2. It shows a connection string like:
   `postgresql://user:pass@ep-xyz.region.neon.tech/spentrax?sslmode=require`
3. Keep it; you'll paste it into Render in step 3.

## 1. Push this project to GitHub

```bash
cd "Smart_Expense_Manager"
git init
git add .
git commit -m "Initial commit"
gh auth login              # one-time GitHub login
gh repo create <your-name>/smart-expense-manager --private --source=. --push
```

## 2. Create the Render Blueprint

1. https://render.com -> **New -> Blueprint** -> connect your GitHub repo
2. Render reads `render.yaml` and creates two free resources:

| Resource | Type | URL |
|---|---|---|
| `spentrax-api` | Web service (free) | https://spentrax-api.onrender.com |
| `spentrax-web` | Static site (free) | https://spentrax-web.onrender.com |

## 3. Wire the database

1. Open **spentrax-api -> Environment**
2. Set `DATABASE_URL` = the Neon connection string from step 0 (make sure it
   ends with `?sslmode=require`)
3. Save + **Manual Deploy -> Clear build cache & deploy** (first deploy runs
   `alembic upgrade head`, which creates all tables on Neon)

## 4. Done

Open https://spentrax-web.onrender.com -> register a new account and use the app.

## Optional: enable real AI insights

In Render dashboard (`spentrax-api` -> Environment), set `AI_PROVIDER=openai`
and `AI_API_KEY` to your OpenAI key. The app keeps working with `rule_based`
(no key) otherwise.

## Local development (unchanged)

```bash
# Backend  (.env: DATABASE_URL=sqlite:///./expense.db)
cd Backend && venv\Scripts\activate
alembic upgrade head
uvicorn main:app --reload          # http://127.0.0.1:8000

# Frontend (.env: VITE_API_URL=http://localhost:8000)
cd Frontend && npm run dev         # http://localhost:5173
```

## Alternative: Docker (Postgres via Neon or any provider)

```bash
cd Backend
docker build -t spentrax-api .     # Postgres URL + secret via env at run time
docker run -p 8000:8000 -e DATABASE_URL=postgresql://... -e SECRET_KEY=... spentrax-api
```

> Note: `render.yaml` and `Dockerfile` are the source of truth for deploys;
> backend config is 100% env-driven (`app/core/config.py`), no code changes needed.
> `psycopg2-binary` is included for Postgres; local dev still uses SQLite.