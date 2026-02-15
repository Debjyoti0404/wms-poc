from datetime import datetime
from decimal import Decimal
from enum import StrEnum

from sqlalchemy import CheckConstraint, DateTime, Enum, ForeignKey, Numeric, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class InventoryMovementType(StrEnum):
    MOVE = "move"
    ADJUSTMENT = "adjustment"


class InventoryPosition(Base):
    __tablename__ = "inventory_positions"
    __table_args__ = (
        UniqueConstraint("hu_id", "item_id", name="uq_inventory_positions_hu_item"),
        CheckConstraint("qty_on_hand >= 0", name="ck_inventory_positions_on_hand_non_negative"),
        CheckConstraint("qty_reserved >= 0", name="ck_inventory_positions_reserved_non_negative"),
        CheckConstraint(
            "qty_reserved <= qty_on_hand",
            name="ck_inventory_positions_reserved_le_on_hand",
        ),
        CheckConstraint("version >= 1", name="ck_inventory_positions_version_positive"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    hu_id: Mapped[int] = mapped_column(ForeignKey("handling_units.id", ondelete="CASCADE"), nullable=False)
    item_id: Mapped[int] = mapped_column(ForeignKey("items.id", ondelete="RESTRICT"), nullable=False)
    qty_on_hand: Mapped[Decimal] = mapped_column(
        Numeric(18, 3), nullable=False, default=Decimal("0"), server_default="0"
    )
    qty_reserved: Mapped[Decimal] = mapped_column(
        Numeric(18, 3), nullable=False, default=Decimal("0"), server_default="0"
    )
    version: Mapped[int] = mapped_column(nullable=False, default=1, server_default="1")
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    handling_unit = relationship("HandlingUnit", back_populates="positions")
    item = relationship("Item", back_populates="positions")


class InventoryMovement(Base):
    __tablename__ = "inventory_movements"
    __table_args__ = (
        CheckConstraint("qty > 0", name="ck_inventory_movements_qty_positive"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    mission_line_id: Mapped[int | None] = mapped_column(
        ForeignKey("mission_lines.id", ondelete="SET NULL"), nullable=True
    )
    movement_type: Mapped[InventoryMovementType] = mapped_column(
        Enum(InventoryMovementType, name="inventory_movement_type", native_enum=False),
        nullable=False,
        default=InventoryMovementType.MOVE,
        server_default=InventoryMovementType.MOVE.value,
    )
    item_id: Mapped[int | None] = mapped_column(
        ForeignKey("items.id", ondelete="RESTRICT"), nullable=True
    )
    from_location_id: Mapped[int | None] = mapped_column(
        ForeignKey("locations.id", ondelete="RESTRICT"), nullable=True
    )
    to_location_id: Mapped[int | None] = mapped_column(
        ForeignKey("locations.id", ondelete="RESTRICT"), nullable=True
    )
    from_hu_id: Mapped[int | None] = mapped_column(
        ForeignKey("handling_units.id", ondelete="RESTRICT"), nullable=True
    )
    to_hu_id: Mapped[int | None] = mapped_column(
        ForeignKey("handling_units.id", ondelete="RESTRICT"), nullable=True
    )
    qty: Mapped[Decimal] = mapped_column(Numeric(18, 3), nullable=False)
    executed_by_executor_id: Mapped[int | None] = mapped_column(
        ForeignKey("executors.id", ondelete="SET NULL"), nullable=True
    )
    executed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    idempotency_key: Mapped[str | None] = mapped_column(String(128), unique=True, nullable=True)
    reason: Mapped[str | None] = mapped_column(String(500), nullable=True)

    mission_line = relationship("MissionLine", back_populates="movements")
    item = relationship("Item", back_populates="movements")
    executed_by_executor = relationship("Executor", back_populates="movements")
    from_handling_unit = relationship(
        "HandlingUnit",
        back_populates="movement_source_hus",
        foreign_keys=[from_hu_id],
    )
    to_handling_unit = relationship(
        "HandlingUnit",
        back_populates="movement_destination_hus",
        foreign_keys=[to_hu_id],
    )
