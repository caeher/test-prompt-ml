"""Tests de la API FastAPI (predictor mockeado)."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import numpy as np
import pytest
from fastapi.testclient import TestClient

from main import app
from ml.inference_contract import InferenceContract
from schemas import ExplainResponse, PredictResponse, ProbabilityMap, TextFeatures, TokenWeight


@pytest.fixture(autouse=True)
def noop_lifespan():
    with patch("services.load_predictor"):
        with patch("services.unload_predictor"):
            yield


@pytest.fixture
def mock_predictor():
    contract = InferenceContract(
        max_length=128,
        text_column="texto_modelo",
        normalizer="normalize_for_model",
        normalizer_version="1.1",
    )
    predictor = MagicMock()
    predictor.model_dir = "models/mbert-sv"
    predictor.device = "cpu"
    predictor.contract = contract
    predictor.predict_single.return_value = (1, 0.87, np.array([0.05, 0.87, 0.06, 0.02]))
    predictor.predict_proba.return_value = np.array([[0.05, 0.87, 0.06, 0.02]])
    return predictor


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_health_ok(client, mock_predictor):
    with patch("services.get_predictor", return_value=mock_predictor):
        response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["model_loaded"] is True
    assert data["backend"] == "mbert"


def test_health_unavailable():
    with patch("services.get_predictor", side_effect=RuntimeError("no model")):
        with TestClient(app) as test_client:
            response = test_client.get("/health")
    assert response.status_code == 503


def test_predict_empty_text(client):
    response = client.post("/api/predict", json={"text": ""})
    assert response.status_code == 422


def test_predict_success(client):
    with patch(
        "services.predict_text",
        return_value=PredictResponse(
            text_original="hola",
            text_normalized="hola",
            label="Lenguaje Ofensivo",
            label_index=1,
            confidence=0.87,
            probabilities=ProbabilityMap(
                no_toxico=0.05,
                ofensivo=0.87,
                odio=0.06,
                amenazas=0.02,
            ),
            features=TextFeatures(n_palabras=1, has_url=False, has_mention=False),
        ),
    ):
        response = client.post("/api/predict", json={"text": "hola"})
    assert response.status_code == 200
    data = response.json()
    assert data["label_index"] == 1
    assert data["probabilities"]["ofensivo"] == 0.87


def test_explain_success(client):
    with patch(
        "services.explain_text",
        return_value=ExplainResponse(
            text="ese maje",
            predicted_class=1,
            predicted_label="Lenguaje Ofensivo",
            weights=[TokenWeight(token="maje", weight=0.31)],
        ),
    ):
        response = client.post("/api/explain", json={"text": "ese maje"})
    assert response.status_code == 200
    data = response.json()
    assert data["weights"][0]["token"] == "maje"


def test_metrics_endpoint(client):
    response = client.get("/api/metrics")
    assert response.status_code == 200
    data = response.json()
    assert data["model"] == "mbert"
    assert "f1_macro_official" in data
