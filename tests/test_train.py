"""Tests de l'entraînement."""

import json

import pandas as pd
from sklearn.pipeline import Pipeline

from immo_price import train
from immo_price.config import get_settings
from immo_price.predict import load_model
from immo_price.preprocessing import FEATURE_COLUMNS
from immo_price.train import (
    build_pipeline,
    evaluate,
    prepare_features,
    save_metrics,
    save_model,
    train_model,
)


def test_build_pipeline_has_two_steps() -> None:
    pipeline = build_pipeline(n_estimators=10)
    assert isinstance(pipeline, Pipeline)
    assert [name for name, _ in pipeline.steps] == ["prep", "model"]


def test_prepare_features_converts_postal_code_to_text(clean_df) -> None:
    features = prepare_features(clean_df)
    assert list(features.columns) == FEATURE_COLUMNS
    assert all(isinstance(code, str) for code in features["code_postal"])


def test_train_model_returns_expected_metrics(clean_df) -> None:
    _, metrics = train_model(clean_df)
    expected = {"mae", "rmse", "r2", "baseline_mae", "n_train", "n_test"}
    assert set(metrics) == expected
    assert metrics["n_train"] + metrics["n_test"] == len(clean_df)


def test_model_beats_median_baseline(clean_df) -> None:
    _, metrics = train_model(clean_df)
    assert metrics["mae"] < metrics["baseline_mae"]


def test_evaluate_returns_consistent_metrics(trained_model, clean_df) -> None:
    metrics = evaluate(trained_model, clean_df)
    assert metrics["rmse"] >= metrics["mae"] >= 0


def test_save_and_load_model_roundtrip(trained_model, clean_df, tmp_path) -> None:
    path = tmp_path / "models" / "model.joblib"
    save_model(trained_model, path)
    reloaded = load_model(path)
    features = prepare_features(clean_df.head(5))
    expected = trained_model.predict(features).tolist()
    assert reloaded.predict(features).tolist() == expected


def test_save_metrics_writes_json(tmp_path) -> None:
    path = tmp_path / "out" / "metrics.json"
    save_metrics({"mae": 1.5}, path)
    assert json.loads(path.read_text(encoding="utf-8")) == {"mae": 1.5}


def test_main_trains_and_saves_model(monkeypatch, tmp_path, clean_df) -> None:
    model_path = tmp_path / "models" / "model.joblib"
    monkeypatch.setenv("IMMO_MODEL_PATH", str(model_path))
    monkeypatch.setenv("IMMO_DATA_DIR", str(tmp_path))
    monkeypatch.setattr(train, "load_raw", lambda paths: pd.DataFrame())
    monkeypatch.setattr(train, "clean_dvf", lambda raw: clean_df)
    monkeypatch.setattr("sys.argv", ["immo-train", "--years", "2023", "2024"])
    get_settings.cache_clear()
    train.main()
    get_settings.cache_clear()
    assert model_path.exists()
    assert (model_path.parent / "metrics.json").exists()
