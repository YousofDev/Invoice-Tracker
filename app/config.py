from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql://postgres:1234@localhost:5432/invoice_tracker"
    testing_database_url: str = "postgresql://postgres:1234@localhost:5432/testing_db"


settings = Settings()
