# database.py
import sqlite3
import os

DB_PATH = "app.db"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row   # dict처럼 컬럼명으로 접근 가능
    return conn

def init_db():
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS tasks (
            id             TEXT PRIMARY KEY,
            status         TEXT NOT NULL DEFAULT 'PENDING',
            progress       TEXT,
            video_url      TEXT,
            summary_length TEXT DEFAULT 'normal',
            estimated_time TEXT
            summary_length TEXT DEFAULT 'normal',  -- 추가
            created_at     DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at     DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS results (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id       TEXT NOT NULL REFERENCES tasks(id),
            video_url     TEXT,
            video_title   TEXT,
            thumbnail_url TEXT,
            duration      INTEGER,
            full_script   TEXT,
            summary       TEXT,
            chapters      TEXT,
            keywords      TEXT,
            pdf_path      TEXT,
            created_at    DATETIME DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    conn.close()
