from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.db.models.location import LocationType


class LocationCreate(BaseModel):
    code: str = Field(min_length=1, max_length=64)
    name: str = Field(min_length=1, max_length=255)
    type: LocationType = LocationType.BULK
    active: bool = True


class LocationUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    type: LocationType | None = None
    active: bool | None = None


class LocationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    name: str
    type: LocationType
    active: bool
    created_at: datetime
