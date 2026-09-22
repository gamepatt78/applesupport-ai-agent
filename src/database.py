"""PostgreSQL persistence with SQLite fallback for local development."""

from __future__ import annotations

import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

DATABASE_PATH = Path(__file__).parent.parent / "data" / "support.db"
DATABASE_URL = os.getenv("DATABASE_URL")


@contextmanager
def get_connection() -> Iterator[Any]:
    if DATABASE_URL:
        import psycopg

        connection = psycopg.connect(DATABASE_URL)
        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()
    else:
        DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(DATABASE_PATH)
        connection.row_factory = sqlite3.Row
        try:
            yield connection
            connection.commit()
        finally:
            connection.close()


def _placeholder() -> str:
    return "%s" if DATABASE_URL else "?"


def initialize_database() -> None:
    identity = "GENERATED ALWAYS AS IDENTITY" if DATABASE_URL else "AUTOINCREMENT"
    boolean_type = "BOOLEAN" if DATABASE_URL else "INTEGER"
    with get_connection() as connection:
        connection.execute(
            f"""
            CREATE TABLE IF NOT EXISTS support_interactions (
                id INTEGER PRIMARY KEY {identity},
                customer_message TEXT NOT NULL,
                intent TEXT NOT NULL,
                escalated {boolean_type} NOT NULL,
                escalation_reason TEXT NOT NULL,
                draft_reply TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        if DATABASE_URL:
            connection.execute("ALTER TABLE support_interactions ADD COLUMN IF NOT EXISTS draft_reply TEXT NOT NULL DEFAULT ''")
            connection.execute("ALTER TABLE support_interactions ADD COLUMN IF NOT EXISTS created_at TEXT NOT NULL DEFAULT ''")
        else:
            existing_columns = {row[1] for row in connection.execute("PRAGMA table_info(support_interactions)").fetchall()}
            if "draft_reply" not in existing_columns:
                connection.execute("ALTER TABLE support_interactions ADD COLUMN draft_reply TEXT NOT NULL DEFAULT ''")
            if "created_at" not in existing_columns:
                connection.execute("ALTER TABLE support_interactions ADD COLUMN created_at TEXT NOT NULL DEFAULT ''")


def _rows(cursor: Any) -> list[dict]:
    if DATABASE_URL:
        columns = [column.name for column in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
    return [dict(row) for row in cursor.fetchall()]


def save_interaction(
    customer_message: str,
    intent: str,
    escalated: bool,
    escalation_reason: str,
    draft_reply: str,
) -> int:
    placeholder = _placeholder()
    with get_connection() as connection:
        cursor = connection.execute(
            f"""
            INSERT INTO support_interactions
                (customer_message, intent, escalated, escalation_reason, draft_reply, created_at)
            VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
            {"RETURNING id" if DATABASE_URL else ""}
            """,
            (customer_message, intent, escalated, escalation_reason, draft_reply, datetime.now(timezone.utc).isoformat()),
        )
        if DATABASE_URL:
            return int(cursor.fetchone()[0])
        return int(cursor.lastrowid)


def update_interaction(
    interaction_id: int,
    intent: str,
    escalated: bool,
    escalation_reason: str,
    draft_reply: str,
) -> None:
    placeholder = _placeholder()
    with get_connection() as connection:
        connection.execute(
            f"""UPDATE support_interactions
            SET intent = {placeholder}, escalated = {placeholder},
                escalation_reason = {placeholder}, draft_reply = {placeholder}
            WHERE id = {placeholder}""",
            (intent, escalated, escalation_reason, draft_reply, interaction_id),
        )


def list_interactions(limit: int = 50) -> list[dict]:
    bounded_limit = max(1, min(int(limit), 200))
    with get_connection() as connection:
        if DATABASE_URL:
            column_cursor = connection.execute(
                "SELECT column_name FROM information_schema.columns WHERE table_name = %s",
                ("support_interactions",),
            )
            columns = {row[0] for row in column_cursor.fetchall()}
            selected = [
                column if column in columns else "'' AS " + column
                for column in [
                    "id",
                    "customer_message",
                    "intent",
                    "escalated",
                    "escalation_reason",
                    "draft_reply",
                    "created_at",
                ]
            ]
            cursor = connection.execute(
                f"SELECT {', '.join(selected)} FROM support_interactions ORDER BY id DESC LIMIT %s",
                (bounded_limit,),
            )
        else:
            cursor = connection.execute(
                """SELECT id, customer_message, intent, escalated, escalation_reason, draft_reply, created_at
                FROM support_interactions ORDER BY id DESC LIMIT ?""",
                (bounded_limit,),
            )
        return _rows(cursor)


def list_escalations(limit: int = 20) -> list[dict]:
    bounded_limit = max(1, min(int(limit), 100))
    with get_connection() as connection:
        cursor = connection.execute(
            f"""SELECT id, customer_message, intent, escalation_reason, created_at
            FROM support_interactions WHERE escalated = {"TRUE" if DATABASE_URL else "1"}
            ORDER BY id DESC LIMIT {_placeholder()}""",
            (bounded_limit,),
        )
        return _rows(cursor)


def get_metrics() -> dict:
    today = datetime.now(timezone.utc).date().isoformat()
    placeholder = _placeholder()
    date_expression = f"DATE(created_at) = DATE({placeholder})"
    with get_connection() as connection:
        cursor = connection.execute(
            f"""SELECT COUNT(*) AS total,
            COALESCE(SUM(CASE WHEN escalated = {"TRUE" if DATABASE_URL else "1"} THEN 1 ELSE 0 END), 0) AS escalated
            FROM support_interactions WHERE {date_expression}""",
            (today,),
        )
        row = _rows(cursor)[0]
    total = int(row["total"])
    escalated = int(row["escalated"])
    return {
        "handled_today": total,
        "escalated_today": escalated,
        "escalation_rate": round((escalated / total) * 100, 1) if total else 0,
        "baseline_confidence": 87,
        "database": "postgresql" if DATABASE_URL else "sqlite",
    }


initialize_database()
