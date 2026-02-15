from sqlalchemy import select

from app.db.models.item import Item
from app.repositories.base import BaseRepository


class ItemRepository(BaseRepository):
    def create(self, *, sku: str, name: str, uom: str = "ea") -> Item:
        entity = Item(sku=sku, name=name, uom=uom)
        self.db.add(entity)
        self.db.flush()
        self.db.refresh(entity)
        return entity

    def get(self, item_id: int) -> Item | None:
        return self.db.get(Item, item_id)

    def list(self) -> list[Item]:
        return list(self.db.scalars(select(Item).order_by(Item.id)).all())
