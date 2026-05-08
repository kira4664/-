"""SQLite 기반 작업 기록 관리"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional

from config.settings import DB_PATH
from modules.utils import logger


def _get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """DB 테이블 초기화"""
    with _get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS jobs (
                job_id       TEXT PRIMARY KEY,
                topic        TEXT NOT NULL,
                duration     INTEGER,
                tone         TEXT,
                status       TEXT DEFAULT 'pending',
                title        TEXT,
                script_path  TEXT,
                audio_path   TEXT,
                video_path   TEXT,
                thumb_path   TEXT,
                youtube_url  TEXT,
                error_msg    TEXT,
                created_at   TEXT NOT NULL,
                updated_at   TEXT NOT NULL
            )
        """)
        conn.commit()


def create_job(job_id: str, topic: str, duration: int, tone: str) -> dict:
    now = datetime.now().isoformat()
    with _get_conn() as conn:
        conn.execute(
            """INSERT INTO jobs (job_id, topic, duration, tone, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (job_id, topic, duration, tone, now, now),
        )
        conn.commit()
    return get_job(job_id)


def update_job(job_id: str, **kwargs):
    if not kwargs:
        return
    kwargs["updated_at"] = datetime.now().isoformat()
    set_clause = ", ".join(f"{k} = ?" for k in kwargs)
    values = list(kwargs.values()) + [job_id]
    with _get_conn() as conn:
        conn.execute(
            f"UPDATE jobs SET {set_clause} WHERE job_id = ?",
            values,
        )
        conn.commit()


def get_job(job_id: str) -> Optional[dict]:
    with _get_conn() as conn:
        row = conn.execute("SELECT * FROM jobs WHERE job_id = ?", (job_id,)).fetchone()
    return dict(row) if row else None


def list_jobs(limit: int = 50) -> list[dict]:
    with _get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM jobs ORDER BY created_at DESC LIMIT ?", (limit,)
        ).fetchall()
    return [dict(r) for r in rows]


# 앱 시작 시 DB 초기화
init_db()
