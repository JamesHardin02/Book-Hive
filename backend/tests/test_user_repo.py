import os
import sys
import unittest

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
)

os.environ["BOOKHIVE_ENV"] = "test"

from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402
from sqlalchemy.pool import StaticPool  # noqa: E402

from bookhive.db.base import Base  # noqa: E402
from bookhive.repos.user_repo import UserRepo  # noqa: E402
from bookhive.db.models.user import User  # noqa: F401, E402


engine = create_engine(
    "sqlite+pysqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class UserRepoTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)

    @classmethod
    def tearDownClass(cls):
        engine.dispose()

    def setUp(self):
        self.db = SessionLocal()
        self.repo = UserRepo(self.db)

    def tearDown(self):
        self.db.close()

    def test_create_and_get_by_email(self):
        user = self.repo.create(
            username="repo", email="repo@example.com", hashed_password="hashed"
        )
        self.assertIsNotNone(user.id)

        fetched = self.repo.get_by_email("repo@example.com")
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched.id, user.id)

    def test_get_by_id_missing(self):
        self.assertIsNone(self.repo.get_by_id(999999))


if __name__ == "__main__":
    unittest.main()
