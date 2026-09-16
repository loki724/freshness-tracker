import datetime
from sqlalchemy import Column, Integer, Float, String, Text, Boolean, DateTime, ForeignKey, Date
from sqlalchemy.orm import relationship
from database.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, index=True, nullable=False)
    phone = Column(String(20), nullable=True)
    password_hash = Column(String(255), nullable=False)
    salt = Column(String(64), nullable=False)
    role = Column(String(50), default="Kitchen Staff")  # Kitchen Staff, Volunteer, Admin
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    donations = relationship("Donation", back_populates="created_by_user")
    scans = relationship("ScanResult", back_populates="user")

class Vegetable(Base):
    __tablename__ = "vegetables"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    category = Column(String(50), default="Other")  # Leafy vegetables, Root vegetables, Fruit vegetables, Tubers, Other
    default_shelf_life_days = Column(Integer, default=7)
    description = Column(Text, nullable=True)
    storage_recommendation = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    donations = relationship("Donation", back_populates="vegetable")
    inventory_items = relationship("Inventory", back_populates="vegetable")

class Donation(Base):
    __tablename__ = "donations"

    id = Column(Integer, primary_key=True, index=True)
    donation_code = Column(String(50), unique=True, nullable=False, index=True)
    donor_name = Column(String(150), nullable=False, default="Anonymous Citizen")
    donation_date = Column(Date, default=datetime.date.today, nullable=False)
    vegetable_id = Column(Integer, ForeignKey("vegetables.id"), nullable=False)
    quantity = Column(Float, nullable=False)
    unit = Column(String(20), default="kg")
    freshness_status = Column(String(30), default="Fresh")  # Fresh, Medium, Spoiled
    storage_condition = Column(String(50), default="Room Temperature")  # Room Temperature, Refrigerated, Cool & Dark
    configured_shelf_life_used = Column(Integer, nullable=True, default=7)
    multiplier_used = Column(Float, nullable=True, default=1.0)
    effective_life_days = Column(Integer, nullable=True, default=7)
    alert_status = Column(String(50), nullable=True, default="SAFE / FRESH")
    estimated_use_by_date = Column(Date, nullable=False)
    notes = Column(Text, nullable=True)
    created_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    vegetable = relationship("Vegetable", back_populates="donations", lazy="joined")
    created_by_user = relationship("User", back_populates="donations")
    inventory_item = relationship("Inventory", back_populates="donation", uselist=False, cascade="all, delete-orphan")

class Inventory(Base):
    __tablename__ = "inventory"

    id = Column(Integer, primary_key=True, index=True)
    donation_id = Column(Integer, ForeignKey("donations.id"), nullable=False)
    vegetable_id = Column(Integer, ForeignKey("vegetables.id"), nullable=False)
    initial_quantity = Column(Float, nullable=False)
    current_quantity = Column(Float, nullable=False)
    unit = Column(String(20), default="kg")
    received_date = Column(Date, nullable=False)
    freshness_status = Column(String(30), default="Fresh")  # Fresh, Medium, Spoiled
    configured_shelf_life_used = Column(Integer, nullable=True, default=7)
    multiplier_used = Column(Float, nullable=True, default=1.0)
    effective_life_days = Column(Integer, nullable=True, default=7)
    alert_status = Column(String(50), nullable=True, default="SAFE / FRESH")
    estimated_use_by_date = Column(Date, nullable=False)
    priority_level = Column(String(20), default="Normal")  # Urgent, Use Soon, Normal
    status = Column(String(30), default="In Stock")  # In Stock, Depleted, Discarded
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    donation = relationship("Donation", back_populates="inventory_item")
    vegetable = relationship("Vegetable", back_populates="inventory_items", lazy="joined")
    usage_records = relationship("UsageRecord", back_populates="inventory_item", cascade="all, delete-orphan")
    waste_records = relationship("WasteRecord", back_populates="inventory_item", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="inventory_item", cascade="all, delete-orphan")

class UsageRecord(Base):
    __tablename__ = "usage_records"

    id = Column(Integer, primary_key=True, index=True)
    inventory_id = Column(Integer, ForeignKey("inventory.id"), nullable=False)
    vegetable_id = Column(Integer, ForeignKey("vegetables.id"), nullable=False)
    quantity_used = Column(Float, nullable=False)
    unit = Column(String(20), default="kg")
    date_used = Column(Date, default=datetime.date.today, nullable=False)
    meal_purpose = Column(String(100), default="Lunch for Children")
    staff_name = Column(String(100), default="Kitchen Staff")
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    inventory_item = relationship("Inventory", back_populates="usage_records")
    vegetable = relationship("Vegetable", lazy="joined")

class WasteRecord(Base):
    __tablename__ = "waste_records"

    id = Column(Integer, primary_key=True, index=True)
    inventory_id = Column(Integer, ForeignKey("inventory.id"), nullable=False)
    vegetable_id = Column(Integer, ForeignKey("vegetables.id"), nullable=False)
    quantity_wasted = Column(Float, nullable=False)
    unit = Column(String(20), default="kg")
    date_wasted = Column(Date, default=datetime.date.today, nullable=False)
    reason = Column(String(50), default="Spoiled")  # Spoiled, Overripe, Damaged, Excess, Other
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    inventory_item = relationship("Inventory", back_populates="waste_records")
    vegetable = relationship("Vegetable", lazy="joined")

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    inventory_id = Column(Integer, ForeignKey("inventory.id"), nullable=False)
    alert_type = Column(String(30), nullable=False)  # EXPIRED, EXPIRING_SOON, USE_SOON
    message = Column(Text, nullable=False)
    severity = Column(String(20), default="WARNING")  # CRITICAL, WARNING, INFO
    is_viewed = Column(Boolean, default=False)
    is_resolved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    inventory_item = relationship("Inventory", back_populates="alerts")

class ScanResult(Base):
    __tablename__ = "scan_results"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    image_path = Column(String(255), nullable=False)
    annotated_image_path = Column(String(255), nullable=True)
    detected_vegetables_json = Column(Text, nullable=False)
    confidence_scores_json = Column(Text, nullable=True)
    freshness_estimate = Column(String(50), default="Fresh")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="scans")

class SystemSetting(Base):
    __tablename__ = "system_settings"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), unique=True, nullable=False)
    value = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
