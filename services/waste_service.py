import datetime
from database.database import SessionLocal
from database.models import UsageRecord, WasteRecord, Inventory, Donation, Vegetable
from services.alert_service import AlertService

class WasteService:
    @staticmethod
    def record_usage(inventory_id: int, quantity_used: float, staff_name: str = "Kitchen Staff", meal_purpose: str = "Lunch for Children", date_used: datetime.date = None, notes: str = ""):
        if date_used is None:
            date_used = datetime.date.today()

        if quantity_used <= 0:
            return False, "Usage quantity must be greater than zero."

        db = SessionLocal()
        try:
            item = db.query(Inventory).filter(Inventory.id == inventory_id).first()
            if not item:
                return False, "Inventory item not found."

            if quantity_used > item.current_quantity:
                return False, f"Cannot use {quantity_used} {item.unit}. Only {item.current_quantity} {item.unit} remaining in stock."

            item.current_quantity -= float(quantity_used)
            if item.current_quantity <= 0.001:
                item.current_quantity = 0.0
                item.status = "Depleted"

            usage = UsageRecord(
                inventory_id=item.id,
                vegetable_id=item.vegetable_id,
                quantity_used=float(quantity_used),
                unit=item.unit,
                date_used=date_used,
                meal_purpose=meal_purpose,
                staff_name=staff_name,
                notes=notes
            )
            db.add(usage)
            db.commit()

            AlertService.sync_inventory_alerts(db)
            return True, f"Successfully recorded {quantity_used} {item.unit} used for {meal_purpose}. Stock updated!"
        except Exception as e:
            db.rollback()
            return False, f"Error logging usage: {str(e)}"
        finally:
            db.close()

    @staticmethod
    def record_waste(inventory_id: int, quantity_wasted: float, reason: str = "Spoiled", date_wasted: datetime.date = None, notes: str = ""):
        if date_wasted is None:
            date_wasted = datetime.date.today()

        if quantity_wasted <= 0:
            return False, "Wasted quantity must be greater than zero."

        db = SessionLocal()
        try:
            item = db.query(Inventory).filter(Inventory.id == inventory_id).first()
            if not item:
                return False, "Inventory item not found."

            if quantity_wasted > item.current_quantity:
                return False, f"Cannot waste {quantity_wasted} {item.unit}. Only {item.current_quantity} {item.unit} left in stock."

            item.current_quantity -= float(quantity_wasted)
            if item.current_quantity <= 0.001:
                item.current_quantity = 0.0
                item.status = "Discarded"

            waste = WasteRecord(
                inventory_id=item.id,
                vegetable_id=item.vegetable_id,
                quantity_wasted=float(quantity_wasted),
                unit=item.unit,
                date_wasted=date_wasted,
                reason=reason,
                notes=notes
            )
            db.add(waste)
            db.commit()

            AlertService.sync_inventory_alerts(db)
            return True, f"Logged {quantity_wasted} {item.unit} as waste ({reason}). Inventory updated."
        except Exception as e:
            db.rollback()
            return False, f"Error logging waste: {str(e)}"
        finally:
            db.close()

    @staticmethod
    def get_waste_metrics():
        db = SessionLocal()
        try:
            donations = db.query(Donation).all()
            usages = db.query(UsageRecord).all()
            wastes = db.query(WasteRecord).all()
            inventory_items = db.query(Inventory).all()

            total_donated_qty = sum(d.quantity for d in donations)
            total_used_qty = sum(u.quantity_used for u in usages)
            total_wasted_qty = sum(w.quantity_wasted for w in wastes)
            current_stock_qty = sum(i.current_quantity for i in inventory_items if i.status == "In Stock")

            waste_percentage = 0.0
            if total_donated_qty > 0:
                waste_percentage = (total_wasted_qty / total_donated_qty) * 100.0

            return {
                "total_donations_count": len(donations),
                "total_donated_qty": round(total_donated_qty, 2),
                "total_used_qty": round(total_used_qty, 2),
                "total_wasted_qty": round(total_wasted_qty, 2),
                "current_stock_qty": round(current_stock_qty, 2),
                "waste_percentage": round(waste_percentage, 1),
                "utilization_rate": round((total_used_qty / total_donated_qty * 100) if total_donated_qty > 0 else 0.0, 1)
            }
        finally:
            db.close()
