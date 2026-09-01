"""Carga de configuración YAML."""

from __future__ import annotations

from functools import lru_cache
from typing import Any

import yaml
from dotenv import load_dotenv

from ml.paths import APP_ROOT, CONFIG_PATH

load_dotenv(APP_ROOT / ".env")


@lru_cache(maxsize=1)
def load_settings() -> dict[str, Any]:
    with open(CONFIG_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f)
