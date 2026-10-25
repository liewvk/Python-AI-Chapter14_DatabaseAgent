"""Chapter 14 configuration."""
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent
DATABASE_FILE = PROJECT_DIR / "data" / "inventory.db"
OLLAMA_HOST = "http://localhost:11434"
MODEL_NAME = "qwen3.5:9b"  # Use "qwen3.5:4b" on smaller computers.
