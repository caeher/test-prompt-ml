"""Servicios de inferencia, LIME y métricas globales."""

from __future__ import annotations

import json
import os
from functools import lru_cache

from ml.config import load_settings
from ml.inference_contract import apply_normalization_single
from ml.lime_explainer import build_lime_explainer, explain_instance, make_predict_proba_fn
from ml.normalization import has_mention_literal, has_url_literal
from ml.paths import METRICS_DIR
from ml.runtime import CachedPredictor
from schemas import (
    ExplainResponse,
    MetricsResponse,
    PredictResponse,
    ProbabilityMap,
    SliceMetric,
    TextFeatures,
    TokenWeight,
)

_predictor: CachedPredictor | None = None
_predictor_error: str | None = None


def get_backend_name() -> str:
    return os.getenv("MODEL_BACKEND", "mbert").lower()


def get_predictor() -> CachedPredictor:
    if _predictor is None:
        raise RuntimeError(_predictor_error or "Modelo no cargado")
    return _predictor


def load_predictor() -> None:
    global _predictor, _predictor_error
    try:
        _predictor = CachedPredictor(backend=get_backend_name())
        _predictor_error = None
    except FileNotFoundError as exc:
        _predictor = None
        _predictor_error = str(exc)


def unload_predictor() -> None:
    global _predictor, _predictor_error
    _predictor = None
    _predictor_error = None


def extract_features(text: str) -> TextFeatures:
    words = text.split()
    return TextFeatures(
        n_palabras=len(words),
        has_url=bool(has_url_literal(text)),
        has_mention=bool(has_mention_literal(text)),
    )


def predict_text(text: str) -> PredictResponse:
    predictor = get_predictor()
    settings = load_settings()
    label_names: list[str] = settings["labels"]["names"]
    short_names: list[str] = settings["labels"]["short_names"]

    text_normalized = apply_normalization_single(text, predictor.contract)
    label_index, confidence, probs = predictor.predict_single(text)

    prob_map = {
        short_names[i]: float(probs[i]) for i in range(len(short_names))
    }
    return PredictResponse(
        text_original=text,
        text_normalized=text_normalized,
        label=label_names[label_index],
        label_index=label_index,
        confidence=confidence,
        probabilities=ProbabilityMap(**prob_map),
        features=extract_features(text),
    )


def explain_text(text: str, *, num_samples: int = 200, num_features: int = 10) -> ExplainResponse:
    predictor = get_predictor()
    settings = load_settings()
    label_names: list[str] = settings["labels"]["names"]

    explainer = build_lime_explainer()
    predict_proba_fn = make_predict_proba_fn(predictor.predict_proba)
    result = explain_instance(
        text,
        predict_proba_fn,
        explainer,
        num_features=num_features,
        num_samples=num_samples,
    )

    pred_class = int(result["predicted_class"])
    weights = [
        TokenWeight(token=str(token), weight=float(weight))
        for token, weight in result.get("weights", [])
    ]
    return ExplainResponse(
        text=str(result.get("text", text)),
        predicted_class=pred_class,
        predicted_label=label_names[pred_class] if 0 <= pred_class < len(label_names) else "",
        weights=weights,
    )


@lru_cache(maxsize=1)
def load_metrics() -> MetricsResponse:
    official_path = METRICS_DIR / "mbert_official_run.json"
    slice_path = METRICS_DIR / "slice_metrics.json"

    f1_macro = 0.0
    test_n = 0
    if official_path.exists():
        with open(official_path, encoding="utf-8") as f:
            official = json.load(f)
        f1_macro = float(official.get("official_f1_macro", official.get("f1_macro_raw", 0.0)))
        test_n = int(official.get("test_n", 0))

    slices: list[SliceMetric] = []
    if slice_path.exists():
        with open(slice_path, encoding="utf-8") as f:
            slice_data = json.load(f)
        for row in slice_data.get("rows", []):
            if row.get("model") != "mbert":
                continue
            slice_name = str(row.get("slice", ""))
            if slice_name in {"con_jerga", "sin_jerga", "sarcasmo_si", "sarcasmo_no"}:
                slices.append(
                    SliceMetric(
                        slice=slice_name,
                        f1_macro=float(row.get("f1_macro", 0.0)),
                        accuracy=float(row.get("accuracy", 0.0)),
                        n=int(row.get("n", 0)),
                        definition=str(row.get("definition", "")),
                    )
                )

    return MetricsResponse(
        model="mbert",
        f1_macro_official=f1_macro,
        test_n=test_n,
        slices=slices,
    )
