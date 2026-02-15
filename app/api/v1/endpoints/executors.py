from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.models.executor import ExecutorType
from app.db.session import get_db
from app.repositories.executor import ExecutorRepository
from app.schemas.executor import ExecutorCreate, ExecutorRead, ExecutorUpdate

router = APIRouter(prefix="/executors")


@router.post("", response_model=ExecutorRead, status_code=status.HTTP_201_CREATED)
def create_executor(payload: ExecutorCreate, db: Session = Depends(get_db)) -> ExecutorRead:
    repo = ExecutorRepository(db)
    try:
        entity = repo.create(
            code=payload.code,
            name=payload.name,
            executor_type=payload.executor_type,
            max_payload_kg=payload.max_payload_kg,
            active=payload.active,
        )
        db.commit()
        return ExecutorRead.model_validate(entity)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Executor code already exists") from exc


@router.get("", response_model=list[ExecutorRead])
def list_executors(
    db: Session = Depends(get_db),
    executor_type: ExecutorType | None = Query(default=None),
) -> list[ExecutorRead]:
    repo = ExecutorRepository(db)
    items = repo.list()
    if executor_type is not None:
        items = [item for item in items if item.executor_type == executor_type]
    return [ExecutorRead.model_validate(item) for item in items]


@router.get("/{executor_id}", response_model=ExecutorRead)
def get_executor(executor_id: int, db: Session = Depends(get_db)) -> ExecutorRead:
    repo = ExecutorRepository(db)
    entity = repo.get(executor_id)
    if entity is None:
        raise HTTPException(status_code=404, detail="Executor not found")
    return ExecutorRead.model_validate(entity)


@router.patch("/{executor_id}", response_model=ExecutorRead)
def update_executor(executor_id: int, payload: ExecutorUpdate, db: Session = Depends(get_db)) -> ExecutorRead:
    repo = ExecutorRepository(db)
    entity = repo.get(executor_id)
    if entity is None:
        raise HTTPException(status_code=404, detail="Executor not found")

    updated = repo.update(
        entity,
        name=payload.name,
        executor_type=payload.executor_type,
        max_payload_kg=payload.max_payload_kg,
        active=payload.active,
        last_seen_at=payload.last_seen_at,
    )
    db.commit()
    return ExecutorRead.model_validate(updated)
