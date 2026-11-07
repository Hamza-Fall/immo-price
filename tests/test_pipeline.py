"""Test d'intégration : du fichier brut à la prédiction."""

import numpy as np
import pandas as pd
import pytest

from immo_price.data_loading import load_raw
from immo_price.predict import load_model, predict_price
from immo_price.preprocessing import clean_dvf
from immo_price.train import save_model, train_model


def make_raw(n: int = 240) -> pd.DataFrame:
    """Construit un faux DVF brut valide, sur trois années."""
    rng = np.random.default_rng(1)
    index = np.arange(n)
    postal = np.array(["94000", "94270", "94120"])[index % 3]
    base = np.array([5000.0, 7000.0, 6000.0])[index % 3]
    surface = rng.uniform(20, 100, n).round(1)
    prix_m2 = base + rng.normal(0, 150, n)
    years = 2022 + (index // 3) % 3
    return pd.DataFrame(
        {
            "id_mutation": [f"M{i}" for i in index],
            "date_mutation": [f"{year}-06-15" for year in years],
            "nature_mutation": "Vente",
            "valeur_fonciere": (surface * prix_m2).round(0),
            "code_postal": postal,
            "type_local": "Appartement",
            "surface_reelle_bati": surface,
            "nombre_pieces_principales": np.clip(surface // 25 + 1, 1, 5),
        }
    )


def test_full_pipeline_from_files_to_prediction(tmp_path) -> None:
    raw = make_raw()
    paths = []
    for year in (2022, 2023, 2024):
        path = tmp_path / f"dvf_94_{year}.csv.gz"
        subset = raw[raw["date_mutation"].str.startswith(str(year))]
        subset.to_csv(path, index=False, compression="gzip")
        paths.append(path)

    clean = clean_dvf(load_raw(paths))
    assert len(clean) == len(raw)

    model, metrics = train_model(clean)
    assert metrics["mae"] < metrics["baseline_mae"]

    model_path = tmp_path / "models" / "model.joblib"
    save_model(model, model_path)
    result = predict_price(load_model(model_path), 50.0, 2, "94270", 2024)
    assert 6000 < result["prix_m2"] < 8000
    assert result["prix_estime"] == pytest.approx(result["prix_m2"] * 50, rel=1e-3)
