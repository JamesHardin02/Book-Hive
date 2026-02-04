import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL

load_dotenv()

def build_connection_url() -> str:
    # mysqlclient is referred to as "mysqldb" driver name in SQLAlchemy URLs
    # dialect+driver://user:pass@host:port/dbname
    return URL.create(
      "mysql+mysqldb",
      username= os.getenv("DB_USER", "root"),
      password= os.getenv("DB_PASSWORD", ""),
      host= os.getenv("DB_HOST", "localhost"),
      port= os.getenv("DB_PORT", "3307"),
      database= os.getenv("DB_NAME", "bookhive"),
    )

engine = create_engine(build_connection_url(), pool_pre_ping=True)

def db_healthcheck() -> tuple[bool, str]:
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True, "connected"
    except Exception as ex:
        return False, f"error: {type(ex).__name__}"
