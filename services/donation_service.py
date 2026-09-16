import datetime
import random
from database.database import SessionLocal
from database.models import Donation, Inventory, Vegetable
from services.freshness_service import FreshnessService
from services.alert_service import AlertService

class DonationService:
    @staticmethod
    def generate_donation_code() -> str:
        date_str = datetime.date.today().strftime("%Y%m%d")
        rand_num = random.randint(1000, 9999)
        return f"DON-{date_str}-{rand_num}"

    @staticmethod
    def add_donation(
        donor_name: str,
        vegetable_name_or_id,
        quantity: float,
        unit: str = "kg",
        freshness_status: str = "Fresh",
        storage_condition: str = "Room Temperature",
        donation_date: datetime.date = None,
        notes: str = "",
        user_id: int = None
    ):
        if donation_date is None:
            donation_date = datetime.date.today()

        if quantity <= 0:
            return False, "Quantity must be greater than zero.", None

        db = SessionLocal()
        try:
            if isinstance(vegetable_name_or_id, int):
                veg = db.query(Vegetable).filter(Vegetable.id == vegetable_name_or_id).first()
            else:
                veg = db.query(Vegetable).filter(Vegetable.name.ilike(str(vegetable_name_or_id).strip())).first()
                if not veg:
                    veg = Vegetable(
                        name=str(vegetable_name_or_id).strip().title(),
                        category="Other",
                        default_shelf_life_days=7
                    )
                    db.add(veg)
                    db.flush()

            # Unified life & use-by calculation based on DB settings
            calc = FreshnessService.calculate_life_and_use_by(
                vegetable_name=veg.name,
                freshness=freshness_status,
                received_date=donation_date,
                db=db
            )
            use_by_date = calc["estimated_use_by_date"]
            priority_level = calc["priority"]
            alert_status = calc["status"]
            effective_life = calc["effective_remaining_life"]
            shelf_life_used = calc["configured_shelf_life"]
            multiplier_used = calc["multiplier_used"]

            donation_code = DonationService.generate_donation_code()

            new_donation = Donation(
                donation_code=donation_code,
                donor_name=donor_name.strip() if donor_name else "Anonymous Citizen",
                donation_date=donation_date,
                vegetable_id=veg.id,
                quantity=float(quantity),
                unit=unit,
                freshness_status=calc["freshness"],
                storage_condition=storage_condition,
                configured_shelf_life_used=shelf_life_used,
                multiplier_used=multiplier_used,
                effective_life_days=effective_life,
                alert_status=alert_status,
                estimated_use_by_date=use_by_date,
                notes=notes,
                created_by_user_id=user_id
            )
            db.add(new_donation)
            db.flush()

            inv_status = "In Stock"
            if calc["freshness"] == "SPOILED":
                inv_status = "Discarded"

            inventory_item = Inventory(
                donation_id=new_donation.id,
                vegetable_id=veg.id,
                initial_quantity=float(quantity),
                current_quantity=float(quantity) if inv_status == "In Stock" else 0.0,
                unit=unit,
                received_date=donation_date,
                freshness_status=calc["freshness"],
                configured_shelf_life_used=shelf_life_used,
                multiplier_used=multiplier_used,
                effective_life_days=effective_life,
                alert_status=alert_status,
                estimated_use_by_date=use_by_date,
                priority_level=priority_level,
                status=inv_status
            )
            db.add(inventory_item)
            db.commit()
            db.refresh(new_donation)

            AlertService.sync_inventory_alerts(db)
            return True, f"Donation {donation_code} recorded successfully and added to Inventory!", new_donation
        except Exception as e:
            db.rollback()
            return False, f"Failed to record donation: {str(e)}", None
        finally:
            db.close()

    @staticmethod
    def get_all_donations():
        db = SessionLocal()
        try:
            return db.query(Donation).order_by(Donation.donation_date.desc(), Donation.id.desc()).all()
        finally:
            db.close()
