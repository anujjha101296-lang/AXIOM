"""Identity — user accounts for MVP multi-user auth."""

from __future__ import annotations

import hashlib
import hmac
import os
import secrets
import sqlite3
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime, timezone


def _utc_now() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def hash_password(password: str, *, salt: bytes | None = None) -> str:
    """PBKDF2-SHA256 password hash. Format: pbkdf2_sha256$iterations$salt_hex$hash_hex."""
    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters")
    iterations = 120_000
    salt = salt or secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    return f"pbkdf2_sha256${iterations}${salt.hex()}${digest.hex()}"


def verify_password(password: str, encoded: str) -> bool:
    try:
        algo, iter_s, salt_hex, hash_hex = encoded.split("$", 3)
        if algo != "pbkdf2_sha256":
            return False
        iterations = int(iter_s)
        salt = bytes.fromhex(salt_hex)
        expected = bytes.fromhex(hash_hex)
        digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
        return hmac.compare_digest(digest, expected)
    except (ValueError, TypeError):
        return False


@dataclass
class User:
    user_id: str
    email: str
    display_name: str
    role: str
    created_at: str
    password_hash: str = ""

    def public_dict(self) -> dict:
        return {
            "user_id": self.user_id,
            "email": self.email,
            "display_name": self.display_name,
            "role": self.role,
            "created_at": self.created_at,
        }


class IdentityStore:
    def __init__(self, db_path: str) -> None:
        self.db_path = db_path
        self._persistent: sqlite3.Connection | None = None
        if db_path == ":memory:":
            self._persistent = sqlite3.connect(":memory:", check_same_thread=False)
            self._persistent.row_factory = sqlite3.Row
        self._ensure_schema()

    def _conn(self) -> sqlite3.Connection:
        if self._persistent is not None:
            return self._persistent
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _release(self, conn: sqlite3.Connection) -> None:
        if conn is not self._persistent:
            conn.close()

    def _ensure_schema(self) -> None:
        conn = self._conn()
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS identity_users (
                user_id TEXT PRIMARY KEY,
                email TEXT NOT NULL UNIQUE COLLATE NOCASE,
                display_name TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'RESEARCHER',
                created_at TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_identity_email ON identity_users(email);
            """
        )
        conn.commit()
        self._release(conn)

    def create_user(
        self,
        email: str,
        password: str,
        *,
        display_name: str = "",
        role: str = "RESEARCHER",
    ) -> User:
        email_n = email.strip().lower()
        if "@" not in email_n or "." not in email_n.split("@")[-1]:
            raise ValueError("Invalid email address")
        if self.get_by_email(email_n):
            raise ValueError("Email already registered")
        user = User(
            user_id=f"usr_{uuid.uuid4().hex[:12]}",
            email=email_n,
            display_name=(display_name or email_n.split("@")[0]).strip()[:80],
            role=role,
            created_at=_utc_now(),
            password_hash=hash_password(password),
        )
        conn = self._conn()
        conn.execute(
            """INSERT INTO identity_users
               (user_id, email, display_name, password_hash, role, created_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (user.user_id, user.email, user.display_name, user.password_hash, user.role, user.created_at),
        )
        conn.commit()
        self._release(conn)
        return user

    def get_by_email(self, email: str) -> User | None:
        conn = self._conn()
        row = conn.execute(
            "SELECT * FROM identity_users WHERE email = ?", (email.strip().lower(),)
        ).fetchone()
        self._release(conn)
        return self._row_to_user(row) if row else None

    def get_by_id(self, user_id: str) -> User | None:
        conn = self._conn()
        row = conn.execute(
            "SELECT * FROM identity_users WHERE user_id = ?", (user_id,)
        ).fetchone()
        self._release(conn)
        return self._row_to_user(row) if row else None

    def authenticate(self, email: str, password: str) -> User | None:
        user = self.get_by_email(email)
        if not user or not verify_password(password, user.password_hash):
            return None
        return user

    @staticmethod
    def _row_to_user(row: sqlite3.Row) -> User:
        return User(
            user_id=row["user_id"],
            email=row["email"],
            display_name=row["display_name"],
            role=row["role"],
            created_at=row["created_at"],
            password_hash=row["password_hash"],
        )


_store_cache: dict[str, IdentityStore] = {}


def get_identity_store(db_path: str | None = None) -> IdentityStore:
    path = db_path or os.environ.get("AXIOM_DB_PATH", "./axiom.db")
    if path not in _store_cache:
        _store_cache[path] = IdentityStore(path)
    return _store_cache[path]
