import datetime
import pytest
from services.donation_service import DonationService
from services.waste_service import WasteService
from database.database import SessionLocal
from database.models import Inventory

def test_donation_and_inventory_lifecycle():
    # 1. Add Donation
    ok, msg, don = DonationService.add_donation(
        donor_name="Unit Test Donor",
        vegetable_name_or_id="Tomato",
        quantity=20.0,
        unit="kg",
        freshness_status="Fresh",
        storage_condition="Room Temperature",
        notes="Automated service test"
    )
    assert ok is True
    assert don is not None

    db = SessionLocal()
    try:
        inv = db.query(Inventory).filter(Inventory.donation_id == don.id).first()
        assert inv is not None
        assert inv.current_quantity == 20.0
        inv_id = inv.id
    finally:
        db.close()

    # 2. Record Usage (Deduct 5 kg)
    ok_use, msg_use = WasteService.record_usage(
        inventory_id=inv_id,
        quantity_used=5.0,
        meal_purpose="Testing soup"
    )
    assert ok_use is True

    db = SessionLocal()
    try:
        inv_after_use = db.query(Inventory).filter(Inventory.id == inv_id).first()
        assert inv_after_use.current_quantity == 15.0
    finally:
        db.close()

    # 3. Record Waste (Deduct 2 kg)
    ok_wst, msg_wst = WasteService.record_waste(
        inventory_id=inv_id,
        quantity_wasted=2.0,
        reason="Spoiled"
    )
    assert ok_wst is True

    db = SessionLocal()
    try:
        inv_after_waste = db.query(Inventory).filter(Inventory.id == inv_id).first()
        assert inv_after_waste.current_quantity == 13.0
    finally:
        db.close()

    # 4. Waste metrics check
    metrics = WasteService.get_waste_metrics()
    assert metrics["total_donated_qty"] > 0
    assert metrics["total_used_qty"] > 0
    assert metrics["total_wasted_qty"] > 0
    assert 0 <= metrics["waste_percentage"] <= 100
