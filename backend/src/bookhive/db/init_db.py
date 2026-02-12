from bookhive.db.base import Base
from bookhive.db.engine import engine

# Import models so they register with SQLAlchemy metadata
from bookhive.db.models.user import User  # noqa: F401


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
