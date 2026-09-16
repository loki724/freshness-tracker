import datetime
from sqlalchemy.orm import joinedload
from database.database import SessionLocal
from database.models import Vegetable, SystemSetting, Inventory

DEFAULT_SHELF_LIVES = {
    "Spinach": 4,
    "Tomato": 7,
    "Cabbage": 10,
    "Carrot": 10,
    "Potato": 14,
    "Onion": 25,
    "Brinjal": 5,
    "Beans": 5,
    "Cauliflower": 7,
    "Capsicum": 7,
    "Cucumber": 6,
    "Bottle Gourd": 7
}

DEFAULT_SETTINGS = {
    "fresh_multiplier": "1.0",        # 100%
    "medium_multiplier": "0.40",      # 40%
    "spoiled_multiplier": "0.0",      # 0%
    "urgent_threshold_days": "1",     # 0-1 days
    "use_soon_threshold_days": "3",   # 2-3 days
    "confidence_threshold": "0.50",   # 50%
    "iou_threshold": "0.45",          # 45%
    "org_name": "Santhi Welfare Children Home",
    "default_unit": "kg"
}

class FreshnessService:
    @staticmethod
    def get_settings(db=None) -> dict:
        """
        Single Source of Truth: Reads all active settings from SQLite database.
        """
        close_db = False
        if db is None:
            db = SessionLocal()
            close_db = True
        try:
            settings_records = db.query(SystemSetting).all()
            settings_map = {s.key: s.value for s in settings_records}
            latest_time = max([s.updated_at for s in settings_records if s.updated_at] or [datetime.datetime.utcnow()])

            fresh_mult = float(settings_map.get("fresh_multiplier", DEFAULT_SETTINGS["fresh_multiplier"]))
            med_mult = float(settings_map.get("medium_multiplier", DEFAULT_SETTINGS["medium_multiplier"]))
            spoil_mult = float(settings_map.get("spoiled_multiplier", DEFAULT_SETTINGS["spoiled_multiplier"]))
            urgent_thresh = int(float(settings_map.get("urgent_threshold_days", DEFAULT_SETTINGS["urgent_threshold_days"])))
            use_soon_thresh = int(float(settings_map.get("use_soon_threshold_days", DEFAULT_SETTINGS["use_soon_threshold_days"])))
            conf_thresh = float(settings_map.get("confidence_threshold", DEFAULT_SETTINGS["confidence_threshold"]))
            iou_thresh = float(settings_map.get("iou_threshold", DEFAULT_SETTINGS["iou_threshold"]))
            org_name = settings_map.get("org_name", DEFAULT_SETTINGS["org_name"])
            default_unit = settings_map.get("default_unit", DEFAULT_SETTINGS["default_unit"])

            return {
                "fresh_multiplier": fresh_mult,
                "medium_multiplier": med_mult,
                "spoiled_multiplier": spoil_mult,
                "fresh_multiplier_pct": int(round(fresh_mult * 100)),
                "medium_multiplier_pct": int(round(med_mult * 100)),
                "spoiled_multiplier_pct": int(round(spoil_mult * 100)),
                "urgent_threshold_days": urgent_thresh,
                "use_soon_threshold_days": use_soon_thresh,
                "confidence_threshold": conf_thresh,
                "confidence_threshold_pct": int(round(conf_thresh * 100)),
                "iou_threshold": iou_thresh,
                "iou_threshold_pct": int(round(iou_thresh * 100)),
                "org_name": org_name,
                "default_unit": default_unit,
                "last_updated": latest_time.strftime("%d %B %Y, %I:%M %p")
            }
        finally:
            if close_db:
                db.close()

    @staticmethod
    def save_settings(settings_dict: dict, db=None) -> bool:
        """
        Saves updated multipliers and thresholds to SQLite database.
        """
        close_db = False
        if db is None:
            db = SessionLocal()
            close_db = True
        try:
            now = datetime.datetime.utcnow()
            for key, val in settings_dict.items():
                setting = db.query(SystemSetting).filter(SystemSetting.key == key).first()
                if setting:
                    setting.value = str(val)
                    setting.updated_at = now
                else:
                    db.add(SystemSetting(key=key, value=str(val), updated_at=now))
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            print(f"Error saving settings: {e}")
            return False
        finally:
            if close_db:
                db.close()

    @staticmethod
    def get_shelf_life_days(vegetable_name: str, db=None) -> int:
        close_db = False
        if db is None:
            db = SessionLocal()
            close_db = True
        try:
            veg = db.query(Vegetable).filter(Vegetable.name.ilike(vegetable_name.strip())).first()
            if veg and veg.default_shelf_life_days is not None:
                return int(veg.default_shelf_life_days)
            return DEFAULT_SHELF_LIVES.get(vegetable_name.strip().title(), 7)
        finally:
            if close_db:
                db.close()

    @staticmethod
    def calculate_life_and_use_by(
        vegetable_name: str,
        freshness: str = "FRESH",
        received_date: datetime.date = None,
        db=None
    ) -> dict:
        """
        Core Calculation Engine:
        Configured Shelf Life x Freshness Multiplier = Effective Remaining Life
        Received Date + Effective Remaining Life = Estimated Use-By Date
        """
        if received_date is None:
            received_date = datetime.date.today()

        settings = FreshnessService.get_settings(db)
        shelf_life = FreshnessService.get_shelf_life_days(vegetable_name, db)
        
        freshness_norm = str(freshness).strip().upper()
        if "SPOIL" in freshness_norm:
            freshness_clean = "SPOILED"
            multiplier = settings["spoiled_multiplier"]
            effective_life = 0
        elif "MED" in freshness_norm or "RIPE" in freshness_norm:
            freshness_clean = "MEDIUM"
            multiplier = settings["medium_multiplier"]
            effective_life = max(1, int(round(shelf_life * multiplier)))
        else:
            freshness_clean = "FRESH"
            multiplier = settings["fresh_multiplier"]
            effective_life = int(round(shelf_life * multiplier))

        estimated_use_by = received_date + datetime.timedelta(days=effective_life)
        
        # Calculate status and alert using settings thresholds
        urgent_days = settings["urgent_threshold_days"]
        use_soon_days = settings["use_soon_threshold_days"]

        if freshness_clean == "SPOILED" or effective_life <= 0:
            status_text = "SPOILED — DO NOT USE"
            priority_level = "Urgent"
            badge_color = "#ef4444"
            alert_msg = f"🚨 {vegetable_name} is classified as spoiled. Do not use."
        elif effective_life <= urgent_days:
            status_text = "URGENT"
            priority_level = "Urgent"
            badge_color = "#f97316"
            alert_msg = f"⚠ {vegetable_name} should be used within 24 hours."
        elif effective_life <= use_soon_days:
            status_text = "USE SOON"
            priority_level = "Use Soon"
            badge_color = "#eab308"
            alert_msg = f"{vegetable_name} is in medium freshness condition. Use within approximately {effective_life} days."
        else:
            status_text = "SAFE / FRESH"
            priority_level = "Normal"
            badge_color = "#10b981"
            alert_msg = f"{vegetable_name} is fresh. Estimated remaining life: {effective_life} days."

        return {
            "vegetable_name": vegetable_name,
            "freshness": freshness_clean,
            "configured_shelf_life": shelf_life,
            "multiplier_used": multiplier,
            "multiplier_pct": int(round(multiplier * 100)),
            "effective_remaining_life": effective_life,
            "received_date": received_date,
            "estimated_use_by_date": estimated_use_by,
            "status": status_text,
            "priority": priority_level,
            "color": badge_color,
            "alert_msg": alert_msg
        }

    # Backward compatibility helper
    @staticmethod
    def calculate_use_by_date(vegetable_name: str, received_date: datetime.date, freshness: str = "Fresh", storage_condition: str = "Room Temperature") -> datetime.date:
        res = FreshnessService.calculate_life_and_use_by(vegetable_name, freshness, received_date)
        return res["estimated_use_by_date"]

    @staticmethod
    def calculate_priority_and_status(estimated_use_by: datetime.date, current_date: datetime.date = None):
        if current_date is None:
            current_date = datetime.date.today()
        
        days_remaining = (estimated_use_by - current_date).days
        settings = FreshnessService.get_settings()
        urgent_days = settings["urgent_threshold_days"]
        use_soon_days = settings["use_soon_threshold_days"]

        if days_remaining < 0:
            return "Urgent", "Expired", days_remaining, "#ef4444"
        elif days_remaining <= urgent_days:
            return "Urgent", "Expiring Soon", days_remaining, "#f97316"
        elif days_remaining <= use_soon_days:
            return "Use Soon", "Use Soon", days_remaining, "#eab308"
        else:
            return "Normal", "Fresh", days_remaining, "#10b981"

    @staticmethod
    def rank_inventory_fifo(inventory_items: list):
        """
        Sort inventory using:
        1. Spoiled / Urgent status first
        2. Lowest remaining life
        3. Earliest estimated use-by date
        4. Freshness level
        """
        today = datetime.date.today()
        def sort_key(item):
            days_rem = (item.estimated_use_by_date - today).days
            fresh_status = str(item.freshness_status).upper()
            
            # Priority rank: 0=Spoiled/Expired, 1=Urgent, 2=Medium, 3=Fresh
            if "SPOIL" in fresh_status or days_rem < 0:
                rank_group = 0
            elif days_rem <= 1:
                rank_group = 1
            elif "MED" in fresh_status or days_rem <= 3:
                rank_group = 2
            else:
                rank_group = 3

            return (rank_group, days_rem, item.estimated_use_by_date, item.received_date)

        return sorted(inventory_items, key=sort_key)
