from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from .core import settings


s = settings()


engine = create_engine(
    s.database_url,
    connect_args={
        "check_same_thread": False
    } if s.database_url.startswith("sqlite") else {}
)


SessionLocal = sessionmaker(
    bind=engine
)


class Base(DeclarativeBase):
    pass


def db():

    database = SessionLocal()

    try:
        yield database

    finally:
        database.close()


def init_db():

    from .models import User, Recommendation

    Base.metadata.create_all(engine)