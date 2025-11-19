from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config.config import settings
from sqlalchemy.pool import QueuePool
import urllib.parse

# ------------------------------
# Database Configuration
# ------------------------------

DB_CONNECTION = settings.DB_CONNECTION.strip()  # e.g. "mysql"
DB_USERNAME = settings.DB_USER
DB_PASSWORD = settings.DB_PASSWORD
DB_HOST = settings.DB_HOST
DB_PORT = str(settings.DB_PORT)
DB_DATABASE = settings.DB_NAME
DB_DRIVER = settings.DB_DRIVER  # e.g. "pymysql"

# ------------------------------
# Build Connection String
# ------------------------------
if DB_PASSWORD:
    encoded_password = urllib.parse.quote_plus(DB_PASSWORD)
    DATABASE_URL = (
        f"{DB_CONNECTION}+{DB_DRIVER}://{DB_USERNAME}:{encoded_password}@"
        f"{DB_HOST}:{DB_PORT}/{DB_DATABASE}"
    )
# else:
    DATABASE_URL = (
        f"{DB_CONNECTION}+{DB_DRIVER}://{DB_USERNAME}@"
        f"{DB_HOST}:{DB_PORT}/{DB_DATABASE}"
    )

# ------------------------------
# Engine and Session
# ------------------------------
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=40,
    max_overflow=60,
    pool_timeout=10,
    pool_recycle=3600,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ------------------------------
# Base Model for ORM
# ------------------------------
Base = declarative_base()  # ✅ Correct definition — no cls needed


# ------------------------------
# Dependency for FastAPI
# ------------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
