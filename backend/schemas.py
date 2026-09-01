"""Esquemas Pydantic para la API de inferencia."""

from __future__ import annotations

from pydantic import BaseModel, Field


class TextRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=2000)


class ProbabilityMap(BaseModel):
    no_toxico: float
    ofensivo: float
    odio: float
    amenazas: float


class TextFeatures(BaseModel):
    n_palabras: int
    has_url: bool
    has_mention: bool


class PredictResponse(BaseModel):
    text_original: str
    text_normalized: str
    label: str
    label_index: int
    confidence: float
    probabilities: ProbabilityMap
    features: TextFeatures


class TokenWeight(BaseModel):
    token: str
    weight: float


class ExplainResponse(BaseModel):
    text: str
    predicted_class: int
    predicted_label: str
    weights: list[TokenWeight]


class ContractInfo(BaseModel):
    max_length: int
    normalizer: str
    normalizer_version: str


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    model_dir: str | None = None
    backend: str
    device: str | None = None
    contract: ContractInfo | None = None
    error: str | None = None


class SliceMetric(BaseModel):
    slice: str
    f1_macro: float
    accuracy: float
    n: int
    definition: str


class MetricsResponse(BaseModel):
    model: str
    f1_macro_official: float
    test_n: int
    slices: list[SliceMetric]
