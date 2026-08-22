import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = os.path.join(BASE_DIR, "financas.db")
DATABASE_URL = f"sqlite:///{DB_PATH}"
