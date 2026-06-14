import sqlite3
import numpy as np
from pathlib import Path
from typing import Optional

from .config import settings


def _to_blob(vector: np.ndarray) -> bytes:
    return vector.astype(np.float32).tobytes()


def _from_blob(blob: bytes) -> np.ndarray:
    return np.frombuffer(blob, dtype=np.float32)


class MemoryStore:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.db_path)
        self._create_tables()

    def _create_tables(self):
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                embedding BLOB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        self.conn.commit()

    def add_interaction(self, role: str, content: str, embedding: Optional[np.ndarray] = None):
        blob = _to_blob(embedding) if embedding is not None else None
        self.conn.execute(
            "INSERT INTO memory (role, content, embedding) VALUES (?, ?, ?)",
            (role, content, blob),
        )
        self.conn.commit()

    def get_recent(self, limit: int = 10) -> list[dict[str, str]]:
        rows = self.conn.execute(
            "SELECT role, content FROM memory ORDER BY created_at DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return [{"role": role, "content": content} for role, content in rows]

    def retrieve_relevant(self, query_embedding: np.ndarray, limit: int = 5) -> list[dict[str, str]]:
        rows = self.conn.execute(
            "SELECT id, role, content, embedding FROM memory WHERE embedding IS NOT NULL").fetchall()
        documents = []
        embeddings = []
        for row in rows:
            vector = _from_blob(row[3])
            documents.append({"role": row[1], "content": row[2]})
            embeddings.append(vector)

        if not embeddings:
            return []

        matrix = np.vstack(embeddings)
        query = query_embedding.reshape(1, -1)
        similarities = (matrix @ query.T).squeeze()
        top_indices = np.argsort(-similarities)[:limit]
        return [documents[idx] for idx in top_indices if similarities[idx] > 0.0]

    def prune(self, max_items: int = 200):
        count = self.conn.execute("SELECT COUNT(*) FROM memory").fetchone()[0]
        if count <= max_items:
            return
        to_delete = count - max_items
        self.conn.execute(
            "DELETE FROM memory WHERE id IN (SELECT id FROM memory ORDER BY created_at ASC LIMIT ?)",
            (to_delete,),
        )
        self.conn.commit()
