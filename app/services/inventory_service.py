from decimal import Decimal

from sqlalchemy.orm import Session

from app.db.models.inventory import InventoryMovement, InventoryMovementType
from app.repositories.handling_unit import HandlingUnitRepository
from app.repositories.inventory import InventoryMovementRepository, InventoryPositionRepository
from app.rules.exceptions import RuleViolation


class InventoryService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.handling_units = HandlingUnitRepository(db)
        self.positions = InventoryPositionRepository(db)
        self.movements = InventoryMovementRepository(db)

    def adjust_inventory(
        self,
        *,
        hu_id: int,
        item_id: int,
        qty_delta: Decimal,
        reason: str,
        executor_id: int | None = None,
        idempotency_key: str | None = None,
    ) -> InventoryMovement:
        if qty_delta == 0:
            raise RuleViolation("qty_delta must not be zero")

        handling_unit = self.handling_units.get(hu_id)
        if handling_unit is None:
            raise RuleViolation("Handling unit not found", status_code=404)

        if idempotency_key:
            existing = self.movements.get_by_idempotency_key(idempotency_key)
            if existing is not None:
                return existing

        position = self.positions.get_by_hu_item(hu_id, item_id)
        if position is None:
            if qty_delta < 0:
                raise RuleViolation("Cannot reduce stock for a missing inventory position")
            position = self.positions.create(hu_id=hu_id, item_id=item_id, qty_on_hand=Decimal("0"))

        changed = self.positions.update_qty_on_hand_if_version(
            position_id=position.id,
            expected_version=position.version,
            qty_delta=qty_delta,
        )
        if not changed:
            raise RuleViolation("Inventory update conflict or insufficient stock")

        from_location_id = handling_unit.location_id if qty_delta < 0 else None
        to_location_id = handling_unit.location_id if qty_delta > 0 else None
        from_hu_id = hu_id if qty_delta < 0 else None
        to_hu_id = hu_id if qty_delta > 0 else None

        return self.movements.create(
            movement_type=InventoryMovementType.ADJUSTMENT,
            item_id=item_id,
            qty=abs(Decimal(str(qty_delta))),
            from_location_id=from_location_id,
            to_location_id=to_location_id,
            from_hu_id=from_hu_id,
            to_hu_id=to_hu_id,
            executed_by_executor_id=executor_id,
            idempotency_key=idempotency_key,
            reason=reason,
        )
