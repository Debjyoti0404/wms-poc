from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories.inventory import InventoryPositionRepository
from app.rules.exceptions import RuleViolation
from app.schemas.inventory import InventoryAdjustmentCreate, InventoryMovementRead, InventoryPositionRead
from app.services.inventory_service import InventoryService

router = APIRouter(prefix="/inventory")


@router.get("/positions", response_model=list[InventoryPositionRead])
def list_inventory_positions(
    hu_id: int | None = None,
    item_id: int | None = None,
    db: Session = Depends(get_db),
) -> list[InventoryPositionRead]:
    repo = InventoryPositionRepository(db)
    items = repo.list(hu_id=hu_id, item_id=item_id)
    return [InventoryPositionRead.model_validate(item) for item in items]


@router.post("/adjustments", response_model=InventoryMovementRead, status_code=status.HTTP_201_CREATED)
def create_inventory_adjustment(
    payload: InventoryAdjustmentCreate,
    db: Session = Depends(get_db),
) -> InventoryMovementRead:
    service = InventoryService(db)
    try:
        movement = service.adjust_inventory(
            hu_id=payload.hu_id,
            item_id=payload.item_id,
            qty_delta=payload.qty_delta,
            reason=payload.reason,
            executor_id=payload.executor_id,
            idempotency_key=payload.idempotency_key,
        )
        db.commit()
        return InventoryMovementRead.model_validate(movement)
    except RuleViolation as exc:
        db.rollback()
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Inventory adjustment conflict") from exc
