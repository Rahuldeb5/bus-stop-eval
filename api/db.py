import sqlite3
import os
from contextlib import contextmanager
import json

DB_PATH = os.path.join(os.path.dirname(__file__), "../data/evaluations.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS evaluations (
    id          TEXT PRIMARY KEY,
    lat         REAL,
    lng         REAL,
    snapped_lat REAL,
    snapped_lng REAL,
    city        TEXT,
    state       TEXT,
    country     TEXT,
    score       REAL,
    verdict     TEXT,
    failures    TEXT,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS results (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    eval_id     TEXT REFERENCES evaluations(id),
    criterion   TEXT,
    passed      INTEGER,
    importance  TEXT,
    notes       TEXT
);
"""

@contextmanager
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()

def init_db():
    with get_conn() as conn:
        conn.executescript(SCHEMA)

def save_evaluation(result: dict):
    with get_conn() as conn:
        conn.execute("""
            INSERT OR REPLACE INTO evaluations
            (id, lat, lng, snapped_lat, snapped_lng, city, state, country, score, verdict, failures)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            result["job_id"],
            result["lat"],
            result["lng"],
            result["snapped_lat"],
            result["snapped_lng"],
            result.get("city"),
            result.get("state"),
            result.get("country"),
            result.get("score"),
            result.get("verdict"),
            json.dumps(result.get("failures", {})),
        ))
        conn.executemany("""
            INSERT INTO results (eval_id, criterion, passed, importance, notes)
            VALUES (?, ?, ?, ?, ?)
        """, [
            (result["job_id"], r.criterion, r.passed,
             r.importance.value if r.importance else None, r.notes)
            for r in result["results"]
        ])

def get_evaluation(job_id: str) -> dict | None:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM evaluations WHERE id = ?", (job_id,)
        ).fetchone()
        if not row:
            return None
        results = conn.execute(
            "SELECT * FROM results WHERE eval_id = ?", (job_id,)
        ).fetchall()
        
        row_dict = dict(row)
        row_dict["failures"] = json.loads(row_dict.get("failures") or "{}")
        return {**row_dict, "results": [dict(r) for r in results]}

def get_evaluations(limit: int = 50) -> list[dict]:
    """Return recent evaluations for the history page, no results rows needed."""
    with get_conn() as conn:
        rows = conn.execute("""
            SELECT id, city, state, country, snapped_lat, snapped_lng,
                   score, verdict, created_at
            FROM evaluations
            ORDER BY created_at DESC
            LIMIT ?
        """, (limit,)).fetchall()
        return [dict(r) for r in rows]
