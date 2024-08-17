from fastapi import Depends, HTTPException, status
from sqlalchemy import delete, update
from sqlalchemy.orm import Session

from app.database import get_db
from app.client.models import Client
from app.client.schemas import (
    ClientCreate,
    ClientUpdate,
    ClientInDB,
)


class ClientService:

    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    def get_client_list(self, skip: int = 0, limit: int = 100):
        clients = self.db.query(Client).offset(skip).limit(limit).all()
        return clients

    def get_client(self, client_id: int) -> ClientInDB:
        client = self.db.query(Client).filter(Client.id == client_id).first()

        if not client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Client not found"
            )

        return ClientInDB.model_validate(client)

    def create_client(self, client_data: ClientCreate) -> ClientInDB:
        client_dict = client_data.model_dump()

        client = Client(**client_dict)
        self.db.add(client)

        self.db.commit()
        self.db.refresh(client)

        return ClientInDB.model_validate(client)

    def update_client(self, client_id: int, client_data: ClientUpdate) -> ClientInDB:
        client_dict = client_data.model_dump()

        stmt = (
            update(Client)
            .where(Client.id == client_id)
            .values(**client_dict)
            .returning(Client)
        )

        result = self.db.execute(stmt)
        updated_client = result.scalar_one()

        self.db.commit()

        return ClientInDB.model_validate(updated_client)

    def delete_client(self, client_id: int) -> None:
        stmt = delete(Client).where(Client.id == client_id)
        self.db.execute(stmt)
        self.db.commit()
