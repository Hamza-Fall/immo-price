"""Tests de l'API."""

import pytest
from fastapi.testclient import TestClient

from immo_price.api import main as api_main
from immo_price.api.main import app
from immo_price.config import get_settings
from immo_price.train import save_model

HEADERS = {"X-API-Key": "test-key"}
BODY = {"surface": 45.0, "nombre_pieces": 2, "code_postal": "94270", "annee": 2025}


def test_health_with_model(client) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "model_loaded": True}


def test_health_without_model(client, monkeypatch) -> None:
    monkeypatch.setattr(app.state, "model", None)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["model_loaded"] is False


def test_predict_success(client) -> None:
    response = client.post("/predict", json=BODY, headers=HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert set(data) == {"prix_m2", "prix_estime"}
    assert data["prix_estime"] == pytest.approx(data["prix_m2"] * 45, rel=1e-3)


def test_predict_without_key(client) -> None:
    assert client.post("/predict", json=BODY).status_code == 401


def test_predict_wrong_key(client) -> None:
    wrong = {"X-API-Key": "mauvaise"}
    response = client.post("/predict", json=BODY, headers=wrong)
    assert response.status_code == 401


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("surface", -5),
        ("surface", 5),
        ("nombre_pieces", 0),
        ("code_postal", "abc"),
        ("annee", 1900),
    ],
)
def test_predict_invalid_input(client, field, value) -> None:
    response = client.post("/predict", json={**BODY, field: value}, headers=HEADERS)
    assert response.status_code == 422


def test_predict_missing_field(client) -> None:
    incomplete = {key: val for key, val in BODY.items() if key != "surface"}
    response = client.post("/predict", json=incomplete, headers=HEADERS)
    assert response.status_code == 422


def test_predict_model_not_loaded(client, monkeypatch) -> None:
    monkeypatch.setattr(app.state, "model", None)
    response = client.post("/predict", json=BODY, headers=HEADERS)
    assert response.status_code == 503


def test_predict_api_key_not_configured(client, monkeypatch) -> None:
    monkeypatch.setenv("IMMO_API_KEY", "")
    get_settings.cache_clear()
    response = client.post("/predict", json=BODY, headers=HEADERS)
    assert response.status_code == 503


def test_swagger_documentation_is_available(client) -> None:
    assert client.get("/docs").status_code == 200
    schema = client.get("/openapi.json").json()
    assert "/predict" in schema["paths"]
    assert "/health" in schema["paths"]


def test_lifespan_loads_model(monkeypatch, tmp_path, trained_model) -> None:
    path = tmp_path / "model.joblib"
    save_model(trained_model, path)
    monkeypatch.setenv("IMMO_MODEL_PATH", str(path))
    get_settings.cache_clear()
    with TestClient(app) as test_client:
        assert test_client.get("/health").json()["model_loaded"] is True
    get_settings.cache_clear()


def test_lifespan_without_model_file(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("IMMO_MODEL_PATH", str(tmp_path / "absent.joblib"))
    get_settings.cache_clear()
    with TestClient(app) as test_client:
        assert test_client.get("/health").json()["model_loaded"] is False
    get_settings.cache_clear()


def test_run_starts_uvicorn(monkeypatch) -> None:
    calls = {}

    def fake_run(*args, **kwargs) -> None:
        calls["args"] = args
        calls["kwargs"] = kwargs

    monkeypatch.setattr(api_main.uvicorn, "run", fake_run)
    api_main.run()
    assert calls["args"] == ("immo_price.api.main:app",)
    assert calls["kwargs"]["port"] == 8000
