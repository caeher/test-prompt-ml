"""Rutas centralizadas del backend."""

from pathlib import Path

APP_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = APP_ROOT / "config" / "settings.yaml"
MODELS_DIR = APP_ROOT / "models"
METRICS_DIR = APP_ROOT / "metrics"

MODELS_DIR.mkdir(parents=True, exist_ok=True)
METRICS_DIR.mkdir(parents=True, exist_ok=True)
