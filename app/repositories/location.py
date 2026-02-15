from sqlalchemy import select

from app.db.models.location import Location, LocationType
from app.repositories.base import BaseRepository


class LocationRepository(BaseRepository):
    def create(
        self,
        *,
        code: str,
        name: str,
        type: LocationType = LocationType.BULK,
        active: bool = True,
    ) -> Location:
        entity = Location(code=code, name=name, type=type, active=active)
        self.db.add(entity)
        self.db.flush()
        self.db.refresh(entity)
        return entity

    def get(self, location_id: int) -> Location | None:
        return self.db.get(Location, location_id)

    def list(self) -> list[Location]:
        return list(self.db.scalars(select(Location).order_by(Location.id)).all())

    def update(
        self,
        location: Location,
        *,
        name: str | None = None,
        type: LocationType | None = None,
        active: bool | None = None,
    ) -> Location:
        if name is not None:
            location.name = name
        if type is not None:
            location.type = type
        if active is not None:
            location.active = active
        self.db.flush()
        self.db.refresh(location)
        return location
