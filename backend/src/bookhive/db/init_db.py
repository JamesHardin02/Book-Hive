from bookhive.db.base import Base
from bookhive.db.engine import engine

# Import models so they register with SQLAlchemy metadata
from bookhive.db.models.book import Book  # noqa: F401
from bookhive.db.models.inventory import Inventory  # noqa: F401
from bookhive.db.models.loan import Loan  # noqa: F401
from bookhive.db.models.location import Location  # noqa: F401
from bookhive.db.models.member import Member  # noqa: F401
from bookhive.db.models.metadata_cache import Metadata_Cache  # noqa: F401
from bookhive.db.models.sale import Sale  # noqa: F401
from bookhive.db.models.stock_adjustment import Stock_Adjustment  # noqa: F401
from bookhive.db.models.user import User  # noqa: F401
from bookhive.db.models.app_setting import AppSetting  # noqa: F401

def init_db() -> None:
    Base.metadata.create_all(bind=engine)
