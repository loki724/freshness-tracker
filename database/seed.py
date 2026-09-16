import datetime
from database.database import SessionLocal, init_db
from database.models import User, Vegetable, Donation, Inventory, UsageRecord, WasteRecord, SystemSetting, ScanResult
from auth.password import generate_salt, hash_password
from services.freshness_service import FreshnessService
from services.alert_service import AlertService

def seed_database():
    init_db()
    db = SessionLocal()
    try:
        # 1. Seed Users (Idempotent: check by unique email)
        staff = db.query(User).filter(User.email == "staff@nourishai.org").first()
        if not staff:
            salt1 = generate_salt()
            staff = User(
                full_name="Priya Sharma",
                email="staff@nourishai.org",
                phone="+91 98765 43210",
                password_hash=hash_password("staff123", salt1),
                salt=salt1,
                role="Kitchen Staff"
            )
            db.add(staff)

        volunteer = db.query(User).filter(User.email == "volunteer@nourishai.org").first()
        if not volunteer:
            salt2 = generate_salt()
            volunteer = User(
                full_name="Karthik Raj",
                email="volunteer@nourishai.org",
                phone="+91 98765 43211",
                password_hash=hash_password("volunteer123", salt2),
                salt=salt2,
                role="Volunteer"
            )
            db.add(volunteer)
        db.commit()

        # 2. Seed Vegetables (Idempotent: check by unique name)
        veg_list = [
            ("Spinach", "Leafy vegetables", 3, "Refrigerate or keep in damp cloth in cool area"),
            ("Tomato", "Fruit vegetables", 6, "Room temperature away from direct sunlight"),
            ("Carrot", "Root vegetables", 12, "Cool, dry container or crisper drawer"),
            ("Potato", "Tubers", 25, "Dark, dry and well-ventilated spot away from onions"),
            ("Onion", "Tubers", 25, "Dry, airy basket at room temperature"),
            ("Cabbage", "Leafy vegetables", 10, "Refrigerated crisper or cool shaded shelf"),
            ("Brinjal", "Fruit vegetables", 5, "Cool room temperature or crisper drawer"),
            ("Beans", "Leafy vegetables", 5, "Refrigerate in breathable bag"),
            ("Cauliflower", "Other", 7, "Keep dry in refrigerator crisper"),
            ("Capsicum", "Fruit vegetables", 7, "Crisper drawer in refrigerator")
        ]
        for vname, vcat, vshelf, vstor in veg_list:
            v_exist = db.query(Vegetable).filter(Vegetable.name == vname).first()
            if not v_exist:
                db.add(Vegetable(name=vname, category=vcat, default_shelf_life_days=vshelf, storage_recommendation=vstor))
        db.commit()

        # 3. Seed System Settings (Idempotent: check by unique key)
        settings_list = [
            ("urgent_threshold_days", "2", "Items expiring within these days trigger urgent cook alert"),
            ("use_soon_threshold_days", "5", "Items expiring within these days trigger use-soon alert"),
            ("org_name", "Santhi Welfare Children Home", "Name of the beneficiary organization"),
            ("default_unit", "kg", "Default weight unit for logging donations")
        ]
        for skey, sval, sdesc in settings_list:
            s_exist = db.query(SystemSetting).filter(SystemSetting.key == skey).first()
            if not s_exist:
                db.add(SystemSetting(key=skey, value=sval, description=sdesc))
        db.commit()

        # 4. Seed Realistic Sample Donations & Inventory (Idempotent: check by unique donation_code)
        today = datetime.date.today()
        staff_user = db.query(User).filter(User.email == "staff@nourishai.org").first()
        user_id = staff_user.id if staff_user else None

        sample_donations = [
            {"donor": "Green Valley Farms", "veg": "Spinach", "qty": 8.0, "days_ago": 2, "fresh": "Ripe", "storage": "Room Temperature"},
            {"donor": "Sunita Devi (Citizen)", "veg": "Tomato", "qty": 15.0, "days_ago": 4, "fresh": "Ripe", "storage": "Room Temperature"},
            {"donor": "City Market Vendors", "veg": "Brinjal", "qty": 12.0, "days_ago": 2, "fresh": "Fresh", "storage": "Room Temperature"},
            {"donor": "Ramesh Kumar (Citizen)", "veg": "Beans", "qty": 10.0, "days_ago": 1, "fresh": "Fresh", "storage": "Room Temperature"},
            {"donor": "Fresh Roots Co-op", "veg": "Carrot", "qty": 25.0, "days_ago": 6, "fresh": "Fresh", "storage": "Cool & Dark"},
            {"donor": "Rotary Club Donation", "veg": "Potato", "qty": 50.0, "days_ago": 3, "fresh": "Fresh", "storage": "Cool & Dark"},
            {"donor": "Metro Supermarket Surplus", "veg": "Cabbage", "qty": 20.0, "days_ago": 2, "fresh": "Fresh", "storage": "Refrigerated"},
            {"donor": "Citizen Collective", "veg": "Onion", "qty": 40.0, "days_ago": 4, "fresh": "Fresh", "storage": "Room Temperature"},
        ]

        for idx, item in enumerate(sample_donations, 10):
            rec_date = today - datetime.timedelta(days=item["days_ago"])
            veg = db.query(Vegetable).filter(Vegetable.name == item["veg"]).first()
            if not veg:
                continue

            don_code = f"DON-{rec_date.strftime('%Y%m%d')}-{1000 + idx}"
            
            # Idempotency check: Skip if donation_code already exists
            existing_don = db.query(Donation).filter(Donation.donation_code == don_code).first()
            if existing_don:
                continue

            use_by = FreshnessService.calculate_use_by_date(veg.name, rec_date, item["fresh"], item["storage"])
            priority, status_lbl, days_rem, _ = FreshnessService.calculate_priority_and_status(use_by, today)
            
            don = Donation(
                donation_code=don_code,
                donor_name=item["donor"],
                donation_date=rec_date,
                vegetable_id=veg.id,
                quantity=item["qty"],
                unit="kg",
                freshness_status=item["fresh"],
                storage_condition=item["storage"],
                estimated_use_by_date=use_by,
                notes="Community donation batch",
                created_by_user_id=user_id
            )
            db.add(don)
            db.flush()

            used_qty = 3.0 if item["qty"] > 15 else 1.5
            curr_qty = item["qty"] - used_qty

            inv = Inventory(
                donation_id=don.id,
                vegetable_id=veg.id,
                initial_quantity=item["qty"],
                current_quantity=curr_qty,
                unit="kg",
                received_date=rec_date,
                freshness_status=item["fresh"],
                estimated_use_by_date=use_by,
                priority_level=priority,
                status="In Stock"
            )
            db.add(inv)
            db.flush()

            usage = UsageRecord(
                inventory_id=inv.id,
                vegetable_id=veg.id,
                quantity_used=used_qty,
                unit="kg",
                date_used=today - datetime.timedelta(days=1),
                meal_purpose="Community Lunch for Children",
                staff_name="Priya Sharma",
                notes="Cooked in noon meal"
            )
            db.add(usage)

        # 5. Seed initial waste record if none exists
        if db.query(WasteRecord).count() == 0:
            waste_inv = db.query(Inventory).filter(Inventory.priority_level == "Urgent").first()
            if not waste_inv:
                waste_inv = db.query(Inventory).first()
            if waste_inv:
                db.add(WasteRecord(
                    inventory_id=waste_inv.id,
                    vegetable_id=waste_inv.vegetable_id,
                    quantity_wasted=1.5,
                    unit="kg",
                    date_wasted=today,
                    reason="Spoiled",
                    notes="Damaged trimmings upon arrival"
                ))

        db.commit()
        AlertService.sync_inventory_alerts(db)
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
    print("Database seeded and alerts synchronized successfully.")
