from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.db.models.inventory import InventoryMovementType


class InventoryPositionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    hu_id: int
    item_id: int
    qty_on_hand: Decimal
    qty_reserved: Decimal
    version: int
    updated_at: datetime


class InventoryAdjustmentCreate(BaseModel):
    hu_id: int
    item_id: int
    qty_delta: Decimal
    reason: str = Field(min_length=1, max_length=500)
    executor_id: int | None = None
    idempotency_key: str | None = Field(default=None, min_length=1, max_length=128)


class InventoryMovementRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    mission_line_id: int | None
    movement_type: InventoryMovementType
    item_id: int | None
    from_location_id: int | None
    to_location_id: int | None
    from_hu_id: int | None
    to_hu_id: int | None
    qty: Decimal
    executed_by_executor_id: int | None
    executed_at: datetime
    idempotency_key: str | None
    reason: str | None
