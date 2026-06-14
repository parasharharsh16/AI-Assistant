from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_name: str = "google/flan-t5-small"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    memory_db: Path = Path("data/memory.db")
    max_memory_items: int = 200
    top_memory: int = 5
    api_host: str = "127.0.0.1"
    api_port: int = 8000
    assistant_name: str = "Jarvis"

    class Config:
        env_file = ".env"


settings = Settings()
