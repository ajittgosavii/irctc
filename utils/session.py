"""
Session & persistence utilities.
Uses st.session_state for per-session data + SQLite for cross-session history.
"""

import sqlite3
import json
import os
import uuid
import hashlib
import streamlit as st
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "railways.db")


def ensure_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL,
            api_key TEXT DEFAULT ''
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS search_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            search_type TEXT NOT NULL,
            query TEXT NOT NULL,
            searched_at TEXT NOT NULL
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS favourites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            item_type TEXT NOT NULL,
            item_data TEXT NOT NULL,
            added_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def hash_password(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()


def register_user(username: str, password: str) -> tuple[bool, str]:
    ensure_db()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        uid = str(uuid.uuid4())
        c.execute(
            "INSERT INTO users (user_id, username, password_hash, created_at) VALUES (?,?,?,?)",
            (uid, username.strip(), hash_password(password), datetime.now().isoformat()),
        )
        conn.commit()
        return True, uid
    except sqlite3.IntegrityError:
        return False, "Username already exists."
    finally:
        conn.close()


def login_user(username: str, password: str) -> tuple[bool, dict]:
    ensure_db()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "SELECT user_id, username, api_key FROM users WHERE username=? AND password_hash=?",
        (username.strip(), hash_password(password)),
    )
    row = c.fetchone()
    conn.close()
    if row:
        return True, {"user_id": row[0], "username": row[1], "api_key": row[2] or ""}
    return False, {}


def save_api_key(user_id: str, api_key: str):
    ensure_db()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE users SET api_key=? WHERE user_id=?", (api_key, user_id))
    conn.commit()
    conn.close()


def log_search(user_id: str, search_type: str, query: str):
    ensure_db()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT INTO search_history (user_id, search_type, query, searched_at) VALUES (?,?,?,?)",
        (user_id, search_type, query, datetime.now().isoformat()),
    )
    conn.commit()
    conn.close()


def get_search_history(user_id: str, limit: int = 20) -> list:
    ensure_db()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "SELECT search_type, query, searched_at FROM search_history WHERE user_id=? ORDER BY searched_at DESC LIMIT ?",
        (user_id, limit),
    )
    rows = c.fetchall()
    conn.close()
    return [{"type": r[0], "query": r[1], "at": r[2]} for r in rows]


def add_favourite(user_id: str, item_type: str, item_data: dict):
    ensure_db()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT INTO favourites (user_id, item_type, item_data, added_at) VALUES (?,?,?,?)",
        (user_id, item_type, json.dumps(item_data), datetime.now().isoformat()),
    )
    conn.commit()
    conn.close()


def get_favourites(user_id: str) -> list:
    ensure_db()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "SELECT id, item_type, item_data, added_at FROM favourites WHERE user_id=? ORDER BY added_at DESC",
        (user_id,),
    )
    rows = c.fetchall()
    conn.close()
    return [{"id": r[0], "type": r[1], "data": json.loads(r[2]), "at": r[3]} for r in rows]


def remove_favourite(fav_id: int):
    ensure_db()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM favourites WHERE id=?", (fav_id,))
    conn.commit()
    conn.close()


# ── Session state helpers ──────────────────────────────────────
def init_session():
    defaults = {
        "logged_in": False,
        "user_id": None,
        "username": None,
        "rapidapi_key": "",
        "active_page": "Home",
        "search_results": None,
        "from_station": {"code": "", "name": ""},
        "to_station": {"code": "", "name": ""},
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def is_logged_in() -> bool:
    return st.session_state.get("logged_in", False)


def logout():
    for key in ["logged_in", "user_id", "username", "rapidapi_key"]:
        st.session_state[key] = None if key != "logged_in" else False
    st.rerun()
