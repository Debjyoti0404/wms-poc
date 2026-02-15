from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.models.executor import ExecutorType
from app.db.session import get_db
from app.repositories.executor import ExecutorRepository
from app.schemas.executor import ExecutorCreate, ExecutorRead, ExecutorUpdate

router = APIRouter(prefix="/vehicles")


@router.post("", response_model=ExecutorRead, status_code=status.HTTP_201_CREATED)
def create_vehicle(payload: ExecutorCreate, db: Session = Depends(get_db)) -> ExecutorRead:
    repo = ExecutorRepository(db)
    try:
        entity = repo.create(
            code=payload.code,
            name=payload.name,
            executor_type=ExecutorType.AGV,
            max_payload_kg=payload.max_payload_kg,
            active=payload.active,
        )
        db.commit()
        return ExecutorRead.model_validate(entity)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Vehicle code already exists") from exc


@router.get("", response_model=list[ExecutorRead])
def list_vehicles(db: Session = Depends(get_db)) -> list[ExecutorRead]:
    repo = ExecutorRepository(db)
    items = [item for item in repo.list() if item.executor_type == ExecutorType.AGV]
    return [ExecutorRead.model_validate(item) for item in items]


@router.get("/{vehicle_id}", response_model=ExecutorRead)
def get_vehicle(vehicle_id: int, db: Session = Depends(get_db)) -> ExecutorRead:
    repo = ExecutorRepository(db)
    entity = repo.get(vehicle_id)
    if entity is None or entity.executor_type != ExecutorType.AGV:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return ExecutorRead.model_validate(entity)


@router.patch("/{vehicle_id}", response_model=ExecutorRead)
def update_vehicle(vehicle_id: int, payload: ExecutorUpdate, db: Session = Depends(get_db)) -> ExecutorRead:
    repo = ExecutorRepository(db)
    entity = repo.get(vehicle_id)
    if entity is None or entity.executor_type != ExecutorType.AGV:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    updated = repo.update(
        entity,
        name=payload.name,
        executor_type=ExecutorType.AGV,
        max_payload_kg=payload.max_payload_kg,
        active=payload.active,
        last_seen_at=payload.last_seen_at,
    )
    db.commit()
    return ExecutorRead.model_validate(updated)
