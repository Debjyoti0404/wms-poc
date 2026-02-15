from sqlalchemy import select

from app.db.models.handling_unit import HandlingUnit, HandlingUnitStatus
from app.repositories.base import BaseRepository


class HandlingUnitRepository(BaseRepository):
    def create(
        self,
        *,
        hu_code: str,
        location_id: int,
        status: HandlingUnitStatus = HandlingUnitStatus.OPEN,
    ) -> HandlingUnit:
        entity = HandlingUnit(hu_code=hu_code, location_id=location_id, status=status)
        self.db.add(entity)
        self.db.flush()
        self.db.refresh(entity)
        return entity

    def get(self, handling_unit_id: int) -> HandlingUnit | None:
        return self.db.get(HandlingUnit, handling_unit_id)

    def list(self) -> list[HandlingUnit]:
        return list(self.db.scalars(select(HandlingUnit).order_by(HandlingUnit.id)).all())

    def update(
        self,
        handling_unit: HandlingUnit,
        *,
        location_id: int | None = None,
        status: HandlingUnitStatus | None = None,
    ) -> HandlingUnit:
        if location_id is not None:
            handling_unit.location_id = location_id
        if status is not None:
            handling_unit.status = status
        self.db.flush()
        self.db.refresh(handling_unit)
        return handling_unit
