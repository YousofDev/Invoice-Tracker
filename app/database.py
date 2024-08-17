from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.config import settings


engine = create_engine(
    settings.database_url,
    echo=False,
)  # connect_args={"sslmode": "require"}

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    from app.auth.models import User
    from app.item.models import Item
    from app.payment.models import Payment
    from app.client.models import Client
    from app.invoice.models import Invoice, InvoiceItem

    Base.metadata.create_all(bind=engine)
