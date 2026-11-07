"""Fixtures partagées par les tests."""

import pandas as pd
import pytest

NAN = float("nan")


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
