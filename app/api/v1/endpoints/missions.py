from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories.mission import MissionRepository
from app.rules.exceptions import RuleViolation
from app.schemas.inventory import InventoryMovementRead
from app.schemas.mission import (
    MissionAssignCommand,
    MissionCancelCommand,
    MissionCompleteCommand,
    MissionCreate,
    MissionRead,
    MissionRecordMovementCommand,
    MissionStartCommand,
    MissionUpdate,
)
from app.services.mission_service import MissionService

router = APIRouter(prefix="/missions")


@router.post("", response_model=MissionRead, status_code=status.HTTP_201_CREATED)
def create_mission(payload: MissionCreate, db: Session = Depends(get_db)) -> MissionRead:
    service = MissionService(db)
    try:
        mission = service.create_mission(payload)
        db.commit()
        return MissionRead.model_validate(mission)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Mission number conflict or invalid references") from exc


@router.get("", response_model=list[MissionRead])
def list_missions(db: Session = Depends(get_db)) -> list[MissionRead]:
    repo = MissionRepository(db)
    return [MissionRead.model_validate(item) for item in repo.list()]


@router.get("/{mission_id}", response_model=MissionRead)
def get_mission(mission_id: int, db: Session = Depends(get_db)) -> MissionRead:
    repo = MissionRepository(db)
    mission = repo.get_with_lines(mission_id)
    if mission is None:
        raise HTTPException(status_code=404, detail="Mission not found")
    return MissionRead.model_validate(mission)


@router.patch("/{mission_id}", response_model=MissionRead)
def update_mission(mission_id: int, payload: MissionUpdate, db: Session = Depends(get_db)) -> MissionRead:
    repo = MissionRepository(db)
    mission = repo.get_with_lines(mission_id)
    if mission is None:
        raise HTTPException(status_code=404, detail="Mission not found")

    if payload.priority is not None:
        mission = repo.update_priority(mission, priority=payload.priority)
        db.commit()
    return MissionRead.model_validate(mission)


@router.post("/{mission_id}/assign", response_model=MissionRead)
def assign_mission(
    mission_id: int,
    payload: MissionAssignCommand,
    db: Session = Depends(get_db),
) -> MissionRead:
    service = MissionService(db)
    try:
        mission = service.assign(mission_id=mission_id, executor_id=payload.executor_id)
        db.commit()
        return MissionRead.model_validate(mission)
    except RuleViolation as exc:
        db.rollback()
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc


@router.post("/{mission_id}/start", response_model=MissionRead)
def start_mission(
    mission_id: int,
    payload: MissionStartCommand,
    db: Session = Depends(get_db),
) -> MissionRead:
    service = MissionService(db)
    try:
        mission = service.start(mission_id=mission_id, executor_id=payload.executor_id)
        db.commit()
        return MissionRead.model_validate(mission)
    except RuleViolation as exc:
        db.rollback()
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc


@router.post("/{mission_id}/record-movement", response_model=InventoryMovementRead)
def record_movement(
    mission_id: int,
    payload: MissionRecordMovementCommand,
    db: Session = Depends(get_db),
) -> InventoryMovementRead:
    service = MissionService(db)
    try:
        movement = service.record_movement(mission_id=mission_id, payload=payload)
        db.commit()
        return InventoryMovementRead.model_validate(movement)
    except RuleViolation as exc:
        db.rollback()
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Movement conflict") from exc


@router.post("/{mission_id}/complete", response_model=MissionRead)
def complete_mission(
    mission_id: int,
    payload: MissionCompleteCommand,
    db: Session = Depends(get_db),
) -> MissionRead:
    service = MissionService(db)
    try:
        mission = service.complete(mission_id=mission_id)
        db.commit()
        return MissionRead.model_validate(mission)
    except RuleViolation as exc:
        db.rollback()
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc


@router.post("/{mission_id}/cancel", response_model=MissionRead)
def cancel_mission(
    mission_id: int,
    payload: MissionCancelCommand,
    db: Session = Depends(get_db),
) -> MissionRead:
    service = MissionService(db)
    try:
        mission = service.cancel(mission_id=mission_id, reason=payload.reason)
        db.commit()
        return MissionRead.model_validate(mission)
    except RuleViolation as exc:
        db.rollback()
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc
