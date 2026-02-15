## Warehouse Management System API (MVP)

FastAPI + SQLite scaffold for a Warehouse Management System with API-only scope.

### Current Scope (Phase 4)
- FastAPI API with version prefix: `/api/v1`
- SQLite + SQLAlchemy + Alembic baseline schema
- Business rule validation for mission transitions and movements
- Resource endpoints for:
  - Operators (`/operators`)
  - Executors (`/executors`)
  - Vehicles (`/vehicles`)
  - Materials (`/materials`)
  - Locations (`/locations`)
  - Handling Units (`/handling-units`)
  - Inventory (`/inventory/positions`, `/inventory/adjustments`)
  - Missions (`/missions/...`)
  - Requests (`/requests`)
  - Rules validation (`/rules/...`)
  - Movement audit (`/movements`)
  - Health (`/healthz`)
- SQLite session setup with pragmas:
  - `foreign_keys=ON`
  - `journal_mode=WAL`
  - `busy_timeout=5000`

## Quick Start

### 1) Create virtual environment
```bash
python -m venv .venv
source .venv/bin/activate
```

### 2) Install dependencies
```bash
pip install -e ".[dev]"
```

### 3) (Optional) Create env file
```bash
cp .env.example .env
```

### 4) Run the API
```bash
uvicorn app.main:app --reload
```

### 5) Run migrations
```bash
alembic upgrade head
```

API docs: http://127.0.0.1:8000/docs

## Project Layout

- `app/main.py` – FastAPI app factory + router registration
- `app/api/v1/router.py` – API v1 router
- `app/api/v1/endpoints/health.py` – `healthz` endpoint
- `app/core/config.py` – settings via environment variables
- `app/db/session.py` – SQLAlchemy engine/session setup
- `tests/` – test package scaffold

## Next Phases
- Add unit and integration tests for mission state machine and stock safety.
- Add OpenAPI examples and request/response samples.
- Add optional auth layer when required.

## Migration Commands

- Apply latest migration: `alembic upgrade head`
- Roll back one revision: `alembic downgrade -1`
- Create new revision: `alembic revision -m "description"`
