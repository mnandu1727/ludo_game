import sqlite3
from database.db import get_connection
from database.auth.utils import hash_password, verify_password

def signup(username: str, password: str) -> tuple[bool, str]:
    if not username.strip() or not password.strip():
        return False, "Fields cannot be blank."
    
    hashed = hash_password(password)
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, hashed))
            conn.commit()
            return True, "Signup successful! You can now log in."
    except sqlite3.IntegrityError:
        return False, "Username already exists."

def login(username: str, password: str) -> tuple[bool, dict | str]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        
        if user and verify_password(password, user["password_hash"]):
            return True, dict(user)
        return False, "Invalid username or password."