import pandas as pd
import datetime
from sqlalchemy.orm import joinedload
from database.database import SessionLocal
from database.models import Donation, Inventory, UsageRecord, WasteRecord, Vegetable

class ReportService:
    @staticmethod
    def get_donations_dataframe():
        db = SessionLocal()
        try:
            donations = (
                db.query(Donation)
                .options(joinedload(Donation.vegetable))
                .order_by(Donation.donation_date.desc())
                .all()
            )
            data = []
            for d in donations:
                data.append({
                    "Donation Code": d.donation_code,
                    "Donor Name": d.donor_name,
                    "Donation Date": d.donation_date,
                    "Vegetable": d.vegetable.name if d.vegetable else "Unknown",
                    "Category": d.vegetable.category if d.vegetable else "Other",
                    "Quantity": d.quantity,
                    "Unit": d.unit,
                    "Freshness Status": d.freshness_status,
                    "Storage Condition": d.storage_condition,
                    "Estimated Use-By Date": d.estimated_use_by_date,
                    "Notes": d.notes or ""
                })
            return pd.DataFrame(data)
        finally:
            db.close()

    @staticmethod
    def get_inventory_dataframe():
        db = SessionLocal()
        try:
            today = datetime.date.today()
            items = (
                db.query(Inventory)
                .options(joinedload(Inventory.vegetable))
                .filter(Inventory.status == "In Stock")
                .all()
            )
            data = []
            for i in items:
                days_left = (i.estimated_use_by_date - today).days
                data.append({
                    "Inventory ID": f"INV-{i.id:04d}",
                    "Vegetable": i.vegetable.name if i.vegetable else "Unknown",
                    "Category": i.vegetable.category if i.vegetable else "Other",
                    "Current Qty": i.current_quantity,
                    "Initial Qty": i.initial_quantity,
                    "Unit": i.unit,
                    "Received Date": i.received_date,
                    "Freshness Condition": i.freshness_status,
                    "Estimated Use-By": i.estimated_use_by_date,
                    "Days Remaining": days_left,
                    "Priority": i.priority_level,
                    "Status": i.status
                })
            return pd.DataFrame(data)
        finally:
            db.close()

    @staticmethod
    def get_usage_dataframe():
        db = SessionLocal()
        try:
            records = (
                db.query(UsageRecord)
                .options(joinedload(UsageRecord.vegetable))
                .order_by(UsageRecord.date_used.desc())
                .all()
            )
            data = []
            for r in records:
                data.append({
                    "Usage ID": f"USE-{r.id:04d}",
                    "Date Used": r.date_used,
                    "Vegetable": r.vegetable.name if r.vegetable else "Unknown",
                    "Quantity Used": r.quantity_used,
                    "Unit": r.unit,
                    "Meal Purpose": r.meal_purpose,
                    "Staff Name": r.staff_name,
                    "Notes": r.notes or ""
                })
            return pd.DataFrame(data)
        finally:
            db.close()

    @staticmethod
    def get_waste_dataframe():
        db = SessionLocal()
        try:
            records = (
                db.query(WasteRecord)
                .options(joinedload(WasteRecord.vegetable))
                .order_by(WasteRecord.date_wasted.desc())
                .all()
            )
            data = []
            for r in records:
                data.append({
                    "Waste ID": f"WST-{r.id:04d}",
                    "Date Wasted": r.date_wasted,
                    "Vegetable": r.vegetable.name if r.vegetable else "Unknown",
                    "Quantity Wasted": r.quantity_wasted,
                    "Unit": r.unit,
                    "Reason": r.reason,
                    "Notes": r.notes or ""
                })
            return pd.DataFrame(data)
        finally:
            db.close()
