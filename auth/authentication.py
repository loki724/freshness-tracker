import re
import streamlit as st
from database.database import SessionLocal
from database.models import User
from auth.password import generate_salt, hash_password, verify_password

def validate_email(email: str) -> bool:
    pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return bool(re.match(pattern, email.strip()))

def register_user(full_name: str, email: str, phone: str, password: str, confirm_password: str, role: str = "Kitchen Staff"):
    if not full_name or not email or not password:
        return False, "All required fields must be filled."
    if not validate_email(email):
        return False, "Invalid email address format."
    if password != confirm_password:
        return False, "Passwords do not match."
    if len(password) < 6:
        return False, "Password must be at least 6 characters long."

    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.email == email.strip().lower()).first()
        if existing:
            return False, "An account with this email already exists."

        salt = generate_salt()
        pwd_hash = hash_password(password, salt)
        new_user = User(
            full_name=full_name.strip(),
            email=email.strip().lower(),
            phone=phone.strip() if phone else "",
            password_hash=pwd_hash,
            salt=salt,
            role=role
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return True, "Registration successful! You can now log in."
    except Exception as e:
        db.rollback()
        return False, f"Registration failed: {str(e)}"
    finally:
        db.close()

def authenticate_user(email: str, password: str):
    if not email or not password:
        return None, "Please provide both email and password."

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email.strip().lower()).first()
        if not user:
            return None, "Invalid email or password."
        
        if verify_password(password, user.password_hash, user.salt):
            user_data = {
                "id": user.id,
                "full_name": user.full_name,
                "email": user.email,
                "phone": user.phone,
                "role": user.role
            }
            return user_data, "Login successful!"
        return None, "Invalid email or password."
    finally:
        db.close()

def is_logged_in() -> bool:
    return "user" in st.session_state and st.session_state.user is not None

def get_current_user():
    return st.session_state.get("user", None)

def login_user(user_data):
    st.session_state.user = user_data

def logout_user():
    st.session_state.user = None
    if "current_page" in st.session_state:
        st.session_state.current_page = "Dashboard"
