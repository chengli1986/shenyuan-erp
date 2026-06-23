# Shenyuan ERP

## Overview
ERP for engineering-project management (projects, contract BOQ/清单, file management,
purchase requisitions, system testing). UI is Simplified Chinese.
- **Backend**: FastAPI + SQLAlchemy 2.0 + Pydantic v2, PostgreSQL (SQLite default for dev), Uvicorn.
- **Frontend**: React 19 + TypeScript + Ant Design 5, built with Vite. axios + react-router.

## Develop / Test
Backend (run from `backend/`, inside a venv):
```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload   # API docs at /docs
python -m pytest tests/                                              # unit/ integration/ workflow/
```
Frontend (run from `frontend/`):
```bash
npm install
npm run dev      # Vite dev server, port 3000
npm run build    # tsc --noEmit && vite build  -> dist/
```
- Vite dev proxy: requests to `/api` are forwarded to `http://localhost:8000` (see `vite.config.ts`).
- Helper scripts in `scripts/`: `start-erp-dev.sh`, `start-erp-prod.sh`, `stop-erp.sh`, `check-erp.sh`.

## Architecture
Backend `backend/app/`:
- `api/v1/` — routers: `auth`, `projects`, `contracts` / `contract_items` / `contract_versions`,
  `file_upload` / `project_files`, `purchases` / `purchase_workflow` / `purchase_query` /
  `purchase_suppliers`, `test_results`. Mounted via `api/v1/api_router`.
- `models/` — SQLAlchemy models (`project`, `contract`, `project_file`, `purchase`, `test_result`,
  `user`, `permission`). `schemas/` — Pydantic request/response models.
- `core/` — `config` (Settings), `database` (engine/Base), `test_scheduler`. `services/`, `utils/`.
- Tables are auto-created at startup via `Base.metadata.create_all` in `main.py` lifespan; there is no
  Alembic-managed migration chain (`db-migration/` holds ad-hoc scripts only).

Frontend `frontend/src/`: `pages/` (e.g. `Purchase/`), `components/`, `services/` (axios API layer),
`types/` (TS types). Feature areas: project mgmt, contract BOQ (Excel import via pandas/openpyxl),
purchase requisition workflow, system-test dashboard, material system classification (物料系统分类).

## Key Facts / Gotchas
- Default DB is SQLite (`erp_test.db`). For PostgreSQL set `database_driver=postgresql` + `postgres_*`
  env vars (see `core/config.py:effective_database_url`).
- Frontend uses Vite, not CRA — call APIs as relative `/api/v1/...` so the dev proxy applies.
- Contract version endpoints are `/contract-versions/` (NOT `/versions/`).
- File downloads must use fetch + blob, not direct anchor links.
- CORS allowed origins live in `app/main.py`; add a new frontend origin there or the UI shows
  "backend not connected".
- Project-level permission isolation: a project manager only sees/manages their own projects.
- The system-test scheduler starts automatically as a background asyncio task on app startup.

> The 170KB root `CLAUDE.md` is the historical dev journal; this file is the lean dev reference.
