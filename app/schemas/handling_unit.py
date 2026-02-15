from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.db.models.handling_unit import HandlingUnitStatus


class HandlingUnitCreate(BaseModel):
    hu_code: str = Field(min_length=1, max_length=64)
    location_id: int
    status: HandlingUnitStatus = HandlingUnitStatus.OPEN


class HandlingUnitUpdate(BaseModel):
    location_id: int | None = None
    status: HandlingUnitStatus | None = None


class HandlingUnitRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    hu_code: str
    location_id: int
    status: HandlingUnitStatus
    created_at: datetime
