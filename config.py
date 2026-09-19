from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent
INSTANCE_DIR = BASE_DIR / "instance"
INSTANCE_DIR.mkdir(parents=True, exist_ok=True)

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key")

    SQLALCHEMY_DATABASE_URI = (
        f"sqlite:///{INSTANCE_DIR / 'microblog.db'}"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False