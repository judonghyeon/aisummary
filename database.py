import os

DATABASE_URL = os.getenv("DATABASE_URL", "")

# Railway는 PostgreSQL, 로컬은 SQLite
if DATABASE_URL:
    import psycopg2
    from psycopg2.extras import RealDictCursor

    def get_db():
        conn = psycopg2.connect(DATABASE_URL)
        return conn

    def query(conn, sql, params=None):
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute(sql, params or ())
        return cur

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

else:
    import sqlite3

    DB_PATH = "app.db"

    def get_db():
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn

    def query(conn, sql, params=None):
        # SQLite는 %s 대신 ? 사용
        sql = sql.replace("%s", "?")
        cur = conn.cursor()
        cur.execute(sql, params or ())
        return cur

    def init_db():
        conn = get_db()
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS tasks (
                id             TEXT PRIMARY KEY,
                status         TEXT NOT NULL DEFAULT 'PENDING',
                progress       TEXT,
                video_url      TEXT,
                summary_length TEXT DEFAULT 'normal',
                estimated_time TEXT,
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
