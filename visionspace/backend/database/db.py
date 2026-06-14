from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from visionspace.backend.config.config import settings
from visionspace.backend.database.models import Base

DATABASE_URL = settings.DATABASE_URL

connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Create all tables in the SQLite database and run self-healing migrations for missing columns."""
    from sqlalchemy import inspect, text
    Base.metadata.create_all(bind=engine)
    
    # Self-healing migration for missing columns
    inspector = inspect(engine)
    columns = [c["name"] for c in inspector.get_columns("products")]
    if "currency" not in columns:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE products ADD COLUMN currency VARCHAR DEFAULT 'INR'"))

def get_db():
    """FastAPI DB session generator."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
