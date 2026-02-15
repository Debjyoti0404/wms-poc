from datetime import datetime
from decimal import Decimal
from enum import StrEnum

from sqlalchemy import CheckConstraint, DateTime, Enum, ForeignKey, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class MissionType(StrEnum):
    MOVE_HU = "move_hu"
    MOVE_ITEM = "move_item"


class MissionState(StrEnum):
    DRAFT = "draft"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Mission(Base):
    __tablename__ = "missions"
    __table_args__ = (
        CheckConstraint("priority >= 0", name="ck_missions_priority_non_negative"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    mission_no: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    type: Mapped[MissionType] = mapped_column(
        Enum(MissionType, name="mission_type", native_enum=False),
        nullable=False,
    )
    state: Mapped[MissionState] = mapped_column(
        Enum(MissionState, name="mission_state", native_enum=False),
        nullable=False,
        default=MissionState.DRAFT,
        server_default=MissionState.DRAFT.value,
    )
    priority: Mapped[int] = mapped_column(nullable=False, default=0, server_default="0")
    created_by_operator_id: Mapped[int] = mapped_column(
        ForeignKey("operators.id", ondelete="RESTRICT"), nullable=False
    )
    assigned_executor_id: Mapped[int | None] = mapped_column(
        ForeignKey("executors.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    cancel_reason: Mapped[str | None] = mapped_column(String(500), nullable=True)

    created_by_operator = relationship("Operator", back_populates="missions")
    assigned_executor = relationship("Executor", back_populates="assigned_missions")
    lines = relationship("MissionLine", back_populates="mission", cascade="all, delete-orphan")


class MissionLine(Base):
    __tablename__ = "mission_lines"
    __table_args__ = (
        CheckConstraint("qty > 0", name="ck_mission_lines_qty_positive"),
        CheckConstraint("qty_done >= 0", name="ck_mission_lines_qty_done_non_negative"),
        CheckConstraint("qty_done <= qty", name="ck_mission_lines_qty_done_le_qty"),
        CheckConstraint(
            "item_id IS NOT NULL OR hu_id IS NOT NULL",
            name="ck_mission_lines_item_or_hu_present",
        ),
        CheckConstraint(
            "from_location_id != to_location_id",
            name="ck_mission_lines_source_destination_different",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    mission_id: Mapped[int] = mapped_column(ForeignKey("missions.id", ondelete="CASCADE"), nullable=False)
    from_location_id: Mapped[int] = mapped_column(
        ForeignKey("locations.id", ondelete="RESTRICT"), nullable=False
    )
    to_location_id: Mapped[int] = mapped_column(
        ForeignKey("locations.id", ondelete="RESTRICT"), nullable=False
    )
    item_id: Mapped[int | None] = mapped_column(ForeignKey("items.id", ondelete="RESTRICT"), nullable=True)
    hu_id: Mapped[int | None] = mapped_column(
        ForeignKey("handling_units.id", ondelete="RESTRICT"), nullable=True
    )
    qty: Mapped[Decimal] = mapped_column(Numeric(18, 3), nullable=False)
    qty_done: Mapped[Decimal] = mapped_column(
        Numeric(18, 3), nullable=False, default=Decimal("0"), server_default="0"
    )

    mission = relationship("Mission", back_populates="lines")
    from_location = relationship(
        "Location",
        back_populates="mission_line_sources",
        foreign_keys=[from_location_id],
    )
    to_location = relationship(
        "Location",
        back_populates="mission_line_destinations",
        foreign_keys=[to_location_id],
    )
    item = relationship("Item", back_populates="mission_lines")
    handling_unit = relationship("HandlingUnit", back_populates="mission_lines")
    movements = relationship("InventoryMovement", back_populates="mission_line")
