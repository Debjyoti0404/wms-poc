from datetime import datetime
from decimal import Decimal
from enum import StrEnum

from sqlalchemy import Boolean, DateTime, Enum, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ExecutorType(StrEnum):
    HUMAN = "human"
    AGV = "agv"


class Executor(Base):
    __tablename__ = "executors"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    code: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    executor_type: Mapped[ExecutorType] = mapped_column(
        Enum(ExecutorType, name="executor_type", native_enum=False),
        nullable=False,
        default=ExecutorType.HUMAN,
        server_default=ExecutorType.HUMAN.value,
    )
    max_payload_kg: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), nullable=False, default=Decimal("500"), server_default="500"
    )
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="1")
    last_seen_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    assigned_missions = relationship("Mission", back_populates="assigned_executor")
    movements = relationship("InventoryMovement", back_populates="executed_by_executor")
