"""
VeristasOS — SQLite Conversation Memory Service
Provides persistent, sliding-window conversation history management.
"""

import os
import sqlite3
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
DB_PATH = DATA_DIR / "conversations.db"


class MemoryService:
    """SQLite-backed conversation history store."""

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        """Ensure conversation messages table exists."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversation_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id TEXT NOT NULL,
                    user_name TEXT NOT NULL DEFAULT 'User',
                    role TEXT NOT NULL,
                    message TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_conv_id 
                ON conversation_messages(conversation_id)
            """)
            conn.commit()

    def generate_conversation_id(self) -> str:
        """Create a new unique conversation session ID."""
        return f"conv_{uuid.uuid4().hex[:12]}"

    def save_message(
        self,
        conversation_id: str,
        role: str,
        message: str,
        user_name: str = "User",
    ) -> bool:
        """Persist a message turn in conversation memory."""
        if not conversation_id or not message:
            return False

        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO conversation_messages (conversation_id, user_name, role, message, timestamp)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (conversation_id, user_name, role, message, datetime.utcnow().isoformat()),
                )
                conn.commit()
                return True
        except Exception:
            return False

    def get_recent_history(
        self,
        conversation_id: str,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """Retrieve recent conversation turns up to sliding window limit."""
        if not conversation_id:
            return []

        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT role, message, user_name, timestamp 
                    FROM conversation_messages
                    WHERE conversation_id = ?
                    ORDER BY id DESC
                    LIMIT ?
                    """,
                    (conversation_id, limit),
                )
                rows = cursor.fetchall()
                history = [
                    {
                        "role": row["role"],
                        "message": row["message"],
                        "user_name": row["user_name"],
                        "timestamp": row["timestamp"],
                    }
                    for row in reversed(rows)
                ]
                return history
        except Exception:
            return []

    def clear_conversation(self, conversation_id: str) -> bool:
        """Delete all message turns for a conversation session."""
        if not conversation_id:
            return False

        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "DELETE FROM conversation_messages WHERE conversation_id = ?",
                    (conversation_id,),
                )
                conn.commit()
                return True
        except Exception:
            return False

    def list_conversations(self, user_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """List distinct active conversations with latest message timestamp."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                if user_name:
                    cursor.execute(
                        """
                        SELECT conversation_id, MAX(timestamp) as last_updated, COUNT(*) as message_count
                        FROM conversation_messages
                        WHERE user_name = ?
                        GROUP BY conversation_id
                        ORDER BY last_updated DESC
                        """,
                        (user_name,),
                    )
                else:
                    cursor.execute(
                        """
                        SELECT conversation_id, MAX(timestamp) as last_updated, COUNT(*) as message_count
                        FROM conversation_messages
                        GROUP BY conversation_id
                        ORDER BY last_updated DESC
                        """
                    )
                rows = cursor.fetchall()
                return [
                    {
                        "conversation_id": row["conversation_id"],
                        "last_updated": row["last_updated"],
                        "message_count": row["message_count"],
                    }
                    for row in rows
                ]
        except Exception:
            return []


memory_service_instance = MemoryService()
