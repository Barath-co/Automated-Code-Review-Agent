import sqlite3
import json
import os
import logging
from typing import List, Optional, Dict, Any
from ..models.schemas import FinalReviewReport

logger = logging.getLogger(__name__)

# In serverless environments (like Vercel or AWS Lambda), the filesystem is read-only
# except for /tmp. Use /tmp on Vercel to allow SQLite read/write operations without crashes.
_default_db_dir = "/tmp" if os.getenv("VERCEL") or os.getenv("AWS_LAMBDA_FUNCTION_NAME") else os.path.dirname(__file__)
DB_PATH = os.getenv("SQLITE_DB_PATH", os.path.join(_default_db_dir, "reviews.db"))

class ReviewStorage:
    @classmethod
    def init_db(cls):
        try:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS review_tasks (
                        task_id TEXT PRIMARY KEY,
                        created_at TEXT,
                        language TEXT,
                        loc INTEGER,
                        status TEXT,
                        consensus_score REAL,
                        total_tokens INTEGER,
                        cost_inr REAL,
                        latency_ms INTEGER,
                        human_review_required INTEGER,
                        report_json TEXT
                    )
                """)
                conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Failed to initialise database: {e}")

    @classmethod
    def save_report(cls, report: FinalReviewReport) -> bool:
        """Returns True on success, False on failure (does not raise)."""
        cls.init_db()
        try:
            with sqlite3.connect(DB_PATH, timeout=10) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO review_tasks
                    (task_id, created_at, language, loc, status, consensus_score,
                     total_tokens, cost_inr, latency_ms, human_review_required, report_json)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    report.task_id,
                    report.created_at,
                    report.classification.language,
                    report.classification.loc,
                    report.status,
                    report.consensus.consensus_score,
                    report.metrics.total_tokens,
                    report.metrics.estimated_cost_inr,
                    report.metrics.total_latency_ms,
                    1 if report.human_review_required else 0,
                    report.model_dump_json()
                ))
                conn.commit()
                return True
        except sqlite3.Error as e:
            logger.error(f"Failed to save report {report.task_id}: {e}")
            return False

    @classmethod
    def get_recent_tasks(cls, limit: int = 15) -> List[Dict[str, Any]]:
        cls.init_db()
        try:
            with sqlite3.connect(DB_PATH) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT task_id, created_at, language, loc, status, consensus_score,
                           total_tokens, cost_inr, latency_ms, human_review_required
                    FROM review_tasks
                    ORDER BY created_at DESC
                    LIMIT ?
                """, (limit,))
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except sqlite3.Error as e:
            logger.error(f"Failed to fetch review history: {e}")
            return []

    @classmethod
    def get_report_by_id(cls, task_id: str) -> Optional[Dict[str, Any]]:
        cls.init_db()
        try:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT report_json FROM review_tasks WHERE task_id = ?", (task_id,))
                row = cursor.fetchone()
                if row:
                    return json.loads(row[0])
                return None
        except (sqlite3.Error, json.JSONDecodeError) as e:
            logger.error(f"Failed to retrieve report {task_id}: {e}")
            return None

    @classmethod
    def delete_report(cls, task_id: str) -> bool:
        """Delete a specific report by task ID (data retention support)."""
        cls.init_db()
        try:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM review_tasks WHERE task_id = ?", (task_id,))
                conn.commit()
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            logger.error(f"Failed to delete report {task_id}: {e}")
            return False
