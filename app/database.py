import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL is None:
    raise RuntimeError(
        "DATABASE_URL is not set. Did you create a .env file? "
        "See .env.example for the expected format."
    )

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Base class that all SQLAlchemy models inherit from."""
    pass


def get_db():
    """
    Dependency function that provides a database session to API routes.

    Using a generator with try/finally guarantees the session is always
    closed after the request finishes, even if an error occurs — this
    prevents connection leaks under load.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()