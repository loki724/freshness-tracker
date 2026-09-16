import random
import pytest
from database.database import init_db
from auth.password import generate_salt, hash_password, verify_password
from auth.authentication import validate_email, register_user, authenticate_user

def test_password_hashing():
    salt = generate_salt()
    pwd = "secretpassword123"
    hashed = hash_password(pwd, salt)
    assert verify_password(pwd, hashed, salt) is True
    assert verify_password("wrongpassword", hashed, salt) is False

def test_email_validation():
    assert validate_email("staff@nourishai.org") is True
    assert validate_email("invalid-email") is False
    assert validate_email("user@domain") is False

def test_user_registration_and_login():
    init_db()
    rand_id = random.randint(10000, 99999)
    email = f"test_staff_{rand_id}@nourishai.org"
    ok, msg = register_user("Test Staff", email, "+91 99999 88888", "testpass123", "testpass123", "Kitchen Staff")
    assert ok is True, f"Registration failed with: {msg}"

    # Duplicate registration should fail
    ok_dup, msg_dup = register_user("Test Staff 2", email, "+91 99999 88888", "testpass123", "testpass123")
    assert ok_dup is False

    # Login
    user, login_msg = authenticate_user(email, "testpass123")
    assert user is not None
    assert user["email"] == email

    # Bad login
    bad_user, _ = authenticate_user(email, "wrongpass")
    assert bad_user is None
