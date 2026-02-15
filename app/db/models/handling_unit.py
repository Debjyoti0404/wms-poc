from datetime import datetime
from enum import StrEnum

from sqlalchemy import DateTime, Enum, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class HandlingUnitStatus(StrEnum):
    OPEN = "open"
    SEALED = "sealed"
    BLOCKED = "blocked"


class HandlingUnit(Base):
    __tablename__ = "handling_units"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    hu_code: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    location_id: Mapped[int] = mapped_column(ForeignKey("locations.id", ondelete="RESTRICT"), nullable=False)
    status: Mapped[HandlingUnitStatus] = mapped_column(
        Enum(HandlingUnitStatus, name="handling_unit_status", native_enum=False),
        nullable=False,
        default=HandlingUnitStatus.OPEN,
        server_default=HandlingUnitStatus.OPEN.value,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    location = relationship("Location", back_populates="handling_units")
    positions = relationship("InventoryPosition", back_populates="handling_unit")
    mission_lines = relationship("MissionLine", back_populates="handling_unit")
    movement_source_hus = relationship(
        "InventoryMovement",
        back_populates="from_handling_unit",
        foreign_keys="InventoryMovement.from_hu_id",
    )
    movement_destination_hus = relationship(
        "InventoryMovement",
        back_populates="to_handling_unit",
        foreign_keys="InventoryMovement.to_hu_id",
    )
