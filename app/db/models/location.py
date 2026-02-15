from datetime import datetime
from enum import StrEnum

from sqlalchemy import Boolean, DateTime, Enum, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class LocationType(StrEnum):
    PICK = "pick"
    BULK = "bulk"
    STAGING = "staging"
    DOCK = "dock"


class Location(Base):
    __tablename__ = "locations"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    code: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[LocationType] = mapped_column(
        Enum(LocationType, name="location_type", native_enum=False),
        nullable=False,
        default=LocationType.BULK,
        server_default=LocationType.BULK.value,
    )
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="1")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    handling_units = relationship("HandlingUnit", back_populates="location")
    mission_line_sources = relationship(
        "MissionLine",
        back_populates="from_location",
        foreign_keys="MissionLine.from_location_id",
    )
    mission_line_destinations = relationship(
        "MissionLine",
        back_populates="to_location",
        foreign_keys="MissionLine.to_location_id",
    )
