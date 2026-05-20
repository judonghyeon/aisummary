import os
import psycopg2
from psycopg2.extras import RealDictCursor

DATABASE_URL = os.getenv("DATABASE_URL", "")

def get_db():
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    return conn

def init_db():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id             TEXT PRIMARY KEY,
            status         TEXT NOT NULL DEFAULT 'PENDING',
            progress       TEXT,
            video_url      TEXT,
            summary_length TEXT DEFAULT 'normal',
            estimated_time TEXT,
            created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS results (
            id            SERIAL PRIMARY KEY,
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
            created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    cur.close()
    conn.close()
