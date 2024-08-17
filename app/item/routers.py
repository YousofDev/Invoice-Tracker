from fastapi import APIRouter, Depends
from typing import List

from app.item.service import ItemService
from app.item.schemas import (
    ItemCreate,
    ItemUpdate,
    ItemInDB,
)

router = APIRouter()


@router.get("/items", response_model=List[ItemInDB])
def get_item_list(skip: int = 0, limit: int = 100, service: ItemService = Depends()):
    return service.get_item_list(skip, limit)


@router.post("/items", response_model=ItemInDB)
def create_item(item: ItemCreate, service: ItemService = Depends()):
    return service.create_item(item)


@router.get("/items/{item_id}", response_model=ItemInDB)
def get_item(item_id: int, service: ItemService = Depends()):
    return service.get_item(item_id)


@router.put("/items/{item_id}", response_model=ItemInDB)
def update_item(item_id: int, item: ItemUpdate, service: ItemService = Depends()):
    return service.update_item(item_id, item)


@router.delete("/items/{item_id}")
def delete_item(item_id: int, service: ItemService = Depends()):
    return service.delete_item(item_id)
