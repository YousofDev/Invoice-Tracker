from fastapi import APIRouter, Depends, status
from typing import List

from app.client.service import ClientService
from app.client.schemas import (
    ClientCreate,
    ClientUpdate,
    ClientInDB,
)

router = APIRouter()


@router.get("/clients", response_model=List[ClientInDB])
def get_client_list(
    skip: int = 0, limit: int = 100, service: ClientService = Depends()
):
    return service.get_client_list(skip, limit)


@router.post("/clients", status_code=status.HTTP_201_CREATED, response_model=ClientInDB)
def create_client(client: ClientCreate, service: ClientService = Depends()):
    return service.create_client(client)


@router.get("/clients/{client_id}", response_model=ClientInDB)
def get_client(client_id: int, service: ClientService = Depends()):
    return service.get_client(client_id)


@router.put("/clients/{client_id}", response_model=ClientInDB)
def update_client(
    client_id: int, client: ClientUpdate, service: ClientService = Depends()
):
    return service.update_client(client_id, client)


@router.delete("/clients/{client_id}")
def delete_client(client_id: int, service: ClientService = Depends()):
    return service.delete_client(client_id)
