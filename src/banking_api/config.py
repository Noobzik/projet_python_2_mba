from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import os

@dataclass(frozen=True)
class Settings:
    app_env: str
    download_dir: Path

def get_settings() -> Settings:
    """
    Configuration de l'application.
    """
    app_env = os.getenv("APP_ENV", "dev").strip().lower()
    
    # Dossier caché pour éviter de polluer le projet
    default_dir = Path.cwd() / "kaggle_cache"
    download_dir = Path(os.getenv("KAGGLE_CACHE_DIR", str(default_dir)))
    
    return Settings(app_env=app_env, download_dir=download_dir)