"""Chargement du modèle et prédiction."""

from pathlib import Path

import joblib
import pandas as pd
from sklearn.pipeline import Pipeline


def load_model(path: Path) -> Pipeline:
    """Charge un modèle sauvegardé.

    N'ouvrez que des fichiers que vous avez produits vous-même : joblib
    repose sur pickle, qui peut exécuter du code arbitraire.

    Args:
        path: Chemin du fichier du modèle.

    Returns:
        Le pipeline chargé.

    Raises:
        FileNotFoundError: si le fichier n'existe pas.
    """
    if not path.exists():
        raise FileNotFoundError(f"Modèle introuvable : {path}")
    return joblib.load(path)


def predict_price(
    model: Pipeline,
    surface: float,
    nombre_pieces: int,
    code_postal: str,
    annee: int,
) -> dict[str, float]:
    """Estime le prix d'un appartement.

    Args:
        model: Pipeline entraîné.
        surface: Surface en m².
        nombre_pieces: Nombre de pièces principales.
        code_postal: Code postal à cinq chiffres.
        annee: Année de la vente.

    Returns:
        Un dictionnaire avec "prix_m2" et "prix_estime" (en euros).
    """
    features = pd.DataFrame(
        [
            {
                "surface": surface,
                "nombre_pieces": nombre_pieces,
                "code_postal": code_postal,
                "annee": annee,
            }
        ]
    )
    prix_m2 = float(model.predict(features)[0])
    return {
        "prix_m2": round(prix_m2, 2),
        "prix_estime": round(prix_m2 * surface, 2),
    }
