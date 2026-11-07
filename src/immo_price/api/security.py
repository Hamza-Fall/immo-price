"""Authentification par clé API."""

import logging
import secrets
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader

from immo_price.config import get_settings

logger = logging.getLogger(__name__)
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def verify_api_key(key: Annotated[str | None, Depends(api_key_header)] = None) -> None:
    """Refuse la requête si la clé API est absente ou invalide.

    Args:
        key: Valeur de l'en-tête X-API-Key.

    Raises:
        HTTPException: 503 si le serveur n'a pas de clé configurée, 401 si la
            clé est absente ou incorrecte.
    """
    expected = get_settings().api_key
    if not expected:
        logger.error("IMMO_API_KEY n'est pas configurée")
        raise HTTPException(
            status.HTTP_503_SERVICE_UNAVAILABLE, "Clé API non configurée"
        )
    if key is None or not secrets.compare_digest(key.encode(), expected.encode()):
        logger.warning("Accès refusé : clé API absente ou invalide")
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Clé API invalide")
