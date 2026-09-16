import datetime
from sqlalchemy.orm import joinedload
from database.database import SessionLocal
from database.models import Alert, Inventory, Vegetable
from services.freshness_service import FreshnessService

class AlertService:
    @staticmethod
    def sync_inventory_alerts(db=None):
        close_db = False
        if db is None:
            db = SessionLocal()
            close_db = True
        try:
            today = datetime.date.today()
            active_items = (
                db.query(Inventory)
                .options(joinedload(Inventory.vegetable))
                .filter(
                    Inventory.status == "In Stock",
                    Inventory.current_quantity > 0
                )
                .all()
            )

            settings = FreshnessService.get_settings(db)
            urgent_days = settings["urgent_threshold_days"]
            use_soon_days = settings["use_soon_threshold_days"]

            for item in active_items:
                days_left = (item.estimated_use_by_date - today).days
                veg_name = item.vegetable.name if item.vegetable else "Vegetable"
                fresh_status = str(item.freshness_status).upper()
                
                existing_alert = db.query(Alert).filter(
                    Alert.inventory_id == item.id,
                    Alert.is_resolved == False
                ).first()

                if "SPOIL" in fresh_status or days_left < 0:
                    msg = f"🚨 {veg_name} ({item.current_quantity} {item.unit}) is classified as spoiled/expired. Do not use."
                    alert_type = "SPOILED"
                    severity = "CRITICAL"
                elif days_left <= urgent_days:
                    msg = f"⚠ {veg_name} ({item.current_quantity} {item.unit}) should be used within 24 hours (Estimated Use-By: {item.estimated_use_by_date})."
                    alert_type = "URGENT"
                    severity = "CRITICAL"
                elif days_left <= use_soon_days:
                    msg = f"🟡 {veg_name} ({item.current_quantity} {item.unit}) is in medium freshness condition. Use within approximately {days_left} days."
                    alert_type = "USE_SOON"
                    severity = "WARNING"
                else:
                    if existing_alert:
                        existing_alert.is_resolved = True
                    continue

                if not existing_alert:
                    db.add(Alert(inventory_id=item.id, alert_type=alert_type, message=msg, severity=severity))
                else:
                    existing_alert.alert_type = alert_type
                    existing_alert.message = msg
                    existing_alert.severity = severity

            db.commit()
        finally:
            if close_db:
                db.close()

    @staticmethod
    def get_active_alerts():
        db = SessionLocal()
        try:
            AlertService.sync_inventory_alerts(db)
            return db.query(Alert).filter(Alert.is_resolved == False).order_by(Alert.created_at.desc()).all()
        finally:
            db.close()

    @staticmethod
    def resolve_alert(alert_id: int):
        db = SessionLocal()
        try:
            alert = db.query(Alert).filter(Alert.id == alert_id).first()
            if alert:
                alert.is_resolved = True
                alert.is_viewed = True
                db.commit()
                return True
            return False
        finally:
            db.close()
