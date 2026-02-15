from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.db.models.executor import ExecutorType


class ExecutorCreate(BaseModel):
    code: str = Field(min_length=1, max_length=64)
    name: str = Field(min_length=1, max_length=255)
    executor_type: ExecutorType = ExecutorType.HUMAN
    max_payload_kg: Decimal = Field(default=Decimal("500"), gt=0)
    active: bool = True


class ExecutorUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    executor_type: ExecutorType | None = None
    max_payload_kg: Decimal | None = Field(default=None, gt=0)
    active: bool | None = None
    last_seen_at: datetime | None = None


class ExecutorRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    name: str
    executor_type: ExecutorType
    max_payload_kg: Decimal
    active: bool
    last_seen_at: datetime | None
    created_at: datetime
