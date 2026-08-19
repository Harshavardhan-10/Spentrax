# Deploy to Render

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

1. Go to https://render.com -> sign up / log in
2. **New -> Blueprint** -> connect your GitHub repo
3. Render reads `render.yaml` and creates three resources automatically:

| Resource | Type | URL |
|---|---|---|
| `spentrax-db` | PostgreSQL (free) | internal |
| `spentrax-api` | Web service | https://spentrax-api.onrender.com |
| `spentrax-web` | Static site | https://spentrax-web.onrender.com |

4. Click **Apply**. First deploy takes ~5-10 minutes (installs deps + runs
   `alembic upgrade head` which creates all tables).

## 3. Done

Open https://spentrax-web.onrender.com -> register a new account and use the app.

## Optional: enable real AI insights

In the Render dashboard (`spentrax-api` -> Environment), set:

- `AI_PROVIDER` = `openai`
- `AI_API_KEY` = your OpenAI key

The app keeps working with `rule_based` (no key) otherwise.

## Local development (unchanged)

```bash
# Backend  (.env: DATABASE_URL=sqlite:///./expense.db)
cd Backend && venv\Scripts\activate
alembic upgrade head
uvicorn main:app --reload          # http://127.0.0.1:8000

# Frontend (.env: VITE_API_URL=http://localhost:8000)
cd Frontend && npm run dev         # http://localhost:5173
```

## Alternative: Docker

```bash
cd Backend
docker build -t spentrax-api .     # Postgres URL + secret via env at run time
docker run -p 8000:8000 -e DATABASE_URL=... -e SECRET_KEY=... spentrax-api
```

> Note: `render.yaml` and `Dockerfile` are the source of truth for deploys;
> backend config is 100% env-driven (`app/core/config.py`), no code changes needed.