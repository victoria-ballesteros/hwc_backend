import app.adapters.database.postgres.models  # noqa: F401

from app.adapters.database.postgres.connection import engine, Base

def initialize_tables() -> None:
    try:
        Base.metadata.create_all(bind=engine) # type: ignore

    except Exception as e:
        raise e
