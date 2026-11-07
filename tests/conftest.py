"""Fixtures partagées par les tests."""

import numpy as np
import pandas as pd
import pytest
from fastapi.testclient import TestClient

from immo_price.api.main import app
from immo_price.config import get_settings
from immo_price.train import train_model

NAN = float("nan")


def make_clean_df(n: int = 300) -> pd.DataFrame:
    """Construit un jeu nettoyé synthétique, avec un signal par code postal."""
    rng = np.random.default_rng(0)
    index = np.arange(n)
    postal = np.array(["94000", "94270", "94120"])
    base = np.array([5000.0, 7000.0, 6000.0])
    return pd.DataFrame(
        {
            "surface": rng.uniform(15, 120, n),
            "nombre_pieces": rng.integers(1, 6, n),
            "code_postal": postal[index % 3],
            "annee": 2022 + (index // 3) % 3,
            "prix_m2": base[index % 3] + rng.normal(0, 150, n),
        }
    )


@pytest.fixture
def raw_df() -> pd.DataFrame:
    """Petit extrait DVF brut contenant des cas limites."""
    columns = [
        "id_mutation",
        "date_mutation",
        "nature_mutation",
        "valeur_fonciere",
        "code_postal",
        "type_local",
        "surface_reelle_bati",
        "nombre_pieces_principales",
    ]
    rows = [
        # A : appartement valide, code postal avec ".0" à nettoyer
        ("A", "2024-03-01", "Vente", 300000, "94270.0", "Appartement", 50, 2),
        # B : maison, donc exclue
        ("B", "2024-03-01", "Vente", 200000, "94000", "Maison", 80, 4),
        # C : deux appartements dans la même vente, donc exclue
        ("C", "2024-03-01", "Vente", 500000, "94000", "Appartement", 60, 3),
        ("C", "2024-03-01", "Vente", 500000, "94000", "Appartement", 40, 2),
        # D : prix aberrant (2 euros par m2)
        ("D", "2024-03-01", "Vente", 100, "94000", "Appartement", 50, 2),
        # E : échange, pas une vente
        ("E", "2024-03-01", "Echange", 250000, "94000", "Appartement", 50, 2),
        # F : appartement valide avec une dépendance (cave) dans la même vente
        ("F", "2023-06-01", "Vente", 360000, "94120", "Appartement", 60, 3),
        ("F", "2023-06-01", "Vente", 360000, "94120", "Dépendance", NAN, 0),
        # G : surface manquante
        ("G", "2024-03-01", "Vente", 300000, "94000", "Appartement", NAN, 2),
        # H : surface trop petite
        ("H", "2024-03-01", "Vente", 40000, "94000", "Appartement", 5, 1),
        # I : type de local manquant
        ("I", "2024-03-01", "Vente", 400000, "94000", None, NAN, NAN),
    ]
    return pd.DataFrame(rows, columns=columns)


@pytest.fixture
def clean_df() -> pd.DataFrame:
    """Jeu nettoyé synthétique sur trois années."""
    return make_clean_df()


@pytest.fixture(scope="session")
def trained_model():
    """Modèle entraîné une seule fois pour toute la session de tests."""
    model, _ = train_model(make_clean_df())
    return model


@pytest.fixture
def client(monkeypatch, trained_model):
    """Client de test de l'API, avec modèle chargé et clé API configurée."""
    monkeypatch.setenv("IMMO_API_KEY", "test-key")
    get_settings.cache_clear()
    app.state.model = trained_model
    yield TestClient(app)
    get_settings.cache_clear()
