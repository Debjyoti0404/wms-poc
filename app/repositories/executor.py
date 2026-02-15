from datetime import datetime
from decimal import Decimal

from sqlalchemy import select

from app.db.models.executor import Executor, ExecutorType
from app.repositories.base import BaseRepository


class ExecutorRepository(BaseRepository):
    def create(
        self,
        *,
        code: str,
        name: str,
        executor_type: ExecutorType,
        max_payload_kg: Decimal,
        active: bool = True,
    ) -> Executor:
        entity = Executor(
            code=code,
            name=name,
            executor_type=executor_type,
            max_payload_kg=max_payload_kg,
            active=active,
        )
        self.db.add(entity)
        self.db.flush()
        self.db.refresh(entity)
        return entity

    def get(self, executor_id: int) -> Executor | None:
        return self.db.get(Executor, executor_id)

    def list(self) -> list[Executor]:
        return list(self.db.scalars(select(Executor).order_by(Executor.id)).all())

    def update(
        self,
        executor: Executor,
        *,
        name: str | None = None,
        executor_type: ExecutorType | None = None,
        max_payload_kg: Decimal | None = None,
        active: bool | None = None,
        last_seen_at: datetime | None = None,
    ) -> Executor:
        if name is not None:
            executor.name = name
        if executor_type is not None:
            executor.executor_type = executor_type
        if max_payload_kg is not None:
            executor.max_payload_kg = max_payload_kg
        if active is not None:
            executor.active = active
        if last_seen_at is not None:
            executor.last_seen_at = last_seen_at
        self.db.flush()
        self.db.refresh(executor)
        return executor
