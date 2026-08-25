"""Pruebas del bootstrap del checkpoint remoto."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from ml.runtime import ensure_model_weights


def test_ensure_model_weights_skips_download_when_weights_exist(tmp_path):
    (tmp_path / "model.safetensors").touch()

    with patch("ml.runtime.snapshot_download") as download:
        ensure_model_weights(tmp_path)

    download.assert_not_called()


def test_ensure_model_weights_downloads_to_requested_directory(tmp_path):
    def create_weights(**kwargs):
        assert kwargs["repo_id"] == "caeher/mbert-sv"
        assert kwargs["local_dir"] == str(tmp_path)
        (tmp_path / "model.safetensors").touch()

    with patch("ml.runtime.snapshot_download", side_effect=create_weights) as download:
        ensure_model_weights(tmp_path)

    download.assert_called_once()


def test_ensure_model_weights_rejects_download_without_weights(tmp_path):
    with patch("ml.runtime.snapshot_download"):
        with pytest.raises(RuntimeError, match="no contiene pesos compatibles"):
            ensure_model_weights(tmp_path)
