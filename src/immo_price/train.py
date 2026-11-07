"""Entraînement, évaluation et sauvegarde du modèle."""

import argparse
import json
import logging
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

from immo_price.config import get_settings
from immo_price.data_loading import DEFAULT_YEARS, load_raw
from immo_price.logging_config import setup_logging
from immo_price.preprocessing import (
    FEATURE_COLUMNS,
    TARGET_COLUMN,
    clean_dvf,
    split_by_year,
)

logger = logging.getLogger(__name__)


def prepare_features(df: pd.DataFrame) -> pd.DataFrame:
    """Extrait les variables explicatives avec des types homogènes.

    Args:
        df: DataFrame contenant au moins les colonnes FEATURE_COLUMNS.

    Returns:
        Une copie avec le code postal converti en texte.
    """
    features = df[FEATURE_COLUMNS].copy()
    features["code_postal"] = features["code_postal"].astype(str)
    return features


def build_pipeline(n_estimators: int = 200, random_state: int = 42) -> Pipeline:
    """Construit le pipeline de prétraitement et de régression.

    Args:
        n_estimators: Nombre d'arbres du modèle.
        random_state: Graine aléatoire, pour des résultats reproductibles.

    Returns:
        Un pipeline scikit-learn non entraîné.
    """
    preprocessor = ColumnTransformer(
        [
            ("cat", OneHotEncoder(handle_unknown="ignore"), ["code_postal"]),
            ("num", "passthrough", ["surface", "nombre_pieces", "annee"]),
        ]
    )
    model = GradientBoostingRegressor(
        n_estimators=n_estimators, max_depth=4, random_state=random_state
    )
    return Pipeline([("prep", preprocessor), ("model", model)])


def evaluate(model: Pipeline, test: pd.DataFrame) -> dict[str, float]:
    """Calcule MAE, RMSE et R² sur un jeu de test.

    Args:
        model: Pipeline entraîné.
        test: DataFrame nettoyé contenant la cible.

    Returns:
        Un dictionnaire de métriques.
    """
    predictions = model.predict(prepare_features(test))
    target = test[TARGET_COLUMN]
    return {
        "mae": float(mean_absolute_error(target, predictions)),
        "rmse": float(np.sqrt(mean_squared_error(target, predictions))),
        "r2": float(r2_score(target, predictions)),
    }


def train_model(clean: pd.DataFrame) -> tuple[Pipeline, dict[str, float]]:
    """Entraîne le modèle et l'évalue face à une baseline.

    La baseline prédit toujours le prix au m² médian de l'entraînement.

    Args:
        clean: DataFrame nettoyé, avec une colonne "annee".

    Returns:
        Le modèle entraîné et ses métriques.
    """
    train, test = split_by_year(clean)
    model = build_pipeline()
    model.fit(prepare_features(train), train[TARGET_COLUMN])
    metrics = evaluate(model, test)
    median = float(train[TARGET_COLUMN].median())
    baseline = np.full(len(test), median)
    baseline_mae = mean_absolute_error(test[TARGET_COLUMN], baseline)
    metrics["baseline_mae"] = float(baseline_mae)
    metrics["n_train"] = float(len(train))
    metrics["n_test"] = float(len(test))
    return model, metrics


def save_model(model: Pipeline, path: Path) -> None:
    """Sauvegarde le modèle avec joblib.

    Args:
        model: Pipeline entraîné.
        path: Fichier de destination, dossier parent créé si besoin.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, path)


def save_metrics(metrics: dict[str, float], path: Path) -> None:
    """Sauvegarde les métriques au format JSON.

    Args:
        metrics: Métriques à écrire.
        path: Fichier de destination, dossier parent créé si besoin.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")


def main() -> None:
    """Point d'entrée en ligne de commande : entraîne le modèle."""
    parser = argparse.ArgumentParser(description="Entraîne le modèle de prix.")
    parser.add_argument("--departement", default="94")
    parser.add_argument("--years", type=int, nargs="+", default=DEFAULT_YEARS)
    args = parser.parse_args()
    settings = get_settings()
    setup_logging(settings.log_level)
    paths = [
        settings.data_dir / f"dvf_{args.departement}_{year}.csv.gz"
        for year in args.years
    ]
    clean = clean_dvf(load_raw(paths))
    logger.info("%d ventes d'appartements retenues", len(clean))
    model, metrics = train_model(clean)
    save_model(model, settings.model_path)
    save_metrics(metrics, settings.model_path.parent / "metrics.json")
    logger.info("Modèle sauvegardé : %s", settings.model_path)
    logger.info("Métriques : %s", metrics)
