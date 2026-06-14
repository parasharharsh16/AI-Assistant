import tempfile
from pathlib import Path

import numpy as np

from app.memory import MemoryStore


def test_memory_store_roundtrip():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "memory.db"
        memory = MemoryStore(db_path)

        vector = np.ones((384,), dtype=np.float32)
        memory.add_interaction("user", "Hello Jarvis", embedding=vector)
        memory.add_interaction("assistant", "Hello, how can I help?", embedding=vector)

        recent = memory.get_recent(limit=2)
        assert len(recent) == 2
        assert recent[0]["role"] == "assistant"
        assert recent[1]["role"] == "user"
