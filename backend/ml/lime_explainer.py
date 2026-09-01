"""Explicaciones LIME para clasificación de toxicidad."""

from __future__ import annotations

from typing import Callable

import numpy as np
from lime.lime_text import LimeTextExplainer

from ml.config import load_settings


def build_lime_explainer(class_names: list[str] | None = None) -> LimeTextExplainer:
    settings = load_settings()
    class_names = class_names or settings["labels"]["names"]
    return LimeTextExplainer(class_names=class_names, random_state=settings["project"]["seed"])


def make_predict_proba_fn(predict_fn: Callable[[list[str]], np.ndarray]) -> Callable:
    """Crea callable para LIME que devuelve probabilidades (n_samples, n_classes)."""

    def _predict(texts: list[str]) -> np.ndarray:
        texts = [str(t) if t else " " for t in texts]
        probs = predict_fn(texts)
        if isinstance(probs, tuple):
            _, probs = probs
        return np.asarray(probs, dtype=np.float64)

    return _predict


def explain_instance(
    text: str,
    predict_proba_fn: Callable,
    explainer: LimeTextExplainer | None = None,
    num_features: int = 10,
    num_samples: int = 500,
) -> dict:
    if not str(text).strip():
        return {"text": text, "predicted_class": -1, "weights": [], "top_tokens": []}

    explainer = explainer or build_lime_explainer()
    exp = explainer.explain_instance(
        text,
        predict_proba_fn,
        num_features=num_features,
        num_samples=num_samples,
    )
    if not exp.top_labels:
        return {"text": text, "predicted_class": -1, "weights": [], "top_tokens": []}

    pred_class = exp.top_labels[0]
    weights = exp.as_list(label=pred_class)
    return {
        "text": text,
        "predicted_class": pred_class,
        "weights": weights,
        "top_tokens": [w[0] for w in weights[:num_features]],
    }
