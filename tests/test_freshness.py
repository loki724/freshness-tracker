import datetime
import pytest
from services.freshness_service import FreshnessService

def test_shelf_life_calculation():
    rec_date = datetime.date(2026, 9, 14)
    
    # Fresh tomato (6 days)
    use_by_fresh = FreshnessService.calculate_use_by_date("Tomato", rec_date, freshness="Fresh", storage_condition="Room Temperature")
    assert use_by_fresh == datetime.date(2026, 9, 20)

    # Ripe tomato (50% reduction = 3 days)
    use_by_ripe = FreshnessService.calculate_use_by_date("Tomato", rec_date, freshness="Ripe", storage_condition="Room Temperature")
    assert use_by_ripe == datetime.date(2026, 9, 17)

    # Refrigerated Spinach (3 days * 1.4 = 4 days)
    use_by_refrig = FreshnessService.calculate_use_by_date("Spinach", rec_date, freshness="Fresh", storage_condition="Refrigerated")
    assert use_by_refrig == datetime.date(2026, 9, 18)

def test_priority_and_status():
    today = datetime.date(2026, 9, 14)

    # Urgent (expired / 1 day)
    priority, status, days_rem, color = FreshnessService.calculate_priority_and_status(datetime.date(2026, 9, 15), today)
    assert priority == "Urgent"
    assert days_rem == 1

    # Use Soon (4 days)
    priority, status, days_rem, color = FreshnessService.calculate_priority_and_status(datetime.date(2026, 9, 18), today)
    assert priority == "Use Soon"
    assert days_rem == 4

    # Fresh (>5 days)
    priority, status, days_rem, color = FreshnessService.calculate_priority_and_status(datetime.date(2026, 9, 25), today)
    assert priority == "Normal"
    assert days_rem == 11
