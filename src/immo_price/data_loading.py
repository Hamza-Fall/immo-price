"""Téléchargement et chargement des données DVF géolocalisées."""

import argparse
import logging
from pathlib import Path

import pandas as pd
import requests

from immo_price.config import get_settings
from immo_price.logging_config import setup_logging

logger = logging.getLogger(__name__)

BASE_URL = "https://files.data.gouv.fr/geo-dvf/latest/csv"
DEFAULT_YEARS = [2021, 2022, 2023, 2024, 2025]
USECOLS = [
    "id_mutation",
    "date_mutation",
    "nature_mutation",
    "valeur_fonciere",
    "code_postal",
    "type_local",
    "surface_reelle_bati",
    "nombre_pieces_principales",
]


def build_url(year: int, departement: str) -> str:
    """Construit l'URL du fichier DVF d'un département pour une année.

    Args:
        year: Année des transactions.
        departement: Code du département, par exemple "94".

    Returns:
        L'URL du fichier compressé.
    """
    return f"{BASE_URL}/{year}/departements/{departement}.csv.gz"


def download_dvf(
    departement: str, years: list[int], dest_dir: Path, timeout: int = 60
) -> list[Path]:
    """Télécharge les fichiers DVF manquants.

    Un fichier déjà présent dans le dossier n'est pas retéléchargé.

    Args:
        departement: Code du département.
        years: Années à télécharger.
        dest_dir: Dossier de destination, créé si besoin.
        timeout: Délai maximal de la requête, en secondes.

    Returns:
        Les chemins des fichiers locaux, dans l'ordre des années.

    Raises:
        requests.HTTPError: si le serveur répond par une erreur.
    """
    dest_dir.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    for year in years:
        target = dest_dir / f"dvf_{departement}_{year}.csv.gz"
        if target.exists():
            logger.info("Déjà présent : %s", target)
        else:
            url = build_url(year, departement)
            logger.info("Téléchargement de %s", url)
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()
            target.write_bytes(response.content)
        paths.append(target)
    return paths


def load_raw(paths: list[Path]) -> pd.DataFrame:
    """Charge et concatène les fichiers DVF bruts.

    Args:
        paths: Chemins des fichiers CSV compressés.

    Returns:
        Un DataFrame avec uniquement les colonnes utiles.

    Raises:
        ValueError: si la liste de fichiers est vide.
        FileNotFoundError: si un fichier est introuvable.
    """
    if not paths:
        raise ValueError("Aucun fichier à charger.")
    frames = []
    for path in paths:
        if not path.exists():
            raise FileNotFoundError(f"Fichier introuvable : {path}")
        frames.append(
            pd.read_csv(path, usecols=USECOLS, dtype={"code_postal": "string"})
        )
    return pd.concat(frames, ignore_index=True)


def main() -> None:
    """Point d'entrée en ligne de commande : télécharge les données."""
    parser = argparse.ArgumentParser(description="Télécharge les données DVF.")
    parser.add_argument("--departement", default="94")
    parser.add_argument("--years", type=int, nargs="+", default=DEFAULT_YEARS)
    args = parser.parse_args()
    settings = get_settings()
    setup_logging(settings.log_level)
    download_dvf(args.departement, args.years, settings.data_dir)
