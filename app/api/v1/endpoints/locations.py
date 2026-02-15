from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories.location import LocationRepository
from app.schemas.location import LocationCreate, LocationRead, LocationUpdate

router = APIRouter(prefix="/locations")


@router.post("", response_model=LocationRead, status_code=status.HTTP_201_CREATED)
def create_location(payload: LocationCreate, db: Session = Depends(get_db)) -> LocationRead:
    repo = LocationRepository(db)
    try:
        entity = repo.create(
            code=payload.code,
            name=payload.name,
            type=payload.type,
            active=payload.active,
        )
        db.commit()
        return LocationRead.model_validate(entity)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Location code already exists") from exc


@router.get("", response_model=list[LocationRead])
def list_locations(db: Session = Depends(get_db)) -> list[LocationRead]:
    repo = LocationRepository(db)
    return [LocationRead.model_validate(item) for item in repo.list()]


@router.get("/{location_id}", response_model=LocationRead)
def get_location(location_id: int, db: Session = Depends(get_db)) -> LocationRead:
    repo = LocationRepository(db)
    entity = repo.get(location_id)
    if entity is None:
        raise HTTPException(status_code=404, detail="Location not found")
    return LocationRead.model_validate(entity)


@router.patch("/{location_id}", response_model=LocationRead)
def update_location(location_id: int, payload: LocationUpdate, db: Session = Depends(get_db)) -> LocationRead:
    repo = LocationRepository(db)
    entity = repo.get(location_id)
    if entity is None:
        raise HTTPException(status_code=404, detail="Location not found")

    updated = repo.update(
        entity,
        name=payload.name,
        type=payload.type,
        active=payload.active,
    )
    db.commit()
    return LocationRead.model_validate(updated)
