from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key")

    SQLALCHEMY_DATABASE_URI = "sqlite:////tmp/microblog.db"

    SQLALCHEMY_TRACK_MODIFICATIONS = False