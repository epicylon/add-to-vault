from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# SQLite database stored in the persistent Docker volume
SQLALCHEMY_DATABASE_URL = "sqlite:////app/data/add_to_vault.db"

# check_same_thread is required for SQLite when used with FastAPI
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency to get the database session in our API endpoints
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
