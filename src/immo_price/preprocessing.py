"""Nettoyage et préparation des données DVF."""

import pandas as pd

FEATURE_COLUMNS = ["surface", "nombre_pieces", "code_postal", "annee"]
TARGET_COLUMN = "prix_m2"
DWELLING_TYPES = ("Appartement", "Maison")
MIN_SURFACE, MAX_SURFACE = 9.0, 300.0
MIN_PIECES, MAX_PIECES = 1, 10
MIN_PRIX_M2, MAX_PRIX_M2 = 1000.0, 30000.0


def _empty_result() -> pd.DataFrame:
    """Retourne un DataFrame vide avec les colonnes attendues."""
    return pd.DataFrame(columns=[*FEATURE_COLUMNS, TARGET_COLUMN])


def clean_dvf(df: pd.DataFrame) -> pd.DataFrame:
    """Nettoie les DVF bruts et retourne les variables et la cible.

    Ne garde que les ventes d'un seul logement de type appartement. Les
    mutations qui contiennent plusieurs logements sont supprimées, car le prix
    est global et ne peut pas être attribué à un bien. Les valeurs manquantes
    et aberrantes sont retirées, puis le prix au m² est calculé.

    Args:
        df: DataFrame DVF brut.

    Returns:
        Un DataFrame avec les colonnes FEATURE_COLUMNS et TARGET_COLUMN.
    """
    data = df[df["nature_mutation"] == "Vente"].copy()
    if data.empty:
        return _empty_result()

    is_dwelling = data["type_local"].isin(DWELLING_TYPES)
    n_dwellings = is_dwelling.groupby(data["id_mutation"]).transform("sum")
    data = data[is_dwelling & (n_dwellings == 1)]
    data = data[data["type_local"] == "Appartement"].rename(
        columns={
            "surface_reelle_bati": "surface",
            "nombre_pieces_principales": "nombre_pieces",
        }
    )
    data = data.dropna(
        subset=[
            "valeur_fonciere",
            "surface",
            "nombre_pieces",
            "code_postal",
            "date_mutation",
        ]
    ).copy()
    if data.empty:
        return _empty_result()

    data["date_mutation"] = pd.to_datetime(data["date_mutation"], errors="coerce")
    data = data.dropna(subset=["date_mutation"]).copy()
    data["annee"] = data["date_mutation"].dt.year
    data["code_postal"] = (
        data["code_postal"]
        .astype("string")
        .str.replace(r"\.0$", "", regex=True)
        .str.zfill(5)
    )
    data[TARGET_COLUMN] = data["valeur_fonciere"] / data["surface"]

    mask = (
        data["surface"].between(MIN_SURFACE, MAX_SURFACE)
        & data["nombre_pieces"].between(MIN_PIECES, MAX_PIECES)
        & data[TARGET_COLUMN].between(MIN_PRIX_M2, MAX_PRIX_M2)
    )
    return data.loc[mask, [*FEATURE_COLUMNS, TARGET_COLUMN]].reset_index(drop=True)


def split_by_year(
    df: pd.DataFrame, test_year: int | None = None
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Sépare entraînement (années passées) et test (dernière année).

    Une séparation temporelle évite d'évaluer le modèle sur des ventes
    antérieures à celles qu'il a vues à l'entraînement.

    Args:
        df: DataFrame nettoyé, avec une colonne "annee".
        test_year: Année de test. Par défaut, la dernière année du jeu.

    Returns:
        Le couple (entraînement, test).

    Raises:
        ValueError: si l'un des deux jeux est vide.
    """
    last = int(df["annee"].max()) if test_year is None else test_year
    train, test = df[df["annee"] < last], df[df["annee"] == last]
    if train.empty or test.empty:
        raise ValueError("Séparation temporelle impossible : jeu vide.")
    return train, test
