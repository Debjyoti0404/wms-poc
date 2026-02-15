from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories.inventory import InventoryMovementRepository
from app.schemas.inventory import InventoryMovementRead

router = APIRouter(prefix="/movements")


@router.get("", response_model=list[InventoryMovementRead])
def list_movements(db: Session = Depends(get_db)) -> list[InventoryMovementRead]:
    repo = InventoryMovementRepository(db)
    return [InventoryMovementRead.model_validate(item) for item in repo.list()]
