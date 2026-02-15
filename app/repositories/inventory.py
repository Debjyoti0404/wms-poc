from decimal import Decimal

from sqlalchemy import and_, select, update

from app.db.models.inventory import InventoryMovement, InventoryMovementType, InventoryPosition
from app.repositories.base import BaseRepository


class InventoryPositionRepository(BaseRepository):
    def get(self, position_id: int) -> InventoryPosition | None:
        return self.db.get(InventoryPosition, position_id)

    def get_by_hu_item(self, hu_id: int, item_id: int) -> InventoryPosition | None:
        statement = select(InventoryPosition).where(
            and_(InventoryPosition.hu_id == hu_id, InventoryPosition.item_id == item_id)
        )
        return self.db.scalar(statement)

    def list(
        self,
        *,
        hu_id: int | None = None,
        item_id: int | None = None,
    ) -> list[InventoryPosition]:
        statement = select(InventoryPosition).order_by(InventoryPosition.id)
        if hu_id is not None:
            statement = statement.where(InventoryPosition.hu_id == hu_id)
        if item_id is not None:
            statement = statement.where(InventoryPosition.item_id == item_id)
        return list(self.db.scalars(statement).all())

    def create(self, *, hu_id: int, item_id: int, qty_on_hand: Decimal = Decimal("0")) -> InventoryPosition:
        entity = InventoryPosition(hu_id=hu_id, item_id=item_id, qty_on_hand=qty_on_hand, qty_reserved=Decimal("0"))
        self.db.add(entity)
        self.db.flush()
        self.db.refresh(entity)
        return entity

    def update_qty_on_hand_if_version(
        self,
        *,
        position_id: int,
        expected_version: int,
        qty_delta: Decimal,
    ) -> bool:
        statement = (
            update(InventoryPosition)
            .where(
                and_(
                    InventoryPosition.id == position_id,
                    InventoryPosition.version == expected_version,
                    (InventoryPosition.qty_on_hand + qty_delta) >= 0,
                )
            )
            .values(
                qty_on_hand=InventoryPosition.qty_on_hand + qty_delta,
                version=InventoryPosition.version + 1,
            )
        )
        result = self.db.execute(statement)
        return result.rowcount == 1


class InventoryMovementRepository(BaseRepository):
    def create(
        self,
        *,
        movement_type: InventoryMovementType,
        item_id: int | None,
        qty: Decimal,
        mission_line_id: int | None = None,
        from_location_id: int | None = None,
        to_location_id: int | None = None,
        from_hu_id: int | None = None,
        to_hu_id: int | None = None,
        executed_by_executor_id: int | None = None,
        idempotency_key: str | None = None,
        reason: str | None = None,
    ) -> InventoryMovement:
        entity = InventoryMovement(
            mission_line_id=mission_line_id,
            movement_type=movement_type,
            item_id=item_id,
            from_location_id=from_location_id,
            to_location_id=to_location_id,
            from_hu_id=from_hu_id,
            to_hu_id=to_hu_id,
            qty=qty,
            executed_by_executor_id=executed_by_executor_id,
            idempotency_key=idempotency_key,
            reason=reason,
        )
        self.db.add(entity)
        self.db.flush()
        self.db.refresh(entity)
        return entity

    def get_by_idempotency_key(self, idempotency_key: str) -> InventoryMovement | None:
        statement = select(InventoryMovement).where(InventoryMovement.idempotency_key == idempotency_key)
        return self.db.scalar(statement)

    def list(self) -> list[InventoryMovement]:
        statement = select(InventoryMovement).order_by(InventoryMovement.id)
        return list(self.db.scalars(statement).all())
