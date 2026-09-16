import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, scoped_session

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

DB_PATH = os.path.join(DATA_DIR, "nourishai.db")
DATABASE_URL = os.getenv("NOURISHAI_DB_URL", f"sqlite:///{DB_PATH}")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    echo=False
)

SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, expire_on_commit=False, bind=engine))
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    from database import models
    Base.metadata.create_all(bind=engine)
    
    # Safe SQLite column migration for new tracking columns
    if "sqlite" in DATABASE_URL:
        with engine.connect() as conn:
            # Check inventory columns
            result = conn.exec_driver_sql("PRAGMA table_info(inventory)").fetchall()
            existing_cols = [row[1] for row in result]
            if "configured_shelf_life_used" not in existing_cols:
                conn.exec_driver_sql("ALTER TABLE inventory ADD COLUMN configured_shelf_life_used INTEGER DEFAULT 7")
            if "multiplier_used" not in existing_cols:
                conn.exec_driver_sql("ALTER TABLE inventory ADD COLUMN multiplier_used FLOAT DEFAULT 1.0")
            if "effective_life_days" not in existing_cols:
                conn.exec_driver_sql("ALTER TABLE inventory ADD COLUMN effective_life_days INTEGER DEFAULT 7")
            if "alert_status" not in existing_cols:
                conn.exec_driver_sql("ALTER TABLE inventory ADD COLUMN alert_status VARCHAR(50) DEFAULT 'SAFE / FRESH'")

            # Check donations columns
            res_don = conn.exec_driver_sql("PRAGMA table_info(donations)").fetchall()
            existing_don_cols = [row[1] for row in res_don]
            if "configured_shelf_life_used" not in existing_don_cols:
                conn.exec_driver_sql("ALTER TABLE donations ADD COLUMN configured_shelf_life_used INTEGER DEFAULT 7")
            if "multiplier_used" not in existing_don_cols:
                conn.exec_driver_sql("ALTER TABLE donations ADD COLUMN multiplier_used FLOAT DEFAULT 1.0")
            if "effective_life_days" not in existing_don_cols:
                conn.exec_driver_sql("ALTER TABLE donations ADD COLUMN effective_life_days INTEGER DEFAULT 7")
            if "alert_status" not in existing_don_cols:
                conn.exec_driver_sql("ALTER TABLE donations ADD COLUMN alert_status VARCHAR(50) DEFAULT 'SAFE / FRESH'")

# Auto-init on import
init_db()
