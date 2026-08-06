"""SQLite-backed user accounts for MVP authentication."""

from __future__ import annotations

import hashlib
import hmac
import os
import re
import secrets
import sqlite3
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

from axiom.observability.logger import get_logger

logger = get_logger(__name__)

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_PBKDF2_ITERATIONS = 120_000


@dataclass
class User:
    id: str
    email: str
    name: str
    role: str
    created_at: str


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _hash_password(password: str, salt: Optional[bytes] = None) -> str:
    salt = salt or os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, _PBKDF2_ITERATIONS)
    return f"{salt.hex()}${digest.hex()}"


def _verify_password(password: str, stored: str) -> bool:
    try:
        salt_hex, digest_hex = stored.split("$", 1)
        salt = bytes.fromhex(salt_hex)
        expected = bytes.fromhex(digest_hex)
        actual = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, _PBKDF2_ITERATIONS)
        return hmac.compare_digest(actual, expected)
    except (ValueError, TypeError):
        return False


def ensure_user_schema(conn: sqlite3.Connection) -> None:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id            TEXT PRIMARY KEY,
            email         TEXT NOT NULL UNIQUE COLLATE NOCASE,
            name          TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            role          TEXT NOT NULL DEFAULT 'RESEARCHER',
            created_at    TEXT NOT NULL
        );
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);")
    conn.commit()


class UserStore:
    """Minimal user persistence for register/login."""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        ensure_user_schema(self.conn)

    def close(self) -> None:
        if self.conn:
            self.conn.close()

    def _row_to_user(self, row: sqlite3.Row) -> User:
        return User(
            id=row["id"],
            email=row["email"],
            name=row["name"],
            role=row["role"],
            created_at=row["created_at"],
        )

    def register(self, email: str, password: str, name: str) -> User:
        email = email.strip().lower()
        name = name.strip()
        if not _EMAIL_RE.match(email):
            raise ValueError("Invalid email address")
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not name:
            raise ValueError("Name is required")

        existing = self.conn.execute(
            "SELECT id FROM users WHERE email = ?", (email,)
        ).fetchone()
        if existing:
            raise ValueError("An account with this email already exists")

        user_id = str(uuid.uuid4())
        now = _utc_now()
        self.conn.execute(
            """
            INSERT INTO users (id, email, name, password_hash, role, created_at)
            VALUES (?, ?, ?, ?, 'RESEARCHER', ?)
            """,
            (user_id, email, name, _hash_password(password), now),
        )
        self.conn.commit()
        logger.info("User registered", extra={"user_id": user_id, "email": email})
        return self.get_by_id(user_id)

    def authenticate(self, email: str, password: str) -> User:
        email = email.strip().lower()
        row = self.conn.execute(
            "SELECT * FROM users WHERE email = ?", (email,)
        ).fetchone()
        if not row or not _verify_password(password, row["password_hash"]):
            raise ValueError("Invalid email or password")
        return self._row_to_user(row)

    def get_by_id(self, user_id: str) -> User:
        row = self.conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        if not row:
            raise KeyError(user_id)
        return self._row_to_user(row)

    def get_by_email(self, email: str) -> Optional[User]:
        row = self.conn.execute(
            "SELECT * FROM users WHERE email = ?", (email.strip().lower(),)
        ).fetchone()
        return self._row_to_user(row) if row else None
