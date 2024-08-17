from fastapi import Depends, HTTPException, status
from sqlalchemy import delete, update
from sqlalchemy.orm import Session

from app.database import get_db
from app.item.models import Item
from app.item.schemas import (
    ItemCreate,
    ItemUpdate,
    ItemInDB,
)


class ItemService:

    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    def get_item_list(self, skip: int = 0, limit: int = 100):
        clients = self.db.query(Item).offset(skip).limit(limit).all()
        return clients

    def get_item(self, item_id: int) -> ItemInDB:

        item = self.db.query(Item).filter(Item.id == item_id).first()
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Item not found"
            )

        return ItemInDB.model_validate(item)

    def create_item(self, item_data: ItemCreate) -> ItemInDB:
        item_dict = item_data.model_dump()

        item = Item(**item_dict)
        self.db.add(item)

        self.db.commit()
        self.db.refresh(item)

        return ItemInDB.model_validate(item)

    def update_item(self, item_id: int, item_data: ItemUpdate) -> ItemInDB:
        item_dict = item_data.model_dump()

        stmt = (
            update(Item).where(Item.id == item_id).values(**item_dict).returning(Item)
        )

        result = self.db.execute(stmt)
        updated_item = result.scalar_one()

        self.db.commit()

        return ItemInDB.model_validate(updated_item)

    def delete_item(self, item_id: int) -> None:
        stmt = delete(Item).where(Item.id == item_id)
        self.db.execute(stmt)
        self.db.commit()
