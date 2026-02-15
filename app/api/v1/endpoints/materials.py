from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories.item import ItemRepository
from app.schemas.item import ItemCreate, ItemRead

router = APIRouter(prefix="/materials")


@router.post("", response_model=ItemRead, status_code=status.HTTP_201_CREATED)
def create_material(payload: ItemCreate, db: Session = Depends(get_db)) -> ItemRead:
    repo = ItemRepository(db)
    try:
        entity = repo.create(sku=payload.sku, name=payload.name, uom=payload.uom)
        db.commit()
        return ItemRead.model_validate(entity)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Material SKU already exists") from exc


@router.get("", response_model=list[ItemRead])
def list_materials(db: Session = Depends(get_db)) -> list[ItemRead]:
    repo = ItemRepository(db)
    return [ItemRead.model_validate(item) for item in repo.list()]


@router.get("/{material_id}", response_model=ItemRead)
def get_material(material_id: int, db: Session = Depends(get_db)) -> ItemRead:
    repo = ItemRepository(db)
    entity = repo.get(material_id)
    if entity is None:
        raise HTTPException(status_code=404, detail="Material not found")
    return ItemRead.model_validate(entity)
