## Implementation Checklist: FastAPI WMS API MVP

Use this checklist to implement the plan in small, verifiable phases.

### Delivery Principles
- Keep scope API-only.
- Enforce mission lifecycle strictly: `draft -> assigned -> in_progress -> completed | cancelled`.
- Keep inventory updates transaction-safe and audit-backed (movement ledger).
- Avoid adding auth, lot tracking, and Storage entity in MVP.

## Phase 0 — Bootstrap

### P0.1 Project foundation
- [ ] Create project structure (`app/`, `tests/`, `alembic/`).
- [ ] Add dependency config for FastAPI, SQLAlchemy, Alembic, Pydantic, Uvicorn, pytest.
- [ ] Add app entrypoint and API v1 router wiring.
- [ ] Add SQLite connection/session management.

**Done when**
- [ ] App starts successfully and `/api/v1/healthz` responds.

## Phase 1 — Data Model + Migrations

### P1.1 Core entities
- [ ] Add ORM models for: Operator, Executor, Location, Item, HandlingUnit.
- [ ] Add ORM models for: Mission, MissionLine, InventoryPosition, InventoryMovement.

### P1.2 Constraints and enums
- [ ] Add unique codes/IDs where required.
- [ ] Add mission state enum and enforce valid values.
- [ ] Add non-negative checks for inventory quantities.
- [ ] Add foreign keys across mission, line, HU, location, and inventory tables.

### P1.3 Migration baseline
- [ ] Initialize Alembic config and migration env.
- [ ] Generate initial migration from models.
- [ ] Apply migration to SQLite database.

**Done when**
- [ ] Fresh DB bootstraps entirely from migrations.
- [ ] Core constraints are visible in schema and enforced at runtime.

## Phase 2 — Schemas + Repositories

### P2.1 API schemas
- [ ] Add create/read/update Pydantic schemas for all resources.
- [ ] Add command schemas for mission transitions and movement recording.
- [ ] Add validation for quantity > 0 and required references.

### P2.2 Repository layer
- [ ] Add repositories for CRUD access per aggregate.
- [ ] Add atomic inventory update helpers with optimistic versioning.
- [ ] Add movement ledger write path as immutable inserts.

**Done when**
- [ ] Service layer can perform persistence without direct session logic in routes.

## Phase 3 — Business Rules

### P3.1 Mission rules
- [ ] Enforce legal mission transitions only.
- [ ] Enforce assign only from `draft` and to active executor.
- [ ] Enforce start only from `assigned`.
- [ ] Enforce complete only when all line quantities are fully done.
- [ ] Allow cancel from non-terminal states and require reason.

### P3.2 Movement rules
- [ ] Validate source/destination active and not equal.
- [ ] Validate mission is `in_progress` before movement.
- [ ] Prevent negative stock after movement.
- [ ] Validate HU location consistency for HU movements.

**Done when**
- [ ] Invalid transitions/movements return deterministic 4xx responses.
- [ ] No mutation path changes stock without ledger entry.

## Phase 4 — Endpoints

### P4.1 Master data endpoints
- [ ] `POST/GET/GET{id}` for Operators.
- [ ] `POST/GET/GET{id}` for Executors.
- [ ] `POST/GET/GET{id}/PATCH{id}` for Locations.
- [ ] `POST/GET/GET{id}` for Items.
- [ ] `POST/GET/GET{id}/PATCH{id}` for Handling Units.

### P4.2 Inventory endpoints
- [ ] `GET /inventory/positions` with filters.
- [ ] `POST /inventory/adjustments` with reason.

### P4.3 Mission endpoints
- [ ] `POST/GET/GET{id}/PATCH{id}` for missions.
- [ ] `POST /missions/{id}/assign`
- [ ] `POST /missions/{id}/start`
- [ ] `POST /missions/{id}/record-movement`
- [ ] `POST /missions/{id}/complete`
- [ ] `POST /missions/{id}/cancel`

### P4.4 Audit/ops
- [ ] `GET /movements`
- [ ] `GET /healthz`

**Done when**
- [ ] OpenAPI exposes all MVP endpoints.
- [ ] Happy-path mission flow executes end-to-end using only APIs.

## Phase 5 — SQLite Hardening

### P5.1 Connection/session safeguards
- [ ] Enable `PRAGMA foreign_keys=ON`.
- [ ] Enable WAL mode.
- [ ] Configure busy timeout.
- [ ] Use UTC timestamps consistently.

### P5.2 Concurrency handling
- [ ] Add optimistic conflict checks on inventory updates.
- [ ] Add retry-or-fail behavior for write contention.

**Done when**
- [ ] Concurrent movement attempts do not create negative stock or duplicate movement effects.

## Phase 6 — Tests

### P6.1 Unit tests
- [ ] Transition matrix tests for mission states.
- [ ] Rule tests for assignment/start/complete/cancel invariants.
- [ ] Movement validation and stock guard tests.

### P6.2 Integration tests
- [ ] API happy path: create data → create mission → assign/start/move/complete.
- [ ] API cancel path with partial execution retained.
- [ ] Inventory adjustment and movements query tests.

### P6.3 Concurrency tests
- [ ] Simultaneous movement requests on same inventory position.
- [ ] Assert one succeeds and conflicts are handled safely.

**Done when**
- [ ] Core test suite passes reliably on clean DB.

## Phase 7 — Docs and Handoff

### P7.1 README completion
- [ ] Setup and run instructions.
- [ ] Migration commands.
- [ ] API overview and mission lifecycle semantics.
- [ ] Explicit MVP exclusions: auth, lot tracking, storage entity.

### P7.2 Operational notes
- [ ] Known SQLite limitations and recommended single-process deployment.
- [ ] Future extension points (Rules API, auth, lot tracking).

**Done when**
- [ ] New developer can run, migrate, and exercise key endpoints without tribal knowledge.

---

## Milestones

### Milestone A — Foundation Ready
- Complete Phases 0–1.
- Output: runnable app + migrated schema.

### Milestone B — Domain Logic Ready
- Complete Phases 2–3.
- Output: validated services and safe persistence behavior.

### Milestone C — API MVP Ready
- Complete Phase 4.
- Output: all agreed endpoints functional.

### Milestone D — Production-leaning MVP
- Complete Phases 5–7.
- Output: hardened SQLite behavior, tests, and documentation.

---

## Suggested Execution Order (Low Risk)
1. Phases 0 and 1 together
2. Phase 2 repositories before full routes
3. Phase 3 rules before mission action endpoints
4. Phase 4 endpoint wiring
5. Phase 6 tests in parallel with Phases 3–4
6. Phases 5 and 7 finalization

## Change Control
- Any new feature request should declare whether it is:
  - [ ] In-scope MVP (endpoint-only)
  - [ ] Deferred post-MVP
- If in-scope and model-affecting, update:
  - [ ] ORM model
  - [ ] migration
  - [ ] schema
  - [ ] service rules
  - [ ] endpoint
  - [ ] tests
  - [ ] docs