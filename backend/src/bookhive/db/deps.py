from collections.abc import Generator

from bookhive.db.engine import SessionLocal


def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
