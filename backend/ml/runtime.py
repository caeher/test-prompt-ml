"""Predictor en memoria para serving (API, LIME)."""

from __future__ import annotations

import os
from pathlib import Path

import numpy as np
import torch
from huggingface_hub import snapshot_download
from transformers import AutoModelForSequenceClassification, AutoTokenizer

from ml.inference_contract import InferenceContract, apply_normalization, resolve_inference_contract
from ml.paths import MODELS_DIR

DEFAULT_MODEL_REPOSITORY = "caeher/mbert-sv"


def has_model_weights(model_dir: Path) -> bool:
    """Indica si el directorio contiene un checkpoint que Transformers puede cargar."""
    return any(
        (
            (model_dir / "model.safetensors").is_file(),
            (model_dir / "pytorch_model.bin").is_file(),
            bool(list(model_dir.glob("model-*.safetensors"))),
            bool(list(model_dir.glob("pytorch_model-*.bin"))),
        )
    )


def ensure_model_weights(model_dir: Path) -> None:
    """Descarga el checkpoint de Hugging Face si todavía no hay pesos locales.

    ``local_dir`` permite reutilizar el checkpoint fuera de Docker y mediante el
    volumen nombrado de Docker Compose.
    """
    if has_model_weights(model_dir):
        return

    repository = os.getenv("HF_MODEL_REPO", DEFAULT_MODEL_REPOSITORY)
    revision = os.getenv("HF_MODEL_REVISION") or None
    token = os.getenv("HF_TOKEN") or None
    model_dir.mkdir(parents=True, exist_ok=True)

    try:
        snapshot_download(
            repo_id=repository,
            revision=revision,
            token=token,
            local_dir=str(model_dir),
        )
    except Exception as exc:  # pragma: no cover - depende de red/credenciales
        raise RuntimeError(
            f"No se pudieron descargar los pesos de {repository}. "
            "Compruebe la conexión a Hugging Face o defina HF_TOKEN si el repo es privado."
        ) from exc

    if not has_model_weights(model_dir):
        raise RuntimeError(
            f"La descarga desde {repository} finalizó, pero no contiene pesos compatibles "
            f"en {model_dir}."
        )


def get_device() -> torch.device:
    if torch.cuda.is_available():
        return torch.device("cuda")
    return torch.device("cpu")


def default_model_dir() -> Path:
    return MODELS_DIR / "mbert-sv"


def resolve_model_dir(
    model_dir: Path | str | None = None,
    *,
    backend: str | None = None,
) -> Path:
    """Resuelve directorio del checkpoint desde env o backend."""
    if model_dir is not None:
        return Path(model_dir)

    env_dir = os.getenv("MODEL_DIR")
    if env_dir:
        return Path(env_dir)

    _ = (backend or os.getenv("MODEL_BACKEND", "mbert")).lower()
    return default_model_dir()


class CachedPredictor:
    """Carga tokenizer + modelo una vez; aplica contrato de normalización."""

    def __init__(
        self,
        model_dir: Path | str | None = None,
        *,
        backend: str | None = None,
        batch_size: int = 16,
        normalize: bool = True,
    ):
        self.model_dir = resolve_model_dir(model_dir, backend=backend)
        ensure_model_weights(self.model_dir)

        self.contract: InferenceContract = resolve_inference_contract(self.model_dir)
        self.device = get_device()
        self.tokenizer = AutoTokenizer.from_pretrained(str(self.model_dir))
        self.model = AutoModelForSequenceClassification.from_pretrained(str(self.model_dir))
        self.model.to(self.device)
        self.model.eval()
        self.batch_size = batch_size
        self.normalize = normalize

    @property
    def max_length(self) -> int:
        return self.contract.max_length

    @torch.no_grad()
    def predict_proba(self, texts: list[str]) -> np.ndarray:
        """Devuelve probabilidades (n_samples, n_classes)."""
        if self.normalize:
            texts = apply_normalization(texts, self.contract)
        else:
            texts = [str(t) if t else " " for t in texts]

        all_probs: list[np.ndarray] = []
        for i in range(0, len(texts), self.batch_size):
            batch = [str(t) if t else " " for t in texts[i : i + self.batch_size]]
            enc = self.tokenizer(
                batch,
                truncation=True,
                padding=True,
                max_length=self.contract.max_length,
                return_tensors="pt",
            )
            enc = {k: v.to(self.device) for k, v in enc.items()}
            logits = self.model(**enc).logits
            probs = torch.softmax(logits, dim=-1).cpu().numpy()
            all_probs.append(probs)
        return np.concatenate(all_probs, axis=0)

    @torch.no_grad()
    def predict_single(self, text: str) -> tuple[int, float, np.ndarray]:
        """Predice una instancia: (label_index, confidence, probs)."""
        probs = self.predict_proba([text])[0]
        idx = int(np.argmax(probs))
        return idx, float(probs[idx]), probs
