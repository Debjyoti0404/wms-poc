## Plan: FastAPI WMS API MVP (DRAFT)

This plan builds a greenfield warehouse API using FastAPI + SQLite, with API endpoints only. It reflects your confirmed decisions: separate Operator and Executor entities, no Storage entity (Location only), hardcoded rule checks in service logic (no Rules API for now), mission states as draft → assigned → in_progress → completed/cancelled, partial execution allowed, cancellation allowed without auto-reversal, lot tracking excluded for MVP, and no authentication for now. The design centers on consistent mission state transitions and inventory integrity with an immutable movement ledger, while keeping scope minimal and implementation-ready.

**Steps**
1. Initialize project skeleton and runtime foundations in [pyproject.toml](pyproject.toml), [README.md](README.md), [app/main.py](app/main.py), [app/core/config.py](app/core/config.py), [app/db/session.py](app/db/session.py), and [app/api/v1/router.py](app/api/v1/router.py), including API versioning at `/api/v1`.
2. Define persistence models in [app/db/models/](app/db/models/) for Operator, Executor, Location, Item, HandlingUnit, Mission, MissionLine, InventoryPosition, and InventoryMovement; enforce key constraints (unique codes, foreign keys, non-negative quantities, mission state enums).
3. Create migration baseline with Alembic in [alembic.ini](alembic.ini), [alembic/env.py](alembic/env.py), and [alembic/versions/](alembic/versions/) to materialize the initial schema in SQLite.
4. Create DTO schemas in [app/schemas/](app/schemas/) for create/read/update payloads and state-transition command bodies, with strict validation for quantities, required references, and allowed enum values.
5. Implement repository layer in [app/repositories/](app/repositories/) for atomic inventory updates and mission persistence, including optimistic concurrency via a version field on inventory positions.
6. Implement rule/validation services in [app/services/](app/services/) and hardcoded checks in [app/rules/mission_rules.py](app/rules/mission_rules.py) and [app/rules/movement_rules.py](app/rules/movement_rules.py): executor activity checks, legal mission transitions, source/destination validation, prevention of negative stock, and HU location consistency.
7. Add endpoint modules in [app/api/v1/endpoints/](app/api/v1/endpoints/) with the MVP surface:
   - Operators: `POST /operators`, `GET /operators`, `GET /operators/{id}`
   - Executors: `POST /executors`, `GET /executors`, `GET /executors/{id}`
   - Locations: `POST /locations`, `GET /locations`, `GET /locations/{id}`, `PATCH /locations/{id}`
   - Items: `POST /items`, `GET /items`, `GET /items/{id}`
   - Handling Units: `POST /handling-units`, `GET /handling-units`, `GET /handling-units/{id}`, `PATCH /handling-units/{id}`
   - Inventory: `GET /inventory/positions`, `POST /inventory/adjustments`
   - Missions: `POST /missions`, `GET /missions`, `GET /missions/{id}`, `PATCH /missions/{id}`, `POST /missions/{id}/assign`, `POST /missions/{id}/start`, `POST /missions/{id}/record-movement`, `POST /missions/{id}/complete`, `POST /missions/{id}/cancel`
   - Audit: `GET /movements`
   - Ops: `GET /healthz`
8. Add robust transaction and SQLite safeguards in DB/session setup: WAL mode, foreign keys pragma, busy timeout, and consistent UTC timestamps for all movement and mission events.
9. Add focused tests in [tests/unit/](tests/unit/) and [tests/integration/](tests/integration/) covering state transitions, rule validation failures, movement ledger creation, and concurrent stock-update conflict handling.
10. Document API behavior and state machine in [README.md](README.md), including mission lifecycle, cancellation semantics (partial movements remain), and inventory invariants.

**Verification**
- Run formatting/lint and test suite via project commands defined in [pyproject.toml](pyproject.toml).
- Validate endpoint flow manually: create master data → create mission with lines → assign/start/record movement → complete/cancel.
- Confirm invariants: no negative on-hand, immutable movement ledger entries, and forbidden mission transitions rejected with clear errors.
- Validate SQLite behavior under concurrent movement requests (conflict/retry path) using integration tests.

**Decisions**
- Separate Operator and Executor resources.
- Location-only physical model (no Storage entity).
- Rules implemented in code (no Rules API in MVP).
- No lot tracking in MVP inventory model.
- No authentication/authorization in MVP.
- Cancellation allowed after partial execution; no automatic movement reversal.