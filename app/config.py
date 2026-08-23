import os
import secrets
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = Path(os.environ.get("FINANCAS_DATA_DIR", BASE_DIR))
DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = os.path.join(DATA_DIR, "financas.db")
DATABASE_URL = f"sqlite:///{DB_PATH}"

# --- Authentication / JWT settings ---
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 dias

def _load_or_create_secret_key() -> str:
    """Read the JWT signing secret from the FINANCAS_SECRET_KEY env var if set.
    Otherwise, persist a randomly generated secret in a local file so tokens
    remain valid across app restarts on this machine."""
    env_secret = os.environ.get("FINANCAS_SECRET_KEY")
    if env_secret:
        return env_secret

    secret_file = DATA_DIR / ".secret_key"
    if secret_file.exists():
        return secret_file.read_text().strip()

    generated = secrets.token_hex(32)
    secret_file.write_text(generated)
    return generated

SECRET_KEY = _load_or_create_secret_key()
