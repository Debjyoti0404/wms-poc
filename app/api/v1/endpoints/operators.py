from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories.operator import OperatorRepository
from app.schemas.operator import OperatorCreate, OperatorRead, OperatorUpdate

router = APIRouter(prefix="/operators")


@router.post("", response_model=OperatorRead, status_code=status.HTTP_201_CREATED)
def create_operator(payload: OperatorCreate, db: Session = Depends(get_db)) -> OperatorRead:
    repo = OperatorRepository(db)
    try:
        entity = repo.create(code=payload.code, name=payload.name, active=payload.active)
        db.commit()
        return OperatorRead.model_validate(entity)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Operator code already exists") from exc


@router.get("", response_model=list[OperatorRead])
def list_operators(db: Session = Depends(get_db)) -> list[OperatorRead]:
    repo = OperatorRepository(db)
    return [OperatorRead.model_validate(item) for item in repo.list()]


@router.get("/{operator_id}", response_model=OperatorRead)
def get_operator(operator_id: int, db: Session = Depends(get_db)) -> OperatorRead:
    repo = OperatorRepository(db)
    entity = repo.get(operator_id)
    if entity is None:
        raise HTTPException(status_code=404, detail="Operator not found")
    return OperatorRead.model_validate(entity)


@router.patch("/{operator_id}", response_model=OperatorRead)
def update_operator(operator_id: int, payload: OperatorUpdate, db: Session = Depends(get_db)) -> OperatorRead:
    repo = OperatorRepository(db)
    entity = repo.get(operator_id)
    if entity is None:
        raise HTTPException(status_code=404, detail="Operator not found")

    updated = repo.update(
        entity,
        name=payload.name,
        active=payload.active,
    )
    db.commit()
    return OperatorRead.model_validate(updated)
