"""SQLite persistence for AppleSupport interactions."""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path


DATABASE_PATH = Path(__file__).parent.parent / "data" / "support.db"


def get_connection() -> sqlite3.Connection:
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database() -> None:
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS support_interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_message TEXT NOT NULL,
                intent TEXT NOT NULL,
                escalated INTEGER NOT NULL CHECK (escalated IN (0, 1)),
                escalation_reason TEXT NOT NULL,
                draft_reply TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        connection.commit()


def save_interaction(
    customer_message: str,
    intent: str,
    escalated: bool,
    escalation_reason: str,
    draft_reply: str,
) -> int:
    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO support_interactions
                (customer_message, intent, escalated, escalation_reason, draft_reply, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                customer_message,
                intent,
                int(escalated),
                escalation_reason,
                draft_reply,
                datetime.now(timezone.utc).isoformat(),
            ),
        )
        connection.commit()
        return int(cursor.lastrowid)


def list_interactions(limit: int = 50) -> list[dict]:
    bounded_limit = max(1, min(int(limit), 200))
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT id, customer_message, intent, escalated,
                   escalation_reason, draft_reply, created_at
            FROM support_interactions
            ORDER BY id DESC
            LIMIT ?
            """,
            (bounded_limit,),
        ).fetchall()
    return [dict(row) for row in rows]


initialize_database()
