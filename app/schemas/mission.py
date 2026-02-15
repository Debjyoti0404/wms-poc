from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.db.models.mission import MissionState, MissionType


class MissionLineCreate(BaseModel):
    from_location_id: int
    to_location_id: int
    item_id: int | None = None
    hu_id: int | None = None
    qty: Decimal = Field(gt=0)


class MissionLineRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    mission_id: int
    from_location_id: int
    to_location_id: int
    item_id: int | None
    hu_id: int | None
    qty: Decimal
    qty_done: Decimal


class MissionCreate(BaseModel):
    mission_no: str = Field(min_length=1, max_length=64)
    type: MissionType
    priority: int = Field(default=0, ge=0)
    created_by_operator_id: int
    lines: list[MissionLineCreate] = Field(min_length=1)


class MissionUpdate(BaseModel):
    priority: int | None = Field(default=None, ge=0)


class MissionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    mission_no: str
    type: MissionType
    state: MissionState
    priority: int
    created_by_operator_id: int
    assigned_executor_id: int | None
    created_at: datetime
    started_at: datetime | None
    completed_at: datetime | None
    cancel_reason: str | None
    lines: list[MissionLineRead]


class MissionAssignCommand(BaseModel):
    executor_id: int


class MissionStartCommand(BaseModel):
    executor_id: int


class MissionRecordMovementCommand(BaseModel):
    mission_line_id: int
    qty: Decimal = Field(gt=0)
    executor_id: int
    from_hu_id: int | None = None
    to_hu_id: int | None = None
    idempotency_key: str | None = Field(default=None, min_length=1, max_length=128)


class MissionCompleteCommand(BaseModel):
    idempotency_key: str | None = Field(default=None, min_length=1, max_length=128)


class MissionCancelCommand(BaseModel):
    reason: str = Field(min_length=1, max_length=500)
    idempotency_key: str | None = Field(default=None, min_length=1, max_length=128)
