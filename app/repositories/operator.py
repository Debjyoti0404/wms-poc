from sqlalchemy import select

from app.db.models.operator import Operator
from app.repositories.base import BaseRepository


class OperatorRepository(BaseRepository):
    def create(self, *, code: str, name: str, active: bool = True) -> Operator:
        entity = Operator(code=code, name=name, active=active)
        self.db.add(entity)
        self.db.flush()
        self.db.refresh(entity)
        return entity

    def get(self, operator_id: int) -> Operator | None:
        return self.db.get(Operator, operator_id)

    def list(self) -> list[Operator]:
        return list(self.db.scalars(select(Operator).order_by(Operator.id)).all())

    def update(self, operator: Operator, *, name: str | None = None, active: bool | None = None) -> Operator:
        if name is not None:
            operator.name = name
        if active is not None:
            operator.active = active
        self.db.flush()
        self.db.refresh(operator)
        return operator
