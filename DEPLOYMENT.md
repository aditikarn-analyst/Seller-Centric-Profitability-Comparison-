# Deployment Guide

Deploy the Marketplace Profitability Analyzer to a free, reproducible stack:

| Tier | Service | What runs there |
|---|---|---|
| **Database** | [Neon](https://neon.tech) | PostgreSQL (schema + seeded `fee_components`) |
| **Backend** | [Render](https://render.com) | FastAPI API (`/api/v1/...`) |
| **Frontend** | [Vercel](https://vercel.com) | TanStack Start SSR app |

```
Browser → Vercel (frontend) → Render (FastAPI) → Neon (PostgreSQL)
```

> The app uses **manually source-verified** fee data, not a live feed. Fees change —
> re-seed and re-verify per cycle. See [`DATA_SOURCES.md`](DATA_SOURCES.md).

Deploy in the order below: the backend needs the database, the frontend needs the
backend URL, and the backend's CORS needs the frontend URL.

---

## Prerequisites

- Code pushed to GitHub (`main`), including `backend/requirements.txt` with `psycopg2-binary`.
- Accounts on Neon, Render, and Vercel (all have free tiers).

---

## 1. Neon — PostgreSQL

1. Create a project at **neon.tech** → choose a region near you.
2. **Connection Details** → copy the **direct (non-pooled)** connection string:
   ```
   postgresql://neondb_owner:PASSWORD@ep-name-123456.us-east-2.aws.neon.tech/neondb?sslmode=require
   ```
3. Keep this — it is your `DATABASE_URL`. `sslmode=require` is required by Neon; SQLAlchemy
   uses the string as-is via `psycopg2`.

---

## 2. Render — FastAPI backend

You can use the **Blueprint** (recommended) or configure manually.

### Option A — Blueprint (`render.yaml`, in the repo root)

1. Render dashboard → **New → Blueprint** → select this repo. Render reads [`render.yaml`](render.yaml).
2. When prompted, fill the `sync: false` secrets:
   - `DATABASE_URL` = your Neon string (step 1)
   - `CORS_ORIGINS` = `http://localhost:8080` *(placeholder; updated in step 4)*
   - `JWT_SECRET_KEY` is generated automatically.
3. **Apply** → wait for the first deploy.

### Option B — Manual Web Service

| Field | Value |
|---|---|
| Root Directory | `backend` |
| Runtime | Python 3 |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
| Health Check Path | `/health` |

Environment variables:

| Key | Value |
|---|---|
| `DATABASE_URL` | Neon string (step 1) |
| `JWT_SECRET_KEY` | a long random string |
| `ENVIRONMENT` | `production` |
| `PYTHON_VERSION` | `3.11.9` |
| `CORS_ORIGINS` | `http://localhost:8080` *(placeholder; updated in step 4)* |

### Initialize the database (once)

After the first deploy, open the service's **Shell** tab and run:

```bash
alembic upgrade head && python -m app.db.seed
```

This creates the schema on Neon and seeds the fee dataset. It is **idempotent** — safe to
re-run after future deploys. *(On a paid instance you can automate this with a
`preDeployCommand` — see the comment in `render.yaml`.)*

### Verify

- `https://YOUR-BACKEND.onrender.com/health` → `{"status":"ok","environment":"production"}`
- `https://YOUR-BACKEND.onrender.com/docs` → Swagger UI

Copy your backend URL for the next step.

---

## 3. Vercel — TanStack Start frontend

1. Vercel → **Add New → Project** → import this repo.
2. Settings:
   | Field | Value |
   |---|---|
   | Root Directory | `front_end` |
   | Framework Preset | Other (auto) |
   | Build Command | `npm run build` |
   | Install Command | `npm install` |
3. Environment Variables:
   | Key | Value |
   |---|---|
   | `VITE_API_URL` | `https://YOUR-BACKEND.onrender.com/api/v1` |
   | `NITRO_PRESET` | `vercel` |

   > **`NITRO_PRESET=vercel` is required.** The frontend is TanStack Start (SSR via Nitro),
   > whose bundled config defaults to a Cloudflare target; this env var retargets the build
   > to Vercel. `VITE_API_URL` is compiled in at build time, so set it **before** deploying.
4. **Deploy** → copy the frontend URL (e.g. `https://your-app.vercel.app`).

---

## 4. Connect CORS

1. Render → service → **Environment** → set `CORS_ORIGINS` to your Vercel URL
   (exact, no trailing slash; comma-separate multiple origins):
   ```
   https://your-app.vercel.app
   ```
2. Save → Render redeploys automatically.

---

## 5. Verify end-to-end

Open the Vercel URL and run a comparison — it should reach Render → Neon and return results.
Register / login / history work against Neon.

---

## Notes & limitations

- **Cold starts:** Render (free) sleeps after ~15 min idle → first request ~30–50s. Neon (free)
  also auto-suspends and wakes on first query (~1s). Normal for a demo/evaluation.
- **Secrets:** `JWT_SECRET_KEY` and `DATABASE_URL` live only in the platform dashboards; `.env`
  files are git-ignored. Never commit them.
- **Local `.env`:** `front_end/.env.example` documents `VITE_API_URL` for local runs; copy it to
  `front_end/.env`. See [`README_updated.md`](README_updated.md) for local startup.
- **Vercel build fails with a Cloudflare/Nitro error?** Confirm `NITRO_PRESET=vercel` is set.
  Fallback: the bundled config already targets **Cloudflare Pages**, so the frontend can deploy
  there with no changes.
- **Schema/data changes later:** redeploy, then re-run `alembic upgrade head && python -m app.db.seed`
  in the Render Shell.

## Local development (reference)

```bash
# Terminal 1 — backend
cd backend
python -m app.db.seed
python -m uvicorn app.main:app --reload --port 8000

# Terminal 2 — frontend
cd front_end
npm install
npm run dev        # http://localhost:8080
```
