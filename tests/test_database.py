import pytest
from sqlalchemy.orm import joinedload
from database.database import SessionLocal, init_db
from database.models import User, Vegetable, Donation, Inventory

def test_database_models_creation():
    init_db()
    db = SessionLocal()
    try:
        veg_count = db.query(Vegetable).count()
        assert veg_count >= 0
    finally:
        db.close()

def test_eager_loading_inventory_vegetable_detached():
    db = SessionLocal()
    try:
        items = (
            db.query(Inventory)
            .options(joinedload(Inventory.vegetable))
            .filter(Inventory.status == "In Stock")
            .all()
        )
    finally:
        db.close()

    # Session is closed; accessing relationships must succeed without DetachedInstanceError
    for item in items:
        assert item.vegetable is not None
        assert isinstance(item.vegetable.name, str)
        assert len(item.vegetable.name) > 0
