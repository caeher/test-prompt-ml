"""API FastAPI para clasificación de toxicidad."""

from __future__ import annotations

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

import services
from schemas import (
    ContractInfo,
    ExplainResponse,
    HealthResponse,
    MetricsResponse,
    PredictResponse,
    TextRequest,
)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    services.load_predictor()
    yield
    services.unload_predictor()


app = FastAPI(
    title="Discurso de Odio API",
    description="Clasificación de toxicidad en español salvadoreño (4 clases)",
    version="0.1.0",
    lifespan=lifespan,
)

cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in cors_origins if origin.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    backend = services.get_backend_name()
    try:
        predictor = services.get_predictor()
        return HealthResponse(
            status="ok",
            model_loaded=True,
            model_dir=str(predictor.model_dir),
            backend=backend,
            device=str(predictor.device),
            contract=ContractInfo(
                max_length=predictor.contract.max_length,
                normalizer=predictor.contract.normalizer,
                normalizer_version=predictor.contract.normalizer_version,
            ),
        )
    except RuntimeError as exc:
        raise HTTPException(
            status_code=503,
            detail={
                "status": "unavailable",
                "model_loaded": False,
                "backend": backend,
                "error": str(exc),
                "hint": "Coloque el checkpoint en backend/models/mbert-sv/ (ver README)",
            },
        ) from exc


@app.post("/api/predict", response_model=PredictResponse)
def predict(request: TextRequest) -> PredictResponse:
    try:
        return services.predict_text(request.text.strip())
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@app.post("/api/explain", response_model=ExplainResponse)
def explain(request: TextRequest) -> ExplainResponse:
    try:
        return services.explain_text(request.text.strip())
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@app.get("/api/metrics", response_model=MetricsResponse)
def metrics() -> MetricsResponse:
    return services.load_metrics()
