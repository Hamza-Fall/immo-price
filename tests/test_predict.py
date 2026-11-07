"""Tests de l'inférence."""

import pytest

from immo_price.predict import load_model, predict_price


def test_load_model_missing_file(tmp_path) -> None:
    with pytest.raises(FileNotFoundError):
        load_model(tmp_path / "absent.joblib")


def test_predict_price_returns_both_prices(trained_model) -> None:
    result = predict_price(trained_model, 50.0, 2, "94270", 2024)
    assert set(result) == {"prix_m2", "prix_estime"}
    assert result["prix_m2"] > 0
    assert result["prix_estime"] == pytest.approx(result["prix_m2"] * 50, rel=1e-3)


def test_predict_price_unknown_postal_code_does_not_crash(trained_model) -> None:
    result = predict_price(trained_model, 50.0, 2, "99999", 2024)
    assert result["prix_m2"] > 0
