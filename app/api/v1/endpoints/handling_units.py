from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories.handling_unit import HandlingUnitRepository
from app.repositories.location import LocationRepository
from app.schemas.handling_unit import HandlingUnitCreate, HandlingUnitRead, HandlingUnitUpdate

router = APIRouter(prefix="/handling-units")


@router.post("", response_model=HandlingUnitRead, status_code=status.HTTP_201_CREATED)
def create_handling_unit(payload: HandlingUnitCreate, db: Session = Depends(get_db)) -> HandlingUnitRead:
    hu_repo = HandlingUnitRepository(db)
    location_repo = LocationRepository(db)

    if location_repo.get(payload.location_id) is None:
        raise HTTPException(status_code=404, detail="Location not found")

    try:
        entity = hu_repo.create(
            hu_code=payload.hu_code,
            location_id=payload.location_id,
            status=payload.status,
        )
        db.commit()
        return HandlingUnitRead.model_validate(entity)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Handling unit code already exists") from exc


@router.get("", response_model=list[HandlingUnitRead])
def list_handling_units(db: Session = Depends(get_db)) -> list[HandlingUnitRead]:
    repo = HandlingUnitRepository(db)
    return [HandlingUnitRead.model_validate(item) for item in repo.list()]


@router.get("/{handling_unit_id}", response_model=HandlingUnitRead)
def get_handling_unit(handling_unit_id: int, db: Session = Depends(get_db)) -> HandlingUnitRead:
    repo = HandlingUnitRepository(db)
    entity = repo.get(handling_unit_id)
    if entity is None:
        raise HTTPException(status_code=404, detail="Handling unit not found")
    return HandlingUnitRead.model_validate(entity)


@router.patch("/{handling_unit_id}", response_model=HandlingUnitRead)
def update_handling_unit(
    handling_unit_id: int,
    payload: HandlingUnitUpdate,
    db: Session = Depends(get_db),
) -> HandlingUnitRead:
    hu_repo = HandlingUnitRepository(db)
    location_repo = LocationRepository(db)

    entity = hu_repo.get(handling_unit_id)
    if entity is None:
        raise HTTPException(status_code=404, detail="Handling unit not found")

    if payload.location_id is not None and location_repo.get(payload.location_id) is None:
        raise HTTPException(status_code=404, detail="Location not found")

    updated = hu_repo.update(entity, location_id=payload.location_id, status=payload.status)
    db.commit()
    return HandlingUnitRead.model_validate(updated)
